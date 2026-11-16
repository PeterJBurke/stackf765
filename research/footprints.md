# Footprint facts verified against manufacturer drawings

Date: 2026-11-16. Every value below was read from the manufacturer PDF/drawing named in the section (LCSC-hosted copies unless stated) or from the KiCad library files under `/usr/share/kicad`. Anything that could not be read from a drawing is marked **UNVERIFIED**.

Coordinates are KiCad footprint coordinates: x to the right, y DOWN, in mm, viewed from the component side (top view), origin at body centre.

---

## 1. SMD magnetic buzzer MLT-8530 (C94599) / KLJ-8530-3627 (C189206)

### KiCad `Buzzer_Beeper:MagneticBuzzer_CUI_CMT-8504-100-SMT`

| Pad | x | y | Size | Corner |
|---|---|---|---|---|
| 1 | -3.5 | -3.5 | 2.5 x 2.5 | top-left (silk and fab "+" are at this pad) |
| 2 | -3.5 | +3.5 | 2.5 x 2.5 | bottom-left |
| 3 | +3.5 | +3.5 | 2.5 x 2.5 | bottom-right |
| 4 | +3.5 | -3.5 | 2.5 x 2.5 | top-right |

### MLT-8530 (Jiangsu Huaneng spec, pages 2 and 4)

- Body 8.5 x 8.5, height 3.0 (2.4 to a step), terminals span 8.7 x 8.7. Rated 3.6 Vo-p, coil 16 +/-3 ohm, 2700 Hz.
- "5.2 Soldering pattern": four square pads 2.3 x 2.3, gap 4.8 between pads in both axes, so pad centres are at (+/-3.55, +/-3.55).
- Labels in that pattern and in the top-view outline drawing (same orientation):
  - top-left = **+ Lead**
  - bottom-left = **- Lead**
  - top-right and bottom-right = **Dummy Pad** (both)
  - **Sound Port** is in the middle of the right-hand side face (side-firing), i.e. on the dummy-pad side, opposite the two leads. A triangle on the drawing marks it.
- The text says "Terminal plate: 3 soldering pads" while the drawing shows four corner pads (two dummy). Which dummy is actually metal is UNVERIFIED; treat both as NC and solder both.
- The soldering pattern is not explicitly labelled "top view". It is drawn in the same orientation as the body view that shows the outline with pads half hidden (top view); the other view, with fully visible pads, is the bottom view. The KLJ drawing below independently gives the same handedness.

### KLJ-8530-3627 (Changzhou Kailijin spec, page 3)

- Body 8.5 x 8.5, height 3.0 +/-0.3, corner pads with 4x 1.5 x 45 deg chamfer. Rated 3.6 Vp-p, 16 +/-3 ohm, 2731 Hz.
- **No recommended land pattern in this datasheet: pad size/positions UNVERIFIED.**
- Bottom view labels "-POLARITY" and "+POLARITY" on the two pads of one side. Top view shows a round "+" mark at the corner that corresponds to the + pad, and a solid triangle on the opposite side of the top face.
- So: the top-face "+" mark sits over the + pad; the - pad is the other corner on the same side; the triangle is on the far side from the two leads (same arrangement as MLT-8530, where the triangle side is the sound-port side).
- The sound-port slot is shown only in the side view; which side face it is on is not labelled. That the triangle points to it is an inference from the MLT drawing: **UNVERIFIED for KLJ**.
- The other two corner pads are unlabelled (NC/dummy status UNVERIFIED, same position as MLT dummies).

### Mapping to the KiCad footprint

Place the part with the **sound port / triangle side facing +X (right)**. Then:

| KiCad pad | MLT-8530 / KLJ-8530 |
|---|---|
| 1 (top-left, "+" silk) | **+** |
| 2 (bottom-left) | **-** |
| 3 (bottom-right) | dummy / NC |
| 4 (top-right) | dummy / NC |

Land pattern compatibility: MLT pads cover 2.40 to 4.70 mm from centre; KiCad pads cover 2.25 to 4.75 mm. KiCad pads fully contain the MLT recommended pads (0.05 to 0.15 mm larger per edge). **Compatible.**

---

