# Firmware

StackF765 runs standard ArduPilot. The board is described by two files in
`firmware/hwdef/StackF765/` (`hwdef.dat` for the vehicle firmware, `hwdef-bl.dat` for the
bootloader). The board is not yet part of the ArduPilot tree, so you build the firmware yourself.

Prebuilt files from the last verification run are in `firmware/bin/`:

| File | Use |
|---|---|
| `StackF765_bl.bin` | ArduPilot bootloader (flash once over DFU) |
| `arducopter_with_bl.hex` | Bootloader + ArduCopter in one file (flash over DFU) |
| `arducopter.apj` | ArduCopter for loading from a ground station once the bootloader is in place |

These binaries have been compiled but **never run on hardware**.

## Building

```sh
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
# install ArduPilot's build prerequisites (arm-none-eabi-gcc 10.x, Python packages)
firmware/build.sh /path/to/ardupilot copter      # or plane, rover
```

The script copies the hwdef into the ArduPilot tree, builds the bootloader, then builds the
vehicle firmware with the bootloader embedded, and copies the results to `firmware/bin/`.

## Flashing a new board

1. Hold the **BOOT** button on the service board and plug in USB. The board appears as
   "STM32 BOOTLOADER". (Disconnect anything on header pin RX1 first.)
2. Flash `arducopter_with_bl.hex` with STM32CubeProgrammer, or with dfu-util:
   ```sh
   dfu-util -a 0 --dfuse-address 0x08000000:leave -D firmware/bin/arducopter_with_bl.bin
   ```
   (convert the hex to bin with `arm-none-eabi-objcopy -I ihex -O binary` if you use dfu-util).
3. Unplug and replug USB. The board now appears as an ArduPilot serial port; later updates
   can be loaded from Mission Planner or QGroundControl with the `.apj` file ("load custom firmware").

## Board ID

`APJ_BOARD_ID` is set to **20765**, a private number outside the range ArduPilot manages
(1000–19999). It is fine for your own boards. Before distributing firmware or proposing the
board upstream, request an official ID with a pull request against
`Tools/AP_Bootloader/board_types.txt` in ArduPilot and change both hwdef files.

## Default configuration

| Function | Setting |
|---|---|
| Serial ports | SERIAL0 = USB; SERIAL1–7 = UART 1, 2, 3, 4, 6, 7, 8 (header labels TXn/RXn) |
| Battery monitor | analog voltage and current, `BATT_VOLT_MULT` 11.0, `BATT_AMP_PERVLT` 20.0 |
| IMU | ICM-45686 (or ICM-42688-P) on SPI1, `ROTATION_ROLL_180_YAW_90` |
| Barometer | BMP388, I2C2, address 0x76 |
| OSD | AT7456E on SPI2, enabled by default (`OSD_TYPE` 1) |
| Logging | microSD |
| Outputs | M1–M4 on TIM2/TIM5 (M1 and M3 bidirectional-DShot capable), M5–M6 on TIM8, LED on TIM1 (output 7) |
| Buzzer | passive, PWM tones on PB9 |
| Status LEDs | blue PD10, green PD11 (active low) |

To use bidirectional DShot on all four motors, set `SERVO_BLH_BDMASK` and check the ArduPilot
documentation for timer-group limits: M1/M2 share TIM2 and M3/M4 share TIM5.

## Keeping firmware and hardware in step

`tools/check_hwdef.py` compares every pin in `hwdef.dat` with the schematic netlist and fails
if they differ. Run `make verify` after changing either.
