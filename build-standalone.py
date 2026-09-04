# -*- coding: utf-8 -*-
"""
由 kidquest-pwa/index.html + zhuyin-data.js 生成「單檔版」HTML。

單檔版＝雙擊即可用（file://），不需要伺服器、不需要網路。
與 PWA 版的差異全部在這裡自動處理，兩邊共用同一份程式碼，不必手動同步：
  1. 注音字典直接內嵌（原本是 <script src="zhuyin-data.js">）
  2. 移除 manifest / icon 的 <link>（單檔版沒有那些檔案）
  3. 關閉「安裝到主畫面」卡片（file:// 沒有安裝流程）
  4. 版本號標示為「單檔版」，方便分辨手上開的是哪一版

用法：python build-standalone.py
"""
import io, os, re

SRC_HTML = "index.html"
SRC_ZY = "zhuyin-data.js"
OUT = os.path.join("..", "小小任務家-集點AppDemo-v3.4.html")

html = io.open(SRC_HTML, encoding="utf-8").read()
zy = io.open(SRC_ZY, encoding="utf-8").read()


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
html = sub(html,
           '<script src="zhuyin-data.js"></script>',
           "<script>\n" + zy.rstrip("\n") + "\n</script>",
           "zhuyin script tag")

# 3. 單檔版沒有安裝流程 → 讓 isStandalone() 恆真，設定頁的安裝卡片自動隱藏
html = sub(html,
           'const isStandalone = () => window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;',
           'const isStandalone = () => true;   /* 單檔版：沒有安裝流程，安裝卡片一律隱藏 */',
           "isStandalone")

# 4. 版本號加註，避免和 PWA 版搞混
html = sub(html, 'const APP_VER = "3.4.0";', 'const APP_VER = "3.4.0 單檔版";', "APP_VER")

# 5. 檔頭註記
html = sub(html, "<!DOCTYPE html>",
           "<!DOCTYPE html>\n<!-- 小小任務家 v3.4.0 單檔版 — 由 kidquest-pwa/build-standalone.py 自動生成，請勿直接編輯。\n"
           "     要改功能請改 kidquest-pwa/index.html 後重新執行生成腳本。 -->",
           "header comment")

io.open(OUT, "w", encoding="utf-8", newline="\n").write(html)

# 驗證：不應殘留任何外部資源參照
leftovers = re.findall(r'(?:src|href)="(?!data:|#)([^"]+)"', html)
print("已生成 %s（%.0f KB）" % (OUT, os.path.getsize(OUT) / 1024))
print("外部資源參照：%s" % (leftovers if leftovers else "無（完全自足）"))
