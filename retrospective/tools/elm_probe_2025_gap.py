# -*- coding: utf-8 -*-
"""2025 批 Web 补漏探针：直查候选 DOI 是否在库，不在库则抓 EPMC 摘要供判定。"""
import json, pathlib, urllib.request, urllib.parse

base = pathlib.Path(__file__).resolve().parent.parent
all_db = json.loads((base / "literature_database_all.json").read_text(encoding="utf-8"))
dois = {(it.get("doi") or "").lower() for it in all_db}

CANDIDATES = [
    "10.1038/s41578-024-00766-y",
    "10.1038/s44222-025-00370-x",
    "10.1038/s41563-024-01958-1",
]

def epmc_search(query):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": "5", "resultType": "core"})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())

print("=== 库内存在性检查 ===")
for d in CANDIDATES:
    print(("IN-DB  " if d.lower() in dois else "MISSING"), d)

print()
print("=== EPMC 直查候选（含关键词搜索） ===")
queries = [
    'DOI:"10.1038/s41578-024-00766-y"',
    'DOI:"10.1038/s44222-025-00370-x"',
    'DOI:"10.1038/s41563-024-01958-1"',
    'TITLE:"living materials 4.0"',
    'TITLE_ABS:"nascent living" AND FIRST_PDATE:[2024-01-01 TO 2026-10-09]',
]
for q in queries:
    try:
        res = epmc_search(q)
        hits = res.get("resultList", {}).get("result", [])
        print(f"\n--- Q: {q}  ({len(hits)} hits) ---")
        for h in hits[:3]:
            doi = (h.get("doi") or "").lower()
            mark = "IN-DB" if doi in dois else "NEW"
            print(f"[{mark}] {h.get('firstPublicationDate')} | {h.get('journalTitle')} | {h.get('title','')[:100]}")
            print(f"    DOI: {h.get('doi')} | types: {h.get('pubTypeList',{}).get('pubType',[])}")
            ab = (h.get('abstractText') or '')[:500]
            print(f"    A: {ab}")
    except Exception as e:
        print(f"ERR {q}: {e}")
