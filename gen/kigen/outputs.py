"""ERC/DRC and manufacturing outputs via kicad-cli."""
import csv
import json
import os
import subprocess


def run(cmd, check=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def erc(proj_dir, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rpt = os.path.join(out_dir, f"{name}-erc.json")
    run(["kicad-cli", "sch", "erc", os.path.join(proj_dir, f"{name}.kicad_sch"), "-o", rpt,
         "--format", "json", "--severity-all"])
    data = json.load(open(rpt))
    viol = [v for sh in data.get("sheets", []) for v in sh.get("violations", [])]
    return viol


def drc(proj_dir, name, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rpt = os.path.join(out_dir, f"{name}-drc.json")
    run(["kicad-cli", "pcb", "drc", os.path.join(proj_dir, f"{name}.kicad_pcb"), "-o", rpt,
         "--format", "json", "--severity-all", "--schematic-parity"])
    data = json.load(open(rpt))
    return data.get("violations", []), data.get("unconnected_items", []), data.get("schematic_parity", [])


def summarize(items):
    out = {}
    for v in items:
        k = (v.get("severity", "?"), v.get("type", "?"))
        out[k] = out.get(k, 0) + 1
    return out


def netlist(proj_dir, name, out_dir):
    out = os.path.join(out_dir, f"{name}.net")
    run(["kicad-cli", "sch", "export", "netlist", os.path.join(proj_dir, f"{name}.kicad_sch"), "-o", out], check=True)
    return out


def compare_netlist(design, netfile):
    """Check that the netlist KiCad extracts from the generated schematic equals the Python model."""
    from .sexpr import parse, find, findall
    tree = parse(open(netfile).read())
    kicad = {}
    for net in findall(find(tree, "nets"), "net"):
        name = find(net, "name")[1]
        for node in findall(net, "node"):
            kicad[(find(node, "ref")[1], find(node, "pin")[1])] = name.lstrip("/")
    model = {}
    for netname, nodes in design.nets().items():
        for ref, pin in nodes:
            model[(ref, pin)] = netname
    errs = []
    for k, v in model.items():
        if kicad.get(k) != v:
            errs.append(f"{k[0]}.{k[1]}: model={v} schematic={kicad.get(k)}")
    for k, v in kicad.items():
        if k not in model and not v.startswith("unconnected-"):
            errs.append(f"{k[0]}.{k[1]}: schematic={v} but not in model")
    return errs


def fab(proj_dir, name, out_dir, layers):
    pcb = os.path.join(proj_dir, f"{name}.kicad_pcb")
    g = os.path.join(out_dir, "gerbers")
    os.makedirs(g, exist_ok=True)
    for f in os.listdir(g):
        os.remove(os.path.join(g, f))
    lay = ",".join(layers + ["F.Paste", "B.Paste", "F.SilkS", "B.SilkS", "F.Mask", "B.Mask", "Edge.Cuts"])
    run(["kicad-cli", "pcb", "export", "gerbers", pcb, "-o", g + "/", "--layers", lay,
         "--subtract-soldermask", "--no-protel-ext" if False else "--use-drill-file-origin"], check=True)
    run(["kicad-cli", "pcb", "export", "drill", pcb, "-o", g + "/", "--format", "excellon",
         "--drill-origin", "plot", "--excellon-separate-th", "--generate-map", "--map-format", "pdf",
         "--excellon-units", "mm"], check=True)
    pos = os.path.join(out_dir, f"{name}-pos.csv")
    run(["kicad-cli", "pcb", "export", "pos", pcb, "-o", pos, "--format", "csv", "--units", "mm",
         "--side", "both", "--use-drill-file-origin", "--exclude-dnp"], check=True)
    # JLCPCB CPL format
    rows = list(csv.DictReader(open(pos)))
    with open(os.path.join(out_dir, f"{name}-cpl-jlc.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in rows:
            w.writerow([r["Ref"], r["PosX"], r["PosY"], "Top" if r["Side"] == "top" else "Bottom", r["Rot"]])
    zipf = os.path.join(out_dir, f"{name}-gerbers.zip")
    if os.path.exists(zipf):
        os.remove(zipf)
    run(["zip", "-j", "-q", zipf] + [os.path.join(g, f) for f in sorted(os.listdir(g)) if not f.endswith(".pdf")])
    run(["kicad-cli", "pcb", "export", "ipcd356", pcb, "-o", os.path.join(out_dir, f"{name}.d356")])


def bom(design, out_dir, side_of=None):
    groups = {}
    for p in design.parts.values():
        if p.fields.get("BOM", "yes") == "no":
            continue
        key = (p.value, p.footprint, p.fields.get("MPN", ""), p.fields.get("LCSC", ""), p.dnp)
        groups.setdefault(key, []).append(p.ref)

    def refkey(r):
        import re
        m = re.match(r"([A-Za-z]+)(\d+)", r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)
    rows = []
    for (value, fpn, mpn, lcsc, dnp), refs in groups.items():
        p0 = design.parts[refs[0]]
        rows.append(dict(refs=sorted(refs, key=refkey), qty=len(refs), value=value, footprint=fpn.split(":")[1],
                         mfr=p0.fields.get("Manufacturer", ""), mpn=mpn, lcsc=lcsc, dnp=dnp,
                         descr=p0.fields.get("Description", ""), price=p0.fields.get("Price", "")))
    rows.sort(key=lambda r: refkey(r["refs"][0]))
    with open(os.path.join(out_dir, f"{design.name}-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Designators", "Qty", "Value", "Description", "Footprint", "Manufacturer", "MPN", "LCSC",
                    "Unit price USD", "Fit"])
        for r in rows:
            w.writerow([" ".join(r["refs"]), r["qty"], r["value"], r["descr"], r["footprint"], r["mfr"], r["mpn"],
                        r["lcsc"], r["price"], "DNP" if r["dnp"] else "yes"])
    with open(os.path.join(out_dir, f"{design.name}-bom-jlc.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for r in rows:
            if not r["dnp"] and r["lcsc"]:
                w.writerow([r["value"], ",".join(r["refs"]), r["footprint"], r["lcsc"]])
    return rows


def docs(proj_dir, name, out_dir, layers):
    pcb = os.path.join(proj_dir, f"{name}.kicad_pcb")
    os.makedirs(out_dir, exist_ok=True)
    run(["kicad-cli", "sch", "export", "pdf", os.path.join(proj_dir, f"{name}.kicad_sch"), "-o",
         os.path.join(out_dir, f"{name}-schematic.pdf")], check=True)
    for side, rot in (("top", ""), ("bottom", "")):
        run(["kicad-cli", "pcb", "render", pcb, "-o", os.path.join(out_dir, f"{name}-{side}.png"), "--side", side,
             "-w", "1600", "-h", "1600", "--quality", "high", "--background", "opaque"])
    run(["kicad-cli", "pcb", "render", pcb, "-o", os.path.join(out_dir, f"{name}-angle-top.png"), "--side", "top",
         "-w", "1600", "-h", "1200", "--quality", "high", "--perspective", "--rotate", "-50,0,25",
         "--background", "opaque"])
    run(["kicad-cli", "pcb", "render", pcb, "-o", os.path.join(out_dir, f"{name}-angle-bottom.png"), "--side", "bottom",
         "-w", "1600", "-h", "1200", "--quality", "high", "--perspective", "--rotate", "50,0,25",
         "--background", "opaque"])
    for l in layers:
        run(["kicad-cli", "pcb", "export", "svg", pcb, "-o", os.path.join(out_dir, f"{name}-{l.replace('.', '_')}.svg"),
             "--layers", f"{l},Edge.Cuts", "--mode-single", "--page-size-mode", "2", "--exclude-drawing-sheet"])
    run(["kicad-cli", "pcb", "export", "svg", pcb, "-o", os.path.join(out_dir, f"{name}-assembly-top.svg"),
         "--layers", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "--page-size-mode", "2", "--exclude-drawing-sheet"])
    run(["kicad-cli", "pcb", "export", "svg", pcb, "-o", os.path.join(out_dir, f"{name}-assembly-bottom.svg"),
         "--layers", "B.Fab,B.SilkS,Edge.Cuts", "--mode-single", "--page-size-mode", "2", "--exclude-drawing-sheet",
         "--mirror"])
    run(["kicad-cli", "pcb", "export", "glb", pcb, "-o", os.path.join(out_dir, f"{name}.glb"), "--subst-models",
         "--include-tracks", "--include-pads", "--include-zones", "--include-silkscreen", "--include-soldermask",
         "--user-origin", "100x100mm", "--force"])
    run(["kicad-cli", "pcb", "export", "step", pcb, "-o", os.path.join(out_dir, f"{name}.step"), "--subst-models",
         "--user-origin", "100x100mm", "--force"])
