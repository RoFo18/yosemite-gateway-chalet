---
url: /journal/
title: Journal
eyebrow: Notes from June Lake
kicker: Journal
seo_title: "Journal | Yosemite Gateway Chalet, June Lake"
description: "Stories from the Yosemite Gateway Chalet and June Lake: paddleboarding Rush Creek, fall on the June Lake Loop, skiing June Mountain, the hot tub, and press."
hero: family-room-wood-stove
hero_focus: 50% 55%
hero_alt: The family room off the kitchen, with log walls and beams, leather couches by the windows, the wood stove and the bar with its copper sink
updated: 2026-10-27
---
<ul class="posts">
{% for u in ["/journal/paddleboarding-rush-creek-june-lake/", "/journal/june-lakes-fall-feast-for-the-senses/", "/journal/better-than-a-june-lake-hotel/", "/journal/the-spirit-of-glisse/", "/journal/yosemite-gateway-chalet-in-the-news/"] %}{% set p = pages[u] %}<li><a href="{{ u }}"><span class="p-title">{{ p.title }}</span><span class="p-desc">{{ p.description }}</span></a></li>
{% endfor %}
</ul>
