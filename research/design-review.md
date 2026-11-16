# StackF765 independent design review (schematic level)

Reviewed 2026-11-16. Scope: `build/{lower,upper,service}/*.net`, `gen/*.py`, `firmware/hwdef/StackF765/*`, `research/*.md`.
No project file was modified; this file is the only output.

## How things were checked (evidence classes)

- **[DS]** = read in the manufacturer datasheet text during this review (TI PDFs downloaded and converted with `pdftotext`):
  LM66200 (SLVSG04), TPS62933 (SLUSEA4D), TLV755P (SBVS320D), INA21x (SBOS437K), TPS7A20.
- **[AP]** = checked against the ArduPilot tree that was used for the build (`/root/fcclaude-build/ardupilot`, commit a995235, 2026-10-11),
  its `STM32F767xx.py` pin table, `chibios_hwdef.py`, the in-tree `MatekF765-Wing` hwdef, and `firmware/bin/hwdef.generated.h`.
- **[NET]** = read from the KiCad netlists (a per-component pin/net dump of all three boards was produced and read in full).
- **[MEM]** = from my own knowledge of the datasheet; the ST (STM32F765), TDK (ICM-42688-P), Bosch and AT7456E PDFs could **not** be
  re-fetched in this session (st.com timed out, TDK returned HTML). For those parts I relied on `research/parts.md`, the KiCad
  library symbol (generated from ST data), ArduPilot's pin tables and memory. Treat [MEM] items as "not independently re-verified".

Severity: **BLOCKER** = will not work / will be damaged / cannot be fabricated as is. **SHOULD-FIX** = real risk of damage or
marginal operation, cheap to fix now. **NOTE** = awareness, bring-up or optional improvement.

## Summary

No schematic-level wiring error was found: every IC pin number matches its datasheet function, every MCU signal is on a pin that
has the claimed alternate function, the connectors are consistent between boards, and the hwdef matches the netlist.
The two blockers are about project state, not the circuit. The should-fix items are all about margins (transients, thermal, fault tolerance).

| # | Sev | One-line |
|---|---|---|
| B1 | BLOCKER | Upper-board PCB is not finished: 159 unconnected items, no `fab/upper` |
| B2 | BLOCKER (firmware artefact) | `firmware/bin/*` was built with `BARO DPS310`; hardware and current hwdef are BMP388 |
| S1 | SHOULD-FIX | INA214 inputs (abs max 26 V) sit behind a TVS that clamps at 29.2 V; 10 ohm does not limit the current |
| S2 | SHOULD-FIX | 25 V 0805 X5R input capacitors on a 17 V bus that is clamped at 29 V; little effective capacitance |
| S3 | SHOULD-FIX | TLV75533 in SOT-23-5 dissipates ~0.35-0.7 W; junction temperature marginal |
| S4 | SHOULD-FIX | BUZ_OUT leaves the FC with no current limit: a cable short collapses +5V_SYS; R3 is under-rated |
| S5 | SHOULD-FIX | USB VBUS goes straight into LM66200 (abs max 6 V) with no clamp below 6 V and no fuse |
| S6 | SHOULD-FIX (if 3 A is really needed) | 4.7 uH instead of TI's 6.8 uH: peak current close to the minimum current limit |
| N1-N20 | NOTE | see below |

---

## BLOCKER

### B1. Upper board layout is incomplete (outside schematic scope, but it stops fabrication)
- Evidence: `build/upper/summary.json` -> `"unconnected": 159`; `build/upper/upper-drc.json` lists 159 unconnected items
  (+3V3 25, +5V_SYS 22, +3V3_SENS 13, +5V 12, VDDA 4, and one or two each on most signal nets: TXn/RXn, M1-M5, SDA/SCL, OSC_IN/OUT,
  NRST, BOOT0, VBAT_ADC, CURR_ADC ...). `build/upper/route.log` shows the router failing 6 and then 11 nets.
  There is `fab/lower` and `fab/service` but no `fab/upper`.
