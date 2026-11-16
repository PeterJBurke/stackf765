"""Tool-chain self test: tiny design -> schematic -> board -> autoroute.

Usage: python3 gen/selftest.py OUTDIR
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kigen.design import Design, box
from kigen.pcb import Board, write_project

out = sys.argv[1]
JAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "bin", "freerouting.jar")

d = Design("t1", "Test", rails=("+3V3", "+5V"))
s = d.sheet("main", "Main")
u = d.part("U1", box("LDO", left=[(1, "VIN", "power_in"), (3, "EN", "input"), (2, "GND", "power_in")],
                     right=[(5, "VOUT", "power_out"), (4, "NC")]), "Package_TO_SOT_SMD:SOT-23-5", "AP2112K-3.3")
u["VIN"] = "+5V"; u["EN"] = "EN_X"; u["GND"] = "GND"; u["VOUT"] = "+3V3"; u.nc("NC")
r = d.part("R1", "Device:R", "Resistor_SMD:R_0402_1005Metric", "10k"); r["1"] = "+5V"; r["2"] = "EN_X"
c = d.part("C1", "Device:C", "Capacitor_SMD:C_0402_1005Metric", "1u"); c["1"] = "+3V3"; c["2"] = "GND"
m = d.part("U2", "MCU_ST_STM32F7:STM32F765VITx", "Package_QFP:LQFP-100_14x14mm_P0.5mm", "STM32F765VIT6")
m["VDD"] = "+3V3"; m["VSS"] = "GND"; m["PA0"] = "EN_X"; m.nc_rest()
s.place(u, 60, 60); s.place(r, 30, 60, 90); s.place(c, 90, 70); s.place(m, 200, 150)
s.flag("+5V", 30.48, 30.48); s.flag("GND", 50.8, 30.48)
d.check()
d.write_schematic(out)

bd = Board(d, out, layers=4)
bd.outline_roundrect(30, 30, 2)
bd.place("U2", 0, 0, 0); bd.place("U1", -11, 11, 0); bd.place("R1", -11, 7, 0)
bd.place("C1", 11, 11, 90, side="bottom")
bd.hole(12, -12, 2.2)
bd.zone("GND", ["In1.Cu"], bd.rect(-15, -15, 15, 15))
bd.zone("+3V3", ["In2.Cu"], bd.rect(-15, -15, 15, 15))
write_project(out, "t1", [{"name": "Default", "clearance": 0.15, "track_width": 0.15,
                           "via_diameter": 0.5, "via_drill": 0.3}], {}, [])
bd.save()
from kigen.router import Router
rt = Router(bd, ["F.Cu", "B.Cu"], plane_nets=("GND", "+3V3"))
print("unrouted:", rt.route_all())
rt.commit()
bd.fill()
bd.save()
print("tracks", len(bd.b.GetTracks()))
