"""Build one board end to end:  python3 gen/build.py lower|upper|service [--no-route] [--docs]

 design (gen/<board>.py)  ->  hardware/<board>/*.kicad_sch, *.kicad_pcb, *.kicad_pro
                          ->  ERC, netlist cross-check, autoroute, zone fill, DRC
                          ->  fab/<board>/ (gerbers, drill, BOM, CPL) and docs assets
"""
import importlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from kigen import design as kd          # noqa: E402
from kigen import outputs               # noqa: E402
from kigen.pcb import Board, write_project   # noqa: E402
from kigen.router import Router         # noqa: E402
from kigen.sexpr import Sym, dump       # noqa: E402


def write_symbol_libs(libdir):
    """Dump the symbols drawn by the generator into real KiCad libraries so the project opens cleanly."""
    os.makedirs(libdir, exist_ok=True)
    for nick in ("fc", "fcpwr"):
        path = os.path.join(libdir, f"{nick}.kicad_sym")
        syms = {}
        if os.path.exists(path):
            from kigen.sexpr import parse, findall
            for s in findall(parse(open(path).read()), "symbol"):
                syms[s[1]] = s
        for lib_id, sym in kd._symcache.items():
            if lib_id.startswith(nick + ":"):
                sx = [sym.sx[0], lib_id.split(":", 1)[1]] + sym.sx[2:]
                syms[sx[1]] = sx
        tree = [Sym("kicad_symbol_lib"), [Sym("version"), 20241209], [Sym("generator"), "fcgen"],
                [Sym("generator_version"), "9.0"]] + [syms[k] for k in sorted(syms)]
        with open(path, "w") as f:
            f.write(dump(tree) + "\n")


def main():
    name = sys.argv[1]
    do_route = "--no-route" not in sys.argv
    mod = importlib.import_module(name)
    d = mod.design()
    d.check()
    proj = os.path.join(ROOT, "hardware", name)
    os.makedirs(proj, exist_ok=True)
    d.write_schematic(proj)
    write_symbol_libs(os.path.join(ROOT, "hardware", "lib"))
    std_libs = sorted({p.symbol.lib_id.split(":")[0] for p in d.parts.values()} - {"fc", "fcpwr"})
    sym_libs = [(l, "${KICAD9_SYMBOL_DIR}/" + l + ".kicad_sym") for l in std_libs] + \
               [("fc", "${KIPRJMOD}/../lib/fc.kicad_sym"), ("fcpwr", "${KIPRJMOD}/../lib/fcpwr.kicad_sym")]
    fp_libs = [("fc", "${KIPRJMOD}/../lib/fc.pretty")]
    cfg = mod.RULES

    def project():
        write_project(proj, name, cfg["netclasses"], cfg["rules"], cfg["patterns"], cfg.get("dru", ""),
                      fp_libs=fp_libs, sym_libs=sym_libs)
    project()

    rep = os.path.join(ROOT, "build", name)
    os.makedirs(rep, exist_ok=True)
    net = outputs.netlist(proj, name, rep)
    diffs = outputs.compare_netlist(d, net)
    print(f"[{name}] parts: {len(d.parts)}  nets: {len(d.nets())}  schematic-vs-model differences: {len(diffs)}")
    for e in diffs[:20]:
        print("   ", e)
    erc = outputs.erc(proj, name, rep)
    print(f"[{name}] ERC: {outputs.summarize(erc)}")

    bd = Board(d, proj, layers=cfg["layers"], local_fp_dir=os.path.join(ROOT, "hardware", "lib"))
    mod.layout(bd)
    bd.save()
    project()
    unrouted = []
    if do_route:
        t0 = time.time()
        rt = Router(bd, **mod.router_config(bd))
        if hasattr(mod, "pre_route"):
            mod.pre_route(bd, rt)
        if getattr(mod, "ROUTER", "negotiated") == "sequential":
            unrouted = rt.route_seq(order=getattr(mod, "ROUTE_ORDER", None))
        else:
            unrouted = rt.route_all(order=getattr(mod, "ROUTE_ORDER", None))
        for net, ref, num in rt.failed[:0]:
            pass
        rt.commit()
        print(f"[{name}] routing took {time.time() - t0:.0f}s; unrouted nets: {unrouted}")
    if hasattr(mod, "post_route"):
        mod.post_route(bd)
    bd.fill()
    project()
    viol, unconn, parity = outputs.drc(proj, name, rep)
    print(f"[{name}] DRC violations: {outputs.summarize(viol)}")
    print(f"[{name}] unconnected: {len(unconn)}   schematic parity issues: {len(parity)}")
    json.dump(dict(parts=len(d.parts), nets=len(d.nets()), netlist_diffs=diffs, erc=[str(k) + ":" + str(v) for k, v in outputs.summarize(erc).items()],
                   drc=[str(k) + ":" + str(v) for k, v in outputs.summarize(viol).items()],
                   unconnected=len(unconn), parity=len(parity), unrouted=unrouted),
              open(os.path.join(rep, "summary.json"), "w"), indent=1)
    if "--docs" in sys.argv:
        fab = os.path.join(ROOT, "fab", name)
        os.makedirs(fab, exist_ok=True)
        copper = ["F.Cu"] + [f"In{i}.Cu" for i in range(1, cfg["layers"] - 1)] + ["B.Cu"]
        outputs.fab(proj, name, fab, copper)
        outputs.bom(d, fab)
        outputs.docs(proj, name, os.path.join(ROOT, "docs", "boards", name), copper)
        print(f"[{name}] fab + docs written")


if __name__ == "__main__":
    main()
