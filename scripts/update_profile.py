"""Apply verified profile metadata via authenticated gh; never persists credentials."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOCIALS = ["https://www.linkedin.com/in/horvathmar/",
           "https://scholar.google.com/citations?user=9q0s2u4AAAAJ&hl=en"]


def api(gh, endpoint, method="GET", data=None):
    args = [gh, "api", endpoint, "--method", method]
    if data is not None:
        args += ["--input", "-"]
    result = subprocess.run(args, input=json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None,
                            capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return json.loads(result.stdout) if result.stdout.strip() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    metadata = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    assert len(metadata["bio"]) <= 160
    if not args.apply:
        print(json.dumps({"profile": metadata, "social_links": SOCIALS}, ensure_ascii=False, indent=2))
        return 0
    gh = shutil.which("gh")
    if not gh:
        candidate = Path("C:/Program Files/GitHub CLI/gh.exe")
        gh = str(candidate) if candidate.exists() else None
    if not gh:
        raise RuntimeError("Install and authenticate the official GitHub CLI first")
    user = api(gh, "user")
    if user["login"] != "marek-horvath":
        raise RuntimeError("Refusing to modify a different authenticated account")
    social_before = api(gh, "user/social_accounts")
    backup = ROOT / ".preview/profile-before.json"
    if not backup.exists():
        backup.parent.mkdir(exist_ok=True)
        backup.write_text(json.dumps({"profile": {key: user.get(key) for key in metadata},
                                     "social_links": social_before}, ensure_ascii=False, indent=2), encoding="utf-8")
    updated = api(gh, "user", "PATCH", metadata)
    for key, value in metadata.items():
        if updated.get(key) != value:
            raise RuntimeError(f"GitHub did not retain the intended {key}")
    existing = {item["url"].rstrip("/") for item in social_before}
    missing = [url for url in SOCIALS if url.rstrip("/") not in existing]
    if len(social_before) + len(missing) > 4:
        raise RuntimeError("Profile fields updated; social links need manual selection because four slots are occupied")
    if missing:
        api(gh, "user/social_accounts", "POST", {"account_urls": missing})
    actual = api(gh, "user/social_accounts")
    if not {url.rstrip("/") for url in SOCIALS} <= {item["url"].rstrip("/") for item in actual}:
        raise RuntimeError("Profile fields updated; social links require manual verification")
    print("Verified live profile metadata for marek-horvath and both social links.")
    print(json.dumps({key: updated[key] for key in metadata}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
