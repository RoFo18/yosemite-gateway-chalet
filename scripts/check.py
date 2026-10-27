#!/usr/bin/env python3
"""Build the site and fail on anything that would hurt guests or search.

    python3 scripts/check.py

Checks: broken internal links and images, missing alt text, missing or duplicate
titles and descriptions, invalid JSON-LD, any email address in the output,
redirect targets that do not exist, em dashes in copy, and missing sitemap pages.
"""
import json, os, re, subprocess, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
import yaml
SITE = yaml.safe_load(open(os.path.join(ROOT, "src", "data", "property.yaml")))["site_url"].rstrip("/")
subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True)
errors = []
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z.]{2,}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.title, self.desc, self.ld, self._t, self._ld = [], [], None, None, [], False, False
        self.h1 = 0
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag in ("img",):
            self.imgs.append(a)
        if tag == "source" and a.get("srcset"):
            for part in a["srcset"].split(","): self.links.append(part.strip().split(" ")[0])
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href", "").startswith("/"): self.links.append(a["href"])
        if tag == "script" and a.get("src", "").startswith("/"): self.links.append(a["src"])
        if tag == "title": self._t = True
        if tag == "meta" and a.get("name") == "description": self.desc = a.get("content")
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True
        if tag == "h1": self.h1 += 1
    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        if tag == "script": self._ld = False
    def handle_data(self, d):
        if self._t: self.title = (self.title or "") + d
        if self._ld: self.ld.append(d)


def exists(url):
    url = url.split("#")[0].split("?")[0]
    if not url: return True
    p = os.path.join(DIST, url.lstrip("/"))
    if url.endswith("/"): p = os.path.join(p, "index.html")
    return os.path.exists(p)


titles, descs = {}, {}
pages = []
for d, _, fs in os.walk(DIST):
    for f in fs:
        path = os.path.join(d, f)
        rel = "/" + os.path.relpath(path, DIST)
        if f.endswith((".html", ".txt", ".xml", ".json", ".css", ".js")):
            text = open(path, encoding="utf-8").read()
            for m in EMAIL.finditer(text):
                if not m.group(0).endswith((".png", ".jpg", ".webp", ".avif", ".svg")):
                    errors.append(f"{rel}: email address published: {m.group(0)}")
            if "mailto:" in text: errors.append(f"{rel}: mailto link")
            if f.endswith((".html", ".txt")) and "—" in text: errors.append(f"{rel}: em dash in copy")
        if not f.endswith(".html"): continue
        pages.append(rel)
        p = Page(); p.feed(open(path, encoding="utf-8").read())
        url = rel.replace("index.html", "")
        if not p.title: errors.append(f"{url}: missing <title>")
        if not p.desc: errors.append(f"{url}: missing meta description")
        if p.h1 != 1: errors.append(f"{url}: {p.h1} h1 elements")
        if p.title: titles.setdefault(p.title.strip(), []).append(url)
        if p.desc: descs.setdefault(p.desc.strip(), []).append(url)
        for i in p.imgs:
            if "alt" not in i: errors.append(f"{url}: img without alt: {i.get('src')}")
            if i.get("src", "").startswith("/") and not exists(i["src"]): errors.append(f"{url}: missing image {i['src']}")
        for l in p.links:
            if l.startswith("/") and not l.startswith("//") and not exists(l):
                errors.append(f"{url}: broken link {l}")
        for block in p.ld:
            try: json.loads(block)
            except Exception as e: errors.append(f"{url}: invalid JSON-LD ({e})")

for t, us in titles.items():
    if len(us) > 1: errors.append(f"duplicate title on {us}: {t}")
for t, us in descs.items():
    if len(us) > 1: errors.append(f"duplicate description on {us}")

# redirects must land on real pages, in one hop
rules = []
for line in open(os.path.join(DIST, "_redirects")):
    line = line.strip()
    if not line or line.startswith("#"): continue
    src, dst, code = line.split()[:3]
    rules.append((src, dst, code))
sources = {src for src, _, _ in rules if src.startswith("/")}
for src, dst, code in rules:
    if not code.startswith("30"): continue
    path = (dst[len(SITE):] or "/") if dst.startswith(SITE) else dst
    if path.endswith(":splat"): continue
    if not exists(path):
        errors.append(f"_redirects: {src} -> {dst} does not exist")
    elif path.split("#")[0] in sources:
        errors.append(f"_redirects: {src} -> {dst} is a chain")

# sitemap covers every indexable page
sm = open(os.path.join(DIST, "sitemap.xml")).read()
for rel in pages:
    url = rel.replace("index.html", "")
    if url in ("/404.html", "/thank-you/"): continue
    if f"yosemitechalet.us{url}<" not in sm: errors.append(f"sitemap missing {url}")

if errors:
    print("\n".join(errors))
    print(f"\n{len(errors)} problem(s) found")
    sys.exit(1)
print(f"check passed: {len(pages)} pages, no problems")
