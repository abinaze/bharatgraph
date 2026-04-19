// BUG-12/23 FIX: was caching API responses (health, search, stats) with cache-then-network.
// Cold-start 503 responses were being served from cache for minutes.
// Fix: static assets only (cache-first). API calls always network-first, no caching.
// Never cache health, search, stats, investigate — these must always be fresh.
const CACHE = "bharatgraph-v4";
const STATIC = [
  "/","/index.html",
  "/css/design-system.css","/css/components.css",
  "/js/router.js","/js/api.js","/js/components.js",
  "/js/graph.js","/js/timeline.js","/js/evidence_panel.js","/js/app.js"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = e.request.url;
  // BUG-12/23 FIX: API calls NEVER cached — always fetch live from network
  const isApi = url.includes("hf.space") || url.includes("/api/") ||
                url.includes("/health") || url.includes("/stats") ||
                url.includes("/search") || url.includes("/investigate");
  if (isApi) {
    // Network only — no cache fallback for API
    e.respondWith(fetch(e.request).catch(() =>
      new Response(JSON.stringify({error:"API temporarily unavailable"}),
        {status:503, headers:{"Content-Type":"application/json"}})
    ));
  } else {
    // Static assets: cache-first
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
  }
});