- Fix: finish routing / zone fill and get DRC to 0 unconnected before generating upper-board fabrication data. (Lower and service: DRC and ERC clean.)
- Also note for layout: the router config gives `+5V` on the upper board a 0.4 mm track. That net feeds eight "5V" header pins
  (camera, VTX, GPS, receivers) from the board-to-board connector - up to ~2-3 A. 0.4 mm of 1 oz copper is good for roughly 1 A. Use a pour or >= 1.2 mm.

### B2. The firmware binaries in `firmware/bin` do not match the hardware (barometer)
- Evidence [AP]: `firmware/bin/hwdef.generated.h` line 233: `HAL_BARO_PROBE1 probe_i2c_dev(AP_Baro_DPS310::probe, 0, 118)`.
  The hwdef copy inside the build tree has `BARO DPS310 I2C:0:0x76`; `firmware/hwdef/StackF765/hwdef.dat` (edited 06:22, after the 05:35 build)
  has `BARO BMP388 I2C:0:0x76`, and U3 on the board is a BMP388. Only that one line differs (`diff` run).
- Effect: the existing `arducopter.apj/.bin/_with_bl.hex` will not find a barometer; ArduPilot then stops in its
  "Baro: unable to initialise driver" config-error loop and never finishes booting.
- Fix: re-run `firmware/build.sh`. The bootloader (`StackF765_bl.bin`, 16 268 bytes, fits the 32 KB sector 0) is unaffected; hwdef-bl is unchanged.
- `BARO BMP388 I2C:0:0x76` is valid syntax (11 in-tree boards use exactly this line).

---

## SHOULD-FIX

### S1. INA214 (lower U3) input over-voltage during a TVS clamp event
- Nets/refs: VBAT/VESC -> NT1/NT2 -> R2/R3 (10R) -> INA_P/INA_N -> U3 pins 4/5; D1 SMBJ18CA on VESC.
- Evidence [DS]: INA21x abs max, version A: common-mode GND-0.3 V to **26 V**; note 3: "Input voltage at any terminal may exceed
  the voltage shown if the current at that pin is limited to 5 mA". SMBJ18CA: stand-off 18 V, breakdown ~20-22 V, clamp 29.2 V (parts.md).
  10 ohm cannot limit to 5 mA with 3 V of overdrive. INA21x datasheet section 6.4.4 "Using the INA21x with common-mode transients above 26 V"
  shows exactly the missing parts: the 10 ohm resistors **plus a zener / transzorb at each input**.
- When it happens: battery hot-plug ringing with long leads and ceramic-only input capacitance, or ESC regenerative braking on 4S.
- Fix (any one): (a) add a small zener or TVS from INA_P to GND and INA_N to GND (after R2/R3), breakdown 20-24 V, e.g. BZT52C22 / SOD-523 parts,
  as in datasheet Fig. 6-5; (b) use a 40 V-class amplifier with the same SC-70 pinout (INA190A2, 50 V/V, is in parts.md stock list -
  needs HAL_BATT_CURR_SCALE 40 or a 1 mohm shunt); (c) at minimum document "4S only with ESC bulk capacitor fitted".

### S2. Input capacitors C10, C11, C20, C21 (10 uF 25 V X5R 0805) on VESC
- Evidence [DS] TPS62933 10.2.2.9: "The capacitor voltage rating needs to be greater than the maximum input voltage ... must also be selected
  with the DC bias taken into account"; TI's own example uses 10 uF **50 V 1206 X7R** and still gets only 3.45 uF effective each at 24 V.
  A 25 V 0805 X5R 10 uF at 17 V bias keeps roughly a quarter of its value (my estimate, not a datasheet figure) -> about 5 uF per regulator.
  The bus is allowed to reach 29 V before D1 clamps, i.e. above the capacitors' rating.
- Fix: CL31A106KBHNNNE 10 uF 50 V 1206 (C13585, already listed as basic in parts.md) x2 per regulator, and consider a footprint for a
  35 V bulk electrolytic/polymer across VESC (it also damps the hot-plug ringing behind S1). The 100 nF 50 V parts (C12, C22, C3) are fine.

