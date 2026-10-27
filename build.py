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
    ("Experiences", "/experiences/"),
    ("Guides", "/guides/"),
    ("Location", "/location/"),
    ("FAQ", "/faq/"),
]
FOOTER = [
    ("Stay", [("The Chalet", "/the-chalet/"), ("Suites", "/the-chalet/#suites"), ("Floorplan", "/the-chalet/floorplan/"),
              ("Gallery", "/gallery/"), ("Rates and policies", "/rates-and-policies/"), ("Inquire", "/inquire/")]),
    ("Guides", [("Tioga Pass", "/guides/tioga-pass/"), ("Tuolumne Meadows", "/guides/tuolumne-meadows/"),
                ("June Lake", "/guides/june-lake/"), ("June Lake Loop fall colors", "/guides/june-lake-fall-colors/"),
                ("Yosemite's east side in winter", "/guides/yosemite-east-side-in-winter/"),
                ("Lodging near Yosemite's east entrance", "/yosemite-national-park-lodging/"),
                ("June Lake lodging", "/june-lake-lodging/")]),
    ("Plan", [("Getting here", "/location/"), ("Experiences", "/experiences/"), ("FAQ", "/faq/"),
              ("Journal", "/journal/"), ("Privacy", "/privacy/")]),
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
    sizes = {"wide": "(min-width: 1100px) 1040px, 100vw", "full": "100vw",
             "right": "(min-width: 900px) 420px, 100vw", "left": "(min-width: 900px) 420px, 100vw",
             "small": "(min-width: 900px) 320px, 70vw"}.get(layout, "100vw")
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return Markup(f'<figure class="fig fig-{layout}">{picture(name, alt, sizes)}{cap}</figure>')


def gallery(items, cols=3):
    cells = "".join(
        f'<a class="g-cell" href="/img/{n}-{IMAGES[n]["widths"][-1]}.webp" data-lightbox aria-label="Enlarge: {html.escape(a, quote=True)}">'
        f'{picture(n, a, "(min-width: 900px) 33vw, 50vw")}</a>' for n, a in items)
    return Markup(f'<div class="gallery cols-{cols}">{cells}</div>')


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


def note(text):
    return Markup(f'<aside class="note"><p>{text}</p></aside>')


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
        "name": P["name"],
        "alternateName": [P["former_name"], "Yosemite Chalet"],
        "description": (f"A {h['square_feet']:,} square foot log chalet in June Lake, California, rented as a whole home. "
                        f"Sleeps {h['max_overnight_guests']} in three private suites, with an outdoor hydrotherapy tub, "
                        "one mile from June Mountain and 27 miles from Yosemite's Tioga Pass entrance."),
        "url": SITE + "/",
        "telephone": P["phone"]["tel"],
        "image": [f"{SITE}/img/{n}-{IMAGES[n]['widths'][-1]}.webp" for n in
                  ("chalet-exterior-carson-peak", "grand-room-oak-bar-wine", "hydrotherapy-tub-night-steam",
                   "master-suite-bed", "elsie-room-suite", "paddleboard-rush-creek-silver-lake")],
        "address": {"@type": "PostalAddress", "streetAddress": a["street"], "addressLocality": a["city"],
                    "addressRegion": a["region"], "postalCode": a["postal"], "addressCountry": a["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": P["geo"]["lat"], "longitude": P["geo"]["lng"]},
        "containedInPlace": {"@type": "Place", "name": a["area"]},
        "checkinTime": h["check_in_24"], "checkoutTime": h["check_out_24"],
        "petsAllowed": False,
        "identifier": P["booking"]["vrbo_id"],
        "sameAs": [P["booking"]["vrbo_url"]],
        "knowsAbout": ["June Lake", "Tioga Pass", "Tuolumne Meadows", "Yosemite National Park", "June Mountain",
                       "Eastern Sierra"],
        "containsPlace": {
            "@type": "Accommodation",
            "additionalType": "EntirePlace",
            "name": P["name"],
            "occupancy": {"@type": "QuantitativeValue", "maxValue": h["max_overnight_guests"]},
            "numberOfBedrooms": h["bedrooms"],
            "numberOfFullBathrooms": h["full_baths"],
            "numberOfPartialBathrooms": h["half_baths"],
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
         "author": {"@type": "Organization", "name": P["name"], "url": SITE + "/"},
         "publisher": {"@id": SITE + "/#chalet"}}
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
    helpers = dict(picture=picture, figure=figure, gallery=gallery, distance_table=distance_table, note=note, film=film,
                   facts=facts, P=P, IMAGES=IMAGES)
    env.globals.update(helpers, NAV=NAV, FOOTER=FOOTER, SITE=SITE, year=dt.date.today().year)
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
        if c.get("template") in ("guide", "post"):
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
        if c.get("template") == "guide":
            text = re.sub(r"<[^>]+>", "", str(body))
            text = re.sub(r"\n{3,}", "\n\n", html.unescape(text)).strip()
            llms_full.append(f"# {c['title']}\n\nURL: {SITE}{url}\nLast checked: {c.get('updated')}\n\n{c.get('lead','')}\n\n{text}\n")

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
