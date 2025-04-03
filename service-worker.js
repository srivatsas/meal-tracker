self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("meal-tracker").then((cache) =>
      cache.addAll([
        "/",
        "/home",
        "/static/style.css",
        "/manifest.json",
        "/static/icons/icon-192.png",
        "/static/icons/icon-512.png"
      ])
    )
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
