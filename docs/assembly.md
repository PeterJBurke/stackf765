# Assembling the stack

You need: the three assembled boards, the two right-angle headers, the two Samtec board-to-board
connectors if they were not factory-fitted, three M2 × 4 mm screws,
four silicone grommets ("M4 to M3") with brass "M3 to M2" inserts and M2 screws, a 6-wire JST-SH cable wired 1:1
(JST A06SR06SR30K102A), battery and ESC wires.

Do the electrical checks in [bringup.md](bringup.md) on each board **before** stacking them.

## 1. Solder the headers and board-to-board connectors

**Board-to-board connectors (if not factory-fitted).** Socket SFMC-110-02-L-D on the top of the lower
board (J1), header FTSH-110-04-L-DV on the bottom of the upper board (J3). They are 1.27 mm-pitch
surface-mount parts: tack one corner pin, check alignment, then solder the rest with flux and a fine tip.

**Lower board, J2 (3 × 9 right-angle, three 3 × 3 pieces).** Top side, front edge, pins pointing off the
board; the plastic body hangs just beyond the board edge. Columns left to right: `M1 M2 M3 M4 M5 M6 LED PI5V PI5V`.
In each column the top pin is signal, the middle pin 5 V, the bottom pin ground.

**Upper board, J1 (3 × 12 right-angle).** Top side, front edge, pins pointing off the board.
You can use one Samtec TSW-112-08-G-T-RA or four generic 3 × 3 pieces side by side.
The plastic body hangs just beyond the board edge. **Cut the pin tails under the upper board flush: 0.5 mm
or less.** As supplied (about 1.4 mm) their tips end level with the tops of the lower header's pins, and only
the half-pitch sideways offset between the two headers (0.63 mm) keeps them apart. Cut flush, they clear by
about 0.9 mm. Use the generic 7.5 mm-body header on the lower board, seated flat; a taller header there
removes the clearance.

Before first power with the stack assembled, check with a meter that `PI5V` is not shorted to ground and
that the upper board's `5V` pins are not connected to `M1`–`M6` or `LED`.

## 2. Solder the power wires

On the lower board's rear edge, left to right seen from above with the pads towards you:

`BAT+   ESC+   ESC−   BAT−`

Use wire sized for your current (12 AWG for 50 A). Tin the pads, solder with a large tip, and
keep the wires flat and pointing rearward so they clear the upper board. Add the ESC's bulk
capacitor at the ESC as usual.

**There is no reverse-polarity protection. Check twice with a meter before connecting a battery.**

## 3. Mount the lower board

Press a grommet into each of the four 4 mm holes (20 × 20 mm pattern), push a brass insert into each
grommet, and fasten to the frame with M2 screws. The area around each grommet is kept free of parts.

## 4. Fit the upper board

Line up the 20-pin connector on the underside of the upper board with the socket on the lower
board, press down until the board rests on the three 8 mm standoffs (the connector is designed to stop about 0.35 mm short of fully seated), and fasten with three M2 × 4 mm
screws. Do not use longer screws.

## 5. Connect the service board

Plug the 6-wire cable between `J5` on the right-hand edge of the upper board and `J2` on the
service board. **The cable must be wired pin 1 to pin 1** — check with a meter; some ready-made
cables are reversed. A reversed cable does no damage, but USB will not connect. Mount the service board where the USB socket and button are reachable.

| Pin | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Signal | VBUS | GND | D− | D+ | BOOT | BUZ |

## 6. Wire the rest

See [pinout.md](pinout.md). Pins marked **5V** are powered only from the battery; pins marked
**4V5** are also powered from USB.
