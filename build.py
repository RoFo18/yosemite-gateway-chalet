#!/usr/bin/env python3
"""Build the Yosemite Gateway Chalet site into ./dist

    python3 build.py

Content lives in src/content/**/*.md (YAML front matter + Markdown).
Facts live in src/data/property.yaml. Templates live in src/templates/.
Everything in public/ is copied to the site root as is.
"""
import datetime as dt
import html
import json
import os
import re
import shutil

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
P = yaml.safe_load(open(os.path.join(SRC, "data", "property.yaml")))
IMAGES = json.load(open(os.path.join(SRC, "data", "images.json")))
SITE = P["site_url"]
BUILD_DATE = dt.date.today().isoformat()

NAV = [
    ("The Chalet", "/the-chalet/"),
    ("Gallery", "/gallery/"),
    ("Things to Do", "/experiences/"),
    ("Plan Your Trip", "/guides/"),
    ("Reviews", "/reviews/"),
]
FOOTER = [
    ("Stay", [("The Chalet", "/the-chalet/"), ("Suites", "/the-chalet/#suites"), ("Floorplan", "/the-chalet/floorplan/"),
              ("Gallery", "/gallery/"), ("Guest reviews", "/reviews/"), ("Rates and policies", "/rates-and-policies/"), ("Inquire", "/inquire/")]),
    ("Things to do", [("Skiing June Mountain", "/experiences/winter/"), ("Fly fishing, and where to fish today", "/fly-fishing/"),
                      ("Lakes and paddleboarding", "/experiences/summer/"),
                      ("Horseback riding and hiking", "/experiences/hiking/"), ("Mono Lake and hidden places", "/experiences/sightseeing/"),
                      ("Hot springs and the spa", "/experiences/spa-and-hot-springs/"),
                      ("Where to eat", "/experiences/dining/")]),
    ("Plan your trip", [("Tioga Pass", "/guides/tioga-pass/"), ("When Tioga Pass opens", "/guides/tioga-pass-opening-dates/"), ("Tuolumne Meadows", "/guides/tuolumne-meadows/"),
                ("June Lake", "/guides/june-lake/"), ("June Lake Loop fall colors", "/guides/june-lake-fall-colors/"),
                ("Yosemite's east side in winter", "/guides/yosemite-east-side-in-winter/"),
                ("Lodging near Yosemite's east entrance", "/yosemite-national-park-lodging/"),
                ("June Lake lodging", "/june-lake-lodging/"), ("June Lake cabin rentals", "/june-lake-cabin-rentals/"),
                ("Group lodging near Yosemite", "/yosemite-group-lodging/"), ("Tuolumne Meadows lodging", "/tuolumne-meadows-lodging/"),
                ("June Mountain lodging", "/june-mountain-lodging/")]),
    ("More", [("Getting here", "/location/"), ("FAQ", "/faq/"), ("Local favorites", "/local-favorites/"), ("Journal", "/journal/"), ("Privacy", "/privacy/")]),
]


# ------------------------------------------------------------------ images
def srcset(name, fmt):
    m = IMAGES[name]
    return ", ".join(f"/img/{name}-{w}.{fmt} {w}w" for w in m["widths"])


def picture(name, alt, sizes="100vw", cls="", eager=False, fit=None):
    if name not in IMAGES:
        raise KeyError(f"unknown image {name}")
    m = IMAGES[name]
    fallback = m["widths"][min(1, len(m["widths"]) - 1)]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    style = f'background-color:{m["color"]}'
    if fit:
        style += f";object-position:{fit}"
    return Markup(
        f'<picture class="{cls}"><source type="image/avif" srcset="{srcset(name, "avif")}" sizes="{sizes}">'
        f'<source type="image/webp" srcset="{srcset(name, "webp")}" sizes="{sizes}">'
        f'<img src="/img/{name}-{fallback}.webp" alt="{html.escape(alt, quote=True)}" width="{m["w"]}" height="{m["h"]}" '
        f'{load} style="{style}"></picture>')


