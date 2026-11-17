# What has been verified, and what has not

**No StackF765 hardware has been built.** Everything below is verification of the
*design files*. It shows the design is internally consistent, manufacturable by the stated
rules, and that firmware compiles for it. It does not show that a built board works; for
that, follow [bringup.md](bringup.md).

The current results are in [verification-report.md](verification-report.md) and on the
[project page](https://peterjburke.github.io/stackf765/#verify). Re-run them with `make verify`.

## Automated checks

| Check | Tool | What it proves | What it does not prove |
|---|---|---|---|
| Electrical rules (ERC) | KiCad 9 `kicad-cli sch erc` | No unconnected pins, no shorted outputs, every power pin driven | That the circuit is the right circuit |
| Schematic = design model | `gen/build.py` netlist comparison | The schematic KiCad reads has exactly the nets written in `gen/*.py` | – |
| Design rules (DRC) | KiCad 9 `kicad-cli pcb drc` | No clearance, width, hole, edge or courtyard violations against the fab rules in each `.kicad_pro` | Signal integrity, thermal behaviour |
| Routing complete | same | Zero unconnected pads | – |
| Board = schematic | same, `--schematic-parity` | Every footprint, pad and net on the board matches the schematic | – |
| Firmware pin map | `tools/check_hwdef.py` | Each of the 49 MCU pins used by ArduPilot's `hwdef.dat` is wired to the matching net, and that net reaches the right sensor, header or connector pin; sensor address straps match the firmware | That the firmware behaves correctly on hardware |
| Stack fit | `tools/check_stack.py` | The 20 board-to-board pins line up and carry the same signals; standoffs meet screw holes; parts fit in the 8 mm gap; the two headers' pins interleave; grommet zones are clear; the service cable is consistent at both ends | Real part tolerances |
| Firmware build | `firmware/build.sh` | ArduPilot's own generator accepts the pin assignment (alternate functions, timers, DMA) and bootloader plus ArduCopter compile and link | Run-time behaviour |
| BOM completeness | `tools/verify.py` | Every fitted part has a manufacturer part number and an LCSC number | Current stock |

The stack check has already earned its keep: it caught the board-to-board header placed
rotated by 180°, which no rule check would have flagged.

## Manual reviews

* **Datasheet checks.** Pin numbers and land patterns of every IC and connector were read
  from the manufacturers' datasheets; notes and sources are in `research/parts.md` and
  `research/footprints.md`. Items that could not be confirmed are listed there as UNVERIFIED.
* **Independent schematic review.** A separate review pass found no wiring errors and six margin
  issues, all since addressed (15 V input clamp, USB VBUS clamp, buzzer current limit on the
  flight-controller side, regulator heat sharing, 3 A regulator rating explained, firmware
  rebuilt for the fitted barometer). The full report is `research/design-review.md`.

## Known limitations and open items

| Item | Detail |
|---|---|
| No hardware test | No board has been fabricated, powered or flown. |
| Autorouted layout | Tracks were routed by the script in `gen/kigen/router.py`. It respects clearances but does not length-match or impedance-control. USB runs at full speed (12 Mbit/s) over an unshielded cable and the SD bus is short, so neither needs it, but the layout has not been reviewed by a human layout engineer. |
| Thermal | 50 A continuous rating is by calculation (about 1.7 W near the shunt). Measure it (bring-up section E). |
| IMU orientation | Set from the footprint drawing; confirm on the bench (bring-up C9). |
| Buzzer polarity | "+" on the part goes to pad 1; the land pattern was checked against the MLT-8530 drawing, the KLJ part's drawing is less explicit. |
| Standoff footprint | Hole 3.75 mm, pad 6.2 mm, from the PEM SMTSO family data; Sinhoo's drawing gives the part dimensions (8.00 mm tall) but no land pattern. |
| Grommet size | The 4 mm hole and 7 mm keep-out follow Matek's "M4 to M3" grommets; measure yours. |
| Header pin clearance | The top-row pins of the lower header reach 6.6 mm above the lower board; the upper header's solder tails hang 1.4 mm below the upper board. They do not collide only because the two headers are offset by half a pitch. Trim the tails to 1.5 mm or less. |
| Board-to-board connector | Samtec SFMC + FTSH-04 mates at 7.65 mm; with 8.0 mm standoffs it runs 0.35 mm short of fully seated, inside Samtec's stated range (maximum 8.38 mm). Land patterns were read from Samtec's footprint drawings (`research/samtec-b2b.md`). |
| Part stock | Several connectors could not be stock-checked on the day; see [manufacturing.md](manufacturing.md). |
| Board ID | Private ArduPilot board ID 20765; see [firmware.md](firmware.md). |
| No reverse-polarity protection | By design, as on most small flight controllers. |