## 2. AT7456E (C82351) HTSSOP-28

From the datasheet package page (p.38, "HTSSOP28" table):

| Symbol | Min | Nom | Max |
|---|---|---|---|
| D (body length) | 9.60 | 9.70 | 9.80 |
| E (overall width incl. leads) | 6.20 | 6.40 | 6.60 |
| E1 (body width) | 4.30 | 4.40 | 4.50 |
| A (height) | - | - | 1.20 |
| e (pitch) | 0.55 | 0.65 | 0.75 |
| b (lead width) | 0.20 | - | 0.29 |
| L (foot) | 0.45 | 0.60 | 0.75 |
| **D1 (EP length)** | | **6.20 REF** | |
| **E2 (EP width)** | | **2.75 REF** | |

KiCad EP variants available in `Package_SO.pretty`:

- `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.75x6.2mm` (+ `_ThermalVias`): pad 29 = 2.75 x 6.2
- `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm` (+ `_ThermalVias`): pad 29 = 2.85 x 5.4
- `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm` (+ `_ThermalVias`): pad 29 = 3.4 x 9.5
- `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm_Mask2.4x6.17mm` (+ `_ThermalVias`)
- `NXP_HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.2x3.4mm` (+ `_ThermalVias`)

**Best fit: `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.75x6.2mm`** (exact EP match; EP is pad 29). Signal pads in this family are 1.475 x 0.4 at x = +/-2.8625.

---

## 3. TI SOT-583 (DRL0008A): TPS62933DRLR and LM66200DRLR

### TI land pattern (tps62933.pdf p.48-49; lm66200.pdf p.18-19 shows the same DRL0008A numbers)

- Package: body 1.1-1.3 wide x 2.0-2.2 long, 1.5-1.7 across leads, 0.6 max height, pitch 0.5, lead width 0.17-0.27.
- Land pattern example: 8x pad **0.67 x 0.3** (R0.05 corners), pitch **0.5**, row centre-to-centre **1.48**.
- Pin 1 top-left (pin-1 ID area on top face), pins 1-4 down the left side, 5-8 up the right side.

### KiCad `Package_TO_SOT_SMD:SOT-583-8`

Pads roundrect 0.67 x 0.3; pads 1-4 at x = -0.74, y = -0.75 / -0.25 / +0.25 / +0.75; pads 5-8 at x = +0.74, y = +0.75 / +0.25 / -0.25 / -0.75. Row spacing 1.48. **Exact match to the TI land pattern, including numbering.**

### Pinouts

TPS62933 (datasheet pin table, top view): **1 RT, 2 EN, 3 VIN, 4 GND, 5 SW, 6 BST, 7 SS, 8 FB**. Confirmed. (Pin 7 is PG instead of SS only on the TPS62933P variant.) EN: high or floating enables. RT: float = 500 kHz, GND = 1.2 MHz, or resistor.

LM66200 (Figure 5-1 top view and Table 5-1): **1 GND, 2 VOUT, 3 VIN1, 4 ON (active low), 5 GND, 6 VIN2, 7 VOUT, 8 ST**. Confirmed.

- **ON is active LOW**: device enabled when ON is low; ON high turns off both channels (VOUT Hi-Z).
- **ST is an open-drain output** that "must be pulled up to an external voltage for proper operation". High (released) when VIN1 is powering the output; pulled low when VIN2 is powering the output; pulled low during a fault and when ON is high. VOL 0.1 V at 1 mA. TI suggests pulling it up to VIN1 to cut quiescent current when VIN2 is in use.
- Truth table: VIN1 > VIN2, ON low: ST high, VOUT = VIN1. VIN1 < VIN2, ON low: ST low, VOUT = VIN2. ON high: ST low, VOUT Hi-Z.

---

## 4. Molex 104031-0811 microSD socket (drawing SD-104031-001, LCSC C585350)

### KiCad `Connector_Card:microSD_HC_Molex_104031-0811` pads