def figure(name, alt, caption=None, layout="wide"):
    """Body photos are always large: content width plus a bleed, or full width.
    Old "right", "left" and "small" layouts now render wide too. Portrait photos
    are centred at a generous width instead of being stretched edge to edge."""
    m = IMAGES[name]
    if layout in ("right", "left", "small"):
        layout = "wide"
    if layout == "wide" and m["h"] > m["w"] * 0.88:
        layout = "portrait"
    sizes = {"wide": "(min-width: 1200px) 1180px, 100vw", "full": "100vw",
             "portrait": "(min-width: 900px) 720px, 100vw"}.get(layout, "100vw")
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return Markup(f'<figure class="fig fig-{layout}">{picture(name, alt, sizes)}{cap}</figure>')


def gallery(items, cols=3):
    """A dark, full-width carousel: one photo at a time, captioned, with arrows, a counter and a filmstrip.
    Swipe or scroll on touch screens; arrow keys and the filmstrip on desktop. Click a photo to view it full screen."""
    n = len(items)
    slides = "".join(
        f'<figure class="car-slide" aria-roledescription="slide" aria-label="{i + 1} of {n}">'
        f'<a href="/img/{name}-{IMAGES[name]["widths"][-1]}.webp" data-lightbox aria-label="View full screen: {html.escape(alt, quote=True)}">'
        f'{picture(name, alt, "(min-width: 1100px) 1100px, 100vw", eager=False)}</a>'
        f'<figcaption>{html.escape(alt)}</figcaption></figure>' for i, (name, alt) in enumerate(items))
    thumbs = "".join(
        f'<button type="button" class="car-thumb" data-go="{i}" aria-label="Show photo {i + 1}: {html.escape(alt, quote=True)}">'
        f'{picture(name, "", "120px")}</button>' for i, (name, alt) in enumerate(items)) if n > 1 else ""
    nav = ('<button type="button" class="car-arrow car-prev" data-prev aria-label="Previous photo"><span aria-hidden="true">&#8592;</span></button>'
           '<button type="button" class="car-arrow car-next" data-next aria-label="Next photo"><span aria-hidden="true">&#8594;</span></button>'
           f'<p class="car-count" aria-hidden="true"><span data-idx>1</span> / {n}</p>') if n > 1 else ""
    return Markup(f'<div class="carousel" data-carousel aria-roledescription="carousel" tabindex="0">'
                  f'<div class="car-stage"><div class="car-track" data-track>{slides}</div>{nav}</div>'
                  f'{f"<div class=car-thumbs>{thumbs}</div>" if thumbs else ""}</div>')


def story(chapters):
    """The gallery page: one curated carousel in chapters. Each photo carries a title and a line of commentary.
    chapters = [(chapter name, [(image, title, note), ...]), ...]"""
    seen, slides, thumbs, tabs, i = set(), [], [], [], 0
    for ch, items in chapters:
        tabs.append(f'<button type="button" class="st-tab" data-go="{i}" data-chapter-start="{i}">{html.escape(ch)}</button>')
        for name, title, note in items:
            if name in seen:
                raise ValueError(f"photo used twice in the gallery: {name}")
            seen.add(name)
            m = IMAGES[name]
            slides.append(
                f'<figure class="st-slide" data-chapter="{html.escape(ch, quote=True)}" aria-roledescription="slide">'
                f'<a class="st-photo" href="/img/{name}-{m["widths"][-1]}.webp" data-lightbox aria-label="View full screen: {html.escape(title, quote=True)}">'
                f'{picture(name, title, "(min-width: 1200px) 1200px, 100vw")}</a>'
                f'<figcaption><p class="st-title">{html.escape(title)}</p><p class="st-note">{html.escape(note)}</p></figcaption></figure>')
            thumbs.append(f'<button type="button" class="car-thumb" data-go="{i}" aria-label="Show {html.escape(title, quote=True)}">{picture(name, "", "120px")}</button>')
            i += 1
    n = i
    return Markup(
        f'<div class="story" data-carousel aria-roledescription="carousel" aria-label="Photographs of the chalet and the Eastern Sierra" tabindex="0">'
        f'<nav class="st-tabs" aria-label="Chapters">{"".join(tabs)}</nav>'
        f'<div class="car-stage"><div class="car-track" data-track>{"".join(slides)}</div>'
        '<button type="button" class="car-arrow car-prev" data-prev aria-label="Previous photo"><span aria-hidden="true">&#8592;</span></button>'
        '<button type="button" class="car-arrow car-next" data-next aria-label="Next photo"><span aria-hidden="true">&#8594;</span></button>'
        f'<p class="car-count" aria-hidden="true"><span data-idx>1</span> / {n}</p></div>'
        f'<div class="car-thumbs">{"".join(thumbs)}</div></div>')


