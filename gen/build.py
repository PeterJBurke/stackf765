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


def widen_tracks(brd, targets, clear):
    """Where the router necked a supply track down to reach a pad, widen each such segment again as far
    as the neighbouring copper allows.  targets = {net: wanted width in mm}.  The check is conservative
    (pads are treated as their bounding boxes); KiCad's DRC is still the judge afterwards."""
    import math
    import pcbnew
    mm = pcbnew.ToMM

    def seg_seg(a, b, c, d):
        def pt_seg(p, a, b):
            vx, vy = b[0] - a[0], b[1] - a[1]
            L = vx * vx + vy * vy
            t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L))
            return math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)

        def ccw(p, q, r):
            return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        if ccw(a, b, c) * ccw(a, b, d) < 0 and ccw(c, d, a) * ccw(c, d, b) < 0:
            return 0.0
        return min(pt_seg(a, c, d), pt_seg(b, c, d), pt_seg(c, a, b), pt_seg(d, a, b))

    def xy(p):
        return (mm(p.x), mm(p.y))
    obstacles = []          # [net, layer or None for all layers, [segments], radius, track or None]
    for t in brd.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = xy(t.GetPosition())
            obstacles.append([t.GetNetname(), None, [(p, p)], mm(t.GetWidth(pcbnew.F_Cu)) / 2, None])
        else:
            obstacles.append([t.GetNetname(), t.GetLayer(), [(xy(t.GetStart()), xy(t.GetEnd()))], mm(t.GetWidth()) / 2, t])
    for p in brd.GetPads():
        bb = p.GetBoundingBox()
        x0, y0, x1, y1 = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
        box = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0)),
               ((x0, y0), (x1, y1))]
        obstacles.append([p.GetNetname(), None if p.HasHole() else p.GetLayer(), box, 0.0, None])
    done, left = 0, 0
    for ob in obstacles:
        t = ob[4]
        want = targets.get(ob[0]) if t is not None else None
        if not want or mm(t.GetWidth()) >= want - 1e-6:
            continue
        a, b = xy(t.GetStart()), xy(t.GetEnd())
        room = min((seg_seg(a, b, c, d) - r for net, lay, segs, r, _ in obstacles
                    if net != t.GetNetname() and lay in (None, t.GetLayer()) for c, d in segs), default=9)
        w = min(want, math.floor((2 * (room - clear - 0.01)) * 100) / 100)
        if w > mm(t.GetWidth()) + 1e-6:
            t.SetWidth(pcbnew.FromMM(w))
            ob[3] = w / 2          # later segments must keep clear of the new width
            done += 1
        if mm(t.GetWidth()) < want - 1e-6:
            left += 1
    return done, left


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
        if getattr(mod, "WIDEN", None):
            n, left = widen_tracks(bd.b, mod.WIDEN, mod.router_config(bd).get("clear", 0.15))
            print(f"[{name}] widened {n} necked-down supply segment(s); still below target: {left}")
    if hasattr(mod, "post_route"):
        mod.post_route(bd)
    bd.fill()
    project()
    viol, unconn, parity = outputs.drc(proj, name, rep)
    for _pass in range(6):
        stubs = [v for v in viol if v["type"] == "track_dangling"]
        if not stubs:
            break
        import pcbnew
        brd = pcbnew.LoadBoard(bd.path)
        removed = 0
        for v in stubs:
            x, y = v["items"][0]["pos"]["x"], v["items"][0]["pos"]["y"]
            for t in list(brd.GetTracks()):
                if t.Type() == pcbnew.PCB_TRACE_T and t.GetLength() < pcbnew.FromMM(0.12) and \
                        abs(pcbnew.ToMM(t.GetStart().x) - x) < 0.2 and abs(pcbnew.ToMM(t.GetStart().y) - y) < 0.2:
                    brd.Remove(t)
                    removed += 1
        bd.b = brd                 # fill() saves bd.b, reloads it and fills the zones
        bd.fill()
        project()
        viol, unconn, parity = outputs.drc(proj, name, rep)
        print(f"[{name}] removed {removed} leftover stub(s)")
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
        outputs.fab(proj, name, fab, copper, hand=[r for r, p in d.parts.items() if p.fields.get("Assembly") == "hand"],
                    lcsc={r: p.fields.get("LCSC", "") for r, p in d.parts.items()})
        outputs.bom(d, fab)
        outputs.docs(proj, name, os.path.join(ROOT, "docs", "boards", name), copper)
        print(f"[{name}] fab + docs written")


if __name__ == "__main__":
    main()
