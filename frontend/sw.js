const CACHE = "bharatgraph-v1";
const STATIC = ["/","/index.html","/css/design-system.css",
  "/css/components.css","/js/router.js","/js/api.js",
  "/js/components.js","/js/graph.js","/js/app.js"];

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
  const isApi = e.request.url.includes("hf.space") || e.request.url.includes("/api/");
  if (isApi) {
    e.respondWith(
      fetch(e.request)
        .then(r => { if (r.ok) caches.open(CACHE).then(c => c.put(e.request, r.clone())); return r; })
        .catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
  }
});