### S3. 3.3 V main LDO U6 (TLV75533PDBVR) thermal margin
- Evidence [DS] TLV755P thermal table, DBV: RthetaJA **231.1 C/W (JEDEC)**, **100.8 C/W (TI EVM)**; recommended Tj max 125 C; shutdown ~165 C.
- Load estimate (mine): STM32F765 at 216 MHz ~150-220 mA, microSD 30-100 mA (peaks higher), LEDs/INA/pull-ups ~5 mA -> 0.2-0.35 A typical, 0.4 A peak.
  P = (5.06 - 3.3) V x I = 0.35 W at 0.2 A, 0.62 W at 0.35 A. Rise: +35...+62 C with EVM-class copper, +80...+140 C with JEDEC-class copper.
  The LDO sits on a small board directly above two 3 A bucks and a 1.25 W shunt, so ambient is not 25 C.
- Fix (pick one): (a) TLV75533P**DYD** - same SOT-23-5 pinout/footprint, RthetaJA 60.3 C/W on the EVM [DS]; (b) give U6 pins 2 (GND) and 1/5
  generous copper and vias to the planes; (c) replace with a small 3.3 V buck. Measure case temperature at bring-up with SD logging running.
- U7 (TPS7A2033, < 5 mA load) has no thermal issue.

### S4. Buzzer output: no fault limiting on the FC side, and R3 rating
- Refs: upper Q2 (AO3401A) S=+5V_SYS, D=BUZ_OUT -> J5 pin 5 -> cable -> service R3 (10R 0805 1/8 W) -> BZ1 (16 ohm), D1 across BZ1.
- Problem 1: the only series resistance is on the service board. A pinched cable or a short of BUZ_OUT to GND/frame while a tone plays
  connects +5V_SYS to ground through ~50-60 mohm: +5V_SYS collapses and the flight controller resets (LM66200 pulsed limit is 4 A [DS]).
  Fix: put the series resistor on the upper board between Q2 drain and J5 pin 5 (or add a second one there), so a cable short draws <= 0.5 A.
- Problem 2: R3 dissipation. I = 5 V / (10 + 16) = 190 mA -> 0.37 W while on; ~0.18 W average at 50 % duty; 0.37 W if the pin is ever stuck high.
  The part in `parts.py` is a 1/8 W 0805 (0805W8F100JT5E). Fix: 1206 / 0.25 W or better, or 2 x 22R 0805 in parallel. The buzzer itself sees
  3.1 V peak (rated 3.6 V) - fine.
- Everything else about the driver is correct, see "Verified".

### S5. USB VBUS path into U5 (LM66200)
- Evidence [DS]: LM66200 abs max VIN1/VIN2/VOUT **6 V**, recommended 1.6-5.5 V. VBUS reaches U5 pin 6 through the service cable with only
  1 uF + 1 uF ceramic (service C1, upper C2) and the USBLC6-2SC6 VBUS pin as protection. The USBLC6 VBUS clamp only starts above ~6 V and
  clamps at 12-17 V [MEM], so it does not keep VIN2 under 6 V. Hot-plugging a cable into low-ESR ceramics can overshoot towards 2 x VBUS.
  There is no fuse/PTC: a short on the 6-wire cable is limited only by the host.
- Fix: add a 5 V uni-directional TVS (e.g. SMF5.0A / PESD5V0 class) or a 5.6 V zener + 1-2 ohm (or ferrite) at J5 pin 1 on the upper board;
  optionally a 500 mA PTC on the service board. Total VBUS-side capacitance (2 uF) and inrush are otherwise fine (see Verified).

### S6. Buck inductor value (L1, L2 = 4.7 uH, SXN SMMS0530-4R7M, Isat 5 A)
- Evidence [DS] TPS62933 Table 10-2: for 5 V at 500 kHz, typical L = **6.8 uH** (4.7 uH is the 3.3 V row); design text uses K = 0.4.
  IHS_LIMIT = 4.2 A min / 5 A typ / 5.8 A max [DS]; "the inductor saturation current must not be less than the maximum peak inductor current",
  ideally >= the HS limit.