| Pad | x | y | Size |
|---|---|---|---|
| 1 | -3.105 | -5.45 | 0.85 x 1.1 |
| 2 | -2.005 | -5.45 | 0.85 x 1.1 |
| 3 | -0.905 | -5.45 | 0.85 x 1.1 |
| 4 | +0.195 | -5.45 | 0.85 x 1.1 |
| 5 | +1.295 | -5.45 | 0.85 x 1.1 |
| 6 | +2.395 | -5.45 | 0.85 x 1.1 |
| 7 | +3.495 | -5.45 | 0.85 x 1.1 |
| 8 | +4.545 | -5.45 | 0.75 x 1.1 |
| 9 | -5.74 | +0.70 | 1.2 x 1.0 |
| 10 | -5.74 | +4.40 | 1.2 x 1.0 |
| 11 | -5.565 | -5.325 | 1.55 x 1.35 (Molex G1) |
| 11 | +5.755 | -5.10 | 1.17 x 1.8 (Molex G2) |
| 11 | -2.24 | +5.375 | 1.9 x 1.35 (G3/G4) |
| 11 | +3.73 | +5.375 | 1.9 x 1.35 (G3/G4) |

The KiCad footprint is the Molex "Recommended PCB layout" rotated 180 degrees; every pad position and size checks against the drawing dimensions (3.105 offset, 7x 1.1 pitch, 7x 0.85 + 1x 0.75 wide, 1.1 long, G1 1.55 x 1.35, G2 1.17 x 1.8, G3/G4 1.9 x 1.35, detect pads 1.2 x 1.0 at 5.14 + 0.6 from centre).

### Signal mapping

The Molex drawing numbers the contacts No.1 to No.8, with No.1 at the 3.105 mm offset end and the narrow 0.75 pad at the No.8 end, and gives the card pin map T1..T8. Hence:

| KiCad pad | Signal |
|---|---|
| 1 | DAT2 |
| 2 | CD/DAT3 |
| 3 | CMD |
| 4 | VDD |
| 5 | CLK |
| 6 | VSS |
| 7 | DAT0 |
| 8 | DAT1 |
| 9, 10 | card-detect switch (two terminals: "switch terminal" and "detect terminal") |
| 11 (x4) | metal shell / ground pattern G1-G4 |

- Card detect: **open without card, closed with card inserted** (drawing table). Which of pads 9/10 is the "switch" vs "detect" terminal is not identified on the drawing (UNVERIFIED, and irrelevant for a simple switch). The drawing lists them separately from the shell and calls only G1-G4 "ground pattern"; isolation of both switch pads from the shell is not explicitly stated (UNVERIFIED).

### KiCad symbols (`Connector.kicad_sym`)

| Symbol | Pins |
|---|---|
| `Micro_SD_Card` | 1 DAT2, 2 DAT3/CD, 3 CMD, 4 VDD, 5 CLK, 6 VSS, 7 DAT0, 8 DAT1, 9 SHIELD |
| `Micro_SD_Card_Det1` | 1-8 as above, 9 DET, 10 SHIELD |
| `Micro_SD_Card_Det2` | 1-8 as above, 9 DET_B, 10 DET_A, 11 SHIELD |
| `Micro_SD_Card_Det_Hirose_DM3AT` | extends `Micro_SD_Card_Det2` (same pins) |

**Use `Connector:Micro_SD_Card_Det2`** (or the DM3AT alias): pins 1-8 = signals, 9/10 = detect switch, 11 = shield. This matches the Molex footprint pad numbers one-to-one. `Micro_SD_Card` and `_Det1` do NOT match (their pin 9/10 would land on the switch pads, shield unconnected).

### Size and orientation

- Body: 11.95 +/-0.15 wide (x) by 11.40 +/-0.15 deep (y); height **1.42 +/-0.15** above the PCB.
- In KiCad coordinates the body spans x = +/-5.975, y = -5.70 to +5.70. Pad copper extremes: x = +/-6.34, y = -6.0 to +6.05.
- **Card insertion edge: the -Y edge (the edge with signal pads 1-8)**. The Molex top view shows the card outline protruding 4.0 +/-0.2 mm beyond the "product line" on the solder-tail side (overall 15.4 with card). So an inserted card occupies roughly x = -5.5 to +5.5 about the "card centre", y down to about -9.7. The card centre is offset 0.095 mm from the socket centre.
- Push-pull type (no ejector spring).

