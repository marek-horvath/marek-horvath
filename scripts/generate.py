"""Generate the profile's SVG identity, publication panels, and grouped toolkit."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "dark": dict(bg="#0d1b2a", ink="#edf5ff", muted="#afc3d9", line="#29445e",
                 accent="#a9d2ff", soft="#142b42", diagram="#b8d6f4",
                 hero_ink="#ffffff", hero_muted="#e4edff"),
    "light": dict(bg="#f2f6ff", ink="#10233d", muted="#46627e", line="#c6d6e9",
                  accent="#2c5ea8", soft="#e4edfc", diagram="#446489",
                  hero_ink="#10233d", hero_muted="#2d4668"),
}
LINKS = {"portfolio": "Portfolio", "scholar": "Scholar", "linkedin": "LinkedIn", "email": "Email"}
PALETTES = {
    "dark": ("#173c75", "#553990", "#863b68", "#855033", "#17615d", "#175278", "#173c75"),
    "light": ("#c7dcff", "#ddc9f7", "#f4c6db", "#f7dcc1", "#bde8de", "#bce0f3", "#c7dcff"),
}
PUBLICATIONS = json.loads((ROOT / "data/publications.json").read_text(encoding="utf-8"))


def text(x: int, y: int, value: str, size: int = 16, fill: str = "ink",
         family: str = "sans", extra: str = "") -> str:
    families = {"sans": "'Segoe UI',Arial,sans-serif", "serif": "Georgia,'Times New Roman',serif",
                "mono": "Consolas,'Liberation Mono',monospace"}
    return (f'<text x="{x}" y="{y}" font-family="{families[family]}" font-size="{size}" '
            f'fill="{{{fill}}}" {extra}>{escape(value)}</text>')


def wrap(value: str, limit: int) -> list[str]:
    """Wrap at word boundaries; browser validation checks the final font metrics."""
    lines = []
    for word in value.split():
        if not lines or len(lines[-1]) + len(word) + 1 > limit:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


def lines(x: int, y: int, values: list[str], size: int, step: int,
          fill: str = "ink", extra: str = "") -> str:
    return "".join(text(x, y + index * step, value, size, fill, extra=extra)
                   for index, value in enumerate(values))


def gradient(theme: str, width: int, animated: bool = False) -> str:
    period = width * 2
    stops = "".join(f'<stop offset="{i / (len(PALETTES[theme]) - 1):.6f}" stop-color="{color}"/>'
                    for i, color in enumerate(PALETTES[theme]))
    def definition(identifier: str, motion: bool) -> str:
        animation = (f'<animateTransform attributeName="gradientTransform" type="translate" '
                     f'from="-{period} 0" to="0 0" dur="18s" calcMode="linear" '
                     'repeatCount="indefinite"/>') if motion else ""
        return (f'<linearGradient id="{identifier}" gradientUnits="userSpaceOnUse" '
                f'x1="0" y1="0" x2="{period}" y2="0" spreadMethod="repeat">'
                f'{stops}{animation}</linearGradient>')
    return '<defs>' + definition("palette", False) + (definition("palette-flow", True) if animated else "") + '</defs>'


def svg(width: int, height: int, title: str, description: str, body: str, theme: str,
        full_palette: bool = False, animated: bool = False) -> str:
    background = 'url(#palette)' if full_palette else '{bg}'
    flow = (f'<rect id="background-flow" class="moving" width="{width}" height="{height}" '
            'rx="18" fill="url(#palette-flow)"/>') if animated else ""
    content = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
               f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
               f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
               '<style>@media(prefers-reduced-motion:reduce){.moving{display:none}}</style>'
               f'{gradient(theme, width, animated)}'
               f'<rect width="{width}" height="{height}" rx="18" fill="{background}"/>{flow}{body}</svg>\n')
    for key, color in THEMES[theme].items():
        content = content.replace("{" + key + "}", color)
    return content


def network(x: int, y: int, scale: float = 1, animated: bool = True) -> str:
    routes = ["M12 82H48V28H132", "M12 82H132", "M12 82H48V136H132"]
    out = [f'<g transform="translate({x} {y}) scale({scale})" fill="none" '
           'stroke="{diagram}" stroke-width="1.4">']
    out.append('<path d="M12 82H48M48 82V28H132M48 82H132M48 82V136H132"/>')
    for row, lengths in enumerate(((76, 42, 58), (54, 80, 36), (68, 46, 78))):
        yy = 14 + row * 54
        for line, length in enumerate(lengths):
            out.append(f'<path d="M148 {yy + line * 12}h{length}" opacity="{0.8 - line * .18}"/>')
        out.append(f'<circle cx="132" cy="{28 + row * 54}" r="4" fill="none"/>')
    out.append('<circle cx="12" cy="82" r="5" fill="{hero_ink}" stroke="none"/>')
    for index, route in enumerate(routes if animated else []):
        out.append(f'<circle class="moving" r="2.6" fill="{{hero_ink}}" stroke="none" opacity="0.85">'
                   f'<animateMotion dur="{7 + index}s" begin="-{2 + index}s" '
                   f'path="{route}" repeatCount="indefinite"/></circle>')
    out.append('</g>')
    return "".join(out)


def hero(theme: str, mobile: bool = False, animated: bool = True) -> str:
    if mobile:
        w, h = 440, 280
        body = text(26, 35, "RESEARCH / SOFTWARE / EDUCATION", 11, "hero_ink", "mono", 'letter-spacing="1.1"')
        body += text(25, 91, "Marek Horváth", 43, "hero_ink", "serif")
        body += text(27, 123, "PhD · Košice, Slovakia", 15, "hero_muted")
        body += '<path d="M27 145H413" stroke="{hero_ink}" opacity=".3"/>'
        body += text(27, 177, "Assistant Professor at TUKE", 19, "hero_ink")
        body += text(27, 204, "& Software Engineer", 19, "hero_ink")
        body += network(294, 201, .35, animated)
        body += '<path d="M27 250H90" stroke="{hero_ink}" stroke-width="3"/>'
    else:
        w, h = 900, 236
        body = text(36, 40, "RESEARCH / SOFTWARE / EDUCATION", 12, "hero_ink", "mono", 'letter-spacing="1.7"')
        body += text(33, 114, "Marek Horváth", 59, "hero_ink", "serif")
        body += text(459, 112, "PhD", 21, "hero_muted", "serif")
        body += text(37, 156, "Assistant Professor at TUKE & Software Engineer", 19, "hero_ink")
        body += text(37, 195, "Košice, Slovakia", 14, "hero_muted")
        body += network(620, 30, animated=animated)
        body += '<path d="M37 214H100" stroke="{hero_ink}" stroke-width="3"/>'
    return svg(w, h, "Marek Horváth, PhD", "Assistant Professor at TUKE and Software Engineer, "
               "Košice, Slovakia. A continuous full-palette gradient flows from left to right. "
               "Reduced-motion preference is respected.", body, theme, full_palette=True, animated=animated)


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


def section(kind: str, theme: str, mobile: bool = False) -> str:
    w, h = (440, 104) if mobile else (900, 104)
    heading, label, count = ("Journal articles", "01 / RESEARCH", "03 ARTICLES") if kind == "journals" else ("arXiv preprints", "02 / RESEARCH", "02 PREPRINTS")
    body = text(26 if mobile else 32, 33, label, 11, "hero_muted", "mono", 'letter-spacing="1.6"')
    body += text(25 if mobile else 30, 77, heading, 31, "hero_ink", "serif")
    if not mobile:
        body += text(864, 72, count, 11, "hero_muted", "mono", 'text-anchor="end" letter-spacing="1.1"')
    return svg(w, h, heading, heading + ", selected research publications", body, theme, full_palette=True)


def publication(paper: dict, number: int, theme: str, mobile: bool = False) -> str:
    w = 440 if mobile else 900
    x = 26 if mobile else 80
    titles = wrap(paper["title"], 37 if mobile else 66)
    authors = wrap(paper["authors"], 47 if mobile else 106)
    title_y = 68 if mobile else 45
    title_step = 26 if mobile else 29
    author_y = title_y + len(titles) * title_step + 12
    author_step = 22 if mobile else 19
    venue_y = author_y + len(authors) * author_step + 20
    h = venue_y + (57 if mobile else 28)
    body = f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="17" fill="none" stroke="{{line}}" stroke-width="1.5"/>'
    body += f'<rect x="26" y="0" width="{w - 52}" height="3" rx="1.5" fill="url(#palette)"/>'
    if mobile:
        body += text(26, 30, f"{number:02d} / " + ("JOURNAL" if paper["kind"] == "journal" else "PREPRINT"), 10, "accent", "mono", 'letter-spacing="1.2"')
    else:
        body += text(28, 43, f"{number:02d}", 15, "accent", "mono")
    body += lines(x, title_y, titles, 20 if mobile else 22, title_step, extra='font-weight="600"')
    body += lines(x, author_y, authors, 15 if mobile else 14, author_step, "muted")
    if mobile:
        body += text(x, venue_y, paper["venue"], 16, "accent", extra='font-weight="600"')
        body += text(x, venue_y + 24, paper["details"], 14, "muted", "mono")
    else:
        body += text(x, venue_y, paper["venue"] + "  /  " + paper["details"], 13, "accent")
    arrow_y = 29 if mobile else 42
    arrow_x = w - 35
    body += f'<path d="M{arrow_x - 7} {arrow_y + 5}l10-10m-8 0h8v8" fill="none" stroke="{{accent}}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
    return svg(w, h, paper["title"], f"{paper['authors']}. {paper['venue']}, {paper['details']}.", body, theme)


def toolkit(theme: str, mobile: bool = False) -> str:
    w, h = (440, 556) if mobile else (900, 290)
    body = f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="17" fill="none" stroke="{{line}}" stroke-width="1.5"/>'
    body += f'<rect x="26" width="{w - 52}" height="4" rx="2" fill="url(#palette)"/>'
    body += text(27 if mobile else 32, 38, "03 / PRACTICE", 11, "accent", "mono", 'letter-spacing="1.6"')
    body += text(25 if mobile else 30, 80, "Technology & tools", 31, family="serif")
    groups = [
        ("Research", ["Python", "Machine learning", "Static analysis · BibTeX"], "#699de0"),
        ("Web", ["Vue · Angular", "JavaScript · HTML/CSS", "UI/UX"], "#b28bdc"),
        ("Development & teaching", ["Git · GitLab", "Docker · Selenium", "C · Godot"], "#60b8b0"),
    ]
    for index, (heading, items, color) in enumerate(groups):
        x, y = (28, 125 + index * 140) if mobile else (32 + index * 289, 131)
        body += f'<rect x="{x}" y="{y - 15}" width="3" height="20" rx="1.5" fill="{color}"/>'
        body += text(x + 14, y, heading, 19 if mobile else 17, extra='font-weight="600"')
        body += lines(x + 14, y + 32, items, 17 if mobile else 15, 25, "muted")
        if mobile and index < 2:
            body += f'<path d="M28 {y + 110}H412" stroke="{{line}}"/>'
        elif not mobile and index < 2:
            body += f'<path d="M{x + 270} 115V251" stroke="{{line}}"/>'
    return svg(w, h, "Technology & tools", "Research: Python, machine learning, static analysis, BibTeX. "
               "Web: Vue, Angular, JavaScript, HTML/CSS, UI/UX. Development and teaching: Git, GitLab, Docker, Selenium, C, Godot.", body, theme)


def outputs() -> dict[Path, str]:
    result = {}
    for theme in THEMES:
        for mobile in (False, True):
            suffix = ("mobile-" if mobile else "") + theme
            result[ROOT / f"assets/hero-{suffix}.svg"] = hero(theme, mobile)
            result[ROOT / f"assets/hero-{suffix}-still.svg"] = hero(theme, mobile, animated=False)
            result[ROOT / f"assets/research-journals-{suffix}.svg"] = section("journals", theme, mobile)
            result[ROOT / f"assets/research-preprints-{suffix}.svg"] = section("preprints", theme, mobile)
            result[ROOT / f"assets/toolkit-{suffix}.svg"] = toolkit(theme, mobile)
            for number, paper in enumerate(PUBLICATIONS, 1):
                result[ROOT / f"assets/paper-{paper['id']}-{suffix}.svg"] = publication(paper, number, theme, mobile)
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
