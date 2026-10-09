# -*- coding: utf-8 -*-
"""2025 Web 补漏（双保险）：5 条入 kept（4 条 2025 批 + 1 条 2023 批回补）。
- all-db 已有记录直接复制（含 elm_fetch_by_doi 预抓的 Nat Rev Mater）
- EPMC 未收录者按 Crossref/出版页元数据手工构造
全部设期刊组与体裁。幂等。"""
import json, pathlib

base = pathlib.Path(__file__).resolve().parent.parent
kept_p = base / "literature_database.json"
all_p = base / "literature_database_all.json"

kept = json.loads(kept_p.read_text(encoding="utf-8"))
all_db = json.loads(all_p.read_text(encoding="utf-8"))

# DOI -> (journal_group, add_review, note)
GAP = {
    "10.1038/s41578-024-00766-y": ("A-Nature家族", True,
        "Nat Rev Mater《Delivering living medicines with biomaterials》综述，Web 双保险补漏（EPMC 检索 miss），2025-01-27 归 2025 批综述节"),
    "10.1016/j.mattod.2025.03.021": ("F-用户补充", False,
        "Materials Today 主刊《high cell-density bioinks》研究论文，白名单补键前漏检，2025-05-16 归 2025 批研究节"),
    "10.1016/j.mattod.2023.05.030": ("F-用户补充", True,
        "Materials Today 主刊《3D Printed Materials for Combating Antimicrobial Resistance》综述，白名单补键前漏检，2023-06-19 回补归 2023 批综述节"),
    "10.1038/s44222-025-00370-x": ("A-Nature家族", True,
        "Nat Rev Bioeng《Bioengineering a live biotherapeutic product from bench to business》评论/综述，EPMC 未收录经 Crossref/出版页补录，2025-10-02 归 2025 批综述节"),
    "10.1016/j.mattod.2025.08.015": ("F-用户补充", True,
        "Materials Today 主刊《Integrating life into material design for living materials 4.0》前瞻综述（LM 1.0-4.0 代际框架），EPMC 未收录经 Crossref/出版页补录，2025-09-06 归 2025 批综述节"),
}

# EPMC 未收录条目的手工构造记录
MANUAL = {
    "10.1038/s44222-025-00370-x": {
        "source": "WebGap-2025", "id": "WebGap-2025-NRB-00370",
        "doi": "10.1038/s44222-025-00370-x", "pmid": None, "pmcid": None,
        "title": "Bioengineering a live biotherapeutic product from bench to business.",
        "journal": "Nature Reviews Bioengineering", "journal_abbrev": "Nat Rev Bioeng",
        "date": "2025-10-02", "authors": [], "corresponding_author": None,
        "abstract": "Translational account of bioengineering Escherichia coli Nissle into a live therapeutic product: from bench science through spin-off company creation to business development. (Abstract reconstructed from publisher/Crossref metadata; record not indexed in Europe PMC as of 2026-10-09.)",
        "pubtypes": ["Review", "Journal Article"],
        "is_oa": None, "pdf_url": None, "pdf_downloaded": False,
        "pdf_file": None, "pdf_manual": False, "topics": ["LBP"],
    },
    "10.1016/j.mattod.2025.08.015": {
        "source": "WebGap-2025", "id": "WebGap-2025-MT-08015",
        "doi": "10.1016/j.mattod.2025.08.015", "pmid": None, "pmcid": None,
        "title": "Integrating life into material design for living materials 4.0: Navigating challenges and future trajectories from static to dynamic evolution.",
        "journal": "Materials Today", "journal_abbrev": "Mater Today",
        "date": "2025-09-06", "authors": [], "corresponding_author": None,
        "abstract": "Perspective review proposing a four-generation classification of living materials (LM 1.0 traditional fermented products to LM 4.0 AI-feedback smart biohybrid systems), surveying cell-matrix interactions and signaling dynamics with application blueprints in optics, energy storage and beyond. (Abstract reconstructed from publisher/media metadata; record not indexed in Europe PMC as of 2026-10-09.)",
        "pubtypes": ["Review", "Journal Article"],
        "is_oa": None, "pdf_url": None, "pdf_downloaded": False,
        "pdf_file": None, "pdf_manual": False, "topics": ["ELM"],
    },
}

have = {(r.get("doi") or "").lower() for r in kept}
idx = {(r.get("doi") or "").lower(): r for r in all_db}
n = 0
for doi, (grp, add_rev, note) in GAP.items():
    if doi in have:
        continue
    r = idx.get(doi)
    if not r:
        r = MANUAL.get(doi)
        if not r:
            print("MISSING in all-db and no manual record:", doi)
            continue
        r = dict(r)  # copy
    r["journal_group"] = grp
    r["source"] = r.get("source") or "WebGap-2025"
    if add_rev:
        pts = r.get("pubtypes") or []
        if not any("review" in p.lower() for p in pts):
            pts.append("Review")
        r["pubtypes"] = pts
    r["note"] = note
    kept.append(r)
    n += 1
kept_p.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"copied {n} gap records into kept -> {len(kept)}")
