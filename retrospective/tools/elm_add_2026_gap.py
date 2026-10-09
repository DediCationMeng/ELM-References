# -*- coding: utf-8 -*-
"""2026 批 Web 补漏：把 all-db 中经 DOI 直查补录的记录拷入 kept（幂等）。

补漏 7 条（Nature 系 2026 漏检经 Web 双保险捕获；npj 系列按白名单规则不收）：
  10.1038/s44221-026-00664-3  Nature Water 菌丝活体生物覆盖材料（研究）
  10.1038/s43018-026-01171-w  Nature Cancer 细菌工程抗癌 Perspective（综述/观点）
  10.1038/s41579-026-01325-8  Nat Rev Microbiol 评植入材料封装细菌（观点）
  10.1038/s41587-026-03183-4  Nat Biotechnol 评 Science 坚韧支架细菌治疗（观点）
  10.1038/s41579-026-01311-0  Nat Rev Microbiol 下一代益生菌综述（综述）
"""
import argparse, json, pathlib

GAP = {
    # DOI: (journal_group, add_review, note)
    "10.1038/s44221-026-00664-3": ("A-Nature家族", False, "Nature Water 菌丝活体生物覆盖材料（大气水收集），Web 补漏补入"),
    "10.1038/s43018-026-01171-w": ("A-Nature家族", True, "Nature Cancer 细菌工程抗癌 Perspective，人工归类入综述/观点节（Web 补漏补入）"),
    "10.1038/s41579-026-01325-8": ("A-Nature家族", True, "Nat Rev Microbiol 评论（评 Science 植入式活体材料封装细菌），人工归类入综述/观点节（Web 补漏补入）"),
    "10.1038/s41587-026-03183-4": ("A-Nature家族", True, "Nat Biotechnol 研究评述（评 Science 坚韧支架细菌治疗），人工归类入综述/观点节（Web 补漏补入）"),
    "10.1038/s41579-026-01311-0": ("A-Nature家族", True, "Nat Rev Microbiol 下一代益生菌综述，人工归类入综述节（Web 补漏补入）"),
    "10.1038/s41893-026-01921-9": ("A-Nature家族", False, "Nature Sustainability 3D 打印 ELM 厌氧氨氧化-反硝化耦合脱氮（环境 ELM），Web 补漏补入"),
    "10.1038/s44222-026-00416-8": ("A-Nature家族", True, "Nat Rev Bioeng 生物杂化微机器人生物物理设计综述，人工归类入综述节（Web 补漏补入）"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(pathlib.Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    base = pathlib.Path(args.dir)
    all_recs = json.loads((base / "literature_database_all.json").read_text(encoding="utf-8"))
    kept_path = base / "literature_database.json"
    kept = json.loads(kept_path.read_text(encoding="utf-8"))
    have = {(r.get("doi") or "").lower() for r in kept}

    idx = {(r.get("doi") or "").lower(): r for r in all_recs}
    added = 0
    for doi, (grp, rev, note) in GAP.items():
        if doi in have:
            continue
        rec = idx.get(doi)
        if not rec:
            print(f"!! not in all-db: {doi}")
            continue
        rec["journal_group"] = grp
        if rev:
            pts = rec.get("pubtypes") or []
            if not any("review" in p.lower() for p in pts):
                pts.append("Review")
            rec["pubtypes"] = pts
        rec["note"] = note
        kept.append(rec)
        added += 1
    kept_path.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"copied {added} gap records into kept -> {len(kept)}")


if __name__ == "__main__":
    main()
