# Layout review, 2026-11-18

Review of the routed rev B boards. Method: scripts over the KiCad board files (track lengths
and widths per net, via counts, distances from supply pins to capacitors and plane vias,
parallel-run scans), then reading the copper around anything that stood out.

## Lower board

**Battery path.** BAT+ pad, shunt and ESC+ pad sit side by side; each pad is a 5 x 4 mm surface pad
with twelve 0.4 mm plated holes, inside a solid zone on all four layers. Copper between pad and
shunt is about 1.5 mm long and 5 mm wide: under 0.1 mΩ. BAT- and ESC- are 2.5 mm apart in one
4.25 mm-tall four-layer zone: about 0.06 mΩ, 0.15 W at 50 A. The shunt itself dissipates 1.25 W at 50 A.

**5 V rails.** `+5V`: 62 mm of 0.6 mm track (2 oz) plus a 0.2 mm spur that feeds only the LED resistor.
IPC-2221 gives about 3.7 A for 20 °C rise. `+5V_PI`: 26 mm of 0.8 mm track, about 4.6 A for 20 °C rise.

**Regulator inputs.** Each buck draws from the inner VESC plane through two or three 0.3 mm vias
beside its input capacitors.

**Input clamp D1.** Joined to the VESC plane by one 0.3 mm via. Fine for the short pulses it handles;
a second via would be an easy improvement.

## Upper board

**Finding, fixed: 5 V feed into U5.** The battery-side 5 V input of the supply selector (U5 pin 3)
was reached by 6.7 mm of 0.15 mm track (about 22 mΩ, roughly 0.6 A for 10 °C rise) because the router
dropped straight to minimum width when the 0.5 mm track could not reach the pin. `+5V` is now routed
first and necked segments are widened afterwards as far as neighbouring copper allows
(`widen_tracks` in `gen/build.py`). Result: 0.5 mm everywhere except 5.0 mm at 0.24 mm (about 10 mΩ,
roughly 0.85 A for 10 °C rise) where the track passes between a ground via and U5 pin 4.
Expected load through it: about 0.3 A for the board plus whatever hangs on the two 4V5 pins,
which the pinout now limits to 0.5 A in total.

**`+5V_SYS`.** 116 mm at 0.4 mm. The only narrower pieces (2.9 mm) feed the sensor regulator U7 alone (about 10 mA).

**Header 5 V pins.** Fed from the board-to-board connector by 0.5 mm track (1 oz): about 1.4 A for
10 °C rise, 2 A for 20 °C. Keep the total drawn from the upper header's 5V pins under 2 A.

**Decoupling.** Capacitor to processor supply pin: 0.8 to 2.8 mm. Plane via to pin: 1.1 to 1.4 mm.
Several capacitors share the pin's via rather than having their own (capacitor pad to nearest via
2 to 4 mm); the loop from capacitor to pin is still short.

**Inner layers.** Layers 3 and 4 are both signal layers and only 0.1 mm apart in the JLC06161H-3313
stack-up, so tracks lying on top of each other would couple. Total parallel overlap found: 2.9 mm
(OSD_MISO over OSD_SCK).

**Same-layer coupling.** Longest parallel runs: SD_CMD beside SD_D3 (16.6 mm, same bus) and OSD_CS
beside OSD_MISO (6.4 mm, same bus). Nothing beside the video, ADC, crystal or reset nets.

**USB.** D+ 30 mm, D- 21 mm, on different inner layers, not routed as a pair. At full speed
(12 Mbit/s, 83 ns per bit) the 9 mm difference is about 60 ps and does not matter.

**SD card.** Clock 18 mm, data 15 to 45 mm; worst skew about 0.2 ns against a 20 ns period at 50 MHz.

**Crystals.** 8 MHz: 7.1 and 9.1 mm with two vias each. 27 MHz (OSD): 9.4 and 3.1 mm, one via each.
Longer and with more vias than ideal; not changed.

## Not covered

No field-solver or thermal simulation was run. Current ratings are from IPC-2221 and are estimates.
