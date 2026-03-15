const CACHE_NAME = 'qct-cache-v1';

// Sadece arayüzün temellerini (HTML, CSS iskeleti ve QR kütüphanesini) önbelleğe alıyoruz.
// Kullanıcı interneti olmasa bile uygulamayı açabilecek.
const urlsToCache = [
  '/',
  'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js'
];

// Kurulum (Install): Dosyaları önbelleğe al
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Arayüz dosyaları önbelleğe alındı.');
        return cache.addAll(urlsToCache);
      })
  );
});

// Aktivasyon (Activate): Eski önbellekleri temizle
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eski önbellek silindi:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Yakalama (Fetch): İnternet varsa ağdan, yoksa önbellekten (Cache Fallback) getir
self.addEventListener('fetch', event => {
  // Sadece GET isteklerini önbellekle, WebSocket (ws://) veya POST isteklerine dokunma
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});