"""Grid autorouter for the generated boards (drives maze.c).

Works directly on a kigen.pcb.Board: reads pads/holes/tracks from pcbnew,
routes every net (signal nets pad-to-pad, plane nets pad-to-via), and writes
tracks and vias back.  KiCad's own DRC is the judge of the result.
"""
import ctypes
import math
import os
import subprocess
import numpy as np
import pcbnew
from pcbnew import ToMM
from .pcb import unP

HERE = os.path.dirname(os.path.abspath(__file__))


def _kernel():
    so, src = os.path.join(HERE, "maze.so"), os.path.join(HERE, "maze.c")
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
        subprocess.check_call(["gcc", "-O2", "-shared", "-fPIC", "-o", so, src])
    lib = ctypes.CDLL(so)
    lib.route.restype = ctypes.c_int
    return lib


def _disk(r_cells):
    r = int(math.ceil(r_cells))
    pts = [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r_cells * r_cells + 1e-9]
    # only the rim matters for a convex probe, but interior obstacles smaller than the disk exist: keep all
    return np.array(pts, dtype=np.int32).reshape(-1)


class Router:
    def __init__(self, board, layers, grid=0.05, track=0.15, clear=0.15, via_dia=0.6, via_drill=0.3,
                 edge_clear=0.3, hole_clear=0.25, widths=None, plane_nets=(), layer_cost=None,
                 via_cost=400, turn_cost=3, margin=None, plane_region=None, no_route=(), local_span=0.0,
                 max_victims=4):
        self.bd, self.b = board, board.b
        self.layers = layers                       # copper layer names in the grid, e.g. ["F.Cu","B.Cu"]
        self.lid = [board.layer(n) for n in layers]
        self.g = grid
        self.track, self.clear = track, clear
        self.via_dia, self.via_drill = via_dia, via_drill
        self.edge_clear, self.hole_clear = edge_clear, hole_clear
        self.widths = widths or {}
        self.plane_nets = set(plane_nets)
        self.plane_region = plane_region or {}     # net -> list of rects (x0,y0,x1,y1) where vias may reach the plane
        self.no_route = set(no_route)
        self.local_span, self.max_victims = local_span, max_victims
        self.layer_cost = layer_cost or [10] * len(layers)
        self.via_cost, self.turn_cost = via_cost, turn_cost
        self.margin = margin if margin is not None else grid * 0.75
        w, h = board.size
        self.x0, self.y1 = -w / 2, h / 2
        self.W, self.H, self.L = int(round(w / grid)) + 1, int(round(h / grid)) + 1, len(layers)
        self.hard = np.zeros((self.L, self.H, self.W), dtype=np.int32)
        self.soft = np.zeros((self.L, self.H, self.W), dtype=np.int32)
        self.novia = np.zeros((self.H, self.W), dtype=np.uint8)
        self.hist = np.zeros((self.L, self.H, self.W), dtype=np.int32)
        self.netid = {}
        self.netname = {}
        self.routes = {}          # net -> list of ("t", layer_idx, (x,y), (x,y), width) / ("v", (x,y))
        self.fixed = {}           # pre-routed copper per net (never ripped)
        self.failed = []
        self.k = _kernel()
        self.xs = self.x0 + np.arange(self.W) * grid
        self.ys = self.y1 - np.arange(self.H) * grid
        self._collect()

    # ---- helpers ---------------------------------------------------------
    def nid(self, name):
        if name not in self.netid:
            self.netid[name] = len(self.netid) + 1
            self.netname[self.netid[name]] = name
        return self.netid[name]

    def ix(self, x):
        return int(round((x - self.x0) / self.g))

    def iy(self, y):
        return int(round((self.y1 - y) / self.g))

    def xy(self, ix, iy):
        return (round(self.x0 + ix * self.g, 4), round(self.y1 - iy * self.g, 4))

    def _window(self, cx, cy, ext):
        ix0, ix1 = max(0, self.ix(cx - ext) - 1), min(self.W, self.ix(cx + ext) + 2)
        iy0, iy1 = max(0, self.iy(cy + ext) - 1), min(self.H, self.iy(cy - ext) + 2)
        return ix0, ix1, iy0, iy1

    def _sdf_box(self, cx, cy, hx, hy, r, rot, win):
        ix0, ix1, iy0, iy1 = win
        X, Y = np.meshgrid(self.xs[ix0:ix1] - cx, self.ys[iy0:iy1] - cy)
        th = math.radians(rot)
        c, s = math.cos(th), math.sin(th)
        lx, ly = X * c + Y * s, -X * s + Y * c
        qx, qy = np.abs(lx) - (hx - r), np.abs(ly) - (hy - r)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

    def _sdf_seg(self, a, b, win):
        ix0, ix1, iy0, iy1 = win
        X, Y = np.meshgrid(self.xs[ix0:ix1], self.ys[iy0:iy1])
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        if l2 < 1e-12:
            return np.hypot(X - a[0], Y - a[1])
        t = np.clip(((X - a[0]) * dx + (Y - a[1]) * dy) / l2, 0, 1)
        return np.hypot(X - (a[0] + t * dx), Y - (a[1] + t * dy))

    def _paint(self, grid, li, mask, win, net):
        ix0, ix1, iy0, iy1 = win
        sl = grid[li, iy0:iy1, ix0:ix1]
        if net < 0:
            sl[mask] = -1
            return
        conflict = mask & (sl != 0) & (sl != net)
        sl[mask & (sl == 0)] = net
        sl[conflict] = -1

    # ---- obstacle collection --------------------------------------------
    def _pad_geom(self, pad):
        x, y = unP(pad.GetPosition())
        sz = pad.GetSize(pcbnew.F_Cu)
        hx, hy = ToMM(sz.x) / 2, ToMM(sz.y) / 2
        rot = pad.GetOrientationDegrees()
        shape = pad.GetShape(pcbnew.F_Cu)
        if shape == pcbnew.PAD_SHAPE_CIRCLE:
            r = hx
        elif shape == pcbnew.PAD_SHAPE_OVAL:
            r = min(hx, hy)
        elif shape == pcbnew.PAD_SHAPE_ROUNDRECT:
            r = ToMM(pad.GetRoundRectCornerRadius(pcbnew.F_Cu))
        else:
            r = 0.0
        if shape == pcbnew.PAD_SHAPE_CUSTOM:
            bb = pad.GetBoundingBox()
            cx, cy = unP(bb.GetCenter())
            return cx, cy, ToMM(bb.GetWidth()) / 2, ToMM(bb.GetHeight()) / 2, 0.0, 0.0
        off = pad.GetOffset(pcbnew.F_Cu)
        if off.x or off.y:
            th = math.radians(rot)
            ox, oy = ToMM(off.x), -ToMM(off.y)
            x += ox * math.cos(th) - oy * math.sin(th)
            y += ox * math.sin(th) + oy * math.cos(th)
        return x, y, hx, hy, r, rot

    def _collect(self):
        g, m = self.g, self.margin
        infl = self.clear + self.track / 2 + m
        via_r = self.via_dia / 2
        # board edge: block everything closer than edge_clear + track/2 to the outline (rounded rectangle)
        w, h = self.bd.size
        e = self.edge_clear + self.track / 2 + m
        win = (0, self.W, 0, self.H)
        d = self._sdf_box(0, 0, w / 2, h / 2, getattr(self.bd, "corner_r", 1.0), 0, win)
        for li in range(self.L):
            self.hard[li][d > -e] = -1
        self.novia[d > -(self.edge_clear + via_r + m)] = 1
        self.pads = {}
        for fp in self.b.GetFootprints():
            for pad in fp.Pads():
                x, y, hx, hy, r, rot = self._pad_geom(pad)
                netname = pad.GetNetname()
                net = self.nid(netname) if netname else -1
                tht = pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                ext = max(hx, hy) * 1.5 + 1.5
                win = self._window(x, y, ext)
                d = self._sdf_box(x, y, hx, hy, r, rot, win)
                lis = [li for li, l in enumerate(self.lid) if pad.IsOnLayer(l)]
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    hr = ToMM(pad.GetDrillSize().x) / 2
                    dh = self._sdf_box(x, y, hr, hr, hr, 0, win)
                    for li in range(self.L):
                        self._paint(self.hard, li, dh < self.hole_clear + self.track / 2 + m, win, -1)
                    ix0, ix1, iy0, iy1 = win
                    self.novia[iy0:iy1, ix0:ix1][dh < self.hole_clear + via_r + m] = 1
                    continue
                for li in lis:
                    self._paint(self.hard, li, d < infl, win, net)
                ix0, ix1, iy0, iy1 = win
                self.novia[iy0:iy1, ix0:ix1][d < via_r + 0.1 + m] = 1
                if tht:
                    hr = ToMM(pad.GetDrillSize().x) / 2
                    dh = self._sdf_box(x, y, hr, hr, hr, 0, win)
                    for li in range(self.L):
                        if li not in lis:
                            self._paint(self.hard, li, dh < self.hole_clear + self.track / 2 + m, win, net)
                if netname:
                    inner = d < -min(self.track / 2, min(hx, hy) * 0.6)
                    cells = []
                    yy, xx = np.nonzero(inner)
                    for li in lis:
                        cells += [(li, int(a) + ix0, int(b) + iy0) for a, b in zip(xx, yy)]
                    cc = [(li, self.ix(x), self.iy(y)) for li in lis]
                    self.pads.setdefault(netname, []).append(
                        dict(ref=fp.GetReference(), num=pad.GetNumber(), x=x, y=y, cells=cells or cc, centre=cc,
                             tht=tht, layers=lis, small=max(hx, hy) < 1.2, hx=hx, hy=hy))
        # keep-out rule areas
        for z in self.b.Zones():
            if z.GetIsRuleArea() and (z.GetDoNotAllowTracks() or z.GetDoNotAllowVias()):
                bb = z.GetBoundingBox()
                x0, y1 = unP(bb.GetOrigin())
                x1, y0 = unP(bb.GetEnd())
                win = self._window((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + 1)
                d = self._sdf_box((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2, 0, 0, win)
                if z.GetDoNotAllowTracks():
                    for li, l in enumerate(self.lid):
                        if z.IsOnLayer(l):
                            self._paint(self.hard, li, d < self.track / 2 + m, win, -1)
                if z.GetDoNotAllowVias():
                    ix0, ix1, iy0, iy1 = win
                    self.novia[iy0:iy1, ix0:ix1][d < via_r + m] = 1
        # existing (hand-placed) tracks and vias are fixed
        for t in self.b.GetTracks():
            name = t.GetNetname()
            if t.Type() == pcbnew.PCB_VIA_T:
                self.fixed.setdefault(name, []).append(("v", unP(t.GetPosition()), ToMM(t.GetWidth(pcbnew.F_Cu))))
            else:
                if t.GetLayer() in self.lid:
                    self.fixed.setdefault(name, []).append(
                        ("t", self.lid.index(t.GetLayer()), unP(t.GetStart()), unP(t.GetEnd()), ToMM(t.GetWidth())))
        for name, items in self.fixed.items():
            for it in items:
                self._paint_item(self.hard, self.nid(name), it)

    def _paint_item(self, grid, net, it):
        m = self.margin
        if it[0] == "t":
            _, li, a, b, w = it
            rad = w / 2 + self.clear + self.track / 2 + m
            cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            win = self._window(cx, cy, math.hypot(a[0] - b[0], a[1] - b[1]) / 2 + rad)
            self._paint(grid, li, self._sdf_seg(a, b, win) < rad, win, net)
        else:
            (x, y), dia = it[1], (it[2] if len(it) > 2 else self.via_dia)
            rad = dia / 2 + self.clear + self.track / 2 + m
            win = self._window(x, y, rad + 0.3)
            d = self._sdf_seg((x, y), (x, y), win)
            for li in range(self.L):
                self._paint(grid, li, d < rad, win, net)
            ix0, ix1, iy0, iy1 = win
            self.novia[iy0:iy1, ix0:ix1][d < self.via_drill / 2 + dia / 2 + max(self.hole_clear - (dia - self.via_drill) / 2, 0.0) + m] = 1

    def _rebuild_soft(self):
        self.soft[:] = 0
        for name, items in self.routes.items():
            for it in items:
                self._paint_item(self.soft, self.nid(name), it)

    # ---- search ----------------------------------------------------------
    def _search(self, net, src, tgt, mode, width, soft_cost=0, novia=None, max_expand=3_000_000):
        if not src or (mode == 0 and not tgt):
            return None
        src_a = np.array(src, dtype=np.int32).reshape(-1)
        tgt_a = np.array(tgt if tgt else [(0, -1, -1)], dtype=np.int32).reshape(-1)
        extra = (width - self.track) / 2
        probe_t = _disk(extra / self.g) if extra > 1e-6 else np.array([0, 0], dtype=np.int32)
        probe_v = _disk((self.via_dia / 2 - self.track / 2) / self.g)
        lc = np.array(self.layer_cost, dtype=np.int32)
        maxp = 20000
        out = np.zeros(3 * maxp, dtype=np.int32)
        cost = ctypes.c_int(0)
        nv = self.novia if novia is None else novia
        P = lambda a, t: a.ctypes.data_as(ctypes.POINTER(t))
        n = self.k.route(self.W, self.H, self.L, P(self.hard, ctypes.c_int32), P(self.soft, ctypes.c_int32),
                         P(nv, ctypes.c_uint8), P(self.hist, ctypes.c_int32), self.nid(net), P(lc, ctypes.c_int),
                         len(src_a) // 3, P(src_a, ctypes.c_int), len(tgt_a) // 3, P(tgt_a, ctypes.c_int), mode,
                         self.via_cost, soft_cost, self.turn_cost,
                         len(probe_t) // 2, P(probe_t, ctypes.c_int), len(probe_v) // 2, P(probe_v, ctypes.c_int),
                         max_expand, P(out, ctypes.c_int), maxp, ctypes.byref(cost))
        if n <= 0:
            return None
        return [tuple(int(v) for v in out[3 * i:3 * i + 3]) for i in range(n)], cost.value

    def _path_items(self, path, width, end_via=False):
        """Convert a cell path (target first) to track/via items."""
        items = []
        run = [path[0]]
        for c in path[1:]:
            if c[0] != run[-1][0]:
                items += self._run_items(run, width)
                items.append(("v", self.xy(c[1], c[2])))
                run = [c]
            else:
                run.append(c)
        items += self._run_items(run, width)
        if end_via:
            items.append(("v", self.xy(path[0][1], path[0][2])))
        return items

    def _run_items(self, run, width):
        if len(run) < 2:
            return []
        out = []
        start = run[0]
        prev = run[0]
        d = None
        for c in run[1:]:
            nd = (c[1] - prev[1], c[2] - prev[2])
            if d is not None and nd != d:
                out.append(("t", start[0], self.xy(start[1], start[2]), self.xy(prev[1], prev[2]), width))
                start = prev
            d = nd
            prev = c
        out.append(("t", start[0], self.xy(start[1], start[2]), self.xy(prev[1], prev[2]), width))
        return out

    def _cells_of(self, items):
        cells = []
        for it in items:
            if it[0] == "t":
                _, li, a, b, w = it
                n = max(1, int(round(max(abs(a[0] - b[0]), abs(a[1] - b[1])) / self.g)))
                for i in range(n + 1):
                    t = i / n
                    cells.append((li, self.ix(a[0] + (b[0] - a[0]) * t), self.iy(a[1] + (b[1] - a[1]) * t)))
            else:
                x, y = it[1]
                cells += [(li, self.ix(x), self.iy(y)) for li in range(self.L)]
        return cells

    def _stub(self, pad, cell, width):
        """Short segment from the path end to the exact pad centre (keeps ends tidy)."""
        li, cx, cy = cell
        p = self.xy(cx, cy)
        if pad["small"] and (abs(p[0] - pad["x"]) > 1e-4 or abs(p[1] - pad["y"]) > 1e-4) and \
                math.hypot(p[0] - pad["x"], p[1] - pad["y"]) < 0.5:
            w = min(width, 2 * min(pad["hx"], pad["hy"]))    # never wider than the pad it ends in
            return [("t", li, p, (round(pad["x"], 4), round(pad["y"], 4)), w)]
        return []

    def _pad_at(self, net, cell):
        for pad in self.pads.get(net, []):
            if cell in pad["_cellset"]:
                return pad
        return None

    def _novia_for(self, net):
        regs = self.plane_region.get(net)
        if not regs:
            return self.novia
        allow = np.zeros_like(self.novia)
        for (x0, y0, x1, y1) in regs:
            allow[max(0, self.iy(y1)):self.iy(y0) + 1, max(0, self.ix(x0)):self.ix(x1) + 1] = 1
        return np.ascontiguousarray(self.novia | (1 - allow))

    def route_net(self, net, soft_cost=0):
        """Route one net completely; returns True on success.  Items are appended to self.routes[net]."""
        pads = self.pads.get(net, [])
        width = self.widths.get(net, self.track)
        for p in pads:
            p.setdefault("_cellset", set(p["cells"]) | set(p["centre"]))
        items = self.routes.setdefault(net, [])
        fixed = self.fixed.get(net, [])
        ok = True
        if net in self.plane_nets:
            novia = self._novia_for(net)
            # cells already tied to the plane: through-hole pads, vias, and tracks that lead to a via.
            # Track pieces left without a via (after a rip-up) are discarded.
            def key(pt, li):
                return (li, self.ix(pt[0]), self.iy(pt[1]))
            allit = list(items) + list(fixed)
            parent = list(range(len(allit)))

            def find_(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i
            ends = {}
            for i, it in enumerate(allit):
                ks = [key(it[2], it[1]), key(it[3], it[1])] if it[0] == "t" else [key(it[1], li) for li in range(self.L)]
                for k_ in ks:
                    if k_ in ends:
                        parent[find_(i)] = find_(ends[k_])
                    else:
                        ends[k_] = i
            good = {find_(i) for i, it in enumerate(allit) if it[0] == "v"}
            kept = [it for i, it in enumerate(allit[:len(items)]) if find_(i) in good]
            if len(kept) != len(items):
                items[:] = kept
                self._rebuild_soft()
            anchored = [c for p in pads if p["tht"] for c in p["centre"]] + self._cells_of(list(items) + list(fixed))
            todo = [p for p in pads if not p["tht"]]
            # hardest (most boxed-in) pads first: smallest pads tend to be IC pins
            todo.sort(key=lambda p: -p["hx"] * p["hy"])     # capacitors first, IC pins then join them
            for p in todo:
                aset = set(anchored)
                if any(c in aset for c in p["cells"]):
                    anchored += p["cells"]
                    continue
                src = p["cells"]
                r1 = self._search(net, src, None, 1, width, soft_cost, novia=novia, max_expand=600_000)
                r0 = self._search(net, src, anchored, 0, width, soft_cost, max_expand=600_000) if anchored else None
                best = None
                if r1 and (not r0 or r1[1] <= r0[1]):
                    best = self._path_items(r1[0], width, end_via=True) + self._stub(p, r1[0][-1], width)
                elif r0:
                    best = self._path_items(r0[0], width) + self._stub(p, r0[0][-1], width)
                if best is None:
                    ok = False
                    self.failed.append((net, p["ref"], p["num"]))
                    continue
                for it in best:
                    self._paint_item(self.soft, self.nid(net), it)
                items += best
                anchored += self._cells_of(best) + p["cells"]
            return ok
        if len(pads) < 2:
            return True
        # connected groups: start from the pad nearest the centroid of the net
        remaining = list(pads)
        tree_cells = list(remaining.pop(0)["cells"]) + self._cells_of(fixed)
        treeset = set(tree_cells)
        while remaining:
            done = [p for p in remaining if any(c in treeset for c in p["centre"])]
            for p in done:
                remaining.remove(p)
                tree_cells += p["cells"]; treeset |= set(p["cells"])
            if not remaining:
                break
            tgt = [c for p in remaining for c in p["cells"]]
            res = self._search(net, tree_cells, tgt, 0, width, soft_cost)
            seg_w = width
            if not res and width > self.track + 1e-6:      # neck down where the wide track cannot reach a pad
                res = self._search(net, tree_cells, tgt, 0, self.track, soft_cost)
                seg_w = self.track
            if not res:
                ok = False
                self.failed += [(net, p["ref"], p["num"]) for p in remaining]
                break
            path = res[0]
            hit = self._pad_at(net, path[0])
            new = self._path_items(path, seg_w)
            if hit:
                new += self._stub(hit, path[0], seg_w)
            sp = self._pad_at(net, path[-1])
            if sp:
                new += self._stub(sp, path[-1], seg_w)
            for it in new:
                self._paint_item(self.soft, self.nid(net), it)
            items += new
            nc = self._cells_of(new)
            tree_cells += nc; treeset |= set(nc)
            if hit:
                remaining.remove(hit)
                tree_cells += hit["cells"]; treeset |= set(hit["cells"])
        return ok

    def _conflicts(self, net):
        """Nets whose routed copper violates clearance against 'net' routed copper (after a soft route)."""
        mine = self.routes.get(net, [])
        out = set()
        for other, items in self.routes.items():
            if other == net or not items:
                continue
            for a in mine:
                for b in items:
                    if self._item_clash(a, b):
                        out.add(other)
                        break
                if other in out:
                    break
        return out

    def _item_clash(self, a, b):
        def geom(it):
            if it[0] == "t":
                return [it[1]], it[2], it[3], it[4] / 2
            return list(range(self.L)), it[1], it[1], self.via_dia / 2
        la, a0, a1, ra = geom(a)
        lb, b0, b1, rb = geom(b)
        if not set(la) & set(lb):
            return False
        return _segdist(a0, a1, b0, b1) < ra + rb + self.clear - 1e-6

    def _find_conflicts(self):
        """Return {net: set(other nets)} for routed copper closer than the clearance, and bump the
        history cost where it happens.  Uses each net's widest track, so wide power tracks are covered."""
        cl = np.zeros((self.L, self.H, self.W), dtype=np.int32)
        hw = np.zeros(len(self.netid) + 2, dtype=np.float32)
        for name, items in self.routes.items():
            nid = self.nid(name)
            if nid >= len(hw):
                hw = np.resize(hw, nid + 2)
            hw[nid] = max([it[4] for it in items if it[0] == "t"] + [self.track]) / 2
            for c in self._cells_of(items):
                if 0 <= c[1] < self.W and 0 <= c[2] < self.H:
                    cl[c[0], c[2], c[1]] = nid
        via_cl = np.zeros((self.H, self.W), dtype=np.int32)      # via centres need the via radius instead
        for name, items in self.routes.items():
            for it in items:
                if it[0] == "v":
                    via_cl[self.iy(it[1][1]), self.ix(it[1][0])] = self.nid(name)
        out = {}
        hwmax = float(hw.max())
        vr = self.via_dia / 2
        for name, items in self.routes.items():
            nid = self.nid(name)
            for it in items:
                if it[0] == "t":
                    _, li, a, b, w = it
                    own = w / 2
                    win = self._window((a[0] + b[0]) / 2, (a[1] + b[1]) / 2,
                                       math.hypot(a[0] - b[0], a[1] - b[1]) / 2 + own + self.clear + max(hwmax, vr))
                    d = self._sdf_seg(a, b, win)
                    lis = [li]
                else:
                    x, y = it[1]
                    own = vr
                    win = self._window(x, y, own + self.clear + max(hwmax, vr) + 0.3)
                    d = self._sdf_seg((x, y), (x, y), win)
                    lis = range(self.L)
                ix0, ix1, iy0, iy1 = win
                base = own + self.clear - 0.01
                vsub = via_cl[iy0:iy1, ix0:ix1]
                vbad = (vsub != 0) & (vsub != nid) & (d < base + vr)
                for l in lis:
                    sub = cl[l, iy0:iy1, ix0:ix1]
                    bad = ((sub != 0) & (sub != nid) & (d < base + hw[sub])) | vbad
                    if bad.any():
                        for o in np.unique(np.concatenate([sub[bad & (sub != 0) & (sub != nid)], vsub[vbad]])):
                            if int(o) == 0 or int(o) == nid:
                                continue
                            out.setdefault(name, set()).add(self.netname[int(o)])
                            out.setdefault(self.netname[int(o)], set()).add(name)
                        self.hist[l, iy0:iy1, ix0:ix1][d < base + hwmax] += self.hist_inc
        return out

    def route_all(self, order=None, iterations=40, log=print, **_):
        """Negotiated-congestion routing (PathFinder style).

        Plane nets (pad -> via fan-outs) are routed first and kept.  Signal nets are then routed
        allowing overlaps at a cost; every iteration the nets involved in a clash are ripped up and
        rerouted with a higher overlap price and with a history cost on the contested cells, until
        no clashes remain."""
        import copy
        nets = [n for n in self.pads if n not in self.no_route]

        def span(n):
            ps = self.pads[n]
            return (max(p["x"] for p in ps) - min(p["x"] for p in ps)) + (max(p["y"] for p in ps) - min(p["y"] for p in ps))
        planes = [n for n in nets if n in self.plane_nets]
        sig = sorted([n for n in nets if n not in self.plane_nets and len(self.pads[n]) > 1], key=span)
        if order:
            sig = [n for n in order if n in sig] + [n for n in sig if n not in order]
        self.hist_inc = 4
        self.routes = {}
        self._rebuild_soft()
        unreachable = set()
        for n in planes:
            self.failed = []
            if not self.route_net(n):
                unreachable.add(n)
        # plane fan-outs become fixed obstacles for the signal nets
        plane_routes = {n: self.routes.get(n, []) for n in planes}
        for n, items in plane_routes.items():
            for it in items:
                self._paint_item(self.hard, self.nid(n), it)
        self.routes = {}
        self._rebuild_soft()
        todo = list(sig)
        best = None
        for it in range(iterations):
            pen = int(30 * (1.35 ** it))
            for n in todo:
                self.routes[n] = []
            self._rebuild_soft()
            for n in todo:
                self.failed = []
                if not self.route_net(n, soft_cost=pen):
                    unreachable.add(n)
                else:
                    unreachable.discard(n)
            clashes = self._find_conflicts()
            bad = set(clashes) | {n for n in unreachable if n in sig}
            log(f"  iteration {it + 1}: overlap price {pen}, nets in conflict {len(clashes)}, unroutable {sorted(n for n in unreachable if n in sig)}")
            score = len(bad)
            if best is None or score < best[0]:
                best = (score, copy.deepcopy(self.routes), sorted(bad))
            if not bad:
                break
            todo = [n for n in sig if n in bad]
        self.routes = best[1]
        # drop anything still clashing so the board never contains shorts; report it as unrouted
        failed = [n for n in best[2] if n in sig]
        for n in failed:
            self.routes[n] = []
        self.routes.update({n: plane_routes[n] for n in planes})
        self._rebuild_soft()
        self.unrouted = failed + sorted(n for n in unreachable if n in planes)
        return self.unrouted

    def route_seq(self, order=None, rip_rounds=8, log=print):
        """Sequential routing: plane fan-outs, then signal nets shortest first, never overlapping.
        Nets that fail are retried by ripping up the few nets in their way (best state is kept)."""
        import copy
        nets = [n for n in self.pads if n not in self.no_route]

        def span(n):
            ps = self.pads[n]
            return (max(p["x"] for p in ps) - min(p["x"] for p in ps)) + (max(p["y"] for p in ps) - min(p["y"] for p in ps))
        planes = [n for n in nets if n in self.plane_nets]
        sig = sorted([n for n in nets if n not in self.plane_nets and len(self.pads[n]) > 1], key=span)
        if order:
            sig = [n for n in order if n in sig] + [n for n in sig if n not in order]
        self.routes = {}
        self._rebuild_soft()
        failed = []
        # very short nets (a capacitor next to its pin) go in before the plane fan-outs can box them in
        local = [n for n in sig if span(n) < self.local_span and n not in (order or [])]
        for n in local + planes + [n for n in sig if n not in local]:
            self.failed = []
            if not self.route_net(n):
                failed.append(n)
                if n not in self.plane_nets:
                    self.routes[n] = []
                    self._rebuild_soft()
        log(f"  first pass: {len(planes) + len(sig) - len(failed)}/{len(planes) + len(sig)} routed; failed {failed}")
        best = (len(failed) + 1, copy.deepcopy(self.routes), list(failed))
        for rnd in range(rip_rounds + 4):
            still = []
            # plane nets are re-checked every round: a rip-up may have removed one of their fan-out vias
            for n in list(dict.fromkeys(failed + planes)):
                self.failed = []
                if self.route_net(n):
                    continue
                if n not in self.plane_nets:
                    self.routes[n] = []
                    self._rebuild_soft()
                keep = copy.deepcopy(self.routes)
                self.failed = []
                if not self.route_net(n, soft_cost=150 + 100 * rnd):
                    still.append(n)
                    self.routes = keep
                    self._rebuild_soft()
                    continue
                victims = [v for v in self._conflicts(n)]
                if len(victims) > self.max_victims:
                    still.append(n)
                    self.routes = keep
                    self._rebuild_soft()
                    continue
                saved = {v: self.routes[v] for v in victims}
                for v in victims:
                    self.routes[v] = [] if v not in self.plane_nets else \
                        [i for i in self.routes[v] if not any(self._item_clash(i, j) for j in self.routes[n])]
                self._rebuild_soft()
                lost = []
                for v in sorted(victims, key=span):
                    self.failed = []
                    if not self.route_net(v):
                        lost.append(v)
                if len(lost) >= 1 + (rnd % 2):          # made things worse (or no better): undo
                    self.routes = keep
                    self._rebuild_soft()
                    still.append(n)
                else:
                    for v in lost:
                        if v not in self.plane_nets:
                            self.routes[v] = []
                        still.append(v)
                    self._rebuild_soft()
            failed = list(dict.fromkeys(still))
            log(f"  rip-up round {rnd + 1}: still failing {failed}")
            if len(failed) < best[0] or (not failed):
                best = (len(failed), copy.deepcopy(self.routes), list(failed))
            if not failed:
                break
        self.routes = best[1]
        self._rebuild_soft()
        self.unrouted = best[2]
        return best[2]

    def _prune(self):
        """Remove dead-end track stubs (an end that touches no pad, via or other track of the net)."""
        for net, items in self.routes.items():
            padcells = set()
            for p in self.pads.get(net, []):
                padcells |= set(p["cells"]) | set(p["centre"])
            for it in self.fixed.get(net, []):
                padcells |= set(self._cells_of([it]))
            changed = True
            while changed:
                changed = False
                count = {}
                for it in items:
                    if it[0] == "t":
                        for pt in (it[2], it[3]):
                            k = (it[1], self.ix(pt[0]), self.iy(pt[1]))
                            count[k] = count.get(k, 0) + 1
                    else:
                        for li in range(self.L):
                            k = (li, self.ix(it[1][0]), self.iy(it[1][1]))
                            count[k] = count.get(k, 0) + 1
                # cells along other tracks also count as contacts (T junctions)
                body = {}
                for i, it in enumerate(items):
                    if it[0] == "t":
                        for c in self._cells_of([it]):
                            body.setdefault(c, set()).add(i)
                for i, it in enumerate(items):
                    if it[0] != "t" or net in self.plane_nets:
                        continue
                    if math.hypot(it[2][0] - it[3][0], it[2][1] - it[3][1]) > 0.11:
                        continue            # only tiny leftovers are pruned
                    for pt in (it[2], it[3]):
                        k = (it[1], self.ix(pt[0]), self.iy(pt[1]))
                        touching = count.get(k, 0) > 1 or k in padcells or len(body.get(k, ())) > 1
                        if not touching:
                            items.pop(i)
                            changed = True
                            break
                    if changed:
                        break

    def commit(self):
        self._prune()
        for net, items in self.routes.items():
            for it in items:
                if it[0] == "t":
                    _, li, a, b, w = it
                    if a != b:
                        self.bd.track(net, self.layers[li], [a, b], w)
                else:
                    self.bd.via(net, it[1][0], it[1][1], self.via_drill, self.via_dia)


def _segdist(a0, a1, b0, b1):
    def pt_seg(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        t = 0 if l2 < 1e-12 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
        return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1, d2, d3, d4 = cross(b0, b1, a0), cross(b0, b1, a1), cross(a0, a1, b0), cross(a0, a1, b1)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and a0 != a1 and b0 != b1:
        return 0.0
    return min(pt_seg(a0, b0, b1), pt_seg(a1, b0, b1), pt_seg(b0, a0, a1), pt_seg(b1, a0, a1))
