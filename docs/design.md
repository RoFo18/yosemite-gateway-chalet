# Design system

The Yosemite Gateway Chalet site should feel quiet, expensive and specific to its place: granite, lodgepole pine, aspen gold, snow, firelight on log walls. It is an editorial magazine, not a booking engine.

## Palette

| Token | Light | Dark | Use |
|---|---|---|---|
| `--ground` | `#f2f1ec` granite flour | `#111613` | Page background |
| `--paper` | `#fbfaf7` first snow | `#171d19` | Alternate bands, cards |
| `--ink` | `#18201c` lodgepole night | `#ecebe5` | Headings, primary text, solid buttons |
| `--ink-2` | `#4c544f` weathered bark | `#b2b7b0` | Body copy |
| `--ink-3` | `#626963` | `#8b918a` | Labels, captions (4.99:1 on ground) |
| `--rule` | `#d8d8d0` | `#2b332e` | Hairlines |
| `--bronze` | `#8a6536` aspen bronze | `#d2a96f` | Eyebrows, list markers, the one accent |
| `--night` | `#121915` | same | Footer, menu overlay, "where to stay" panels |

One accent only. Bronze is never a fill, only type and hairlines. Over photography, eyebrows use a warm `#e8d2a8`.

## Type

- **Display:** Cormorant Garamond 500 (and italic 500). Headings, the wordmark, large statements, numbers in the distance band.
- **Text:** Work Sans 400 and 500. Body, UI, labels.
- **Labels:** Work Sans 500, 0.70 to 0.78rem, uppercase, 0.18 to 0.26em tracking.
- **Scale:** h1 2.6 to 5.4rem (hero up to 6rem), h2 2 to 3.4rem, h3 1.45 to 1.9rem, statement 1.55 to 2.45rem, body 1.0625rem at 1.72 line height.
- **Measure:** body copy is held to about 64 characters.
- Fonts load from Google Fonts with `display=swap` and serif and sans fallbacks. To self-host later, drop the WOFF2 files in `public/fonts/` and swap the `<link>` in `src/templates/base.html` for `@font-face` rules.

## Space and grid

- Spacing scale: 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4.5 and 7rem (`--s-1` to `--s-9`).
- Side gutter: `clamp(20px, 5vw, 72px)`. Content max width 1320px. Reading column 900px.
- Asymmetric splits (7:5 and 7:4) rather than halves. Sections breathe: 4.5 to 7rem between bands.
- Hairline rules and space separate things. No card shadows, no rounded corners. Buttons are square.

## Photography

- Full-bleed only for photos that can hold it: the chalet under Carson Peak (home), fall aspens, the alpine lake (closing band), and page heroes.
- Smaller interior photos (many are 860px wide from 2014) appear framed: three-up suite cards, galleries, and floated figures. Never stretched past native width.
- `scripts/images.py` trims the black letterbox bars baked into the old slideshow images, renames every file descriptively, and writes AVIF and WebP at 480, 800, 1200 and 1800 wide (never larger than the original).
- Never use an image with text printed on it. The old `gallery_intro_header_*` images and the "SKI JUNE MT." postcard are excluded.
- Each image's dominant color is the placeholder background while it loads.
- New professional photography is the single biggest upgrade available. Shoot the exterior at golden hour, the tub at dusk with steam, each suite in daylight, and the Grand Room with the fire lit.

## Motion

- The hero photo settles from 104.5% to 100% over 2.4 seconds on load.
- Sections below the fold rise 18px and fade in as they enter the viewport. Content is always visible without JavaScript, and nothing animates when the visitor prefers reduced motion.
- Image hover: a slow 3 to 5% zoom over one second.
- The masthead is transparent over hero photos and turns solid after 80px of scroll.

## Components

- **Masthead:** wordmark, six links, an outlined Inquire button. Below 1100px, a full-screen dark menu in large serif type.
- **Mobile inquiry bar:** slides up after the first screen on phones, with Inquire and Call.
- **Distance band:** five figures in display type with small tracked units. Signature element.
- **Facts list:** label and value pairs on hairlines, for specs on every room page.
- **Guide layout:** sticky "At a glance" and contents rail, an answer-first lead in display type, a dated byline, FAQ, a dark "Where to stay" panel, and sources.
- **Closing band:** every page except Inquire, Thank you, Privacy and 404 ends with an inquiry call to action over the alpine lake.
