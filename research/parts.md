# Parts sourcing — STM32F765VIT6 ArduPilot flight controller (JLCPCB assembly)

Compiled 2026-11-16. Input 2S–4S (6–17 V).

## 0. How to read this file (stock-data caveats — important)

- **Stock source**: `https://jlcsearch.tscircuit.com/api/search?q=…` (text search), queried 2026-11-16 ~05:00–05:40 UTC.
- The text search only returns parts whose stock is **known and > 0**. A part that does not show up is **"not listed"** = zero *or unknown*, not proven out of stock.
- Exact-part lookups (`q=Cxxxxx`) returned `stock: null` (unknown) for almost every part, with `stock_checked_at` dates between 2026-11-01 and 2026-11-15. Per the jlcsearch docs, `null` means "observation older than 72 h / unverified", not zero. So **the stock figures below are the search-index values, up to ~2 weeks old**. During the session one part (KH-TYPE-C-16P) changed from 147,898 to "unknown" within minutes. **Re-check every extended part on jlcpcb.com/parts before ordering.**
- Prices are the search-index unit price (USD, qty-1 tier). Where the exact lookup gave a materially different price it is noted (e.g. BMP388 $2.39 vs $6.83, ICM-42688-P $17.01 vs $22.73).
- The API has no manufacturer field. Manufacturer names come from the LCSC datasheet page title for that C-number. Several high-stock listings of "brand-name" MPNs are **clones from other makers** (Tokmas, HXY, Tech Public, UMW…); these are called out.
- "Basic" = `is_basic` from the API. Everything else is Extended (JLC charges a per-part loading fee).
- **UNVERIFIED** = I could not confirm the fact from a datasheet I actually opened. "From memory" items are flagged the same way.
- KiCad footprint checks were made against the locally installed **KiCad 9.0.9** library (`/usr/share/kicad/footprints`).
- Datasheet links of the form `https://www.lcsc.com/datasheet/Cxxxxx.pdf` open the LCSC-hosted datasheet for that exact C-number.

---

## 1. MCU

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| Recommended | ST | STM32F765VIT6 | C710319 | Ext | **52** | $16.34 | LQFP-100 14x14 |
| Alternate (drop-in) | ST | STM32F767VIT6 | C91934 | Ext | **26** | $14.61 | LQFP-100 14x14 |
| Alternate | ST | STM32F777VIT6 | — | — | **not listed** (no LQFP-100 F777 in the index) | — | — |

- C710319 confirmed: 52 pcs, $16.34.
- STM32F765xx and STM32F767xx share one ST datasheet (title page lists STM32F765xx/767xx/768Ax/769xx), so F767VIT6 is the same LQFP-100 pinout family. F767 adds LCD-TFT/JPEG peripherals only. Pin-for-pin identity of every LQFP-100 pin was not diffed in this task (UNVERIFIED at pin level, but it is the same datasheet pinout table).
- Other F7 seen in stock (different packages, not drop-in): STM32F777ZIT6 LQFP-144 C5271061 (173), STM32F767ZIT6 LQFP-144 C90235 (119), STM32F765VGT6 (1 MB flash, LQFP-100) C435845 (18, $8.39), STM32F765IIK6 UFBGA-176 C968766 (271).
- Sources: https://www.lcsc.com/datasheet/C710319.pdf , https://www.lcsc.com/datasheet/C91934.pdf

---

## 2. IMU

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| Requested part (genuine) | TDK InvenSense | ICM-42688-P | C1850418 | Ext | **5** | $17.01 (exact lookup: $22.73) | LGA-14 2.5x3 |
| Same MPN, **clone** | Tokmas | ICM-42688-P(TOKMAS) | C54308212 | Ext | 6,202 | $3.28 | LGA-14 2.5x3 |
| Same MPN, **clone** | HXY MOSFET | ICM-42688P-HXY | C46550687 | Ext | 2,545 | $3.53 | LGA-14 2.5x3 |
| **Alternate A (genuine, pin-compatible)** | TDK InvenSense | ICM-45686 | C22459454 | Ext | 1,217 | $14.35 | LGA-14 3x2.5 |
| **Alternate B (genuine, cheap)** | Bosch | BMI270 | C2836813 | Ext | 8,303 | $3.63 | LGA-14 2.5x3 |
| Other | TDK InvenSense | ICM-42670-P | C3288646 | Ext | 3,988 | $3.18 | LGA-14 2.5x3 |
| Other | TDK / HXY clone | ICM-42605 / ICM-42605-HXY | C2655099 / C46550688 | Ext | 65 / 542 | $8.95 / $3.50 | LGA-14 2.5x3 |

**Surprise:** genuine TDK ICM-42688-P has only 5 pcs. The well-stocked "ICM-42688-P" listings are Tokmas/HXY parts (behaviour vs. the TDK part is UNVERIFIED). Options: (a) use the 5 genuine pcs for a ≤5-board prototype run, (b) populate ICM-45686 (genuine, same pin functions — see below; needs ArduPilot Invensensev3 driver support for 45686, UNVERIFIED in this task), (c) BMI270.

### ICM-42688-P pinout (TDK DS-000347, section 4.1)

| Pin | Name | Function |
|---|---|---|
| 1 | AP_SDO / AP_AD0 | SPI MISO (4-wire) / I2C address LSB |
| 2 | RESV | No connect or GND |
| 3 | RESV | No connect or GND |
| 4 | INT1 / INT | Interrupt 1 (push-pull or open-drain) |
| 5 | VDDIO | IO supply |
| 6 | GND | Ground |
| 7 | RESV | Connect to GND |
| 8 | VDD | Supply |
| 9 | INT2 / FSYNC / CLKIN | Interrupt 2 / frame sync (GND if FSYNC unused) / external clock in |
| 10 | RESV | No connect or GND |
| 11 | RESV | No connect or GND |
| 12 | AP_CS | SPI chip select (tie to VDDIO for I2C) |
| 13 | AP_SCL / AP_SCLK | I2C SCL / SPI clock |
| 14 | AP_SDA / AP_SDIO / AP_SDI | I2C SDA / SPI MOSI |

- External parts (datasheet Table 10): VDD → **0.1 µF + 2.2 µF** X7R; VDDIO → **10 nF** X7R. I2C address 0x68 (AD0=0) / 0x69 (AD0=1). Supply 1.71–3.6 V.
- **ICM-45686** (DS-000489 Table 10): pin 1 AP_SDO/AD0, 4 INT1, 5 VDDIO, 6 GND, 8 VDD, 9 INT2/FSYNC/CLKIN, 12 AP_CS, 13 AP_SCLK, 14 AP_SDI — same positions. Pins 2, 3, 10, 11 are RESV/AUX1 ("NC or VDDIO or GND"), pin 7 RESV ("NC, VDDIO or GND"). BOM: 0.1 µF on VDD, 0.1 µF on VDDIO. So an ICM-42688-P footprint with pins 2/3/10/11 unconnected and pin 7 to GND takes either part.
- **BMI270** (BST-BMI270-DS000 Table 22): 1 SDO, 2 ASDx, 3 ASCx, 4 INT1, 5 VDDIO, 6 GNDIO, 7 GND, 8 VDD, 9 INT2, 10 OCSB, 11 OSDO (pins 12 CSB / 13 SCx / 14 SDx: table rows beyond pin 11 were not extracted — UNVERIFIED). Pins 2/3 "VDDIO or DNC", 10/11 DNC. Same power/INT positions as the ICM parts, so a footprint with 2/3/10/11 left open is compatible with all three, subject to confirming BMI270 pins 12–14.
- Sources: https://www.lcsc.com/datasheet/C1850418.pdf , https://www.lcsc.com/datasheet/C22459454.pdf , https://www.lcsc.com/datasheet/C2836813.pdf

---

## 3. Barometer (I2C)

