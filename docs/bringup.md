# First power-up and test procedure

No StackF765 hardware had been built when this was written. Treat the first boards as
prototypes and work through every step, in order, with a **current-limited bench supply**.
Record the measurements; if any step fails, stop and investigate before going on.

Equipment: bench supply (0–13 V, current limit), multimeter, USB cable, computer with
Mission Planner or QGroundControl, optionally an oscilloscope and a thermal camera or thermocouple.

## A. Bare-board checks (no power)

| # | Check | Expected |
|---|---|---|
| A1 | Lower board: resistance BAT+ to BAT− | > 1 kΩ (about 11 kΩ divider in parallel with regulator inputs) |
| A2 | Lower board: resistance BAT+ to ESC+ | < 0.1 Ω (the shunt) |
| A3 | Lower board: resistance ESC− to BAT− | < 0.1 Ω |
| A4 | Lower board J2: middle-row `5V` holes and the `PI5V` holes to ground | not shorted (> 100 Ω) |
| A5 | Upper board: TP1 (+3V3) to TP2 (GND) | not shorted (> 100 Ω) |
| A6 | Upper board: TP3 (+5V_SYS) to TP2 (GND) | not shorted |
| A7 | Service cable: pin 1 to pin 1 … pin 6 to pin 6 | continuity; no continuity pin 1 to pin 6 |

## B. Lower board alone

Supply on BAT+ / BAT−, **8.0 V, current limit 0.2 A**, nothing connected to the outputs.

| # | Check | Expected |
|---|---|---|
| B1 | Supply current | under 20 mA |
| B2 | J2 middle-row `5V` hole (any of columns 1–7) | 5.06 V ± 0.15 V |
| B3 | J2 `PI5V` holes (columns 8–9, inner and middle) | 5.06 V ± 0.15 V |
| B4 | Green LED D2 | on |
| B5 | J1 socket pin `VBAT_SENSE` (column 6, row nearest the header) | supply voltage ÷ 11 (0.73 V at 8.0 V) |
| B6 | Raise the supply to 12.6 V | outputs unchanged, current still small |
| B7 | Lower the supply slowly | both outputs hold 5 V down to about 5.6 V |
| B8 | Load each 5 V output with 2.5 Ω (2 A) for 5 minutes at 8 V in (raise the current limit to 3 A) | output stays above 4.9 V; regulator and inductor comfortably below 85 °C |

The current-sense amplifier cannot be checked without the upper board because it is powered from `+3V3`.

## C. Upper board alone, on USB

Connect the service board with the cable and plug USB into a computer. Do **not** fit the upper board to the lower board yet.

| # | Check | Expected |
|---|---|---|
| C1 | TP3 (+5V_SYS) | 4.6–5.2 V |
| C2 | TP1 (+3V3) | 3.30 V ± 0.07 V |
| C3 | USB current (inline meter if you have one) | under 250 mA |
| C4 | U6 temperature after 5 minutes | warm, below 70 °C |
| C5 | Hold BOOT, plug USB | computer lists "STM32 BOOTLOADER" (DFU). Unplug anything on header pin RX1 first: the ROM bootloader also listens there. |
| C6 | Flash the bootloader and firmware ([firmware.md](firmware.md)) | board re-enumerates as an ArduPilot serial port; blue/green LEDs active |
| C7 | Connect with the ground station | heartbeat; no "Config error" for IMU or baro |
| C8 | Status: accelerometer | about (0, 0, −9.8) m/s² flat on the table |
| C9 | **IMU orientation**: tilt the nose (header end) down, then roll right | pitch reads negative, then roll reads positive. If not, change `IMU … ROTATION_…` in the hwdef (or `AHRS_ORIENTATION`) and report it. |
| C10 | Barometer | plausible pressure / altitude; moves when you lift the board 1 m |
| C11 | microSD card inserted, reboot | a log file is created (`LOG_BACKEND_TYPE` = 1) |
| C12 | Buzzer | start-up tune plays; no sound when idle |
| C13 | A GPS or receiver on a `4V5` pin group | powered and detected on USB power alone |

## D. Complete stack on the bench supply

Fit the upper board. Supply **8.0 V, limit 1 A**, USB disconnected.

| # | Check | Expected |
|---|---|---|
| D1 | Supply current | about 150–250 mA |
| D2 | Board boots, buzzer tune | yes |
| D3 | Ground station battery voltage (connect USB as well, or telemetry) | within 2 % of the supply; trim `BATT_VOLT_MULT` |
| D4 | Battery current with a known load on ESC+/ESC− (for example 5 A electronic load) | within 5 %; trim `BATT_AMP_PERVLT` (default 20.18) and `BATT_AMP_OFFSET` |
| D5 | Plug and unplug USB while on the supply | no reset |
| D6 | Each UART: loop TX to RX with a jumper, run a loopback or connect a device | data on all seven ports |
| D7 | I2C header (SDA/SCL) with an external compass | detected |
| D8 | Motor outputs M1–M6 with the motor test (props off) | each ESC responds in order; then enable DShot and check again |
| D9 | LED pin with an addressable LED strip (`SERVO7_FUNCTION` = 120) | LEDs respond |
| D10 | OSD: camera on CAM, monitor or VTX on VTX | picture with overlay; picture still passes with the OSD disabled |
| D11 | Companion computer on `PI5V`, running at load | rail stays above 4.9 V; flight controller unaffected |

## E. High current

Do this last, with props off or on a thrust stand, and the stack in moving air.

| # | Check | Expected |
|---|---|---|
| E1 | 20 A for 2 minutes through BAT+ → ESC+ / ESC− → BAT− | shunt and pad area below 60 °C |
| E2 | 50 A for 2 minutes | shunt, pads and wire joints below 100 °C; current reading stable |
| E3 | Throttle steps with the real ESC and motors | no resets, no brown-out messages, clean logs |

## What to report

Please open an issue on the repository with the board revision, the measurements that
differ from this table, and photos. Results from real hardware are the one thing this
project does not yet have.