- Numbers (mine): ripple at 17 V in = 5 x (1 - 5/17) / (4.7 uH x 500 kHz) = 1.50 A p-p (K = 0.5); with -20 % tolerance 1.88 A.
  Peak at 3 A load = 3.75-3.94 A, against a 4.2 A minimum limit and a 5 A (30 %-drop) saturation rating; hot inductors saturate earlier.
- It works at up to ~2.5 A. For a true 3 A rating: fit a 6.8 uH part with Isat >= 5.8 A, or add an RT resistor for ~700-800 kHz
  (RT is currently open = 500 kHz, [DS] "Floating > 280 kohm = 500 kHz"). Otherwise label the rails 2.5 A.

---

## NOTE

- **N1. TPS62933 EN (U1/U2 pin 2) floats.** Allowed: "Driving EN high or leaving this pin floating enables the converter" [DS], internal pull-up 0.7 uA.
  That is a megohm-impedance node: flux residue or condensation leaking > ~1 uA to ground would shut the 5 V rail off in flight.
  Either conformal-coat / keep the pad guarded, or add a divider VESC-100k-EN-33k-GND (turn-on <= 5.2 V, EN = 4.2 V at 17 V, 5.5 V at 22 V;
  EN abs max is 6 V [DS], so never tie EN straight to VIN). RT floating and SS = 33 nF ("approximately 5 ms"; SS must not float) are per datasheet.
- **N2. Current-sense gain error from R2/R3.** [DS] section 6.4.1: series resistors change the gain; with INA214 (internal 10 k) and 10 ohm the factor is
  12.5e6 / 12.6125e6 = 0.991, i.e. the reading is 0.9 % low. Compensate with BATT_AMP_PERVLT = 20.18 or accept (shunt is 1 %, gain 1 %).
- **N3. Zero-current offset.** INA214 output swing to GND is 5 mV typ / 50 mV max [DS] with REF = GND, i.e. up to 1 A of indicated current at rest
  and a small dead zone. Set BATT_AMP_OFFSET at bring-up.
- **N4. Full scale.** 3.3 V / 50 mV/A = 66 A (output swings to V+ - 50...200 mV, so ~62-65 A usable). Bursts above that clip.
- **N5. ROM DFU pins.** The STM32F7 system bootloader also listens on USART1 (PA10 = RX1 header pin) and USART3 (PB11 = BARO_SDA, PC11 = SD_D3) and
  I2C1 (PB6 / PB9 = BUZZER) [MEM, AN2606]. PB9 is held low by R12 and BARO_SDA high by R7, so those are benign. A talking device on RX1
  while the BOOT button is used can capture the bootloader; unplug RX1 for DFU. Normal updates go through the ArduPilot bootloader and do not need BOOT.
- **N6. BOOT0 level.** VBUS 5 V x 10k/(10k+10k) = 2.5 V (2.2 V at VBUS 4.4 V); above the BOOT0 VIH (~0.17 VDD + 0.7 V = 1.26 V [MEM]) and far below
  the pin's rating. The button only works when USB is plugged in (by design). R1 keeps BOOT0 low when the service board is absent.
- **N7. AT7456E SDOUT at 5 V into PB14.** PB14 is an FT (5 V-tolerant) pin [MEM; same pin is SPI2_MISO on many 5 V-OSD boards]. Tolerance requires the
  internal pull-up/down to be off: `chibios_hwdef.py get_PUPDR_value` leaves SPI MISO pins FLOATING [AP]. Do not add PULLUP to PB14 in the hwdef.
  CS/SCLK/SDIN at 3.3 V meet VIH 2.0 V (parts.md).
- **N8. LEDs.** Blue (and InGaN green) LEDs have Vf ~2.8-3.1 V; from 3.3 V through 1 k (upper R2, R3) the current is 0.2-0.5 mA. Visible but dim,
  and unit-to-unit variable. 330 ohm would be safer.