| Part | Mfr | LCSC | Stock | Price | Package | Notes |
|---|---|---|---|---|---|---|
| **BMP388 (recommended)** | Bosch | C779278 | 12,887 | $2.39 (exact lookup: $6.83) | LGA-10 2x2 | best-stocked of the five requested |
| BMP388(TOKMAS) | Tokmas (clone) | C54582187 | 8,135 | $2.29 | LGA-10 2x2 | clone |
| **BMP581 (alternate, same footprint/pinout)** | Bosch | C5362283 | 10,875 | $2.83 | LGA-10 2x2 | I2C 0x46/0x47 |
| DPS310XTSA1 | Infineon | — | **not listed** | — | — | no in-stock hit for DPS310 |
| DPS368XTSA1 | Infineon | C3232508 | 10,848 | $3.90 | VLGA-8 2x2.5 | DPS310 successor, same pinout |
| BMP390 | Bosch | — | **not listed** | — | — | |
| SPL06-001 | Goertek | C2684428 | unknown (null) | $1.02 | LGA-8 2x2.5 | not in in-stock index |
| SPL07-003 | Goertek | C3253727 | 24,526 | $0.88 | SMD-10P | ArduPilot support UNVERIFIED |
| ICP-20100 | TDK | C5343527 | 16,387 | $1.38 | LGA-10 | |

ArduPilot driver support (BMP388/390, DPS310/DPS368 via DPS280 driver, BMP581, SPL06, ICP-201xx) is from memory and was **not re-checked against the ArduPilot source — UNVERIFIED**.

### BMP388 pinout (BST-BMP388-DS001 Table 50)

| Pin | Name | I2C connection |
|---|---|---|
| 1 | VDDIO | VDDIO (1.2–3.6 V) |
| 2 | SCK | SCL |
| 3 | VSS | GND |
| 4 | SDI | SDA |
| 5 | SDO | address select (SA0) |
| 6 | CSB | VDDIO (selects I2C) |
| 7 | INT | host interrupt or leave open |
| 8 | VSS | GND |
| 9 | VSS | GND |
| 10 | VDD | VDD (1.65–3.6 V) |

- **Address: SDO → GND = 0x76; SDO → VDDIO = 0x77. SDO must not float.** CSB tied to VDDIO for I2C.
- Recommended: C1, C2 = 100 nF (VDD, VDDIO); I2C pull-ups 4.7 kΩ.
- **BMP581** has the identical 10-pin assignment (1 VDDIO, 2 SCK, 3 VSS, 4 SDI, 5 SDO, 6 CSB, 7 INT, 8 VSS, 9 VSS, 10 VDD); address 0x46 (SDO=0) / 0x47 (SDO=1).
- **DPS368**: 1 GND, 2 CSB, 3 SDI, 4 SCK, 5 SDO, 6 VDDIO, 7 GND, 8 VDD; address 0x77 default, 0x76 with SDO pulled to GND.
- Sources: https://www.lcsc.com/datasheet/C779278.pdf , https://www.lcsc.com/datasheet/C5362283.pdf , https://www.lcsc.com/datasheet/C3232508.pdf

---

## 4. Analog OSD — AT7456E

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| Recommended | Zhongkewei (Hangzhou) | AT7456E | C82351 | Ext | 22,167 | $3.29 (exact lookup $3.74) | HTSSOP-28 with EP |
| Alternate | Zhongkewei | AT7456ELAH | C42388749 | Ext | 658 | $3.53 | LGA-16 4x6.8 |

### Supply voltage — the key question

- **AT7456E datasheet (V1.1): AVDD, DVDD, PVDD each 3.15 V min / 5 V typ / 5.25 V max.** So it **is 3.3 V capable** (unlike the original MAX7456, whose datasheet says 4.75–5.25 V only). Abs max 6 V.
- Logic inputs (CS, SDIN, SCLK): VIH 2.0 V min, VIL 0.8 V max → 3.3 V SPI works even with the chip at 5 V. CLKIN thresholds are 0.65/0.3 × DVDD.
- SDOUT / open-drain outputs: VOL 0.45 V max at 4 mA. SDOUT high level is DVDD-referenced, so with DVDD = 5 V SDOUT swings to 5 V (STM32F7 5 V-tolerant pin needed); running everything at 3.3 V avoids this.
- Supply current (typ/max): IAVDD 2.2/2.5 mA, IDVDD 43.1/60 mA, IPVDD 6/10 mA.
- All electrical tables' typical values are given at 5 V; video output performance at 3.3 V is not separately specified (UNVERIFIED).

### Pinout, TSSOP-28 (datasheet pin table)

| Pin | Name | Function |
|---|---|---|
| 1, 2 | N.C. | not connected |
| 3 | DVDD | digital supply, 0.1 µF to DGND |
| 4 | DGND | digital ground |
| 5 | CLKIN | crystal 1 / 27 MHz clock input |
| 6 | XFB | crystal 2 (leave open with external clock) |
| 7 | CLKOUT | 27 MHz clock out |
| 8 | CS | chip select, active low |
| 9 | SDIN | SPI data in |
| 10 | SCLK | SPI clock (to 10 MHz) |
| 11 | SDOUT | SPI data out (hi-Z when CS high) |
| 12 | LOS | loss-of-sync, open drain, 1 kΩ pull-up |
| 13 | SYNC_IN | external composite sync in (AT7456E only) — **the table also lists 13–16 as N.C.; treat 13 as SYNC_IN, leave open if unused (datasheet inconsistency)** |
| 14–16 | N.C. | |
| 17 | VSYNC | open drain, 1 kΩ pull-up |
| 18 | HSYNC | open drain, 1 kΩ pull-up |
| 19 | RESET | active-low reset in |
| 20 | AGND | analog ground |
| 21 | AVDD | analog supply, 0.1 µF to AGND |
| 22 | VIN | CVBS in |
| 23 | PGND | driver ground |
| 24 | PVDD | driver supply, 0.1 µF to PGND |
| 25 | SAG | sag-correction input; tie to VOUT if unused |
| 26 | VOUT | video out |
| 27, 28 | N.C. | |
| EP | — | internally AGND; solder to AGND plane |

### Reference circuit values

- **VIN: 0.1 µF series (AC-coupling) capacitor is required**; the input is clamped internally (DC restore), so **no external clamp**. 75 Ω termination to AGND at the video input.
- **VOUT: series 75 Ω** back-termination. Output coupling (datasheet Table 2, COUT / CSAG / line-time distortion): 470 µF/—/0.2 %, 100 µF/—/0.4 %, 100 µF/22 µF/0.3 %, 47 µF/47 µF/0.3 %, 22 µF/22 µF/0.4 %, 10 µF/10 µF/0.6 %. If SAG is not used tie SAG to VOUT. (Small FCs commonly DC-couple or use a small ceramic here — that is practice, not datasheet.)
- 0.1 µF bypass on each of DVDD/AVDD/PVDD; 1 kΩ pull-ups on LOS/VSYNC/HSYNC if used.
- **Crystal: 27 MHz, parallel-resonant, fundamental mode, between CLKIN and XFB.** The AT7456E datasheet text gives no load-capacitance figure. The MAX7456 datasheet (which the part clones) says "No external load capacitors are needed. All capacitors required for the Pierce oscillator are included on-chip." **Required crystal CL: UNVERIFIED** (not stated in either datasheet). See section 16 for the crystal.
- Sources: https://www.lcsc.com/datasheet/C82351.pdf , MAX7456 datasheet https://www.sparkfun.com/datasheets/BreakoutBoards/MAX7456.pdf

---

## 5. 5 V buck regulator (6–17 V in, ≥3 A)

### Candidate stock