---

## 5. YXC 3225 crystals

Sources: C2973805 = part-specific spec for XL2EL89COI-111YLC-8M (YSX321SL, 8 MHz, 12 pF, +/-10 ppm, ESR 150 ohm max). C5210645 = generic YSX321SL series sheet (the LCSC PDF does not name X322527MMB4SI itself; same series drawing).

Both drawings are identical:

- Top view: **#1 bottom-left, #2 bottom-right, #3 top-right, #4 top-left**.
- "Top View Crystal Connection": crystal element between **#1 and #3**; **#2 and #4 = GND** (case/lid).
- Body 3.20 x 2.50 x 0.70. Suggested layout: pads 1.4 x 1.2, gaps 0.8 (x) and 0.5 (y), so centres at (+/-1.1, +/-0.85).

KiCad `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm`: pad 1 (-1.1, +0.85) bottom-left, pad 2 (+1.1, +0.85) bottom-right, pad 3 (+1.1, -0.85) top-right, pad 4 (-1.1, -0.85) top-left; pads 1.4 x 1.2.

**Identical numbering and identical land pattern. Crystal = pads 1 and 3; GND = pads 2 and 4.**

---

## 6. HCTL 1.27 mm 2x10 socket PM127-2-10-S-4.3 (C3975136) and header PZ127-2-10-S (C3975193)

### Manufacturer land patterns

Socket (drawing PM127-2-N-S-4.3-XX, "Recommended P.C.B Layout (Top Side)"):

- Pad width 0.66, pitch 1.27, gap between the two pad rows 1.9, overall across pads 5.6. So pads are 0.66 x 1.85, centred at +/-1.875 from the centre line (cover 0.95 to 2.80).
- Body height 4.3 +/-0.2 (4.6 +/-0.2 overall dimension shown), body width 3.0 +/-0.15, lead span 4.70 +/-0.25, body length 1.27 x N + 0.4.
- Optional locating posts: 2x dia 0.6 posts, 0.9 long, PCB holes 2x dia 0.8 on the centre line at 1.27 x N - 2.54 spacing. Per the ordering code, posts exist only with the trailing "-P" option; the part number here has no "-P", so no holes expected (confirm on the LCSC photo: UNVERIFIED).

Header (drawing PZ127-2-N-S-1.0-XX (L5.3), "Recommended P.C.B Layout (Top Side)"):

- Pad width 0.74, pitch 1.27, gap between rows 1.2, overall W + 1 = 6.5 (W = 5.50). So pads are 0.74 x 2.65, centred at +/-1.925 (cover 0.60 to 3.25).
- Plastic height 1.0 +/-0.15, body width 3.4 +/-0.15, lead span W = 5.50 +/-0.25, PA = 3.80, PB = 1.50, L = 5.30 (total pin length), pin 0.4 square.
- Optional posts as above (dia 0.6, holes dia 0.8); default is without post.

Neither HCTL drawing assigns pin numbers (rows are only labelled "1P"/"2P"). Pad numbering is therefore purely the KiCad convention.

### KiCad footprints

`Connector_PinSocket_1.27mm:PinSocket_2x10_P1.27mm_Vertical_SMD`: pads 2.1 x 0.75 at x = +/-1.8 (cover 0.75 to 2.85). **Odd pads on the +x (right) side, even pads on the -x (left) side.** Pad 1 = (+1.8, -5.715), pad 2 = (-1.8, -5.715), pad 19 = (+1.8, +5.715), pad 20 = (-1.8, +5.715). y step 1.27.

`Connector_PinHeader_1.27mm:PinHeader_2x10_P1.27mm_Vertical_SMD`: pads 2.4 x 0.74 at x = +/-1.95 (cover 0.75 to 3.15). **Odd pads on the -x (left) side, even pads on the +x (right) side.** Pad 1 = (-1.95, -5.715), pad 2 = (+1.95, -5.715), pad 19 = (-1.95, +5.715), pad 20 = (+1.95, +5.715).

