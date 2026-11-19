"""SERVICE board: USB-C socket, passive buzzer and BOOT (DFU) button on a
6-wire JST-SH cable, so they can be mounted anywhere on the airframe.
"""
from kigen.design import Design
from blocks import Blocks
from upper import SVC

W, H = 18.0, 32.0


def design():
    d = Design("service", "StackF765 service board (USB / buzzer / boot)", rev="B", date="2026-11-16",
               rails=("VBUS",))
    B = Blocks(d)
    d.root_notes = [
        "SERVICE BOARD: mount it where the USB socket is easy to reach.  Connects to J5 on the upper board",
        "with a 6-wire JST-SH (1.0 mm) cable wired 1:1 (pin 1 to pin 1).  Pin names are printed at both ends.",
        "A cable wired 6-to-1 does no harm (USB simply does not connect): swap it for a 1:1 cable.",
        "The buzzer is driven with 5 V pulses from the flight controller (BUZ wire, current-limited there by 10 ohm).",
        "BOOT button: hold while plugging in USB to start the STM32 DFU bootloader.",
    ]
    s = d.sheet("main", "USB-C, buzzer, boot button")
    s.frame(15, 20, 215, 130, "J1: USB-C (USB 2.0 device).  5.1 k on CC1/CC2 = 'I am a device, give me 5 V'")
    B.part(s, "J1", "usbc", 70, 90, nets={"VBUS": "VBUS", "GND": "GND", "SHIELD": "GND", "CC1": "CC1", "CC2": "CC2",
                                         "D+": "USB_DP", "D-": "USB_DM"}, nc=("SBU1", "SBU2"))
    B.R(s, "R1", "5.1k", "CC1", "GND", 130, 60, 90)
    B.R(s, "R2", "5.1k", "CC2", "GND", 130, 75, 90)
    B.part(s, "U1", "usbesd", 180, 100, nets={"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM",
                                             "VBUS": "VBUS", "GND": "GND"})
    B.C(s, "C1", "1u", "VBUS", "GND", 135, 120, 0)
    s.frame(240, 20, 160, 130, "J2: cable to the flight controller (JST-SH 6)")
    j = B.part(s, "J2", "jst6", 320, 80, nets={"MP": "GND"})
    for pin, net in SVC.items():
        j[str(pin)] = net
    s.text(245, 140, "1 VBUS   2 GND   3 D-   4 D+   5 BOOT   6 BUZ", 1.6)
    s.frame(15, 160, 215, 85, "Buzzer (passive, 2.7 kHz, 16 ohm).  D1 catches the coil's turn-off spike")
    B.part(s, "BZ1", "buzzer", 110, 205, nets={"+": "BUZ_OUT", "-": "GND"})
    B.part(s, "D1", "schottky", 160, 205, 90, nets={"K": "BUZ_OUT", "A": "GND"})
    s.frame(240, 160, 160, 85, "BOOT button: VBUS -> 10 k -> BOOT0 (10 k pull-down on the FC)")
    B.part(s, "SW1", "button", 290, 200, nets={"1": "VBUS", "2": "BOOT_SW"})
    B.R(s, "R4", "10k", "BOOT_SW", "BOOT0", 345, 200, 90)
    s.flag("VBUS", 30, 50)
    s.flag("GND", 30, 120)
    return d


RULES = dict(
    layers=2,
    netclasses=[{"name": "Default", "clearance": 0.15, "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3},
                {"name": "Power", "clearance": 0.15, "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3}],
    patterns=[("Power", n) for n in ("VBUS", "GND", "BUZ_OUT")],
    rules=dict(clearance=0.15, track=0.15, via_dia=0.5, via_drill=0.3, annular=0.1, hole_clearance=0.25, edge=0.25,
               severities={"lib_footprint_mismatch": "ignore", "lib_footprint_issues": "ignore",
                           "silk_over_copper": "ignore", "silk_overlap": "ignore", "silk_edge_clearance": "ignore"}),
)
HOLES = [(-6.6, 2.2), (6.6, 2.2)]


def layout(bd):
    bd.outline_roundrect(W, H, 1.5)
    for x, y in HOLES:
        bd.hole(x, y, 2.2)
    bd.place("J1", 0, 12.81, 180)          # USB-C at the top edge, opening upward
    bd.place("U1", 0, 5.0, 0)
    bd.place("R1", -4.0, 6.0, 90)
    bd.place("R2", 4.0, 6.0, 90)
    bd.place("C1", -4.0, 3.6, 90)
    bd.place("BZ1", -4.0, -4.2, 0)        # sound port faces +X
    bd.place("SW1", 5.2, -3.6, 90)
    bd.place("R4", 7.6, -9.6, 90)
    bd.place("D1", -6.6, -11.2, 90)
    bd.place("J2", 2.2, -12.9, 0)         # cable exits at the bottom edge
    full = bd.rect(-W / 2, -H / 2, W / 2, H / 2)
    bd.zone("GND", ["F.Cu", "B.Cu"], full, priority=0, name="GND pour")
    bd.text("1", -1.3, -10.4, size=0.8, thick=0.14)
    bd.text("BOOT", 5.2, 0.6, size=0.9, thick=0.15)
    bd.text("StackF765 SERVICE rev B", 0, 9.5, "B.SilkS", size=0.9, thick=0.15)
    bd.text("USB / BUZZER / BOOT", 0, 7.5, "B.SilkS", size=0.9, thick=0.15)
    bd.text("JST-SH 6, cable wired 1:1", 0, -3.0, "B.SilkS", size=0.8, thick=0.14)
    bd.text("1 VBUS  2 GND  3 D-", 0, -5.0, "B.SilkS", size=0.9, thick=0.15)
    bd.text("4 D+  5 BOOT  6 BUZ", 0, -7.0, "B.SilkS", size=0.9, thick=0.15)


def router_config(bd):
    return dict(layers=["F.Cu", "B.Cu"], grid=0.05, track=0.2, clear=0.15, via_dia=0.6, via_drill=0.3,
                plane_nets=("GND",), widths={"VBUS": 0.4, "BUZ_OUT": 0.4}, layer_cost=[10, 30])
