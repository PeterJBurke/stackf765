# Header clearance: upper J1 solder tails vs lower J2 pins

Independent check, 2026-11-19. Read-only on the design files. Dimensions in mm.
z is measured up from the top surface of the lower board; x runs along the front edge; y runs towards the front edge (board edge at y = +24.0).

## Verdict

- The render is faithful. It shows the untrimmed generic header, where the tail tips sit at the same height as the tops of the lower header's top-row pins (0.01 mm overlap) and 0.63 mm to the side of them.
- The half-pitch (1.27 mm) sideways offset is real in the routed boards. It is the only thing that separates the metal if the tails are not trimmed.
- An untrimmed build does not short at nominal dimensions, but it is not guaranteed safe: the worst-case sideways gap is about 0.1 mm before solder, and solder on the tails can close it.
- "Trim to 1.0 mm" gives 0.39 mm vertical clearance at nominal only. With tolerances it goes to about 0 or negative. Flush-cutting (0.5 mm or less) is what gives a real vertical margin.
- No board change is needed. The boards can be ordered. The assembly instruction and `tools/check_stack.py` should be tightened (see Recommendation).

## Measured from the files

Both `.kicad_pcb` files use the same frame (board centre at 100, 100), read with pcbnew:

| Item | Lower | Upper |
|---|---|---|
| Edge.Cuts bounding box | 31.6 x 48.1 (incl. 0.1 line) | same |
| Board thickness setting | 1.6 | 1.6 |
| Board-to-board connector | J1 at (0, 0), top | J3 at (0, 0), bottom |
| Standoffs / screw holes | H1 (-12.3, 3.0), H2 (12.3, 3.0), H3 (12.3, -15.9), hole 3.75 | NPTH 2.2 at the same three points |
| Header | J2, 3 x 9, top side | J1, 3 x 12, top side |
| Hole rows (y) | A 17.72, B 20.26, C 22.80 | A 17.72, B 20.26, C 22.80 |
| Hole columns (x) | -10.16 ... +10.16, step 2.54 | -13.97 ... +13.97, step 2.54 |
| Hole / pad | 1.02 drill, 1.6 pad | same |

So the two headers have identical row positions and the columns are offset by exactly 1.27. Row C is 1.20 from the board edge on both boards. Row A (furthest from the edge) carries the tallest pins.

Upper columns 1 and 12 (x = +/-13.97) have no lower pin near them. Columns 2 and 11 have one lower neighbour. Columns 3 to 10 sit between two lower pins.

The 3D model (`gen/make_models.py`, checked against the STEP point coordinates) has pin centre heights 1.21 / 3.75 / 6.29, pin top of row A at 6.61, body 7.50 high, tails ending 3.00 below the board top (1.40 below a 1.6 board). The web viewer (`docs/drone/assets/stackf765.js`) places the upper board 9.6 above the lower (8.0 standoff + 1.6 board). Tail tips in the render are therefore at z = 6.60 and lower pin tops at z = 6.61.

## Header geometry from the manufacturers' drawings

Downloaded to `/tmp/claude-0/-root-fcclaude/3115490e-4cef-411f-8226-519a0fbe1e45/scratchpad/headers/dl/`; page images one level up.

| | HCTL PZ254-3-N-W-2.5 (generic 3 x 3, LCSC C7429379) | Samtec TSW-1xx-08-x-T-RA |
|---|---|---|
| Source | drawing "PZ254-3-N-W-2.5-XX (L15.54)" rev A | print TSW-XXX-XX-XXX-X-XX-XXX rev DS, sheet 4, Fig 5 and Table 5 |
| Post | 0.64 square | 0.64 square |
| Body height | 7.50 +/-0.15 | 8.13 REF |
| Row pitch | 2.54 +/-0.1, 5.08 +/-0.1 | 2.54, 5.08 |
| Row centre heights above the body's board-side face | 1.21 / 3.75 / 6.29 (derived, body symmetric about the rows; confirmed by scaling the drawing) | 1.78 / 4.32 / 6.86 (derived: 8.13 - 1.27 - 5.08; scaling the drawing gives 1.85 for the first row) |
| Top of row-A pin | 6.61 | 7.18 |
| Tail length from the body's board-side face | PC = 3.00 +/-0.25 | E = 2.29 (lead style -08, RA triple) |
| Tail through a 1.6 board | 1.40 (1.0 to 1.8 with part and board tolerance) | 0.69 |
| Lowest hole row to body rear face | 1.96 (derived from PB 9.54) | 1.52 |
| Body beyond the board edge | 0.76 | 0.32 |
| Other tolerances | angle +/-3 degrees | tow and sway 2 degrees |