- **N9. Board-to-board current.** +5V uses 4 pins (15-18), GND 6 pins (1, 2, 10, 14, 19, 20). 1.27 mm headers are normally rated about 1 A per pin;
  I could not confirm the 2 A figure for HCTL PM127/PZ127 (datasheet not opened). 3 A / 4 pins = 0.75 A per pin: acceptable, no margin for uneven sharing.
  Signal return currents of six ESC signals share those 6 GND pins - fine.
- **N10. No reverse-polarity protection** (stated on the schematic). A reversed battery forward-biases the buck FET body diodes and takes
  INA214 inputs to -17 V (abs min -0.3 V): U1, U2, U3 will be destroyed. The bidirectional TVS does not help. Make the silkscreen polarity unmistakable.
- **N11. Lower-board heat.** TPS62933 RthetaJA is 60 C/W on TI's 2-layer 2-oz EVM [DS]; each regulator loses roughly 1 W at 3 A, the shunt 1.25 W at 50 A,
  plus copper loss, all on 31.5 x 48 mm under the upper board. Both rails at 3 A continuously with 50 A flowing is not realistic without airflow.
  Specify 2 oz copper for the lower board if the 50 A figure is to be kept.
- **N12. No ESD/series protection** on header signals (UART, I2C, CAM, VTX, motor, LED). Normal for this class of board; handle accordingly.
- **N13. Service cable must be 1:1.** A reversed 6-pin JST-SH cable puts VBUS on BOOT0 and BUZ_OUT (5 V pulses) on USB D-. Mark pin 1 at both ends.
- **N14. Buzzer footprint polarity.** `MagneticBuzzer_CUI_CMT-8504-100-SMT` pad 1 = BUZ_P, pad 2 = GND; which physical corner of the MLT-8530 / KLJ-8530
  is "+" was flagged UNVERIFIED in parts.md and I could not verify it either. Wrong polarity still sounds but quieter.
- **N15. Test access.** Upper: TP for +3V3, GND, +5V_SYS, SWDIO, SWCLK, NRST. Missing and useful: +3V3_SENS, +5V, VBAT_ADC/CURR_ADC. Lower: none
  (+5V, +5V_PI are reachable on J2). No reset button (NRST pad only).
- **N16. LED strip level.** PA8 drives 3.3 V logic into a 5 V WS2812 (VIH 0.7 x VDD = 3.5 V). Usually works; if not, power the first LED via a diode.
- **N17. PC5 IMU1_INT** is declared `INPUT` with no pull while the ICM-42688 INT1 pad may be open-drain after reset [MEM]. Unused by ArduPilot; harmless.
- **N18. ICM-42688 pin 9 (INT2/FSYNC/CLKIN) tied to GND.** Correct for "FSYNC unused" (parts.md, TDK table). ArduPilot only reprograms pin 9 when
  `INVENSENSEV3_CLKIN_BITMASK` is defined [AP]; do not define it on this board.
- **N19. USB-only operation.** On USB the "5V" header pins and the lower board are unpowered (by design); MCU TX pins will idle high into unpowered peripherals.
- **N20. Clone parts.** parts.md notes genuine ICM-42688-P stock is 5 pcs; Tokmas/HXY parts are untested with the ArduPilot Invensensev3 driver.

---

## Verified as correct (what was actually checked)

