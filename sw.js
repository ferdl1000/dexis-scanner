// DEXIS Scanner Service Worker
// - Cache-First für App-Shell (HTML, Icons, externe Libs)
// - Network-First für articles.json (Auto-Update Quelle)
// - Offline-fähig nach erstem Aufruf

const VERSION = 'dorn-v4.0.0';
const SHELL = [
  './',
  './index.html',
  './scanner-app.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon.ico',
  'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.6.0/jspdf.plugin.autotable.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(VERSION)
      .then(c => Promise.all(SHELL.map(u =>
        c.add(u).catch(err => console.warn('SW skip cache:', u, err))
      )))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);

  // Nicht-GET: durchlassen
  if (req.method !== 'GET') return;

  // articles.json: Network-First (für Auto-Update)
  if (url.pathname.endsWith('/articles.json')) {
    e.respondWith(
      fetch(req).then(resp => {
        const copy = resp.clone();
        caches.open(VERSION).then(c => c.put(req, copy)).catch(()=>{});
        return resp;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // Sonst: Cache-First, mit Hintergrund-Update
  e.respondWith(
    caches.match(req).then(cached => {
      const network = fetch(req).then(resp => {
        if (resp && resp.status === 200 && (resp.type === 'basic' || resp.type === 'cors')) {
          const copy = resp.clone();
          caches.open(VERSION).then(c => c.put(req, copy)).catch(()=>{});
        }
        return resp;
      }).catch(() => cached);
      return cached || network;
    })
  );
});
