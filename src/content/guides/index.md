---
url: /guides/
title: Field Guides
eyebrow: Yosemite's east side, written from June Lake
kicker: Guides
seo_title: "Guides to Tioga Pass, Tuolumne Meadows and June Lake | Yosemite Gateway Chalet"
description: "Field guides to Yosemite's east side from June Lake: Tioga Pass, Tuolumne Meadows, where to stay near the east entrance, June Lake, fall colors, and winter on the east side."
topic: Yosemite east side guides
hero: white-mountain-summit-sunrise
hero_alt: Sunrise from the summit of White Mountain, looking west to the Sierra
lead: Practical, current guides to the high country around the chalet, checked against official sources each season.
wide: true
updated: 2026-10-27
---
<div class="gfeat-list">
{% for u in ["/guides/tioga-pass/", "/guides/tuolumne-meadows/", "/yosemite-national-park-lodging/", "/guides/june-lake/", "/guides/june-lake-fall-colors/", "/guides/yosemite-east-side-in-winter/"] %}{% set g = pages[u] %}<a class="gfeat" href="{{ u }}"><span class="gf-img">{{ picture(g.hero, g.hero_alt or "", "(min-width: 900px) 60vw, 100vw") }}</span><span class="gf-text"><span class="gf-title">{{ g.nav_title or g.title }}</span><span class="gf-desc">{{ g.card }}</span><span class="gf-more">Read the guide</span></span></a>
{% endfor %}
</div>