def distance_table(rows=None):
    rows = rows or P["distances"]
    body = "".join(
        f'<tr><th scope="row">{html.escape(r["place"])}</th><td class="num">{r["value"]} {r["unit"]}</td>'
        f'<td>{html.escape(r["note"])}</td></tr>' for r in rows)
    return Markup('<div class="table-wrap"><table class="data"><caption>Distances and drive times from the chalet</caption>'
                  '<thead><tr><th scope="col">From the chalet to</th><th scope="col">Distance or time</th>'
                  f'<th scope="col">Notes</th></tr></thead><tbody>{body}</tbody></table></div>')


def film(vimeo_id, title, credit, minutes, poster="eastern-sierra-sunset-panorama",
         eyebrow="Yosemite in motion", heading="The high country, minutes from the door"):
    """Full-bleed film band. Shows a poster until clicked, so no Vimeo code loads on page view."""
    label = html.escape(f"Play {title}, {minutes} minutes", quote=True)
    return Markup(
        f'<section class="film" aria-label="Film: {html.escape(title, quote=True)}">'
        f'<button type="button" class="film-frame" data-vimeo="{vimeo_id}" aria-label="{label}">'
        f'{picture(poster, "", "100vw", "film-poster")}'
        f'<span class="film-copy"><span class="eyebrow">{html.escape(eyebrow)}</span>'
        f'<span class="film-title">{html.escape(heading)}</span>'
        f'<span class="film-cta"><span class="film-icon" aria-hidden="true"></span>Play the film &middot; {minutes} min</span></span>'
        f'</button><p class="film-credit">{credit}</p></section>')


def video_tour(youtube_id, title, credit, minutes, upload_date, description,
               eyebrow="A guest's video tour", heading="Walk through the chalet"):
    """Click-to-play YouTube band in the same style as film(). Uses youtube-nocookie and loads
    nothing from YouTube until pressed, apart from the video's own poster frame."""
    label = html.escape(f"Play {title}, {minutes} minutes", quote=True)
    thumb = f"https://i.ytimg.com/vi/{youtube_id}/maxresdefault.jpg"
    ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": title, "description": description,
          "thumbnailUrl": thumb, "uploadDate": upload_date, "duration": f"PT{int(minutes)}M{round((minutes % 1) * 60)}S",
          "embedUrl": f"https://www.youtube-nocookie.com/embed/{youtube_id}",
          "contentUrl": f"https://www.youtube.com/watch?v={youtube_id}"}
    mins = f"{int(minutes)}:{round((minutes % 1) * 60):02d}"
    return Markup(
        f'<section class="film film-tour" id="walkthrough" aria-label="Video: {html.escape(title, quote=True)}">'
        f'<button type="button" class="film-frame" data-youtube="{youtube_id}" aria-label="{label}">'
        f'<span class="film-poster"><img src="{thumb}" alt="" loading="lazy" width="1280" height="720" '
        f'onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{youtube_id}/hqdefault.jpg\'"></span>'
        f'<span class="film-copy"><span class="eyebrow">{html.escape(eyebrow)}</span>'
        f'<span class="film-title">{html.escape(heading)}</span>'
        f'<span class="film-cta"><span class="film-icon" aria-hidden="true"></span>Play the tour &middot; {mins}</span></span>'
        f'</button><p class="film-credit">{credit}</p>'
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></section>')


GLANCE = [('Who it suits', 'Families and groups of up to eight'), ('Sleeps', '8 in three suites, each with its own bath'), ('Yosemite', '27 miles to Tioga Pass, 45 minutes to Tuolumne Meadows, late May to November'), ('June Mountain', '1 mile; kids 12 and under ski free'), ('Season', 'Open all year; the hot tub runs all year'), ('Rates', '$295 to $995 a night, plus a flat $295 cleaning fee and 15% Mono County tax')]


def glance(title="At a glance"):
    """Short facts block for answer engines and skimmers: who it suits, distances, season, fees."""
    rows = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in GLANCE)
    return Markup(f'<section class="glance" aria-label="{html.escape(title)}"><h2 class="glance-h">{html.escape(title)}</h2><dl>{rows}</dl></section>')


REVIEWS = yaml.safe_load(open(os.path.join(SRC, "data", "reviews.yaml"), encoding="utf-8"))
_RV = {r["id"]: r for r in REVIEWS["reviews"]}