Compatibility: socket: KiCad pads contain the HCTL pads in length on the outside (2.85 vs 2.80) and extend 0.2 further inward; width 0.75 vs 0.66. Header: KiCad pads 0.75-3.15 vs HCTL 0.60-3.25 (0.1 shorter at the toe, 0.15 shorter at the heel); lead tips at 2.75 nominal are inside both. **Both KiCad footprints are usable for the HCTL parts.**

### Does header pad N mate with socket pad N in the stacked arrangement?

Setup: socket on TOP of the lower board, unflipped, at (X, Y), rotation 0. Header on the BOTTOM of the upper board at the same (X, Y), rotation 0, flipped by KiCad's default left-right flip (mirror in x about the footprint origin).

- Socket pad positions seen from above: pad 1 at (+1.8, -5.715), pad 2 at (-1.8, -5.715); pad 2k-1 at x > 0 and pad 2k at x < 0, y = -5.715 + 1.27 (k-1).
- Header library positions: pad 1 at (-1.95, -5.715), pad 2 at (+1.95, -5.715). After the left-right flip, seen from above through the board: pad 1 at (**+1.95**, -5.715), pad 2 at (**-1.95**, -5.715); pad 2k-1 at x > 0, pad 2k at x < 0, same y as the socket.
- Each SMD lead exits outward from its own pin row, so the pin belonging to a pad on the +x side is the +x pin row (x = +0.635), directly above the socket contact row whose lead goes to the +x socket pad.

**Yes: header pad N mates with socket pad N** (odd pads both on +x, even pads both on -x, same y per pair). This is exactly why the KiCad socket footprint is numbered as the mirror image of the header.

Caveats:

- This holds for rotation 0 or 180 applied to both. For other angles the requirement is that the header's pads, as seen from above, are the x-mirror of its library coordinates with the same rotation as the socket, i.e. world position = R(theta) applied to (-x_lib, y_lib). If boards are generated by script, check numerically that header pad 1 and socket pad 1 land at the same y and on the same side (x differing only by 1.95 vs 1.8); a top-bottom flip or a rotation sign error swaps odd/even or reverses the order.
- If both connectors were on facing sides but one footprint were replaced by the other type (two headers, or socket numbered like the header), rows would be swapped.
- Mated stack height is not given in either HCTL drawing: UNVERIFIED (socket body 4.3, header plastic 1.0, pin above plastic PA 3.80).

---

## 7. XKB TS-1187A-B-A-B tact switch (C318884, drawing TS-1187A-X-X-X)

- Drawing terminals: A top-left, B top-right, C bottom-left, D bottom-right. Circuit diagram: **A-B internally connected, C-D internally connected, switch closes between the A/B pair and the C/D pair.**
- PCB layout (top view): pads span 5.0 to 7.0 in x (1.0 long, centres +/-3.0) and 3.0 to 4.5 in y (0.75 wide, centres +/-1.875).
- Body 5.1 x 5.1, 6.5 +/-0.25 over terminals, actuator dia 2.0, travel 0.2-0.25 mm. Part code -B-A-B = 160 gf, height code A = 1.5 mm, brass keystake. Rating 50 mA 12 V DC.

KiCad `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A`: pad "1" twice at (-3, -1.875) and (+3, -1.875); pad "2" twice at (-3, +1.875) and (+3, +1.875); all 1.0 x 0.75.

**Pad 1 = A+B (the two top pads, internally connected). Pad 2 = C+D (the two bottom pads, internally connected). The switch closes between pad 1 and pad 2.** Land pattern identical to the XKB drawing. Each same-numbered pair can be used as a through-connection, left to right.

---

## 8. Sinhoo SMTSO2060CTJ (C2915628)

From the Sinhoo drawing (description "M2*5.56*L6+1.53", brass C3604, tin finish, "based on PEM SMTSO"):

| Feature | Value |
|---|---|
| Thread | M2 x 0.4, through |
| Body (flange) diameter | 5.56 +/-0.13 |
| Body length above PCB | 6.00 +/-0.13 |
| Pilot diameter | 3.60 +0 / -0.15 |
| Pilot length | 1.53 +0 / -0.15 |

