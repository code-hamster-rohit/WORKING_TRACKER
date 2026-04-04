const CACHE_NAME = 'working-tracker-v2';
const ASSETS_TO_CACHE = [
    '/',
    '/previous-workings',
    '/static/manifest.json',
    '/static/images/logo.png',
    '/static/css/style.css',
    '/static/css/add_working.css',
    '/static/css/previous_workings.css',
    '/static/js/script.js',
    '/static/js/add_working.js',
    '/static/js/previous_workings.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS_TO_CACHE))
            .catch(err => console.error('Cache addAll failed:', err))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // If network fetch is successful, clone the response and update the cache
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }
                const responseToCache = response.clone();
                caches.open(CACHE_NAME)
                    .then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                return response;
            })
            .catch(() => {
                // If network request fails (e.g., offline), fallback to cache
                return caches.match(event.request);
            })
    );
});
