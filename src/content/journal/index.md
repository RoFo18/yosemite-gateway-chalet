---
url: /journal/
title: Journal
eyebrow: Notes from June Lake
kicker: Journal
seo_title: "Journal | Yosemite Gateway Chalet, June Lake"
description: "Stories and notes from the Yosemite Gateway Chalet and June Lake: fall in the Eastern Sierra, skiing, the hot tub, and press coverage."
updated: 2026-10-26
---
<ul class="posts">
{% for u in ["/journal/june-lakes-fall-feast-for-the-senses/", "/journal/fall-colours-and-fine-coffee/", "/journal/better-than-a-june-lake-hotel/", "/journal/the-spirit-of-glisse/", "/journal/yosemite-gateway-chalet-in-the-news/", "/journal/earliest-tioga-pass-opening-since-1987/"] %}{% set p = pages[u] %}<li><a href="{{ u }}"><span class="p-date">{{ p.published.strftime("%B %Y") }}</span><span class="p-title">{{ p.title }}</span><span class="p-desc">{{ p.description }}</span></a></li>
{% endfor %}
</ul>
