/* Sing Korean — service worker
 * Cache first with a background refresh. Song files are immutable once built,
 * so they are worth caching hard; the shell and the index are checked against
 * the network first so a new build reaches people on their next visit.
 * Bump VERSION on every deploy. */
const VERSION = 'sk-v1-20261024';
const CORE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-512.png',
  './data/index.json',
  './data/freq.json'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION)
      .then((c) => Promise.allSettled(CORE.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  const shell = e.request.mode === 'navigate'
    || url.pathname === '/'
    || /\.(html|webmanifest)$/.test(url.pathname)
    || url.pathname.endsWith('/data/index.json');
  e.respondWith(
    caches.open(VERSION).then(async (cache) => {
      const cached = await cache.match(e.request, { ignoreSearch: true });
      const fetched = fetch(e.request)
        .then((res) => { if (res && res.ok) cache.put(e.request, res.clone()); return res; })
        .catch(() => null);
      if (shell) {
        const res = await fetched;
        return res || cached || offline();
      }
      return cached || (await fetched) || offline();
    })
  );
});

function offline() {
  return new Response('You are offline. Pages you have opened before still work.', {
    status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' }
  });
}
