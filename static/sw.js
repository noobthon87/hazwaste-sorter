// HazWaste Sorter Service Worker
// Enables PWA installation ("Add to Home Screen") and standalone launch.

const CACHE_NAME = 'hazwaste-v1';
const STATIC_ASSETS = [
  '/',
  '/static/style.css',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/apple-touch-icon.png',
  '/static/favicon.ico'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Network-first strategy: always fetch fresh from server, fallback to cache if offline
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        return response;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
