"""Build getpaydarapp.com into _site/.

Usage: python3 -I tools/build.py [--out _site] [--prices URL_OR_PATH] [--today YYYY-MM-DD] [--content DIR]

Everything is loaded and validated before the output directory is touched, so a failed
run (prices unreachable, bad content) exits 1 and leaves the previous build alone.
"""

import argparse
import http.client
import json
import shutil
import sys
import urllib.request
from datetime import date
from pathlib import Path

# -I leaves the script's own directory off sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sitegen.content import ContentError, load_catalog, load_services, load_site  # noqa: E402
from sitegen.prices import parse_changes  # noqa: E402
from sitegen.site import BuildError, build_site  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load_prices(source: str) -> dict:
    if source.startswith(("https://", "http://")):
        req = urllib.request.Request(source, headers={"User-Agent": "paydar-site-build"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    return json.loads(Path(source).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(ROOT / "_site"))
    parser.add_argument("--prices", help="prices.json URL or file (default: pricesUrl from content/site.json)")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--content", default=str(ROOT / "content"), help="folder with site.json and services/")
    args = parser.parse_args()

    try:
        site = load_site(Path(args.content) / "site.json")
    except (OSError, KeyError, ValueError) as e:
        print(f"Bad content/site.json: {e!r}", file=sys.stderr)
        return 1
    content = Path(args.content)
    try:
        services = load_services(content / "services")
        catalog = load_catalog(content / "catalog.json") if (content / "catalog.json").is_file() else None
        privacy = (content / "privacy.md").read_text(encoding="utf-8") if (content / "privacy.md").is_file() else None
    except ContentError as e:
        print(f"Content problems:\n{e}", file=sys.stderr)
        return 1
    try:
        prices = load_prices(args.prices or site.prices_url)
        parse_changes(prices)
    except (OSError, ValueError, http.client.HTTPException) as e:  # network/file errors, bad JSON, no 'changes'
        print(f"Could not load prices: {e!r}", file=sys.stderr)
        return 1

    # Build next to the output and swap at the end, so a failed build leaves the previous one intact.
    out = Path(args.out)
    tmp = out.with_name(out.name + ".building")
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        warnings = build_site(tmp, site, services, prices, args.today, ROOT / "static", catalog, privacy)
    except BuildError as e:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"Build stopped:\n{e}", file=sys.stderr)
        return 1
    if out.exists():
        shutil.rmtree(out)
    tmp.rename(out)
    print(f"Built {len(services)} service pages into {out}")
    for w in warnings:
        print(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
