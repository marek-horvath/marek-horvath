"""Generate self-contained animated SVGs and link buttons. Standard library only."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "dark": dict(bg="#0d1b2a", ink="#edf5ff", muted="#a4bad0", line="#29445e",
                 accent="#9bc8fa", soft="#142b42", diagram="#688caf"),
    "light": dict(bg="#eef6ff", ink="#10233d", muted="#46627e", line="#bfd2e6",
                  accent="#2c5ea8", soft="#e0edfb", diagram="#6486a8"),
}
LINKS = {"portfolio": "Portfolio", "scholar": "Scholar", "linkedin": "LinkedIn", "email": "Email"}


def text(x: int, y: int, value: str, size: int = 16, fill: str = "ink",
         family: str = "sans", extra: str = "") -> str:
    families = {"sans": "'Segoe UI',Arial,sans-serif", "serif": "Georgia,'Times New Roman',serif",
                "mono": "Consolas,'Liberation Mono',monospace"}
    return (f'<text x="{x}" y="{y}" font-family="{families[family]}" font-size="{size}" '
            f'fill="{{{fill}}}" {extra}>{escape(value)}</text>')


def svg(width: int, height: int, title: str, description: str, body: str, theme: str) -> str:
    content = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
               f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
               '<style>@media(prefers-reduced-motion:reduce){.moving{display:none}}</style>'
               f'<rect width="{width}" height="{height}" rx="18" fill="{{bg}}"/>{body}</svg>\n')
    for key, color in THEMES[theme].items():
        content = content.replace("{" + key + "}", color)
    return content


def network(x: int, y: int, scale: float = 1, animated: bool = True) -> str:
    """Decorative branching network with slowly moving signals; no measured data."""
    routes = ["M12 82H48V28H132", "M12 82H132", "M12 82H48V136H132"]
    out = [f'<g transform="translate({x} {y}) scale({scale})" fill="none" '
           'stroke="{diagram}" stroke-width="1.4">']
    out.append('<path d="M12 82H48M48 82V28H132M48 82H132M48 82V136H132"/>')
    for row, lengths in enumerate(((76, 42, 58), (54, 80, 36), (68, 46, 78))):
        yy = 14 + row * 54
        for line, length in enumerate(lengths):
            out.append(f'<path d="M148 {yy + line * 12}h{length}" opacity="{0.75 - line * .2}"/>')
        out.append(f'<circle cx="132" cy="{28 + row * 54}" r="4" fill="{{bg}}"/>')
    out.append('<circle cx="12" cy="82" r="5" fill="{accent}" stroke="none"/>')
    for index, route in enumerate(routes if animated else []):
        out.append(f'<circle class="moving" r="2.6" fill="{{accent}}" stroke="none" opacity="0.85">'
                   f'<animateMotion dur="{7 + index}s" begin="-{2 + index}s" '
                   f'path="{route}" repeatCount="indefinite"/></circle>')
    out.append('</g>')
    return "".join(out)


def hero(theme: str, mobile: bool = False, animated: bool = True) -> str:
    if mobile:
        w, h = 440, 280
        body = text(26, 35, "RESEARCH / SOFTWARE / EDUCATION", 11, "accent", "mono", 'letter-spacing="1.1"')
        body += text(25, 91, "Marek Horváth", 43, family="serif")
        body += text(27, 123, "PhD · Košice, Slovakia", 15, "muted")
        body += '<path d="M27 145H413" stroke="{line}"/>'
        body += text(27, 177, "Assistant Professor at TUKE", 19)
        body += text(27, 204, "& Software Engineer", 19)
        body += network(294, 201, .35, animated)
        body += '<path d="M27 250H90" stroke="{accent}" stroke-width="3"/>'
    else:
        w, h = 900, 236
        body = text(36, 40, "RESEARCH / SOFTWARE / EDUCATION", 12, "accent", "mono", 'letter-spacing="1.7"')
        body += text(33, 114, "Marek Horváth", 59, family="serif")
        body += text(459, 112, "PhD", 21, "muted", "serif")
        body += text(37, 156, "Assistant Professor at TUKE & Software Engineer", 19)
        body += text(37, 195, "Košice, Slovakia", 14, "muted")
        body += network(620, 30, animated=animated)
        body += '<path d="M37 214H100" stroke="{accent}" stroke-width="3"/>'
    return svg(w, h, "Marek Horváth, PhD", "Assistant Professor at TUKE and Software Engineer, "
               "Košice, Slovakia. Decorative animated network; reduced-motion preference is respected.", body, theme)


def button(key: str, theme: str) -> str:
    icons = {
        "portfolio": '<rect x="18" y="15" width="18" height="16" rx="3"/><path d="M18 20H36M23 16V19"/>',
        "scholar": '<path d="M17 18L27 13L37 18L27 23ZM21 21V27Q27 31 33 27V21M37 18V27"/>',
        "linkedin": '<rect x="18" y="14" width="18" height="18" rx="3"/>',
        "email": '<rect x="17" y="16" width="20" height="15" rx="3"/><path d="M18 18L27 24L36 18"/>',
    }
    body = '<rect x=".75" y=".75" width="148.5" height="44.5" rx="11" fill="{soft}" stroke="{line}" stroke-width="1.5"/>'
    body += '<g fill="none" stroke="{accent}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round">' + icons[key] + '</g>'
    if key == "linkedin":
        body += text(21, 27, "in", 11, "accent", extra='font-weight="700"')
    body += text(46, 29, LINKS[key], 15, extra='font-weight="600"')
    body += '<path d="M126 26L133 19M127 19H133V25" fill="none" stroke="{muted}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
    return svg(150, 46, LINKS[key], f"Open {LINKS[key]}", body, theme)


def outputs() -> dict[Path, str]:
    result = {}
    for theme in THEMES:
        for mobile in (False, True):
            suffix = ("mobile-" if mobile else "") + theme
            result[ROOT / f"assets/hero-{suffix}.svg"] = hero(theme, mobile)
            result[ROOT / f"assets/hero-{suffix}-still.svg"] = hero(theme, mobile, animated=False)
        for key in LINKS:
            result[ROOT / f"assets/link-{key}-{theme}.svg"] = button(key, theme)
    return result


def write_if_changed(path: Path, content: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed assets without writes or network")
    args = parser.parse_args()
    generated = outputs()
    for content in generated.values():
        ET.fromstring(content)
    if args.check:
        stale = [str(p.relative_to(ROOT)) for p, content in generated.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != content]
        if stale:
            print("Assets need regeneration: " + ", ".join(stale), file=sys.stderr)
            return 1
    else:
        for path, content in generated.items():
            write_if_changed(path, content)
    print(f"Verified {len(generated)} self-contained SVG assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
