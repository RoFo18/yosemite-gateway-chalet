// Live availability for the chalet.
// Reads the Airbnb and VRBO iCal feeds (URLs live in Netlify environment variables,
// never in this repo), merges the booked nights, and returns them as JSON.
// Netlify's CDN caches the answer for 15 minutes, so the feeds are not hit on every visit.

const FEEDS = [
  ["airbnb", process.env.AIRBNB_ICAL_URL],
  ["vrbo", process.env.VRBO_ICAL_URL],
].filter(([, url]) => url);

const iso = (d) => d.toISOString().slice(0, 10);
const addDays = (s, n) => { const d = new Date(s + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return iso(d); };

// "20261101" or "20261101T160000Z" -> "2026-11-01"
const toDate = (v) => { const m = /(\d{4})(\d{2})(\d{2})/.exec(v || ""); return m ? `${m[1]}-${m[2]}-${m[3]}` : null; };

export function parseIcs(text) {
  const lines = text.replace(/\r?\n[ \t]/g, "").split(/\r?\n/);
  const ranges = [];
  let ev = null;
  for (const line of lines) {
    if (line.startsWith("BEGIN:VEVENT")) ev = {};
    else if (line.startsWith("END:VEVENT")) {
      if (ev && ev.start) {
        const end = ev.end && ev.end > ev.start ? ev.end : addDays(ev.start, 1);
        ranges.push([ev.start, end]);
      }
      ev = null;
    } else if (ev) {
      const i = line.indexOf(":");
      const key = line.slice(0, i).split(";")[0];
      if (key === "DTSTART") ev.start = toDate(line.slice(i + 1));
      if (key === "DTEND") ev.end = toDate(line.slice(i + 1));
    }
  }
  return ranges;
}

// Merge [start, end) night ranges that overlap or touch.
export function merge(ranges) {
  const out = [];
  for (const [s, e] of [...ranges].sort((a, b) => (a[0] < b[0] ? -1 : 1))) {
    const last = out[out.length - 1];
    if (last && s <= last[1]) { if (e > last[1]) last[1] = e; }
    else out.push([s, e]);
  }
  return out;
}

export default async () => {
  const today = iso(new Date());
  const results = await Promise.allSettled(
    FEEDS.map(async ([name, url]) => {
      const r = await fetch(url, { headers: { "user-agent": "YosemiteGatewayChalet/1.0 availability" }, signal: AbortSignal.timeout(8000) });
      if (!r.ok) throw new Error(`${name} ${r.status}`);
      const text = await r.text();
      if (!text.includes("BEGIN:VCALENDAR")) throw new Error(`${name} not a calendar`);
      return parseIcs(text);
    })
  );
  const ok = results.filter((r) => r.status === "fulfilled");
  if (!ok.length) {
    return Response.json({ error: "calendars unavailable" }, { status: 503, headers: { "cache-control": "no-store" } });
  }
  const booked = merge(ok.flatMap((r) => r.value)).filter(([, e]) => e > today);
  return Response.json(
    { updated: new Date().toISOString(), complete: ok.length === FEEDS.length, booked },
    {
      headers: {
        "cache-control": "public, max-age=0, must-revalidate",
        "netlify-cdn-cache-control": "public, durable, s-maxage=900, stale-while-revalidate=3600",
      },
    }
  );
};

export const config = { path: "/api/availability" };
