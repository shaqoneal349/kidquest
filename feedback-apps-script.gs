/**
 * 小小任務家 — 意見回饋收集端點
 *
 * 把 App 送來的回饋寫進 Google 試算表。資料完全在你自己的 Google 帳號裡，
 * 不經過第三方服務，不用架伺服器、不用花錢。
 *
 * ── 設定步驟（3 分鐘，只有 4 步）─────────────────────
 * 1. 開一份新的 Google 試算表（網址列輸入 sheets.new），取名例如「小小任務家 意見回饋」。
 * 2. 點「擴充功能 → Apps Script」，把這整個檔案的內容貼進去（覆蓋原本的 myFunction）。
 *    ★ 不需要填任何 ID：腳本綁在這份試算表上，會自動寫進去。
 * 3. 右上角「部署 → 新增部署作業」：
 *      類型：網頁應用程式
 *      執行身分：我
 *      誰可以存取：★ 所有人 ★（一定要選這個，App 才送得進來）
 *    按「部署」→ 授權存取。
 *    會看到「Google 尚未驗證這個應用程式」——那是因為這是你自己寫的腳本，
 *    點「進階 → 前往（專案名稱）」→「允許」即可。
 *    授權範圍只有「查看及管理你的試算表」，沒有信箱、沒有雲端硬碟其他檔案。
 * 4. 複製那串以 /exec 結尾的網址，傳給我，我會填進 App 並重新發布。
 *
 * ── 之後要改這支程式 ─────────────────────────────
 * 改完一定要「部署 → 管理部署作業 → 編輯（鉛筆）→ 版本選『新版本』」再部署，
 * 否則線上跑的還是舊版。網址不會變。
 */

/** 通行碼：擋掉隨機掃描的機器人。
 *  注意這不是密碼——它會出現在 App 的公開原始碼裡，任何人都看得到。
 *  它的作用只是讓「亂打這個網址的爬蟲」寫不進來。真的被針對就要換一組。 */
const TOKEN = 'kq-2026-fb';

/** 一般不用填。只有在腳本不是綁在試算表上（獨立專案）時，才填試算表 ID。 */
const SHEET_ID = '';

const HEADERS = ['收到時間', '類型', '內容', '聯絡方式', 'App 版本', '小孩數', '已安裝', '裝置'];
const MAX_TEXT = 1000;

function doPost(e) {
  try {
    const p = (e && e.parameter) || {};

    if (p.k !== TOKEN) return json({ ok: false, error: 'bad token' });

    const text = String(p.text || '').trim();
    if (!text) return json({ ok: false, error: 'empty' });

    getSheet().appendRow([
      new Date(),
      String(p.type || '').slice(0, 20),
      text.slice(0, MAX_TEXT),
      String(p.contact || '').slice(0, 120),
      String(p.ver || '').slice(0, 30),
      String(p.kids || '').slice(0, 5),
      p.standalone === '1' ? '是' : '否',
      String(p.ua || '').slice(0, 180),
    ]);
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

/** 用瀏覽器直接打開 /exec 網址時會看到這行，用來確認部署成功 */
function doGet() {
  return ContentService.createTextOutput('kidquest feedback endpoint is running');
}

function getSheet() {
  const ss = SHEET_ID
    ? SpreadsheetApp.openById(SHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheets()[0];
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(3, 420);   // 內容欄寬一點才好讀
  }
  return sheet;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * ── 選配：有新回饋時寄通知信給自己 ─────────────────
 * 想要的話，把下面這段的註解拿掉，並在 doPost 成功後呼叫 notify(p, text)。
 * 注意這會讓授權範圍多一項「以你的名義寄送郵件」，加完要重新部署並重新授權。
 *
 * const NOTIFY_EMAIL = '你的Email';
 * function notify(p, text) {
 *   if (!NOTIFY_EMAIL) return;
 *   MailApp.sendEmail({
 *     to: NOTIFY_EMAIL,
 *     subject: '[小小任務家] 新回饋：' + (p.type || '其他'),
 *     body: text + '\n\n聯絡方式：' + (p.contact || '（未留）') +
 *           '\nApp 版本：' + (p.ver || '') + '　小孩數：' + (p.kids || ''),
 *   });
 * }
 */
