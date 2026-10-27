// The old WordPress site was hit by a "Japanese keyword hack" that created thousands of fake
// shopping pages like /?detail/723525913. Those addresses now land here. Tell search engines
// they are gone for good (410) instead of showing the home page, so they drop out of results fast.
// Runs only on the home page path, and only acts when the address carries a spam-style query.
const SPAM = /^\?(detail|goods|shop|product|item|list|category|cat|good|p=\d+&|[a-z]{1,12}\/\d{3,})/i;

export default async (request, context) => {
  const { search } = new URL(request.url);
  if (!search || !SPAM.test(search)) return context.next();
  const page = await fetch(new URL("/404.html", request.url));
  return new Response(page.body, {
    status: 410,
    headers: { "content-type": "text/html; charset=utf-8", "x-robots-tag": "noindex", "cache-control": "public, max-age=3600" },
  });
};

export const config = { path: "/" };
