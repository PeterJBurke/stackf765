# How StackF765 works

This page explains each circuit, with the numbers behind the part values.
Reference designators match the schematics (`docs/boards/*/*-schematic.pdf`).

## The three boards

| Board | Job | Layers | Size |
|---|---|---|---|
| **Upper** | Flight controller: MCU, sensors, OSD, microSD, 3 × 12 header | 6 | 31.5 × 48 mm |
| **Lower** | Power: battery/ESC pads, current and voltage sensing, two 5 V regulators, 2 × 10 header | 4 (2 oz outer) | 31.5 × 48 mm |
| **Service** | USB-C socket, buzzer, BOOT button, on a 6-wire cable | 2 | 18 × 32 mm |

The lower board mounts to the frame on four rubber grommets (20 × 20 mm pattern).
The upper board plugs into it through a 20-pin 1.27 mm connector and is held by
three soldered M2 standoffs, 6.0 mm tall. The two boards therefore move as one
rigid block on the grommets.

Signals that cross between the boards (connector J1 lower / J3 upper):

| Column (left → right, top view) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Row nearest the header | GND | M1 | M3 | M5 | LED | VBAT_SENSE | +3V3 | +5V | +5V | GND |
| Other row | GND | M2 | M4 | M6 | GND | CURR_SENSE | GND | +5V | +5V | GND |

## Lower board

### Battery path and current sensing

Battery + is soldered to pad **BAT+**, passes through shunt **R1** (0.5 mΩ) and
leaves on pad **ESC+**. The two ground pads are joined by copper on all four
layers. Everything on the flight controller is fed from the ESC+ side of the
shunt, so the current reading includes the flight controller itself.

* Shunt voltage at 50 A: 50 A × 0.5 mΩ = 25 mV. Shunt dissipation: 50² × 0.0005 = **1.25 W** (part rated 6 W).
* Amplifier **U3** (INA214, gain 100): 2.5 V at 50 A, i.e. **50 mV per amp**. ArduPilot's
  `BATT_AMP_PERVLT` is therefore 20 A/V. Full scale (3.3 V) is 66 A.
* **NT1/NT2** are Kelvin taps: the amplifier's sense lines leave from the inner edges of the
  shunt pads, so voltage dropped in the high-current copper is not measured.
* **R2/R3** (10 Ω) with **C3** (100 nF) filter switching noise. They make the reading about 0.9 % low;
  calibrate `BATT_AMP_PERVLT` against a known current.

### Battery voltage sensing

**R4/R5** divide the battery voltage by 11 (10 kΩ over 1 kΩ): 8.4 V (2S full) reads 0.76 V,
12.6 V (3S full) reads 1.15 V. ArduPilot's `BATT_VOLT_MULT` is 11.0.

### Input protection and voltage range

**D1** (SMBJ15CA) clamps spikes from wiring inductance to 24.4 V or less. That keeps the
current-sense amplifier (26 V limit), the regulators (30 V) and the 25 V capacitors inside
their ratings. Its 15 V stand-off is why the board is rated **2S–3S (6–13 V)** and not 4S.

There is **no reverse-polarity protection**. Connecting the battery backwards will destroy
the regulators. Check polarity before the first connection.

### 5 V regulators

**U1** makes `+5V` for the flight controller and its peripherals. **U2** makes `+5V_PI`
for a companion computer on header J2. They are identical TPS62933 buck converters, so a
brown-out or noise on the companion's rail cannot reset the flight controller.

* Output voltage: 0.8 V × (1 + (51 k + 2.2 k) / 10 k) = **5.06 V**.
* Switching frequency 500 kHz (RT pin open). Inductor 4.7 µH, 5 A saturation.
* Ripple current at 8.4 V in: 5.06 × (1 − 5.06/8.4) / (4.7 µH × 500 kHz) = 0.86 A peak-to-peak,
  so the peak at 3 A load is 3.4 A, below the 4.2 A minimum current limit and the 5 A inductor rating.
  At 12.6 V in the peak is 3.65 A.
