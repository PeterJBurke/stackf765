"""Design model (parts, pins, nets) and KiCad 9 schematic writer.

The Python design files are the single source of truth.  This module turns
them into hierarchical .kicad_sch files; pcb.py turns the same model into a
board.  kicad-cli then cross-checks schematic against board (ERC + DRC with
schematic parity), so a bug in either writer is caught.
"""
import math
import os
import uuid as _uuid
from .sexpr import Sym, S, parse, dump, find, findall

KICAD_SYM = "/usr/share/kicad/symbols"
NS = _uuid.UUID("7d3c5c7e-3f0b-4c4e-9a53-0f765f765f76")
NC = "__NC__"


def uid(*parts):
    return str(_uuid.uuid5(NS, "/".join(str(p) for p in parts)))


class Pin:
    def __init__(self, number, name, x, y, angle, length, etype, hidden=False):
        self.number, self.name = number, name
        self.x, self.y, self.angle, self.length = x, y, angle, length
        self.etype, self.hidden = etype, hidden


class Symbol:
    """A library symbol definition (sexpr + extracted pins)."""
    def __init__(self, lib_id, sx, pins, props):
        self.lib_id, self.sx, self.pins, self.props = lib_id, sx, pins, props
        xs = [p.x for p in pins] or [0]
        ys = [p.y for p in pins] or [0]
        self.bbox = (min(xs), min(ys), max(xs), max(ys))


_libcache = {}
_symcache = {}


def _loadlib(lib):
    if lib not in _libcache:
        with open(os.path.join(KICAD_SYM, lib + ".kicad_sym")) as f:
            tree = parse(f.read())
        _libcache[lib] = {s[1]: s for s in findall(tree, "symbol")}
    return _libcache[lib]


def _extract_pins(sx):
    pins = []
    for sub in findall(sx, "symbol"):
        for p in findall(sub, "pin"):
            at = find(p, "at")
            hide = find(p, "hide")
            pins.append(Pin(find(p, "number")[1], find(p, "name")[1], float(at[1]), float(at[2]),
                            int(float(at[3])) if len(at) > 3 else 0, float(find(p, "length")[1]),
                            str(p[1]), bool(hide and hide[1] == "yes")))
    return pins


def lib(lib_id):
    """Load a symbol from the installed KiCad library, flattening 'extends'."""
    if lib_id in _symcache:
        return _symcache[lib_id]
    libname, name = lib_id.split(":")
    syms = _loadlib(libname)
    sx = syms[name]
    ext = find(sx, "extends")
    if ext:
        parent = syms[ext[1]]
        new = [Sym("symbol"), name]
        for item in parent[2:]:
            if isinstance(item, list) and item[0] == "property":
                continue
            if isinstance(item, list) and item[0] == "symbol":
                item = [item[0], name + item[1][len(ext[1]):]] + item[2:]
            new.append(item)
        new += findall(sx, "property")
        sx = new
    sx = [sx[0], lib_id] + [i for i in sx[2:]]
    props = {p[1]: p for p in findall(sx, "property")}
    sym = Symbol(lib_id, sx, _extract_pins(sx), props)
    _symcache[lib_id] = sym
    return sym


def _font(size=1.27, hide=False, justify=None):
    e = S("effects", S("font", S("size", size, size)))
    if justify:
        e.append(S("justify", *[Sym(j) for j in justify.split()]))
    if hide:
        e.append(S("hide", Sym("yes")))
    return e


