# -*- coding: utf-8 -*-
"""酵母展示口径变更恢复（2026-10-09 用户确认）：
酵母展示系统本质为基于酵母的活药递送平台，2020-2025 各批按旧口径
（酵母展示/生产技术=剔）剔除的酵母展示类条目全部恢复入库。
- 从 relevance_drops.json drop 区移出 → restored 区留档
- 用途非活药递送（体外工具/催化）者进 flag 区标注"如嫌宽可删"
- 从 all-db 复制记录入 kept 并设 note
幂等。"""
import json, pathlib

base = pathlib.Path(__file__).resolve().parent.parent
kept_p = base / "literature_database.json"
all_p = base / "literature_database_all.json"
drops_p = base / "relevance_drops.json"

# DOI -> flag_note（None=直接保留；str=保留并 flag）
RESTORE = {
    # —— 2020 批（2 条）——
    "10.1021/acssynbio.9b00360": None,
    #   酵母表面展示噬菌体内溶素 LysSA11（治疗性抗菌蛋白的活体展示平台）
    "10.1021/acssynbio.0c00159": None,
    #   酵母展示平台多重进化治疗性抗体片段（CRISPR 辅助定向进化）
    # —— 2022 批（1 条，按现 date 归属）——
    "10.1021/acssynbio.2c00101": "酵母展示蛋白质组规模信号肽筛选——展示系统体外工具，按酵母展示口径纳入，如嫌宽可删",
    # —— 2023 批（5 条）——
    "10.1021/acssynbio.2c00371": "酵母表面共展示多酶级联催化天然产物糖基化——展示系统催化应用，按酵母展示口径纳入，如嫌宽可删",
    "10.1021/acssynbio.2c00351": "转录调控器滴定酵母展示蛋白亲和力——展示工程工具，按酵母展示口径纳入，如嫌宽可删",
    "10.1002/adhm.202300793": None,
    #   酵母展示筛选 BMP-2 affibody 调控 BMP-2 递送与生物活性（展示→药物递送）
    "10.1021/acssynbio.3c00299": "酵母多样化碱基编辑器 yDBE 抗体增强平台——酵母蛋白进化平台（非严格表面展示），按酵母展示口径纳入，如嫌宽可删",
    "10.1021/jacs.3c08291": "酵母展示超高通量定向进化聚合物降解酶——展示系统酶进化/环境应用，按酵母展示口径纳入，如嫌宽可删",
    # —— 2025 批（4 条）——
    "10.1038/s41589-025-01881-9": "展示技术平台生成淀粉样纤维构象抗体——抗体发现方法学，按酵母展示口径纳入，如嫌宽可删",
    "10.1021/acssynbio.5c00209": "酵母表面展示 PETase/MHETase 全细胞催化 PET 降解——展示系统环境催化，按酵母展示口径纳入，如嫌宽可删",
    "10.1021/acssynbio.5c00321": None,
    #   酵母展示/OrthoRep 免疫治疗蛋白发现系统综述（Review→综述节）
    "10.1038/s41467-025-65236-7": "酵母展示 SCASA 模拟癌细胞表征 CAR-T 抗原密度响应——展示系统体外表征工具，按酵母展示口径纳入，如嫌宽可删",
}

NOTE_BASE = "2026-10-09 口径变更恢复：酵母展示系统视为基于酵母的活药递送平台（用户确认），2020-2025 批按旧口径剔除的酵母展示类条目纳入"

cfg = json.loads(drops_p.read_text(encoding="utf-8"))
drop, flag = cfg.setdefault("drop", {}), cfg.setdefault("flag", {})
restored = cfg.setdefault("restored", {})

kept = json.loads(kept_p.read_text(encoding="utf-8"))
all_db = json.loads(all_p.read_text(encoding="utf-8"))
have = {(r.get("doi") or "").lower() for r in kept}
idx = {(r.get("doi") or "").lower(): r for r in all_db}

n_copy = n_flag = n_move = 0
for doi, fl in RESTORE.items():
    # 1) drop -> restored
    if doi in drop:
        restored[doi] = drop.pop(doi) + " ｜ " + NOTE_BASE
        n_move += 1
    elif doi not in restored:
        restored[doi] = NOTE_BASE
    # 2) flag 标注
    if fl:
        flag.setdefault(doi, fl)
        n_flag += 1
    # 3) 复制入 kept
    if doi not in have:
        r = idx.get(doi)
        if not r:
            print("MISSING in all-db:", doi)
            continue
        r = dict(r)
        r["source"] = r.get("source") or "YeastDisplayRestore-2026"
        r["note"] = NOTE_BASE + (f"；{fl}" if fl else "（治疗蛋白展示/递送方向，直接保留）")
        kept.append(r)
        have.add(doi)
        n_copy += 1

kept_p.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
drops_p.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"drop->restored: {n_move}, flagged: {n_flag}, copied into kept: {n_copy}")
print(f"kept -> {len(kept)} | drop {len(drop)} / flag {len(flag)} / restored {len(restored)}")
