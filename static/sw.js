/* ══════════════════════════════════════════════
   Service Worker — VEM Transporte Universitário
   Estratégia: Network-First para páginas, cache como reserva offline
   Garante funcionamento Offline-First (RNF02)
══════════════════════════════════════════════ */

const CACHE_NAME = 'vem-v2';
const ASSETS = [
    '/',
    '/manifest.json'
];

// ── Install: Cache core assets ──
self.addEventListener('install', function(event) {
    console.log('🔧 SW: Instalando cache v2...');
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

// ── Activate: Clean old caches ──
self.addEventListener('activate', function(event) {
    console.log('✅ SW: Ativado');
    event.waitUntil(
        caches.keys().then(function(names) {
            return Promise.all(
                names.filter(function(n) { return n !== CACHE_NAME; })
                     .map(function(n) { return caches.delete(n); })
            );
        })
    );
    self.clients.claim();
});

// ── Fetch ──
self.addEventListener('fetch', function(event) {
    const url = new URL(event.request.url);

    // API e requisições que não são GET: sem interceptação.
    // Sem rede, o fetch falha na própria página e o motorista enfileira o check-in offline.
    if (event.request.method !== 'GET' || url.pathname.startsWith('/api/')) {
        return;
    }

    // Páginas e arquivos: rede primeiro (sempre a versão mais nova); sem conexão, usa o cache
    event.respondWith(
        fetch(event.request).then(function(response) {
            if (response.ok) {
                var clone = response.clone();
                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(event.request, clone);
                });
            }
            return response;
        }).catch(function() {
            return caches.match(event.request);
        })
    );
});