### IC pin numbers vs datasheet function [NET] against [DS] unless marked
| Ref | Part | Result |
|---|---|---|
| lower U1, U2 | TPS62933DRLR | 1 RT (open), 2 EN (open), 3 VIN=VESC, 4 GND, 5 SW, 6 BST, 7 SS, 8 FB - matches [DS] Fig. 7-1. Plain TPS62933 has SS on pin 7 (the "P"/"O" variants have PG there - do not substitute). |
| lower U3 | INA214AIDCKR | 1 REF=GND, 2 GND, 3 V+=+3V3, 4 IN+=INA_P (battery side), 5 IN-=INA_N (ESC side), 6 OUT - matches [DS]; "IN+ connect to supply side of shunt". |
| upper U5 | LM66200DRLR | 1,5 GND; 2,7 VOUT=+5V_SYS; 3 VIN1=+5V; 6 VIN2=VBUS; 4 ON=GND ("Device is enabled when ON is pulled low"); 8 ST open (open-drain output, unused) - matches [DS]. |
| upper U6 | TLV75533PDBVR | 1 IN, 2 GND, 3 EN=IN, 4 NC, 5 OUT - matches [DS]. 1 uF in, 1 uF + 10 uF out. |
| upper U7 | TPS7A2033PDBVR | 1 IN, 2 GND, 3 EN=IN (needed: EN has a 500 k pull-down [DS]), 4 NC, 5 OUT - matches [DS]. |
| upper U2 | ICM-42688-P | 1 SDO, 4 INT1, 5 VDDIO, 6 GND, 7 GND, 8 VDD, 9 GND, 12 CS, 13 SCLK, 14 SDI; 2/3/10/11 open - matches the TDK table in parts.md [MEM agrees]. 100 nF + 2.2 uF on VDD, 100 nF on VDDIO. |
| upper U3 | BMP388 | 1 VDDIO, 2 SCK, 3/8/9 VSS, 4 SDI, 5 SDO=GND (addr 0x76), 6 CSB=VDDIO (I2C), 7 INT open, 10 VDD - matches Bosch table in parts.md [MEM agrees]. No pin floats that must not. |
| upper U4 | AT7456E | 3 DVDD, 4 DGND, 5 CLKIN, 6 XFB, 8 CS, 9 SDIN, 10 SCLK, 11 SDOUT, 19 RESET=+5V_SYS, 20 AGND, 21 AVDD, 22 VIN, 23 PGND, 24 PVDD, 25 SAG=VOUT, 26 VOUT, EP=GND; 7/12/13/17/18 open (open-drain or outputs) - matches MAX7456 TSSOP-28 pinout [MEM] and parts.md. 3 x 100 nF + 4.7 uF. Supply 5.06 V < 5.25 V max. |
| service U1 | USBLC6-2SC6 | 1,6 = D+; 3,4 = D-; 2 GND; 5 VBUS - consistent [MEM]. |
| upper Q1/Q2 | 2N7002 / AO3401A | SOT-23 1 G, 2 S, 3 D for both [MEM]. |
| LEDs, D1 | | upper D1/D2: A to resistor/+3V3, K to MCU pin (active low, matches hwdef). lower D2: A via R6 to +5V, K GND. service D1: K=BUZ_P, A=GND (correct flyback direction for a high-side switch). |

### STM32F765VIT6 (U1) [NET] + [AP] (+ KiCad library symbol for pin numbers)
- 100 pins in the netlist, **no PDR_ON, no VDDUSB/VDDSDMMC pin** on this package (confirmed: none present in the ST-derived symbol).
- Power: VDD 11, 27, 50, 75, 100 -> +3V3; VSS 10, 26, 49, 74, 99 -> GND; VSSA 19 GND; VREF+ 20 and VDDA 21 -> VDDA (FB1 + 1 uF + 100 nF);
  VBAT 6 -> +3V3 (+100 nF); VCAP_1 48 and VCAP_2 73 -> 2.2 uF each; NRST 14 -> 100 nF + pad; BOOT0 94 -> 10 k to GND; PH0/PH1 12/13 -> 8 MHz + 2 x 15 pF.
- Decoupling: 5 x 100 nF (one per VDD pin by placement table) + 4.7 uF + 10 uF on the +3V3 rail: adequate.
- Crystal: CL 12 pF with 2 x 15 pF and 3-5 pF stray -> 10.5-12.5 pF. OK.
- Alternate functions: every pin in `pinmap.py` exists with that function in ArduPilot's `STM32F767xx.py` (the hwdef generator refuses unknown
  functions and the build completed): USART1 PA9/PA10, USART2 PD5/PD6, USART3 PD8/PD9, UART4 PD1/PD0, USART6 PC6/PC7, UART7 PE8/PE7, UART8 PE1/PE0,
  SPI1 PA5/6/7, SPI2 PB13/14/15, I2C1 PB6/PB7, I2C2 PB10/PB11, SDMMC1 PC8-PC12 + PD2, TIM2_CH1/2 PA0/PA1 (AF1), TIM5_CH3/4 PA2/PA3 (AF2),
  TIM8_CH2N/3N PB0/PB1 (AF3), TIM1_CH1 PA8 (AF1), TIM11_CH1 PB9 (AF3), ADC1 IN12/IN13 on PC2/PC3, OTG_FS PA11 (DM) / PA12 (DP), SWD PA13/PA14.
  The same assignments for PA9/PA10, PB9 ALARM and PB0/PB1 TIM8_CHxN are used by the in-tree MatekF765-Wing board.
