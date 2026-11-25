"""Generate the pinout drawings, BOM summary and the GitHub Pages site (docs/).

    python3 gen/make_site.py
"""
import csv
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import upper  # noqa: E402
import lower  # noqa: E402

DOCS = os.path.join(ROOT, "docs")
REPO = "https://github.com/PeterJBurke/stackf765"

COL = {"G": ("#2b2b2b", "#fff"), "5V": ("#c62828", "#fff"), "4V5": ("#ef6c00", "#fff"), "PI5V": ("#ad1457", "#fff"),
       "TX": ("#1565c0", "#fff"), "RX": ("#2e7d32", "#fff"), "SDA": ("#6a1b9a", "#fff"), "SCL": ("#6a1b9a", "#fff"),
       "CAM": ("#00838f", "#fff"), "VTX": ("#00838f", "#fff"), "M": ("#455a64", "#fff"), "LED": ("#f9a825", "#000")}


def colour(label):
    for k in ("PI5V", "4V5", "5V", "SDA", "SCL", "CAM", "VTX", "LED", "TX", "RX", "G", "M"):
        if label.startswith(k):
            return COL[k]
    return ("#777", "#fff")


def grid_svg(rows, row_names, title, note, cell=46, rh=34):
    """rows: list of lists of labels.  Returns an SVG string."""
    n = len(rows[0])
    w = 70 + n * cell + 20
    h = 46 + len(rows) * rh + 34
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="system-ui,Segoe UI,Arial,sans-serif">',
           f'<text x="10" y="20" font-size="15" font-weight="700" fill="currentColor">{html.escape(title)}</text>']
    for r, row in enumerate(rows):
        y = 34 + r * rh
        out.append(f'<text x="10" y="{y + rh / 2 + 4}" font-size="12" fill="currentColor">{html.escape(row_names[r])}</text>')
        for c, lab in enumerate(row):
            bg, fg = colour(lab)
            x = 70 + c * cell
            out.append(f'<rect x="{x + 2}" y="{y + 2}" width="{cell - 4}" height="{rh - 4}" rx="5" fill="{bg}"/>')
            out.append(f'<text x="{x + cell / 2}" y="{y + rh / 2 + 4.5}" font-size="12.5" font-weight="600" '
                       f'text-anchor="middle" fill="{fg}">{html.escape(lab)}</text>')
    out.append(f'<text x="10" y="{h - 10}" font-size="11.5" fill="currentColor" opacity="0.75">{html.escape(note)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def pinouts():
    A = [l for l, _ in upper.J1_ROWS["A"]]
    Bq = [l for l, _ in upper.J1_ROWS["B"]]
    C = [l for l, _ in upper.J1_ROWS["C"]]
    svgs = {}
    svgs["upper-header-front"] = grid_svg(
        [A[::-1], Bq[::-1], C[::-1]], ["top row", "middle", "bottom row"],
        "Upper board 3 x 12 header - looking INTO the pins from the front",
        "Bottom row is the one nearest the circuit board.  TX/RX are named from the flight controller's side.")
    svgs["upper-header-top"] = grid_svg(
        [C, Bq, A], ["front edge", "middle", "inner row"],
        "Upper board 3 x 12 header - seen from ABOVE (header pointing away from you)",
        "This is how the labels are printed on the board.  Inner row = highest pins.")
    LA, LB, LC = ([l for l, _ in lower.J2_ROWS[r]] for r in "ABC")
    svgs["lower-header-front"] = grid_svg(
        [LC, LB, LA], ["edge row: ground", "middle: 5 V", "inner row: signal"],
        "Lower board 3 x 9 solder holes - seen from ABOVE (front edge away from you)",
        "No header is fitted: solder the ESC, LED and companion-computer wires into the holes.  PI5V = separate 5 V / 3 A.",
        cell=52)
    svgs["power-pads"] = grid_svg(
        [["BAT+", "ESC+", "ESC-", "BAT-"]], ["rear edge"],
        "Lower board solder pads - seen from above",
        "Battery + passes through the current shunt to ESC +.  2S-3S LiPo, 50 A continuous.", cell=80)
    svgs["service-cable"] = grid_svg(
        [["VBUS", "G", "D-", "D+", "BOOT", "BUZ"]], ["pin 1 - 6"],
        "Service cable (JST-SH 6 pin, wired 1:1)",
        "Same order on the flight controller (J5) and on the service board (J2).", cell=64)
    os.makedirs(os.path.join(DOCS, "img"), exist_ok=True)
    for k, v in svgs.items():
        with open(os.path.join(DOCS, "img", k + ".svg"), "w") as f:
            f.write(v)
    return svgs


def pinout_md():
    from pinmap import PINMAP
    A, Bq, C = (upper.J1_ROWS[r] for r in "ABC")
    L = ["# Pinout", "",
         "Diagrams: [project page](https://peterjburke.github.io/stackf765/#pinout). "
         "This file is generated from `gen/upper.py`, `gen/lower.py` and `gen/pinmap.py`.", "",
         "TX and RX are named from the flight controller's side: connect a device's TX to an RX pin.", "",
         "## Upper board, 3 x 12 header (J1)", "",
         "Seen from above with the header pointing away from you. Column 1 is on the left.", "",
         "| Row | " + " | ".join(str(i) for i in range(1, 13)) + " |", "|---|" + "---|" * 12,
         "| C: front edge, lowest pins | " + " | ".join(l for l, _ in C) + " |",
         "| B: middle | " + " | ".join(l for l, _ in Bq) + " |",
         "| A: inner row, highest pins | " + " | ".join(l for l, _ in A) + " |", "",
         "Looking into the pins from the front, the order is mirrored (column 12 on the left) and row A is on top.", "",
         "| Label | Meaning |", "|---|---|",
         "| G | Ground |", "| 5V | 5 V from the battery regulator (off on USB power) |",
         "| 4V5 | 5 V that is also live on USB power |",
         "| TXn / RXn | UART n (3.3 V logic). ArduPilot SERIAL1-7 = UART 1, 2, 3, 4, 6, 7, 8 |",
         "| SDA / SCL | I2C bus for an external compass etc. (3.3 V, 2.2 k pull-ups fitted) |",
         "| CAM | Analog video in from the camera |", "| VTX | Analog video out to the transmitter, with OSD |", "",
         "Suggested use (any UART can be given any role with `SERIALn_PROTOCOL`):", "",
         "| Pins | Typical device |", "|---|---|",
         "| A1-A6: G 4V5 TX1 RX1 SDA SCL | GPS + compass module (6-wire) |",
         "| B1-B4: G 4V5 TX2 RX2 | Radio receiver (CRSF / ELRS) |",
         "| A7-A9, A10-A12 | Camera (G 5V CAM) and video transmitter (G 5V VTX) |",
         "| other G 5V TX RX groups | Telemetry radio, ESC telemetry, VTX control, companion computer |", "",
         "## Lower board, 3 x 9 solder holes (J2)", "",
         "Seen from above with the front edge away from you. No header is fitted: solder wires into the holes. "
         "Each column is one servo / ESC lead (signal, 5 V, ground). " + "Do not fit a pin header here: its pins would sit directly under the pins of the upper board's header.", "",
         "| Row | " + " | ".join(str(i) for i in range(1, 10)) + " |", "|---|" + "---|" * 9,
         "| C: nearest the board edge | " + " | ".join(l for l, _ in lower.J2_ROWS["C"]) + " |",
         "| B: middle | " + " | ".join(l for l, _ in lower.J2_ROWS["B"]) + " |",
         "| A: inner row (signal) | " + " | ".join(l for l, _ in lower.J2_ROWS["A"]) + " |", "",
         "M1-M6: motor or servo outputs (PWM, OneShot, DShot). LED: addressable LED data (ArduPilot output 7). "
         "5V: flight-controller 5 V rail. PI5V: separate 5 V / 3 A regulator for a companion computer "
         "(two columns: inner and middle holes are PI5V, edge hole is ground).", "",
         "## Lower board, power pads", "", "Rear edge, seen from above: `BAT+  ESC+  ESC-  BAT-`. 2S-3S LiPo, 50 A continuous.", "",
         "## Service cable (J5 on the upper board, J2 on the service board)", "",
         "| Pin | 1 | 2 | 3 | 4 | 5 | 6 |", "|---|---|---|---|---|---|---|", "| Signal | VBUS | GND | D- | D+ | BOOT | BUZ |", "",
         "JST-SH 1.0 mm, wired pin 1 to pin 1.", "",
         "## Microcontroller pins", "", "| MCU pin | ArduPilot function | Net | Goes to |", "|---|---|---|---|"]
    dest = {"USB_DM": "service cable pin 2", "USB_DP": "service cable pin 3", "SWDIO": "test pad TP4", "SWCLK": "test pad TP5",
            "BUZZER": "buzzer switch Q1", "LED_BLUE": "blue LED", "LED_GREEN": "green LED", "VBAT_ADC": "battery voltage divider (lower board)",
            "CURR_ADC": "current-sense amplifier (lower board)", "LED_STRIP": "lower board, LED solder hole"}
    for pin in sorted(PINMAP, key=lambda p: (p[1], int(p[2:]))):
        net, fn = PINMAP[pin]
        d = dest.get(net)
        if not d:
            if net.startswith(("TX", "RX")) or net in ("SDA", "SCL"):
                d = "upper header pin " + net
            elif net.startswith("M") and net[1:].isdigit():
                d = "lower board solder hole " + net
            elif net.startswith("IMU"):
                d = "IMU (U2)"
            elif net.startswith("OSD"):
                d = "OSD chip (U4)"
            elif net.startswith("BARO"):
                d = "barometer (U3)"
            elif net.startswith("SD_"):
                d = "microSD socket (J4)"
            else:
                d = ""
        L.append(f"| {pin} | {fn} | {net} | {d} |")
    open(os.path.join(DOCS, "pinout.md"), "w").write("\n".join(L) + "\n")


def read_bom(board):
    p = os.path.join(ROOT, "fab", board, f"{board}-bom.csv")
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def summary(board):
    p = os.path.join(ROOT, "build", board, "summary.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def bom_table(board):
    rows = read_bom(board)
    total = 0.0
    out = ['<table class="bom"><thead><tr><th>Ref</th><th>Qty</th><th>Value</th><th>Description</th><th>MPN</th>'
           '<th>LCSC</th><th>$ each</th></tr></thead><tbody>']
    for r in rows:
        try:
            total += float(r["Unit price USD"] or 0) * int(r["Qty"])
        except ValueError:
            pass
        lc = r["LCSC"]
        link = f'<a href="https://www.lcsc.com/product-detail/{lc}.html">{lc}</a>' if lc else ""
        out.append(f'<tr><td>{html.escape(r["Designators"])}</td><td>{r["Qty"]}</td><td>{html.escape(r["Value"])}</td>'
                   f'<td>{html.escape(r["Description"])}</td><td>{html.escape(r["MPN"])}</td><td>{link}</td>'
                   f'<td>{r["Unit price USD"]}</td></tr>')
    out.append("</tbody></table>")
    return "\n".join(out), total, sum(int(r["Qty"]) for r in rows), len(rows)


BOARDS = [("upper", "Upper board - flight controller", "6-layer, 1.6 mm, 31.5 x 48 mm"),
          ("lower", "Lower board - power", "4-layer, 1.6 mm, 2 oz outer copper, 31.5 x 48 mm"),
          ("service", "Service board - USB / buzzer / boot", "2-layer, 1.6 mm, 18 x 32 mm")]


def main():
    svgs = pinouts()
    pinout_md()
    vj = os.path.join(DOCS, "verification.json")
    checks = json.load(open(vj)) if os.path.exists(vj) else {}
    cards, boms, grand = [], [], 0.0
    for b, title, sub in BOARDS:
        s = summary(b)
        table, total, nparts, nlines = bom_table(b)
        grand += total
        # badge from the committed verification results; build/<board>/summary.json is only a local
        # by-product of the last full build and goes stale when a board file is patched in place
        mine = [c for c in checks.get("checks", []) if c["name"].startswith(b + ": ")
                and any(k in c["name"] for k in ("(KiCad ERC)", "(KiCad DRC)", "fully routed", "matches schematic"))]
        if len(mine) == 4:
            ok = all(c["ok"] for c in mine)
        else:
            ok = s and not s.get("drc") and not s.get("unconnected") and not s.get("parity") and not s.get("netlist_diffs")
        badge = '<span class="ok">ERC / DRC clean</span>' if ok else '<span class="warn">work in progress</span>'
        cards.append(f'''
<article class="board" id="{b}">
  <h3>{title} {badge}</h3>
  <p class="sub">{sub} &middot; {s.get("parts", "?")} parts &middot; {s.get("nets", "?")} nets</p>
  <div class="imgs">
    <a href="boards/{b}/{b}-top.png"><img loading="lazy" src="boards/{b}/{b}-top.png" alt="{title}, top"></a>
    <a href="boards/{b}/{b}-bottom.png"><img loading="lazy" src="boards/{b}/{b}-bottom.png" alt="{title}, bottom"></a>
    <a href="boards/{b}/{b}-angle-top.png"><img loading="lazy" src="boards/{b}/{b}-angle-top.png" alt="{title}, angled"></a>
  </div>
  <p class="links">
    <a href="boards/{b}/{b}-schematic.pdf">Schematic (PDF)</a>
    <a href="{REPO}/tree/main/hardware/{b}">KiCad project</a>
    <a href="{REPO}/tree/main/fab/{b}">Gerbers, BOM, placement</a>
    <a href="boards/{b}/{b}.step">STEP</a>
    <a href="boards/{b}/{b}.glb">GLB</a>
  </p>
  <details><summary>Bill of materials: {nlines} lines, {nparts} parts, about ${total:.2f} in components</summary>{table}</details>
  <details><summary>Copper layers and assembly drawings</summary><div class="layers">
    {"".join(f'<figure><img loading="lazy" src="boards/{b}/{f}"><figcaption>{f.replace(b + "-", "").replace(".svg", "").replace("_", ".")}</figcaption></figure>'
             for f in sorted(os.listdir(os.path.join(DOCS, "boards", b))) if f.endswith(".svg"))}
  </div></details>
</article>''')
    vrows = "".join(f'<tr><td>{html.escape(c["name"])}</td><td class="{"pass" if c["ok"] else "fail"}">'
                    f'{"PASS" if c["ok"] else "FAIL"}</td><td>{html.escape(c["detail"])}</td></tr>'
                    for c in checks.get("checks", []))
    page = TEMPLATE.replace("{{CARDS}}", "\n".join(cards)).replace("{{VROWS}}", vrows) \
        .replace("{{REPO}}", REPO).replace("{{TOTAL}}", f"{grand:.0f}") \
        .replace("{{DATE}}", checks.get("date", ""))
    for k, v in svgs.items():
        page = page.replace("{{SVG:" + k + "}}", v)
    with open(os.path.join(DOCS, "index.html"), "w") as f:
        f.write(page)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("site written to", DOCS)


TEMPLATE = open(os.path.join(HERE, "site_template.html")).read() if os.path.exists(
    os.path.join(HERE, "site_template.html")) else ""

if __name__ == "__main__":
    main()
