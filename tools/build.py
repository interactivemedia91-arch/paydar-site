"""Build getpaydarapp.com into _site/.

Usage: python3 -I tools/build.py [--out _site] [--prices URL_OR_PATH] [--today YYYY-MM-DD]

Everything is loaded and validated before the output directory is touched, so a failed
run (prices unreachable, bad content) exits 1 and leaves the previous build alone.
"""

import argparse
import json
import shutil
import sys
import urllib.request
from datetime import date
from pathlib import Path

# -I leaves the script's own directory off sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sitegen.content import ContentError, load_services, load_site  # noqa: E402
from sitegen.prices import parse_changes  # noqa: E402
from sitegen.site import build_site  # noqa: E402

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
    args = parser.parse_args()

    try:
        site = load_site(ROOT / "content" / "site.json")
        services = load_services(ROOT / "content" / "services")
        prices = load_prices(args.prices or site.prices_url)
        parse_changes(prices)  # validate before touching the output
    except ContentError as e:
        print(f"Content problems:\n{e}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:  # network/file errors, bad JSON, no 'changes' list
        print(f"Could not load prices: {e}", file=sys.stderr)
        return 1

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    warnings = build_site(out, site, services, prices, args.today, ROOT / "static")
    print(f"Built {len(services)} service pages into {out}")
    for w in warnings:
        print(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
