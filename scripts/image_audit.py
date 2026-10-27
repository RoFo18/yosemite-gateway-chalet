#!/usr/bin/env python3
"""List every photo a visitor sees on more than one page (the gallery and the site-wide closing band excluded)."""
import os, re, sys, collections
DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
use = collections.defaultdict(list)
for root, _, files in os.walk(DIST):
    if "index.html" not in files: continue
    page = "/" + os.path.relpath(root, DIST) + "/" if root != DIST else "/"
    if page in ("/gallery/", "/404/"): continue
    h = open(os.path.join(root, "index.html")).read()
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<head>.*?</head>', '', h, flags=re.S)
    h = re.sub(r'<section class="closing".*?</section>', '', h, flags=re.S)
    for n in set(re.findall(r'/img/([a-z0-9-]+?)-\d+\.(?:webp|avif)', h)):
        use[n].append(page)
rep = {n: p for n, p in use.items() if len(p) > 1}
for n, p in sorted(rep.items(), key=lambda x: -len(x[1])):
    print(f"{n} ({len(p)}): {', '.join(sorted(p))}")
sys.exit(0)
