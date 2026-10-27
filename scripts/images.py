#!/usr/bin/env python3
"""Turn the source photos into responsive AVIF and WebP files.

Run this when you add or replace a photo in src/assets/source/, then commit the
results in public/img/ and src/data/images.json. Netlify does not need to run it.

    python3 scripts/images.py

What it does for each photo listed in NAMES:
  1. trims the black letterbox bars baked into the old slideshow images
  2. gives the file a descriptive name
  3. writes AVIF and WebP versions at several widths (never wider than the original)
  4. records width, height and a dominant colour in src/data/images.json
"""
import json
import os

from PIL import Image, ImageChops, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "assets", "source")
OUT = os.path.join(ROOT, "public", "img")
MANIFEST = os.path.join(ROOT, "src", "data", "images.json")
WIDTHS = [480, 800, 1200, 1800]

# source file -> descriptive name used across the site
NAMES = {
    "044-1front2.jpg": "chalet-exterior-carson-peak",
    "the-grounds-gallery-3.jpg": "chalet-lawn-lodgepole-pines",
    "the-grounds-gallery-4.jpg": "chalet-grounds-log-exterior",
    "the-grounds-gallery-5.jpg": "chalet-grounds-hammock-aspens",
    "the-grounds-gallery-6.jpg": "chalet-deck-and-forest",
    "backyard-3.jpg": "guest-in-deep-snow",
    "044-3grand-room.jpg": "grand-room-fireside-gathering",
    "044-3grand-room2.jpg": "grand-room-fireside-evening",
    "grand-room2.jpg": "grand-room-oak-bar-wine",
    "grand-room52.jpg": "grand-room-fireplace-and-bar",
    "grad-room22.jpg": "grand-room-evening-lamplight",
    "dining-room-gallery-1.jpg": "dining-room-timber-table",
    "dining-room-gallery-2.jpg": "dining-room-doorway",
    "dining-room-gallery-3.jpg": "dinner-at-the-chalet",
    "family-kitchen-gallery-1.jpg": "family-room-wood-stove",
    "family-kitchen-gallery-2.jpg": "family-room-evening",
    "family-kitchen-gallery-3.jpg": "kitchen-and-breakfast-bar",
    "family-kitchen-gallery-4.jpg": "kitchen-copper-sink",
    "family-kitchen-gallery-5.jpg": "kitchen-wide-view",
    "family-kitchen-gallery-6.jpg": "family-room-wide-view",
    "master-bedroom-gallery-1.jpg": "master-suite-bed",
    "master-bedroom-gallery-2.jpg": "master-suite-evening",
    "master-bedroom-gallery-3.jpg": "master-suite-window-snow-peaks",
    "elsie-room-gallery-1.jpg": "elsie-room-granite-peak-view",
    "elsie-room-gallery-2.jpg": "elsie-room-claw-foot-tub",
    "elsie-room-gallery-3.jpg": "elsie-room-suite",
    "river-room-gallery-1.jpg": "river-room-suite",
    "river-room-gallery-2.jpg": "river-room-evening",
    "outdoor-hydrotherapy-pool-gallery-1.jpg": "hydrotherapy-tub-night-steam",
    "outdoor-hydrotherapy-pool-gallery-2.jpg": "hydrotherapy-tub-winter-guests",
    "outdoor-hydrotherapy-pool-gallery-3.jpg": "hydrotherapy-tub-and-chalet",
    "spa.jpg": "hydrotherapy-tub-stone-surround",
    "ski-to-the-hydrotherapy-tub-of-the-ygc.jpg": "ski-tracks-to-the-hot-tub",
    "snowshoe-out-backdoor.jpg": "guests-celebrating-in-snow",
    "main-level.jpg": "floorplan-main-level",
    "upper-level.jpg": "floorplan-upper-level",
    "fall-colors-2.jpg": "june-lake-loop-fall-aspens",
    "fall-colors-22.jpg": "june-lake-loop-fall-aspens-wide",
    "fall-colors.jpg": "fall-aspen-meadow-eastern-sierra",
    "img-1287.jpg": "june-lake-fall-reflections",
    "valentine-lake2.jpg": "alpine-lake-below-sierra-peaks",
    "the-region-gallery-6.jpg": "sierra-lake-and-forest",
    "ritter-range2.jpg": "ritter-range-snow",
    "yosemite-park-lodging.jpg": "yosemite-high-country-lake",
    "yosemite.jpg": "tuolumne-granite-reflection",
    "yosemite-3.jpg": "granite-dome-and-pond",
    "yosemite-32.jpg": "granite-boulder-pond",
    "yosemite-gateway-vacation-trees-lake-california-slide1.jpg": "june-lake-loop-mountain-panorama",
    "june-lake-lodging.jpg": "june-lake-chalet-summer",
    "img-3363.jpg": "fall-view-over-yosemite-climber",
    "dscn6179.jpg": "white-mountain-summit-sunrise",
    "dscn6404.jpg": "backcountry-skier-gaylor-peak",
    "dscn6533-001.jpg": "eastern-sierra-sunset-panorama",
    "2012-02-16-12-47-33.pdf000.jpg": "june-mountain-winter-forest",
    "56ski-june-mtn2.jpg": "skiing-june-mountain-corduroy",
    "55fishing.jpg": "fly-fishing-rush-creek",
    "hot-springs.jpg": "hot-creek-eastern-sierra",
    "hotsprings-2.jpg": "natural-hot-spring-soak",
    "ice-climbing-ines-15637.jpg": "ice-climbing-lee-vining-canyon",
    "img-7697.jpg": "gull-lake-rope-swing",
    "nearby-bachar-boulders.jpg": "bachar-boulders-climbing",
    "nearby-bodie.jpg": "bodie-wagon-wheel",
    "clarks-nutcracker.jpg": "clarks-nutcracker",
    "970034-10151393441486485-531394880-n.jpg": "horse-drive-riders",
    "fern-creek2.jpg": "fern-creek-falls",
    "june-lake-loop-map.png": "june-lake-loop-map",
    "camap.jpg": "california-map-june-lake",
    "mr.jpg": "press-magazine-review",
    "np.jpg": "press-newspaper-geothermal",
}


