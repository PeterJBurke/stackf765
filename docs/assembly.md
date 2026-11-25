# Assembling the stack

You need: the three assembled boards, the two right-angle pin headers for the upper board, three M2 × 4 mm screws,
four silicone grommets ("M4 to M3") with brass "M3 to M2" inserts and M2 screws, a 6-wire JST-SH cable wired 1:1
(JST A06SR06SR30K102A), battery and ESC wires.

Do the electrical checks in [bringup.md](bringup.md) on each board **before** stacking them.

## 1. Solder the two pin headers to the upper board

Both Dupont headers are on the upper board. The lower board has none: do not add one.

**Front header, J1 (3 × 12 right-angle).** Top side, front edge, pins pointing forward off the board.
Use four generic 3 × 3 pieces side by side, or one Samtec TSW-112-08-G-T-RA.

**Rear header, J2 (3 × 9 right-angle).** Top side, rear edge, pins pointing rearward off the board.
Use three generic 3 × 3 pieces side by side. Looking into the pins from behind, the columns read
`PI5V PI5V M1 M2 M3 M4 M5 M6 LED`; in each column the top pin is signal, the middle pin 5 V and the bottom pin ground.

For both: the plastic body hangs just beyond the board edge. Hold the body's lower face level with the top of
the board while you solder, and solder from the underside. **Cut the rear header's tails flush after
soldering**: they hang over the battery and ESC wire joints on the lower board (1.2 mm spare with a 5 mm joint
and untrimmed tails; flush-cut tails give about 2.5 mm).

**Board-to-board connectors.** These come fitted by JLCPCB: the socket on the top of the lower board (J1) and
the header on the bottom of the upper board (J3). Peel the clear placement film off the top of the socket.
Only if your assembler left them off: they are 1.27 mm-pitch surface-mount parts (SFMC-110-02-L-D and
FTSH-110-04-L-DV); tack one corner pin, check alignment, then solder the rest with flux and a fine tip.

Before first power with the stack assembled, check with a meter that `PI5V` is not shorted to ground and
that the `5V` pins are not connected to `M1`–`M6` or `LED`.

## 2. Solder the power wires

On the lower board's rear edge, left to right seen from above with the pads towards you:

`BAT+   ESC+   ESC−   BAT−`

Use wire sized for your current (12 AWG for 50 A). Tin the pads, solder with a large tip, and
keep the wires flat and pointing rearward, with each joint no more than 5 mm above the board: the rear
pin header of the upper board sits directly above these pads. Add the ESC's bulk
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

## 6. Fit the microSD card

The socket is on the underside of the upper board. Slide the card in from the left-hand edge, between the two
boards, contacts facing up towards the upper board. It is a push-pull socket: pull the card out by its edge.

## 7. Wire the rest

ESC signal leads, servos and the LED strip plug onto the rear header; a companion computer takes its 5 V from the
two `PI5V` columns. See [pinout.md](pinout.md). Pins marked **5V** are powered only from the battery; pins marked
**4V5** are also powered from USB.
