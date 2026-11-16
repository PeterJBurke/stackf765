#!/usr/bin/env bash
# Build the ArduPilot bootloader and ArduCopter firmware for the StackF765 board.
#
#   firmware/build.sh /path/to/ardupilot [vehicle]
#
# Needs: an ArduPilot checkout (with submodules), arm-none-eabi-gcc on PATH,
# and the ArduPilot Python build dependencies (empy==3.3.4, pexpect, future).
set -euo pipefail
AP="${1:?usage: build.sh /path/to/ardupilot [copter|plane|rover]}"
VEHICLE="${2:-copter}"
HERE="$(cd "$(dirname "$0")" && pwd)"
BOARD=StackF765

rm -rf "$AP/libraries/AP_HAL_ChibiOS/hwdef/$BOARD"
cp -r "$HERE/hwdef/$BOARD" "$AP/libraries/AP_HAL_ChibiOS/hwdef/$BOARD"
cd "$AP"

# 1) bootloader
./waf configure --board "$BOARD" --bootloader
./waf bootloader
mkdir -p "$HERE/bin"
cp "build/$BOARD/bin/AP_Bootloader.bin" "$HERE/bin/${BOARD}_bl.bin"
cp "build/$BOARD/bin/AP_Bootloader.bin" "Tools/bootloaders/${BOARD}_bl.bin"

# 2) vehicle firmware (embeds the bootloader so it can be re-flashed from the GCS)
./waf configure --board "$BOARD"
./waf "$VEHICLE"
cp build/$BOARD/bin/ardu${VEHICLE}.apj "$HERE/bin/" 2>/dev/null || true
cp build/$BOARD/bin/ardu${VEHICLE}.bin "$HERE/bin/" 2>/dev/null || true
cp build/$BOARD/bin/ardu${VEHICLE}_with_bl.hex "$HERE/bin/" 2>/dev/null || true
cp build/$BOARD/hwdef.h "$HERE/bin/hwdef.generated.h" 2>/dev/null || true
ls -la "$HERE/bin"