- Not re-verified against the ST PDF: I/O structure (FT) of individual pins, BOOT0 thresholds. [MEM]

### Buck regulators [DS]
- Vout = 0.8 x (1 + 53.2k/10k) = 5.056 V (TI table: 52.5k/10k for 5.00 V). With 1 % resistors and the 788-812 mV reference: about 4.96-5.15 V.
  Inside every downstream limit (LM66200 5.5 V, LDOs 5.5/6 V, AT7456E 5.25 V).
- BST 100 nF 16 V ("must have a 16 V or higher rating") OK. SS 33 nF OK. RT open = 500 kHz OK. EN open = on OK (see N1).
- Output 2 x 22 uF 25 V 0805 + 100 nF: about 20-25 uF effective at 5 V (estimate) vs TI typical 20 uF / minimum 10 uF effective. OK.
- VIN abs max 32 V vs TVS clamp 29.2 V: OK. Minimum input 6 V: OK (98 % max duty).

### Sensing
- Current: 0.5 mohm x 100 V/V = 50 mV/A -> 20 A/V = `HAL_BATT_CURR_SCALE 20.0`. Direction correct (IN+ on VBAT). The regulators are fed from VESC,
  i.e. downstream of the shunt, so the FC's own current is measured. Common mode 16.8 V < 26 V in normal operation. Kelvin taps via NT1/NT2 into
  10R/10R/100 nF differential filter: concept correct. Shunt 1.25 W at 50 A in a 6 W part.
- Voltage: R4 10k / R5 1k from VBAT (battery side) = 11:1 = `HAL_BATT_VOLT_SCALE 11.0`; 1.53 V at 16.8 V. If R5 opens, (17 - 3.6)/11k = 1.2 mA into PC2 - survivable.
- ADC pins: PC2 = ADC1_IN12, PC3 = IN13 = `HAL_BATT_VOLT_PIN 12`, `HAL_BATT_CURR_PIN 13`; 1k/100n filters at the MCU; INA output isolated from the 100 nF by R15.

### Buzzer driver
- PB9 high -> Q1 on -> BUZ_G low -> Q2 on (Vgs = -5 V, within +-12 V) -> BUZ_OUT = 5 V. PB9 low or floating (reset, bootloader, ROM DFU): R12 holds Q1 off,
  R13 holds Q2 off -> buzzer off. ArduPilot `ALARM` on TIM11_CH1 generates active-high PWM and idles low [AP: HAL_PWM_ALARM generated] -> polarity correct.
- 2N7002 at 3.3 V gate drive only has to sink 0.5 mA: OK. Gate RC (10 k x ~1 nF) is ~10 us against a 370 us period: OK.

### USB and power paths
- CC1 and CC2 each have their own 5.1 k to GND. D+ (A6/B6) and D- (A7/B7) are paired correctly. Naming is consistent end to end:
  J1 D- -> USB_DM -> U1 I/O2 -> J2 pin 2 -> cable -> J5 pin 2 -> PA11 (OTG_FS_DM); D+ -> pin 3 -> PA12 (OTG_FS_DP). `tools/check_stack.py` passes.
- USB alone: VBUS -> U5 -> +5V_SYS -> U6/U7/OSD: board runs; +5V stays off (LM66200 blocks reverse current, [DS] VRCB 42 mV typ).
  Battery alone: +5V -> U5 -> +5V_SYS; VBUS not back-fed. Both: higher input wins, no cross-conduction path. Header "4V5" pins A2/B2 are +5V_SYS.
