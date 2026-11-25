"""LOWER (power) board: battery/ESC pads, current sensor, two 5 V regulators
and the board-to-board socket.  All parts on the top side.  It carries no pin header:
every Dupont header is on the upper board.
"""
from kigen.design import Design
from blocks import Blocks
import parts

# Board-to-board connector: socket pin -> net (same numbers on the upper board header)
# Columns 1..10 run left to right (top view); each column is (odd pin = top row, even pin = bottom row).
# Odd pins are the row nearer the front edge.  Four pins each carry +5V_PI (3 A, 0.75 A per pin) and +5V.
B2B_COLS = [("GND", "GND"), ("GND", "GND"), ("+3V3", "GND"), ("VBAT_SENSE", "CURR_SENSE"), ("GND", "GND"),
            ("GND", "GND"), ("+5V", "+5V_PI"), ("+5V", "+5V_PI"), ("+5V", "+5V_PI"), ("+5V", "+5V_PI")]
B2B_Y = 4.5                # connector centre, forward of the board centre: leaves room for the microSD socket
                           # on the underside of the upper board
B2B = {}
for _c, (_t, _b) in enumerate(B2B_COLS):
    B2B[2 * _c + 1] = _t
    B2B[2 * _c + 2] = _b

HDR_ROW_A_Y = 17.72        # upper-board header hole rows at 17.72 / 20.26 / 22.80 from the centre: the plastic
                           # body hangs off the board edge

W, H = 31.5, 48.0
PAD_Y = -21.75
PAD_X = {"BAT+": -11.25, "ESC+": -3.75, "ESC-": 3.75, "BAT-": 11.25}
STANDOFFS = [(-12.3, 3.0), (12.3, 3.0), (12.3, -15.9)]
GROMMETS = [(-10, 10), (10, 10), (-10, -10), (10, -10)]


def buck(d, B, sh, n, out, x, y):
    """TPS62933 5 V / 3 A regulator.  n = index (1 or 2), out = output net."""
    u = B.part(sh, f"U{n}", "buck", x, y, nets={"VIN": "VESC", "GND": "GND", "SW": f"SW{n}", "BST": f"BST{n}",
                                                "FB": f"FB{n}", "SS": f"SS{n}"}, nc=("EN", "RT"))
    k = n * 10
    B.C(sh, f"C{k}", "22u", "VESC", "GND", x - 40, y + 2, 0, "1206")
    B.C(sh, f"C{k + 1}", "22u", "VESC", "GND", x - 32, y + 2, 0, "1206")
    B.C(sh, f"C{k + 2}", "100n 50V", "VESC", "GND", x - 24, y + 2, 0)
    B.C(sh, f"C{k + 3}", "33n", f"SS{n}", "GND", x - 22, y + 16, 0)
    B.C(sh, f"C{k + 4}", "100n", f"BST{n}", f"SW{n}", x + 28, y - 12, 90)
    B.part(sh, f"L{n}", "inductor", x + 46, y - 2.54, 90, nets={"1": f"SW{n}", "2": out})
    B.R(sh, f"R{k}", "51k", out, f"FBM{n}", x + 60, y + 8, 0)
    B.R(sh, f"R{k + 1}", "2.2k", f"FBM{n}", f"FB{n}", x + 60, y + 22, 0)
    B.R(sh, f"R{k + 2}", "10k", f"FB{n}", "GND", x + 60, y + 36, 0)
    B.C(sh, f"C{k + 5}", "22u", out, "GND", x + 74, y + 8, 0, "0805")
    B.C(sh, f"C{k + 6}", "22u", out, "GND", x + 82, y + 8, 0, "0805")
    B.C(sh, f"C{k + 7}", "100n", out, "GND", x + 90, y + 8, 0)
    sh.text(x - 42, y - 22, f"Vout = 0.8 V x (1 + (51k + 2.2k) / 10k) = 5.06 V     fsw = 500 kHz (RT open)     "
                            f"EN open = always on     soft-start 5 ms", 1.5)
    return u


