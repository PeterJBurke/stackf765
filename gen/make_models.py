"""Generate STEP models for the project-specific footprints (needs CadQuery).

    python gen/make_models.py        # in an environment with `pip install cadquery`
"""
import os
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hardware", "lib", "3d")
os.makedirs(OUT, exist_ok=True)


def save(assy, name):
    assy.save(os.path.join(OUT, name + ".step"))
    print("wrote", name)


def header_3xN(n):
    """Model frame: footprint origin, X as footprint X, Y = -footprint Y, Z up from the PCB top."""
    bx0, bx1, tip = 5.08 + 1.96, 5.08 + 4.46, 5.08 + 10.46
    heights = {0: 6.29, 1: 3.75, 2: 1.21}       # row A/B/C pin height above the PCB
    y_len = n * 2.54
    body = (cq.Workplane("XY").box(bx1 - bx0, y_len, 7.5, centered=False)
            .translate((bx0, -(n - 1) * 2.54 - 1.27, 0)))
    pins = None
    s = 0.64
    for col in range(n):
        y = -col * 2.54
        for r in range(3):
            x, z = r * 2.54, heights[r]
            vert = cq.Workplane("XY").box(s, s, z + 3.0 - 1.6 + 1.6 + s / 2, centered=(True, True, False)).translate((x, y, -3.0))
            hor = cq.Workplane("XY").box(tip - x + s / 2, s, s, centered=(False, True, True)).translate((x - s / 2, y, z))
            p = vert.union(hor)
            pins = p if pins is None else pins.union(p)
    a = cq.Assembly()
    a.add(body, name="body", color=cq.Color(0.08, 0.08, 0.08))
    a.add(pins, name="pins", color=cq.Color(0.85, 0.68, 0.25))
    save(a, f"PinHeader_3x{n:02d}_P2.54mm_Horizontal")


def standoff(name, h):
    body = cq.Workplane("XY").circle(5.56 / 2).circle(0.8).extrude(h)
    pilot = cq.Workplane("XY").circle(3.6 / 2).circle(0.8).extrude(-1.53)
    a = cq.Assembly()
    a.add(body.union(pilot), name="standoff", color=cq.Color(0.8, 0.8, 0.82))
    save(a, name)


header_3xN(12)
standoff("Standoff_SMT_M2_H6.0", 6.0)


def block(name, w, h, z, color, term=None):
    a = cq.Assembly()
    a.add(cq.Workplane("XY").box(w, h, z, centered=(True, True, False)), name="body", color=cq.Color(*color))
    save(a, name)


block("L_SXN_SMMS0530", 5.5, 5.2, 3.0, (0.25, 0.25, 0.27))
block("R_Shunt_2512", 6.3, 3.1, 0.6, (0.75, 0.6, 0.45))
block("Bosch_LGA-10", 2.0, 2.0, 0.75, (0.75, 0.75, 0.78))


# ---- simple stand-in models for library footprints that ship without a 3D model -------------
def shell(name, x0, y0, x1, y1, z, color, extra=None):
    """Box given in footprint coordinates (Y down); converted to model coordinates (Y up)."""
    a = cq.Assembly()
    body = cq.Workplane("XY").box(x1 - x0, y1 - y0, z, centered=False).translate((x0, -y1, 0))
    a.add(body, name="body", color=cq.Color(*color))
    if extra:
        for i, (ex0, ey0, ex1, ey1, ez0, ez1, ecol) in enumerate(extra):
            e = cq.Workplane("XY").box(ex1 - ex0, ey1 - ey0, ez1 - ez0, centered=False).translate((ex0, -ey1, ez0))
            a.add(e, name=f"part{i}", color=cq.Color(*ecol))
    save(a, name)


SILVER, BLACK = (0.78, 0.78, 0.8), (0.1, 0.1, 0.1)
shell("USB_C_Receptacle_HRO_TYPE-C-31-M-12", -4.47, -3.7, 4.47, 3.7, 3.2, SILVER,
      extra=[(-3.6, 3.2, 3.6, 3.75, 0.6, 2.6, BLACK)])
