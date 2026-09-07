# -*- coding: utf-8 -*-
"""
使用手冊截圖流水線
  1. 複製 index.html，注入「狀態驅動」腳本（依 #shot=xxx 把 App 帶到指定畫面）
  2. 本機起 http server
  3. 無頭 Chrome 以 2 倍解析度截圖
  4. 縮回 1 倍、輸出 WebP 到 kidquest-pwa/images/
"""
import io, os, re, shutil, subprocess, sys, time, http.server, socketserver, threading, functools
from PIL import Image

PWA = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "kidquest_shots_%d" % int(time.time()))
OUTDIR = os.path.join(PWA, "images")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 8823
W, H, SCALE = 470, 880, 2   # 470 是版面不被裁切的最小寬度

SHOTS = [
    "kid-today", "kid-pending", "kid-shop", "kid-history", "kid-ledger", "kid-switch",
    "parent-pin", "parent-assign", "parent-approve", "parent-adjust", "parent-rewards", "parent-settings",
]

DRIVER = r"""
<script>
/* 截圖用狀態驅動——只在網址帶 #shot= 時作用，正式版不會載入這段 */
(function () {
  const m = /shot=([\w-]+)/.exec(location.hash);
  if (!m) return;
  const id = m[1];
  try { localStorage.clear(); } catch (e) {}
  seedDemo();
  S.introSeen = true;
  const A = S.children[0].id, B = S.children[1].id;
  const today = todayStr();
  const pick = (tid, status) => { const t = S.tasks.find(x => x.id === tid); return { ...t, tid: t.id, id: uid(), status }; };
  // 今天：一個已完成、一個等待確認、兩個待辦——三種狀態都看得到
  S.data[A].days[today] = [pick("b1", "done"), pick("b6", "pending"), pick("b3", "todo"), pick("a5", "todo")];
  S.data[A].redemptions.push({ id: uid(), name: "冰淇淋一支", icon: "🍦", pts: 25, date: today, status: "pending", claimedDate: null });
  S.data[B].days[today] = [pick("b2", "pending"), pick("b4", "todo")];
  S.activeId = A;
  save();

  const P = () => { show("parent"); renderParent(); };
  const K = v => { show("kid"); kidView = v; kidDayOff = 0; renderKid(); };
  const acts = {
    "kid-today":    () => K("today"),
    "kid-pending":  () => K("today"),
    "kid-shop":     () => K("shop"),
    "kid-history":  () => { calYM = null; histView = "cal"; K("history"); },
    "kid-ledger":   () => { histView = "log"; K("history"); },
    "kid-switch":   () => { K("today"); drawSwitch(); document.querySelector("#modal-switch").classList.remove("hidden"); },
    "parent-pin":   () => { K("today"); pinBuf = "00"; drawPin(); document.querySelector("#modal-pin").classList.remove("hidden"); },
    "parent-assign":() => { pView = "assign"; libSel = new Set(["b1", "b3"]); assignSel = new Set([todayStr(0), todayStr(1), todayStr(2)]); P(); },
    "parent-approve":() => { pView = "approve"; P(); },
    "parent-adjust":() => { pView = "adjust"; adjKind = "minus"; P(); },
    "parent-rewards":() => { pView = "rewards"; P(); },
    "parent-settings":() => { pView = "settings"; P(); },
  };
  (acts[id] || (() => {}))();

  // 部分畫面需要捲動才看得到重點
  const scroll = { "parent-rewards": 0, "parent-settings": 250, "kid-shop": 0, "kid-ledger": 0 };
  const sc = document.querySelector(id.startsWith("parent") ? "#parent .scroll" : "#kid-scroll");
  if (sc) sc.scrollTop = scroll[id] || 0;

  document.documentElement.setAttribute("data-shot", id);
})();
</script>
"""


def build_workdir():
    os.makedirs(WORK, exist_ok=True)
    for f in ["zhuyin-data.js", "manifest.webmanifest"]:
        shutil.copy(os.path.join(PWA, f), WORK)
    shutil.copytree(os.path.join(PWA, "icons"), os.path.join(WORK, "icons"))
    h = io.open(os.path.join(PWA, "index.html"), encoding="utf-8").read()
    # 截圖時關閉動畫，避免拍到動畫中間狀態
    h = h.replace("</style>", "*{animation:none!important;transition:none!important}\n</style>", 1)
    h = h.replace("</body>", DRIVER + "</body>", 1)
    io.open(os.path.join(WORK, "index.html"), "w", encoding="utf-8", newline="\n").write(h)


def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*a): pass
    handler = functools.partial(Q, directory=WORK)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def shoot(name):
    raw = os.path.join(WORK, name + ".png")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--no-first-run", "--no-default-browser-check",
           "--force-device-scale-factor=%d" % SCALE,
           "--window-size=%d,%d" % (W, H),
           "--virtual-time-budget=6000",
           "--screenshot=" + raw,
           "http://127.0.0.1:%d/#shot=%s" % (PORT, name)]
    subprocess.run(cmd, capture_output=True, timeout=90)
    if not os.path.exists(raw):
        return None
    img = Image.open(raw).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    out = os.path.join(OUTDIR, "manual-%s.webp" % name)
    img.save(out, "WEBP", quality=82, method=6)
    os.remove(raw)
    return os.path.getsize(out)


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    build_workdir()
    import logging; logging.getLogger().setLevel(logging.ERROR)
    httpd = serve()
    time.sleep(0.6)
    total = 0
    try:
        for s in SHOTS:
            size = shoot(s)
            if size is None:
                print("  FAIL %-18s" % s)
            else:
                total += size
                print("  OK   %-18s %5.1f KB" % (s, size / 1024))
    finally:
        httpd.shutdown()
    print("total %d shots, %.0f KB" % (len(SHOTS), total / 1024))
