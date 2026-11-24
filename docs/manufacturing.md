# Ordering the boards

Everything a board house needs is in `fab/<board>/`:

| File | What it is |
|---|---|
| `<board>-gerbers.zip` | Gerber and drill files (upload this) |
| `<board>-bom-jlc.csv` | Bill of materials in JLCPCB format (LCSC part numbers) |
| `<board>-cpl-jlc.csv` | Component placement in JLCPCB format |
| `<board>-bom.csv` | Full bill of materials with manufacturer part numbers and prices. The `Fit` column reads `yes` (machine-placed), `hand` (you solder it) or `DNP`. |
| `<board>-pos.csv` | Placement file in KiCad's native format |
| `<board>.d356` | IPC-D-356 netlist for bare-board electrical test |

The files were prepared against JLCPCB's published capabilities, but any fab that
meets the table below can build them. For JLCPCB there is a step-by-step guide: [ordering-jlcpcb.md](ordering-jlcpcb.md).

## Board specifications

| | Upper | Lower | Service |
|---|---|---|---|
| Size | 31.5 × 48 mm | 31.5 × 48 mm | 18 × 32 mm |
| Layers | 6 | 4 | 2 |
| Thickness | 1.6 mm | 1.6 mm | 1.6 mm |
| Outer copper | 1 oz | **2 oz** | 1 oz |
| Inner copper | 0.5 oz | 0.5 oz or 1 oz | – |
| Minimum track / gap | 0.15 / 0.127 mm | 0.2 / 0.2 mm | 0.2 / 0.15 mm |
| Minimum via (hole / pad) | 0.3 / 0.5 mm | 0.3 / 0.7 mm | 0.3 / 0.6 mm |
| Surface finish | ENIG (JLCPCB does not offer HASL on 6 layers; ENIG is a paid option) | ENIG or HASL | any |
| Stack-up (JLCPCB name) | JLC06161H-3313 | JLC04161H-7628 | standard |
| Assembly sides | top **and** bottom | top only | top only |

Layer order, upper board: top signal / ground plane / signal / signal / 3.3 V plane / bottom signal.
Layer order, lower board: top / ground plane / battery (VESC) plane / bottom.

Choose ENIG for the upper board: it has 0.5 mm-pitch LGA sensor packages.
The boards carry no reserved spot for the fab's order number, so choose the option that removes it
("Remove mark" at JLCPCB); "specify a location" will not work.

## Assembly notes

* **Hand-soldered parts (not in the JLCPCB files):** the right-angle header
  `J1` on the upper board (3 × 12) and the two Samtec
  board-to-board connectors (`J1` lower: SFMC-110-02-L-D, `J3` upper: FTSH-110-04-L-DV). LCSC had only a
  handful of the Samtec parts when checked, so buy them from DigiKey, Mouser or Samtec and either
  hand-solder them or send them to the assembler as consigned parts. See [assembly.md](assembly.md).
* **Lower board `J2` (3 × 9 holes) is left empty.** Wires are soldered into the holes. Do not fit a pin header here: its pins would sit directly under the pins of the upper board's header.
* **Standoffs H1–H3** on the lower board are reflow-soldered M2 standoffs, 8.0 mm (Sinhoo SMTSO2080CTJ). At JLCPCB they are a "Standard PCBA only" part.
  If your assembler will not place them, solder them by hand or use loose M2 × 8 mm standoffs
  with screws from below.
* **Check rotations in the assembler's preview.** The `-cpl-jlc.csv` files already include JLCPCB's
  rotation corrections for each part (table in [ordering-jlcpcb.md](ordering-jlcpcb.md)); `-pos.csv` has
  KiCad's own angles for other assemblers. The corrections come from JLCPCB's library drawings, not
  from a built board, so still compare every polarised part against the assembly drawings
  (`docs/boards/<board>/<board>-assembly-top.svg`) before approving.
* **Barometer U3 and IMU U2** are moisture- and stress-sensitive LGA parts: no-clean flux only,
  no ultrasonic cleaning.

## Parts that need attention before ordering

Stock was checked for every part on 2026-11-18 (LCSC) and 2026-11-19 (JLCPCB's assembly library). Every
machine-placed part is in JLCPCB's library. Parts JLCPCB is short of can usually be pre-ordered through its parts
manager. All parts not listed below had more than 2,500 in stock.

| Part | Note |
|---|---|
| STM32F765VIT6 (U1) | **48 in stock** at both. The scarcest part; order it first. STM32F767VIT6 is pin-compatible and works with the same firmware. |
| ICM-45686 (U2) | 186 at JLCPCB, 492 at LCSC. ICM-42688-P fits the same footprint; the firmware detects either. |
| TPS62933DRLR (lower U1, U2) | **36 at JLCPCB**, 817 at LCSC; two per lower board. Pre-order if short. TPS62933FDRLR fits but runs in forced-PWM mode and can push current back into the battery rail if an ESC's BEC also feeds the 5 V pins. |
| Buzzer BZ1 | MLT-8530. The "+" mark on the part goes to pad 1 (marked "+" on the board). |
| 27 MHz crystal Y2 | 905 in stock. |
| Samtec SFMC-110-02-L-D / FTSH-110-04-L-DV | LCSC holds 30 and 5 of close variants only, and the LCSC numbers and prices in the BOM are those variants (C3323057 is SFMC-110-02-L-D-K-TR, C7279869 is FTSH-110-04-F-DV-TR). Buy the exact part numbers from DigiKey, Mouser or Samtec. Board-to-board pair. Use lead style **-04** on the FTSH (3.81 mm posts); other styles do not mate correctly at 8.0 mm. Do not order the FTSH with the -K option. |

Approximate component cost at single-unit prices is shown per board on the
[project page](https://peterjburke.github.io/stackf765/#boards). PCB fabrication,
assembly fees and shipping are extra and depend on quantity.

## Mounting hardware (not on the BOM)

| Item | Qty | Note |
|---|---|---|
| M2 × 4 mm screws | 3 | upper board into the standoffs |
| Silicone grommets for a 4 mm board hole with a 3 mm bore ("M4 to M3", Matek style) | 4 | lower board to frame, 20 × 20 mm. Dimensions vary between makers; measure yours. |
| Brass "M3 to M2" inserts for the grommets | 4 | only if the frame uses M2 screws |
| M2 screws and nuts to suit the frame | 4 | |
| JST-SH 6-pin cable, 100 mm, wired 1:1 (JST A06SR06SR30K102A) | 1 | flight controller to service board. JST's drawing for this part states pin 1 to pin 1; DigiKey's listing calls it "Reversed". Check with a meter. |
