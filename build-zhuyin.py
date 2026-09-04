# -*- coding: utf-8 -*-
"""
重建 zhuyin-data.js（第二版，修正 heteronym 取用方式）
資料來源：教育部《重編國語辭典修訂本》(g0v/moedict-data, CC BY-ND 3.0 TW)

方法：
  1. 詞條讀音 = 釋義數最多的 heteronym（平手取第一個）
     → 避免取到罕用義，例如「運動」的[0]是「奔走鑽營」ㄩㄣˋㄉㄨㄥ˙，[1]才是體育義ㄉㄨㄥˋ
  2. 字級預設 ZY_CHAR：只在「現行讀音不是教育部任一合法讀音」時才替換（保守，避免動到多音字的常用選擇）
  3. 詞級 ZY_PHRASE：逐字預設拼不出詞條讀音者才收錄
  4. 人工覆蓋：異體字資料假象（台/唇）與已驗證的誤判（便當…）
"""
import json, io, re, collections, gzip

HAN = re.compile(r"^[一-鿿]+$")
BPMF = set("ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦˊˇˋ˙")

def norm_syl(s):
    s = s.strip()
    if not s: return None
    if s.startswith("˙"): s = s[1:] + "˙"      # 輕聲統一為後綴，與現有資料一致
    return s if all(ch in BPMF for ch in s) else None

def syls(b):
    if not b: return None
    b = b.replace("　", " ").strip()
    if any(x in b for x in "（()、，"): return None
    p = [norm_syl(x) for x in b.split(" ") if x.strip()]
    return p if p and all(p) else None

d = json.load(io.open("dict-revised.json", encoding="utf-8"))
old = json.load(io.open("zy_char.json", encoding="utf-8"))
old_ph = json.load(io.open("zy_phrase.json", encoding="utf-8"))

single, words = {}, {}
for e in d:
    t, hs = e.get("title", ""), (e.get("heteronyms") or [])
    if not t or not hs or not HAN.match(t) or len(t) > 6: continue
    scored = []
    for h in hs:
        sy = syls(h.get("bopomofo"))
        if sy and len(sy) == len(t):
            defs = h.get("definitions") or []
            modern = sum(1 for x in defs if not x.get("quote"))   # 無古籍引文＝現代義
            scored.append(((modern, len(defs)), sy))
    if not scored: continue
    if len(t) == 1:
        single[t] = []
        for _, sy in scored:
            if sy[0] not in single[t]: single[t].append(sy[0])
    else:
        words[t] = max(scored, key=lambda x: x[0])[1]      # 釋義數最多者；平手取先出現的

# 字在詞中的讀音頻次（用最終選定的詞讀音統計）
cnt = collections.defaultdict(collections.Counter)
for w, sy in words.items():
    for c, s in zip(w, sy): cnt[c][s] += 1

# ---- 字級：保守修正 ----
CHAR_FIX = {"台": "ㄊㄞˊ", "唇": "ㄔㄨㄣˊ"}   # 異體字資料假象（台↔臺、唇↔脣）
new, fixed, nodata = dict(old), [], []
for c, o in old.items():
    legal = single.get(c)
    if not legal:
        nodata.append(c); continue
    if o in legal: continue
    cand = None
    for s, _ in cnt[c].most_common() if c in cnt else []:
        if s in legal: cand = s; break
    new[c] = cand or legal[0]
    fixed.append((c, o, new[c]))
for c, v in CHAR_FIX.items():
    if new.get(c) != v:
        fixed = [f for f in fixed if f[0] != c] + [(c, old.get(c, "?"), v + "（人工覆蓋）")]
        new[c] = v

# ---- 詞級 ----
PHRASE_FIX = {
    # 辭典選到古義：早起[0]是元曲的「起初」義
    "早起": ["ㄗㄠˇ", "ㄑㄧˇ"],
    "早睡早起": ["ㄗㄠˇ", "ㄕㄨㄟˋ", "ㄗㄠˇ", "ㄑㄧˇ"],
    # 東西：物品義讀輕聲（辭典兩義釋義數相同，自動選到方位義）
    "東西": ["ㄉㄨㄥ", "ㄒㄧ˙"],
    # 量：動詞測量義為 ㄌㄧㄤˊ，字級預設是名詞義 ㄌㄧㄤˋ；下列非辭典詞
    "量體溫": ["ㄌㄧㄤˊ", "ㄊㄧˇ", "ㄨㄣ"],
    "量身高": ["ㄌㄧㄤˊ", "ㄕㄣ", "ㄍㄠ"],
    "量血壓": ["ㄌㄧㄤˊ", "ㄒㄧㄝˇ", "ㄧㄚ"],
    # 非辭典詞，逐字會拼成 ㄉㄢˋ
    "彈鋼琴": ["ㄊㄢˊ", "ㄍㄤ", "ㄑㄧㄣˊ"],
    "彈吉他": ["ㄊㄢˊ", "ㄐㄧˊ", "ㄊㄚ"],
    # 異體字資料假象（台↔臺、唇↔脣）
    "台灣": ["ㄊㄞˊ", "ㄨㄢ"], "台北": ["ㄊㄞˊ", "ㄅㄟˇ"],
    "嘴唇": ["ㄗㄨㄟˇ", "ㄔㄨㄣˊ"],
}
def render(w):
    return [new[c] for c in w] if all(c in new for c in w) else None