def box(name, left=(), right=(), top=(), bottom=(), ref="U", width=None, title=None):
    """Create a rectangular IC symbol.  Pin entries: (number, name[, etype]) or None for a gap."""
    lib_id = "fc:" + name
    if lib_id in _symcache:
        return _symcache[lib_id]
    P = 2.54
    nv = max(len(left), len(right), 1)
    maxl = max([len(p[1]) for p in left if p] + [1])
    maxr = max([len(p[1]) for p in right if p] + [1])
    nh = max(len(top), len(bottom))
    w = width or max((maxl + maxr) * 1.1 + 6, (nh + 1) * P, 12.7)
    w = math.ceil(w / (2 * P)) * 2 * P
    h = (nv + 1) * P
    x0, x1 = -w / 2, w / 2
    y1 = math.ceil(h / 2 / P) * P
    y0 = y1 - h
    body = [Sym("symbol"), f"{name}_1_1",
            S("rectangle", S("start", x0, y1), S("end", x1, y0),
              S("stroke", S("width", 0.254), S("type", Sym("default"))), S("fill", S("type", Sym("background"))))]
    pins = []

    def addpin(entry, x, y, ang):
        if not entry:
            return
        num, pname = str(entry[0]), entry[1]
        et = entry[2] if len(entry) > 2 else "passive"
        body.append(S("pin", Sym(et), Sym("line"), S("at", x, y, ang), S("length", P),
                      S("name", pname, _font(1.27)), S("number", num, _font(1.27))))
    for i, e in enumerate(left):
        addpin(e, x0 - P, y1 - P * (i + 1), 0)
    for i, e in enumerate(right):
        addpin(e, x1 + P, y1 - P * (i + 1), 180)
    for i, e in enumerate(top):
        addpin(e, (i - (len(top) - 1) / 2) * P, y1 + P, 270)
    for i, e in enumerate(bottom):
        addpin(e, (i - (len(bottom) - 1) / 2) * P, y0 - P, 90)
    sx = [Sym("symbol"), lib_id, S("pin_names", S("offset", 1.016)),
          S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes")), S("on_board", Sym("yes")),
          S("property", "Reference", ref, S("at", x0, y1 + 1.27, 0), _font(justify="left bottom")),
          S("property", "Value", title or name, S("at", x0, y0 - 1.27, 0), _font(justify="left top")),
          S("property", "Footprint", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Datasheet", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Description", "", S("at", 0, 0, 0), _font(hide=True)),
          body]
    sym = Symbol(lib_id, sx, _extract_pins(sx), {p[1]: p for p in findall(sx, "property")})
    _symcache[lib_id] = sym
    return sym


