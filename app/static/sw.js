const CACHE_NAME = 'control-salidas-cache-v2';
const urlsToCache = [
  '/',
  '/index',
  '/scan',
  // Agrega aquí otras URLs importantes y archivos estáticos (CSS, JS)
  '/static/img/logo.png',
  '/static/img/avatar.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response; // Servir desde la caché
        }
        return fetch(event.request); // Si no está en caché, ir a la red
      }
    )
  );
});