# 小小任務家 v3.5.1 — 階段一發布包

> 🟢 **已上線**：https://shaqoneal349.github.io/kidquest/
> 📦 **原始碼**：https://github.com/shaqoneal349/kidquest（public，GitHub Pages 由 `main` / root 自動發布）
> 傳這個網址給家長，手機開啟後即可「加到主畫面」，離線也能用。

這個資料夾就是**完整可上線的網站**。整包丟到任何 HTTPS 靜態空間即可，不需要後端、不需要建置步驟。

```
kidquest-pwa/
├─ index.html            ← 主程式（HTML + CSS + App 邏輯）＝唯一的程式碼來源
├─ zhuyin-data.js        ← 注音字典（約 92KB，獨立檔以利快取）
├─ manifest.webmanifest  ← App 名稱、圖示、啟動方式
├─ sw.js                 ← Service Worker（離線快取）
├─ icons/                ← 192 / 512 / apple-touch / favicon
└─ images/               ← 使用手冊的 10 張畫面截圖（WebP，約 194KB）

build-zhuyin.py         ← 由教育部辭典重建注音字典
build-standalone.py     ← 由 index.html 生成「單檔版」，輸出檔名依版本自動決定
shoot.py（在 scratchpad）← 用無頭 Chrome 重拍手冊截圖
feedback-apps-script.gs ← 意見回饋收集端點（貼到 Google Apps Script）
```

> **單檔版**：雙擊即可用、不需伺服器與網路，適合傳給不想裝東西的人。
> 它由 `index.html` 自動生成（內嵌注音字典、移除 manifest/icon 連結、關閉安裝卡片），
> **不要直接編輯單檔版**——改功能請改 `index.html` 後執行 `python build-standalone.py`。

---

## 一、上線 ✅ 已完成（GitHub Pages）

已經用 GitHub CLI 建好 public repo 並開啟 Pages，站台在 https://shaqoneal349.github.io/kidquest/。
**之後改版只要 `git push`，GitHub 會自動重新發布**（約 1 分鐘）：

```bash
git add -A
git commit -m "說明改了什麼"
git push
```

<details>
<summary>備援：想換去 Cloudflare Pages / Netlify 的話</summary>

### 備援選項（三選一，都免費）

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


</details>

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
2. **把 `sw.js` 裡的 `CACHE = "kidquest-v3.5.1"` 版本號往上加**（例如 `v3.3.2`）
3. `git add -A && git commit -m "..." && git push`（GitHub Pages 約 1 分鐘後自動更新）

沒有改版本號的話，因為是 cache-first，使用者會一直看到舊版。
改了之後，使用者**開兩次**才會完全切到新版（第一次背景更新、第二次生效）。

---

## 五、這一版做了什麼（對照原檢查清單階段一）

| 項目 | 狀態 |
|---|---|
| manifest.json | ✅ `manifest.webmanifest`，含 192/512 的 any + maskable |
| Service Worker（cache-first、離線） | ✅ `sw.js`，含導覽離線 fallback |
| HTTPS 靜態託管 | ✅ GitHub Pages：https://shaqoneal349.github.io/kidquest/ |
| iOS 專用 meta | ✅ `apple-mobile-web-app-capable` / `apple-touch-icon` / `viewport-fit=cover` + 安全區 padding |
| 移除自動 seedDemo | ✅ 第一次開啟是乾淨初始設定；範例資料改成設定頁的「先載入範例資料試玩」按鈕 |
| 匯出 / 匯入備份 | ✅ 設定頁「資料備份」，下載 `小小任務家-備份-YYYY-MM-DD.json` |
| `navigator.storage.persist()` | ✅ 啟動時申請，設定頁顯示目前狀態與資料量 |
| 頭像壓縮 | ✅ 置中裁正方形 → 最長邊 256px → JPEG q0.8（約 10～20KB） |
| 注音字典拆檔 | ✅ `zhuyin-data.js`，改版時不必重載 |
| 注音正確性 | ✅ v3.4.0 全面改用教育部《重編國語辭典修訂本》重建（見下方第六節） |

**未涵蓋（屬階段二，需後端）**：跨裝置同步、多家庭帳號、PIN 雜湊儲存、頭像存雲端。

---

## 六、注音資料來源與已知限制（v3.4.0）

