// PASO IMPORTANTE: Incrementa la versión del caché.
// Esto asegura que el navegador descarte el caché antiguo y cree uno nuevo.
const CACHE_NAME = 'control-salidas-cache-v4'; 
const urlsToCache = [
  '/',
  '/index',
  '/scan',
  '/static/img/logo.png',
  '/static/img/avatar.png'
];

// El evento 'install' no cambia, sigue precargando la app shell.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache abierto y precargado');
        return cache.addAll(urlsToCache);
      })
  );
});

// El evento 'activate' se usa para limpiar cachés viejos.
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Borrando caché antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// CAMBIO CLAVE: Nueva lógica para el evento 'fetch' (Network First)
self.addEventListener('fetch', event => {
  // Ignorar peticiones que no son GET (como POST)
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    // 1. Intenta obtener el recurso de la red primero.
    fetch(event.request)
      .then(networkResponse => {
        // 2. Si la red responde, guarda una copia en el caché y devuelve la respuesta.
        // Es importante clonar la respuesta, ya que solo se puede consumir una vez.
        let responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME)
          .then(cache => {
            cache.put(event.request, responseToCache);
          });
        return networkResponse;
      })
      .catch(error => {
        // 3. Si la red falla, intenta obtener el recurso del caché.
        console.log('La red falló, intentando servir desde el caché para:', event.request.url);
        return caches.match(event.request);
      })
  );
});