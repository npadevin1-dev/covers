const CACHE_NAME = 'cover-repo-v2';
const ASSETS = [
  './',
  './index.html',
  './songs.html'
];

// Установка воркера и кэширование страниц
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(self.clients.claim());
});

// Умный перехват запросов
self.addEventListener('fetch', (e) => {
  const url = e.request.url;

  // Если это аудио-запрос (с Dropbox или .mp3)
  if (url.includes('dropbox.com') || url.includes('.mp3')) {
    e.respondWith(
      caches.match(e.request).then((cachedResponse) => {
        if (cachedResponse) {
          // Корректно возвращаем аудио из кэша для Range-запросов (статус 206)
          return cachedResponse;
        }

        // Если в кэше нет, качаем из сети БЕЗ CORS-блокировки (mode: 'cors' или 'no-cors' в зависимости от плеера)
        // Для аудио с Dropbox лучше использовать стандартный fetch, но если он падает, обрабатываем оффлайн
        return fetch(e.request).then((networkResponse) => {
          if (!networkResponse || networkResponse.status !== 200) {
            return networkResponse;
          }

          // Дублируем в кэш только чистые ответы
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(e.request, responseToCache);
          });
          return networkResponse;
        }).catch(() => {
          // Если инет пропал, пытаемся вытащить хоть что-то
          return caches.match(e.request);
        });
      })
    );
  } else {
    // Для обычных страниц сайта (HTML, CSS) стандартная схема: Кэш -> Сеть
    e.respondWith(
      caches.match(e.request).then((response) => {
        return response || fetch(e.request);
      })
    );
  }
});
