---
url: /guides/
title: Field Guides
eyebrow: Yosemite's east side, written from June Lake
kicker: Guides
seo_title: "Guides to Tioga Pass, Tuolumne Meadows and June Lake | Yosemite Gateway Chalet"
description: "Field guides to Yosemite's east side from June Lake: Tioga Pass, Tuolumne Meadows, where to stay near the east entrance, June Lake, fall colors, and winter on the east side."
topic: Yosemite east side guides
hero: alpine-lake-below-sierra-peaks
hero_alt: An alpine lake below snow-streaked Sierra peaks
lead: Practical, current guides to the high country around the chalet, checked against official sources each season.
wide: true
updated: 2026-10-26
---
<ol class="glist in-page">
{% for u in ["/guides/tioga-pass/", "/guides/tuolumne-meadows/", "/yosemite-national-park-lodging/", "/guides/june-lake/", "/guides/june-lake-fall-colors/", "/guides/yosemite-east-side-in-winter/"] %}{% set g = pages[u] %}<li><a href="{{ u }}"><span class="gl-img">{{ picture(g.hero, "", "(min-width: 900px) 240px, 40vw") }}</span><span class="gl-text"><span class="gl-title">{{ g.nav_title }}</span><span class="gl-desc">{{ g.card }}</span></span></a></li>
{% endfor %}
</ol>
