const CACHE = "igna-djongo-v2";
const SHELL = ["./", "manifest.webmanifest", "icon-192.png", "icon-512.png"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, {cache: "reload"})))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// Toujours la version en ligne d'abord (pour avoir les mises à jour), la copie seulement hors connexion.
// « no-cache » : on redemande toujours au serveur s'il y a du nouveau, sans reprendre une vieille copie du navigateur.
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  const fresh = req.mode === "navigate" ? new Request(req.url, {cache: "no-cache"}) : new Request(req, {cache: "no-cache"});
  e.respondWith(fetch(fresh).then(res => {
    const copy = res.clone();
    caches.open(CACHE).then(c => c.put(req, copy));
    return res;
  }).catch(() => caches.match(req).then(r => r || caches.match("./"))));
});
