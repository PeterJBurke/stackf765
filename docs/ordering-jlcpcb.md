# Ordering StackF765 from JLCPCB, step by step

Checked against JLCPCB's public pages and the files in `fab/` on 2026-11-19.
This guide is for someone who has never ordered from JLCPCB. Follow it top to bottom.
You place **three separate orders in one cart**: upper, lower, service.

Labels on JLCPCB's order form change now and then. If a label below is worded
slightly differently on the site, pick the option with the same meaning.
Option names marked *(from memory)* were not re-read on the live form, which needs a browser.

Prices and stock move daily. Every number here is a snapshot.

## 0. Before you start

Read this list first. Each item can cost you a board run.

| # | Thing to know | What to do |
|---|---|---|
| 1 | **Part rotations.** The placement files now carry JLCPCB's rotations (the generator applies the corrections in section 6), but the corrections were worked out from JLCPCB's library drawings, not from a built board. | Check every row of the rotation tables in section 6 in the preview. Tick "Confirm Parts Placement". |
| 2 | **STM32F765VIT6 (C710319): 48 in JLCPCB stock.** | Check stock first. If it is short, stop and see section 8. |
| 3 | **TPS62933DRLR (C3200405): 36 in JLCPCB stock.** You need 2 per lower board. | Check stock. Section 8 has a same-footprint substitute. |
| 4 | **ICM-45686 (C22459454): 186 in stock.** | Check stock. |
| 5 | The upper board must use **Standard PCBA** (parts on both sides; BMP388 is "Standard Only"). | Follow section 3. |
| 6 | The lower board must use **Standard PCBA** if JLCPCB fits the standoffs (SMTSO2080CTJ is "Standard Only"). | Follow section 4. |
| 7 | **HASL is not offered on 6-layer boards. ENIG is no longer free.** | Upper: choose ENIG and accept the fee. |
| 8 | None of the boards has fiducials, rails or tooling holes. All are smaller than 70 × 70 mm. | Let JLCPCB add them (options below). Expect small break-off nubs on two edges; file them flat. |
| 9 | Four parts are **not** in the JLCPCB files: both pin headers and both Samtec connectors. | Buy them (section 7) and solder them yourself. |

Minimum quantities: 5 bare boards per design; 2 assembled. Order 5 and assemble all 5.

## Notes from preparing a real cart (2026-11-19)

- **BMP388 (upper U3) is left unticked** in the parts list because JLCPCB marks it "difficult to process". Tick its
  "Select" box, or it will not be fitted.
- **Buzzer rotation** was wrong by a quarter turn in the first placement file and is corrected (270).
  All other polarised parts on all three boards matched the preview.
- Choosing stack-up JLC06161H-3313 brings up a notice that the finished thickness is 1.54 mm, not 1.6 mm. Accept it.
- On 4- and 6-layer boards "Tented" is not offered; the defaults ("Plugged" for 4 layers, "Epoxy Filled & Capped"
  for 6) are fine and free.
- The lower board can only be ordered as Standard PCBA (Economic is greyed out with 2 oz copper).
- The quote step asks for a customs "Product Description" before it will save to the cart.
- Quotes for 5 assembled of each, before shipping: service $36.74, lower $143.17, upper $397.36.

## 1. Files you upload

| Board | Gerber zip | BOM | Placement (CPL) |
|---|---|---|---|
| upper | `fab/upper/upper-gerbers.zip` | `fab/upper/upper-bom-jlc.csv` | `fab/upper/upper-cpl-jlc.csv` |
| lower | `fab/lower/lower-gerbers.zip` | `fab/lower/lower-bom-jlc.csv` | `fab/lower/lower-cpl-jlc.csv` |
| service | `fab/service/service-gerbers.zip` | `fab/service/service-bom-jlc.csv` | `fab/service/service-cpl-jlc.csv` |

Do not upload `*-bom.csv`, `*-pos.csv` or `*.d356`. They are for reference.

## 2. Start an order (same for each board)