def _power_symbol(net, ground):
    lib_id = "fcpwr:" + net
    if lib_id in _symcache:
        return _symcache[lib_id]
    st = S("stroke", S("width", 0), S("type", Sym("default")))
    nf = S("fill", S("type", Sym("none")))
    if ground:
        g = [S("polyline", S("pts", S("xy", 0, 0), S("xy", 0, -1.27), S("xy", 1.27, -1.27), S("xy", 0, -2.54),
                             S("xy", -1.27, -1.27), S("xy", 0, -1.27)), st, nf)]
        pin = S("pin", Sym("power_in"), Sym("line"), S("at", 0, 0, 270), S("length", 0),
                S("name", net, _font()), S("number", "1", _font()))
        vat = S("at", 0, -3.81, 0)
    else:
        g = [S("polyline", S("pts", S("xy", -0.762, 1.27), S("xy", 0, 2.54)), st, nf),
             S("polyline", S("pts", S("xy", 0, 2.54), S("xy", 0.762, 1.27)), st, nf),
             S("polyline", S("pts", S("xy", 0, 0), S("xy", 0, 2.54)), st, nf)]
        pin = S("pin", Sym("power_in"), Sym("line"), S("at", 0, 0, 90), S("length", 0),
                S("name", net, _font()), S("number", "1", _font()))
        vat = S("at", 0, 3.556, 0)
    pin.insert(4, S("hide", Sym("yes")))
    sx = [Sym("symbol"), lib_id, S("power"), S("pin_numbers", S("hide", Sym("yes"))),
          S("pin_names", S("offset", 0), S("hide", Sym("yes"))),
          S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes")), S("on_board", Sym("yes")),
          S("property", "Reference", "#PWR", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Value", net, vat, _font(1.0)),
          S("property", "Footprint", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Datasheet", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Description", "Power symbol", S("at", 0, 0, 0), _font(hide=True)),
          [Sym("symbol"), f"{net}_0_1"] + g, [Sym("symbol"), f"{net}_1_1", pin]]
    sym = Symbol(lib_id, sx, _extract_pins(sx), {})
    _symcache[lib_id] = sym
    return sym


def _flag_symbol():
    lib_id = "fcpwr:PWR_FLAG"
    if lib_id in _symcache:
        return _symcache[lib_id]
    st = S("stroke", S("width", 0), S("type", Sym("default")))
    nf = S("fill", S("type", Sym("none")))
    g = S("polyline", S("pts", S("xy", 0, 0), S("xy", 0, 1.27), S("xy", -1.016, 1.905), S("xy", 0, 2.54),
                        S("xy", 1.016, 1.905), S("xy", 0, 1.27)), st, nf)
    pin = S("pin", Sym("power_out"), Sym("line"), S("at", 0, 0, 90), S("length", 0),
            S("name", "pwr", _font()), S("number", "1", _font()))
    sx = [Sym("symbol"), lib_id, S("power"), S("pin_numbers", S("hide", Sym("yes"))),
          S("pin_names", S("offset", 0), S("hide", Sym("yes"))),
          S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes")), S("on_board", Sym("yes")),
          S("property", "Reference", "#FLG", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Value", "PWR_FLAG", S("at", 0, 3.3, 0), _font(0.8)),
          S("property", "Footprint", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Datasheet", "", S("at", 0, 0, 0), _font(hide=True)),
          S("property", "Description", "Power flag", S("at", 0, 0, 0), _font(hide=True)),
          [Sym("symbol"), "PWR_FLAG_0_0", pin], [Sym("symbol"), "PWR_FLAG_0_1", g]]
    sym = Symbol(lib_id, sx, _extract_pins(sx), {})
    _symcache[lib_id] = sym
    return sym


class Part:
    def __init__(self, design, ref, symbol, footprint, value, fields):
        self.design, self.ref, self.symbol = design, ref, symbol
        self.footprint, self.value, self.fields = footprint, value, fields
        self.conn = {}
        self.sheet = None
        self.pos = None
        self.dnp = fields.pop("dnp", False)

    def _numbers(self, key):
        key = str(key)
        nums = [p.number for p in self.symbol.pins if p.number == key]
        if not nums:
            nums = [p.number for p in self.symbol.pins if p.name == key]
        if not nums:  # match one of the '/'-separated alternates in a pin name
            nums = [p.number for p in self.symbol.pins if key in p.name.split("/")]
        if not nums:
            raise KeyError(f"{self.ref}: no pin '{key}' (have {[ (p.number,p.name) for p in self.symbol.pins]})")
        return nums

    def __setitem__(self, key, net):
        keys = key if isinstance(key, (tuple, list)) else [key]
        for k in keys:
            for n in self._numbers(k):
                if n in self.conn and self.conn[n] != net:
                    raise ValueError(f"{self.ref}.{k} already on {self.conn[n]}, cannot set {net}")
                self.conn[n] = net

    def nc(self, *keys):
        for k in keys:
            self[k] = NC

    def nc_rest(self):
        for p in self.symbol.pins:
            self.conn.setdefault(p.number, NC)

    def net_of(self, key):
        return self.conn[self._numbers(key)[0]]


class Sheet:
    def __init__(self, design, name, title, paper="A4", scale=0.7):
        self.design, self.name, self.title, self.paper = design, name, title, paper
        self.k = scale      # design files use a 420 x 297 canvas; it is scaled onto the page
        self.parts = []      # (part, x, y, rot)
        self.texts = []
        self.flags = []
        self.rects = []

    def place(self, part, x, y, rot=0):
        assert part.sheet is None, part.ref
        part.sheet = self
        g = 1.27
        x, y = round(x * self.k / g) * g, round(y * self.k / g) * g
        self.parts.append((part, x, y, rot))
        return part

    def text(self, x, y, s, size=1.8, bold=False):
        self.texts.append((x * self.k, y * self.k, s, size * 0.85, bold))

    def frame(self, x, y, w, h, label):
        k = self.k
        self.rects.append((x * k, y * k, w * k, h * k))
        self.texts.append((x * k + 1.5, y * k + 3.6, label, 1.9, True))

    def flag(self, net, x, y):
        g = 2.54
        self.flags.append((net, round(x * self.k / g) * g, round(y * self.k / g) * g))


class Design:
    def __init__(self, name, title, rev="A", date="", grounds=("GND",), rails=()):
        self.name, self.title, self.rev, self.date = name, title, rev, date
        self.parts = {}
        self.sheets = []
        self.grounds = set(grounds)
        self.rails = set(rails)
        self.root_notes = []

    def sheet(self, name, title, paper="A4", scale=0.7):
        s = Sheet(self, name, title, paper, scale)
        self.sheets.append(s)
        return s

    def part(self, ref, symbol, footprint, value, **fields):
        assert ref not in self.parts, ref
        if isinstance(symbol, str):
            symbol = lib(symbol)
        p = Part(self, ref, symbol, footprint, value, fields)
        self.parts[ref] = p
        return p

    # ---- netlist --------------------------------------------------------
    def nets(self):
        nets = {}
        for p in self.parts.values():
            for num, net in p.conn.items():
                if net != NC:
                    nets.setdefault(net, []).append((p.ref, num))
        return nets

    def check(self):
        errs = []
        for p in self.parts.values():
            for pin in p.symbol.pins:
                if pin.number not in p.conn:
                    errs.append(f"{p.ref} pin {pin.number} ({pin.name}) unassigned")
            if p.sheet is None:
                errs.append(f"{p.ref} not placed on a sheet")
        for net, nodes in self.nets().items():
            if len(nodes) < 2:
                errs.append(f"net {net} has a single node {nodes}")
        if errs:
            raise SystemExit("DESIGN CHECK FAILED\n  " + "\n  ".join(errs))

    # ---- schematic ------------------------------------------------------
    def write_schematic(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        root_uuid = uid(self.name, "root")
        pwr_counter = [0]
        for idx, sh in enumerate(self.sheets):
            self._write_sheet(outdir, sh, idx + 2, root_uuid, pwr_counter)
        self._write_root(outdir, root_uuid)

    def _header(self, uu, paper, title, page_comment=""):
        return [Sym("kicad_sch"), S("version", 20250114), S("generator", "fcgen"), S("generator_version", "9.0"),
                S("uuid", uu), S("paper", paper),
                S("title_block", S("title", title), S("date", self.date), S("rev", self.rev),
                  S("company", self.title), S("comment", 1, page_comment))]

    def _write_root(self, outdir, root_uuid):
        sx = self._header(root_uuid, "A4", self.title, "Index sheet - generated from gen/*.py")
        sx.append(S("lib_symbols"))
        y = 30
        sx.append(S("text", self.title, S("exclude_from_sim", Sym("no")), S("at", 20, 20, 0),
                    _font(3.5, justify="left bottom"), S("uuid", uid(self.name, "roottitle"))))
        for i, sh in enumerate(self.sheets):
            su = uid(self.name, "sheet", sh.name)
            col, row = i % 3, i // 3
            x, yy = 20 + col * 85, y + row * 32
            sx.append(S("sheet", S("at", x, yy), S("size", 70, 20),
                        S("exclude_from_sim", Sym("no")), S("in_bom", Sym("yes")), S("on_board", Sym("yes")),
                        S("dnp", Sym("no")), S("fields_autoplaced", Sym("yes")),
                        S("stroke", S("width", 0.1524), S("type", Sym("solid"))),
                        S("fill", S("color", 255, 255, 194, 1.0)), S("uuid", su),
                        S("property", "Sheetname", f"{i + 2}. {sh.title}", S("at", x, yy - 0.7, 0),
                          _font(1.6, justify="left bottom")),
                        S("property", "Sheetfile", f"{self.name}-{sh.name}.kicad_sch", S("at", x, yy + 20.6, 0),
                          _font(1.0, justify="left top")),
                        S("instances", S("project", self.name, S("path", "/" + root_uuid, S("page", str(i + 2)))))))
        ny = y + ((len(self.sheets) + 2) // 3) * 32 + 8
        for i, line in enumerate(self.root_notes):
            sx.append(S("text", line, S("exclude_from_sim", Sym("no")), S("at", 20, ny + i * 4.2, 0),
                        _font(1.8, justify="left bottom"), S("uuid", uid(self.name, "rootnote", i))))
        sx.append(S("sheet_instances", S("path", "/", S("page", "1"))))
        sx.append(S("embedded_fonts", Sym("no")))
        with open(os.path.join(outdir, f"{self.name}.kicad_sch"), "w") as f:
            f.write(dump(sx) + "\n")

    def _write_sheet(self, outdir, sh, page, root_uuid, pwr_counter):
        su = uid(self.name, "sheet", sh.name)
        path = f"/{root_uuid}/{su}"
        sx = self._header(su, sh.paper, f"{self.title} - {sh.title}", f"Sheet {page}: {sh.title}")
        libsyms = {}
        items = []

        def use(sym):
            libsyms[sym.lib_id] = sym.sx

        def instance(sym, ref, value, x, y, rot, uu, props, part=None):
            use(sym)
            s = S("symbol", S("lib_id", sym.lib_id), S("at", x, y, rot), S("unit", 1),
                  S("exclude_from_sim", Sym("no")), S("in_bom", Sym("no" if (ref.startswith("#") or (part and part.fields.get("BOM") == "no")) else "yes")),
                  S("on_board", Sym("yes")), S("dnp", Sym("yes" if (part and part.dnp) else "no")), S("uuid", uu))
            s += props
            seen = set()
            for p in sym.pins:
                if p.number not in seen:
                    seen.add(p.number)
                    s.append(S("pin", p.number, S("uuid", uid(uu, "pin", p.number))))
            s.append(S("instances", S("project", self.name, S("path", path, S("reference", ref), S("unit", 1)))))
            items.append(s)

        def power(net, x, y):
            pwr_counter[0] += 1
            sym = _power_symbol(net, net in self.grounds)
            ref = f"#PWR{pwr_counter[0]:04d}"
            vy = y + 3.81 if net in self.grounds else y - 3.556
            instance(sym, ref, net, x, y, 0, uid(path, ref),
                     [S("property", "Reference", ref, S("at", x, y, 0), _font(hide=True)),
                      S("property", "Value", net, S("at", x, vy, 0), _font(1.0)),
                      S("property", "Footprint", "", S("at", x, y, 0), _font(hide=True)),
                      S("property", "Datasheet", "", S("at", x, y, 0), _font(hide=True)),
                      S("property", "Description", "", S("at", x, y, 0), _font(hide=True))])

        def wire(x1, y1, x2, y2, key):
            items.append(S("wire", S("pts", S("xy", x1, y1), S("xy", x2, y2)),
                           S("stroke", S("width", 0), S("type", Sym("default"))), S("uuid", uid(path, "w", key))))

        def glabel(net, x, y, ang, key):
            just = "left" if ang in (0, 90) else "right"
            items.append(S("global_label", net, S("shape", Sym("passive")), S("at", x, y, ang),
                           S("fields_autoplaced", Sym("yes")), _font(1.1, justify=just),
                           S("uuid", uid(path, "gl", key)),
                           S("property", "Intersheetrefs", "${INTERSHEET_REFS}", S("at", x, y, 0),
                             _font(1.0, hide=True))))

        for (x, y, w, h) in sh.rects:
            items.append(S("rectangle", S("start", x, y), S("end", x + w, y + h),
                           S("stroke", S("width", 0.2), S("type", Sym("dash"))), S("fill", S("type", Sym("none"))),
                           S("uuid", uid(path, "rect", x, y))))
        for i, (x, y, s, size, bold) in enumerate(sh.texts):
            font = S("font", S("size", size, size))
            if bold:
                font.append(S("bold", Sym("yes")))
            items.append(S("text", s, S("exclude_from_sim", Sym("no")), S("at", x, y, 0),
                           S("effects", font, S("justify", Sym("left"), Sym("bottom"))),
                           S("uuid", uid(path, "text", i))))
        for i, (net, x, y) in enumerate(sh.flags):
            pwr_counter[0] += 1
            ref = f"#FLG{pwr_counter[0]:04d}"
            fs = _flag_symbol()
            instance(fs, ref, "PWR_FLAG", x, y, 0, uid(path, ref),
                     [S("property", "Reference", ref, S("at", x, y, 0), _font(hide=True)),
                      S("property", "Value", "PWR_FLAG", S("at", x, y - 3.3, 0), _font(0.8)),
                      S("property", "Footprint", "", S("at", x, y, 0), _font(hide=True)),
                      S("property", "Datasheet", "", S("at", x, y, 0), _font(hide=True)),
                      S("property", "Description", "", S("at", x, y, 0), _font(hide=True))])
            if net in self.grounds or net in self.rails:
                wire(x, y, x, y + 2.54, f"flag{i}")
                wire(x, y + 2.54, x + 2.54, y + 2.54, f"flagb{i}")
                power(net, x + 2.54, y + 2.54)
            else:
                wire(x, y, x, y + 2.54, f"flag{i}")
                glabel(net, x, y + 2.54, 270, f"flag{i}")

        for (part, x, y, rot) in sh.parts:
            sym = part.symbol
            th = math.radians(rot)
            c, s_ = round(math.cos(th)), round(math.sin(th))
            puid = uid(self.name, "sym", part.ref)
            part.path = f"/{su}/{puid}"
            bx0, by0, bx1, by1 = sym.bbox
            two_pin = len({p.number for p in sym.pins}) == 2 and not sym.lib_id.startswith("fc:")
            if two_pin:
                horizontal = (rot in (90, 270)) == (abs(by1 - by0) > abs(bx1 - bx0))
                if horizontal:
                    rp, vp, jr = (x, y - 2.0), (x, y + 2.3), None
                else:
                    rp, vp, jr = (x + 2.0, y - 1.0), (x + 2.0, y + 1.0), "left"
                fsz = 1.0
            elif rot == 0 and "Reference" in sym.props:
                ra, va = find(sym.props["Reference"], "at"), find(sym.props["Value"], "at")
                rp, vp, jr = (x + float(ra[1]), y - float(ra[2])), (x + float(va[1]), y - float(va[2])), "left"
                fsz = 1.27
            else:
                rp, vp, jr = (x - 2, y - abs(by1) - 6), (x - 2, y + abs(by0) + 6), "left"
                fsz = 1.27
            props = [S("property", "Reference", part.ref, S("at", rp[0], rp[1], 0), _font(fsz, justify=jr)),
                     S("property", "Value", part.value, S("at", vp[0], vp[1], 0), _font(fsz, justify=jr)),
                     S("property", "Footprint", part.footprint, S("at", x, y, 0), _font(hide=True)),
                     S("property", "Datasheet", part.fields.get("Datasheet", ""), S("at", x, y, 0), _font(hide=True)),
                     S("property", "Description", part.fields.get("Description", ""), S("at", x, y, 0),
                       _font(hide=True))]
            for k, v in part.fields.items():
                if k not in ("Datasheet", "Description"):
                    props.append(S("property", k, str(v), S("at", x, y, 0), _font(hide=True)))
            instance(sym, part.ref, part.value, x, y, rot, puid, props, part)
            done = {}
            for p in sym.pins:
                net = part.conn.get(p.number)
                px = x + (p.x * c - p.y * s_)
                py = y - (p.x * s_ + p.y * c)
                key = (round(px, 3), round(py, 3))
                if key in done:
                    if done[key] != net:
                        raise ValueError(f"{part.ref}: stacked pins at {key} on different nets {done[key]} / {net}")
                    continue
                done[key] = net
                oa = math.radians(p.angle + 180 + rot)
                dx, dy = round(math.cos(oa)), -round(math.sin(oa))
                if net == NC or net is None:
                    items.append(S("no_connect", S("at", px, py), S("uuid", uid(puid, "nc", p.number))))
                    continue
                L = 2.54
                ex, ey = px + dx * L, py + dy * L
                wire(px, py, ex, ey, f"{part.ref}.{p.number}")
                if net in self.grounds or net in self.rails:
                    power(net, ex, ey)
                else:
                    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(dx, dy)]
                    glabel(net, ex, ey, ang, f"{part.ref}.{p.number}")

        sx.append([Sym("lib_symbols")] + [libsyms[k] for k in sorted(libsyms)])
        sx += items
        sx.append(S("embedded_fonts", Sym("no")))
        with open(os.path.join(outdir, f"{self.name}-{sh.name}.kicad_sch"), "w") as f:
            f.write(dump(sx) + "\n")
