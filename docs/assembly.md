# Assembling the stack

You need: the three assembled boards, the right-angle header for the upper board, three M2 × 4 mm screws,
four silicone grommets ("M4 to M3") with brass "M3 to M2" inserts and M2 screws, a 6-wire JST-SH cable wired 1:1
(JST A06SR06SR30K102A), battery and ESC wires.

Do the electrical checks in [bringup.md](bringup.md) on each board **before** stacking them.

## 1. Solder the header and board-to-board connectors

**Board-to-board connectors.** These come fitted by JLCPCB: the socket on the top of the lower board (J1) and
the header on the bottom of the upper board (J3). Peel the clear placement film off the top of the socket.
Only if your assembler left them off: they are 1.27 mm-pitch surface-mount parts (SFMC-110-02-L-D and
FTSH-110-04-L-DV); tack one corner pin, check alignment, then solder the rest with flux and a fine tip.

**Lower board, J2 (3 × 9 solder holes). Fit no header.** Do not fit a pin header here: its pins would sit directly under the pins of the upper board's header.
Solder the ESC signal leads, the LED lead and the companion-computer power wires straight into the holes from
the top, and keep each joint and wire within 3 mm of the board for the first 8 mm behind the front edge.
Columns left to right, seen from above with the front edge away from you: `M1 M2 M3 M4 M5 M6 LED PI5V PI5V`.
In each column the inner hole is signal, the middle hole 5 V, the hole nearest the edge ground.

**Upper board, J1 (3 × 12 right-angle).** Top side, front edge, pins pointing off the board.
You can use one Samtec TSW-112-08-G-T-RA or four generic 3 × 3 pieces side by side.
The plastic body hangs just beyond the board edge. The pin tails hang about 1.4 mm below the upper board,
over the lower board's solder holes; with no header on the lower board they have about 6.6 mm of clear space
and need no trimming.

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
