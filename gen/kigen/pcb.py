"""Board builder on top of the KiCad pcbnew Python API.

Board coordinates used by the design scripts: millimetres, origin at the
board centre, +X right, +Y up (towards the header edge), viewed from the top.
"""
import json
import math
import os
import subprocess
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

KICAD_FP = "/usr/share/kicad/footprints"
OX, OY = 100.0, 100.0   # board centre on the KiCad page


def P(x, y):
    return VECTOR2I(FromMM(OX + x), FromMM(OY - y))


def unP(v):
    return (ToMM(v.x) - OX, OY - ToMM(v.y))


class Board:
    def __init__(self, design, outdir, layers=4, local_fp_dir=None):
        self.design, self.outdir = design, outdir
        self.name = design.name
        self.path = os.path.join(outdir, f"{self.name}.kicad_pcb")
        self.b = pcbnew.BOARD()
        self.b.SetCopperLayerCount(layers)
        self.layers = layers
        self.local_fp_dir = local_fp_dir
        self.nets = {}
        self.fps = {}
        ds = self.b.GetDesignSettings()
        ds.SetBoardThickness(FromMM(1.6))
        ds.m_SolderMaskExpansion = 0
        ds.m_SolderMaskMinWidth = 0

    # ---- nets ------------------------------------------------------------
    def net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    def layer(self, name):
        lid = self.b.GetLayerID(name)
        if lid < 0:
            lid = self.b.GetLayerID({"F.SilkS": "F.Silkscreen", "B.SilkS": "B.Silkscreen"}.get(name, name))
        if lid < 0:
            raise ValueError(f"unknown layer {name}")
        return lid

    # ---- footprints ------------------------------------------------------
    def place(self, ref, x, y, rot=0, side="top"):
        part = self.design.parts[ref]
        libname, fpname = part.footprint.split(":")
        libdir = os.path.join(KICAD_FP, libname + ".pretty")
        if not os.path.isdir(libdir):
            libdir = os.path.join(self.local_fp_dir, libname + ".pretty")
        fp = pcbnew.FootprintLoad(libdir, fpname)
        if fp is None:
            raise SystemExit(f"footprint not found: {part.footprint}")
        fp.SetFPID(pcbnew.LIB_ID(libname, fpname))
        fp.SetReference(ref)
        fp.SetValue(part.value)
        fp.SetPath(pcbnew.KIID_PATH(part.path))
        for k, v in part.fields.items():
            if k in ("Datasheet", "Description"):
                continue
            fp.SetField(k, str(v))
            f = fp.GetFieldByName(k)
            if f:
                f.SetVisible(False)
        if part.dnp:
            fp.SetDNP(True)
        fp.Reference().SetLayer(self.layer("F.Fab"))      # designators live on the fab/assembly layer
        fp.Reference().SetTextSize(VECTOR2I(FromMM(0.5), FromMM(0.5)))
        fp.Reference().SetTextThickness(FromMM(0.08))
        fp.Reference().SetPosition(fp.GetPosition())
        self.b.Add(fp)
        fp.SetPosition(P(x, y))
        if side == "bottom":
            fp.Flip(P(x, y), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        padnums = set()
        for pad in fp.Pads():
            num = pad.GetNumber()
            padnums.add(num)
            net = part.conn.get(num)
            if net == "__NC__":
                pname = next(p.name for p in part.symbol.pins if p.number == num)
                pad.SetNet(self.net(f"unconnected-({ref}-{pname.replace('/', '{slash}')}-Pad{num})"))
            elif net:
                pad.SetNet(self.net(net))
        missing = [n for n, net in part.conn.items() if net != "__NC__" and n not in padnums]
        if missing:
            raise SystemExit(f"{ref}: footprint {part.footprint} lacks pads {missing}")
        fp.Value().SetVisible(False)
        self.fps[ref] = fp
        return fp

    def pad(self, ref, num):
        for pad in self.fps[ref].Pads():
            if pad.GetNumber() == str(num):
                return pad
        raise KeyError((ref, num))

    def padpos(self, ref, num):
        return unP(self.pad(ref, num).GetPosition())

    # ---- drawing ---------------------------------------------------------
    def _seg(self, layer, a, b, w=0.1):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(P(*a)); s.SetEnd(P(*b))
        s.SetLayer(self.layer(layer)); s.SetWidth(FromMM(w))
        self.b.Add(s)

    def _arc(self, layer, centre, start, angle_deg, w=0.1):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(P(*centre)); s.SetStart(P(*start))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T))
        s.SetLayer(self.layer(layer)); s.SetWidth(FromMM(w))
        self.b.Add(s)

    def outline_roundrect(self, w, h, r):
        self.size = (w, h)
        self.corner_r = r
        x0, x1, y0, y1 = -w / 2, w / 2, -h / 2, h / 2
        L = "Edge.Cuts"
        self._seg(L, (x0 + r, y1), (x1 - r, y1)); self._seg(L, (x1, y1 - r), (x1, y0 + r))
        self._seg(L, (x1 - r, y0), (x0 + r, y0)); self._seg(L, (x0, y0 + r), (x0, y1 - r))
        # KiCad Y is down, so a visually clockwise sweep is a positive angle
        self._arc(L, (x1 - r, y1 - r), (x1 - r, y1), 90)
        self._arc(L, (x1 - r, y0 + r), (x1, y0 + r), 90)
        self._arc(L, (x0 + r, y0 + r), (x0 + r, y0), 90)
        self._arc(L, (x0 + r, y1 - r), (x0, y1 - r), 90)

    def circle(self, layer, x, y, r, w=0.1):
        s = pcbnew.PCB_SHAPE(self.b)
        s.SetShape(pcbnew.SHAPE_T_CIRCLE)
        s.SetCenter(P(x, y)); s.SetEnd(P(x + r, y))
        s.SetLayer(self.layer(layer)); s.SetWidth(FromMM(w))
        self.b.Add(s)

    def line(self, layer, a, b, w=0.12):
        self._seg(layer, a, b, w)

    def text(self, s, x, y, layer="F.SilkS", size=0.8, thick=None, rot=0, justify="center", mirror=None):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetLayer(self.layer(layer))
        t.SetPosition(P(x, y))
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
        t.SetTextThickness(FromMM(thick or max(0.1, size * 0.15)))
        t.SetTextAngleDegrees(rot)
        t.SetHorizJustify({"center": pcbnew.GR_TEXT_H_ALIGN_CENTER, "left": pcbnew.GR_TEXT_H_ALIGN_LEFT,
                           "right": pcbnew.GR_TEXT_H_ALIGN_RIGHT}[justify])
        if mirror if mirror is not None else layer.startswith("B."):
            t.SetMirrored(True)
        self.b.Add(t)
        return t

    def hole(self, x, y, d, ref=None, plated=False, pad_d=None, net=None):
        """Mounting hole as a single-pad footprint (NPTH unless plated)."""
        fp = pcbnew.FOOTPRINT(self.b)
        fp.SetReference(ref or "H")
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetDrillSize(VECTOR2I(FromMM(d), FromMM(d)))
        if plated:
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetSize(VECTOR2I(FromMM(pad_d), FromMM(pad_d)))
            pad.SetLayerSet(pcbnew.PAD.PTHMask())
            pad.SetNumber("1")
            if net:
                pad.SetNet(self.net(net))
        else:
            pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
            pad.SetSize(VECTOR2I(FromMM(d), FromMM(d)))
            pad.SetLayerSet(pcbnew.PAD.UnplatedHoleMask())
        fp.Add(pad)
        self.b.Add(fp)
        fp.SetPosition(P(x, y))
        return fp

    # ---- copper ----------------------------------------------------------
    def track(self, net, layer, pts, width):
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(P(*a)); t.SetEnd(P(*b))
            t.SetWidth(FromMM(width)); t.SetLayer(self.layer(layer))
            t.SetNet(self.net(net))
            self.b.Add(t)

    def via(self, net, x, y, drill=0.3, dia=0.6):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(P(x, y))
        v.SetDrill(FromMM(drill)); v.SetWidth(pcbnew.F_Cu, FromMM(dia))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(self.net(net))
        self.b.Add(v)
        return v

    def zone(self, net, layers, pts, clearance=0.2, min_width=0.2, priority=0, solid=False, name=None,
             thermal_gap=0.25, thermal_width=0.3):
        z = pcbnew.ZONE(self.b)
        if net:
            z.SetNet(self.net(net))
        ls = pcbnew.LSET()
        for l in ([layers] if isinstance(layers, str) else layers):
            ls.AddLayer(self.layer(l))
        z.SetLayerSet(ls)
        ol = z.Outline()
        ol.NewOutline()
        for (x, y) in pts:
            ol.Append(P(x, y))
        z.SetLocalClearance(FromMM(clearance))
        z.SetMinThickness(FromMM(min_width))
        z.SetAssignedPriority(priority)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid else pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(FromMM(thermal_gap))
        z.SetThermalReliefSpokeWidth(FromMM(thermal_width))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        if name:
            z.SetZoneName(name)
        self.b.Add(z)
        return z

    def keepout(self, layers, pts, tracks=True, vias=True, copper=True, footprints=False, name=None):
        z = pcbnew.ZONE(self.b)
        z.SetIsRuleArea(True)
        ls = pcbnew.LSET()
        for l in ([layers] if isinstance(layers, str) else layers):
            ls.AddLayer(self.layer(l))
        z.SetLayerSet(ls)
        z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias)
        z.SetDoNotAllowZoneFills(copper); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(footprints)
        ol = z.Outline()
        ol.NewOutline()
        for (x, y) in pts:
            ol.Append(P(x, y))
        if name:
            z.SetZoneName(name)
        self.b.Add(z)
        return z

    def rect(self, x0, y0, x1, y1):
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def fill(self):
        """Save, reload from disk (fresh connectivity), fill all zones, save again."""
        self.b.Save(self.path)
        self.b = pcbnew.LoadBoard(self.path)
        pcbnew.ZONE_FILLER(self.b).Fill(self.b.Zones())
        self.b.Save(self.path)
        self._local_models()

    def _local_models(self):
        """Point footprints at our own STEP model when hardware/lib/3d has one with the footprint's name
        (stand-ins for models KiCad does not ship, and coloured versions of the connector models)."""
        import re
        d3 = os.path.join(self.local_fp_dir or "", "3d")
        if not os.path.isdir(d3):
            return
        txt = open(self.path).read()

        def sub(m):
            name = m.group(2)
            return f'(model "${{KIPRJMOD}}/../lib/3d/{name}.step"' if os.path.exists(os.path.join(d3, name + ".step")) else m.group(0)
        new = re.sub(r'\(model "\$\{KICAD9_3DMODEL_DIR\}/([^/"]+)/([^/"]+)\.(?:step|wrl)"', sub, txt)
        if new != txt:
            open(self.path, "w").write(new)

    def save(self):
        self.b.Save(self.path)
        self._local_models()

    # ---- autorouting -----------------------------------------------------
    def autoroute(self, jar, passes=30, timeout=1800):
        dsn = self.path.replace(".kicad_pcb", ".dsn")
        ses = self.path.replace(".kicad_pcb", ".ses")
        for f in (dsn, ses):
            if os.path.exists(f):
                os.remove(f)
        if not pcbnew.ExportSpecctraDSN(self.b, dsn):
            raise SystemExit("DSN export failed")
        log = self.path.replace(".kicad_pcb", ".freerouting.log")
        with open(log, "w") as lf:
            subprocess.run(["java", "-Djava.awt.headless=true", "-jar", jar, "-de", dsn, "-do", ses,
                            "-mp", str(passes), "-mt", "1", "-da", "-dct", "0"], stdout=lf, stderr=lf, timeout=timeout)
        if not os.path.exists(ses):
            raise SystemExit("autorouter produced no session file; see " + log)
        if not pcbnew.ImportSpecctraSES(self.b, ses):
            raise SystemExit("SES import failed")