def _cite(r):
    return (f'<figcaption><span class="rv-name">{html.escape(r["name"])}</span>'
            f'<span class="rv-meta">on {html.escape(r["source"])}</span></figcaption>')


def quote(rid, cls=""):
    """One guest review as a large pull quote, quoted exactly."""
    r = _RV[rid]
    return Markup(f'<figure class="rv-pull {cls}"><blockquote><p>{html.escape(r["text"])}</p></blockquote>{_cite(r)}</figure>')


def reviews_wall(skip=()):
    items = "".join(f'<figure class="rv"><blockquote><p>{html.escape(r["text"])}</p></blockquote>{_cite(r)}</figure>'
                    for r in REVIEWS["reviews"] if r["id"] not in skip)
    return Markup(f'<div class="rv-wall">{items}</div>')


def review_scores():
    v, a = REVIEWS["summary"]["vrbo"], REVIEWS["summary"]["airbnb"]
    return Markup(
        '<dl class="rv-scores">'
        f'<div><dt>VRBO</dt><dd><span class="rv-big">{v["score"]}</span> out of {v["scale"]}</dd>'
        f'<dd class="rv-sub"><a href="{v["url"]}" rel="noopener" target="_blank">{v["count"]} verified reviews</a></dd></div>'
        f'<div><dt>Airbnb</dt><dd><span class="rv-big">{a["score"]}</span> out of {a["scale"]}</dd>'
        f'<dd class="rv-sub"><a href="{a["url"]}" rel="noopener" target="_blank">{a["count"]} reviews</a>. {a["note"]}</dd></div>'
        '</dl>')


FF = yaml.safe_load(open(os.path.join(SRC, "data", "flyfishing.yaml"), encoding="utf-8"))
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def ff_calendar():
    """When each water fishes best, by month: a quiet heat strip in one hue."""
    lab = {0: "Closed or out of reach", 1: "Fair", 2: "Good", 3: "Prime"}
    head = "".join(f'<th scope="col">{m}</th>' for m in _MON)
    rows = []
    for w in FF["waters"]:
        cells = "".join(f'<td class="ffc ffc-{v}"><span class="sr">{_MON[i]}: {lab[v]}</span></td>' for i, v in enumerate(w["months"]))
        rows.append(f'<tr><th scope="row"><a href="{w["url"]}">{html.escape(w["name"])}</a></th>{cells}</tr>')
    key = "".join(f'<span><i class="ffc ffc-{v}"></i>{lab[v]}</span>' for v in (3, 2, 1, 0))
    return Markup(f'<figure class="ff-cal"><div class="ff-cal-scroll"><table><thead><tr><th scope="col"><span class="sr">Water</span></th>{head}</tr></thead>'
                  f'<tbody>{"".join(rows)}</tbody></table></div><figcaption><span class="ff-key">{key}</span>'
                  f'Our read of when each water fishes best, from seasons, hatches and access.</figcaption></figure>')


def ff_drive():
    """Drive time from the chalet to each water, as simple bars."""
    ws = sorted(FF["waters"], key=lambda w: w["drive"])
    mx = max(w["drive"] for w in ws)
    rows = "".join(f'<li><a href="{w["url"]}">{html.escape(w["name"])}</a><span class="ffd-bar" style="--v:{w["drive"] / mx:.3f}"></span>'
                   f'<span class="ffd-n">{w["drive"]} min</span></li>' for w in ws)
    return Markup(f'<figure class="ff-drive"><ul>{rows}</ul><figcaption>Approximate drive from the chalet to the usual access point, in good conditions. '
                  'Backcountry times are to the trailhead.</figcaption></figure>')


def ff_facts(wid):
    w = next(x for x in FF["waters"] if x["id"] == wid)
    best = ", ".join(_MON[i] for i, v in enumerate(w["months"]) if v == 3) or "Varies"
    rows = [("Water type", w["type"]), ("Fish", w["species"]), ("Best months", best), ("Drive from the chalet", f'About {w["drive"]} minutes'),
            ("Regulations", w["regs"]), ("The one thing", w["presentation"])]
    lis = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in rows)
    return Markup(f'<dl class="facts ff-facts">{lis}</dl>')


