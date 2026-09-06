# -*- coding: utf-8 -*-
"""
由 kidquest-pwa/index.html 生成「單檔版」HTML。

單檔版＝雙擊即可用（file://），不需要伺服器、不需要網路。
與 PWA 版的差異全部在這裡自動處理，兩邊共用同一份程式碼，不必手動同步：
  1. 注音字典直接內嵌（原本是 <script src="zhuyin-data.js">）
  2. 使用手冊的截圖內嵌成 data URI（填入 IMG 對照表）
  3. 移除 manifest / icon 的 <link>（單檔版沒有那些檔案）
  4. 關閉「安裝到主畫面」卡片（file:// 沒有安裝流程）
  5. 版本號標示為「單檔版」，方便分辨手上開的是哪一版

輸出檔名依 index.html 的 APP_VER 自動決定，例如 3.5.0 → ../小小任務家-集點AppDemo-v3.5.html

用法：python build-standalone.py
"""
import base64, io, json, os, re

SRC_HTML = "index.html"
SRC_ZY = "zhuyin-data.js"
IMGDIR = "images"

html = io.open(SRC_HTML, encoding="utf-8").read()
zy = io.open(SRC_ZY, encoding="utf-8").read()

ver_m = re.search(r'const APP_VER = "([\d.]+)";', html)
assert ver_m, "index.html 找不到 APP_VER"
VER = ver_m.group(1)
OUT = os.path.join("..", "小小任務家-集點AppDemo-v%s.html" % ".".join(VER.split(".")[:2]))


def sub(text, old, new, label):
    assert old in text, "找不到片段：" + label
    return text.replace(old, new, 1)


# 1. 移除 PWA 專屬的外部資源連結
for tag, label in [
    ('<link rel="manifest" href="manifest.webmanifest">\n', "manifest"),
    ('<link rel="icon" href="icons/favicon-32.png" sizes="32x32" type="image/png">\n', "favicon"),
    ('<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n', "apple-touch-icon"),
]:
    html = sub(html, tag, "", label)

# 2. 內嵌注音字典
html = sub(html, '<script src="zhuyin-data.js"></script>',
           "<script>\n" + zy.rstrip("\n") + "\n</script>", "zhuyin script tag")

# 3. 內嵌手冊截圖 → 填入 IMG 對照表（SHOT() 會優先使用它）
MIME = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
imgs = {}
if os.path.isdir(IMGDIR):
    for fn in sorted(os.listdir(IMGDIR)):
        ext = fn.rsplit(".", 1)[-1].lower()
        if ext not in MIME:
            continue
        raw = io.open(os.path.join(IMGDIR, fn), "rb").read()
        imgs[fn] = "data:%s;base64,%s" % (MIME[ext], base64.b64encode(raw).decode())
html = sub(html, "const IMG = {};",
           "const IMG = " + json.dumps(imgs, ensure_ascii=False, separators=(",", ":")) + ";",
           "IMG map")

# 4. 單檔版沒有安裝流程 → isStandalone() 恆真，設定頁的安裝卡片自動隱藏
html = sub(html,
           'const isStandalone = () => window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;',
           'const isStandalone = () => true;   /* 單檔版：沒有安裝流程，安裝卡片一律隱藏 */',
           "isStandalone")

# 5. 版本號加註，避免和 PWA 版搞混
html = sub(html, ver_m.group(0), 'const APP_VER = "%s 單檔版";' % VER, "APP_VER")

# 6. 檔頭註記
html = sub(html, "<!DOCTYPE html>",
           "<!DOCTYPE html>\n<!-- 小小任務家 v%s 單檔版 — 由 kidquest-pwa/build-standalone.py 自動生成，請勿直接編輯。\n"
           "     要改功能請改 kidquest-pwa/index.html 後重新執行生成腳本。 -->" % VER,
           "header comment")

io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)

# 驗證：HTML 標籤中不應殘留任何外部資源
ext_refs = [m for m in re.findall(r'<(?:script|link|img)[^>]*(?:src|href)="([^"]+)"', html)
            if not m.startswith(("data:", "#", "${"))]
print("已生成 %s（%.0f KB）" % (OUT, os.path.getsize(OUT) / 1024))
print("內嵌截圖：%d 張" % len(imgs))
print("外部資源參照：%s" % (ext_refs if ext_refs else "無（完全自足）"))