- USB inrush: about 27 uF on +5V_SYS, LM66200 soft-start 1.7 ms at 5 V [DS] -> I = C x V / t = ~80 mA. Fine. VBUS-side capacitance 2 uF (< 10 uF limit).
- No VBUS-sense pin: same as MatekF765-Wing (PA9 used as USART1_TX) [AP].

### Connectors
- B2B: both boards take the pin map from the same `B2B` dict; netlists agree pin for pin (1,2 GND; 3-8 M1-M6; 9 LED_STRIP; 10 GND; 11 VBAT_SENSE;
  12 CURR_SENSE; 13 +3V3; 14 GND; 15-18 +5V; 19,20 GND). `tools/check_stack.py` (run during this review): all 20 header pads sit over the same-numbered
  socket pad (worst 0.15 mm) with identical nets - so there is no mirror error between top-mounted socket and bottom-mounted header.
- Lower J2: odd pins M1-M6, LED_STRIP, +5V, +5V_PI, +5V_PI; all even pins GND - matches `J2` table and silk labels.
- Upper J1 3x12: netlist matches `J1_ROWS` and labels; all UART RX pins land on the right MCU pins (checked each: A3/A4 PA9/PA10 ... C11/C12 PE1/PE0).
- Service cable: 1 VBUS, 2 D-, 3 D+, 4 GND, 5 BUZ, 6 BOOT identical at J5 (upper) and J2 (service).
- microSD J4: 1 DAT2, 2 DAT3, 3 CMD, 4 VDD, 5 CLK, 6 VSS, 7 DAT0, 8 DAT1, shield GND; detect pins unused. Pull-ups are internal (generator adds PULLUP on SDMMC D0-D3/CMD [AP]).

### hwdef [AP]
- Matches the netlist pin for pin: `tools/check_hwdef.py` run during this review -> "PASS: 49 MCU pins consistent between hwdef.dat,
  pinmap.py and the KiCad schematic"; I also read the hwdef against the netlist dump myself and found no difference.
- `MCU STM32F7xx STM32F767xx`, 8 MHz, 2048 KB, `FLASH_RESERVE_START_KB 96` + `STORAGE_FLASH_PAGE 1` (sectors 1-2, 32 KB each; bootloader in sector 0),
  `STM32_ST_USE_TIMER 12`: same scheme as MatekF765-Wing. TIM12 is not used for anything else.
- I2C_ORDER I2C2 I2C1 -> bus 0 = I2C2 = barometer, `HAL_I2C_INTERNAL_MASK 1` correct; external compass probing uses `AP_COMPASS_PROBING_ENABLED 1`,
  which is the switch this ArduPilot version uses (`AP_Compass_config.h`).
- IMU: `Invensensev3 SPI:icm42688`, MODE3, 2/16 MHz. OSD: `SPIDEV osd SPI2 DEVID4 MAX7456_CS MODE0 10 MHz`, `HAL_WITH_SPI_OSD 1` generated, fonts in ROMFS.
- DMA map resolved by the generator with only two shares (TIM5_UP/TIM5_CH3, and SPI2_RX/UART7_TX); ADC1, SDMMC1, SPI1, SPI2, TIM1/2/5/8_UP,
  USART1 and UART7 all got streams. BIDIR on PA0 and PA2 got their capture streams.
- LEDs active low (`OUTPUT LOW`, default `HAL_GPIO_LED_ON 0`); bootloader LED PD10 consistent.
- Storage, SD (`HAL_OS_FATFS_IO 1`), battery defaults present. Nothing else found that would stop boot, apart from B2.
- Still to do on the bench: IMU `ROTATION_NONE` vs actual placement (already flagged in the hwdef), official APJ_BOARD_ID before distribution.

## Not checked
- Copper: trace widths, Kelvin tap geometry, switch-node layout, plane splits, thermal relief (only DRC summaries and the stack check were looked at).
- Footprint land patterns and 3D heights (see research/footprints.md, mechanical.md - read only for context).
- ST, TDK, Bosch, AT7456E, USBLC6, MOSFET, connector and buzzer datasheets were not re-opened in this session (marked [MEM] above).
- Stock/sourcing.