def ff_tool():
    """The recommender: a map, today's conditions, two choices and one button. Drawn by /js/flyfish.js."""
    data = {"home": {"lat": P["geo"]["lat"], "lng": P["geo"]["lng"]},
            "waters": [{k: w[k] for k in ("id", "name", "url", "lat", "lng", "type", "kind", "skill", "presentation", "note", "flies", "months")} for w in FF["waters"]]}
    return Markup(
        '<section class="fft" id="what-to-fish-today" aria-labelledby="fft-h">'
        '<div class="fft-head"><p class="eyebrow">Today, on the water</p><h2 id="fft-h">Where to fish today, and with what</h2>'
        '<p>Live weather at June Lake, this month&rsquo;s hatches, and the one thing that matters on each water. Pick a style and your level.</p></div>'
        '<div class="fft-body"><div class="fft-map" id="fft-map" role="img" aria-label="Map of the seven waters within about 60 miles of the chalet"></div>'
        '<div class="fft-panel">'
        '<dl class="fft-now" aria-live="polite"><div><dt>Air</dt><dd data-now="t">&ndash;</dd></div><div><dt>Wind</dt><dd data-now="w">&ndash;</dd></div>'
        '<div><dt>Cloud</dt><dd data-now="c">&ndash;</dd></div><div><dt>Pressure</dt><dd data-now="p">&ndash;</dd></div></dl>'
        '<form class="fft-form"><label>Style<select name="style"><option value="best">Best opportunity</option><option value="dry">Dry fly</option>'
        '<option value="nymph">Nymph</option><option value="streamer">Streamer</option></select></label>'
        '<label>Level<select name="skill"><option value="beginner">Beginner</option><option value="intermediate" selected>Intermediate</option>'
        '<option value="advanced">Advanced</option></select></label><button type="submit" class="btn btn-solid">Tell me where to go</button></form>'
        '<div class="fft-out" aria-live="polite"></div>'
        '<p class="fft-src">Weather: <a href="https://open-meteo.com/" rel="noopener" target="_blank">Open-Meteo</a>. Hatches: our month-by-month notes. '
        'Always check <a href="https://wildlife.ca.gov/Regulations" rel="noopener" target="_blank">current regulations</a>.</p></div></div>'
        f'<script type="application/json" id="ff-data">{json.dumps(data)}</script></section>')


LOCALS = yaml.safe_load(open(os.path.join(SRC, "data", "locals.yaml"), encoding="utf-8"))["locals"]


def locals_list():
    """Our favorite local businesses, with verified links and LocalBusiness data for search and AI."""
    items, ld = [], []
    for b in LOCALS:
        links = [(k, b[k]) for k in ("url", "instagram", "facebook") if b.get(k)]
        lab = {"url": "Website", "instagram": "Instagram", "facebook": "Facebook"}
        ls = "".join(f'<a href="{u}" rel="noopener" target="_blank">{lab[k]}</a>' for k, u in links)
        meta = " &middot; ".join(html.escape(x) for x in (b.get("address"), b.get("phone")) if x)
        items.append(f'<article class="lf"><h2 id="{b["id"]}">{html.escape(b["name"])}</h2><p>{html.escape(b["what"])}</p>'
                     f'{f"<p class=lf-meta>{meta}</p>" if meta else ""}{f"<p class=dine-links>{ls}</p>" if ls else ""}</article>')
        d = {"@type": b["kind"], "name": b["name"], "description": b["what"],
             "address": {"@type": "PostalAddress", "addressLocality": "June Lake", "addressRegion": "CA", "addressCountry": "US"}}
        if b.get("phone"): d["telephone"] = b["phone"]
        same = [b[k] for k in ("url", "instagram", "facebook") if b.get(k)]
        if same: d["sameAs"] = same
        ld.append({"@type": "ListItem", "position": len(ld) + 1, "item": d})
    data = {"@context": "https://schema.org", "@type": "ItemList", "name": "Local favorites near the Yosemite Gateway Chalet", "itemListElement": ld}
    return Markup('<div class="lf-list">' + "".join(items) + '</div>'
                  f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


def guide_says(text, label="From the guide's chair"):
    """An aside from the guide: confident, unqualified, occasionally right."""
    return Markup(f'<aside class="gs"><p class="gs-k">{html.escape(label)}</p><p class="gs-t">{text}</p></aside>')


def tioga_data():
    """Tioga Road opening dates and April 1 snowpack (NPS), embedded for the analysis charts."""
    import csv
    rows = list(csv.DictReader(open(os.path.join(SRC, "data", "tioga.csv"), encoding="utf-8")))
    data = [{"y": int(r["year"]), "open": r["open"], "close": r["close"] or None,
             "snow": int(r["snowpack"]) if r["snowpack"] else None, "note": r["note"] or None} for r in rows]
    return Markup(f'<script type="application/json" id="tioga-data">{json.dumps(data)}</script>')


def tioga(kind, label=""):
    """Placeholder the analysis script draws into: residuals, predictor, eras or table."""
    return Markup(f'<div class="tg-block tg-{kind}" data-tioga="{kind}" role="img" aria-label="{html.escape(label, quote=True)}"></div>'
                  if label else f'<div class="tg-block tg-{kind}" data-tioga="{kind}"></div>')


def note(text):
    return Markup(f'<aside class="note"><p>{text}</p></aside>')


def trail_card(title, pairs, img=None, alt="", cap=None, kicker="Trail notes"):
    """A boxed set of trail notes, with an optional photo, the way the Parker Lake card looks."""
    pic = picture(img, alt, "(min-width: 1200px) 780px, (min-width: 760px) 66vw, 100vw") if img else ""
    rows = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>" for k, v in pairs)
    capp = f'<p class="tc-cap">{cap}</p>' if cap else ""
    cls = "trail-card" + ("" if img else " no-img")
    return Markup(f'<aside class="{cls}">{pic}<div class="tc-body"><p class="tc-kicker">{html.escape(kicker)}</p>'
                  f'<p class="tc-title">{html.escape(title)}</p><dl>{rows}</dl>{capp}</div></aside>')


def facts(pairs):
    lis = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in pairs)
    return Markup(f'<dl class="facts">{lis}</dl>')


