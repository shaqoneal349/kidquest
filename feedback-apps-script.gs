/**
 * 小小任務家 — 意見回饋收集端點
 *
 * 把 App 送來的回饋寫進 Google 試算表，資料完全在你自己的 Google 帳號裡，
 * 不經過任何第三方服務，也不用架伺服器、不用花錢。
 *
 * ── 設定步驟（約 5 分鐘）─────────────────────────────
 * 1. 開一份新的 Google 試算表，取名例如「小小任務家 意見回饋」。
 *    從網址列複製試算表 ID：
 *    https://docs.google.com/spreadsheets/d/【這一段就是 ID】/edit
 * 2. 在試算表點「擴充功能 → Apps Script」。
 * 3. 把這整個檔案的內容貼進去，覆蓋原本的 myFunction。
 * 4. 填入下面的 SHEET_ID（想收通知信的話再填 NOTIFY_EMAIL）。
 * 5. 右上角「部署 → 新增部署作業」：
 *      類型：網頁應用程式
 *      執行身分：我
 *      誰可以存取：★ 所有人 ★（一定要選這個，App 才送得進來）
 *    按「部署」→ 授權存取 → 複製那串以 /exec 結尾的網址。
 * 6. 把網址貼到 kidquest-pwa/index.html 的 FEEDBACK_URL，
 *    把 sw.js 的 CACHE 版本號 +1，然後 git push。
 *
 * ── 之後要改這支程式 ─────────────────────────────
 * 改完一定要「部署 → 管理部署作業 → 編輯 → 版本選『新版本』」再部署，
 * 否則線上跑的還是舊版。網址不會變。
 */

const SHEET_ID = '貼上你的試算表 ID';
const NOTIFY_EMAIL = '';   // 想在有新回饋時收信就填你的 Email，留空則不寄信

const HEADERS = ['收到時間', '類型', '內容', '聯絡方式', 'App 版本', '小孩數', '已安裝', '裝置'];

function doPost(e) {
  try {
    const p = (e && e.parameter) || {};
    const text = String(p.text || '').trim();
    if (!text) return json({ ok: false, error: 'empty' });

    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
      sheet.setColumnWidth(3, 420);          // 內容欄寬一點才好讀
    }
    sheet.appendRow([
      new Date(),
      p.type || '',
      text.slice(0, 1000),
      p.contact || '',
      p.ver || '',
      p.kids || '',
      p.standalone === '1' ? '是' : '否',
      String(p.ua || '').slice(0, 180),
    ]);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: '[小小任務家] 新回饋：' + (p.type || '其他'),
        body: text + '\n\n聯絡方式：' + (p.contact || '（未留）') +
              '\nApp 版本：' + (p.ver || '') + '　小孩數：' + (p.kids || ''),
      });
    }
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// 直接用瀏覽器打開 /exec 網址時會看到這行，用來確認部署成功
function doGet() {
  return ContentService.createTextOutput('kidquest feedback endpoint is running');
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
