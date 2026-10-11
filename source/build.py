# Construit le site à publier à partir de app/index.html :
# ajoute l'en-tête de page complet, le manifeste et les icônes pour l'écran d'accueil.
# Usage : python3 build.py
#  - dans le dépôt (source/build.py à côté de source/app/) : écrit le site à la racine du dépôt ;
#  - dans le dossier du projet (site/build.py à côté de ../app/) : écrit le site dans site/.
import json, pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
if (HERE / "app" / "index.html").exists():
    APP, HERE = HERE / "app" / "index.html", HERE.parent
else:
    APP = HERE.parent / "app" / "index.html"
GREEN, GOLD = (14, 90, 74), (233, 185, 73)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def icon(size, pad=0.0, rounded=True):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=GREEN)
    else:
        d.rectangle([0, 0, size, size], fill=GREEN)
    inner = size * (1 - 2 * pad)
    # anneau doré (l'unité de l'igna) et initiales
    r = inner * 0.40
    c = size / 2
    w = max(2, int(inner * 0.045))
    d.ellipse([c - r, c - r, c + r, c + r], outline=GOLD, width=w)
    f = ImageFont.truetype(FONT, int(inner * 0.30))
    d.text((c, c), "ID", font=f, fill=(255, 255, 255), anchor="mm")
    return im


icon(192).save(HERE / "icon-192.png")
icon(512).save(HERE / "icon-512.png")
icon(512, pad=0.12, rounded=False).save(HERE / "icon-maskable-512.png")
icon(180, rounded=False).convert("RGB").save(HERE / "apple-touch-icon.png")

(HERE / "manifest.webmanifest").write_text(json.dumps({
    "name": "Igna Djongo",
    "short_name": "Igna Djongo",
    "lang": "fr",
    "id": "./",
    "start_url": "./",
    "description": "L'application de l'Igna Djongo : membres, cotisations, caisse et histoire. Conçue par M.M.B.T.",
    "orientation": "portrait",
    "scope": "./",
    "display": "standalone",
    "background_color": "#F1F5F2",
    "theme_color": "#0E5A4A",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}, ensure_ascii=False, indent=2))

# Petit service worker : permet l'installation comme une vraie appli et garde
# une copie de la page pour l'ouvrir même avec une connexion faible.
(HERE / "sw.js").write_text("""const CACHE = "igna-djongo-v2";
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
""")

head = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="L'application de l'Igna Djongo : membres, cotisations, caisse et histoire. Conçue par M.M.B.T.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Igna Djongo">
<meta property="og:title" content="Igna Djongo">
<meta property="og:description" content="Annonces, collectes et cotisations de l'Igna Djongo. Ouvre l'application pour voir le détail.">
<meta property="og:url" content="https://kalmache.github.io/igna-djongo/">
<meta property="og:image" content="https://kalmache.github.io/igna-djongo/icon-512.png">
<meta property="og:image:width" content="512">
<meta property="og:image:height" content="512">
<meta property="og:locale" content="fr_FR">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js", {updateViaCache: "none"}).catch(() => {});</script>
"""
body = APP.read_text()
# l'artifact n'a pas de <head>/<body> : on sépare l'en-tête (title, meta, style) du reste
cut = body.index("</style>") + len("</style>")
page = head + body[:cut] + "\n</head>\n<body>\n" + body[cut:] + "\n</body>\n</html>\n"
(HERE / "index.html").write_text(page)
print("ok", len(page))
