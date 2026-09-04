# 小小任務家 v3.3.1 — 階段一發布包

這個資料夾就是**完整可上線的網站**。整包丟到任何 HTTPS 靜態空間即可，不需要後端、不需要建置步驟。

```
kidquest-pwa/
├─ index.html            ← 主程式（HTML + CSS + App 邏輯）
├─ zhuyin-data.js        ← 注音字典（約 92KB，獨立檔以利快取）
├─ manifest.webmanifest  ← App 名稱、圖示、啟動方式
├─ sw.js                 ← Service Worker（離線快取）
└─ icons/                ← 192 / 512 / apple-touch / favicon
```

---

## 一、上線（三選一，都免費）

> ⚠️ **一定要 HTTPS**。Service Worker 在 `http://`（localhost 除外）與 `file://` 下不會啟用，也就沒有離線與「加到主畫面」。

### A. Cloudflare Pages（最快，不用 git）
1. 開 <https://dash.cloudflare.com> → **Workers & Pages** → **Create** → **Pages** → **Upload assets**
2. 專案取名（例如 `kidquest`），把 **`kidquest-pwa` 資料夾整個拖進去**
3. Deploy → 得到 `https://kidquest.pages.dev`

### B. Netlify Drop（最快，連帳號都可先不用）
1. 開 <https://app.netlify.com/drop>
2. 把 `kidquest-pwa` 資料夾拖進去 → 立刻得到 `https://xxxx.netlify.app`
3. 想固定網址再註冊帳號認領這個站

### C. GitHub Pages（想用 git 版控就選這個）
```bash
cd "kidquest-pwa"
git init && git add . && git commit -m "小小任務家 v3.3.1 PWA"
git branch -M main
git remote add origin https://github.com/<你的帳號>/kidquest.git
git push -u origin main
```
接著到 repo → **Settings → Pages** → Source 選 `main` / `/ (root)` → 存檔，
約一分鐘後得到 `https://<你的帳號>.github.io/kidquest/`。

---

## 二、給家長的安裝方式

| 裝置 | 步驟 |
|---|---|
| **Android / Chrome** | 開網址 → 進「家長模式 → 設定」按 **立即安裝**（或瀏覽器選單「安裝應用程式」） |
| **iPhone / iPad** | **必須用 Safari** 開網址 → 下方「分享」→ **加入主畫面** |
| **電腦 Chrome/Edge** | 網址列右側的安裝圖示 |

裝完會有獨立圖示、全螢幕、無網路也能開。

---

## 三、資料在哪裡、怎麼不弄丟

- 資料存在**每台裝置自己的瀏覽器**（`localStorage`，key = `kidquest_v2`）。一個家庭一份，互不干擾，但**不會跨裝置同步**。
- App 啟動時會自動申請 `navigator.storage.persist()`，降低被瀏覽器清掉的機率（Android/Chrome 有效，**iOS 會忽略**）。
- **iOS Safari 若連續 7 天沒開，可能清掉資料** —— 所以「設定 → 資料備份 → 下載備份」是目前唯一保險，建議每月做一次。
- 還原備份會**覆蓋這台裝置的全部資料**，操作前會先跳確認。
- 備份檔就是完整的 state JSON，也可以在不同裝置間手動搬移（等於土法煉鋼版的同步）。

---

## 四、之後要改版怎麼發布

1. 改 `index.html`（或 `zhuyin-data.js`）
2. **把 `sw.js` 裡的 `CACHE = "kidquest-v3.3.1"` 版本號往上加**（例如 `v3.3.2`）
3. 重新上傳整包

沒有改版本號的話，因為是 cache-first，使用者會一直看到舊版。
改了之後，使用者**開兩次**才會完全切到新版（第一次背景更新、第二次生效）。

---

## 五、這一版做了什麼（對照原檢查清單階段一）

| 項目 | 狀態 |
|---|---|
| manifest.json | ✅ `manifest.webmanifest`，含 192/512 的 any + maskable |
| Service Worker（cache-first、離線） | ✅ `sw.js`，含導覽離線 fallback |
| HTTPS 靜態託管 | ⬜ 需你選一家（上方三選一） |
| iOS 專用 meta | ✅ `apple-mobile-web-app-capable` / `apple-touch-icon` / `viewport-fit=cover` + 安全區 padding |
| 移除自動 seedDemo | ✅ 第一次開啟是乾淨初始設定；範例資料改成設定頁的「先載入範例資料試玩」按鈕 |
| 匯出 / 匯入備份 | ✅ 設定頁「資料備份」，下載 `小小任務家-備份-YYYY-MM-DD.json` |
| `navigator.storage.persist()` | ✅ 啟動時申請，設定頁顯示目前狀態與資料量 |
| 頭像壓縮 | ✅ 置中裁正方形 → 最長邊 256px → JPEG q0.8（約 10～20KB） |
| 注音字典拆檔 | ✅ `zhuyin-data.js`，改版時不必重載 92KB |

**未涵蓋（屬階段二，需後端）**：跨裝置同步、多家庭帳號、PIN 雜湊儲存、頭像存雲端。