- **Recommended PCB hole diameter: UNVERIFIED** (not on the Sinhoo drawing).
- **Recommended pad / annular ring diameter: UNVERIFIED** (not on the Sinhoo drawing).
- Constraints that do follow from the drawing: hole must clear the 3.60 max pilot; the solder land must sit under the 5.56 +/-0.13 body (max 5.69); pilot 1.53 max is shorter than a 1.6 mm board, so it does not protrude.
- From memory only (PEM SMTSO bulletin, same 5.56 / 3.6 / 1.53 geometry; could not be fetched, NOT verified here): hole 3.73 +0.08 / -0, solder pad dia 6.19 minimum. Check against the PEM datasheet before committing.

---

## 9. JLCPCB capabilities (jlcpcb.com/capabilities/pcb-capabilities, fetched 2026-11-16)

Applies to multilayer (4- and 6-layer) FR-4; the page makes no 4-vs-6-layer distinction other than where noted.

| Item | Value |
|---|---|
| Min track / space, 1 oz, multilayer | 0.09 / 0.09 mm (3.5 / 3.5 mil); 3 mil acceptable in BGA fan-outs |
| Min track / space, 2 oz, multilayer | 0.15 / 0.15 mm (6 / 6 mil) (0.16 / 0.16 on 2-layer) |
| Outer copper offered on multilayer | 1 oz or 2 oz. **Yes, 2 oz outer is offered on 4-layer.** Inner 0.5 oz (default) / 1 oz / 2 oz |
| Min via hole / via diameter | 0.15 / 0.25 mm (0.1 / 0.2 only for boards <= 1 mm with ENIG/OSP) |
| Via without extra charge | Extra cost applies to 0.1 or 0.15 mm holes (any pad) and to 0.2 or 0.25 mm holes with pad < 0.45 mm. So free: **0.3 mm hole or larger, or 0.2 / 0.25 mm hole with pad >= 0.45 mm.** "Preferred min via hole 0.2 mm". Via pad should be 0.1 mm (0.15 preferred) larger than the hole |
| PTH annular ring, multilayer 1 oz | recommended >= 0.20 mm, absolute min 0.15 mm (2 oz: >= 0.254 mm) |
| Via hole-to-hole spacing | 0.2 mm |
| Pad (PTH) hole-to-hole spacing | 0.45 mm |
| Via hole to track | 0.2 mm |
| PTH hole to track | min 0.28 mm, 0.35 recommended |
| Inner-layer via hole to copper | 0.2 mm; inner-layer PTH pad hole to copper 0.3 mm |
| NPTH to track/copper | 0.2 mm |
| NPTH min diameter | 0.50 mm |
| NPTH pad annular ring (if a pad is drawn) | >= 0.45 mm |
| Pad to track clearance (1 oz) | 0.1 mm (0.09 locally at BGA) |
| SMD pad to pad, different nets | 0.15 mm; minimum SMD pad 0.25 x 0.25 mm |
| Same-net track spacing | 0.25 mm |
| Board edge to copper, routed | >= 0.2 mm (V-cut edges >= 0.4 mm) |
| Soldermask bridge (dam), 1 oz | 0.10 mm min pad spacing for green/red/yellow/blue/purple; 0.13 mm for black/white. 2 oz: 0.20 mm |
| Soldermask expansion | 1:1 allowed; keep >= 0.09 mm from mask opening to neighbouring traces |
| Plugged (mask-filled) vias | max 0.5 mm diameter, >= 0.35 mm from other mask openings |
| Silkscreen | line width >= 0.15 mm; text height >= 1.0 mm (40 mil); pad to silk 0.15 mm |
| Hole tolerance | PTH +0.13 / -0.08 mm; position +/-0.075 mm |
| Min plated slot | 0.35 mm (multilayer) |
| Board thickness tolerance | +/-10% at 1.6 mm |
| Via-in-pad (epoxy filled and capped) | stated as default process for 6-layer and above; via 0.15-0.55 mm |

### Standard stackups (jlcpcb.com/impedance, 1.6 mm, 1 oz outer / 0.5 oz inner)

**JLC04161H-7628** (4-layer default):