| MPN | Mfr | LCSC | Stock | Price | Package | Vin | Comment |
|---|---|---|---|---|---|---|---|
| **TPS62933DRLR (recommended)** | TI | C3200405 | 8,084 | $0.53 | SOT-583 (8-pin, 1.6x2.1) | 3.8–30 V | 98 % max duty |
| **AP63301WU-7 (alternate)** | Diodes | C2158003 | 7,245 | $0.73 | TSOT-26 | 3.8–32 V | LDO (low-dropout) mode, forced PWM |
| TPS563300DRLR | TI | C5219249 | 2,660 | $0.45 | SOT-583 | 3.8–28 V | |
| TPS62933PDRLR / FDRLR / ODRLR | TI | C5219254 / C5219272 / C6290372 | 6,199 / 3,294 / 2,925 | $1.11–1.30 | SOT-583 | | PG / FCCM / OOA variants |
| TPS54302DDCR | TI | C311983 | 71,652 | $0.25 | TSOT-23-6 | 4.5–28 V | max duty not checked |
| TPS563201DDCR | TI | C116592 | 120,951 | $0.07 | SOT-23-6 | 4.5–17 V | Vin max 17 V = no margin on 4S; not recommended |
| AP63300WU-7 | Diodes | C2158012 | 121 | $0.66 | TSOT-26 | | low stock |
| MP2315GJ-Z | MPS | C45889 | 667 | $2.28 | TSOT-23-8 | 4.5–24 V | |
| SY8303AIC | Silergy | C97054 | 107,256 | $0.69 | TSOT-23-8 | 4.5–40 V | |
| TPS62130RGTR / TPS62133RGTR | TI | C43590 / C73973 | 25,065 / 1,684 | $1.24 / $1.68 | QFN-16 3x3 | 3–17 V | Vin max 17 V, no margin on 4S |
| TPS56339DDCR | TI | C2071106 | 11,960 | $0.36 | TSOT-23-6 | 4.5–24 V | |

### TPS62933 key facts (TI SLUSEA4D)

| Item | Value |
|---|---|
| Pinout (SOT-583 DRL) | 1 RT, 2 EN, 3 VIN, 4 GND, 5 SW, 6 BST, 7 SS, 8 FB |
| Vin | 3.8–30 V operating, 32 V abs max |
| Feedback voltage | 0.8 V (788–812 mV, 0–85 °C) |
| Switching frequency | RT floating = 500 kHz (450–550); RT to GND = 1.2 MHz; RT resistor 200 kHz–2.2 MHz |
| Max duty / dropout | **"Maximum 98 % duty cycle"**; on-time extension up to 7 µs, min off-time 140 ns typ, min on-time 70 ns. Frequency folds back in dropout while output stays regulated. |
| FETs | 76 mΩ high-side, 32 mΩ low-side |
| Current limit | high-side 4.2 / 5 / 5.8 A (min/typ/max); low-side 2.9 / 3.8 / 4.5 A |
| EN | rising 1.21 V typ (1.28 max), falling 1.17 V typ (1.1 min); floats high (internal pull-up current 0.7 µA + 1.4 µA hysteresis current); EN abs max 6 V — **do not tie EN directly to a 17 V VIN; use a divider or leave floating** |
| BOOT cap | 100 nF ceramic BST–SW (optional series resistor) |
| Soft-start | SS cap; 33 nF → 5 ms in the reference design |
| Recommended LC, 5 V (Table 10-2) | 500 kHz: **L = 6.8 µH**, typical effective COUT 20 µF, minimum effective 10 µF. 1.2 MHz: 3.3 µH, 20 µF |
| TI 5 V/3 A reference design (Fig. 10-1) | CIN 2x10 µF + 100 nF; L 6.8 µH; COUT 2x22 µF (1206, 35 V) + 100 nF; R6 53.6 kΩ / R7 10.2 kΩ; 49.9 Ω injection resistor; 10 pF feed-forward (DNP) |
| Divider | Table 10-2 gives RTOP 52.5 kΩ / RDOWN 10.0 kΩ for 5 V |

Dropout estimate at 5.8 V in, 3 A (my calculation, not datasheet): 98 % duty → 5.68 V available, minus 3 A × (76 mΩ + ~50 mΩ DCR) ≈ 0.38 V → about 5.3 V, so 5.0 V is held with margin; HS RDS(on) rises with temperature, so expect regulation to be lost somewhere around 5.5–5.6 V in at full load.

**Feedback divider with JLC basic 0402 parts:** RTOP = 51 kΩ (C25794) + 1.5 kΩ (C25867) in series = 52.5 kΩ, RBOT = 10 kΩ (C25744) → 0.8 × (1 + 52.5/10) = **5.000 V**. Single-resistor E96 alternative: 52.3 kΩ (0402WGF5232TCE, C26982, extended, stock unknown) with 10 kΩ → 4.984 V.

### AP63301 (alternate) facts (Diodes datasheet)

- Pinout TSOT-26: 1 FB, 2 EN, 3 IN, 4 GND, 5 SW, 6 BST. FB 0.8 V ±1 %, 500 kHz fixed, forced PWM (AP63300 = PFM at light load).
- EN threshold 1.18 V rising / 1.09 V falling; internal 4 ms soft-start; BST cap 100 nF.
- Feature list: "Low-Dropout (LDO) Mode". Typical application: 5 V out with 6.8 µH and 2x22 µF, 10 µF in. Exact max duty figure UNVERIFIED.

### Inductor

