"""Copies what the site needs from the Paydar app's service catalog (run by hand, outputs committed).

    python3 -I tools/import_catalog.py ~/Code/subsly/native/PaydarKit/Resources

Writes content/catalog.json (name, brand colour, typical US price, category and, for services with
no App Store icon in the app, the simple-icons glyph) and static/logos/<id>.webp (96 px, from the
app's ServiceIcons). The same data the app's onboarding and Add screen use.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The homepage chips, in the order shown; the first four start picked (the free plan's limit).
HOME_CHIPS = ["netflix", "spotify", "icloud", "disney-plus", "youtube-premium", "hbo-max", "playstation-plus",
              "amazon-prime", "apple-music", "xbox-game-pass", "hulu", "peacock",
              "paramount-plus", "duolingo"]


def main() -> int:
    res = Path(sys.argv[1]).expanduser()
    services = {s["id"]: s for s in json.loads((res / "services.json").read_text())}
    glyphs = json.loads((res / "glyphs.json").read_text())
    icons = res / "ServiceIcons.xcassets"
    guide_ids = [p.stem for p in sorted((ROOT / "content" / "services").glob("*.json"))]
    out, logos = {}, ROOT / "static" / "logos"
    logos.mkdir(parents=True, exist_ok=True)
    for sid in dict.fromkeys(HOME_CHIPS + guide_ids):
        s = services[sid]
        entry = {"name": s["name"], "color": s["color"], "price": s.get("defaultPrice"),
                 "frequency": s.get("defaultFrequency", "monthly"), "category": s["category"]}
        png = icons / f"{sid}.imageset" / f"{sid}.png"
        if png.is_file():
            subprocess.run(["cwebp", "-quiet", "-q", "86", "-resize", "96", "96", str(png), "-o",
                            str(logos / f"{sid}.webp")], check=True)
            entry["logo"] = f"/logos/{sid}.webp"
        elif sid in glyphs:
            entry["glyph"] = glyphs[sid]
        out[sid] = entry
    data = {"homeChips": HOME_CHIPS, "services": out}
    (ROOT / "content" / "catalog.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(out)} services, {sum('logo' in e for e in out.values())} logos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