| Layer | Material | Thickness |
|---|---|---|
| L1 | Copper | 0.035 mm |
| Prepreg | 7628 x1 | 0.2104 mm |
| L2 | Copper | 0.0152 mm |
| Core | | 1.065 mm (1.1 mm with copper) |
| L3 | Copper | 0.0152 mm |
| Prepreg | 7628 x1 | 0.2104 mm |
| L4 | Copper | 0.035 mm |

**JLC06161H-3313** (6-layer):

| Layer | Material | Thickness |
|---|---|---|
| L1 | Copper | 0.035 mm |
| Prepreg | 3313 x1 | 0.0994 mm |
| L2 | Copper | 0.0152 mm |
| Core | | 0.55 mm |
| L3 | Copper | 0.0152 mm |
| Prepreg | 2116 x1 | 0.1088 mm |
| L4 | Copper | 0.0152 mm |
| Core | | 0.55 mm |
| L5 | Copper | 0.0152 mm |
| Prepreg | 3313 x1 | 0.0994 mm |
| L6 | Copper | 0.035 mm |

Alternatives also listed: JLC04161H-3313 (prepreg 0.0994, core 1.265); JLC06161H-7628 (prepreg 0.2104 outer, cores 0.4, middle prepreg 7628 0.2028).

Dielectric constants quoted by JLCPCB: 7628 prepreg 4.4, 3313 prepreg 4.1, 2116 prepreg 4.16, soldermask 3.8.

Stackups for 2 oz outer copper were not extracted: UNVERIFIED.

---

## 10. Bosch BMP388 (C779278) LGA-10 2.0 x 2.0 x 0.75

Source: Bosch datasheet BST-BMP388-DS001-07, Figure 23 (pin-out) and Figure 26 (outline). Section 7.2: "Bosch Sensortec suggests the BMP388 outline dimensions (bottom view) as landing pattern", i.e. lands equal to the package pads.

Package pads (Figure 26, bottom view dimensions): column spacing 1.525 (side pads at x = +/-0.7625), side pads at 0.5 pitch (1.000 between outer pads), top/bottom pads 0.500 apart, all pads 0.100 +/-0.05 in from the package edge. Pad sizes: 6x side pads 0.275 x 0.250, 4x top/bottom pads 0.250 x 0.275 (the 0.275 dimension is perpendicular to the package edge).

BMP388 in the datasheet TOP VIEW orientation (pin-1 indicator and pin 1 at the top, right of centre; vent hole 0.6 from the top edge and 0.6 from the right edge):

| Pin | Name | x | y (down) | Pad size (x by y) |
|---|---|---|---|---|
| 1 | VDDIO | +0.25 | -0.7625 | 0.25 x 0.275 |
| 2 | SCK | -0.25 | -0.7625 | 0.25 x 0.275 |
| 3 | VSS | -0.7625 | -0.5 | 0.275 x 0.25 |
| 4 | SDI | -0.7625 | 0 | 0.275 x 0.25 |
| 5 | SDO | -0.7625 | +0.5 | 0.275 x 0.25 |
| 6 | CSB | -0.25 | +0.7625 | 0.25 x 0.275 |
| 7 | INT | +0.25 | +0.7625 | 0.25 x 0.275 |
| 8 | VSS | +0.7625 | +0.5 | 0.275 x 0.25 |
| 9 | VSS | +0.7625 | 0 | 0.275 x 0.25 |
| 10 | VDD | +0.7625 | -0.5 | 0.275 x 0.25 |

Numbering runs counter-clockwise in top view. Vent hole at (+0.4, -0.4) in this orientation.

KiCad `Package_LGA:ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y`:

| Pad | x | y | Size |
|---|---|---|---|
| 1 | -0.7625 | -0.25 | 0.425 x 0.35 |
| 2 | -0.7625 | +0.25 | 0.425 x 0.35 |
| 3 | -0.5 | +0.7625 | 0.35 x 0.425 |
| 4 | 0 | +0.7625 | 0.35 x 0.425 |
| 5 | +0.5 | +0.7625 | 0.35 x 0.425 |
| 6 | +0.7625 | +0.25 | 0.425 x 0.35 |
| 7 | +0.7625 | -0.25 | 0.425 x 0.35 |
| 8 | +0.5 | -0.7625 | 0.35 x 0.425 |
| 9 | 0 | -0.7625 | 0.35 x 0.425 |
| 10 | -0.5 | -0.7625 | 0.35 x 0.425 |

