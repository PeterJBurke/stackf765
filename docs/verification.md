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
| Stack fit | `tools/check_stack.py` | The 20 board-to-board pins line up and carry the same signals; standoffs meet screw holes; parts fit in the 8 mm gap; the lower board carries no pin header; the tails of both upper headers clear everything below them, including a 5 mm power-wire joint; grommet zones are clear; the service cable is consistent at both ends | Real part tolerances |
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

## Layout review

The routed boards were reviewed against the points a layout engineer would check
(2026-11-18). Details and numbers are in `research/layout-review.md`.

| Area | Result |
|---|---|
| 50 A path (lower) | Pads, shunt and return are joined by solid copper on all four layers; about 0.15 mΩ of copper besides the 0.5 mΩ shunt. No change. |
| 5 V rails (lower) | 0.6 mm and 0.8 mm tracks in 2 oz copper carry 3 A with roughly 20 °C rise. No change. |
| 5 V feed into the supply selector U5 (upper) | Was 0.15 mm wide for 6.7 mm. Re-routed: now 0.5 mm except a 5 mm stretch at 0.24 mm between a via and the chip. Adequate for the board's own load plus 0.5 A on the 4V5 pins. |
| Decoupling (upper) | Every processor supply pin has its capacitor within 2.8 mm and a plane via within 1.4 mm. No change. |
| Adjacent inner signal layers (upper) | Only 2.9 mm of parallel overlap between the two inner signal layers in total. No change. |
| Sensitive nets | Video, ADC, crystal and reset tracks have no long parallel runs beside clocks or motor signals. No change. |
| Crystals | The 8 MHz crystal is 5 mm from the processor and its tracks (7 and 9 mm) each use two vias. Acceptable at 8 MHz; a candidate for tidying in a later revision. |

## Independent audit

A separate reviewer re-fetched the datasheets and checked every IC, connector and polarised part pin by pin
against the schematic, the board's pads and the land patterns, and worked the analogue circuits through by
calculation (2026-11-19, `research/audit-2026-11-19.md`). A second reviewer checked the fabrication files
against JLCPCB's requirements (`docs/ordering-jlcpcb.md`). Neither found a wiring, footprint or polarity error.
What they did find, and what was done:

| Finding | Action |
|---|---|
| Placement files carried KiCad rotations; about 12 parts would be placed turned at JLCPCB | Generator now applies JLCPCB's rotation per part |
| A reversed service cable would put USB 5 V on the boot pin | Cable pin order changed so a reversed cable does no harm |
| Regulator input capacitors too small at battery voltage (about 3.5 µF effective) | Now 2 × 22 µF 1206 per regulator (about 11 µF effective at 12.6 V) |
| 3.3 V heat-sharing resistors at their power limit | Now 0.5 W parts; capacitor behind them raised to 10 µF |
| Status LEDs dim | Series resistors 470 Ω → 100 Ω |
| Unused IMU pin 9 tied to ground | Left open, as TDK specifies |
| USB-C socket 0.4 mm too far from the edge | Moved |
| Buzzer and diode part numbers ambiguous or costly | Single, well-stocked parts |
| Regulator output capacitors near the minimum (about 21 µF effective) | Not changed: larger parts do not fit between the grommets. Above TI's 10 µF minimum. |
| VBUS clamp D3 conducts above the supply selector's 6 V limit | Not changed; do not use chargers that overshoot |
| Silkscreen text below JLCPCB's 1.0 mm recommendation | Not changed; small labels may be faint. The pinout is in `docs/pinout.md`. |

Items the audit could not confirm from a primary source are listed at the end of its report
(mainly the land patterns of stock KiCad footprints and the JST connector).

## Known limitations and open items

| Item | Detail |
|---|---|
| No hardware test | No board has been fabricated, powered or flown. |
| Autorouted layout | Tracks were routed by the script in `gen/kigen/router.py`. It respects clearances but does not length-match or impedance-control. USB runs at full speed (12 Mbit/s) over an unshielded cable and the SD bus is short, so neither needs it, and the layout has had a scripted review (above) but not one by a human layout engineer. |
| Thermal | 50 A continuous rating is by calculation (about 1.7 W near the shunt). Measure it (bring-up section E). |
| IMU orientation | Set from the footprint drawing; confirm on the bench (bring-up C9). |
| Buzzer polarity | "+" on the part goes to pad 1; confirmed against the maker's drawing in the audit. Check it in the assembler's preview. |
| Standoff footprint | Hole 3.75 mm, pad 6.2 mm, from the PEM SMTSO family data; Sinhoo's drawing gives the part dimensions (8.00 mm tall) but no land pattern. |
| Grommet size | The 4 mm hole and 7 mm keep-out follow Matek's "M4 to M3" silicone grommets with brass "M3 to M2" inserts. No maker's dimension drawing was found; measure yours. |
| Header pin clearance | Both Dupont headers are on the upper board (revision C, 2026-11-25); their solder tails hang about 1.8 mm below it. The front header has nothing under it. The rear header sits over the battery and ESC wire pads: 1.2 mm spare over a 5 mm wire joint with untrimmed tails, about 2.5 mm with the tails cut flush (assembly step 1). Keep power-wire joints under 5 mm. |
| Rear header 5 V current | The `5V` row of the rear header is fed through the inner power layer; keep the total drawn from that row under 2 A. Servos that need more need their own supply. The two `PI5V` columns have their own regulator and copper. |
| Board-to-board connector | Samtec SFMC + FTSH-04 mates at 7.65 mm; with 8.0 mm standoffs it runs 0.35 mm short of fully seated, inside Samtec's stated range (maximum 8.38 mm). Land patterns were read from Samtec's footprint drawings (`research/samtec-b2b.md`). |
| Part stock | Several connectors could not be stock-checked on the day; see [manufacturing.md](manufacturing.md). |
| Board ID | Private ArduPilot board ID 20765; see [firmware.md](firmware.md). |
| No reverse-polarity protection | By design, as on most small flight controllers. |
