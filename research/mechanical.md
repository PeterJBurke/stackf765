# Mechanical / connector research (two-board stacked FC, 31.5 x 48 mm, 1.6 mm PCBs)

Date: 2026-11-16. All dimensions in mm. "UNVERIFIED" = could not be confirmed from a manufacturer drawing in this session.
"Derived" = computed by me from dimensions that were read off a drawing (the inputs are verified, the result is arithmetic).
Stock/prices are a snapshot from the LCSC product API (wmsc.lcsc.com product detail) on this date.
Note: `jlcsearch.tscircuit.com/api/search` returned nothing for most of these connectors (its index only covers part of the catalogue), so LCSC numbers were found through `jlcsearch.tscircuit.com/headers/list.json` and stock was read from LCSC directly. JLCPCB assembly-library stock was NOT confirmed for any of them.

## Sources actually read

| Item | Source |
|---|---|
| Samtec SFMC print (3 sheets, rev CH) | https://suddendocs.samtec.com/prints/sfmc-1xx-xx-xx-d-xx-xx-mkt.pdf |
| Samtec SFMC catalogue page | https://suddendocs.samtec.com/catalog_english/sfmc.pdf |
| Samtec FTSH-DV print (5 sheets, rev ET) | https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-mkt.pdf |
| Samtec FTSH-DV footprint (rev H) | https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf |
| Samtec FTSH catalogue pages | https://suddendocs.samtec.com/catalog_english/ftsh_smt.pdf , older copy https://pccomponents.com/datasheets/SAMTEC-FTSH_SMT.PDF |
| Samtec TSW print (6 sheets, rev DR) | LCSC datasheet for C7366588 (TSW-XXX-XX-XXX-X-XX-XXX-MKT) |
| Samtec TSW catalogue page | https://suddendocs.samtec.com/catalog_english/tsw_th.pdf |
| XKB, HCTL, XFCN, Sinhoo, JST drawings | LCSC datasheet PDFs of the C-numbers listed below |
| KiCad footprints | local KiCad 9.0.9 library, /usr/share/kicad/footprints |
| Matek | https://www.mateksys.com/?portfolio=f405-wmo , https://www.mateksys.com/?portfolio=f405-minite |
| SpeedyBee | https://www.speedybee.com/speedybee-f405-mini-bls-35a-20x20-stack/ |

Not obtainable (blocked / not found): Samtec SFMC footprint PDF, Samtec mated-height table (samtec.com returned HTTP 429), DigiKey and Mouser product pages, Wurth datasheets (403), grommet dimension drawings, Pimoroni page (429).

---

## A. Board-to-board connector, 2x10, 1.27 mm

### A1. Samtec SFMC-110-02-S-D (socket, lower board top) + FTSH-110-xx-L-DV (header, upper board bottom)

**Mated stack height**

Samtec's own mated-height table could not be retrieved: **official table UNVERIFIED**. Derived from the two prints instead:

