/**
 * Service Worker for The Triumvirate
 * Provides offline functionality and performance optimization
 */

const CACHE_VERSION = 'v1.0.1';
const CACHE_NAME = `triumvirate-${CACHE_VERSION}`;

// Assets to cache on install
const STATIC_ASSETS = [
  '/the_triumvirate/',
  '/the_triumvirate/index.html',
  '/the_triumvirate/404.html',
  '/the_triumvirate/css/main.css',
  '/the_triumvirate/css/tailwind.css',
  '/the_triumvirate/public/manifest.json',
  '/the_triumvirate/assets/images/og-image.png',
  '/the_triumvirate/assets/images/twitter-card.png',
  '/the_triumvirate/assets/images/icon-192x192.png',
  '/the_triumvirate/assets/images/icon-512x512.png',
  '/the_triumvirate/pages/manifesto_gateway.html',
  '/the_triumvirate/pages/trinity_deep_dive.html',
  '/the_triumvirate/pages/project_ai_cognitive_engine.html',
  '/the_triumvirate/pages/cerberus_security_fortress.html',
  '/the_triumvirate/pages/codex_deus_maximus_repository.html',
  '/the_triumvirate/pages/jeremy_karrick_founder_profile.html',
  '/the_triumvirate/pages/research_center.html',
  '/the_triumvirate/pages/scenario_demonstrations.html',
  '/the_triumvirate/pages/trust_transparency_center.html',
  '/the_triumvirate/pages/future_architectures.html'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => cacheName.startsWith('triumvirate-') && cacheName !== CACHE_NAME)
            .map((cacheName) => {
              console.log('[ServiceWorker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) return;

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // Return cached version and update cache in background
          event.waitUntil(
            fetch(event.request)
              .then((response) => {
                if (response && response.status === 200) {
                  const responseToCache = response.clone();
                  caches.open(CACHE_NAME)
                    .then((cache) => cache.put(event.request, responseToCache));
                }
              })
              .catch(() => {
                // Fetch failed, but we already have cached version
              })
          );
          return cachedResponse;
        }

        // Not in cache, fetch from network
        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type === 'error') {
              return response;
            }

            // Cache successful responses
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => cache.put(event.request, responseToCache));

            return response;
          })
          .catch((error) => {
            console.error('[ServiceWorker] Fetch failed:', error);
            
            // Return offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match('/the_triumvirate/404.html')
                .then((offlinePage) => offlinePage || caches.match('/the_triumvirate/index.html'));
            }
            
            throw error;
          });
      })
  );
});

// Message event - handle skip waiting
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
