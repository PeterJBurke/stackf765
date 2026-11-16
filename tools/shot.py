#!/usr/bin/env python3
"""Screenshot the documentation site in headless Chromium (used to check the 3D viewer).

    python3 tools/shot.py OUT.png [--view top] [--explode 20] [--width 1280] [--height 2000] [--full]
"""
import functools
import http.server
import os
import sys
import threading
from playwright.sync_api import sync_playwright

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs"))
args = sys.argv[1:]
out = args[0]
opt = {args[i].lstrip("-"): args[i + 1] for i in range(1, len(args) - 1) if args[i].startswith("--") and not args[i + 1].startswith("--")}
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": int(opt.get("width", 1280)), "height": int(opt.get("height", 900))})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text))
    pg.on("pageerror", lambda e: msgs.append("PAGEERROR " + str(e)))
    pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html")
    pg.wait_for_function("document.getElementById('status').textContent !== 'Loading 3D models…'", timeout=120000)
    pg.wait_for_timeout(1500)
    if "explode" in opt:
        pg.evaluate(f"window.__viewer.setExplode({opt['explode']}); window.__viewer.frame()")
    if "view" in opt:
        pg.evaluate(f"window.__viewer.view('{opt['view']}')")
    pg.wait_for_timeout(1200)
    if "--full" in args:
        pg.screenshot(path=out, full_page=True)
    else:
        box = pg.locator("#viewer").bounding_box()
        pg.screenshot(path=out, clip=box, animations="disabled")
    print("status:", repr(pg.inner_text("#status")), "| console:", msgs[:6])
    b.close()