def design():
    d = Design("lower", "StackF765 lower board (power)", rev="C", date="2026-11-25",
               rails=("VBAT", "VESC", "+5V", "+5V_PI", "+3V3"))
    B = Blocks(d)
    d.root_notes = [
        "LOWER BOARD = power.  Battery and ESC wires solder to four pads at the rear edge.",
        "Battery + -> 0.5 mohm shunt -> ESC +  (all current, including the flight controller's own, is measured).",
        "Two identical 5 V / 3 A regulators: +5V feeds the flight controller, +5V_PI feeds a companion computer.",
        "Both rails go up to the upper board through J1; the motor, LED and companion-power pins are on the upper board.",
        "Input range 6-13 V (2S-3S LiPo); D1 clamps spikes below 25 V so every part stays inside its ratings.  No reverse-polarity protection: check wiring before connecting a battery.",
        "All components are on the top side; the bottom side carries copper only.",
    ]

    # ------------------------------------------------------------------ sheet 1: battery input and sensing
    s = d.sheet("input", "Battery input, current and voltage sensing")
    s.frame(15, 20, 185, 115, "Battery / ESC solder pads and current shunt (50 A continuous)")
    for i, (name, net) in enumerate([("BAT+", "VBAT"), ("ESC+", "VESC"), ("ESC-", "GND"), ("BAT-", "GND")]):
        p = B.part(s, f"J{10 + i}", "wirepad", 35 + i * 22, 50, 180 if net == "GND" else 0, nets={"1": net}, value=name)
    B.part(s, "R1", "shunt", 60, 85, 90, nets={"1": "VBAT", "2": "VESC"})
    B.part(s, "NT1", "nettie", 40, 110, 0, nets={"1": "VBAT", "2": "ISENSE_P"})
    B.part(s, "NT2", "nettie", 80, 110, 0, nets={"1": "VESC", "2": "ISENSE_N"})
    B.part(s, "D1", "tvs", 125, 85, 90, nets={"1": "VESC", "2": "GND"})
    s.text(20, 128, "NT1/NT2 are Kelvin taps: copper-only connections taken from the inner edges of the shunt pads.", 1.5)
    s.text(110, 105, "D1 clamps wiring-inductance spikes.  The ESC needs its own bulk capacitor.", 1.5)

    s.frame(210, 20, 190, 115, "Current sense amplifier:  0.5 mohm x 100 V/V = 50 mV/A  (ArduPilot BATT_AMP_PERVLT = 20)")
    B.R(s, "R2", "10R", "ISENSE_P", "INA_P", 235, 60, 90)
    B.R(s, "R3", "10R", "ISENSE_N", "INA_N", 235, 75, 90)
    B.C(s, "C3", "100n 50V", "INA_P", "INA_N", 255, 95, 0)
    B.part(s, "U3", "ina", 290, 65, nets={"IN+": "INA_P", "IN-": "INA_N", "REF": "GND", "V+": "+3V3",
                                         "OUT": "CURR_SENSE", "GND": "GND"})
    B.C(s, "C4", "100n", "+3V3", "GND", 330, 95, 0)
    s.text(215, 125, "CURR_SENSE: 2.5 V at 50 A, 3.3 V full scale at 66 A.  R2/R3/C3 filter and limit transient input current.", 1.5)

    s.frame(15, 150, 185, 90, "Battery voltage divider:  11:1  (ArduPilot BATT_VOLT_MULT = 11.0)")
    B.R(s, "R4", "10k", "VBAT", "VBAT_SENSE", 60, 180, 0)
    B.R(s, "R5", "1k", "VBAT_SENSE", "GND", 60, 205, 0)
    B.C(s, "C5", "100n", "VBAT_SENSE", "GND", 85, 205, 0)
    s.text(20, 232, "VBAT_SENSE: 0.76 V at 8.4 V (2S), 1.15 V at 12.6 V (3S).", 1.5)

    s.frame(210, 150, 190, 90, "Power flags (tell the rule checker which nets are driven from off-board)")
    for i, n in enumerate(["VBAT", "VESC", "GND", "+3V3"]):
        s.flag(n, 230 + i * 25.4, 190.5)

    # ------------------------------------------------------------------ sheet 2: regulators
    s = d.sheet("regulators", "5 V regulators")
    s.frame(15, 20, 390, 110, "U1: +5V for the flight controller, GPS, receiver, camera, servos (3 A)")
    buck(d, B, s, 1, "+5V", 110, 65)
    s.frame(15, 145, 390, 110, "U2: +5V_PI for a companion computer, to the PI5V pins of the upper board's rear header (3 A)")
    buck(d, B, s, 2, "+5V_PI", 110, 190)
    s.flag("+5V", 370, 60)
    s.flag("+5V_PI", 370, 185)

    # ------------------------------------------------------------------ sheet 3: connectors
    s = d.sheet("connectors", "Connectors and mechanics")
    s.frame(15, 20, 180, 130, "J1: board-to-board socket to the upper board (2x10, 1.27 mm)")
    j = B.part(s, "J1", "b2b_socket", 100, 80)
    for pin, net in B2B.items():
        j[str(pin)] = net
    s.frame(15, 160, 180, 80, "Power indicator and standoffs (M2 x 8 mm, soldered, grounded)")
    B.R(s, "R6", "2.2k", "+5V", "LED_A", 40, 195, 0)
    B.part(s, "D2", "led_green", 40, 215, 90, nets={"A": "LED_A", "K": "GND"})
    for i in range(3):
        B.part(s, f"H{i + 1}", "standoff", 90 + i * 25, 200, nets={"1": "GND"})
    return d