* Dropout: the converter reaches 98 % duty cycle, so it holds 5 V down to about 5.6 V in at full load.
* **Rating: 3 A per rail.** The header pins themselves limit each 5 V pin to about 3 A.

### Copper for 50 A

The BAT+ → shunt and shunt → ESC+ paths are 5 mm long and 5–6 mm wide on four layers
(2 oz outer, pads stitched with twelve vias each). The ground return between the two
ground pads is the longest high-current path: about 7.5 mm between pad centres, roughly
0.15 mΩ with 2 oz outer copper, i.e. about 0.4 W at 50 A. With the shunt this adds up to
roughly 1.7 W in the rear third of the lower board at 50 A continuous; in a multirotor
that area sits in prop wash. Measure the temperature rise during bring-up (see
[bringup.md](bringup.md)).

## Upper board

### Power

* **U5** (LM66200) is a dual ideal diode. It connects whichever of `+5V` (battery) and
  `VBUS` (USB) is higher to `+5V_SYS` and blocks current flowing backwards. The board
  runs from USB alone, from the battery alone, or both, and USB never back-feeds the battery rail.
  **D3** clamps spikes on VBUS.
* Header pins labelled **5V** come straight from the battery regulator. Pins labelled **4V5**
  come from `+5V_SYS`, so they are also live on USB.
* **U6** (TLV75533) makes `+3V3` for the MCU, microSD and pull-ups. **R16‖R17** (2.35 Ω) in its
  input share the heat: at 250 mA they drop 0.6 V and dissipate 0.15 W, leaving 0.28 W in U6
  instead of 0.43 W.
* **U7** (TPS7A2033, 7 µV noise) makes a separate quiet `+3V3_SENS` for the IMU and barometer.

### Microcontroller

STM32F765VIT6 with an 8 MHz crystal (two 15 pF load capacitors for a 12 pF crystal),
one 100 nF capacitor at every supply pin, 2.2 µF on each VCAP pin, and a ferrite-filtered
analog supply. The complete pin assignment is in [pinout.md](pinout.md) and
`gen/pinmap.py`; it follows the proven Matek F765 allocation so the timers and DMA
channels are known to work in ArduPilot.

### Sensors

* **U2** ICM-45686 IMU on SPI1 (the ICM-42688-P fits the same footprint and is detected automatically).
  It sits on the top side near the front-right corner. Board orientation in firmware:
  `ROTATION_ROLL_180_YAW_90` — confirm this on the bench.
* **U3** BMP388 barometer on I2C2, address 0x76. Cover it with a small piece of open-cell foam
  in an aircraft to shield it from prop wash and light.

### On-screen display

**U4** (AT7456E) overlays text on analog video. Camera video enters on header pin `CAM`,
is terminated with 75 Ω (R10) and AC-coupled (C44). The output drives header pin `VTX`
through a 75 Ω back-termination (R11). The chip runs from `+5V_SYS`; its 5 V data output
goes to MCU pin PB14, which is 5 V tolerant.

### Buzzer and BOOT button (through the service cable)

The MCU's alarm pin (PB9) switches **Q1**, which switches **Q2** to put 5 V pulses on the
`BUZ` wire; **R18** (10 Ω, 1 W) limits the current even if the cable is shorted. On the
service board the buzzer sits between `BUZ` and ground with a catch diode. With the MCU
pin idle or unpowered the buzzer is off.

The BOOT button connects USB 5 V through 10 kΩ to the `BOOT` wire; a 10 kΩ pull-down on
the upper board makes that 2.5 V at the MCU's BOOT0 pin. Holding it while plugging in USB
starts the built-in DFU bootloader.

## Service board

USB-C socket with 5.1 kΩ on both CC pins (so any charger or computer supplies 5 V),
ESD protection on the data lines, the buzzer, and the BOOT button. The cable is a
6-wire JST-SH wired 1:1:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Signal | VBUS | D− | D+ | GND | BUZ | BOOT |

**Check your cable.** Some ready-made JST-SH cables are wired reversed (pin 1 to pin 6).
A reversed cable puts USB 5 V on the BOOT line and buzzer pulses on a USB data line.
Test continuity pin 1 to pin 1 before use.
