"""Convert everything in art/raw/** to WebP in art/live/** (same sub-folders).

Usage (from the project root):
    python tools/make_webp.py            # convert new or changed images only
    python tools/make_webp.py --force    # redo everything

Output names are lowercase (Spyro.png -> spyro.webp) so paths also work on
GitHub Pages, which is case-sensitive. Transparency is kept.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW, LIVE = ROOT / "art" / "raw", ROOT / "art" / "live"
MAX_W = 1600          # longest side in pixels; plenty for a full-screen creature
QUALITY = 85
EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

Image.MAX_IMAGE_PIXELS = None   # allow very large source art

force = "--force" in sys.argv
done = 0
for src in sorted(RAW.rglob("*")):
    if src.suffix.lower() not in EXTS:
        continue
    out = LIVE / src.relative_to(RAW).with_name(src.stem.lower().replace(" ", "-") + ".webp")
    if not force and out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        continue
    out.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im.load()
        w, h = im.size
        if max(w, h) > MAX_W:
            k = MAX_W / max(w, h)
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") or "transparency" in im.info else "RGB")
        im.save(out, "WEBP", quality=QUALITY, method=6)
    print(f"{src.relative_to(ROOT)}  {src.stat().st_size/1e6:.1f} MB  ->  {out.relative_to(ROOT)}  {out.stat().st_size/1e3:.0f} KB  ({im.size[0]}x{im.size[1]})")
    done += 1
print(f"{done} converted")
