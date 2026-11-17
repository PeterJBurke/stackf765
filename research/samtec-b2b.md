# Samtec 1.27 mm board-to-board pair: SFMC-110-02-x-D + FTSH-110-04-x-DV

Researched 2026-11-17. Every number below was read from the named Samtec drawing unless it is
marked DERIVED (arithmetic on drawing numbers) or UNVERIFIED (could not be read from a drawing).
Dimensions are mm; Samtec's drawings are inch-primary with mm in brackets.

## Sources (downloaded to /root/fcclaude/build/samtec/dl/, page images in ../img/)

| Tag | File | Samtec document | Rev / date |
|---|---|---|---|
| S-FP | sfmc-d-sm_footprint.pdf | "Recommended P.C.B layout for SFMC-1XX-X2-XX-D-XX" (suddendocs.samtec.com/prints/sfmc-d-sm%20footprint.pdf) | Rev D, 2012-02-09 |
| S-PRT | sfmc-1xx-xx-xxx-d-xx-xx-mkt.pdf | SFMC-1XX-XX-XXX-D-XX-XX assembly print, 3 sheets | Rev CN, PDF 2025-11 |
| S-CAT | sfmc.pdf | SFMC catalog page F-226 | PDF 2025-10 |
| F-FP | ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf | "Recommended PCB layout for FTSH-1XX-XX-XXX-DV-XXX", 4 sheets | Rev H, 2019-08-27 |
| F-PRT | ftsh-1xx-xx-xxx-dv-xxx-xxx-mkt.pdf | FTSH-1XX-XX-XXX-DV-XXX-XXX print, 5 sheets | Rev FQ, PDF 2021-01 |
| F-CAT | ftsh_smt.pdf | FTSH SMT catalog page F-226 | current |
| MATED | ftsh_to_sfmc_mated.pdf | "FTSH to SFMC mated views" (suddendocs.samtec.com/prints/ftsh%20to%20sfmc%20mated%20document.pdf) | Rev A, 2021-04-19, ECN-408612 |
| SINHOO | lcsc_C2916357_sinhoo.pdf | Sinhoo SMTSO2080CTJ drawing | Rev A, 2018-03-02 |

The LCSC "datasheets" for C3323057 and C7279869 are just the one-page Samtec catalog pages (older 2023 issue), no extra data.

