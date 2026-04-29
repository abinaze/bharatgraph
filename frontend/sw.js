// BharatGraph Service Worker v4
// SW-01 FIX: use relative paths so caching works on GitHub Pages
// (site is at /bharatgraph/ prefix, not /)
const CACHE = "bharatgraph-v4";
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
  const host = reqUrl.hostname;
  const path = reqUrl.pathname;
  // API calls: always network-first, never cached
  // L-01 FIX: check for API host/path specifically, not raw URL substrings
  const isGithubIoHost = host === "github.io" || host.endsWith(".github.io");
  const isApi = host === "hf.space" ||
                path.includes("/api/") ||
                path.includes("/health") ||
                path.includes("/stats") ||
                path.includes("/investigate") ||
                (path.includes("/search") && !isGithubIoHost);
  if (isApi) {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(
          JSON.stringify({ error: "API temporarily unavailable" }),
          { status: 503, headers: { "Content-Type": "application/json" } }
        )
      )
    );
  } else {
    // Static assets: cache-first
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request))
    );
  }
});
