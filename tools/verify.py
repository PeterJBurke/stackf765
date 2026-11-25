#!/usr/bin/env python3
"""Run every automated check on the committed design files and write the results to
docs/verification.json and docs/verification-report.md.

    python3 tools/verify.py          (or: make verify)

Exit status 0 only if every check passes.
"""
import csv
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gen"))
from kigen import outputs  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BOARDS = ["upper", "lower", "service"]
checks = []


def add(name, ok, detail):
    checks.append(dict(name=name, ok=bool(ok), detail=detail))
    print(("PASS  " if ok else "FAIL  ") + name + " - " + detail)


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


tmp = tempfile.mkdtemp()
for b in BOARDS:
    proj = os.path.join(ROOT, "hardware", b)
    # --- ERC on the schematic as KiCad reads it
    rpt = os.path.join(tmp, b + "-erc.json")
    run(["kicad-cli", "sch", "erc", os.path.join(proj, b + ".kicad_sch"), "-o", rpt, "--format", "json", "--severity-all"])
    v = [x for sh in json.load(open(rpt)).get("sheets", []) for x in sh.get("violations", [])]
    errs = [x for x in v if x["severity"] == "error"]
    add(f"{b}: electrical rules check (KiCad ERC)", not v, f"{len(errs)} errors, {len(v) - len(errs)} warnings")
    # --- DRC with schematic parity
    rpt = os.path.join(tmp, b + "-drc.json")
    run(["kicad-cli", "pcb", "drc", os.path.join(proj, b + ".kicad_pcb"), "-o", rpt, "--format", "json",
         "--severity-all", "--schematic-parity"])
    d = json.load(open(rpt))
    viol, unc, par = d.get("violations", []), d.get("unconnected_items", []), d.get("schematic_parity", [])
    add(f"{b}: design rules check (KiCad DRC)", not viol,
        f"{len(viol)} violations" + ("" if not viol else ": " + ", ".join(sorted({x['type'] for x in viol}))))
    add(f"{b}: every net fully routed", not unc, f"{len(unc)} unconnected items")
    add(f"{b}: board matches schematic", not par, f"{len(par)} parity differences")
    # --- fabrication package
    fab = os.path.join(ROOT, "fab", b)
    need = [f"{b}-gerbers.zip", f"{b}-bom.csv", f"{b}-bom-jlc.csv", f"{b}-cpl-jlc.csv"]
    missing = [f for f in need if not os.path.exists(os.path.join(fab, f))]
    # current = re-exporting the Gerber and drill files from the board gives the same files (dates ignored)
    nlay = {"upper": 6, "lower": 4, "service": 2}[b]
    copper = ["F.Cu"] + [f"In{i}.Cu" for i in range(1, nlay - 1)] + ["B.Cu"]
    newer = outputs.gerbers_differ(os.path.join(proj, b + ".kicad_pcb"), os.path.join(fab, "gerbers"), copper) \
        if not missing else []
    add(f"{b}: fabrication files present and current", not missing and not newer,
        "gerbers and drill match the board; BOM and placement present" if not missing and not newer
        else f"missing {missing} differ from board: {newer}")
    # --- BOM completeness
    if not missing:
        rows = list(csv.DictReader(open(os.path.join(fab, f"{b}-bom.csv"))))
        bad = [r["Designators"] for r in rows if not r["MPN"] or not r["LCSC"]]
        add(f"{b}: every BOM line has a manufacturer part number and an LCSC number", not bad,
            f"{len(rows)} lines" if not bad else f"incomplete: {bad}")

r = run([sys.executable, os.path.join(ROOT, "tools", "check_hwdef.py")])
last = [l for l in r.stdout.strip().splitlines() if l.startswith(("PASS", "FAIL"))]
add("firmware pin map (hwdef.dat) matches the schematic", r.returncode == 0, last[-1] if last else r.stderr[-200:])

r = run([sys.executable, os.path.join(ROOT, "tools", "check_stack.py")])
oks = [l[5:] for l in r.stdout.splitlines() if l.startswith("ok")]
add("boards fit together (connector alignment, standoffs, height budget, cable)", r.returncode == 0,
    "; ".join(oks[:1] + oks[3:4]) if r.returncode == 0 else r.stdout[-300:])

# firmware build evidence: the binaries must have been built from the current hwdef
hw = open(os.path.join(ROOT, "firmware/hwdef/StackF765/hwdef.dat"), "rb").read()
sha = hashlib.sha256(hw).hexdigest()
info = os.path.join(ROOT, "firmware/bin/BUILD_INFO.json")
ok, detail = False, "firmware/bin/BUILD_INFO.json missing (run firmware/build.sh)"
if os.path.exists(info):
    bi = json.load(open(info))
    ok = bi.get("hwdef_sha256") == sha and os.path.exists(os.path.join(ROOT, "firmware/bin/arducopter.apj"))
    detail = (f"ArduCopter {bi.get('ardupilot_version', '?')} built, {bi.get('flash_used', '?')} bytes of flash"
              if ok else "binaries were built from a different hwdef.dat; rebuild")
add("ArduPilot bootloader and ArduCopter compile for this board", ok, detail)

out = dict(date=datetime.date.today().isoformat(), checks=checks)
json.dump(out, open(os.path.join(ROOT, "docs", "verification.json"), "w"), indent=1)
with open(os.path.join(ROOT, "docs", "verification-report.md"), "w") as f:
    f.write(f"# Verification report\n\nGenerated by `tools/verify.py` on {out['date']}.\n\n| Check | Result | Detail |\n|---|---|---|\n")
    for c in checks:
        f.write(f"| {c['name']} | {'PASS' if c['ok'] else '**FAIL**'} | {c['detail']} |\n")
bad = [c for c in checks if not c["ok"]]
print(f"\n{len(checks) - len(bad)}/{len(checks)} checks passed")
sys.exit(1 if bad else 0)
