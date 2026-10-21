"""Generate the profile's own SVG assets. Python 3.11+, standard library only."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OWNER = "marek-horvath"
SNAPSHOT = ROOT / "data/activity.json"
THEMES = {
    "dark": dict(bg="#0d1b2a", ink="#edf5ff", muted="#a4bad0", line="#29445e",
                 accent="#9bc8fa", soft="#142b42", diagram="#688caf"),
    "light": dict(bg="#eef6ff", ink="#10233d", muted="#46627e", line="#bfd2e6",
                  accent="#2c5ea8", soft="#e0edfb", diagram="#6486a8"),
}


def request_json(url: str, token: str | None = None) -> object:
    headers = {"User-Agent": "marek-horvath-profile", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=20) as response:
                return json.load(response)
        except HTTPError as error:
            # Never print response bodies or credentials. Bound all retry waits.
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"GitHub API returned HTTP {error.code}") from None
            delay = min(10, max(1, int(error.headers.get("Retry-After", "2"))))
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("GitHub API unavailable after three attempts") from None
            delay = 2 ** attempt
        time.sleep(delay)
    raise RuntimeError("GitHub API unavailable")


def validate_snapshot(data: dict) -> None:
    if set(data) != {"owner", "as_of", "repositories"} or data["owner"] != OWNER:
        raise ValueError("Unexpected snapshot schema or owner")
    datetime.strptime(data["as_of"], "%Y-%m-%d")
    names = set()
    for repo in data["repositories"]:
        if set(repo) != {"name", "language", "pushed_at"}:
            raise ValueError("Snapshot contains unexpected fields")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", repo["name"]) or repo["name"] in names:
            raise ValueError("Invalid or duplicate repository name")
        names.add(repo["name"])
        if repo["language"] is not None and not isinstance(repo["language"], str):
            raise ValueError("Invalid repository language")
        datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")
    if not names:
        raise ValueError("Empty repository snapshot")


def fetch_snapshot(token: str | None = None) -> dict:
    repos = []
    for page in range(1, 101):
        batch = request_json(f"https://api.github.com/users/{OWNER}/repos?type=owner&per_page=100&page={page}", token)
        if not isinstance(batch, list):
            raise ValueError("Expected a repository list")
        for repo in batch:
            if (repo.get("private") is not False or repo.get("visibility") != "public"
                    or repo.get("fork") or repo.get("archived") or repo.get("disabled")
                    or repo.get("owner", {}).get("login") != OWNER
                    or repo.get("name") == OWNER or not repo.get("pushed_at")
                    or not repo.get("size")):
                continue
            # Persist only three public, allowlisted fields. Never save raw API responses.
            repos.append({key: repo.get(key) for key in ("name", "language", "pushed_at")})
        if len(batch) < 100:
            break
    else:
        raise ValueError("Repository pagination exceeded its limit")
    data = {"owner": OWNER, "as_of": datetime.now(timezone.utc).date().isoformat(),
            "repositories": sorted(repos, key=lambda r: r["name"].lower())}
    validate_snapshot(data)
    return data


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
               f'<rect width="{width}" height="{height}" rx="18" fill="{{bg}}"/>{body}</svg>\n')
    for key, color in THEMES[theme].items():
        content = content.replace("{" + key + "}", color)
    return content


def fingerprint(x: int, y: int, scale: float = 1) -> str:
    """An abstract syntax tree merging into code lines; decorative, never measured data."""
    out = [f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{{diagram}}" stroke-width="1.4">']
    out.append('<path d="M12 82H48M48 82V28H96M48 82H96M48 82V136H96M96 28H132M96 82H132M96 136H132"/>')
    for row, lengths in enumerate(((76, 42, 58), (54, 80, 36), (68, 46, 78))):
        yy = 14 + row * 54
        for line, length in enumerate(lengths):
            out.append(f'<path d="M148 {yy + line * 12}h{length}" opacity="{0.75 - line * .2}"/>')
        out.append(f'<circle cx="132" cy="{28 + row * 54}" r="4" fill="{{bg}}"/>')
    out.extend(['<circle cx="12" cy="82" r="5" fill="{accent}" stroke="none"/>', '</g>'])
    return "".join(out)


def hero(theme: str, mobile: bool = False) -> str:
    if mobile:
        w, h = 440, 338
        body = text(26, 37, "RESEARCH / SOFTWARE / EDUCATION", 11, "accent", "mono", 'letter-spacing="1.1"')
        body += text(25, 100, "Marek Horváth", 43, family="serif")
        body += text(27, 134, "PhD · Košice, Slovakia", 15, "muted")
        body += '<path d="M27 157H413" stroke="{line}"/>'
        body += text(27, 188, "Assistant Professor at TUKE", 19)
        body += text(27, 215, "& Software Engineer", 19)
        body += text(27, 259, "Source code. Human patterns.", 23, family="serif")
        body += text(27, 288, "Studying authorship. Building tools to learn.", 14, "muted")
        body += '<path d="M27 314H90" stroke="{accent}" stroke-width="3"/>'
    else:
        w, h = 900, 310
        body = text(36, 43, "RESEARCH / SOFTWARE / EDUCATION", 12, "accent", "mono", 'letter-spacing="1.7"')
        body += text(33, 117, "Marek Horváth", 59, family="serif")
        body += text(459, 115, "PhD", 21, "muted", "serif")
        body += text(37, 158, "Assistant Professor at TUKE & Software Engineer", 19)
        body += '<path d="M37 185H555" stroke="{line}"/>'
        body += text(35, 226, "Source code. Human patterns.", 29, family="serif")
        body += text(37, 258, "Studying authorship. Building tools to learn.", 16, "muted")
        body += fingerprint(617, 78, 1)
        body += text(637, 286, "KOŠICE, SLOVAKIA", 11, "muted", "mono", 'letter-spacing="1.5"')
        body += '<path d="M37 285H100" stroke="{accent}" stroke-width="3"/>'
    return svg(w, h, "Marek Horváth, PhD", "Assistant Professor at TUKE and Software Engineer. "
               "Source code analysis, programmer attribution, and programming education.", body, theme)


def short_name(name: str, limit: int) -> str:
    return name if len(name) <= limit else name[:limit - 1] + "…"


def activity(data: dict, theme: str, mobile: bool = False) -> str:
    selected = sorted(data["repositories"], key=lambda r: (r["pushed_at"], r["name"]), reverse=True)[:6]
    as_of = datetime.strptime(data["as_of"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    w, h = (440, 500) if mobile else (900, 350)
    pad = 26 if mobile else 36
    body = text(pad, 36, "FROM THE REPOSITORIES", 11, "accent", "mono", 'letter-spacing="1.4"')
    body += text(pad, 75, "Latest public work", 30, family="serif")
    body += text(pad, 101, f"Snapshot · {data['as_of']} UTC", 13, "muted")
    if not mobile:
        body += text(600, 99, "PUSH RECENCY / LAST 90 DAYS", 10, "muted", "mono")
    dates = []
    for i, repo in enumerate(selected):
        pushed = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        dates.append(f"{repo['name']}: {pushed.date().isoformat()}")
        age = max(0, (as_of.date() - pushed.date()).days)
        strength = max(0, 1 - age / 90)
        if mobile:
            y = 140 + i * 54
            body += text(pad, y, short_name(repo["name"], 33), 16)
            body += text(pad, y + 21, repo["language"] or "—", 12, "muted")
            body += text(413, y + 21, pushed.date().isoformat(), 12, "muted", "mono", 'text-anchor="end"')
            body += f'<path d="M26 {y + 31}H414" stroke="{{line}}"/>'
        else:
            y = 142 + i * 30
            body += text(pad, y, short_name(repo["name"], 35), 15)
            body += text(385, y, repo["language"] or "—", 12, "muted")
            body += text(510, y, pushed.date().isoformat(), 12, "muted", "mono")
            body += f'<rect x="645" y="{y - 9}" width="216" height="4" rx="2" fill="{{line}}"/>'
            if strength:
                body += f'<rect x="645" y="{y - 9}" width="{max(4, round(216 * strength))}" height="4" rx="2" fill="{{accent}}"/>'
    footer = "Public, original repositories · GitHub API" if mobile else "Public, original repositories · Longer bar = more recent push · GitHub API"
    body += text(pad, h - 24, footer, 11, "muted")
    return svg(w, h, f"Public repository activity as of {data['as_of']}", "; ".join(dates), body, theme)


def outputs(data: dict) -> dict[Path, str]:
    result = {}
    for theme in THEMES:
        for mobile in (False, True):
            suffix = ("mobile-" if mobile else "") + theme
            result[ROOT / f"assets/hero-{suffix}.svg"] = hero(theme, mobile)
            result[ROOT / f"assets/activity-{suffix}.svg"] = activity(data, theme, mobile)
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--refresh", action="store_true", help="Fetch public metadata; preserve the previous snapshot on failure")
    mode.add_argument("--check", action="store_true", help="Verify committed assets without writes or network")
    parser.add_argument("--require-fresh", action="store_true", help="Fail if a requested refresh fails")
    args = parser.parse_args()
    data = None
    if args.refresh:
        try:
            data = fetch_snapshot(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
        except (RuntimeError, ValueError, KeyError, TypeError) as error:
            print(f"Refresh unavailable: {error}. Keeping the previous dated snapshot.", file=sys.stderr)
            if args.require_fresh or not SNAPSHOT.exists():
                return 1
    fresh = data is not None
    if data is None:
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    validate_snapshot(data)
    generated = outputs(data)
    if args.check:
        stale = [str(p.relative_to(ROOT)) for p, content in generated.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != content]
        if stale:
            print("Assets need regeneration: " + ", ".join(stale), file=sys.stderr)
            return 1
    else:
        # Render and validate everything before replacing any saved output.
        from xml.etree import ElementTree
        for content in generated.values():
            ElementTree.fromstring(content)
        if fresh:
            write_if_changed(SNAPSHOT, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        for path, content in generated.items():
            write_if_changed(path, content)
    print(f"Verified {len(generated)} assets; public snapshot {data['as_of']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
