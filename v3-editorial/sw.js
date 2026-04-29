// Service worker minimalista — cache "stale-while-revalidate" para shell estático.
// NÃO faz cache de /api/* (sempre rede) — o site precisa de dados frescos pra leads.
const CACHE_NAME = "pv-shell-v3";
const SHELL_URLS = [
  "./",
  "./index.html",
  "../shared/data.jsx",
  "../shared/BuscaNatural.jsx?v=20260429-integracao-front",
  "../shared/PropertyGrid.jsx?v=20260429-integracao-front",
  "../shared/AIChat.jsx?v=20260429-integracao-front",
  "../shared/AvaliacaoImovel.jsx?v=20260429-fix-front",
  "../shared/PaginasDetalhe.jsx?v=20260429-fix-front",
  "./app.jsx?v=20260429-integracao-front",
  "../assets/colors_and_type.css",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_URLS).catch(() => null))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Nunca cachear API / POST / cross-origin (deixa rede direta)
  if (req.method !== "GET") return;
  if (url.pathname.startsWith("/api/")) return;
  if (url.origin !== self.location.origin) return;

  // Stale-while-revalidate
  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cached = await cache.match(req);
      const network = fetch(req)
        .then((resp) => {
          if (resp && resp.status === 200) cache.put(req, resp.clone());
          return resp;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
