"""Generate the project-specific footprints in hardware/lib/fc.pretty.

Run with the system python:  python3 gen/make_footprints.py
(3D models are produced separately by gen/make_models.py, which needs CadQuery.)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hardware", "lib", "fc.pretty")
os.makedirs(OUT, exist_ok=True)
MODEL = "${KIPRJMOD}/../lib/3d/"


def fp(name, descr, body, attr="through_hole", model=None):
    s = f'(footprint "{name}"\n  (version 20241229) (generator "fcgen") (layer "F.Cu")\n  (descr "{descr}")\n'
    s += f'  (property "Reference" "REF**" (at 0 -3 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    s += f'  (property "Value" "{name}" (at 0 3 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    s += f'  (attr {attr})\n' + body
    if model:
        s += f'  (model "{MODEL}{model}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
    s += ")\n"
    with open(os.path.join(OUT, name + ".kicad_mod"), "w") as f:
        f.write(s)


def line(x1, y1, x2, y2, layer="F.SilkS", w=0.12):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'


def rect(x1, y1, x2, y2, layer, w=0.1):
    return f'  (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'


def circle(x, y, r, layer, w=0.1):
    return f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + r:.3f} {y:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))\n'


# Samtec SFMC-1xx-02 socket land pattern (pad length, row centre), see research/samtec-b2b.md
SFMC_PAD_LEN, SFMC_ROW_C = 2.22, 1.365      # Samtec footprint SFMC-D-SM rev D: pads 0.74 x 2.22, outer span 4.95

# ---------------------------------------------------------------------------
# 3 x 12 right-angle 2.54 mm pin header (HCTL PZ254-3-xx-W-2.5 / Samtec TSW-112-08-x-T-RA)
# Rows along +X: A (x=0, highest pins), B (x=2.54), C (x=5.08, lowest pins, nearest the body).
# Columns 1..12 along +Y.  Pins point to +X.  Body rear 1.96 mm in front of row C.
def header_3xN(n):
    b = ""
    for col in range(n):
        y = col * 2.54
        for r, row in enumerate("ABC"):
            shape = "rect" if (row == "A" and col == 0) else "circle"
            b += (f'  (pad "{row}{col + 1}" thru_hole {shape} (at {r * 2.54:.2f} {y:.2f}) (size 1.6 1.6) '
                  f'(drill 1.02) (layers "*.Cu" "*.Mask"))\n')
    y0, y1 = -1.27, (n - 1) * 2.54 + 1.27
    bx0, bx1, tip = 5.08 + 1.96, 5.08 + 4.46, 5.08 + 10.46
    b += rect(bx0, y0, bx1, y1, "F.Fab")
    b += rect(bx0 - 0.06, y0 - 0.06, bx1 + 0.06, y1 + 0.06, "F.SilkS", 0.12)
    for col in range(n):
        y = col * 2.54
        b += rect(bx1, y - 0.32, tip, y + 0.32, "F.Fab")
    b += rect(-1.3, y0 - 0.25, tip + 0.25, y1 + 0.25, "F.CrtYd", 0.05)
    fp(f"PinHeader_3x{n:02d}_P2.54mm_Horizontal",
       f"3x{n} right-angle pin header, 2.54 mm pitch, three rows (HCTL PZ254-3-xx-W-2.5, Samtec TSW-1xx-08-x-T-RA)",
       b, model=f"PinHeader_3x{n:02d}_P2.54mm_Horizontal.step")


# ---------------------------------------------------------------------------
# Wire solder pad (top copper only, with a field of plated vias to share current
# across all layers).  5.0 x 4.0 mm, long axis along X.
def wire_pad(name, w, h, via_pitch=1.25, via_drill=0.4, via_pad=0.8):
    b = f'  (pad "1" smd roundrect (at 0 0) (size {w} {h}) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.1))\n'
    nx, ny = int((w - 1.0) / via_pitch), int((h - 1.0) / via_pitch)
    for i in range(nx + 1):
        for j in range(ny + 1):
            x = (i - nx / 2) * via_pitch
            y = (j - ny / 2) * via_pitch
            b += (f'  (pad "1" thru_hole circle (at {x:.3f} {y:.3f}) (size {via_pad} {via_pad}) (drill {via_drill}) '
                  f'(layers "*.Cu"))\n')
    b += rect(-w / 2, -h / 2, w / 2, h / 2, "F.Fab")
    b += rect(-w / 2 - 0.05, -h / 2 - 0.05, w / 2 + 0.05, h / 2 + 0.05, "F.CrtYd", 0.05)
    fp(name, f"Solder pad for a power wire, {w} x {h} mm, via-stitched to all copper layers", b,
       attr="smd exclude_from_pos_files exclude_from_bom")


# ---------------------------------------------------------------------------
# Sinhoo SMTSO2060CTJ: reflow-solderable M2 round standoff, 6.0 mm tall,
# body dia 5.56, pilot dia 3.60 x 1.53 into the PCB.
def smt_standoff(name, height):
    b = ('  (pad "1" thru_hole circle (at 0 0) (size 6.2 6.2) (drill 3.75) (layers "*.Cu" "*.Mask") )\n')
    # paste ring split in four arcs approximated by 8 small pads on the annulus
    import math
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        x, y = 2.5 * math.cos(a), 2.5 * math.sin(a)
        b += (f'  (pad "1" smd circle (at {x:.3f} {y:.3f}) (size 0.9 0.9) (layers "F.Cu" "F.Paste"))\n')
    b += circle(0, 0, 2.78, "F.Fab")
    b += circle(0, 0, 3.35, "F.CrtYd", 0.05)
    fp(name, f"Sinhoo SMTSO20{int(height * 10):02d}CTJ reflow M2 standoff, {height} mm, dia 5.56, PCB hole 3.75", b,
       attr="smd", model=f"{name}.step")


# Plain M2 clearance hole with a screw-head keep-out ring (upper board).
def screw_hole(name, drill, head):
    b = (f'  (pad "" np_thru_hole circle (at 0 0) (size {drill} {drill}) (drill {drill}) (layers "*.Cu" "*.Mask"))\n')
    b += circle(0, 0, head / 2, "F.CrtYd", 0.05) + circle(0, 0, head / 2, "B.CrtYd", 0.05)
    b += circle(0, 0, head / 2, "F.Fab")
    fp(name, f"NPTH {drill} mm with {head} mm hardware keep-out", b, attr="exclude_from_pos_files exclude_from_bom")


def two_pad(name, descr, pw, ph, cx, body_w, body_h, model=None):
    b = ""
    for n, x in (("1", -cx), ("2", cx)):
        b += (f'  (pad "{n}" smd roundrect (at {x} 0) (size {pw} {ph}) (layers "F.Cu" "F.Paste" "F.Mask") '
              f'(roundrect_rratio 0.08))\n')
    b += rect(-body_w / 2, -body_h / 2, body_w / 2, body_h / 2, "F.Fab")
    ex, ey = max(cx + pw / 2, body_w / 2) + 0.25, max(ph, body_h) / 2 + 0.25
    b += rect(-ex, -ey, ex, ey, "F.CrtYd", 0.05)
    b += line(-body_w / 2, -ey + 0.1, body_w / 2, -ey + 0.1) + line(-body_w / 2, ey - 0.1, body_w / 2, ey - 0.1)
    fp(name, descr, b, attr="smd", model=model)


# SXN SMMS0530 moulded inductor: pads 2.0 x 2.5, centres +/-2.5 (datasheet land pattern)
two_pad("L_SXN_SMMS0530", "SXN SMMS0530 inductor 5.5x5.2x3.0 mm, pads 2.0x2.5 at +/-2.5", 2.0, 2.5, 2.5, 5.5, 5.2,
        model="L_SXN_SMMS0530.step")
# Yezhan ASR-M-3 2512 shunt: pads 1.8 x 3.4, overall span 7.0 (centres +/-2.6)
two_pad("R_Shunt_2512_ASR-M-3", "Yezhan ASR-M-3 2512 metal-strip shunt, pads 1.8x3.4, span 7.0", 1.8, 3.4, 2.6, 6.3, 3.1,
        model="R_Shunt_2512.step")

def bmp388():
    """Bosch BMP388/BMP581 LGA-10 2x2 mm.  Pad centres per Bosch datasheet (same as KiCad ST_HLGA-10),
    pad size per Bosch recommendation (land = package pad) to keep 0.15 mm+ pad-to-pad gaps."""
    b = ""
    P = {1: (-0.7625, -0.25), 2: (-0.7625, 0.25), 3: (-0.5, 0.7625), 4: (0, 0.7625), 5: (0.5, 0.7625),
         6: (0.7625, 0.25), 7: (0.7625, -0.25), 8: (0.5, -0.7625), 9: (0, -0.7625), 10: (-0.5, -0.7625)}
    for n, (x, y) in P.items():
        sx, sy = (0.325, 0.25) if abs(x) > 0.7 else (0.25, 0.325)
        b += f'  (pad "{n}" smd rect (at {x} {y}) (size {sx} {sy}) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
    b += rect(-1.0, -1.0, 1.0, 1.0, "F.Fab") + rect(-1.25, -1.25, 1.25, 1.25, "F.CrtYd", 0.05)
    b += circle(-1.45, -0.25, 0.08, "F.SilkS", 0.16)
    fp("Bosch_LGA-10_2x2mm_P0.5mm", "Bosch BMP388 / BMP581 LGA-10 2.0x2.0 mm", b, attr="smd",
       model="Bosch_LGA-10.step")


bmp388()
def b2b_127(name, descr, pad_len, row_c, first_pad_x_sign, body_w, body_len, model):
    """2x10 1.27 mm SMD connector.  Pads numbered like KiCad's PinHeader/PinSocket 1.27 mm footprints:
    pad 1 and 2 share the first row position (y = -5.715); first_pad_x_sign gives the side of pad 1,
    so that a header on the bottom of one board mates pad N to pad N of a socket on the top of the other."""
    b = ""
    for i in range(10):
        y = -5.715 + i * 1.27
        for k, sx in enumerate((first_pad_x_sign, -first_pad_x_sign)):
            b += (f'  (pad "{2 * i + 1 + k}" smd roundrect (at {sx * row_c:.3f} {y:.3f}) (size {pad_len} 0.74) '
                  f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))\n')
    b += rect(-body_w / 2, -body_len / 2, body_w / 2, body_len / 2, "F.Fab")
    ex, ey = row_c + pad_len / 2 + 0.25, body_len / 2 + 0.25
    b += rect(-ex, -ey, ex, ey, "F.CrtYd", 0.05)
    b += line(-body_w / 2, -ey + 0.1, body_w / 2, -ey + 0.1) + line(-body_w / 2, ey - 0.1, body_w / 2, ey - 0.1)
    b += circle(first_pad_x_sign * (row_c + pad_len / 2 + 0.1), -5.715 - 0.9, 0.1, "F.SilkS", 0.2)
    fp(name, descr, b, attr="smd", model=model)


# Samtec FTSH-110-xx-x-DV terminal strip: pads 0.74 x 2.79, outer span 6.86 (Samtec footprint rev H)
b2b_127("Samtec_FTSH-110-xx-x-DV", "Samtec FTSH-110-xx-x-DV 2x10 1.27 mm SMT terminal strip", 2.79, 2.035, -1, 3.43, 12.7,
        "Samtec_FTSH-110-04-x-DV.step")
# Samtec SFMC-110-02-x-D socket: land pattern per research/samtec-b2b.md
b2b_127("Samtec_SFMC-110-02-x-D", "Samtec SFMC-110-02-x-D 2x10 1.27 mm SMT socket", SFMC_PAD_LEN, SFMC_ROW_C, 1, 3.05, 13.08,
        "Samtec_SFMC-110-02-x-D.step")

header_3xN(12)
header_3xN(9)
smt_standoff("Standoff_SMT_M2_H8.0", 8.0)
wire_pad("WirePad_5x4mm", 5.0, 4.0)
smt_standoff("Standoff_SMT_M2_H6.0", 6.0)
screw_hole("Hole_M2_Screw", 2.2, 4.2)
screw_hole("Hole_Grommet_4mm", 4.0, 7.0)
print("footprints written to", os.path.normpath(OUT))