Not reachable: samtec.com product pages other than SFMC-110-02-L-D (Cloudflare 429/1015 after the first request), DigiKey (403 bot challenge), Mouser (challenge page). SnapEDA / Ultra Librarian not consulted (not needed: Samtec's own footprint drawings were obtained).

## 0. Is this a Samtec-supported mating pair?

Yes, but the catalog pages do not say so:

- S-CAT lists SFMC board mates as "TFM" only; F-CAT lists FTSH board mates as "CLP, FLE" and says lead style -04 "mates with CLP-DH".
- The samtec.com product page for SFMC-110-02-L-D lists mating connectors FW-SM, FW-TH, **FTSH**, FMTP, TFM, FTS, links the "SFMC/FTSH Mated Views" drawing (MATED), and lists test reports "SFMC/FTSH - Design Qualification Test", "SFMC/FTSH - Mixed Flowing Gas", "SFMC/FTSH - Mating/Unmating Report".
- MATED has an explicit row for FTSH-DV lead style -04 against SFMC-02-D.

## 1. SFMC-1xx-02-x-D socket (lower board, top side)

"-02" lead style = **Surface Mount** (S-CAT; S-PRT sheet 1: "-02: SURFACE MOUNT (use contact C-44-02-XXX), see Fig 2"). -01/-03 are through-hole; -L2/-T2 are other SMT variants using the same footprint drawing ("X2").

Land pattern (S-FP Fig 1, all symmetric about both centrelines):

| Item | Value | Status |
|---|---|---|
| Pitch | 1.27 | drawing |
| Pad width (along the row) | 0.74 | drawing |
| Pad length (across the row) | 2.22 | drawing |
| Gap between the two rows of pads (inner edges) | 0.51 | drawing |
| Outer span over both rows | 4.95 | drawing |
| Pad centre to connector centreline | 1.365 | DERIVED (0.51/2 + 2.22/2); check 2 x (0.255 + 2.22) = 4.95 |
| Row centre-to-centre | 2.73 | DERIVED |
| First-to-last pad centre, 10 positions | 11.43 ((N-1) x 1.27) | drawing formula |
| Connector outline on the pattern | (N x 1.27 + 0.38) x 3.05 = 13.08 x 3.05 | drawing formula |
| Holes / pegs | none shown | drawing |
| Stencil (sheet 2) | same apertures as pads, 0.15 thick | drawing |

Alignment / locating pegs: **none** for plain, -K or -P. Neither S-FP nor S-PRT shows any peg, and no -A option exists in the SFMC part-number breakdown. The footprint is identical for all three.

Body (S-PRT sheets 1-2):

- Length = N x 1.27 + 0.38, tolerance +/-0.20 -> **13.08** for 10 positions.
- Body width 3.05 REF; width over the SMT leads 4.19 REF.
- Height above board, finished (-02): **4.70 +0.05/-0.13** (critical dimension). The 4.83 figure on the print is an in-process dimension before re-press, not the finished part.
- Coplanarity 0.10 (2 to 26 positions).
- -K: polyimide film disc, 3.99 dia REF, 0.13 thick, stuck on top; overall height with film 4.83. 4 positions minimum.
- -P: plastic pad PPP-02, 10.01 x 5.72 REF, standing 1.57 above the body top; 5 positions minimum.

## 2. FTSH-1xx-04-x-DV terminal strip (upper board, bottom side)

Land pattern (F-FP sheet 1 Fig 1, symmetric about both centrelines):

| Item | Value | Status |
|---|---|---|
| Pitch | 1.27 | drawing |
| Pad width (along the row) | 0.74 | drawing |
| Pad length (across the row) | 2.79 | drawing |
| Outer span over both rows | 6.86 | drawing |
| Gap between rows (inner edges) | 1.28 | DERIVED (6.86 - 2 x 2.79) |
| Pad centre to connector centreline | 2.035 | DERIVED |
| Row centre-to-centre | 4.07 | DERIVED |
| First-to-last pad centre, 10 positions | 11.43 | drawing formula |
| Connector outline on the pattern | N x 1.27 long x 3.43 wide = 12.70 x 3.43 | drawing |
| Alignment holes | only for option -A: 2 holes dia 1.02 on the centreline, (N-2) x 1.27 apart (10.16 for 10 pos). Table 1: -K, -M, -P = N/A (no holes) | drawing |

Plain -DV and -DV-P therefore have no holes. With -A the pins are 0.89 dia REF (F-PRT sheet 2 Fig 3).

Body and posts (F-PRT sheet 1):

- Body length N x 1.27, +0.13/-0.36 -> **12.70** for 10 positions; body width 3.43 REF; width over SMT leads 5.84 REF (5.8 measured at bend).
- Insulator top above the board: **2.92 +0.13/-0.08** (insulator itself is 2.51 REF thick; the rest is lead standoff).
- Post: 0.41 square REF (catalog says 0.40 SQ).
- Lead style -04: post length "A" above the insulator = **3.81**; gold contact area "B" = 1.78 REF (Table 1). Other styles: -01 3.05, -02 1.91, -03 1.65, -05 4.32.
- Post tip above the board = 6.73 (DERIVED, 2.92 + 3.81).
- Coplanarity 0.10 (2 to 29 positions per F-PRT Table 6; catalog says 02-25).
- -P: plastic pad PPP-25 (PPP-25-NT when combined with -TR) pressed over the posts at mid-length, about 5.1 long x 3.3 wide (5.8 for the -NT version) x 4.1 tall REF; 4 positions minimum.

## 3. Mated height and 8.0 / 8.5 mm standoffs

MATED sheet 1, Fig 2 / Table 2, "FTSH-DV mated with SFMC-02-D"; dimension "B" is drawn from the lower board surface to the upper board surface:

| FTSH-DV lead style | B fully mated | B max | Wipe fully mated | Wipe min |
|---|---|---|---|---|
| **-04** | **7.65** (.301") | **8.38** (.330") | 1.12 | 0.38 |
| -05 | 7.77 | 8.89 | 1.50 | 0.38 |
| -14 | 7.65 | 8.38 | 1.12 | 0.38 |

(The expected 7.62 is 4.70 + 2.92; Samtec's table says 7.65.)

SFMC insertion depth (S-CAT specifications): **3.05 to 4.06 mm**.

| Board gap | Above fully mated | Wipe (DERIVED) | Post insertion (DERIVED, 3.81 at full mate) | Inside Samtec's range? |
|---|---|---|---|---|
| 7.65 | 0 | 1.12 | 3.81 | yes |
| **8.00** | 0.35 | 0.77 | 3.46 | **yes** (0.38 below B max) |
| 8.13 (8.00 standoff at +0.13) | 0.48 | 0.64 | 3.33 | yes |
| 8.38 | 0.73 | 0.39 | 3.08 | limit |
| **8.50** | 0.85 | 0.27 | 2.96 | **no** (0.12 over B max, wipe below 0.38 min, insertion below 3.05 min) |

Conclusion: 8.0 mm standoffs are inside Samtec's specification, including the standoff's own +/-0.13 tolerance (worst case 8.13 leaves 0.25 margin to B max; connector height tolerances and solder-joint thickness under the standoff are not included in that margin). 8.5 mm standoffs are outside it. If more gap than about 8.2 is ever needed, FTSH lead style -05 (B max 8.89) is the in-spec choice.

## 4. Position numbering

- S-FP Fig 1 (looking down on the lower board's top side, rows horizontal): **01 at the bottom-right, 02 directly above it at the top-right, 03 next to 01 in the bottom row**. Odd numbers in one row, even in the other, counting right to left.
- F-FP Fig 1 (looking at the header's own mounting side): **01 at the bottom-left, 02 above it at the top-left, 03 next to 01 in the bottom row**, counting left to right. F-PRT sheet 1 agrees (01/02 at the left end, 49/50 at the right end, odd row at the bottom).
- The SFMC assembly print S-PRT shows no pin-1 mark or polarising feature on the socket, and the plain FTSH-DV has none either: both parts are physically symmetric, so numbering is purely a footprint convention.

The two footprints are mirror images of each other in numbering (same odd row, opposite counting direction). The header is on the bottom of the upper board, so seen from above through that board its pattern is mirrored left-right: 01 lands at the bottom-right, counting right to left, which is exactly the SFMC pattern. So **if each footprint is numbered exactly as its Samtec drawing shows (each viewed from its own component side), position N on the socket mates with position N on the header** when the boards are stacked with the long axes parallel and the odd rows on the same side. In KiCad: draw both footprints as the drawings show on F.Cu, then flip the FTSH one to B.Cu of the upper board; align pad 1 over pad 1. (This is DERIVED from the two footprint drawings; MATED does not show numbering.)

## 5. Part numbers, options, stock and price

Part-number structure (S-PRT, F-PRT): plating -L = 10 u" gold on contact, matte tin tail; -S = 30 u" gold; -F = 3 u" gold flash. Packaging blank = tube, -TR = tape and reel, -FR = full reel.

| Part | Meaning | Seen where | Stock / price |
|---|---|---|---|
| SFMC-110-02-L-D | socket, tube | samtec.com product page | Samtec: $3.964 (1), $3.530 (25), $3.233 (50), $3.042 (100), $2.597 (500), $2.321 (1000); tube multiple 44; "distributor stock 0", "ships tomorrow" column 0 (built to order) |
| SFMC-110-02-S-D | 30 u" gold, tube | listed as a variant on the same page, tube multiple 44 | price UNVERIFIED |
| SFMC-110-02-L-D-TR | tape and reel | same page, reel multiple 950 | price UNVERIFIED |
| SFMC-110-02-L-D-FR | full reel | same page | price UNVERIFIED |
| SFMC-110-02-L-D-K / -K-TR | with polyimide pick-and-place film | valid per S-PRT (4 pos min). -K-TR is LCSC C3323057 | LCSC C3323057: 30 in stock, $5.2057 at 1 pc, MOQ 1 |
| SFMC-110-02-L-D-P / -P-TR | with plastic pick-and-place pad | valid per S-PRT (5 pos min) | UNVERIFIED |
| FTSH-110-04-L-DV | header, tube | valid per F-PRT | Samtec page blocked: UNVERIFIED |
| FTSH-110-04-L-DV-P / -P-TR | with plastic pick-and-place pad | valid per F-PRT (4 pos min; -TR uses pad PPP-25-NT) | UNVERIFIED |
| FTSH-110-04-L-DV-TR | tape and reel | valid per F-PRT | UNVERIFIED |
| FTSH-110-04-F-DV-TR | gold flash, reel | LCSC C7279869 | LCSC: 5 in stock, $3.9748 at 1 pc, MOQ 1 |

DigiKey and Mouser stock and price: UNVERIFIED (both refused scripted access). LCSC ladder prices beyond 1 pc: UNVERIFIED.

Pick-and-place suffixes:

- **SFMC: -K** (polyimide film, 0.13 thick, 3.99 dia) or **-P** (plastic pad PPP-02). No change to the footprint.
- **FTSH-DV: -P** (plastic pad PPP-25) or -M (metal pad, marked "not engineering approved"). **On FTSH, -K is not a pick-and-place pad**: it is a keying shroud for FFSD cable mating, lead style -01 only, and is not valid on a -04 part. (-C, the polyimide film pad, is -DH only.)
- Effect on mated height: both the film/pad on the socket (it covers the contact openings) and the pad on the header (it sits on the posts) must come off before mating, so the 7.65 figure is unchanged. The drawings show the pads' positions but do not state the removal instruction or an effect on mated height in words: UNVERIFIED as a Samtec statement, DERIVED from the geometry.

## 6. Sinhoo SMTSO2080CTJ (LCSC C2916357)

Drawing (SINHOO, description "M2*5.56*L8+1.53", based on PEM SMTSO):

| Item | Value |
|---|---|
| Thread | M2 x 0.4, through |
| Body diameter | 5.56 +/-0.13 |
| Body length (board surface to top) | 8.00 +/-0.13 |
| Pilot diameter | 3.60 +0/-0.15 |
| Pilot length | 1.53 +0/-0.15 |
| Material / finish | brass C3604, tin |
| Packaging | reel, 500 pcs |

All four expected dimensions confirmed. Recommended board hole and pad size are not on this drawing: UNVERIFIED.
LCSC: 3720 in stock, $0.1585 at 1 pc (product page, 2026-11-17).

## KiCad stock library check

No SFMC, FTSH, SFM or TFM footprint exists under /usr/share/kicad/footprints. The generic ones do not match Samtec's patterns and should not be used as-is:

| Footprint | Pad | Pad centre from centreline | Samtec recommends |
|---|---|---|---|
| Connector_PinSocket_1.27mm/PinSocket_2x10_P1.27mm_Vertical_SMD | 2.1 x 0.75 | 1.80 (outer span 5.70, inner gap 1.50) | SFMC: 2.22 x 0.74 at 1.365 (outer 4.95, inner 0.51) |
| Connector_PinHeader_1.27mm/PinHeader_2x10_P1.27mm_Vertical_SMD | 2.4 x 0.74 | 1.95 (outer 6.30, inner 1.50) | FTSH-DV: 2.79 x 0.74 at 2.035 (outer 6.86, inner 1.28) |

The generic socket footprint in particular is far too wide for the SFMC (its pads start 0.75 from the centreline; the SFMC leads only reach 2.095 from it).