# ====================================================================== PCB
RULES = dict(
    layers=4,
    netclasses=[
        {"name": "Default", "clearance": 0.2, "track_width": 0.2, "via_diameter": 0.7, "via_drill": 0.3},
        {"name": "Power", "clearance": 0.2, "track_width": 0.5, "via_diameter": 0.7, "via_drill": 0.4},
    ],
    patterns=[("Power", n) for n in ("VBAT", "VESC", "+5V", "+5V_PI", "SW1", "SW2", "GND")],
    rules=dict(clearance=0.2, track=0.2, via_dia=0.5, via_drill=0.3, annular=0.1, hole_clearance=0.25,
               edge=0.25, severities={"lib_footprint_mismatch": "ignore", "lib_footprint_issues": "ignore",
                                      "silk_over_copper": "ignore", "silk_overlap": "ignore",
                                      "silk_edge_clearance": "ignore"}),
)


def _buck_cluster(bd, n, ox, oy):
    """Place regulator n with its passives; local frame: IC at origin, inductor to the right."""
    k = n * 10

    def at(ref, x, y, rot=0):
        bd.place(ref, ox + x, oy + y, rot)
    at(f"U{n}", 0, 0)
    at(f"C{k}", -2.5, -0.5, 270)        # input cap (1206: about 5 uF each at 12.6 V), VESC pad next to VIN
    at(f"C{k + 1}", -1.8, -4.1, 0)      # second input cap
    at(f"C{k + 2}", -0.2, -2.2, 0)      # 100 nF input
    at(f"L{n}", 5.3, -2.3, 0)           # SW pad towards the IC
    at(f"C{k + 4}", 3.1, 1.2, 0)        # bootstrap
    at(f"C{k + 3}", 3.1, 2.4, 0)        # soft-start
    at(f"R{k + 2}", 0.2, 2.4, 0)        # FB - GND
    at(f"R{k + 1}", 0.2, 3.6, 0)        # 2.2k
    at(f"R{k}", 3.1, 3.6, 0)            # 51k
    at(f"C{k + 5}", 8.15, 2.4, 90)       # output caps (0805: no room for 1206 between the grommets)
    at(f"C{k + 6}", 6.15, 2.4, 90)
    at(f"C{k + 7}", 4.6, 2.4, 90)
    # switch node: one small copper area from the IC pin to the inductor pad
    bd.zone(f"SW{n}", ["F.Cu"], [(ox + 0.42, oy - 3.55), (ox + 3.8, oy - 3.55), (ox + 3.8, oy - 0.58),
                                (ox + 0.42, oy - 0.58)], priority=6, solid=True, clearance=0.2, name=f"SW{n}")


