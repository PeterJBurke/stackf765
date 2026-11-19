#!/usr/bin/env python3
"""Cross-check the ArduPilot hwdef against the KiCad netlist of the upper board.

For every MCU pin it compares three independent sources:
  1. firmware/hwdef/StackF765/hwdef.dat   (what the firmware will drive)
  2. gen/pinmap.py                        (the design intent)
  3. the netlist KiCad extracts from hardware/upper/upper.kicad_sch (what was actually drawn)

and then follows each net to its destination (sensor pin, header pin, connector pin) and
checks that it is the expected one.  Exit status 0 = all consistent.

    python3 tools/check_hwdef.py
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))
from kigen.sexpr import parse, find, findall   # noqa: E402
from pinmap import PINMAP                      # noqa: E402

errors = []
rows = []


def err(msg):
    errors.append(msg)


# ---- 1. hwdef -------------------------------------------------------------------
hw = {}
for line in open(os.path.join(ROOT, "firmware/hwdef/StackF765/hwdef.dat")):
    line = line.split("#")[0].strip()
    m = re.match(r"^(P[A-K]\d+)\s+(\S+)\s+(\S+)", line)
    if m:
        hw[m.group(1)] = (m.group(2), m.group(3))

# ---- 3. netlist from the schematic -------------------------------------------------
tmp = tempfile.mkdtemp()
net = os.path.join(tmp, "upper.net")
subprocess.run(["kicad-cli", "sch", "export", "netlist", os.path.join(ROOT, "hardware/upper/upper.kicad_sch"),
                "-o", net], check=True, capture_output=True)
tree = parse(open(net).read())
pin_net = {}        # (ref, pin) -> net
net_nodes = {}      # net -> [(ref, pin, pinfunction)]
for n in findall(find(tree, "nets"), "net"):
    name = find(n, "name")[1].lstrip("/")
    for node in findall(n, "node"):
        ref, pin = find(node, "ref")[1], find(node, "pin")[1]
        fn = find(node, "pinfunction")
        pin_net[(ref, pin)] = name
        net_nodes.setdefault(name, []).append((ref, pin, fn[1] if fn else ""))

mcu_by_name = {}
for (ref, pin), name in pin_net.items():
    if ref == "U1":
        fn = next(f for r, p, f in net_nodes[name] if r == "U1" and p == pin)
        mcu_by_name[fn.split("/")[0]] = (pin, name)

# ---- compare hwdef <-> pinmap <-> schematic -----------------------------------------
for pin in sorted(set(hw) | set(PINMAP), key=lambda p: (p[1], int(p[2:]))):
    h = hw.get(pin)
    p = PINMAP.get(pin)
    s = mcu_by_name.get(pin, (None, None))
    if h is None:
        err(f"{pin}: in pinmap ({p[0]}) but not in hwdef.dat")
        continue
    if p is None:
        err(f"{pin}: in hwdef.dat ({h[0]}) but not in pinmap")
        continue
    if h[0] != p[1]:
        err(f"{pin}: hwdef function {h[0]} != pinmap {p[1]}")
    if s[1] != p[0]:
        err(f"{pin}: schematic net {s[1]} != pinmap net {p[0]}")
    others = [f"{r}.{q}" for r, q, f in net_nodes.get(s[1], []) if r != "U1"]
    rows.append((pin, s[0], h[0], s[1], ", ".join(sorted(others))))

# every connected MCU GPIO must be declared in hwdef
for name, (pin, netname) in mcu_by_name.items():
    if re.match(r"^P[A-K]\d+$", name) and not netname.startswith("unconnected-") and name not in hw \
            and name not in ("PH0", "PH1"):
        err(f"{name}: wired to {netname} in the schematic but missing from hwdef.dat")

# ---- destinations ---------------------------------------------------------------------
EXPECT = {   # net -> set of "REF.pin-function" that must be on it
    "IMU_SCK": {"U2.SCLK"}, "IMU_MOSI": {"U2.SDI"}, "IMU_MISO": {"U2.SDO"}, "IMU_CS": {"U2.CS"},
    "IMU_INT": {"U2.INT1"},
    "OSD_SCK": {"U4.SCLK"}, "OSD_MOSI": {"U4.SDIN"}, "OSD_MISO": {"U4.SDOUT"}, "OSD_CS": {"U4.~{CS}"},
    "BARO_SCL": {"U3.SCK"}, "BARO_SDA": {"U3.SDI"},
    "SD_D0": {"J4.DAT0"}, "SD_D1": {"J4.DAT1"}, "SD_D2": {"J4.DAT2"}, "SD_D3": {"J4.DAT3/CD"},
    "SD_CK": {"J4.CLK"}, "SD_CMD": {"J4.CMD"},
    "USB_DM": {"J5.Pin_3"}, "USB_DP": {"J5.Pin_4"},
    "M1": {"J3.Pin_3"}, "M2": {"J3.Pin_4"}, "M3": {"J3.Pin_5"}, "M4": {"J3.Pin_6"}, "M5": {"J3.Pin_7"},
    "M6": {"J3.Pin_8"}, "LED_STRIP": {"J3.Pin_9"},
    "VBAT_ADC": {"R14.2"}, "CURR_ADC": {"R15.2"}, "BUZZER": {"Q1.G"},
    "OSC_IN": {"Y1.1"}, "OSC_OUT": {"Y1.3"},
}
for i, r in enumerate("ABC"):
    pass
for netname, want in EXPECT.items():
    have = {f"{r}.{f or p}" for r, p, f in net_nodes.get(netname, [])} | \
           {f"{r}.{p}" for r, p, f in net_nodes.get(netname, [])}
    for w in want:
        if w not in have:
            err(f"net {netname}: expected node {w}, found {sorted(have)}")
# UART pins must reach the header pin carrying the same label
for netname, nodes in net_nodes.items():
    if re.match(r"^[TR]X\d$", netname) or netname in ("SDA", "SCL"):
        hdr = [f for r, p, f in nodes if r == "J1"]
        if len(hdr) != 1 or not hdr[0].replace("_", " ").endswith(" " + netname):
            err(f"net {netname}: header pin label mismatch {hdr}")

# I2C address / device strapping
def on(ref, func):
    return next((n for n, nodes in net_nodes.items() for r, p, f in nodes if r == ref and f == func), None)


if on("U3", "SDO") != "GND":
    err("BMP388 SDO is not tied to GND (hwdef expects I2C address 0x76)")
if on("U3", "CSB") != "+3V3_SENS":
    err("BMP388 CSB must be high for I2C mode")
if on("U2", "RESV7") != "GND":
    err("IMU pin 7 must be grounded")

print(f"{'MCU pin':8} {'pad':>4}  {'hwdef function':18} {'net':12} connects to")
for r in rows:
    print(f"{r[0]:8} {r[1]:>4}  {r[2]:18} {r[3]:12} {r[4]}")
print()
if errors:
    print(f"FAIL: {len(errors)} inconsistencies")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print(f"PASS: {len(rows)} MCU pins consistent between hwdef.dat, pinmap.py and the KiCad schematic")
