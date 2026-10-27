---
url: /guides/
title: Plan Your Trip
nav_title: Plan Your Trip
eyebrow: Practical answers, checked each season
kicker: Guides
seo_title: "Plan Your Trip: Tioga Pass, Tuolumne Meadows and June Lake Guides | Yosemite Gateway Chalet"
description: "Field guides to Yosemite's east side from June Lake: Tioga Pass, Tuolumne Meadows, where to stay near the east entrance, June Lake, fall colors, and winter on the east side."
topic: Yosemite east side guides
hero: white-mountain-summit-sunrise
hero_alt: Sunrise from the summit of White Mountain, looking west to the Sierra
lead: When Tioga Pass opens, how to reach Tuolumne Meadows, what winter means on the east side, and where to stay. Written from June Lake and checked against official sources each season.
wide: true
updated: 2026-10-27
---
<section class="plan-group"><h2>Yosemite and Tioga Pass</h2><ul class="rel-links plan-links">
{% for u in ["/guides/tioga-pass/", "/guides/tioga-pass-opening-dates/", "/guides/tuolumne-meadows/", "/guides/yosemite-east-side-in-winter/"] %}{% set g = pages[u] %}<li><a href="{{ u }}"><span class="rl-title">{{ g.nav_title or g.title }}</span><span class="rl-desc">{{ g.card or (g.description|striptags)[:120] }}</span></a></li>{% endfor %}
</ul></section>
<section class="plan-group"><h2>June Lake</h2><ul class="rel-links plan-links">
{% for u in ["/guides/june-lake/", "/guides/june-lake-fall-colors/", "/location/"] %}{% set g = pages[u] %}<li><a href="{{ u }}"><span class="rl-title">{{ g.nav_title or g.title }}</span><span class="rl-desc">{{ g.card or (g.description|striptags)[:120] }}</span></a></li>{% endfor %}
</ul></section>
<section class="plan-group"><h2>Where to stay</h2><ul class="rel-links plan-links">
{% for u in ["/yosemite-national-park-lodging/", "/june-lake-lodging/", "/june-mountain-lodging/", "/tuolumne-meadows-lodging/", "/yosemite-group-lodging/", "/june-lake-cabin-rentals/"] %}{% set g = pages[u] %}<li><a href="{{ u }}"><span class="rl-title">{{ g.nav_title or g.title }}</span><span class="rl-desc">{{ g.card or (g.description|striptags)[:120] }}</span></a></li>{% endfor %}
</ul></section>
<section class="plan-group"><h2>Before you book</h2><ul class="rel-links plan-links">
{% for u in ["/rates-and-policies/", "/faq/", "/reviews/"] %}{% set g = pages[u] %}<li><a href="{{ u }}"><span class="rl-title">{{ g.nav_title or g.title }}</span><span class="rl-desc">{{ g.card or (g.description|striptags)[:120] }}</span></a></li>{% endfor %}
</ul></section>

<a class="tg-promo" href="/guides/tioga-pass-opening-dates/"><img src="/og/tioga-pass-snow-analysis.jpg" alt="Chart of Tioga Road opening dates against April 1 snowpack, 1980 to 2026" width="1200" height="630" loading="lazy"><span class="gf-text"><span class="gf-title">When does Tioga Pass open?</span><span class="gf-desc">47 springs of park data, charted. Snow explains most of it. The 2020s don't add up.</span><span class="gf-more">See the analysis</span></span></a>