def trim_black(im):
    """Remove near-black bars from the edges of an image."""
    rgb = im.convert("RGB")
    bg = Image.new("RGB", rgb.size, (0, 0, 0))
    diff = ImageChops.difference(rgb, bg).convert("L").point(lambda p: 255 if p > 28 else 0)
    box = diff.getbbox()
    if not box:
        return im
    w, h = im.size
    l, t, r, b = box
    # only trim real bars (at least 3% of a side), never a dark scene
    if (l < 0.03 * w and r > 0.97 * w and t < 0.03 * h and b > 0.97 * h):
        return im
    cropped = im.crop(box)
    if cropped.width < 0.3 * w or cropped.height < 0.3 * h:
        return im
    return cropped


def dominant(im):
    small = im.convert("RGB").resize((1, 1), Image.LANCZOS)
    return "#%02x%02x%02x" % small.getpixel((0, 0))


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for src, name in NAMES.items():
        path = os.path.join(SRC, src)
        if not os.path.exists(path):
            print("missing", src)
            continue
        im = ImageOps.exif_transpose(Image.open(path))
        if not src.endswith(".png"):
            im = trim_black(im.convert("RGB"))
        widths = [w for w in WIDTHS if w < im.width] + [min(im.width, WIDTHS[-1])]
        widths = sorted(set(widths))
        for w in widths:
            h = round(im.height * w / im.width)
            r = im.resize((w, h), Image.LANCZOS) if w != im.width else im
            if r.mode not in ("RGB", "RGBA"):
                r = r.convert("RGB")
            r.save(os.path.join(OUT, f"{name}-{w}.avif"), quality=58)
            r.save(os.path.join(OUT, f"{name}-{w}.webp"), quality=78, method=6)
        top = widths[-1]
        manifest[name] = {"w": top, "h": round(im.height * top / im.width), "widths": widths, "color": dominant(im)}
        print(f"{name:42s} {im.width}x{im.height} -> {widths}")
    json.dump(manifest, open(MANIFEST, "w"), indent=1, sort_keys=True)
    # 1200x630 social sharing images
    og = os.path.join(ROOT, "public", "og")
    os.makedirs(og, exist_ok=True)
    for f in os.listdir(og):
        os.remove(os.path.join(og, f))
    for src, name in NAMES.items():
        if src.endswith(".png") or name.startswith(("press", "floorplan", "california")):
            continue
        im = trim_black(ImageOps.exif_transpose(Image.open(os.path.join(SRC, src))).convert("RGB"))
        r = max(1200 / im.width, 630 / im.height)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        l, t = (im.width - 1200) // 2, (im.height - 630) // 2
        im.crop((l, t, l + 1200, t + 630)).save(os.path.join(og, f"{name}.jpg"), quality=82, optimize=True, progressive=True)
    print(len(manifest), "images")


if __name__ == "__main__":
    main()
