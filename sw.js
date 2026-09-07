/* 小小任務家 — Service Worker（cache-first，離線可開）
   ⚠️ 每次改 index.html / zhuyin-data.js 後，請把 CACHE 版本號 +1 再上傳，
      使用者下次開啟才會拿到新版。 */
const CACHE = "kidquest-v3.6.0";
const ASSETS = [
  "./",
  "./index.html",
  "./zhuyin-data.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
  "./images/manual-kid-history.webp",
  "./images/manual-kid-ledger.webp",
  "./images/manual-kid-pending.webp",
  "./images/manual-kid-shop.webp",
  "./images/manual-kid-switch.webp",
  "./images/manual-kid-today.webp",
  "./images/manual-parent-adjust.webp",
  "./images/manual-parent-approve.webp",
  "./images/manual-parent-assign.webp",
  "./images/manual-parent-pin.webp",
  "./images/manual-parent-rewards.webp",
  "./images/manual-parent-settings.webp",
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  let url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;   // 外部資源不攔

  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res && res.ok && res.type === "basic") {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
      }
      return res;
    }).catch(() => (req.mode === "navigate" ? caches.match("./index.html") : Response.error())))
  );
});
