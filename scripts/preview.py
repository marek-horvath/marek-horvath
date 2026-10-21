"""Review GitHub-rendered Markdown with local assets; requires optional Playwright."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / ".preview"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    PREVIEW.mkdir(exist_ok=True)
    gh = shutil.which("gh") or "C:/Program Files/GitHub CLI/gh.exe"
    payload = json.dumps({"text": (ROOT / "README.md").read_text(encoding="utf-8"), "mode": "gfm"})
    result = subprocess.run([gh, "api", "markdown", "--input", "-"], input=payload.encode(), capture_output=True, check=True)
    rendered = result.stdout.decode("utf-8")
    css = """
    * {box-sizing:border-box} body {margin:0;background:#fff;color:#1f2328;font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    main {max-width:962px;margin:30px auto;padding:30px;border:1px solid #d1d9e0;border-radius:6px}
    p {margin:0 0 16px} h3 {margin:26px 0 16px;font-size:20px} h1,h2 {border-bottom:1px solid #d1d9e0}
    a {color:#0969da;text-decoration:none} a:hover {text-decoration:underline} img {max-width:100%;height:auto;vertical-align:middle}
    table {width:100%;border-spacing:0;border-collapse:collapse;margin:0 0 16px;font-size:15px}
    td,th {border:1px solid #d1d9e0;padding:10px 14px;text-align:left} tr:nth-child(2n) {background:#f6f8fa}
    td:first-child {width:29%} strong {font-weight:600} sub {font-size:12px} .anchor {display:none}
    @media(prefers-color-scheme:dark) {body {background:#0d1117;color:#e6edf3} main,td,th,h1,h2 {border-color:#30363d} a {color:#79c0ff} tr:nth-child(2n) {background:#161b22}}
    @media(max-width:600px) {main {margin:0;padding:16px;border:0} table {font-size:14px} td,th {padding:8px} td:first-child {width:31%}}
    """
    document = f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><base href="/"><style>{css}</style></head><body><main>{rendered}</main></body></html>'
    (PREVIEW / "readme.html").write_text(document, encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            reports = []
            for mobile in (False, True):
                for theme in ("dark", "light"):
                    viewport = {"width": 390, "height": 844} if mobile else {"width": 1280, "height": 1000}
                    page = browser.new_page(viewport=viewport, color_scheme=theme, device_scale_factor=1)
                    page.goto(base + "/.preview/readme.html", wait_until="networkidle")
                    images = page.locator("main img").evaluate_all("items => items.map(i => ({src:i.currentSrc,complete:i.complete,width:i.naturalWidth}))")
                    assert len(images) == 2 and all(i["complete"] and i["width"] for i in images), images
                    overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                    assert not overflow, f"Horizontal overflow at {viewport}"
                    mode = "mobile" if mobile else "desktop"
                    page.screenshot(path=str(PREVIEW / f"{mode}-{theme}.png"), full_page=True)
                    reports.append({"mode": mode, "theme": theme, "images": images, "horizontal_overflow": overflow})
                    page.close()
            # Check actual browser font metrics, which XML validation cannot detect.
            for asset in sorted((ROOT / "assets").glob("*.svg")):
                page = browser.new_page()
                page.goto(base + "/assets/" + asset.name)
                clipped = page.evaluate("""() => {
                    const root = document.querySelector('svg'); const v = root.viewBox.baseVal;
                    return [...root.querySelectorAll('text')].filter(t => {
                      const b=t.getBBox(); return b.x < 0 || b.y < 0 || b.x+b.width > v.width || b.y+b.height > v.height;
                    }).map(t => t.textContent);
                }""")
                assert not clipped, (asset.name, clipped)
                page.close()
            reference = browser.new_page(viewport={"width": 1280, "height": 1000})
            reference.goto("https://marek-horvath.github.io/portfolio/", wait_until="networkidle")
            reference.screenshot(path=str(PREVIEW / "portfolio-reference.png"), full_page=False)
            browser.close()
        print(json.dumps(reports, indent=2))
        print("Reviewed four layouts, all SVG text bounds, and the live portfolio reference.")
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