| Role | Mfr | MPN | LCSC | Stock | Price | L | Isat / Irms | DCR | Size |
|---|---|---|---|---|---|---|---|---|---|
| **Recommended (5x5 class)** | Shun Xiang Nuo (SXN) | SMMS0530-4R7M | C181722 | 18,527 | $0.11 | 4.7 µH ±20 % | 5.0 A / 4.5 A | 50 typ / 60 max mΩ | 5.5±0.3 x 5.2±0.2 x 3.0 max mm |
| Alternate (matches TI's 6.8 µH) | Sunlord | MWSA0624S-6R8MT | C408434 | 1,871 | $0.14 | 6.8 µH | 6 A / 4 A (API listing) | 70 mΩ | 7 x 6.6 x 2.4 mm |
| Alternate | Sunlord | MWSA0603S-6R8MT | C408449 | 675 | $0.14 | 6.8 µH | 6 A / 5 A (API listing) | 48 mΩ | 7 x 6.6 x 3 mm |
| Not suitable | SXN | SMMS0530-6R8M | — | — | — | 6.8 µH | 4.0 A / 3.5 A | 102/110 mΩ | Isat below the 4.5 A target |

- **SMMS0530 land pattern (datasheet p.2):** two pads, each 2.0 mm (along length) x 2.5 mm (H); inner gap F = 3.00 mm; overall span G = 7.00 mm (pad centres ±2.5 mm). Terminal size 2.3 x 1.2 mm typ.
- KiCad 9 has no SXN/Sunlord footprint. Closest stock footprint is `Inductor_SMD:L_APV_APH0530` (pads 1.9 x 2.5 at ±2.05 mm, i.e. span 6.0 / gap 2.2) — usable but not the recommended pattern; a custom footprint per the dimensions above is safer.
- With 4.7 µH at 500 kHz the ripple is larger than TI's 6.8 µH design: ΔI ≈ 5 V × (1 − 5/17) / (4.7 µH × 500 kHz) ≈ 1.5 A p-p at 17 V in → 3.75 A peak at 3 A load (below 5 A Isat and below the 4.2 A min HS limit, but little margin). Either accept this, raise fsw with an RT resistor (~700–800 kHz), or use a 6.8 µH 7x6.6 part. MWSA06xx land pattern UNVERIFIED (datasheet not retrieved); SXN's same-size SMMS0624/0630 uses gap 3.70 / span 8.40 / pad height 3.50 mm.
- Sources: https://www.ti.com/lit/ds/symlink/tps62933.pdf , https://www.lcsc.com/datasheet/C2158003.pdf , https://www.lcsc.com/datasheet/C181722.pdf

---

## 6. High-side current-sense amplifier

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package | Gain |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | TI | INA214AIDCKR | C105240 | Ext | 13,383 | $0.86 | SC-70-6 | 100 V/V |
| **Alternate** | TI (brand UNVERIFIED — LCSC page not found) | INA181A3IDCKR | C32077329 | Ext | 5,732 | $0.34 | SC-70-6 | 100 V/V |
| Other | TI | INA190A2IDCKR | C2870223 | Ext | 2,877 | $1.66 | SC-70-6 | 50 V/V |
| Other | ST | TSC2011IDT | C1857476 | Ext | 2,022 | $2.30 | SO-8 | 60 V/V (from memory) |
| Other | XBLW (clone) | INA180A1IDBVR(XBLW) / INA181A1IDBVR(XBLW) | C45351497 / C45351496 | Ext | 7,289 / 3,516 | $0.15 / $0.20 | SOT-23-5/6 | 20 V/V |
| INA240A2/A3 | TI | — | — | — | **not listed** (only INA240A4QDRQ1, 1 pc) | | | |
| INA186, INA199A1/A2, TSC2010, TSC2012 | | | | | **not listed** (INA199: 1 pc each) | | | |

### INA214 facts (TI INA21x datasheet)

- Pinout SC-70-6 (DCK): **1 REF, 2 GND, 3 V+, 4 IN+, 5 IN−, 6 OUT**. IN+ to the supply side of the shunt, IN− to the load side. REF to GND for unidirectional output.
- Supply 2.7–26 V (3.3 V fine). Common-mode −0.3 to +26 V (version A) — covers 4S (17 V) with margin.
- Family gains: INA210 200, INA211 500, INA212 1000, INA213 50, **INA214 100**, INA215 75 V/V.
- Offset (RTI): INA214 ±1 µV typ, **±60 µV max**; drift 0.1 typ / 0.5 max µV/°C. Gain error ±1 % max (A version). Zero-drift architecture. Input bias current ~28 µA typ.
- Scaling: 0.5 mΩ × 50 A = 25 mV × 100 = **2.5 V** (3.3 V full scale ≈ 66 A); offset ±60 µV ≈ ±0.12 A. With 0.25 mΩ: 1.25 V at 50 A (132 A full scale) — for 0.25 mΩ a 200 V/V part (INA210 / INA181A4) would be the match, neither listed in stock.

### INA181 facts (TI SBOS793)

- Pinout SC-70-6 (DCK): **1 REF, 2 GND, 3 VS, 4 IN+, 5 IN−, 6 OUT** (same as INA214 → footprint-compatible). SOT-23-6 (DBV) differs: 1 OUT, 2 GND, 3 IN+, 4 IN−, 5 REF, 6 VS.
- VS 2.7–5.5 V; common-mode −0.2 to +26 V. Gains A1 20, A2 50, A3 100, A4 200 V/V.
- Offset ±150 µV max at VCM = 0 V, **±500 µV max at VCM = 12 V** (≈ ±1 A with 0.5 mΩ); drift 1 µV/°C max; gain error ±1 % max; 350 kHz bandwidth (A1).
- Sources: https://www.lcsc.com/datasheet/C105240.pdf , https://www.ti.com/lit/ds/symlink/ina181.pdf

---

## 7. Shunt resistor

| Role | Mfr | MPN | LCSC | Stock | Price | Value | Power | TCR | Size |
|---|---|---|---|---|---|---|---|---|---|
| **Recommended 0.5 mΩ** | Yezhan | ASR-M-3-0.5F | C469426 | 127,608 | $0.28 | 0.5 mΩ 1 % | 6 W (P70 °C) | ±115 ppm | 2512 |
| **Alternate 0.25 mΩ (same land pattern)** | Yezhan | ASR-M-3-0.25F | C495759 | 16,958 | $0.30 | 0.25 mΩ 1 % | 6 W (API listing) | ±175 ppm | 2512 |
| 0.5 mΩ, 3 W | TA-I | RLM25FEGMR50M | C710260 | 166,646 | $0.07 | 0.5 mΩ 1 % | 3 W | ±75 ppm | 2512 (**different land pattern**) |
| 0.25 mΩ, 3 W | Milliohm (Ho) | HoLRS2512-3W-0.25mR-1% | C5127850 | 8,268 | $0.17 | 0.25 mΩ 1 % | 3 W (109.5 A rated) | ±100 ppm | 2512 (same pattern as ASR-M-3) |
| 0.5 mΩ | (brand not checked) | EBWM2512FL500S9 | C7178835 | 117,298 | $0.24 | 0.5 mΩ 1 % | 6 W | ±200 ppm | 2512 |
| 0.3 mΩ | Yezhan | ASR-M-3-0.3F | C495760 | 59,697 | $0.31 | 0.3 mΩ 1 % | 6 W | ±175 ppm | 2512 |
| 0.2 mΩ | Yezhan | ASR-M-5-0.2F | C6075495 | 37,186 | $0.46 | 0.2 mΩ 1 % | 12 W | ±200 ppm | **3920** |
| 0.5 mΩ larger | Yezhan | ASR-M-5-0.5F / ASR-M-7-0.5F | C469433 / C469444 | 67,142 / 46,713 | $0.32 / $0.41 | 0.5 mΩ | 9 W / 10 W | ±70 / ±75 ppm | 3920 / 5930 |

No 0.2 mΩ 2512 part was found in stock (0.2 mΩ needs 3920). Dissipation at 50 A: 0.5 mΩ → 1.25 W; 0.25 mΩ → 0.63 W; 0.2 mΩ → 0.5 W.

**Land patterns (from the datasheets):**

- **Yezhan ASR-x-3 (2512)**: body W 6.3±0.2, terminal A 1.2±0.2, width C 3.1±0.3, height 0.5±0.1 mm. Solder pad: overall span w = 7.0 mm, pad height c = 3.4 mm, pad width a = 1.8 mm → two pads 1.8 x 3.4 mm, inner gap 3.4 mm. (3920: w 11 / c 6.2 / a 2.7. 5930: w 16 / c 8.75 / a 5.2.)
- **Milliohm HoLRS2512**: body 6.4±0.3 x 3.2±0.3 x 1.7±0.3 mm, terminal 1.2±0.5 mm. Pad: L = 7 (overall), A = 3.4 (pad height), B = 3.4 (inner gap) → same 1.8 x 3.4 pads, span 7.0. Kelvin sense traces from the inner pad edges.
- **TA-I RLM25**: body 6.4±0.2 x 3.2±0.2, terminal length 2.6±0.2, thickness 0.6 mm. Pad: a = 4.0 (pad height), b = 3.1 (pad length, each), L = 1.3 (gap between pads) → span 7.5 mm; sense traces from the inner edges. **Not interchangeable with the ASR/HoLRS pattern.**
- KiCad `Resistor_SMD:R_2512_6332Metric` (pads 1.225 x 3.35 at ±2.96, gap 4.7 mm) matches none of these well; `R_Shunt_Vishay_WSK2512_*` is a 4-terminal Vishay pattern. Use a custom 2-pad + Kelvin footprint.
- Sources: https://www.lcsc.com/datasheet/C469426.pdf , https://www.lcsc.com/datasheet/C5127850.pdf , https://www.lcsc.com/datasheet/C710260.pdf

---

## 8. 3.3 V LDOs (from 5 V)

### (a) Main, ≥500 mA

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package | Iout |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | TI | TLV75533PDBVR | C404027 | Ext | 73,140 | $0.15 | SOT-23-5 | 500 mA |
| **Alternate** | Diodes | AP2112K-3.3TRG1 | C51118 | Ext | 29,988 | $0.16 | SOT-25 | 600 mA |
| Same MPN, clone | Tech Public | AP2112K-3.3TRG1 | C23380830 | Ext | 109,252 | $0.11 | SOT-23-5 | (clone) |
| Other | Richtek | RT9013-33GB | C47773 | Ext | 309,350 | $0.14 | SOT-23-5 | 500 mA |
| Other | Microne | ME6211C33M5G-N | C82942 | Ext | 292,408 | $0.05 | SOT-23-5 | 500 mA |
| Other (1 A) | TI | TLV75733PDBVR | C485517 | Ext | 20,060 | $0.18 | SOT-23-5 | 1 A |
| Other | Richtek | RT9080-33GJ5 | C841192 | Ext | 27,566 | $0.12 | TSOT-23-5 | 600 mA |
| SOT-223, 1.2 A | ST | LDL1117S33R | C435835 | Ext | 51,388 | $0.21 | SOT-223 | 1.2 A |

- **TLV75533PDBVR**: pinout **1 IN, 2 GND, 3 EN, 4 NC, 5 OUT**. Dropout at 500 mA for 3.3 V ≤ VOUT < 5 V: 150 mV typ / 215 mV max. Vin to 5.5 V. Caps: 1 µF in and out (effective ≥ 0.47 µF). Noise 71.5 µVrms, PSRR 46 dB at 100 kHz.
- **AP2112K-3.3 (Diodes)**: pinout **1 VIN, 2 GND, 3 EN, 4 NC, 5 VOUT**. Dropout 125 typ / 200 max mV at 300 mA; 250 typ / 400 max mV at 600 mA. Caps 1 µF in/out (X5R/X7R). Noise 50 µVrms, Vin max 6 V.
- SOT-23-5 thermal note (my calculation): (5 − 3.3) V × 0.5 A = 0.85 W is too much for a SOT-23-5 continuously; budget the real 3.3 V load or use the SOT-223 part.

### (b) Low-noise sensor LDO, ≥150 mA

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package | Iout |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | TI | TPS7A2033PDBVR | C2862740 | Ext | 165,494 | $0.23 | SOT-23-5 | 300 mA |
| **Alternate** | TI | LP5907MFX-3.3/NOPB | C80670 | Ext | 47,712 | $0.14 | SOT-23-5 | 250 mA |
| Other | TI | TLV73333PDBVR | C134139 | Ext | 2,438 | $0.11 | SOT-23-5 | 300 mA |
| Other | Richtek | RT9193-33GB | C15651 | Ext | 54,892 | $0.14 | SOT-23-5 | 300 mA |
| Other | Microchip | MIC5504-3.3YM5-TR | C88419 | Ext | 23,250 | $0.26 | SOT-23-5 | 300 mA |

- **TPS7A2033 (DBV)**: pinout **1 IN, 2 GND, 3 EN, 4 NC, 5 OUT** (pin 4 NC taken from the standard DBV drawing; the extracted table shows IN 1, GND 2, EN 3, OUT 5). Noise 7 µVrms, PSRR 95 dB at 1 kHz, IQ 6.5 µA. Dropout: 140 mV max at 300 mA (feature list); 145 mV max in the DBV package for 2.5–5.5 V outputs. Caps: 1 µF out (effective 0.47 µF min, 200 µF max); input cap not required for stability, 0.47 µF min effective recommended.
- **LP5907MFX-3.3**: pinout **1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT**. 250 mA; noise 6.5 µVrms (at 250 mA) / 10 µVrms (1 mA); PSRR 82 dB at 1 kHz; dropout 250 mV max at 250 mA (SOT-23); 1 µF in, 1 µF out (0.7–10 µF). EN has internal 1 MΩ pull-down. TI's own datasheet points to TPS7A20 as the updated part.
- All four parts share the 1 IN / 2 GND / 3 EN / 4 NC / 5 OUT SOT-23-5 pinout.
- Sources: https://www.ti.com/lit/ds/symlink/tlv755p.pdf , https://www.lcsc.com/datasheet/C51118.pdf , https://www.ti.com/lit/ds/symlink/tps7a20.pdf , https://www.ti.com/lit/ds/symlink/lp5907.pdf

---

## 9. 5 V power OR-ing (buck 5 V + USB VBUS, ~1 A)

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| **Recommended** | TI | LM66200DRLR | C3235556 | Ext | 20,525 | $0.49 | SOT-583 (8-pin) |
| **Alternate (2 pcs)** | TI | LM66100DCKR | C2869734 | Ext | 38,497 | $0.24 | SC-70-6 |
| Other (priority mux) | TI | TPS2116DRLR | C3235557 | Ext | 64,213 | $0.46 | SOT-583 |
| Other | TI | TPS2121RUXR | C485916 | Ext | 35,562 | $1.02 | VQFN-HR-12 |
| Other | ADI/Maxim | MAX40200AUK+T | C2649430 | Ext | 15,710 | $0.89 | SOT-23-5 |
| TPS2113APWR | TI | C130052 | Ext | 495 | $2.97 | TSSOP-8 | below 500 |
| Schottky fallback | (brand not checked) | B5819WS | C916992 | Ext | 363,102 | $0.013 | SOD-323, 1 A 40 V, VF 600 mV at 1 A |
| Schottky fallback | (brand not checked) | SS34A | C2886580 | Ext | 151,752 | $0.044 | SMA, 3 A 40 V, VF 500 mV at 3 A |

- **LM66200** (TI SLVSG04): dual ideal diode, automatic switchover to the higher input, 1.6–5.5 V, 2.5 A, 40 mΩ typ, reverse-current blocking, IQ 1.32 µA. **Abs max 6 V on VIN1/VIN2/VOUT** — USB VBUS can exceed 5.5 V on a bad charger, so keep the TVS/ESD on VBUS. Pinout: **1 GND, 2 VOUT, 3 VIN1, 4 ON (active-low enable), 5 GND, 6 VIN2, 7 VOUT, 8 ST** (ST high when VIN1 is in use).
- **LM66100** (TI SLVSEZ8A): single ideal diode, 1.5–5.5 V, 1.5 A, 79 mΩ at 5 V, −6 V reverse standoff. Pinout: **1 VIN, 2 GND, 3 CE (active low; tie to the other supply's output/VOUT for OR-ing; do not float), 4 N/C, 5 ST (open drain; GND if unused), 6 VOUT**. Two devices cross-coupled give a 2-input OR.
- **TPS2116**: 1 GND, 2 VOUT, 3 VIN1, 4 PR1, 5 MODE, 6 VIN2, 7 VOUT, 8 ST; 1.6–5.5 V, 2.5 A, 40 mΩ; priority/manual mode (not "highest wins").
- LCSC datasheet pages for C3235556/C3235557 returned "Page Not Found"; manufacturer TI inferred from the MPN.
- Sources: https://www.ti.com/lit/ds/symlink/lm66200.pdf , https://www.ti.com/lit/ds/symlink/lm66100.pdf , https://www.ti.com/lit/ds/symlink/tps2116.pdf

---

## 10. Reverse-polarity / input protection

### P-channel MOSFET (logic-supply branch, ≤7 A)

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package | Key specs |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | AOS | AONR21357 | C431196 | Ext | 48,485 | $0.33 | DFN-8 3x3 | −30 V, −34 A, RDS(on) < 7.8 mΩ at −10 V, **< 12.3 mΩ at −4.5 V**, VGS ±25 V, Vth −1.3/−1.7/−2.3 V |
| **Alternate** | Vishay | SI7617DN-T1-GE3 | C727607 | Ext | 9,727 | $1.00 | PowerPAK 1212-8 (3.3x3.3) | −30 V, −35 A, 12.3 mΩ at −10 V, 22.2 mΩ at −4.5 V, VGS ±25 V |
| SOIC-8 option | AOS | AO4407A | C16072 | Ext | 13,321 | $0.22 | SOIC-8 | −30 V, −12 A, < 13 mΩ at −10 V, < 38 mΩ at the lowest listed drive (API says "38 mΩ@5V"), Vth to −3 V — weak at 2S voltages |
| Clone | Tech Public | AON7401 | C5311002 | Ext | 3,162 | $0.28 | PDFN-8 | not genuine AOS; datasheet not readable |
| Small branch | Vishay | SI2301CDS-T1-GE3 | C10487 | **Basic** | 217,046 | $0.08 | SOT-23 | −20 V only — not for a 4S bus |
| Small branch | AOS | AO3401A | C15127 | **Basic** | 1,514,941 | $0.07 | SOT-23 | −30 V, 4 A, 60 mΩ at −4.5 V |

- AONR21357 VGS rating ±25 V covers a directly grounded gate on 4S (17 V), but a gate clamp (e.g. 12 V zener + 100 kΩ) is still advisable for transients (design advice, not datasheet).
- AON7407 (C176756, 26,957) is a **20 V** part — not suitable.

### TVS for the 2S–4S bus

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Package | Specs |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | Changzhou Starsea | SMBJ18A | C86368 | Ext | 2,010 | $0.07 | SMB | 600 W, VRWM 18 V, VC 29.2 V at 20.5 A, unidirectional (API listing; per-part row not extracted from datasheet) |
| **Alternate** | Vishay | SMAJ20A-E3/61 | C1973957 | Ext | 3,341 | $0.18 | SMA | 400 W, VRWM 20 V, VBR 22.2–24.5 V, VC 32.4 V at 12.3 A |
| Bidirectional | Goodwork | SMBJ18CA | C908850 | Ext | 21,889 | $0.04 | SMB | 600 W, 18 V, VC 29.2 V |
| Other | MCC | SMBJ20A-TP | C129531 | Ext | 905 | $0.10 | SMB | 20 V, VC 32.4 V |
| SMAJ18A, SMF18A | | | | | **not listed** | | | |

- 4S full charge is 16.8 V: 18 V standoff is just above it; clamp voltage 29.2 V is under the TPS62933 32 V abs max and the INA214 26 V common-mode limit is exceeded during a clamp event (INA21x abs max common-mode is 26 V version A) — consider series resistance on the sense inputs or the 20 V/18 V choice carefully. (Design note, my assessment.)
- Sources: https://www.lcsc.com/datasheet/C431196.pdf , https://www.lcsc.com/datasheet/C727607.pdf , https://www.lcsc.com/datasheet/C16072.pdf , https://www.lcsc.com/datasheet/C86368.pdf , https://www.lcsc.com/datasheet/C1973957.pdf

---

## 11. Small-signal parts

| Function | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| N-MOSFET | JSCJ (Changjing) | 2N7002 | C8545 | **Basic** | 6,228,872 | $0.016 | SOT-23 |
| N-MOSFET alt | onsemi | BSS138LT1G | C82045 | Ext | 401,087 | $0.042 | SOT-23 |
| N-MOSFET alt | (brand not checked) | BSS138 | C7420339 | Ext | 674,157 | $0.027 | SOT-23 |
| P-MOSFET | AOS | AO3401A | C15127 | **Basic** | 1,514,941 | $0.072 | SOT-23 |
| NPN | JSCJ | MMBT3904 (hFE 100–300) | C20526 | **Basic** | 4,381,117 | $0.011 | SOT-23 |
| Dual Schottky, common cathode | High Diode | BAT54C | C466637 | Ext | 2,567 | $0.013 | SOT-23 |
| Dual Schottky alt | Nexperia | BAT54C,215 | C37704 | Ext | unknown (null) | $0.015 | SOT-23 |
| Dual Schottky alt | (brand not checked) | BAT54CT | C77320 | Ext | 19,523 | $0.033 | SOT-523 |

No BAT54C is flagged Basic by the API today.

---

## 12. USB

### USB-C 2.0 16-pin receptacle

| Mfr | MPN | LCSC | Stock | Price | KiCad 9 footprint |
|---|---|---|---|---|---|
| Korean Hroparts | TYPE-C-31-M-12 | C165948 | **unknown** (null, last checked 2026-11-03) | $0.19 | **Yes**: `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` |
| GCT | USB4105-GF-A | C3020560 | **unknown** (null, 2026-11-10) | $1.02 | **Yes**: `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` |
| HCTL | HC-TYPE-C-16P-01A | C2894897 | unknown (null, 2026-11-02) | $0.10 | **Yes**: `USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A` |
| G-Switch | GT-USB-7010ASV | C2988369 | unknown (null, 2026-11-10) | $0.09 | **Yes**: `USB_C_Receptacle_G-Switch_GT-USB-7010ASV` |
| XKB | U262-161N-4BVC11 | C319148 | unknown (null, 2026-11-12) | $0.41 | **Yes**: `USB_C_Receptacle_XKB_U262-16XN-4BVC11` |
| Shou Han | TYPE-C 16P QTGM027 | C2681552 | **10,968** (verified 2026-11-16) | $0.18 | **No match found.** All-SMD shell tabs (4 SMD pads, no through-hole legs); datasheet layout: 12 signal pads on 0.5 mm grid spanning 5.78/6.64 mm, shell pads ~1.5 x 2.0 mm, two Ø0.65 pegs. Custom footprint needed. |
| Kinghelm | KH-TYPE-C-16P | C709357 | 147,898 seen at first query, then unknown | $0.08 | No footprint by that name (compatibility with the HRO pattern UNVERIFIED) |
| TXGA | TYPEC-304A-ACP16W | C2909607 | 2,209 | $0.21 | none by name |

**Recommendation:** design with `USB_C_Receptacle_HRO_TYPE-C-31-M-12` (C165948) — native KiCad footprint, historically JLC's most common 16-pin part — but its stock could not be confirmed through this API today. The only 16-pin horizontal part with a verified positive stock figure is C2681552, which needs a custom footprint.

### ESD

| Mfr | MPN | LCSC | Stock | Price | Package |
|---|---|---|---|---|---|
| ST | USBLC6-2SC6 | C7519 | **unknown** (null, last checked 2026-11-04) — not in the in-stock index | $0.18 | SOT-23-6L |
| (brand not checked) | USBLC6-2SC6 | C2687116 | unknown | $0.05 | SOT-23-6 |
| Fuxinsemi (clone) | USBLC6-2SC6-FS | C6807798 | 952 | $0.06 | SOT-23-6L |

USBLC6-2SC6 pinout (ST): 1 I/O1, 2 GND, 3 I/O2, 4 I/O2, 5 VBUS, 6 I/O1. Sources: https://www.lcsc.com/datasheet/C7519.pdf , https://www.lcsc.com/datasheet/C2681552.pdf

---

## 13. microSD push-push socket

| Mfr | MPN | LCSC | Stock | Price | KiCad 9 footprint |
|---|---|---|---|---|---|
| Molex | 104031-0811 | C585350 | **unknown** (null, 2026-11-10) | $0.68 | **Yes**: `Connector_Card:microSD_HC_Molex_104031-0811` |
| Hirose | DM3AT-SF-PEJM5 | C114218 | **unknown** (null, 2026-11-04) | $1.39 | **Yes**: `Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5` |
| Korean Hroparts | TF-01A | C91145 | **unknown** (null, 2026-11-01) | $0.19 | **No** |
| XUNPU | TF-115K | C266621 | **7,652** | $0.22 | **No** — custom footprint |
| (brand not checked) | TF-123-ARP9H17 | C2982548 | 6,447 | $0.13 | No (listed as push-pull) |
| XKB | XKTF-001B | C381080 | 3,041 | $0.42 | No (listed as push-pull) |

Other KiCad 9 microSD footprints present: `microSD_HC_Hirose_DM3BT-DSF-PEJS`, `microSD_HC_Hirose_DM3D-SF`, `microSD_HC_Molex_47219-2001`, `microSD_HC_Wuerth_693072010801`.

**No socket satisfies both "verified in stock" and "KiCad footprint exists" from this API today.** Recommendation: use the Molex 104031-0811 footprint and confirm C585350 stock on jlcpcb.com; fall back to TF-115K with a custom footprint.

**TF-115K land pattern (XUNPU drawing):** push-push, body 14.8 x 14.5 mm, height 1.80–2.00 mm. Nine signal pads in a row at 1.10 mm pitch (order from one end: CD, 8, 7, 6, 5, 4, 3, 2, 1; 8 x 1.10 = 8.80 mm), pad 0.70 x 1.60 mm. Four GND/shell pads: two near the contact row 1.20–1.60 wide x 1.50 mm, two at the rear 1.20 x 2.20 mm; rear pads 9.25–9.95 mm from the contact row; rear pad spacing 12.10 mm. Two Ø1.00 mm locating holes 8.00 mm apart. Pins: 1 DAT2, 2 CD/DAT3, 3 CMD, 4 VDD, 5 CLK, 6 VSS, 7 DAT0, 8 DAT1, plus card-detect switch. Exact pad coordinates must be taken from the drawing: https://www.lcsc.com/datasheet/C266621.pdf

---

## 14. Passive magnetic buzzer (SMD)

| Role | Mfr | MPN | LCSC | Stock | Price | Size | Rated / operating | Coil | Current | Freq |
|---|---|---|---|---|---|---|---|---|---|---|
| **Recommended (verified stock)** | Keliking (KLJ) | KLJ-8530-3627 | C189206 | 3,096 | $0.57 | 8.5 x 8.5 x 3.0 mm | 3.6 Vp-p rated, 2.5–4.5 V | 16 ± 3 Ω | 90 mA max at rated | 2731 Hz, ≥86 dB at 10 cm |
| **Alternate** | Jiangsu Huaneng | MLT-8530 | C94599 | **unknown** (null, 2026-11-10) | $0.20 | 8.5 x 8.5 x 3.0 mm | 3.6 Vo-p rated, 2.5–4.5 V | 16 ± 3 Ω | 95 mA max (2.7 kHz, 50 % square, 5 Vo-p) | 2700 Hz, ≥80 dB |
| Other | FUET | FUET-9045 | C391040 | 1,224 | $0.50 | Ø9 x 4.5 mm | 3 V, 2–4 V | — | 80 mA | 2.7 kHz, 85 dB |
| MLT-5020, HNB09A05 | | | | **not listed** | | | | | | |

- Both 8530 parts are 3.6 V-rated with a 16 Ω coil: from a 5 V rail add a series resistor (or drive from 3.3 V). Drive with an NPN/N-FET low-side switch plus a flyback diode.
- **Land pattern (MLT-8530 drawing):** 8.5 x 8.5 mm body with four chamfered corner terminals; flat edge between terminals 5.5 mm; overall terminal span 8.7 mm. "+ lead" and "− lead" are the two corners on one side; the other two are dummy pads. Height 3.0 mm, side sound port.
- **KiCad:** no MLT-8530/KLJ footprint. `Buzzer_Beeper:MagneticBuzzer_CUI_CMT-8504-100-SMT` (8.5 x 8.5, four 2.5 x 2.5 mm pads at ±3.5 mm) covers the corner terminals geometrically; **which pad numbers are + / − versus dummy must be checked against the buzzer drawing (UNVERIFIED)**. `Buzzer_Murata_PKMCS0909E` is a piezo part, `MagneticBuzzer_ProSignal_ABT-410-RC` is through-hole style — neither fits.
- Sources: https://www.lcsc.com/datasheet/C189206.pdf , https://www.lcsc.com/datasheet/C94599.pdf

---

## 15. Tactile switch

| Role | Mfr | MPN | LCSC | Lib | Stock | Price | Size | KiCad 9 footprint |
|---|---|---|---|---|---|---|---|---|
| **Recommended** | XKB Connection | TS-1187A-B-A-B | C318884 | **Basic** | 851,724 | $0.02 | 5.1 x 5.1 x 1.5 mm, 1.6 N | **Yes**: `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A` (pads 1.0 x 0.75 at ±3.0, ±1.875) |
| **Alternate** | XUNPU | TS-1088-AR02016 | C720477 | **Basic** | 906,645 | $0.06 | 3.9 x 3.0 x 2.0 mm, 1.6 N | No named footprint (datasheet is image-only; land pattern not extracted) |
| Other | Alps | SKRPACE010 | C139797 | Ext | 154,744 | $0.06 | 4.2 x 3.2 x 2.5 mm | none checked |

---

## 16. Crystals (3225, 4-pin)

| Function | Mfr | MPN | LCSC | Lib | Stock | Price | CL | ESR | Tol / stab |
|---|---|---|---|---|---|---|---|---|---|
| **8 MHz recommended** | YXC | XL2EL89COI-111YLC-8M (YSX321SL) | C2973805 | Ext | 167,259 | $0.16 | **12 pF** | 150 Ω max | ±10 / ±20 ppm, −40…85 °C |
| 8 MHz alternate | Yajingxin | TX32258M4DBDD2T | C5308002 | Ext | 9,348 | $0.15 | 10 pF | 250 Ω | ±10 / ±20 ppm |
| 8 MHz alternate | Yajingxin | TAXM8M4RLBDDT2T | C720915 | Ext | 46,809 | $0.15 | 20 pF | 250 Ω | ±10 / ±20 ppm |
| **27 MHz (AT7456E)** | YXC | X322527MMB4SI | C5210645 | Ext | 1,106 | $0.09 | **10 pF** | 50 Ω | ±10 / ±20 ppm (API listing; datasheet is image-only) |
| 27 MHz — **oscillator, not a crystal** | SCTF | SX3M27.000M20F30TNN | C2901577 | Ext | 19,123 | $0.30 | — | — | CMOS 1.62–3.63 V XO; could drive CLKIN directly with XFB open |

- 8 MHz load caps for CL = 12 pF: C1 = C2 = 2 × (CL − Cstray). With 3–5 pF stray → 14–18 pF; use **15 pF** (0402 C0G basic C1548) or 18 pF (C1549). Drive level 100 µW typ.
- 27 MHz for AT7456E: no external load capacitors per the MAX7456 datasheet (on-chip Pierce capacitors); crystal CL requirement UNVERIFIED (see section 4). X322527MMB4SI is the only 27 MHz 3225 passive crystal found in stock (1,106).
- KiCad footprint: `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` (pins 1/3 crystal, 2/4 GND for these parts — pad assignment not confirmed from the YXC drawing, UNVERIFIED).
- Sources: https://www.lcsc.com/datasheet/C2973805.pdf , https://www.lcsc.com/datasheet/C5308002.pdf

---

## 17. JST-SH 6-pin 1.0 mm

| Mfr | MPN | LCSC | Stock | Price | Orientation | KiCad 9 footprint |
|---|---|---|---|---|---|---|
| JST | SM06B-SRSS-TB(LF)(SN) | C160405 | **unknown** (null, 2026-11-03) | $0.30 (exact lookup $0.90) | side entry | `Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal` |
| JST | BM06B-SRSS-TB(LF)(SN) | C160392 | **unknown** (null, 2026-11-03) | $0.35 | top entry | `Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical` |
| BOOMELE | 1.0T-6P (right angle) | C145958 | **0** (explicit zero in the category list) | $0.07 | side entry clone | JST SH horizontal (compatibility UNVERIFIED) |
| BOOMELE | 1.0T-6P (vertical) | C145963 | unknown | $0.08 | top entry clone | JST SH vertical (UNVERIFIED) |
| CAX | 1.0T-6P-WT | C722583 | unknown | $0.05 | side entry clone | UNVERIFIED |
| HCTL / XKB / others | A1002WR-S-6P, X1002WRS-06E-LPSWHF, M1010RS-06P… | C239524, C437066, C541848 | unknown | $0.07–0.31 | clones | UNVERIFIED |

**No 6-pin 1.0 mm SH connector (genuine or clone) has a known positive stock in the API today** — the whole wire-to-board 6P/1.0 mm filter returned null stock. Must be checked manually. Source: https://www.lcsc.com/datasheet/C160405.pdf

---

## 18. LEDs and ferrite beads

| Function | Mfr | MPN | LCSC | Lib | Stock | Price | Package |
|---|---|---|---|---|---|---|---|
| Red LED | Hubei Kento | KT-0603R | C2286 | **Basic** | 5,724,023 | $0.007 | 0603 |
| Green LED 0603 | Everlight | 19-217/GHC-YR1S2/3T | C72043 | Ext per API (`is_basic` false today) | unknown | $0.024 | 0603 |
| Green LED 0603 (in stock) | Nationstar | NCD0603G1 | C84267 | Ext | 873,382 | $0.016 | 0603 |
| Green LED 0603 (in stock) | XINGLIGHT | XL-1608UGC-04 | C965804 | Ext | 3,975,282 | $0.005 | 0603 |
| Green LED 0805 | Hubei Kento | KT-0805G | C2297 | **Basic** | 1,694,750 | $0.016 | 0805 |
| Blue LED 0603 | Everlight | 19-217/BHC-ZL1M2RY/3T | C72041 | Ext per API (`is_basic` false today) | unknown | $0.017 | 0603 |
| Blue LED 0603 (in stock) | Nationstar | NCD0603B1 | C84266 | Ext | 351,835 | $0.017 | 0603 |
| Blue LED 0603 (in stock) | XINGLIGHT | XL-1608UBC-04 | C965807 | Ext | 1,759,825 | $0.004 | 0603 |
| Red/Green/Blue 0402 | XINGLIGHT | XL-1005SURC / XL-1005UGC / XL-1005UBC | C25503345 / C965793 / C22355736 | Ext | 920,652 / 1,503,220 / 219,521 | $0.008–0.009 | 0402 |
| Ferrite 120 Ω, 2 A | Murata | BLM18PG121SN1D | C14709 | **Basic** | 1,647,362 | $0.015 | 0603, 50 mΩ |
| Ferrite 600 Ω, 200 mA | Sunlord | GZ1608D601TF | C1002 | **Basic** | 1,404,191 | $0.019 | 0603, 450 mΩ |
| Ferrite 600 Ω, 1.3 A | Murata | BLM18KG601SN1D | C85833 | Ext | 754,531 | $0.026 | 0603, 150 mΩ |
| Ferrite 220 Ω, 1.4 A | Murata | BLM18PG221SN1D | C80165 | Ext | 193,107 | $0.013 | 0603 |

**Surprise:** the only LED colours flagged Basic today are red and white in 0603 (KT-0603R, KT-0603W C2290) and red/green/yellow/white in 0805. The Everlight blue/green 0603 parts long listed as basic (C72041/C72043) return `is_basic: false`. No 0402 LED is basic. LED manufacturer names other than Murata/Sunlord rows are from memory of the MPN prefixes (UNVERIFIED).

---

## 19. Generic passives (JLC basic parts)

All rows below returned `is_basic: true` from the API. Stock is "unknown (null)" for all of them today (observations expired); they are standing basic-library parts.

### Capacitors

| Value | Mfr | MPN | LCSC | Package | Rating |
|---|---|---|---|---|---|
| 100 nF | Samsung | CL05B104KO5NNNC | **C1525** | 0402 | 16 V X7R |
| 100 nF (50 V) | Samsung | CL05B104KB54PNC | C307331 | 0402 | 50 V X7R |
| 1 µF | Samsung | CL05A105KA5NQNC | **C52923** | 0402 | 25 V X5R |
| 2.2 µF | Samsung | CL05A225MQ5NSNC | C12530 | 0402 | 6.3 V X5R |
| 4.7 µF | Samsung | CL10A475KO8NNNC | **C19666** | 0603 | 16 V X5R |
| 4.7 µF | Samsung | CL21A475KAQNNNE | C1779 | 0805 | 25 V X5R |
| 10 µF | Samsung | CL10A106MA8NRNC | **C96446** | 0603 | 25 V X5R |
| 10 µF | Samsung | CL21A106KAYNNNE | **C15850** | 0805 | 25 V X5R |
| 10 µF | Samsung | CL31A106KBHNNNE | C13585 | 1206 | 50 V X5R |
| 22 µF | Samsung | CL21A226MAQNNNE | **C45783** | 0805 | 25 V X5R |
| 22 µF | Samsung | CL31A226KAHNNNE | **C12891** | 1206 | 25 V X5R |
| 10 nF | Samsung | CL05B103KB5NNNC | C15195 | 0402 | 50 V X7R |
| 1 nF | FH | 0402B102K500NT | C1523 | 0402 | 50 V X7R |
| 10 / 12 / 15 / 18 / 20 / 22 pF | Samsung / FH | CL05C100JB5NNNC / 0402CG120J500NT / …150… / …180… / …200… / …220… | C32949 / C1547 / C1548 / C1549 / C1554 / C1555 | 0402 | 50 V C0G |

Note for the buck: 25 V-rated 10 µF/22 µF X5R parts lose much of their capacitance at 17 V bias (input) and some at 5 V (output); TI's design assumes ≥20 µF *effective* on the output (2x22 µF 1206).

### Resistors, 0402 1 % (UniOhm 0402WGF series)

| Value | LCSC | Basic? |
|---|---|---|
| 0 Ω | C17168 | Basic |
| 22 Ω | C25092 | Basic |
| 75 Ω | C25133 (0402WGF750JTCE) | **Extended** (not basic), stock unknown |
| 100 Ω | C25076 | Basic |
| 1 kΩ | C11702 | Basic |
| 1.5 kΩ | C25867 | Basic |
| 2.2 kΩ | C25879 | Basic |
| 4.7 kΩ | C25900 | Basic |
| 5.1 kΩ | C25905 | Basic |
| 10 kΩ | C25744 | Basic |
| 20 kΩ | C25765 | Basic |
| 47 kΩ | C25792 | Basic |
| 51 kΩ | C25794 | Basic |
| 100 kΩ | C25741 | Basic |
| 52.3 kΩ (E96) | C26982 (0402WGF5232TCE) | Extended, stock unknown |
| 105 kΩ (E96) | C25742 (0402WGF1053TCE) | Extended, stock unknown |
| 19.1 kΩ (E96) | C52036 (0402WGF1912TCE) | Extended, stock unknown |

Other basic 0402 values available: 10, 33, 49.9, 120, 200, 220, 330, 470, 510 Ω; 2, 3.3, 12, 15, 22, 33 kΩ; 200 kΩ; 1 MΩ.

- **Buck divider (basic parts only):** 51 kΩ + 1.5 kΩ over 10 kΩ = 5.000 V (section 5).
- **75 Ω video termination is not a basic 0402 part.** Options: accept one extended part (C25133), or 2 x 150 Ω in parallel (150 Ω 0402 basic status not checked).
- Manufacturer names in this section (Samsung "CL…", FH "0402B/0402CG…", UniOhm "0402WGF…") are inferred from MPN prefixes, not from datasheet pages.

---

## Summary of surprises

1. **jlcsearch stock data is partly stale/unknown** — exact-part lookups return null stock; connectors (USB-C, JST-SH, microSD), USBLC6-2SC6, MLT-8530 and all basic passives show "unknown". Manual re-check needed.
2. **Genuine ICM-42688-P: 5 pcs.** High-stock listings are Tokmas/HXY clones. ICM-45686 (1,217, $14) is pin-function compatible; BMI270 (8,303) is the cheap genuine option.
3. **AT7456E is specified 3.15–5.25 V** on AVDD/DVDD/PVDD (3.3 V capable), unlike MAX7456 (4.75–5.25 V).
4. **DPS310, BMP390, INA240A2/A3, INA186, INA199, TSC2010/2012, SMAJ18A, SMF18A, MLT-5020, HNB09A05, STM32F777VIT6: not listed in stock.**
5. **TPS563201 and TPS62130/33 top out at 17 V input** — no margin for 4S.
6. **Shunt land patterns differ between makers** (ASR-M-3/HoLRS: 1.8 x 3.4 pads, span 7.0; TA-I RLM25: 3.1 x 4.0 pads, gap 1.3).
7. **75 Ω 0402 is not a basic part; blue/green 0603 LEDs are no longer flagged basic.**
8. **No microSD socket and no 6-pin JST-SH has both verified stock and a KiCad footprint** per this API today.
9. Buzzers (8530 type) are 3.6 V / 16 Ω parts, not 5 V.
10. AO4407A is weak at low gate drive (2S); AONR21357 (12.3 mΩ at −4.5 V) is the better reverse-polarity FET.