The Samtec row heights are derived, not stated on the print. The 1.0 dimension on the print is the position of the locking-lead crimp, not a standoff height.

Both bodies sit entirely beyond the board edge. Nothing on the board sets the header's height while soldering; the heights above assume the builder holds the body's lower face level with the board top. The header can sit up to about 0.9 lower (row-C pin resting on the board) or higher by any amount up to the tail length.

## Clearances

Only the lower header's row-A pins matter. They rise at y = 17.72 and run forward at z = 5.97 to 6.61 under all three rows of upper tails. Rows B and C are 2.5 and 5.1 lower. The lower header's plastic body starts at y = 24.76 (HCTL), 1.6 in front of the nearest tail and outside the upper board outline.

Nominal (gap 8.00, boards 1.60, bodies level with the board top):

| Lower header | Upper header | Tail | Vertical | Sideways | True 3D |
|---|---|---|---|---|---|
| HCTL | HCTL | as supplied, 1.40 | -0.01 (level) | 0.63 | 0.63 |
| HCTL | HCTL | trimmed to 1.0 | +0.39 | 0.63 | 0.74 |
| HCTL | HCTL | flush-cut, 0.5 | +0.89 | 0.63 | 1.09 |
| HCTL | Samtec | as supplied, 0.69 | +0.70 | 0.63 | 0.94 |
| Samtec | HCTL | as supplied, 1.40 | -0.58 | 0.63 | 0.63 |
| Samtec | HCTL | trimmed to 1.0 | -0.18 | 0.63 | 0.63 |
| Samtec | Samtec | as supplied, 0.69 | +0.13 | 0.63 | 0.64 |

A Samtec header on the lower board has a second problem: its body top (8.13) is higher than the underside of the upper board (8.00) and stands only 0.32 in front of the upper board's edge, so it can rub on that edge. Plastic against board, not electrical.

A negative vertical figure means the tail tips reach below the pin tops, so the tails sit between the pins and only the sideways gap separates them.

The project's figures (6.61, 1.4, about 0, 0.4 trimmed, 0.6 either side) are correct for the generic header on both boards at nominal dimensions.

Worst case, vertical. Assumed: standoff 8.00 - 0.13; lower pin top +0.20 (part) and +0.30 (header soldered high); upper board 1.44 thick; tail +0.25 (part) and +0.30 (header soldered low):

| Lower | Tail | Vertical, worst case |
|---|---|---|
| HCTL | HCTL as supplied (2.11) | -1.35 |
| HCTL | Samtec as supplied (1.28) | -0.52 |
| HCTL | trimmed to 1.0 | -0.24 (+0.06 if both headers are seated correctly) |
| HCTL | flush-cut to 0.5 | +0.26 |
| Samtec | trimmed to 1.0 | -0.81 |
| Samtec | flush-cut to 0.5 | -0.31 |

Worst case, sideways. Nominal 0.63 edge to edge. Assumed contributions: board-to-board registration through the 1.27 mm connector 0.15; tail position in its 1.02 hole 0.15; lower pin position 0.15; hole positions 0.10.

- Arithmetic sum: 0.08 remaining.
- Root-sum-square: 0.35 remaining.
- Solder on the tail takes a further 0.05 to 0.25 where the tail overlaps the pin height. The fillet is widest at the board (pad radius 0.8) and narrows to the pin at the tip.

So an untrimmed build has about 0.6 nominal, 0.1 to 0.3 realistic worst case, and can touch if a tail carries a solder blob or a pin is bent.

## What would short

Lower row A carries M1 to M6, LED_STRIP and +5V_PI (two pins). Upper tails next to them, from the PCB nets:

| Upper tail (x) | Net | Lower neighbours | Consequence of contact |
|---|---|---|---|
| A10 (8.89) | GND | +5V_PI both sides | dead short of the 3 A companion supply |
| B9, C9 (6.35) | GND | LED_STRIP, +5V_PI | short of +5V_PI, or LED signal grounded |
| B10, C10 (8.89), A11 (11.43) | +5V | +5V_PI | two 5 V regulators tied together |
| A2, B2 (-11.43) | +5V_SYS | M1 | 5 V on a motor signal |
| C2 (-11.43), B6, C6 (-1.27), A8 (3.81) | +5V | M1, M4/M5, M6/LED_STRIP | 5 V on a motor or LED signal pin |
| B5, C5 (-3.81), A7 (1.27) | GND | M3/M4, M5/M6 | motor signal grounded |
| A9 (6.35) | CAM_IN | LED_STRIP, +5V_PI | 5 V into the video input |
| UART / I2C tails, columns 3 to 8 and 11 | TX/RX/SDA/SCL | motor signals, LED_STRIP, +5V_PI | signal-to-signal contention; 5 V on TX4/TX8 at column 11 |

## Is the render accurate

Yes. The model uses the HCTL drawing's dimensions and the viewer uses the true 8.0 gap. The tails in the render are the untrimmed 1.40 length, which is what the part looks like before the trim step. The only simplifications are square corners in place of bend radii and no solder. A build with the Samtec header on top would look better than the render (0.69 tails); a Samtec header on the lower board would be worse than the render (pins 0.57 higher).

## Figures

To scale, front and side views, script `xsec.py` in the same folder:

- `/tmp/claude-0/-root-fcclaude/3115490e-4cef-411f-8226-519a0fbe1e45/scratchpad/headers/xsec_hctl_hctl.png` (generic on both boards, as rendered)
- `/tmp/claude-0/-root-fcclaude/3115490e-4cef-411f-8226-519a0fbe1e45/scratchpad/headers/xsec_hctl_lower_samtec_upper.png`
- `/tmp/claude-0/-root-fcclaude/3115490e-4cef-411f-8226-519a0fbe1e45/scratchpad/headers/xsec_samtec_samtec.png`

The scratch folder is temporary; copy the figures if they are to be kept.

## Recommendation

Acceptable without a board change, provided the assembly rule is tightened. The order does not need to wait.

Ranked options:

| Rank | Option | Re-spin | Effect |
|---|---|---|---|
| 1 | Flush-cut the upper tails (0.5 or less) instead of "1.0 or less", and make it a checked step | no | nominal vertical 0.89, worst case +0.26 with the generic lower header |
| 2 | Seat the lower header as low as it goes (or at least body level with the board top, never high); keep the lower header generic (7.5 body), not Samtec | no | removes the largest worst-case term; Samtec on the lower board costs 0.57 |
| 3 | Polyimide tape strip over the lower row-A pin tops, or over the cut tails | no | insulation if anything is missed; 0.06 thick fits |
| 4 | Samtec TSW-112-08 on the upper board | no | 0.69 tails as supplied; +0.70 nominal without trimming, still cut flush |
| 5 | Continuity check before first power: +5V_PI to GND, +5V to each of M1 to M6 and LED_STRIP, with the stack assembled | no | catches a contact |
| 6 | 8.5 standoffs with FTSH lead style -05 (B max 8.89) | no (parts change) | +0.5 gap; the present -04 pair allows only 8.38, and an 8.0 standoff at +0.13 already uses 8.13, so taller standoffs alone gain at most 0.25 |
| 7 | Two-row lower header | lower board | pin top drops to 4.07, but loses one pin per column |
| 8 | Move the upper header inboard past the lower row A | upper board | needs 6.4 of board depth and a re-route |
| 9 | Larger sideways offset | - | not possible; 1.27 is already the maximum on a 2.54 grid |
| 10 | Surface-mount right-angle 3-row header on the upper board | upper board | no such common part; weak against plug forces |

Follow-ups in the repository (not done here):

- `docs/assembly.md` and `docs/verification.md`: say "cut flush, 0.5 mm or less", state that 0.4 mm is a nominal figure, and that the lower header must be the 7.5 mm-body generic part seated level or low.
- `tools/check_stack.py` hard-codes a 1.0 trimmed tail and a 6.61 pin top; it cannot detect an untrimmed or Samtec-on-lower build. It also reports only the column offset, not a tolerance stack.

## Assumptions (not measured)

- Header seating error of +/-0.30, board registration, pin-in-hole and pin-position figures of 0.10 to 0.15, and solder growth of 0.05 to 0.25 are engineering estimates.
- Samtec row heights are derived from the 8.13 REF body and scaled from the print.
- Board thickness tolerance +/-10 %, standoff 8.00 +/-0.13 (from `research/mechanical.md`, Sinhoo drawing; not re-read).
- The 8.38 maximum mated height is taken from `research/samtec-b2b.md`, not re-read from the Samtec drawing.
