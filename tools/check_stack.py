#!/usr/bin/env python3
"""Mechanical / inter-board consistency checks on the three finished PCBs.

  1. Board-to-board connector: every upper-board header pad sits exactly above the
     lower-board socket pad with the same number, and both carry the same net.
  2. Standoffs on the lower board line up with screw holes on the upper board.
  3. Both main boards have the same outline.
  4. Height budget in the 8.0 mm gap: (lower-board top part height) + (upper-board
     bottom part height) must fit wherever two parts overlap in plan view.  The solder
     tails of both upper-board pin headers count as parts, and so do the power-wire joints
     on the lower board.  The lower board must carry no pin header.
  5. Grommet nut zones (lower board 20 x 20 mm mounting) are free of lower-board parts,
     and only low parts of the upper board hang above them.
  6. Service cable: the 6 pins carry the same nets at both ends (1:1 cable).

    python3 tools/check_stack.py
"""
import math
import os
import sys
import pcbnew

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GAP = 8.0            # mm between the boards (standoff height)
TAIL = 1.8           # mm: upper header solder tails below the upper board, untrimmed, worst case (research/header-clearance.md)
WIRE_H = 5.0         # mm allowed for a 12 AWG wire and its solder joint above each battery / ESC pad
NUT_ZONE_R = 3.5     # mm radius reserved around each grommet centre
NUT_HEIGHT = 4.0     # mm: grommet flange + M2 nut + screw end above the lower board (estimate)
GROMMETS = [(-10, 10), (10, 10), (-10, -10), (10, -10)]

# part heights above their board surface, by footprint name fragment (mm)
HEIGHTS = [("Samtec_SFMC", 4.7), ("Samtec_FTSH", 2.92), ("Standoff", 8.0), ("L_SXN", 3.0), ("D_SMB", 2.4), ("R_Shunt", 0.6), ("SOT-583", 0.6), ("SC-70", 1.1),
           ("SOT-23", 1.2), ("LED_0603", 0.7), ("C_0805", 1.35), ("C_1206", 1.8), ("R_0805", 0.6), ("R_1206", 0.65), ("D_SOD-123F", 1.1), ("C_0603", 0.9), ("L_0603", 0.9), ("C_0402", 0.6),
           ("R_0402", 0.4), ("Crystal_SMD_3225", 0.8), ("TestPoint", 0.05), ("WirePad", WIRE_H), ("NetTie", 0.0), ("microSD", 1.5),
           ("Hole", 0.0)]

errors, notes = [], []


def load(name):
    return pcbnew.LoadBoard(os.path.join(ROOT, "hardware", name, name + ".kicad_pcb"))


def mm(v):
    return (round(pcbnew.ToMM(v.x) - 100, 3), round(100 - pcbnew.ToMM(v.y), 3))


def height(fp):
    n = str(fp.GetFPID().GetLibItemName())
    for frag, h in HEIGHTS:
        if frag in n:
            return h
    return None


def bbox(fp):
    side = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(side)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    x0, y1 = mm(bb.GetOrigin())
    x1, y0 = mm(bb.GetEnd())
    return x0, y0, x1, y1


lower, upper, service = load("lower"), load("upper"), load("service")
L = {fp.GetReference(): fp for fp in lower.GetFootprints()}
U = {fp.GetReference(): fp for fp in upper.GetFootprints()}
S = {fp.GetReference(): fp for fp in service.GetFootprints()}

# 1. board-to-board connector
lp = {p.GetNumber(): p for p in L["J1"].Pads()}
up = {p.GetNumber(): p for p in U["J3"].Pads()}
worst = 0.0
for n in sorted(lp, key=int):
    a, b = mm(lp[n].GetPosition()), mm(up[n].GetPosition())
    d = math.hypot(a[0] - b[0], a[1] - b[1])
    worst = max(worst, d)
    cy = mm(L["J1"].GetPosition())[1]
    if abs(a[0] - b[0]) > 0.05 or abs(a[1] - b[1]) > 0.8 or (a[1] > cy) != (b[1] > cy):   # same column, same row side (row spacing differs by design)
        errors.append(f"B2B pin {n}: lower pad at {a}, upper pad at {b}")
    if lp[n].GetNetname() != up[n].GetNetname():
        errors.append(f"B2B pin {n}: lower net {lp[n].GetNetname()} != upper net {up[n].GetNetname()}")
    if not U["J3"].IsFlipped() or L["J1"].IsFlipped():
        errors.append("B2B: socket must be on lower top, header on upper bottom")
if mm(L["J1"].GetPosition()) != mm(U["J3"].GetPosition()):
    errors.append(f"B2B: connector centres differ: lower {mm(L['J1'].GetPosition())}, upper {mm(U['J3'].GetPosition())}")
notes.append(f"board-to-board: 20 pins aligned (worst offset {worst:.3f} mm) and nets identical")