- SFMC -02 (SMT) height, board to top of socket: 4.70 +0.051/-0.127 (print sheet 2, section B-B).
- FTSH-DV, board to top of insulator (mating shoulder): 2.92 +0.13/-0.08 (print sheet 1). This is the same for every lead style; lead style only changes post length "A".
- Fully seated (insulator on socket top, my assumption): **7.62 mm (0.300") nominal, derived, worst-case +0.18/-0.21**.
- SFMC catalogue: "Insertion Depth 3.05 mm to 4.06 mm".

| FTSH lead style | Post length A | Seated stack (derived) | Comment |
|---|---|---|---|
| -01 | 3.05 | 7.62 | Insertion exactly at SFMC minimum (3.05); no margin for any standoff gap |
| -02 | 1.91 | n/a | Post shorter than SFMC minimum insertion; catalogue lists it for FLE. Not a valid SFMC mate |
| -03 | 1.65 | n/a | Same, listed for CLP-D. Not a valid SFMC mate |
| -04 | 3.81 | 7.62 | Older Samtec FTSH datasheet states "-04 = (3.81) .150 post (Mates with SFMC, SFMH)". Correct choice |
| -05 | 4.32 | 7.62 if it seats: UNVERIFIED | Post exceeds SFMC max insertion 4.06 when fully seated; listed for CLP-BE |

Note: the current FTSH catalogue page lists board mates "CLP, FLE" only and -04 as "mates with CLP-DH"; the SFMC catalogue lists board mate "TFM". The FTSH-04/SFMC pairing comes from the older Samtec FTSH datasheet, so confirm with Samtec before committing.

**SFMC-110-02-x-D body and land pattern**

- Body: length N x 1.27 + 0.38 = 13.08 +/-0.20; width 3.05 REF; height 4.70 above board; across leads 4.19 REF. Contact pitch 1.27, row spacing 1.27.
- Options on the print: -K (polyimide pick-and-place film, dia 4.00) and -P (plastic pick-and-place pad 10.01 x 5.72, adds 1.57 above the body, 5 positions minimum). **There is no -A alignment-pin option on SFMC**, so no alignment holes.
- Land pattern (pad size, row centres): **UNVERIFIED**, Samtec footprint PDF not retrievable. Only the 4.19 lead span, 1.27 pitch and 1.27 row spacing are confirmed.
- Current rating: 2.9 A per pin (2 pins powered), 219 VAC / 310 VDC, -55 to +125 C (SFMC catalogue).

**FTSH-110-xx-L-DV body and land pattern (Samtec footprint rev H)**

- Body: length N x 1.27 = 12.70 +0.13/-0.25; width 3.43 REF; insulator 2.51 REF; post 0.41 square; across leads 5.8.
- Pads: 0.74 x 2.79, pitch 1.27, outer edge to outer edge 6.86 (so pad centres at +/-2.035 from centreline, inner gap 1.28). First-to-last pad centre (N-1) x 1.27 = 11.43.
- -A option: two alignment-pin holes dia 1.02 on the connector centreline, spaced (N-2) x 1.27 = 10.16. Pin dia 0.89 REF, 0.86 below the seating plane. -K, -M, -P need no holes.
- Current rating: 3.4 A/pin with CLP, 2.9 A/pin with FLE (2 pins powered). No FTSH/SFMC-specific figure found; use 2.9 A (SFMC limit).

**Availability**

| Part | Source | Stock | Price |
|---|---|---|---|
| SFMC-110-02-L-D-K-TR | LCSC C3323057 | 30 | $5.50 @1 |
| SFMC-110-01-S-D (through-hole, wrong style) | LCSC C7075755 | 11 | $5.50 @1 |
| SFMC-110-02-S-D | LCSC | not listed | - |
| SFMC-110-02-S-D | DigiKey (regional page via search snippet) | 0, 4-week lead | UNVERIFIED |
| SFMC-110-02-S-D | Master Electronics (search snippet) | 740 | $7.23 @5 |
| FTSH-110-04-F-DV-TR | LCSC C7279869 | 5 | $4.19 @1 |
| FTSH-110-04-L-DV | Newark 250, Sager 250, Powell 165 (findchips) | - | about $1.7-3.1 |
| FTSH-110-04-L-DV-P-TR | Sager 3347, Powell 2209, TME 1375 (findchips) | - | about $1.4-3.8 |
| FTSH-110-01-F-DV-TR | LCSC C3338807 | 103 | $2.75 @1 |
| FTSH-110-01-L-DV-A | LCSC C21295869 | 28 | $3.21 @1 |
| FTSH-110-05-F-DV | LCSC C6558973 | 20 | $3.69 @1 |

DigiKey and Mouser live stock/pricing: **UNVERIFIED** (pages not fetchable).

### A2. Generic LCSC pairs

| Pair | Part | LCSC | Stock | Price | Key dimensions from datasheet |
|---|---|---|---|---|---|
| XKB header | X1321WVS-2x10J-C40D53 | C2881915 | 192 | $0.49 @1 | plastic 1.0; board to plastic top 1.5; pin above plastic 4.0; 0.4 sq pin; lead span 5.3; body width 3.4. Layout: pads 0.74 x 2.4, outer span 6.3 |
| XKB socket | X1321FVS-2x10-C43D48 | C2684738 | 1139 | $0.75 @1 | plastic 4.30; board to top 4.50; width 3.00; lead span 4.80. Layout: pads 0.74 x 2.20, outer span 5.80 |
| HCTL header | PZ127-2-10-S | C3975193 | 2215 | $0.18 @5 | plastic 1.0+/-0.15; board to plastic top PB 1.50; pin above plastic PA 3.80; total 5.30; lead span 5.50; width 3.4. Layout: pads 0.74 wide, outer span 6.5, inner gap 1.2 |
| HCTL socket | PM127-2-10-S-4.3 | C3975136 | 3025 | $0.37 @5 | plastic 4.3+/-0.2; board to top 4.6+/-0.2; width 3.0; lead span 4.70. Layout: pads 0.66 x 1.9, outer span 5.6 |

Other in-stock options not dimension-checked: BOOMELE 1.27-2*10P header C59981 (4830), Kinghelm KH-1.27FH-2X10P-H4.3-SMT socket C2938399 (5285), CONNFLY DS1065-06-2x10S8BSSR socket C19944617 (1246).

**Computed mated height (derived, plastic seated on plastic):**

- XKB pair: 4.50 + 1.50 = **6.0 mm**
- HCTL pair: 4.6 + 1.5 = **6.1 mm** (+/-0.3 from drawing tolerances)

Both are below the 7-10 mm target. Every generic 1.27 mm 2x10 SMD socket found on LCSC is the 4.3 mm plastic type; the one listed as "8.5 mm" (SAMZO C41374314) is actually H = 4.3 per its own drawing. The HCTL header drawing lists other plastic heights (0.85/1.0/1.5/1.7/2.0/2.5) but no LCSC part with a taller plastic was found. Whether the 4.0 mm pin clears the socket floor is UNVERIFIED (geometrically the tip ends 0.5 mm above the lower board).

**KiCad 9 footprints (read from the local library)**

- `PinHeader_2x10_P1.27mm_Vertical_SMD`: pads 2.4 x 0.74 at x = +/-1.95 (outer span 6.3, inner gap 1.5). **Exact match to XKB header layout.** Acceptable for HCTL header (leads 5.5 span; recommended outer 6.5). Too short for Samtec FTSH (Samtec wants 2.79 long pads, outer 6.86; leads span 5.8, leaving only 0.25 toe): make a custom footprint for FTSH.
- `PinSocket_2x10_P1.27mm_Vertical_SMD`: pads 2.1 x 0.75 at x = +/-1.8 (outer span 5.7, inner gap 1.5). **Matches XKB socket within 0.05 per side** (5.8 outer, 2.2 long). Covers HCTL socket (5.6 outer). Not checked against SFMC (footprint unavailable).
- Pin numbering: header pad 1 is at -x, socket pad 1 is at +x (the library mirrors them for mating). Since the header sits on the bottom side of the upper board, check pin 1 mapping by hand in the layout.

### A3. Recommendation and standoff

- **Recommended: SFMC-110-02-x-D + FTSH-110-04-x-DV with 8.0 mm M2 standoffs.** Seated height is 7.62, so 8.0 mm standoffs leave a 0.38 mm gap between insulators and the standoffs, not the connector, set the spacing. Contact insertion becomes 3.81 - 0.38 = 3.43 mm, inside SFMC's 3.05-4.06 window (derived). Do not use -01 with 8.0 mm standoffs (insertion 2.67, below minimum).
- No pair lands exactly on a metric standoff when fully seated: Samtec is 7.62, generics are 6.0/6.1. The XKB pair with 6.0 mm standoffs is the cheap option if a 6 mm gap is acceptable (it is outside the stated 7-10 mm range).
- **Standoff: Sinhoo SMTSO2080CTJ, LCSC C2916357**, stock 3720, $0.17 @5. Reflow-solderable brass (C3604, tin plated) round M2x0.4 female standoff: OD 5.56+/-0.13, length **8.00+/-0.13** above the board, pilot dia 3.60 +0/-0.15 x 1.53 into the PCB hole (drawing read). Soldered to the lower board, M2 screw from the upper board. Same family: 6 mm SMTSO2060CTJ C2915628 (1955), 7 mm SMTSO2070CTJ C2916355 (2897).
- Wurth 9774080243R (WA-SMSI, M2, 8 mm, steel, SMT) is an alternative per RS listings; one distributor lists 9.4 mm for the same number, so its length is UNVERIFIED.
- A loose brass/nylon hex M2 x 8 F-F standoff with a named part number was not verified.

---

## B. Right-angle 2.54 mm headers

### B1. Three-row right-angle, 3x12 (36 pins)

**Samtec TSW-112-08-x-T-RA** (order code confirmed: TSW-1NN-LL-P-T-RA; -08 is the shortest right-angle lead style; plating F/G/L/T/S)

From the print (sheet 2 and sheet 4 FIG 5) and catalogue:

- Hole pattern: 2.54 grid, 3 rows at 2.54 row pitch. Recommended hole 1.02 +/-0.03 is stated for the locking-lead option; plain -RA hole diameter is not separately stated. Post 0.64 square.
- Body: 2.54 thick (along pin axis) x 8.13 high (triple) x N x 2.54 = 30.48 long.
- First hole row (lowest pin row) to rear face of body: 1.52. Tail rows at 1.52 / 4.06 / 6.60 behind the body.
- Mating post beyond body front face: 5.84. Derived: first hole row to body front 4.06; first hole row to pin tips 9.90; third (rearmost) hole row to pin tips 14.98.
- Tail length "E" for -08: 2.29 measured from the body's board-side face (0.69 mm through a 1.6 mm board if the body sits on the board).
- Row heights above PCB: rows are 1.52 / 4.06 / 6.60 from the body's board-side face and the body is 8.13 tall (derived from 8.13 body and 2.54 pitch). The print also shows a 1.0 mm dimension between that face and a reference plane whose meaning I could not determine, so **heights above PCB are 1.52/4.06/6.60 and overall 8.13, or 1.0 mm more: UNVERIFIED**.
- Availability: TSW-112-08-G-T-RA LCSC C7366588, stock 5, $5.36. TSW-110-08-T-T-RA (3x10) C7128283, stock 10. TSW-108-08-T-T-RA (3x8) C6724300, stock 83, $1.61. TSW-125-08-G-T-RA (3x25) C6339711, stock 10. Octopart snippet: TSW-112-08-T-T-RA about 3,900 pcs across distributors. DigiKey/Mouser: UNVERIFIED.

**Generic: HCTL PZ254-3-NN-W-2.5** (drawing "PZ254-3-N-W-2.5-XX (L15.54)")

- Hole pattern: 2.54 x 2.54 grid, 3 rows, **hole dia 1.02**. Pin 0.64 square.
- Body: 2.5+/-0.2 thick x **7.50+/-0.15 high** x N x 2.54 long.
- PA = 6.00 (pin beyond body front); PB = 9.54 (body front face to rearmost tail row); L = 15.54 (pin tip to rearmost tail row); PC = 3.00 (tail length from body side, so about 1.4 mm through a 1.6 mm board).
- Derived: first hole row to body rear face 1.96; first hole row to body front 4.46; first hole row to pin tips 10.46; rearmost hole row to pin tips 15.54.
- Derived row heights with body resting on the PCB: **1.21 / 3.75 / 6.29**; overall height 7.50.
- LCSC: only the 3x3 piece was found, **PZ254-3-03-W-2.5-G0, C7429379, stock 5040, $0.24 @5**. Four side by side on the 2.54 grid make 3x12. No generic 3x12 or 3x40 right-angle part was found on LCSC.

**Wurth / Sullins:** Wurth 61303631021 follows the numbering pattern (61303611021 is single-row angled, 61303621021 dual-row angled) but its datasheet could not be opened: UNVERIFIED. No Sullins triple-row right-angle part number was found.

### B2. Two-row right-angle 2x10

KiCad `PinHeader_2x10_P2.54mm_Horizontal` (read from the library): pads 1.7 with 1.0 drill; pad 1 row at x = 0, pad 2 row at x = 2.54; body from x = 4.04 to 6.58; pin tips at x = 12.58.

**Correction to the question:** 1.5 and 4.04 are not heights. They are horizontal distances from the two hole rows to the rear face of the body (near row 1.5, far row 4.04). Odd pads (far row) are the upper pin row, even pads the lower row.

Commonly sold parts, from their drawings:

| | KiCad | XFCN PZ254R-12-20P | HCTL PZ254-2-10-W-8.5 |
|---|---|---|---|
| Hole | 1.0 drill | 1.02 | 1.02 |
| Body | 2.54 thick | 2.50 thick x 5.00 high | 2.5 thick x 5.0 high |
| Near hole row to body rear | 1.50 | 1.86 (derived from 6.9) | 1.86 (derived from PB 6.90) |
| Near hole row to body front | 4.04 | 4.36 | 4.36 |
| Near hole row to pin tips | 10.04 | 10.36 | 10.36 |
| Pin beyond body | 6.0 | 6.0+/-0.2 | 6.00 |
| Tail from body side | - | 3.0 | 3.00 |

So the hole pattern matches, but real bodies and pin tips sit about 0.3 mm further out than the KiCad outline.

- LCSC: **XFCN PZ254R-12-20P, C492438, stock 41165, $0.18 @5**. Also HCTL PZ254-2-10-W-8.5 C2894990 (7455, $0.35 @5), XKB X6521WR-2x10H-C60D30 C706891 (172).
- Overall height above board: **5.0 mm** (body resting on board). Derived row centres 1.23 and 3.77.
- Top of a mated Dupont housing on the upper row: about **5.0 mm** (3.77 + 1.27), assuming a 2.54 square housing. Housing dimension UNVERIFIED (no housing drawing read). On the HCTL 3-row part the same assumption gives about 7.6 mm.

---

## C. 20 x 20 mounting with grommets

What the makers state:

- Matek F405-miniTE: "20 x 20mm/Φ3mm with Silicon Grommets", "20 x 20mm/Φ2mm with Silicon & Brass Grommets"; includes "6x Silicon grommets M4 to M3" and "6x Brass grommets M3 to M2". H743-MINI and F405-mini are listed with the same kit by resellers. The bare PCB hole is therefore nominally **4 mm** (inferred from "M4 to M3"; Matek does not print the bare hole diameter).
- SpeedyBee F405 Mini: "20 x 20mm 3.5mm hole diameter, Compatible with M2 and M3 screws/Silicone grommets".

Grommet dimensions (groove diameter, groove width, flange OD, total height): **UNVERIFIED**. No vendor or manufacturer page that could be opened gives them; retailers only list overall sizes such as "M3 x 4.5 / 6.6 / 8.0 / 8.4 mm" without saying what they measure.

Working recommendation (the grommet-dependent numbers are estimates, measure the actual grommets before freezing the layout):

- PCB hole: **4.0 mm** non-plated for Matek-style M4-to-M3 silicone grommets with M3-to-M2 brass inserts, or 3.5 mm if using SpeedyBee-style grommets.
- Flange keep-out on both PCB surfaces: estimate 7 mm diameter. UNVERIFIED.
- Protrusion above and below the board: estimate 1.5-2.5 mm each side. UNVERIFIED.

---

## D. Matek F405-WMO / F405-WMN (https://www.mateksys.com/?portfolio=f405-wmo)

- F405-WMO: **32 x 22 x 12.7 mm, 9 g** (product page and photo). F405-WMN shown beside it at 31 x 26 mm.
- Construction: two boards, FC on top and PDB below, joined at four holes by metal spacers and screws. Mounting pattern is not stated; scaled from Matek's layout render it is roughly 18 x 12 mm: UNVERIFIED.
- Board-to-board link: one **2x6 (12-pin)** connector, female socket on the PDB top, male header on the FC bottom. Signals per Matek's layout drawing: one column Vx, Vx, Vx, 5V, Curr, Vbat; the other G, G, G, S1, S2, S3. Pitch is not stated; scaled from photos it is about 1.27 mm: UNVERIFIED.
- USB/Beep adapter: "USB(Type-C)/Beep (Passive buzzer) Extender" with "20cm JST-SH-6P cable". Adapter is 22 mm long, with Type-C, passive buzzer, buzzer ON/OFF switch, DFU button, red USB-power LED.
- JST-SH-6P order as printed on the FC silk: **Buz-, Boot, D+, D-, G, 4V5**. Adapter silk reads 4V5, G, D-, D+, Boot, Buz-, the mirror image because the two connectors face each other; that is consistent with a straight cable. Which end is pin 1 is not marked. WMN silk shows the same order (Bz-, Boot, D+, D-, G, 4V5).
- PDB pads: four large via-stitched pads along one short edge, in order **"-", "-", "ESC+", "BAT+"**; 5.4-30 V (2-6S); current sense 132 A range / 90 A continuous (0.3 mOhm shunt). Small S1/S2/S3 ESC signal pads down one long edge. Vx jumper 5 V default / 6 V.
- FC pads are 2.54 mm through-holes ("Dupont 2.54 pins", shipped unsoldered): three rows of 8 along the top edge and S5-S9 as 3-row servo columns (signal / Vx / G) along the bottom edge.

---

## E. JST SH 6-pin, SM06B-SRSS-TB

- KiCad footprint **`Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` exists** (KiCad 9.0.9 library). Signal pads 0.6 x 1.55 at y = -2.0, x = -2.5 ... +2.5 (pad 1 at x = -2.5); two MP pads 1.2 x 1.8 at (+/-3.8, 1.875); body outline y from -1.675 to +2.575.
- Pin 1: signal leads are at the rear, the mating opening is at the opposite (mounting-tab) side. **Looking into the mating face with the PCB underneath, pin 1 is on the left.** This comes from the KiCad footprint and agrees with JST's through-hole side-entry drawing (Circuit No.1 on the left). The JST SMT sheet itself does not label circuit No.1, so this is not confirmed from the SMT drawing.
- JST drawing dimensions for SM06B-SRSS-TB: A = 5.0, B = 8.0 wide, 4.25 deep, 2.9 high, 1.0 pitch.
- LCSC C160405, SM06B-SRSS-TB(LF)(SN), stock 17104, $0.90 @1.
- Ready-made 100 mm cables:
  - Pololu #5543, 10 cm, 6-pin JST SH-style female-female, 28 AWG, $3.32, shown out of stock (backorder). Page says "the black wire is pin 1" but does not state end-to-end mapping: 1:1 UNVERIFIED. DigiKey also lists a Pololu #4765 100 mm 6-pin cable (search snippet).
  - Pimoroni CAB1009, 100 mm, 6-pin, 26 AWG, pack of 4, GBP 2.50 (also The Pi Hut). Search snippet of Pimoroni's description says both connectors are the same way up when laid flat, so **pin 1 goes to pin 6 (reversed)**. Page itself could not be opened.
  - No Adafruit or SparkFun 6-pin double-ended SH cable was found.
- Wiring is vendor-dependent, so buzz out any cable before use. Matek's own cable behaves as straight for its mirrored silks (see D).