# ------------------------------------------------------------------ content
def load_content():
    items = []
    for dirpath, _, files in os.walk(os.path.join(SRC, "content")):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            raw = open(os.path.join(dirpath, f), encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
            meta, body = yaml.safe_load(m.group(1)), m.group(2)
            meta["source"] = os.path.relpath(os.path.join(dirpath, f), ROOT)
            meta["body_src"] = body
            items.append(meta)
    return items


MD_EXT = ["tables", "attr_list", "md_in_html", "toc", "smarty", "sane_lists"]


def render_md(text, env, ctx):
    md_env = Environment(autoescape=False, comment_start_string="{##", comment_end_string="##}")
    md_env.globals.update(env.globals)
    t = md_env.from_string(text)
    rendered = t.render(**ctx)
    md = markdown.Markdown(extensions=MD_EXT, extension_configs={"toc": {"permalink": False}})
    out = md.convert(rendered)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    return Markup(out), toc


# ------------------------------------------------------------------ schema
def business_ld():
    a = P["address"]
    h = P["home"]
    return {
        "@context": "https://schema.org",
        "@type": "VacationRental",
        "@id": SITE + "/#chalet",
        "additionalType": "EntirePlace",
        "name": P["name"],
        "alternateName": ["Yosemite Chalet"],
        "description": (f"A {h['square_feet']:,} square foot log chalet in June Lake, California, rented as a whole home. "
                        f"Sleeps {h['max_overnight_guests']} in three private suites, with an outdoor hydrotherapy tub, "
                        "one mile from June Mountain and 27 miles from Yosemite's Tioga Pass entrance."),
        "url": SITE + "/",
        "telephone": P["phone"]["tel"],
        "image": [f"{SITE}/img/{n}-{IMAGES[n]['widths'][-1]}.webp" for n in
                  ("chalet-exterior-carson-peak", "grand-room-oak-bar-wine", "hydrotherapy-tub-night-steam",
                   "master-suite-jacuzzi-and-beds", "elsie-room-red-claw-foot-tub", "river-room-suite",
                   "kitchen-copper-sink", "grand-room-daylight", "master-suite-shower", "hydrotherapy-tub-winter-guests",
                   "yost-meadow-out-the-back-door", "paddleboard-rush-creek-silver-lake")],
        "address": {"@type": "PostalAddress", "streetAddress": a["street"], "addressLocality": a["city"],
                    "addressRegion": a["region"], "postalCode": a["postal"], "addressCountry": a["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": P["geo"]["lat"], "longitude": P["geo"]["lng"]},
        "containedInPlace": {"@type": "Place", "name": "June Lake, California",
                             "containedInPlace": {"@type": "AdministrativeArea", "name": "Mono County, California",
                                                  "sameAs": "https://en.wikipedia.org/wiki/Mono_County,_California"},
                             "sameAs": "https://en.wikipedia.org/wiki/June_Lake,_California"},
        "checkinTime": h["check_in_24"], "checkoutTime": h["check_out_24"],
        "petsAllowed": False,
        "priceRange": f"${h['rate_low']}-${h['rate_high']} per night",
        "identifier": P["booking"]["vrbo_id"],
        "sameAs": [P["booking"]["vrbo_url"], P["booking"]["airbnb_url"], P["social"]["x_url"]],
        "knowsAbout": ["June Lake", "Tioga Pass", "Tuolumne Meadows", "Yosemite National Park", "June Mountain",
                       "Eastern Sierra"],
        "containsPlace": {
            "@type": "Accommodation",
            "additionalType": "EntirePlace",
            "name": P["name"],
            "occupancy": {"@type": "QuantitativeValue", "value": h["max_overnight_guests"], "maxValue": h["max_overnight_guests"]},
            "numberOfBedrooms": h["bedrooms"],
            "numberOfFullBathrooms": h["full_baths"],
            "numberOfPartialBathrooms": h["half_baths"],
            "numberOfBathroomsTotal": h["full_baths"] + h["half_baths"],
            "numberOfRooms": h["bedrooms"],
            "floorSize": {"@type": "QuantitativeValue", "value": h["square_feet"], "unitCode": "FTK"},
            "bed": [{"@type": "BedDetails", "typeOfBed": b["type"], "numberOfBeds": b["count"]} for b in P["beds"]],
            "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in P["amenities"]],
            "petsAllowed": False,
        },
    }


def crumbs_ld(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]}


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": strip_tags(q["a"])}}
        for q in faq]}


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", markdown.markdown(s)).strip()