**Result: pad centres AND pin numbering match exactly.** The ST footprint is the BMP388 datasheet top view rotated 90 degrees counter-clockwise (transform (x, y) to (y, -x) maps all ten BMP388 pin centres onto the same-numbered KiCad pads). In the KiCad footprint's nominal orientation the BMP388 two-pad side with pins 1-2 is on the left, pin 1 at upper-left, and the vent hole is at about (-0.4, -0.4).

Difference: pad size. KiCad pads are 0.425 x 0.35 versus Bosch's suggested 0.275 x 0.25 (0.15 longer, 0.10 wider). Adjacent-pad gap in the KiCad footprint is 0.15 mm along a row and 0.125 mm at the corners (pad 1 to pad 10 etc.), which is at or below JLCPCB's 0.15 mm SMD pad-to-pad figure and leaves no room for a 0.10 mm mask dam. For a custom footprint to Bosch's recommendation, use the same ten centres as the KiCad table with pads 0.275 (radial) x 0.25 (tangential); corner gap then becomes 0.25 mm.

---

## 11. TDK ICM-42688-P LGA-14 2.5 x 3.0 x 0.91

Source: TDK DS-000347 rev 1.2, Figure 4 (pin-out, top view) and section 10.2 (package dimensions).

- Top view: pin 1 at the top-left corner (A1 index dot). **Pins 1-4 down the left side (4 pads), 5-7 along the bottom left to right (3 pads), 8-11 up the right side (4 pads), 12-14 along the top right to left (3 pads).** Counter-clockwise.
- In this orientation the package is 3.0 wide (E, x) by 2.5 tall (D, y): the 4-pad sides are the 2.5 mm edges, the 3-pad sides are the 3.0 mm edges.
- Dimensions: lead width W 0.25 (0.2-0.3), lead length L 0.475 (0.425-0.525), pitch 0.5, lead centres at **x = +/-1.1625** (left/right columns, y = +/-0.25, +/-0.75) and **y = +/-0.9125** (top/bottom rows, x = 0, +/-0.5). Leads inset about 0.10 from the package edge.
- Pin names: 1 AP_SDO/AP_AD0, 2 RESV, 3 RESV, 4 INT1, 5 VDDIO, 6 GND, 7 RESV (connect to GND), 8 VDD, 9 INT2/FSYNC/CLKIN, 10 RESV, 11 RESV, 12 AP_CS, 13 AP_SCL/AP_SCLK, 14 AP_SDA/AP_SDIO/AP_SDI. (2, 3, 10, 11: NC or GND.)
- **The datasheet contains no recommended PCB land pattern, only package dimensions: TDK "recommended land pattern" is UNVERIFIED.** The comparison below is against the package lead geometry.

| Footprint | Side pads (1-4, 8-11) | Top/bottom pads (5-7, 12-14) | Pad size |
|---|---|---|---|
| `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` | x = +/-1.1625 | y = +/-0.9125 | 0.625 x 0.35 |
| `Bosch_LGA-14_3x2.5mm_P0.5mm` | x = +/-1.2625 | y = +/-1.0125 | 0.675 x 0.25 |

Both have identical numbering to the ICM-42688-P: pad 1 top-left, 1-4 down the left, 5-7 bottom left to right, 8-11 up the right, 12-14 top right to left; 4 pads on left/right, 3 pads on top/bottom.

- **`LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` matches the TDK lead centres exactly** (1.1625 / 0.9125); pads are 0.15 longer and 0.10 wider than the nominal lead (0.075 beyond each lead end, covering 0.85 to 1.475 from centre versus lead 0.925 to 1.40). Best geometric match.
- `Bosch_LGA-14` has pad width equal to the lead width (0.25) and pads shifted 0.1 outward (cover 0.925 to 1.60: flush with the lead's inner end, 0.2 toe beyond the lead, 0.1 past the package edge). Also usable, with wider pad-to-pad gaps (0.25 vs 0.15).
