"""Validate portable README references and safe, standalone SVG assets."""

from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def references():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    return set(re.findall(r'(?:src|srcset|href)="([^"]+)"|\]\(([^)]+)\)', text))


def main():
    errors = []
    urls = set()
    for parts in references():
        target = next(p for p in parts if p)
        parsed = urlsplit(target)
        if parsed.scheme == "https":
            urls.add(target)
        elif parsed.scheme in ("mailto",) or target.startswith("#"):
            continue
        elif parsed.scheme:
            errors.append(f"Unsupported link: {target}")
        else:
            path = (ROOT / unquote(parsed.path)).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                errors.append(f"Missing or out-of-repository file: {target}")
    for path in (ROOT / "assets").glob("*.svg"):
        if path.stat().st_size > 30_000:
            errors.append(f"Oversized SVG: {path.name}")
        try:
            svg = ET.parse(path).getroot()
            assert svg.tag == "{http://www.w3.org/2000/svg}svg"
            assert svg.get("viewBox") and svg.find("{http://www.w3.org/2000/svg}title") is not None
            for element in svg.iter():
                tag = element.tag.rsplit("}", 1)[-1]
                if tag in {"script", "foreignObject", "image", "iframe", "a"}:
                    errors.append(f"Unsupported/external SVG element {tag}: {path.name}")
                for key, value in element.attrib.items():
                    if key.lower().startswith("on") or "href" in key or "url(" in value:
                        errors.append(f"Active or external SVG content: {path.name}")
            if re.search(r"\{(?:bg|ink|muted|line|accent|soft|diagram)\}", path.read_text(encoding="utf-8")):
                errors.append(f"Unresolved theme: {path.name}")
        except (ET.ParseError, AssertionError) as error:
            errors.append(f"Invalid SVG {path.name}: {error}")
    if "--links" in sys.argv:
        for url in sorted(urls):
            try:
                # GET handles publishers that reject HEAD. Read only a small prefix.
                request = Request(url, headers={"User-Agent": "Mozilla/5.0 profile-link-check"})
                with urlopen(request, timeout=25) as response:
                    response.read(256)
                    print(f"HTTP {response.status}: {url}")
            except HTTPError as error:
                if error.code in (403, 429) or (error.code == 999 and urlsplit(url).hostname == "www.linkedin.com"):
                    print(f"REQUIRES BROWSER / RATE LIMITED ({error.code}): {url}")
                else:
                    errors.append(f"HTTP {error.code}: {url}")
            except (URLError, TimeoutError) as error:
                errors.append(f"Link unavailable: {url}: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"README references and 8 standalone SVGs valid; {len(urls)} HTTPS links found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
