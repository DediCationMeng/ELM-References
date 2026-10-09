#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重放全部手工修正到 literature_database.json（kept）。
原因：elm_filter_journals.py 重建 kept 时会丢失手工编辑（日期归属、体裁归类、备注）。
用法：python tools/elm_apply_manual_fixes.py [--dir DIR]  —— 幂等，可反复执行。
"""
import argparse
import json
import pathlib

FIXES = {
    # DOI: (字段操作) —— date_fix 为按在线首发日归属批次；review=True 加 Review 体裁；note 为备注
    "10.1038/s41563-022-01430-y": {
        "date_fix": "2022-12-22",
        "review": True,
        "note": "News & Views 评论体裁，人工归类入综述/观点节；在线首发 2022-12-22（元数据卷期日期 2023-01），按首发日归属 2022 批",
    },
    "10.1038/s41589-019-0451-y": {
        "review": True,
        "note": "Nat Chem Biol N&V 评论（评 2019 孢子打印活体材料），人工归类入 2020 综述/观点节；2026-10-09 漏检回查补入",
    },
    "10.1002/advs.202205302": {
        "review": True,
        "note": "生物制造光化学综述/观点，人工归类入综述节",
    },
    "10.1016/j.mtbio.2023.100583": {
        "review": True,
        "note": "蓝细菌活体生物材料综述，人工归类入综述节",
    },
    "10.1016/j.mtbio.2023.100560": {
        "review": True,
        "note": "丝状真菌合成生物学综述，人工归类入综述节",
    },
    "10.1038/s44222-023-00078-w": {
        "review": True,
        "note": "LBP 转化评论，人工归类入综述/观点节",
    },
    "10.1038/s44222-023-00105-w": {
        "review": True,
        "note": "活体材料癌症生物学综述，人工归类入综述/观点节",
    },
    "10.1038/s44222-023-00119-4": {
        "review": True,
        "note": "细菌疗法转化综述，人工归类入综述/观点节（Web 补漏补入）",
    },
    "10.1038/s41578-023-00554-0": {
        "note": "Nat Rev Mater ELM 可持续建筑综述（Web 补漏补入）",
    },
    # —— 2024 批 ——
    "10.1016/j.chom.2024.02.008": {
        "review": True,
        "note": "Cell Host Microbe 评论体裁，人工归类入综述/观点节",
    },
    "10.1016/j.xcrm.2024.101562": {
        "review": True,
        "note": "Cell Rep Med 评论/预览体裁，人工归类入综述/观点节",
    },
    "10.1016/j.cels.2024.02.004": {
        "review": True,
        "note": "Cell Systems 评论/预览体裁（评 MELG 活体嫁接材料），人工归类入综述/观点节（Web 补漏补入）",
    },
    "10.1016/j.cels.2024.11.015": {
        "review": True,
        "note": "Cell Systems 评论/预览体裁（评图灵基因电路），人工归类入综述/观点节（Web 补漏补入）",
    },
    # —— 历史一致性修正 ——
    "10.1016/j.ccell.2021.11.009": {
        "review": True,
        "note": "Cancer Cell 评论/观点体裁，人工归类入 2021 综述/观点节（2026-10-09 体裁口径统一时修正）",
    },
    "10.1016/j.chom.2024.01.005": {
        "note": "EPMC 误标 Comment，实为 SYNB1353 工程化活体生物药研究论文（动物模型+健康志愿者），留研究节；配对评论 10.1016/j.chom.2024.02.008",
    },
    # —— 2025 批 ——
    "10.1021/acssynbio.4c00683": {
        "review": True,
        "note": "ACS Synth Biol article-commentary 评论体裁（微藻 ELM 挑战与展望），人工归类入综述/观点节",
    },
    "10.1136/gutjnl-2024-334501": {
        "review": True,
        "note": "Gut 共识声明（Asia-Pacific Microbiota Consortium LBP 开发立场），人工归类入综述/观点节",
    },
    "10.1002/adma.202502728": {
        "review": True,
        "note": "Adv Mater 真菌 ELM 分类学框架论文（taxonomy/概念框架），人工归类入综述/观点节",
    },
    # —— 2026 批体裁标注（18 条综述/观点/协议/评论）——
    "10.1002/adhm.202505346": {"review": True, "note": "Printability-Healing Paradox 综述，人工归类入综述节"},
    "10.1002/anie.6873420": {"review": True, "note": "Angew 评论/Preview（评微生物群落流动生物催化活体材料），人工归类入综述/观点节"},
    "10.1002/advs.202523952": {"review": True, "note": "超声响应工程菌癌症治疗综述，人工归类入综述节"},
    "10.1002/adhm.202504250": {"review": True, "note": "3D 打印心脏补片综述，人工归类入综述节"},
    "10.1002/adma.202510110": {"review": True, "note": "干细胞生物打印综述，人工归类入综述节"},
    "10.1002/advs.202523532": {"review": True, "note": "软体机器人微创原位生物打印综述，人工归类入综述节"},
    "10.1016/j.chom.2026.03.014": {"review": True, "note": "Cell Host Microbe 评论/Preview（评 VIBRANT/LACTIN-V 阴道 LBP 临床试验），人工归类入综述/观点节"},
    "10.1021/acssynbio.6c00119": {"review": True, "note": "沙门菌工程化抗癌 LBP 框架综述，人工归类入综述节"},
    "10.1016/j.trecan.2026.04.005": {"review": True, "note": "肠道微生物代谢物增强癌症治疗综述（含 LBP），人工归类入综述节"},
    "10.1016/j.chom.2026.05.011": {"review": True, "note": "Cell Host Microbe 评论/Preview（评 Cell 工程菌鸡尾酒治肝性脑病），人工归类入综述/观点节"},
    "10.1038/s41596-026-01375-5": {"review": True, "note": "Nat Protoc 协议（生物打印类器官药敏平台），人工归类入综述/观点节"},
    "10.1016/j.chom.2026.05.025": {"review": True, "note": "工程化共生菌 eLBP 综述，人工归类入综述节"},
    "10.1038/s44222-026-00455-1": {"review": True, "note": "Nat Rev Bioeng 生物打印计算方法综述，人工归类入综述节"},
    "10.1038/s41563-026-02651-1": {"review": True, "note": "Nat Mater 评论（ELM 需要 EU 监管），人工归类入综述/观点节"},
    "10.1016/j.matt.2026.102962": {"review": True, "note": "Matter 观点/展望（植入水凝胶封装细菌活体治疗），人工归类入综述/观点节"},
    "10.1002/advs.77267": {"review": True, "note": "Cross-feeding 编程肠道菌群→LBP 综述，人工归类入综述节"},
    "10.1016/j.biomaterials.2026.124565": {"review": True, "note": "活体材料与生物实体多维相互作用综述，人工归类入综述节"},
    "10.1002/advs.77791": {"review": True, "note": "4D 生物打印智能 bioink 综述，人工归类入综述节"},
}

# 重复记录 id（同一论文的 PMC 镜像/重复记录，无 DOI）
# PMC11905049 = Adv Sci 封面镜像（重复于 10.1002/advs.202411769）
# IND609145893 = Biomaterials stiff bioink 重复记录（正式 DOI 10.1016/j.biomaterials.2025.123406）
# IND609298200 = Biomaterials H2S 发生器重复记录（正式 DOI 10.1016/j.biomaterials.2025.123388）
# PMC13580061 = Bioact Mater 瓷土微球 bioink 重复记录（2026 批 #130，与 PMID 42751516 同 DOI
#   10.1016/j.bioactmat.2026.08.018；保留带摘要的 PMID 记录）
DEDUP_IDS = {"PMC10074134", "PMC11095227", "PMC11905049", "IND609145893", "IND609298200", "PMC13580061"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(pathlib.Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    base = pathlib.Path(args.dir)
    db_path = base / "literature_database.json"
    recs = json.loads(db_path.read_text(encoding="utf-8"))
    if isinstance(recs, dict):
        recs = list(recs.values())
    # 去重：同一论文的 PMC 重复记录（期刊名变体/镜像记录，无 DOI）
    before = len(recs)
    recs = [r for r in recs if r.get("id") not in DEDUP_IDS]
    if len(recs) != before:
        print(f"dedup removed: {before - len(recs)}")
    n = 0
    for r in recs:
        fix = FIXES.get((r.get("doi") or "").lower())
        if not fix:
            continue
        if fix.get("date_fix"):
            r["date"] = fix["date_fix"]
        if fix.get("review"):
            pts = r.get("pubtypes") or []
            if not any("review" in p.lower() for p in pts):
                pts.append("Review")
            r["pubtypes"] = pts
        if fix.get("note") and fix["note"] not in (r.get("note") or ""):
            r["note"] = fix["note"]
        n += 1
    db_path.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manual fixes applied: {n} records")


if __name__ == "__main__":
    main()
