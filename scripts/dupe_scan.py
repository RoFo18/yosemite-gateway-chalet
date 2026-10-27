#!/usr/bin/env python3
"""Find duplicate and near-duplicate photos by their pixels, not their names.

    python3 scripts/dupe_scan.py

Hashes every file in src/assets/source with perceptual and difference hashes,
groups images that look the same (including crops and re-exports), and lists
the pages each named image appears on in dist/ (gallery excluded).
"""
import glob, json, os, re, sys
import imagehash
from PIL import Image, ImageOps
try:
    from pillow_heif import register_heif_opener; register_heif_opener()
except ImportError:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from images import NAMES  # noqa: E402

files = sorted(glob.glob(os.path.join(ROOT, "src", "assets", "source", "*")))
H = {}
for f in files:
    try:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    except Exception:
        continue
    # centre crop too, so a cropped re-export still matches
    w, h = im.size
    c = im.crop((w // 8, h // 8, w - w // 8, h - h // 8))
    H[os.path.basename(f)] = (imagehash.phash(im), imagehash.dhash(im), imagehash.phash(c))

names = list(H)
parent = {n: n for n in names}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
for i, a in enumerate(names):
    for b in names[i + 1:]:
        pa, da, ca = H[a]; pb, db, cb = H[b]
        if (pa - pb <= 10 and da - db <= 14) or ca - cb <= 8 or pa - pb <= 6:
            parent[find(a)] = find(b)
groups = {}
for n in names:
    groups.setdefault(find(n), []).append(n)
groups = [sorted(g) for g in groups.values() if len(g) > 1]

usage = {}
same_page = []
for p in glob.glob(os.path.join(ROOT, "dist", "**", "*.html"), recursive=True):
    rel = "/" + os.path.relpath(p, os.path.join(ROOT, "dist")).replace("index.html", "")
    if rel.startswith("/gallery/"):
        continue
    html = open(p, encoding="utf-8").read()
    html = re.sub(r"<head>.*?</head>", "", html, flags=re.S)
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    for name in set(re.findall(r"/img/([a-z0-9-]+?)-\d+\.(?:webp|avif)", html)):
        usage.setdefault(name, set()).add(rel)
    shown = re.findall(r'<img[^>]*src="/img/([a-z0-9-]+?)-\d+\.webp', html)
    for name in set(shown):
        if shown.count(name) > 1:
            same_page.append((rel, name, shown.count(name)))

print(f"{len(H)} source images, {len(groups)} look-alike groups\n")
for g in groups:
    print("GROUP:")
    for f in g:
        n = NAMES.get(f, "(not in site)")
        print(f"  {f:55s} {n:38s} {sorted(usage.get(n, []))}")
print("\nIMAGES ON MORE THAN ONE PAGE (gallery excluded):")
multi = {n: p for n, p in usage.items() if len(p) > 1}
for n, p in sorted(multi.items()):
    print(f"  {n:40s} {sorted(p)}")
print(f"\n{len(multi)} image(s) on more than one page")
print("\nSAME PHOTO TWICE ON ONE PAGE:")
for rel, name, n in same_page:
    print(f"  {rel}: {name} x{n}")
print(f"{len(same_page)} page(s) repeat a photo")
