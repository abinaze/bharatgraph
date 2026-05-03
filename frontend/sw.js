// BharatGraph Service Worker v5
// BUG-28 FIX: API responses were cached indefinitely
// NEW-A5 FIX: host === "hf.space" never matches -- HF uses *.hf.space subdomains
// SW-01 FIX: use relative paths so caching works on GitHub Pages

const CACHE = "bharatgraph-v5";
const STATIC = [
  "./",
  "./index.html",
  "./css/design-system.css",
  "./css/components.css",
  "./js/router.js",
  "./js/api.js",
  "./js/components.js",
  "./js/graph.js",
  "./js/timeline.js",
  "./js/evidence_panel.js",
  "./js/app.js"
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(STATIC))
      .catch(() => {})   // never block install on cache failure
  );
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const reqUrl = new URL(e.request.url);
  const host   = reqUrl.hostname;
  const path   = reqUrl.pathname;

  // NEW-A5 FIX: HuggingFace Spaces run on *.hf.space subdomains.
  // The previous check `host === "hf.space"` never matched because the actual
  // hostname is e.g. "abinazebinoly-bharatgraph.hf.space" -- use endsWith().
  // BUG-28 FIX: all API paths must be network-first, never cached.
  const isHfSpace    = host.endsWith(".hf.space") || host === "hf.space";
  const isApiPath    = path.startsWith("/search") ||
                       path.startsWith("/profile") ||
                       path.startsWith("/risk") ||
                       path.startsWith("/graph") ||
                       path.startsWith("/biography") ||
                       path.startsWith("/investigate") ||
                       path.startsWith("/admin") ||
                       path.startsWith("/stats") ||
                       path.startsWith("/health") ||
                       path.startsWith("/ws/") ||
                       path.startsWith("/runtime") ||
                       path.startsWith("/multilingual") ||
                       path.startsWith("/export");
  const isLocalApi   = host === "localhost" || host === "127.0.0.1";

  const isApi = isHfSpace || (isLocalApi && isApiPath);

  if (isApi) {
    // Network-first: always go to network, fall back to error JSON
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(
          JSON.stringify({ error: "API temporarily unavailable" }),
          { status: 503, headers: { "Content-Type": "application/json" } }
        )
      )
    );
    return;
  }

  // Static assets: cache-first
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(response => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
        return response;
      });
    })
  );
});
