#!/usr/bin/env python3
"""Extract candidate snippet blocks from a live page and score the first 160 chars.
Usage: python extract_blocks.py <url> [--brand YourBrand] [--json]
Scores are heuristic (0/1 per criterion); criterion 5 (keyword) needs --kw terms.
"""
import sys, re, html, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

def fetch(url):
    req = urllib.request.Request(url + ("&" if "?" in url else "?") + "cb=snip", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

def blocks(src):
    src = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", "", src)
    out, seen = [], set()
    for m in re.finditer(r"(?is)<(h1|h2|h3|p|li|summary|strong|b)\b[^>]*>(.*?)</\1>", src):
        inner = m.group(2)
        # glued bold lead-in: <strong>X</strong>Y with no space/punct
        glued = bool(re.search(r"(?i)</(strong|b)>[A-Za-z]", inner))
        t = html.unescape(re.sub(r"<[^>]+>", " ", inner))
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 15 or t in seen: continue
        seen.add(t)
        out.append({"tag": m.group(1), "text": t, "glued": glued})
    return out

PERS = re.compile(r"\b(je|jouw|jij|u|uw|you|your|sie|ihr|ihre|dein|deine)\b", re.I)
USP = re.compile(r"(\d|€|zonder|without|ohne|sem |gratis|free|kostenlos|mediaan|median|direct|sofort|instantly|in één|in one|in einem)", re.I)

def score(b, brand, kws):
    t = b["text"]; head = t[:160]
    full_sentence = len(t) <= 160 or bool(re.search(r"[.!?:]", head)) and head.rstrip()[-1:] in ".!?:" or len(t) <= 160
    # sentence ends within window?
    ends = len(t) <= 160 or bool(re.search(r"[.!?]\s", head)) or b["tag"] in ("h1", "h2", "h3")
    s = {
        "1_volledige_zin": int(ends and not b["glued"]),
        "2_usp_concreet": int(bool(USP.search(head))),
        "3_merk": int(brand.lower() in head.lower()),
        "4_aanspreking": int(bool(PERS.search(head))),
        "5_keyword": int(any(k.lower() in head.lower() for k in kws)) if kws else None,
        "6_structuur": int(b["tag"] in ("h1","h2","h3","li","summary","strong","b")),
        "7_kern_voor_160": int(len(t) <= 160 or ends),
    }
    s["total"] = sum(v for v in s.values() if v)
    return s

if __name__ == "__main__":
    a = sys.argv[1:]
    url = a[0]
    brand = a[a.index("--brand")+1] if "--brand" in a else "YourBrand"
    kws = a[a.index("--kw")+1].split(",") if "--kw" in a else []
    rows = []
    for b in blocks(fetch(url)):
        b["score"] = score(b, brand, kws); b["head"] = b["text"][:160]; rows.append(b)
    if "--json" in a:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for b in rows:
            sc = b["score"]
            flag = " GLUED" if b["glued"] else ""
            print(f"[{b['tag']}] {sc['total']}/7{flag} | {b['head']}")