# 2. standoffs vs screw holes
holes = [mm(p.GetPosition()) for fp in upper.GetFootprints() for p in fp.Pads()
         if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
for ref in ("H1", "H2", "H3"):
    pos = mm(L[ref].GetPosition())
    if not any(math.hypot(pos[0] - h[0], pos[1] - h[1]) < 0.05 for h in holes):
        errors.append(f"standoff {ref} at {pos} has no matching hole on the upper board")
notes.append("3 standoffs line up with upper-board screw holes")

# 3. outline
def outline(b):
    bb = b.GetBoardEdgesBoundingBox()
    return round(pcbnew.ToMM(bb.GetWidth()), 2), round(pcbnew.ToMM(bb.GetHeight()), 2)


if outline(lower) != outline(upper):
    errors.append(f"outlines differ: lower {outline(lower)} upper {outline(upper)}")
notes.append(f"main board outline {outline(lower)[0]} x {outline(lower)[1]} mm (incl. 0.1 mm line width)")

# 4. height budget
unknown = set()
def named(b):
    return [fp for fp in b.GetFootprints() if str(fp.GetFPID().GetLibItemName())]


def shape(fp):
    """Plan-view extent used for the checks.  Standoffs are round; the 2x10 header is tall only at its body."""
    n = str(fp.GetFPID().GetLibItemName())
    b = bbox(fp)
    if "Standoff" in n:
        x, y = mm(fp.GetPosition())
        r = 2.78 * 0.7072 + 0.2          # square inscribed in the 5.56 mm body, plus margin
        return (x - r, y - r, x + r, y + r)
    return b


ltop, ubot = [], []
for fp in named(lower):
    if fp.IsFlipped():
        continue
    if "PinHeader_3x" in str(fp.GetFPID().GetLibItemName()):
        errors.append(f"lower {fp.GetReference()}: the lower board must carry no pin header (it would sit under the upper headers)")
    ltop.append((fp, shape(fp), height(fp)))
ubot = [(fp, shape(fp), height(fp)) for fp in named(upper) if fp.IsFlipped()]
# solder tails of the upper board's two pin headers: one per pin, TAIL below the upper board
tails = []
for ref in ("J1", "J2"):
    if ref not in U or not U[ref].Models().size() or U[ref].IsFlipped():
        errors.append(f"upper {ref}: pin header missing, without a 3D model, or on the wrong side")
        continue
    for pad in U[ref].Pads():
        x, y = mm(pad.GetPosition())
        tails.append((ref, (x - 0.4, y - 0.4, x + 0.4, y + 0.4), TAIL))
tight = (GAP, "")
for fa, ba, ha in ltop:
    if ha is None:
        unknown.add(str(fa.GetFPID().GetLibItemName()))
        continue
    for fb, bb_, hb in ubot + tails:
        if hb is None:
            unknown.add(str(fb.GetFPID().GetLibItemName()))
            continue
        if not isinstance(fb, str) and {fa.GetReference(), fb.GetReference()} == {"J1", "J3"}:
            continue        # the mating connector pair
        if ba[0] < bb_[2] and bb_[0] < ba[2] and ba[1] < bb_[3] and bb_[1] < ba[3]:
            margin = GAP - ha - hb
            name = f"{fa.GetReference()} (lower, {ha} mm) under {fb + ' pin tails' if isinstance(fb, str) else fb.GetReference()} (upper, {hb} mm)"
            if margin < tight[0]:
                tight = (margin, name)
            if margin < 0.3:
                errors.append(f"height clash: {name}: margin {margin:.2f} mm")
if unknown:
    errors.append(f"no height data for footprints: {sorted(unknown)}")
notes.append(f"height budget in the {GAP} mm gap OK; tightest: {tight[1]} -> {tight[0]:.2f} mm spare")
notes.append(f"no pin header on the lower board; {GAP - WIRE_H - TAIL:.1f} mm between a {WIRE_H} mm power-wire joint and "
             f"untrimmed rear-header tails")

# 5. grommet nut zones
for gx, gy in GROMMETS:
    for fp, b, h in ltop:
        cx, cy = min(max(gx, b[0]), b[2]), min(max(gy, b[1]), b[3])
        if math.hypot(cx - gx, cy - gy) < NUT_ZONE_R:
            errors.append(f"lower {fp.GetReference()} is inside the grommet zone at ({gx},{gy})")
    for fp, b, h in ubot:
        cx, cy = min(max(gx, b[0]), b[2]), min(max(gy, b[1]), b[3])
        if math.hypot(cx - gx, cy - gy) < NUT_ZONE_R and (h or 9) > GAP - NUT_HEIGHT - 0.3:
            errors.append(f"upper {fp.GetReference()} ({h} mm) hangs over the grommet nut at ({gx},{gy})")
notes.append("grommet nut zones clear")

# 6. service cable
a = {p.GetNumber(): p.GetNetname() for p in U["J5"].Pads() if p.GetNumber().isdigit()}
b = {p.GetNumber(): p.GetNetname() for p in S["J2"].Pads() if p.GetNumber().isdigit()}
if a != b:
    errors.append(f"service cable pin nets differ: upper {a} service {b}")
notes.append("service cable: " + "  ".join(f"{k}={v}" for k, v in sorted(a.items())))

for n in notes:
    print("ok  ", n)
if errors:
    print(f"FAIL: {len(errors)} problems")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("PASS: stack checks")