phrase = {}
for w, sy in words.items():
    if not (2 <= len(w) <= 6) or any(c not in new for c in w): continue
    if render(w) != sy: phrase[w] = sy
phrase.update(old_ph)      # 原手工詞條優先
phrase.update(PHRASE_FIX)  # 人工覆蓋最優先

def zy_of(text, PH, CH):
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if not HAN.match(ch): i += 1; continue
        hit = None
        for L in range(min(6, len(text) - i), 1, -1):
            seg = text[i:i+L]
            if seg in PH: hit = (seg, PH[seg]); break
        if hit: out.extend(hit[1]); i += len(hit[0])
        else: out.append(CH.get(ch, "?")); i += 1
    return " ".join(out)

log = ["=== 重建報告（第二版）==="]
log.append("字級：%d 字｜修正 %d 字｜教育部查無資料 %d 字（保留原值）" % (len(new), len(fixed), len(nodata)))
log.append("詞級：%d 詞（自動 %d + 手工 %d + 人工覆蓋 %d）" % (len(phrase), len(phrase)-len(old_ph)-len(PHRASE_FIX), len(old_ph), len(PHRASE_FIX)))
log.append("長度分布：%s" % dict(sorted(collections.Counter(len(w) for w in phrase).items())))

TASKS = ["自己整理書包","早晚刷牙","寫完當天功課","收拾自己的玩具","幫忙擺碗筷","閱讀 20 分鐘","幫忙倒垃圾",
         "九點前上床睡覺","考試 90 分以上","寫一篇日記","自己洗好餐盒","運動 30 分鐘","背完一課英文單字",
         "看 30 分鐘卡通","冰淇淋一支","去公園野餐","小樂高一盒"]
CHORES = ["洗碗","掃地","拖地","倒垃圾","摺棉被","折衣服","曬衣服","收衣服","澆花","種花","餵狗","遛狗",
          "餵魚","刷牙","洗澡","洗頭","綁鞋帶","穿衣服","整理房間","鋪床","寫功課","背單字","練鋼琴",
          "彈鋼琴","拉小提琴","複習功課","早睡早起","準時起床","幫忙做家事","陪弟弟玩","照顧妹妹","量體溫",
          "吃青菜","不挑食","收玩具","說謝謝","主動打招呼","自己上廁所","看課外書","學校作業"]
REWARDS = ["看電視","玩遊戲","買玩具","去公園","吃冰淇淋","去露營","看電影","買零食","玩積木","騎腳踏車",
           "去動物園","加零用錢","晚睡半小時","選晚餐","便當","音樂課","相片","數學","快樂","得到","覺得",
           "台灣","嘴唇","蝸牛","垃圾","睡覺","運動","什麼","東西","衣服","地方","長大","重複"]
for title, arr in [("預設任務／獎品", TASKS), ("常見家事任務", CHORES), ("獎品與多音詞", REWARDS)]:
    log.append("\n=== 驗證：%s ===" % title)
    for nm in arr: log.append("%-10s → %s" % (nm, zy_of(nm, phrase, new)))

log.append("\n=== 字級修正清單（%d 字）===" % len(fixed))
for c, o, n in fixed: log.append("  %s  %s → %s" % (c, o, n))

io.open("report2.txt", "w", encoding="utf-8").write("\n".join(log))

body = ("/* 小小任務家 — 注音字典\n"
        "   資料來源：教育部《重編國語辭典修訂本》，取自 g0v/moedict-data（CC BY-ND 3.0 TW）\n"
        "   ZY_CHAR  單字預設讀音；ZY_PHRASE 詞組覆蓋（多音字在詞中的正確讀音，長詞優先比對） */\n"
        "const ZY_CHAR=" + json.dumps(new, ensure_ascii=False, separators=(",", ":")) + ";\n"
        "const ZY_PHRASE=" + json.dumps(phrase, ensure_ascii=False, separators=(",", ":")) + ";\n")
io.open("zhuyin-data.new.js", "w", encoding="utf-8", newline="\n").write(body)
raw = body.encode("utf-8")
print("chars=%d phrases=%d  raw=%.0fKB  gzip=%.0fKB" %
      (len(new), len(phrase), len(raw)/1024, len(gzip.compress(raw, 9))/1024))