def article_ld(meta, url):
    d = {"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
         "description": meta["description"], "mainEntityOfPage": SITE + url,
         "datePublished": str(meta.get("published", BUILD_DATE)), "dateModified": str(meta.get("updated", BUILD_DATE)),
         "author": ({"@type": "Person", "name": "Robert Foster", "worksFor": {"@id": SITE + "/#chalet"}}
                    if meta.get("template") in ("guide", "analysis") else {"@type": "Organization", "name": P["name"], "url": SITE + "/"}),
         "publisher": {"@id": SITE + "/#chalet"}}
    if meta.get("sources"):
        # sources stay machine-readable for search and AI engines, without a visible list
        d["citation"] = [{"@type": "CreativeWork", "name": x["title"], "url": x["url"]} for x in meta["sources"]]
    if meta.get("og") and not meta.get("hero"):
        d["image"] = f"{SITE}/og/{meta['og']}.jpg"
    if meta.get("hero"):
        n = meta["hero"]
        d["image"] = f"{SITE}/img/{n}-{IMAGES[n]['widths'][-1]}.webp"
    return d


def place_ld(p):
    d = {"@context": "https://schema.org", "@type": p.get("type", "TouristAttraction"), "name": p["name"],
         "description": p["description"]}
    if p.get("lat"):
        d["geo"] = {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lng"]}
    if p.get("containedIn"):
        d["containedInPlace"] = {"@type": "Place", "name": p["containedIn"]}
    if p.get("url"):
        d["sameAs"] = p["url"]
    return d


# ------------------------------------------------------------------ build
def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(ROOT, "public"), DIST)

    env = Environment(loader=FileSystemLoader(os.path.join(SRC, "templates")),
                      autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    helpers = dict(picture=picture, figure=figure, gallery=gallery, story=story, glance=glance, video_tour=video_tour, quote=quote, reviews_wall=reviews_wall, review_scores=review_scores, tioga_data=tioga_data, tioga=tioga, ff_calendar=ff_calendar, ff_drive=ff_drive, ff_facts=ff_facts, ff_tool=ff_tool, guide_says=guide_says, locals_list=locals_list, distance_table=distance_table, note=note, film=film,
                   facts=facts, trail_card=trail_card, P=P, IMAGES=IMAGES)
    import hashlib
    def asset_v(rel):
        return hashlib.md5(open(os.path.join(ROOT, "public", rel), "rb").read()).hexdigest()[:10]
    env.globals.update(helpers, NAV=NAV, FOOTER=FOOTER, SITE=SITE, year=dt.date.today().year,
                       CSS_V=asset_v("css/site.css"), JS_V=asset_v("js/site.js"), TG_V=asset_v("js/tioga.js"), FF_V=asset_v("js/flyfish.js"))
    env.filters["md"] = lambda s: Markup(markdown.markdown(str(s), extensions=["smarty"]))
    env.filters["longdate"] = lambda d: (d.strftime("%B %-d, %Y") if hasattr(d, "strftime") else str(d))

    content = load_content()
    by_url = {c["url"]: c for c in content}
    env.globals["pages"] = by_url
    sitemap = []
    llms_full = []

    for c in sorted(content, key=lambda c: c["url"]):
        url = c["url"]
        body, toc = render_md(c["body_src"], env, {**helpers, "page": c, "pages": by_url})
        crumbs = [("Home", "/")]
        parts = [p for p in url.strip("/").split("/") if p]
        for i in range(1, len(parts)):
            parent = "/" + "/".join(parts[:i]) + "/"
            if parent in by_url:
                crumbs.append((by_url[parent].get("nav_title", by_url[parent]["title"]), parent))
        if url != "/":
            crumbs.append((c.get("nav_title", c["title"]), url))
        ld = [] if url == "/" else [crumbs_ld(crumbs)]
        if c.get("business_schema"):
            ld.insert(0, business_ld())
        if c.get("faq"):
            ld.append(faq_ld(c["faq"]))
        if c.get("template") in ("guide", "post", "analysis"):
            ld.append(article_ld(c, url))
        for pl in c.get("places", []) or []:
            ld.append(place_ld(pl))
        related = [by_url[r] for r in c.get("related", []) if r in by_url]
        tpl = env.get_template(c.get("template", "page") + ".html")
        out = tpl.render(page=c, body=body, toc=toc, crumbs=crumbs, related=related,
                         jsonld=Markup("\n".join(
                             f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)),
                         canonical=SITE + url)
        if c.get("output"):
            path = os.path.join(DIST, c["output"])
        else:
            d = os.path.join(DIST, url.strip("/"))
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, "index.html")
        open(path, "w", encoding="utf-8").write(out)
        if not c.get("noindex"):
            sitemap.append((url, str(c.get("updated", c.get("published", BUILD_DATE)))))
        if c.get("template") in ("guide", "analysis"):
            text = re.sub(r"<[^>]+>", "", str(body))
            text = re.sub(r"\n{3,}", "\n\n", html.unescape(text)).strip()
            llms_full.append(f"# {c['title']}\n\nURL: {SITE}{url}\nLast checked: {c.get('updated')}\n\n{c.get('lead','')}\n\n{text}\n")

    # shoutouts.json: a plain feed of local businesses and ready-to-post blurbs for social tools and bots
    feed = {"source": SITE + "/local-favorites/", "updated": str(BUILD_DATE),
            "note": "Local businesses the Yosemite Gateway Chalet recommends. Each entry has verified links and ready-to-post text under 240 characters. Please credit and link the business.",
            "businesses": [{k: b[k] for k in ("id", "name", "what", "address", "phone", "url", "instagram", "facebook", "handle", "posts") if b.get(k)}
                           | {"page": SITE + "/local-favorites/#" + b["id"], "mentioned_on": [SITE + u for u in b.get("used_on", [])]} for b in LOCALS]}
    open(os.path.join(DIST, "shoutouts.json"), "w").write(json.dumps(feed, indent=1, ensure_ascii=False))

    # sitemap
    urls = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in sorted(sitemap))
    open(os.path.join(DIST, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

    # llms.txt
    ctx = dict(P=P, pages=by_url, SITE=SITE, BUILD_DATE=BUILD_DATE)
    llms = env.get_template("llms.txt").render(**ctx)
    open(os.path.join(DIST, "llms.txt"), "w").write(llms)
    open(os.path.join(DIST, "llms-full.txt"), "w").write(
        f"# {P['name']}: destination guides\n\n> Full text of the guides published at {SITE}. Facts were checked against the "
        "sources listed in each guide on the date shown.\n\n" + "\n\n---\n\n".join(llms_full))
    print(f"built {len(content)} pages into dist/")


if __name__ == "__main__":
    main()