def layout(bd):
    bd.outline_roundrect(W, H, 1.5)
    # --- mechanics
    for x, y in GROMMETS:
        bd.hole(x, y, 4.0)
        bd.circle("User.Comments", x, y, 3.5)
    for i, (x, y) in enumerate(STANDOFFS):
        bd.place(f"H{i + 1}", x, y)
    # --- power pads, shunt, Kelvin taps
    for i, name in enumerate(["BAT+", "ESC+", "ESC-", "BAT-"]):
        bd.place(f"J{10 + i}", PAD_X[name], PAD_Y)
    bd.place("R1", -7.5, -16.6, 0)
    bd.place("NT1", -8.95, -16.0, 0)      # pad 1 sits on the inner edge of the shunt's VBAT pad
    bd.place("NT2", -6.05, -17.2, 180)    # pad 1 sits on the inner edge of the shunt's VESC pad
    # --- current-sense amplifier
    bd.place("U3", -1.4, -18.0, 180)
    bd.place("C3", -1.4, -16.1, 0)
    bd.place("R2", -2.4, -15.0, 0)
    bd.place("R3", -0.4, -15.0, 0)
    bd.place("C4", 0.95, -18.0, 90)
    bd.place("D1", 5.1, -16.8, 0)
    # --- battery voltage divider
    bd.place("R4", -14.4, -13.3, 90)
    bd.place("R5", -14.4, -11.2, 90)
    bd.place("C5", -14.4, -9.0, 90)
    # --- regulators
    _buck_cluster(bd, 1, -2.5, 17.0)      # +5V (front): inductor output faces the front row of J1
    _buck_cluster(bd, 2, -2.6, -8.4)      # +5V_PI (rear): reaches the rear row of J1 on the bottom layer
    # --- connectors
    bd.place("J1", 0, B2B_Y, 90)
    bd.place("R6", -14.6, 10.6, 90)
    bd.place("D2", -14.6, 7.6, 90)

    # --- copper zones.  High-current paths use all four layers, stitched by the pad vias.
    ALL = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
    bd.zone("VBAT", ALL, [(-15.5, -23.8), (-8.95, -23.8), (-8.95, -14.75), (-15.5, -14.75)], priority=5, solid=True,
            clearance=0.25, name="VBAT high current")
    bd.zone("VESC", ALL, [(-6.35, -23.8), (-1.1, -23.8), (-1.1, -19.55), (-3.6, -19.55), (-3.6, -14.75),
                          (-6.35, -14.75)], priority=5, solid=True, clearance=0.25, name="VESC high current")
    bd.zone("GND", ALL, [(1.1, -23.8), (15.5, -23.8), (15.5, -19.55), (1.1, -19.55)], priority=5, solid=True,
            clearance=0.25, name="GND high current")
    # +5V: solid top-layer copper from the front regulator's inductor to J1 pins 13/15/17/19 (front row)
    y1 = B2B_Y + 1.36 + 1.11                      # outer end of the front-row pads
    bd.zone("+5V", ["F.Cu"], [(4.2, 13.6), (6.4, 13.6), (6.4, y1 - 0.5), (1.4, y1 - 0.5), (1.4, y1 + 1.2), (4.2, y1 + 1.2)],
            priority=6, solid=True, clearance=0.2, name="+5V to J1")
    # +5V_PI (3 A): output copper of the rear regulator, three vias down, a bottom-layer strip forward to J1,
    # four vias up, and a small top-layer area onto J1 pins 14/16/18/20 (rear row)
    y0 = B2B_Y - 1.36 - 1.11                      # outer end of the rear-row pads
    bd.zone("+5V_PI", ["F.Cu"], [(4.1, -12.0), (6.3, -12.0), (6.3, -6.25), (3.0, -6.25), (3.0, -7.7), (4.1, -7.7)],
            priority=6, solid=True, clearance=0.2, name="+5V_PI output")
    for x in (4.15, 5.05, 5.95):
        bd.via("+5V_PI", x, -8.55, drill=0.4, dia=0.7)
    bd.zone("+5V_PI", ["B.Cu"], [(3.5, -9.3), (6.5, -9.3), (6.5, y0 + 0.9), (1.3, y0 + 0.9), (1.3, y0 - 1.2), (3.5, y0 - 1.2)],
            priority=6, solid=True, clearance=0.2, name="+5V_PI to J1")
    for x in (1.91, 3.17, 4.44, 5.72):
        bd.via("+5V_PI", x, y0 - 0.6, drill=0.4, dia=0.7)
    bd.zone("+5V_PI", ["F.Cu"], [(1.45, y0 - 1.05), (6.15, y0 - 1.05), (6.15, y0 + 0.5), (1.45, y0 + 0.5)],
            priority=6, solid=True, clearance=0.2, name="+5V_PI at J1")
    # keep other nets' tracks out of the +5V_PI strip (their vias may pass through it)
    bd.keepout(["B.Cu"], bd.rect(3.5, -9.3, 6.5, y0 + 0.9), tracks=True, vias=False, copper=False, name="+5V_PI strip")
    bd.keepout(["B.Cu"], bd.rect(1.3, y0 - 1.2, 3.5, y0 + 0.9), tracks=True, vias=False, copper=False, name="+5V_PI strip")
    full = bd.rect(-W / 2, -H / 2, W / 2, H / 2)
    bd.zone("GND", ["In1.Cu"], full, priority=1, name="GND plane")
    bd.zone("VESC", ["In2.Cu"], full, priority=1, name="VESC plane")
    bd.zone("GND", ["F.Cu", "B.Cu"], full, priority=0, name="GND pour")

    # --- silkscreen
    for name, x in (("BAT+", -11.25), ("ESC+", -4.7), ("ESC-", 3.75), ("BAT-", 11.25)):
        bd.text(name, x, -19.1, size=0.8, thick=0.14)
        bd.text(name, PAD_X[name], -19.0, "B.SilkS", size=1.0, thick=0.16)
    bd.text("StackF765 LOWER rev C", 0, 3.5, "B.SilkS", size=1.0, thick=0.16)
    bd.text("2S-3S LiPo  50 A", 0, -15.0, "B.SilkS", size=0.8, thick=0.14)


def router_config(bd):
    return dict(layers=["F.Cu", "B.Cu"], grid=0.05, track=0.2, clear=0.2, via_dia=0.7, via_drill=0.3,
                plane_nets=("GND", "VESC"),
                widths={"+5V": 0.6, "+5V_PI": 0.8, "VBAT": 0.4})


ROUTER = "sequential"