shell("MagneticBuzzer_CUI_CMT-8504-100-SMT", -4.25, -4.25, 4.25, 4.25, 3.0, BLACK)
shell("SW_Push_1P1T_XKB_TS-1187A", -2.55, -2.55, 2.55, 2.55, 1.1, SILVER,
      extra=[(-1.2, -1.2, 1.2, 1.2, 1.1, 1.5, BLACK)])
shell("microSD_HC_Molex_104031-0811", -5.975, -5.7, 5.975, 5.7, 1.42, SILVER,
      extra=[(-5.5, -9.7, 5.5, -5.7, 0.5, 1.2, (0.15, 0.15, 0.35))])


# ---- coloured replacements for library connector models (the library STEP files export without colour) ----
GOLD = (0.85, 0.68, 0.25)


def header_2xN_ra(n):
    body = cq.Workplane("XY").box(2.5, n * 2.54, 5.0, centered=False).translate((4.40, -(n - 1) * 2.54 - 1.27, 0))
    pins = None
    s = 0.64
    for col in range(n):
        y = -col * 2.54
        for x, z in ((0.0, 3.77), (2.54, 1.23)):
            vert = cq.Workplane("XY").box(s, s, z + 3.0 + s / 2, centered=(True, True, False)).translate((x, y, -3.0))
            hor = cq.Workplane("XY").box(12.9 - x + s / 2, s, s, centered=(False, True, True)).translate((x - s / 2, y, z))
            p = vert.union(hor)
            pins = p if pins is None else pins.union(p)
    a = cq.Assembly()
    a.add(body, name="body", color=cq.Color(*BLACK))
    a.add(pins, name="pins", color=cq.Color(*GOLD))
    save(a, f"PinHeader_2x{n:02d}_P2.54mm_Horizontal")


def socket_127(n):
    L = n * 1.27 + 0.4
    body = cq.Workplane("XY").box(3.0, L, 4.3, centered=(True, True, False)).translate((0, 0, 0.3))
    holes = None
    leads = None
    for i in range(n):
        y = (i - (n - 1) / 2) * 1.27
        for x in (-0.635, 0.635):
            h = cq.Workplane("XY").box(0.6, 0.6, 3.6, centered=(True, True, False)).translate((x, y, 1.1))
            holes = h if holes is None else holes.union(h)
        for x in (-1.9, 1.9):
            l = cq.Workplane("XY").box(1.4, 0.4, 0.3, centered=(True, True, False)).translate((x, y, 0))
            leads = l if leads is None else leads.union(l)
    a = cq.Assembly()
    a.add(body.cut(holes), name="body", color=cq.Color(*BLACK))
    a.add(leads, name="leads", color=cq.Color(*GOLD))
    save(a, f"PinSocket_2x{n:02d}_P1.27mm_Vertical_SMD")


def header_127(n):
    L = n * 1.27
    body = cq.Workplane("XY").box(3.4, L, 1.0, centered=(True, True, False)).translate((0, 0, 0.5))
    pins = None
    for i in range(n):
        y = (i - (n - 1) / 2) * 1.27
        for x in (-0.635, 0.635):
            p = cq.Workplane("XY").box(0.4, 0.4, 5.0, centered=(True, True, False)).translate((x, y, 0.3))
            lead = cq.Workplane("XY").box(2.0, 0.4, 0.3, centered=(True, True, False)).translate((x * 2.6, y, 0))
            q = p.union(lead)
            pins = q if pins is None else pins.union(q)
    a = cq.Assembly()
    a.add(body, name="body", color=cq.Color(*BLACK))
    a.add(pins, name="pins", color=cq.Color(*GOLD))
    save(a, f"PinHeader_2x{n:02d}_P1.27mm_Vertical_SMD")


header_2xN_ra(10)
socket_127(10)
header_127(10)

# AT7456E body (KiCad ships no model for the EP 2.75 x 6.2 variant)
shell("HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.75x6.2mm", -2.2, -4.85, 2.2, 4.85, 1.0, BLACK)
