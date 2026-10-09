# -*- coding: utf-8 -*-
"""Europe PMC API retrieval: ELMs / bioprinting / live biotherapeutics / engineered probiotics
Date window: 2026-09-09 .. 2026-10-09 (past month relative to run date 2026-10-09)
"""
import json, time, urllib.request, urllib.parse, ssl, os

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DATE = "2026-09-09 TO 2026-10-09"

QUERIES = {
    "ELM": f'(TITLE_ABS:"engineered living material*" OR TITLE_ABS:"living materials" OR TITLE_ABS:"engineered living material") AND (FIRST_PDATE:[{DATE}])',
    "Bioprinting": f'(TITLE_ABS:"bioprint*" OR TITLE_ABS:"3D print*" OR TITLE_ABS:"bioink" OR TITLE_ABS:"bio-ink" OR TITLE_ABS:"extrusion printing") AND (TITLE_ABS:cell* OR TITLE_ABS:bioink OR TITLE_ABS:tissue OR TITLE_ABS:hydrogel) AND (FIRST_PDATE:[{DATE}])',
    "LBP": f'(TITLE_ABS:"live biotherapeutic*" OR TITLE_ABS:"live bacterial therapeut*" OR TITLE_ABS:"microbial therapeut*" OR TITLE_ABS:"cell-based therap*" OR TITLE_ABS:"bacterial therap*") AND (FIRST_PDATE:[{DATE}])',
    "Probiotics": f'(TITLE_ABS:"engineered probiotic*" OR TITLE_ABS:"programmed bacteria" OR TITLE_ABS:"synthetic probiotic*" OR TITLE_ABS:"engineered bacteria" OR TITLE_ABS:"chassis organism" OR TITLE_ABS:"bacterial circuit") AND (TITLE_ABS:gut OR TITLE_ABS:therapeut* OR TITLE_ABS:probiotic* OR TITLE_ABS:microbiome OR TITLE_ABS:tumor OR TITLE_ABS:disease) AND (FIRST_PDATE:[{DATE}])',
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(q, cursor="*"):
    params = {
        "query": q,
        "format": "json",
        "pageSize": "100",
        "resultType": "core",
        "cursorMark": cursor,
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-literature-agent)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("retry", attempt, e)
            time.sleep(3)
    return None

all_results = {}
for name, q in QUERIES.items():
    print(f"=== {name} ===")
    cursor = "*"
    items = []
    for page in range(5):
        data = fetch(q, cursor)
        if not data:
            break
        res = data.get("resultList", {}).get("result", [])
        items.extend(res)
        print(f"  page {page}: {len(res)} hits (total claimed {data.get('hitCount')})")
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor or not res:
            break
        cursor = nxt
        time.sleep(1.5)
    all_results[name] = items
    time.sleep(1.5)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "epmc_raw.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=1)
print("saved", out)
for name, items in all_results.items():
    print(name, len(items))
