# -*- coding: utf-8 -*-
"""2024 Web 补漏 5 条从 all-db 复制入 kept（fetch 只写 all-db），并设期刊组。幂等。"""
import json, pathlib

base = pathlib.Path(__file__).resolve().parent.parent
kept_p = base / "literature_database.json"
all_p = base / "literature_database_all.json"

kept = json.loads(kept_p.read_text(encoding="utf-8"))
all_db = json.loads(all_p.read_text(encoding="utf-8"))

GAP = {
    "10.1016/j.cels.2024.02.003": "C-Cell家族",   # MELG 活体嫁接材料（研究）
    "10.1016/j.cels.2024.02.004": "C-Cell家族",   # MELG 配对评论（综述/观点）
    "10.1016/j.cels.2024.11.002": "C-Cell家族",   # 图灵基因电路图案（研究，flag）
    "10.1016/j.cels.2024.11.015": "C-Cell家族",   # 图灵图案评论（综述/观点，flag）
    "10.1038/s44222-024-00268-0": "A-Nature家族", # Nat Rev Bioeng 类器官生物打印综述
}

have = {(r.get("doi") or "").lower() for r in kept}
idx = {(r.get("doi") or "").lower(): r for r in all_db}
n = 0
for doi, grp in GAP.items():
    if doi in have:
        continue
    r = idx.get(doi)
    if not r:
        print("MISSING in all-db:", doi)
        continue
    r["journal_group"] = grp
    r["source"] = r.get("source") or "WebGap-2024"
    kept.append(r)
    n += 1
kept_p.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"copied {n} gap records into kept -> {len(kept)}")
