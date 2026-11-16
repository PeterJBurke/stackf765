# Assembling the stack

You need: the three assembled boards, the two right-angle headers, three M2 × 4 mm screws,
four grommets with M2 hardware, a 6-wire JST-SH cable (wired 1:1), battery and ESC wires.

Do the electrical checks in [bringup.md](bringup.md) on each board **before** stacking them.

## 1. Solder the headers

**Lower board, J2 (2 × 10 right-angle).** Fit it on the top side at the front edge with the pins
pointing off the board. Top row: `M1 M2 M3 M4 M5 M6 LED 5V PI5V PI5V`. Bottom row: all ground.

**Upper board, J1 (3 × 12 right-angle).** Top side, front edge, pins pointing off the board.
You can use one Samtec TSW-112-08-G-T-RA or four generic 3 × 3 pieces side by side.
Trim the pin tails under the upper board to **1.5 mm or less**: they sit above the pins of the lower
header with about 0.4 mm to spare (the two headers are offset sideways by half a pitch for this reason).

## 2. Solder the power wires

On the lower board's rear edge, left to right seen from above with the pads towards you:

`BAT+   ESC+   ESC−   BAT−`

Use wire sized for your current (12 AWG for 50 A). Tin the pads, solder with a large tip, and
keep the wires flat and pointing rearward so they clear the upper board. Add the ESC's bulk
capacitor at the ESC as usual.

**There is no reverse-polarity protection. Check twice with a meter before connecting a battery.**

## 3. Mount the lower board

Press a grommet into each of the four 4 mm holes (20 × 20 mm pattern) and fasten to the frame
with M2 screws. The area around each grommet is kept free of parts.

## 4. Fit the upper board

Line up the 20-pin connector on the underside of the upper board with the socket on the lower
board, press down until the board rests on the three standoffs, and fasten with three M2 × 4 mm
screws. Do not use longer screws.

## 5. Connect the service board

Plug the 6-wire cable between `J5` on the right-hand edge of the upper board and `J2` on the
service board. **The cable must be wired pin 1 to pin 1** — check with a meter; some ready-made
cables are reversed. Mount the service board where the USB socket and button are reachable.

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Signal | VBUS | D− | D+ | GND | BUZ | BOOT |

## 6. Wire the rest

See [pinout.md](pinout.md). Pins marked **5V** are powered only from the battery; pins marked
**4V5** are also powered from USB.
