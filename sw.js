const CACHE = "igna-djongo-v4";
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

// Notifications envoyées par mmbt.fr (annonce, collecte, paiement confirmé).
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) { d = {texte: e.data ? e.data.text() : ""}; }
  e.waitUntil(self.registration.showNotification(d.titre || "Igna Djongo", {body: d.texte || "", icon: "icon-192.png", badge: "icon-192.png", data: {url: d.url || "./"}}));
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({type: "window", includeUncontrolled: true}).then(l => l.length ? l[0].focus() : self.clients.openWindow((e.notification.data && e.notification.data.url) || "./")));
});
