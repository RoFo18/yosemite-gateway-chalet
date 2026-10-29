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
    "the-grounds-gallery-4.jpg": "chalet-grounds-log-exterior",
    "the-grounds-gallery-5.jpg": "chalet-grounds-hammock-aspens",
    "the-grounds-gallery-6.jpg": "chalet-deck-and-forest",
    "backyard-3.jpg": "guest-in-deep-snow",
    "044-3grand-room.jpg": "grand-room-fireside-gathering",
    "044-3grand-room2.jpg": "grand-room-fireside-evening",
    "grand-room2.jpg": "grand-room-oak-bar-wine",
    "dining-room-gallery-2.jpg": "dining-room-doorway",
    "dining-room-gallery-3.jpg": "dinner-at-the-chalet",
    "family-kitchen-gallery-2.jpg": "family-room-evening",
    "family-kitchen-gallery-5.jpg": "kitchen-wide-view",
    "family-kitchen-gallery-6.jpg": "family-room-wide-view",
    "master-bedroom-gallery-2.jpg": "master-suite-evening",
    "master-bedroom-gallery-3.jpg": "master-suite-window-snow-peaks",
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
    "hot-springs.jpg": "hot-creek-eastern-sierra",
    "hotsprings-2.jpg": "natural-hot-spring-soak",
    "img-7697.jpg": "gull-lake-rope-swing",
    "grant-lake-jump.jpg": "grant-lake-cliff-jump",
    "sup-rush-creek-silver-lake.jpg": "paddleboard-rush-creek-silver-lake",
    "sup-rush-creek-bw.jpg": "paddleboarding-rush-creek-family-bw",
    "parker-bench-silver-lake.jpg": "parker-bench-silver-lake-view",
    "kids-ski-cart-june-mountain.jpg": "kids-ski-free-june-mountain",
    "wild-mustangs-mono-basin.jpg": "wild-mustangs-mono-basin",
    "grant-lake-sunset-stone.jpg": "grant-lake-sunset-stone-throw",
    "nearby-bachar-boulders.jpg": "bachar-boulders-climbing",
    "nearby-bodie.jpg": "bodie-wagon-wheel",
    "clarks-nutcracker.jpg": "clarks-nutcracker",
    "fern-creek2.jpg": "fern-creek-falls",
    "june-lake-loop-map.png": "june-lake-loop-map",
    "camap.jpg": "california-map-june-lake",
    "mr.jpg": "press-magazine-review",
    "np.jpg": "press-newspaper-geothermal",
    # October 2026, from Robert
    "yost-meadow.jpg": "yost-meadow-out-the-back-door",
    "carson-scree.jpg": "carson-peak-scree-run",
    "kid-sup-rush-creek.jpg": "kid-paddleboard-rush-creek-carson-peak",
    "fern-creek-winter-walk.jpg": "winter-walk-home-from-fern-creek",
    "reversed-peak-hike.jpg": "family-hike-toward-reversed-peak",
    "garage-wall-2.jpg": "garage-climbing-wall-handholds",
    "new-mono-craters-sunset.jpg": "mono-craters-sunset-rays",
    "silver-lake-boards-enhanced.jpg": "paddleboards-silver-lake-shore",
    "new-gull-lake-sunset.jpg": "gull-lake-fiery-sunset",
    "new-wild-mustangs.jpg": "wild-mustang-herd-mono-county",
    "new-crowley-columns-inside.jpg": "crowley-lake-columns-inside",
    "new-crowley-columns-shore.jpg": "crowley-lake-columns-shore",
    "new-chair-7.jpg": "june-mountain-chair-7-empty-runs",
    "new-saddlebag-lake.jpg": "saddlebag-lake-tioga",
    "new-mono-fissures.jpg": "mono-lake-black-point-fissures",
    "new-horseback-june-lake.jpg": "horseback-ride-above-june-lake",
    "new-master-suite-loft.jpg": "master-suite-loft",
    "new-secret-spot-lakes.jpg": "secret-spot-alpine-lakes",
    "new-elsie-red-tub.jpg": "elsie-room-red-claw-foot-tub",
    "new-mount-dana.jpg": "mount-dana-tioga-pass",
    "new-marmot.jpg": "yellow-bellied-marmot",
    "new-chalet-sign.jpg": "yosemite-gateway-chalet-sign",
    "carson-peak-summit-view.jpg": "carson-peak-summit-view",
    "new-matthes-crest.jpg": "matthes-crest-climber",
    "new-bouldering-mono-silhouette.jpg": "bouldering-silhouette-mono-basin",
    "new-tufa-rainbow.jpg": "mono-lake-tufa-rainbow",
    "new-mono-lake-from-fern-lake.jpg": "mono-lake-from-above-fern-lake",
    "new-fern-lake-reflection.jpg": "fern-lake-reflection",
    "new-fly-cast-beard.jpg": "fly-casting-freestone-creek",
    "new-kid-fly-fishing.jpg": "young-angler-fly-fishing-creek",
    "new-fly-cast-red-cap.jpg": "fly-casting-below-granite",
    "new-june-mountain-steep-powder.jpg": "june-mountain-steep-powder",
    "new-glass-creek-meadow-corn-lilies.jpg": "glass-creek-meadow-corn-lilies",
    "new-agnew-tram-tracks-above-silver-lake.jpg": "agnew-tram-tracks-above-silver-lake",
    "new-light-through-the-canyon.jpg": "light-through-the-canyon",
    "new-eastern-sierra-morning-water.jpg": "eastern-sierra-morning-water",
    "new-june-lake-loop-evening-clouds.jpg": "june-lake-loop-evening-clouds",
    "new-reversed-peak-triangle-cave.jpg": "reversed-peak-triangle-cave",
    "new-sierra-ridge-spires.jpg": "sierra-ridge-spires",
    "new-grand-room-daylight.jpg": "grand-room-daylight",
    "new-master-suite-shower.jpg": "master-suite-shower",
    "new-silver-lake-fall-morning-boats.jpg": "silver-lake-fall-morning-boats",
    "new-parker-lake-trail-fall-color.jpg": "parker-lake-trail-fall-color",
    "new-june-lake-golden-light.jpg": "june-lake-golden-light",
    "new-mule-deer-buck.jpg": "mule-deer-buck",
    "new-june-lake-loop-dock-morning.jpg": "june-lake-loop-dock-morning",
    "new-chalet-exterior-sign-carson-peak.jpg": "chalet-exterior-sign-carson-peak",
    "new-ancient-petroglyphs-high-desert.jpg": "ancient-petroglyphs-high-desert",
    "new-glass-mountain-long-valley-view.jpg": "glass-mountain-long-valley-view",
    "new-crater-mountain-summit-view.jpg": "crater-mountain-summit-view",
    "new-crater-mountain-survey-marker.jpg": "crater-mountain-survey-marker",
    "new-june-lake-panorama.jpg": "june-lake-panorama",
    "new-lundy-canyon-fall-aspens.jpg": "lundy-canyon-fall-aspens",
    "new-lundy-canyon-waterfall-fall-color.jpg": "lundy-canyon-waterfall-fall-color",
    "new-hot-creek-canyon-from-above.jpg": "hot-creek-canyon-from-above",
    "new-upper-owens-river-meadow-cast.jpg": "upper-owens-river-meadow-cast",
    "new-rush-creek-meadow-carson-peak.jpg": "rush-creek-meadow-carson-peak",
    "new-rush-creek-wading-angler.jpg": "rush-creek-wading-angler",
    "new-upper-owens-river-winter-snow.jpg": "upper-owens-river-winter-snow",
    "hq-chalet-winter-sign.jpg": "chalet-winter-sign",
    "hq-mud-room-bench-and-cubbies.jpg": "mud-room-bench-and-cubbies",
    "hq-dining-room-timber-table.jpg": "dining-room-timber-table",
    "hq-curio-cabinet-pottery.jpg": "curio-cabinet-pottery",
    "hq-family-room-leather-sofa.jpg": "family-room-leather-sofa",
    "hq-family-room-wood-stove.jpg": "family-room-wood-stove",
    "hq-copper-faucet-detail.jpg": "copper-faucet-detail",
    "hq-kitchen-and-breakfast-bar.jpg": "kitchen-and-breakfast-bar",
    "hq-kitchen-copper-sink.jpg": "kitchen-copper-sink",
    "hq-chalet-winter-yost-creek.jpg": "chalet-winter-yost-creek",
    "hq-staircase-chandelier.jpg": "staircase-chandelier",
    "hq-stair-landing-chandelier.jpg": "stair-landing-chandelier",
    "hq-dreamcatcher-detail.jpg": "dreamcatcher-detail",
    "hq-upper-hall-railings.jpg": "upper-hall-railings",
    "hq-elsie-room-suite.jpg": "elsie-room-suite",
    "hq-elsie-room-claw-foot-tub.jpg": "elsie-room-claw-foot-tub",
    "hq-grand-room-evening-lamplight.jpg": "grand-room-evening-lamplight",
    "hq-grand-room-fireplace-and-bar.jpg": "grand-room-fireplace-and-bar",
    "hq-river-room-suite.jpg": "river-room-suite",
    "hq-hydrotherapy-tub-snow-forest.jpg": "hydrotherapy-tub-snow-forest",
    "hq-river-room-bed-windows.jpg": "river-room-bed-windows",
    "hq-chalet-sign-at-dusk.jpg": "chalet-sign-at-dusk",
    "hq-master-suite-jacuzzi-and-beds.jpg": "master-suite-jacuzzi-and-beds",
    "hq-master-suite-bed.jpg": "master-suite-bed",
    "hq-garage-climbing-wall-full.jpg": "garage-climbing-wall-full",
    "hq-log-sitting-room.jpg": "log-sitting-room",
    "hq-drive-up-395-sierra.jpg": "drive-up-395-sierra",
    "hq-kachina-dolls-mantel.jpg": "kachina-dolls-mantel",
    "hq-dining-room-dinner-set.jpg": "dining-room-dinner-set",
    "hq-la-parrilla-june-lake.jpg": "la-parrilla-june-lake",
    "hq-la-parrilla-yeti.jpg": "la-parrilla-yeti",
    "hq-tiger-bar-logo.jpg": "tiger-bar-logo",
    "june-lake-general-store.jpg": "june-lake-general-store",
    "june-lake-film-poster.jpg": "june-lake-film-poster",
    "vrbo-bear-window.jpg": "vrbo-bear-window",
    "chalet-fall-aspens-sign.jpg": "chalet-fall-aspens-sign",
    "kids-skiing-june-mountain-smiles.jpg": "kids-skiing-june-mountain-smiles",
    "mount-banner-memorial-plaque.jpg": "mount-banner-memorial-plaque",
    "banner-ritter-backcountry-bw.jpg": "banner-ritter-backcountry-bw",
    "reversed-peak-panorama-east.jpg": "reversed-peak-panorama-east",
    "fern-lake-cirque-summer.jpg": "fern-lake-cirque-summer",
    "tuolumne-granite-spire-lake-view.jpg": "tuolumne-granite-spire-lake-view",
    "secret-spot-black-slab-climber.jpg": "secret-spot-black-slab-climber",
    "bouldering-overhang-blue-shirt.jpg": "bouldering-overhang-blue-shirt",
    "ice-climber-belay-granite-snow.jpg": "ice-climber-belay-granite-snow",
    "bouldering-rockin-dave-mono-basin.jpg": "bouldering-rockin-dave-mono-basin",
    "rappel-matthes-crest.jpg": "rappel-matthes-crest",
    "paddleboard-boy-and-mom-glassy-lake.jpg": "paddleboard-boy-and-mom-glassy-lake",
    "paddleboard-family-silver-lake-cliffs.jpg": "paddleboard-family-silver-lake-cliffs",
    "gull-lake-rope-swing-silhouette.jpg": "gull-lake-rope-swing-silhouette",
    "gull-lake-rope-swing-pair.jpg": "gull-lake-rope-swing-pair",
    "mono-pass-sign-bloody-canyon.jpg": "mono-pass-sign-bloody-canyon",
    "bear-broken-minivan-window.jpg": "bear-broken-minivan-window",
    "wild-mustangs-sagebrush-morning.jpg": "wild-mustangs-sagebrush-morning",
    "fresh-powder-tree-slope.jpg": "fresh-powder-tree-slope",
    "backcountry-skier-coffee-break.jpg": "backcountry-skier-coffee-break",
    "june-mountain-groomer-carve.jpg": "june-mountain-groomer-carve",
    "hydrotherapy-tub-red-glow-night.jpg": "hydrotherapy-tub-red-glow-night",
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
    # overwrite only the generated cards; hand-made cards (like the Tioga analysis) stay
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