def write_project(outdir, name, netclasses, rules, classes_patterns, extra_dru="", fp_libs=(), sym_libs=()):
    """Write .kicad_pro (design rules + net classes), .kicad_dru, and library tables."""
    pro = {
        "board": {
            "design_settings": {
                "defaults": {},
                "rules": {
                    "min_clearance": rules.get("clearance", 0.1),
                    "min_track_width": rules.get("track", 0.1),
                    "min_via_diameter": rules.get("via_dia", 0.45),
                    "min_through_hole_diameter": rules.get("via_drill", 0.2),
                    "min_via_annular_width": rules.get("annular", 0.075),
                    "min_hole_clearance": rules.get("hole_clearance", 0.2),
                    "min_hole_to_hole": rules.get("hole_to_hole", 0.25),
                    "min_copper_edge_clearance": rules.get("edge", 0.25),
                    "min_silk_clearance": 0.0,
                    "min_text_height": 0.6,
                    "min_text_thickness": 0.08,
                    "solder_mask_to_copper_clearance": 0.0,
                    "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1,
                    "min_connection": 0.0, "min_resolved_spokes": 1,
                    "use_height_for_length_calcs": True,
                },
                "rule_severities": rules.get("severities", {}),
                "track_widths": [0.0], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}],
            }
        },
        "meta": {"filename": f"{name}.kicad_pro", "version": 3},
        "net_settings": {
            "classes": [dict({"bus_width": 12, "diff_pair_gap": 0.2, "diff_pair_width": 0.2,
                              "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                              "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
                              "wire_width": 6, "priority": i}, **nc) for i, nc in enumerate(netclasses)],
            "meta": {"version": 4},
            "net_colors": None, "netclass_assignments": None,
            "netclass_patterns": [{"netclass": c, "pattern": p} for c, p in classes_patterns],
        },
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [], "text_variables": {},
    }
    with open(os.path.join(outdir, f"{name}.kicad_pro"), "w") as f:
        json.dump(pro, f, indent=2)
    with open(os.path.join(outdir, f"{name}.kicad_dru"), "w") as f:
        f.write("(version 1)\n" + extra_dru)
    with open(os.path.join(outdir, "fp-lib-table"), "w") as f:
        f.write("(fp_lib_table\n  (version 7)\n")
        for nick, uri in fp_libs:
            f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
        f.write(")\n")
    with open(os.path.join(outdir, "sym-lib-table"), "w") as f:
        f.write("(sym_lib_table\n  (version 7)\n")
        for nick, uri in sym_libs:
            f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
        f.write(")\n")