原本的字典是從大陸拼音表轉來的，「垃圾」讀成 ㄌㄚ ㄐㄧ。v3.4.0 全面依 **教育部《重編國語辭典修訂本》**（取自 [g0v/moedict-data](https://github.com/g0v/moedict-data)，CC BY-ND 3.0 TW）重建。

**做法**
1. 詞條讀音取「現代義（無古籍引文）釋義數最多」的那個讀音——避免選到罕用古義。例如「運動」辭典第一個讀音是「奔走鑽營」義的 ㄩㄣˋ ㄉㄨㄥ˙，體育義的 ㄩㄣˋ ㄉㄨㄥˋ 排在第二。
2. 字級 `ZY_CHAR` 保守修正：**只在現行讀音不屬於教育部任一合法讀音時才替換**（共 173 字），不動多音字原本正確的常用選擇。
3. 詞級 `ZY_PHRASE` 收錄 16,332 個「逐字拼會拼錯」的詞，比對時長詞優先，多音字在上下文中自動正確。
4. 11 條人工覆蓋，修正自動化抓不到的情形（異體字資料假象「台／臺」「唇／脣」、辭典選到古義的「早起」、非辭典詞「彈鋼琴」「量體溫」等）。

**已知限制**
- **未實作「一／不」變調**：教育部辭典本身不在注音欄標變調，為與來源一致故未加。因此「一支」顯示 ㄧ ㄓ，課本寫法是 ㄧˋ ㄓ。要改成課本式變調可以做，但得處理「第一」「一月」「星期一」等不變調的例外。
- 5,401 字中有 29 字教育部查無資料（多為罕用異體字），保留原值。
- 逐字校對 5,401 字不可行；保證的是**91 條驗證電池**（全部預設任務／獎品 + 常見家事與獎品用語）逐條人工確認正確。若發現漏網之魚，在 `build_zy2.py` 的 `PHRASE_FIX` 加一行即可。

---

## 七、意見回饋要怎麼串（重要）

✅ **已接上**（v3.5.1）。回饋會寫進 Google 試算表「小小任務家問題回饋」。
入口：**家長模式 → 設定 → 我有話想說**，以及使用手冊最下方。

### 為什麼選 Google Apps Script

比較過幾種做法：

| 做法 | 使用者體驗 | 你的成本 | 缺點 |
|---|---|---|---|
| **Apps Script → 試算表**（建議） | 在 App 內填完就送出，不用離開 | 免費、5 分鐘設定 | 要部署一次 |
| Google 表單連結 | 跳出 App 到瀏覽器填 | 免費、3 分鐘 | 中斷體驗，填答率較低 |
| mailto: 開信箱 | 手機上常常開不起來 | 0 | 體驗差，且要公開你的信箱 |
| Formspree / Tally 等 | 好 | 免費額度有限 | 多依賴一個外部服務 |

選 Apps Script 的關鍵理由：**資料留在你自己的 Google 帳號**、不用註冊第三方、
而且回饋直接進試算表，可以自己排序分類，要做成看板也容易。

### 設定步驟

完整說明寫在 `feedback-apps-script.gs` 的檔頭。摘要：

1. 網址列輸入 `sheets.new` 開一份新試算表
2. 擴充功能 → Apps Script → 貼上 `feedback-apps-script.gs` 全部內容（**不用填任何 ID**）
3. 部署 → 網頁應用程式 → 執行身分「我」、存取權限 **「所有人」** → 授權
4. 複製 `/exec` 網址，填進 `index.html` 的 `FEEDBACK_URL`，`sw.js` 的 `CACHE` 版本號 +1，`git push`

授權時會看到「Google 尚未驗證這個應用程式」——那是你自己寫的腳本，點「進階 → 前往專案 → 允許」即可。
授權範圍**只有試算表**，沒有信箱、沒有雲端硬碟其他檔案。

```js
const FEEDBACK_URL = "https://script.google.com/macros/s/AKfy..../exec";
```

### 防機器人

端點是公開的，任何人都能 POST。腳本裡有一組 `TOKEN`（App 端 `FEEDBACK_TOKEN` 要相同）擋掉隨機掃描的爬蟲。
**這不是密碼**——它在公開原始碼裡看得到，只是提高亂寫的門檻。真的被灌垃圾就換一組字串，兩邊同步改再重新部署。

### 會收到什麼

每筆回饋一列：時間、類型（建議／問題／其他）、內容、聯絡方式、App 版本、小孩數、是否已安裝、裝置字串。

**不會收集**小孩姓名、頭像、任務內容或任何點數紀錄——這些從頭到尾只存在使用者自己的裝置。
`小孩數` 只是個數字，用來判斷回報的人是不是多小孩使用者。

### 端點還沒設定時會怎樣

表單照常可用。按送出後內容會存進本機佇列並複製到剪貼簿，
使用者可以自己貼給你；等你設定好 `FEEDBACK_URL` 並更新版本後，**下次開啟 App 會自動補送**。