1. Go to jlcpcb.com, sign in, click **Order now** / **Instant quote**.
2. Click **Add gerber file** and upload the board's `-gerbers.zip`.
3. Wait for the preview. Check that the detected **layer count** and **size** match the table for that board. If they do not, stop.
4. Set the PCB options from the board's table below.
5. Turn on **PCB Assembly** and set the assembly options.
6. Click **Next**. Look at the board picture, click **Next**.
7. Upload the BOM and CPL files. Click **Process BOM & CPL**.
8. On the parts list: every line must show a matched part and enough stock. Nothing should say "shortfall" or "not selected".
9. On the placement preview: check rotations (section 6).
10. **Save to cart.** Repeat for the next board. Pay once at the end (section 9).

## 3. Upper board (6 layers, parts on both sides)

### PCB options

| Option | Choose | Why |
|---|---|---|
| Base material | FR-4 | |
| Layers | **6** | |
| Dimensions | **31.5 × 48 mm** (auto-detected) | |
| PCB Qty | 5 (or 10) | |
| Different design | 1 | |
| Delivery format | Single PCB | JLCPCB adds assembly rails itself, see below |
| PCB thickness | **1.6 mm** | |
| PCB colour | Green | Finest solder-mask detail; needed between the 0.5 mm-pitch pads |
| Silkscreen | White | |
| Surface finish | **ENIG** (1 U" is enough) | Flat pads for the LGA sensors. HASL is not offered on 6 layers. ENIG costs extra. |
| Outer copper weight | **1 oz** | |
| Inner copper weight | **0.5 oz** | |
| Impedance control / specify stack-up | **Yes → JLC06161H-3313** | The intended stack-up |
| Via covering | **Epoxy filled & capped** (the 6-layer default, no charge) or Tented | The files have all vias covered by mask either way |
| Min via hole / diameter | 0.3 mm / 0.45 mm or larger *(from memory)* | The board uses 0.3 mm holes with 0.5 mm pads. No small-via fee. |
| Board outline tolerance | ±0.2 mm (regular) | |
| Mark on PCB | **Remove mark** *(from memory)* | The boards have no reserved spot for an order number. Do not pick "Specify position": the files contain no position marker. |
| Confirm production file | Yes (optional, small delay) | Lets you see what they will make |
| Electrical test | Flying probe, full test | |
| Gold fingers / castellated holes / edge plating | No | |

### Assembly options

| Option | Choose |
|---|---|
| PCBA type | **Standard** |
| Assembly side | **Both sides** |
| PCBA Qty | 5 (all of them) |
| Edge rails / fiducials | **Added by JLCPCB** |
| Confirm parts placement | **Yes** |
| Tooling holes | Added by JLCPCB |
| Bake components / conformal coating / cleaning | No. Add a remark: "U2 and U3 are MEMS sensors. No ultrasonic cleaning. No-clean flux only." |

### After upload

- 31 BOM lines, 70 parts: 36 top, 34 bottom.
- JLCPCB will apply X-ray inspection for the LGA parts. That is normal.
- Not fitted by JLCPCB: `J1` (3 × 12 right-angle header, top) and `J3` (Samtec FTSH, bottom). The stencil still puts paste on J3's pads; you get small solder bumps there. That is fine.

## 4. Lower board (4 layers, 2 oz copper)

### PCB options

| Option | Choose | Why |
|---|---|---|
| Layers | **4** | |
| Dimensions | **31.5 × 48 mm** | |
| PCB Qty | 5 (or 10) | |
| Delivery format | Single PCB | |
| PCB thickness | **1.6 mm** | |
| PCB colour | Green | |
| Surface finish | **ENIG** recommended; lead-free HASL acceptable | Two 0.5 mm-pitch regulators on thick copper solder better on flat pads |
| Outer copper weight | **2 oz** | Carries battery current. This is the main cost of this board. |
| Inner copper weight | **0.5 oz** (1 oz also fine) | |
| Impedance control / specify stack-up | **JLC04161H-7628** if the form offers it with 2 oz; otherwise "No" (default stack-up) | Nothing on this board needs controlled impedance |
| Via covering | **Tented** | |
| Mark on PCB | Remove mark *(from memory)* | |
| Electrical test | Flying probe, full test | |
| Everything else | As for the upper board | |

If the form shows a warning about **holes in pads** on the four big battery pads: that is intended. They are open 0.4 mm plated holes in hand-soldered wire pads. Do **not** add epoxy filling for them.

### Assembly options

| Option | Choose |
|---|---|
| PCBA type | **Standard** (the standoffs H1–H3 are "Standard Only" parts) |
| Assembly side | **Top side** |
| PCBA Qty | 5 |
| Edge rails / fiducials | Added by JLCPCB |
| Confirm parts placement | Yes |

Cheaper route: choose **Economic**, and on the parts list mark H1–H3 "Do not place". Then solder the standoffs yourself with hot air or a hot plate, or use loose M2 × 8 mm standoffs. Whether Economic accepts 2 oz copper could not be confirmed; the form will tell you.

### After upload

- 17 BOM lines, 41 parts, all on top.
- Not fitted by JLCPCB: `J1` (Samtec SFMC socket), `J2` (3 × 9 right-angle header), and the four wire pads.

## 5. Service board (2 layers)

### PCB options

| Option | Choose |
|---|---|
| Layers | **2** |
| Dimensions | **18 × 32 mm** |
| PCB Qty | 5 (or 10) |
| Delivery format | Single PCB |
| PCB thickness | 1.6 mm |
| Surface finish | Lead-free HASL (cheapest) or ENIG |
| Outer copper weight | 1 oz |
| Via covering | Tented |
| Mark on PCB | Remove mark *(from memory)* |

A small "deburring" surcharge of a few cents per board applies because one side is under 30 mm.

### Assembly options

| Option | Choose |
|---|---|
| PCBA type | **Economic** |
| Assembly side | Top side |
| PCBA Qty | 5 |
| Tooling holes | **Added by JLCPCB** |
| Confirm parts placement | Yes |

### After upload

- 9 BOM lines, 10 parts. Nothing to hand-solder.
- The USB-C socket sits flush with the board edge. If JLCPCB asks about a part at the edge, answer that it is intended.

## 6. Placement preview: what must be checked

JLCPCB draws each part on the board. A red dot or a "1" marks pin 1.
Compare with `docs/boards/<board>/<board>-assembly-top.svg` (and `-bottom.svg`).
Pin 1 in the preview must sit on pin 1 of the drawing.

To fix a part: click it in the preview and use the rotate arrows, or edit the "Rotation" number.

The column "CPL now" is the raw KiCad angle. "JLCPCB needs" is what makes the preview correct, and it is the
value the placement files in `fab/` now contain (since 2026-11-19). The check in the preview is still required.

How the "needs" column was worked out: the pad layout of JLCPCB's own library footprint for that exact part number
(read from EasyEDA) was compared pad by pad with the KiCad footprint. For bottom-side parts JLCPCB's angle is
`180 − KiCad angle`, then the offset is added. "High" means a second source (the community rotation list) agrees.

### Upper board

| Ref | Part | Package | Side | CPL now | JLCPCB needs | Confidence |
|---|---|---|---|---|---|---|
| U1 | STM32F765VIT6 | LQFP-100 | Top | 180 | **90** | High |
| U4 | AT7456E | HTSSOP-28 | Top | 0 | **270** | High |
| U3 | BMP388 | LGA-10 | Top | 0 | **90** | Medium |
| U6 | TLV75533 | SOT-23-5 | Top | 0 | **180** | Medium (the community list says 270; a 90° error is obvious in the preview) |
| U7 | TPS7A2033 | SOT-23-5 | Top | 0 | **180** | Medium (same remark) |
| J4 | microSD socket | Molex 104031 | Top | 180 | **0** | Medium. Card slot must open toward the nearest board edge. |
| U5 | LM66200 | SOT-583 | Bottom | 0 | **90** | Medium |
| Q1 | 2N7002 | SOT-23 | Bottom | 0 | 0 | Medium. The three pads only fit one way; check they line up. |
| Q2 | AO3401A | SOT-23 | Bottom | 0 | 0 | Medium, same remark |
| U2 | ICM-45686 | LGA-14 | Top | 0 | 0 | Medium |
| Y1 | 8 MHz crystal | 3225 | Top | 0 | 0 | High (180° is equivalent) |
| Y2 | 27 MHz crystal | 3225 | Bottom | 90 | 90 | High (180° is equivalent) |
| D1, D2 | LEDs | 0603 | Top | 90 | 90 | Medium. Cathode mark toward the board's cathode mark. |
| J5 | JST-SH 6-pin | SM06B-SRSS | Top | 90 | 90 | Medium. Opening must face the right-hand board edge. |
| D3 | SMF5.0CA | SOD-123F | Bottom | 0 | any | Two-way part, no polarity |
| Other bottom-side C and R at 0 | | 0402–1206 | Bottom | 0 | 180 | No effect: two-pin parts without polarity |

### Lower board

| Ref | Part | Package | CPL now | JLCPCB needs | Confidence |
|---|---|---|---|---|---|
| U1, U2 | TPS62933DRLR | SOT-583 | 0 | **180** | Medium. A 180° error is easy to miss here: check the pin-1 dot. |
| U3 | INA214 | SC-70-6 | 180 | **0** | High. Check the pin-1 dot. |
| D2 | Green LED | 0603 | 90 | 90 | Medium |
| D1 | SMBJ15CA | SMB | 0 | any | Two-way part, no polarity |
| L1, L2, R1 | Inductors, shunt | | 0 | 0 | No polarity |
| H1–H3 | Standoffs | round | 0 | any | Round part. Check it is centred on the hole. |

### Service board

| Ref | Part | Package | CPL now | JLCPCB needs | Confidence |
|---|---|---|---|---|---|
| U1 | USBLC6-2SC6 | SOT-23-6 | 0 | **270** | High. A 90° error is obvious. |
| J1 | USB-C socket | HRO TYPE-C-31-M-12 | 180 | 180 | Medium (the community list says 0). The opening must face the board edge. The part may also show about **1.6 mm** off its pads, because the two footprints use different centre points. Drag it onto the pads, or leave it: JLCPCB's engineers align connectors to the pads. |
| D1 | 1N5819WS | SOD-323 | 90 | 90 | Medium. Cathode bar matches the silkscreen bar. |
| BZ1 | Buzzer | 8.5 × 8.5 mm | 0 | 270 | Corrected from JLCPCB's preview on 2026-11-19. "+" of the part on the pad marked "+" (top-left with USB at the top). |
| SW1 | Tact switch | 5.1 × 5.1 mm | 90 | 90 | High (180° is equivalent) |
| J2 | JST-SH 6-pin | SM06B-SRSS | 0 | 0 | Medium. Opening faces the board edge. |

If any polarised part is still doubtful, write it in the order remark:
"Please check polarity of U1, U3 … against the silkscreen pin-1 marks." JLCPCB's engineers follow the silkscreen when the file and the silkscreen disagree.

## 7. What you buy elsewhere and solder yourself

Quantities are per set of three boards.

| Item | Qty | Where | Note |
|---|---|---|---|
| Samtec **SFMC-110-02-L-D** socket | 1 | DigiKey, Mouser, Samtec | Lower board `J1`, top side |
| Samtec **FTSH-110-04-L-DV** header | 1 | DigiKey, Mouser, Samtec | Upper board `J3`, bottom side. Lead style **-04** only. No "-K". |
| 3 × 3 right-angle pin header, 2.54 mm (HCTL PZ254-3-03-W-2.5-G0, LCSC C7429379) | 7 | LCSC | Four for upper `J1` (3 × 12), three for lower `J2` (3 × 9). Or one Samtec TSW-112-08-G-T-RA for the upper. |
| M2 × 4 mm screws | 3 | any | Upper board into the standoffs. Not longer. |
| Silicone grommets for a 4 mm hole with M2 insert ("M3 to M2") | 4 | drone shops | Lower board to frame |
| M2 screws and nuts for the frame | 4 | any | |
| JST-SH 6-pin cable, 100 mm, **wired 1:1** | 1 | any | Check pin 1 to pin 1 with a meter. A reversed cable does no damage; USB just will not connect. |
| M2 × 8 mm standoffs | 3 | only if you chose "Do not place" for H1–H3 | |

Soldering order and tips are in [assembly.md](assembly.md).
Do the electrical checks in [bringup.md](bringup.md) before stacking the boards.

## 8. If a part is out of stock

| Part | First choice | Then |
|---|---|---|
| STM32F765VIT6 (C710319) | STM32F767VIT6 (C91934). Same footprint, same firmware. It had 21 in stock and cost more. | Pre-order through JLCPCB's parts manager, or wait |
| TPS62933DRLR (C3200405) | Pre-order the original if you can. TPS62933FDRLR (C5219272, about 2,800 in stock) has the same footprint and pins but runs in forced-PWM mode: more idle current, and it can push current back into the battery rail if something else (an ESC's BEC) also feeds the 5 V pins. | Pre-order the original |
| ICM-45686 (C22459454) | Wait or pre-order. ICM-42688-P fits the same pads but JLCPCB had only 3. | |
| 27 MHz crystal Y2 (C5210645) | Pre-order | |

On the parts list you change a part with the magnifier / "Change" button on that line, then type the new C-number.

## 9. Final check before you pay

- [ ] Three items in the cart: 6-layer 31.5 × 48, 4-layer 31.5 × 48, 2-layer 18 × 32.
- [ ] Upper: 6 layers, 1.6 mm, ENIG, 1 oz / 0.5 oz, JLC06161H-3313, Standard PCBA, both sides.
- [ ] Lower: 4 layers, 1.6 mm, **2 oz** outer, Standard PCBA, top side.
- [ ] Service: 2 layers, Economic PCBA, top side.
- [ ] Each board: PCB quantity and PCBA quantity are what you want.
- [ ] Each board: every BOM line matched, no shortfall. STM32, TPS62933, ICM-45686 confirmed in stock.
- [ ] Each board: number of placed parts is 70 / 41 / 10.
- [ ] Each board: every row of section 6 checked in the preview.
- [ ] "Confirm parts placement" is on for all three.
- [ ] Remark about the MEMS sensors is on the upper board.
- [ ] Hand-solder parts from section 7 are ordered separately.
- [ ] The total is near the estimate below. A much higher total usually means a wrong option (for example an unintended via-filling or panel option).

## 10. Cost estimate

**This is an estimate, not a quote.** Assembly fees are from JLCPCB's published fee article (2026-10-22). Part prices are JLCPCB's listed prices on 2026-11-19. **Bare-board prices could not be read** from the live calculator; the ranges are rough figures from memory and are the weakest numbers here. Shipping, duties and tax are not included except where stated.

| | 5 sets | 10 sets |
|---|---|---|
| Upper: bare boards (6-layer, ENIG) | 10–40 | 15–50 |
| Upper: assembly fees (Standard, two sides) | about 143 | about 154 |
| Upper: parts | about 214 | about 389 |
| Lower: bare boards (4-layer, 2 oz) | 35–60 | 40–70 |
| Lower: assembly fees (Standard, one side) | about 62 | about 63 |
| Lower: parts | about 18 | about 34 |
| Service: bare boards | 2–5 | 2–5 |
| Service: assembly fees (Economic) | about 26 | about 26 |
| Service: parts | about 9 | about 16 |
| Shipping (courier) | 20–40 | 25–45 |
| **Total at JLCPCB** | **about 540–620 USD** | **about 770–850 USD** |
| Per set | about 110–125 | about 77–85 |
| Hand-solder parts bought elsewhere (Samtec pair, headers, hardware, cable) | about 15 per set | about 15 per set |

What the assembly fees contain:

- Upper: setup 51.12, stencil 16.42, feeder loading 31 lines × 1.53, X-ray 1.64 per board, fixtures 16.42, solder joints 321 per board × 0.0016, placement check 0.45.
- Lower: setup 25.56, stencil 8.21, feeder loading 17 × 1.53, joints, placement check.
- Service: setup 8.18, stencil 1.53, 5 extended parts × 3.07, joints, placement check.

Not included because they could not be confirmed: a possible Standard-PCBA handling fee (about 15 per order), rail removal, and minimum-quantity or wastage charges on very cheap parts (usually under 5 in total).
