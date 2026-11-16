"""Small helpers shared by the three board design files."""
from kigen.design import box, lib
import parts

FP_R = {"0402": "Resistor_SMD:R_0402_1005Metric", "0603": "Resistor_SMD:R_0603_1608Metric",
        "0805": "Resistor_SMD:R_0805_2012Metric", "1206": "Resistor_SMD:R_1206_3216Metric",
        "2512": "Resistor_SMD:R_2512_6332Metric"}
FP_C = {"0402": "Capacitor_SMD:C_0402_1005Metric", "0603": "Capacitor_SMD:C_0603_1608Metric",
        "0805": "Capacitor_SMD:C_0805_2012Metric", "1206": "Capacitor_SMD:C_1206_3216Metric",
        "1210": "Capacitor_SMD:C_1210_3225Metric"}


class Blocks:
    def __init__(self, design):
        self.d = design

    def R(self, sh, ref, value, a, b, x, y, rot=90, size="0402", **kw):
        f = parts.passive("R", value, size)
        f.update(kw)
        p = self.d.part(ref, "Device:R", FP_R[size], value, **f)
        p["1"] = a; p["2"] = b
        sh.place(p, x, y, rot)
        return p

    def C(self, sh, ref, value, a, b, x, y, rot=0, size="0402", **kw):
        f = parts.passive("C", value, size)
        f.update(kw)
        p = self.d.part(ref, "Device:C", FP_C[size], value, **f)
        p["1"] = a; p["2"] = b
        sh.place(p, x, y, rot)
        return p

    def caps(self, sh, prefix_start, values, rail, x, y, gnd="GND", dx=7.62, size="0402"):
        """Row of decoupling capacitors rail->GND.  values: list of (ref, value[, size])."""
        out = []
        for i, v in enumerate(values):
            ref, val = v[0], v[1]
            sz = v[2] if len(v) > 2 else size
            out.append(self.C(sh, ref, val, rail, gnd, x + i * dx, y, 0, sz))
        return out

    def part(self, sh, ref, key, x, y, rot=0, nets=None, nc=(), **kw):
        """Place a catalogue part (parts.PARTS[key]) and connect pins from a dict."""
        spec = dict(parts.PARTS[key])
        sym = spec.pop("symbol")
        fpn = spec.pop("footprint")
        val = kw.pop("value", None) or spec.pop("value")
        spec.pop("value", None)
        spec.update(kw)
        if callable(sym):
            sym = sym()
        p = self.d.part(ref, sym, fpn, val, **spec)
        for k, v in (nets or {}).items():
            p[k] = v
        if nc:
            p.nc(*nc)
        sh.place(p, x, y, rot)
        return p
