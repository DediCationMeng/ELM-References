# -*- coding: utf-8 -*-
"""Generate: normalized naming manifest (年月-期刊简写-论文中文名), rename PDFs, Zotero-ready BibTeX."""
import json, os, re, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
db = json.load(open(os.path.join(BASE, "literature_database.json"), encoding="utf-8"))

# Chinese titles keyed by original English title (prefix match)
CN = {
"Volumetric 3D printing of microalgae": "体积3D打印微藻工程活体材料",
"Engineered living materials: integration": "工程活体材料：生命与非生命系统的整合",
"Porcelain-clay-inspired microsphere": "瓷土仿生微球水凝胶生物墨水经免疫成骨调控促进骨再生",
"3D Bioprinting Approaches for Dental Pulp": "牙髓再生的3D生物打印策略范围综述",
"Microbial indole-3-acetamide": "微生物吲哚3乙酰胺经HIF2α神经酰胺信号缓解多囊卵巢综合征",
"Why probiotics fail": "益生菌为何失效肠道生态位张力是缺失变量",
"An Automated Thickness Evaluation": "机器人生物打印中基于结构光3D相机的自动厚度评估",
"A Physics-Based Closed-Loop Robotic Bioprinting": "面向容积性肌肉缺损的物理闭环机器人生物打印框架",
"Rewiring lactobacilli": "乳酸菌重编程挑战机遇与治疗转化路径",
"Exploring a cold-gelled whey protein": "用于培养肉3D生物打印的冷凝乳清蛋白基墨水",
"Adhesion-Enhanced Engineered Probiotic": "黏附增强型工程益生菌延长肠道滞留并钙卫蛋白响应性治疗IBD",
"Microbial Signals in Cancer": "癌症中的微生物信号宿主微生物组肿瘤互作与治疗策略",
"Non-Traditional Antibacterial Agents": "针对WHO2024重点病原体的非传统抗菌药物结构化更新",
"Antibiotic- and inducer-free biosynthesis": "工程益生菌大肠杆菌以粗甘油无抗生素无诱导剂合成靛苷",
"Tailored living mycelium macerate": "定制化活体菌丝匀浆用于可重复柔性致动器",
"Biohybrid microalgae living hydrogel": "自供氧微藻生物杂交活体水凝胶联合绿色合成锌纳米颗粒抗耐药菌感染",
"Living Biohybrid Hydrogels for Co-Delivery": "共递送氧气抗癌药与益生菌的生物杂交活体水凝胶",
"Machine-Learning-Assisted Quantitative Printability": "机器学习辅助的挤出式生物打印可打印性定量评估",
"Controlling viscoelastic behavior": "合成黏附素与流变学调控工程活体材料黏弹性与微观结构",
"Probiotics and Extracellular Vesicles as Redox": "益生菌与胞外囊泡作为伤口愈合的氧化还原调节剂",
"CRISPR-Cas9 engineering for high-level": "CRISPRCas9工程布拉氏酵母高水平生产β半乳糖苷酶",
"Mucosal-Associated Invariant T Cells": "黏膜相关恒定T细胞在健康与疾病中的作用",
"In situ bioprinting of patterned prevascular": "纯细胞生物墨水原位生物打印图案化预血管组织",
"Bioactive keratin-pectin methacrylate": "角蛋白果胶甲基丙烯酸酯多丝神经导管修复长段神经缺损",
"FUS-pen": "FUS笔聚焦超声无标记细胞微雕刻构建功能化共培养微组织",
"Prophage-encoding engineered bacteria": "编码前噬菌体的工程菌实现预防性裂解噬菌体疗法",
"Engineered living materials suppress uropathogenic": "工程活体材料经持续益生菌释放抑制尿路致病性大肠杆菌",
"Reprogramming immunological debris clearance": "虾青素装载工程益生菌囊泡重编程免疫碎片清除",
"Genetic principles enabling": "构建细菌疗法的遗传学原理",
"Spectroscopic Insights into Nutrient-Controlled Biofilm": "出芽短梗霉营养控制生物膜形成的光谱学机制",
"Data-driven predictive design": "数据驱动的工程活体水凝胶预测性设计",
"Decellularized extracellular matrix bioinks": "聚合物工程视角下的脱细胞基质生物墨水",
"Silk proteins for 3D bioprinting": "丝蛋白3D生物打印丝素结构支撑与丝胶细胞支持协同",
"A durably colonising engineered native symbiont": "持久定植的工程化天然共生菌实现肠道持续递送治疗代谢功能障碍",
"The Archibiome": "建筑微生物组将工程活体材料拓展至多尺度建成环境",
"Cell-laden 3D bioprinted hydrogels for wound": "载细胞3D生物打印水凝胶用于伤口愈合的机制与转化",
"Modulating innate immune responses to curli": "蛋白质工程调控卷曲纤维的固有免疫应答",
"A New Bioactive Glass-Based Hybrid Bioink": "兼具促细胞活性与抗菌性的生物活性玻璃杂化生物墨水",
"Dysosmobacter": "Dysosmobacter从偶然发现到与健康相关的下一代有益共生菌",
"A 3D-Bioprinted, Cell-Guiding Hydrogel Patch": "3D生物打印细胞引导水凝胶贴片各向异性修复腹壁切口",
"Probiogenomics as a Computational": "益生菌基因组学候选益生菌安全门控基因组分析框架",
"Bacterial metabolic-immune reprogramming in cancer": "癌症中细菌代谢免疫重编程从活体载体到工程化细胞工厂",
"Metabolism-Driven Morphomechanical Transitions": "稳态动态共价双网络活体水凝胶中代谢驱动的形态力学转变",
"Sporulation modulates viscoelastic development": "芽孢形成经胞外基质重塑调控枯草芽孢杆菌材料黏弹性发育",
"Fabrication of a calcium cement-incorporated": "挤出式3D生物打印含钙水泥复合水凝胶支架",
"Cartilage-targeting engineered probiotic bacterial": "软骨靶向工程益生菌胞外囊泡经调控炎症治疗骨关节炎",
"3D bioprinted human vascular organoid sheets": "3D生物打印人血管类器官片促进缺血修复并展现体内适应性重塑",
"The Gut-Liver Axis in Metabolic Dysfunction": "代谢相关脂肪性肝病及肝细胞癌中的肠肝轴",
"Granular Hydrogel Composites as Matrices": "颗粒水凝胶复合材料作为工程活体材料基质",
"Novel options for the management of": "艰难梭菌感染的新型管理方案展望",
"Self-sustaining microalgae-laden hydrogel": "自维持微藻载水凝胶实现高效生物质生产",
"Smart Bioinks for 4D Bioprinting": "4D生物打印智能生物墨水要求设计与应用",
"Engineered Probiotics with Pb-Binding": "铅结合增强卷曲纳米纤维的工程益生菌用于口服排铅",
"Development of chitosan bioink": "纳米纤维素增强壳聚糖生物墨水的3D生物打印研究",
"3D-Printed hydroxysafflor yellow A": "3D打印羟红花黄色素A水凝胶多孔支架用于骨再生",
"Biofabrication of osteochondral composite scaffolds": "骨软骨复合支架生物制造多材料生物打印进展",
"An engineered probiotic Escherichia coli Nissle": "工程化Nissle1917大肠杆菌递送Amuc1100在CT26结肠癌模型中的研究",
"Reversal of the neutrophil barrier": "逆转中性粒细胞屏障增效免疫工程菌治疗胰腺癌",
"Engineered probiotic biointerfaces": "工程益生菌生物界面构建原理显微表征与生物医学功能",
"Airflow controlled droplet bioprinting": "气流控制液滴生物打印高通量生成iPSC来源胸腺类器官",
"Bioprinting of BSA membranes": "预细胞化PLGA微支架生物打印BSA膜迈向膈肌组织工程",
"Cancer and the microbiome: from association": "癌症与微生物组从关联到干预",
"Live probiotic encapsulation": "活益生菌包封工艺工程壁材与人体胃肠道转化差距",
"Targeted tumor desialylation by engineered probiotic": "工程益生菌靶向肿瘤去唾液酸化重编程肿瘤微环境增效免疫治疗",
"Mesaconic acid delivery": "经生物材料与工程益生菌肠道递送中康酸减轻克罗恩病肠道炎症",
"A light-responsive engineered probiotic": "光响应工程益生菌系统经肠脑轴缓解焦虑",
}

def cn_title(t):
    for k, v in CN.items():
        if t.startswith(k):
            return v
    return "未命名文献"

def bibtex_escape(s):
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")

def make_key(rec):
    au = (rec.get("authors") or ["anon"])[0]
    au = re.sub(r"[^A-Za-z]", "", au.split()[-1] if au else "anon") or "anon"
    yr = (rec.get("date") or "2026")[:4]
    kw = re.sub(r"[^A-Za-z]", "", rec["title"].split()[0])[:8] or "paper"
    return f"{au}{yr}{kw}"

manifest_rows = []
entries = []
seen_titles = set()
for rec in db:
    t = rec["title"]
    if t in seen_titles:
        continue
    seen_titles.add(t)
    ym = (rec.get("date") or "2026-09").replace("-", "")[:6]
    ym_fmt = ym[:4] + "-" + ym[4:]
    ja = re.sub(r"[^A-Za-z]", "", (rec.get("journal_abbrev") or "Preprint").split("(")[0].strip().split()[0] if rec.get("journal_abbrev") else "Preprint")
    ja = (rec.get("journal_abbrev") or "Preprint")[:20].split("(")[0].strip().replace(" ", "")
    ja = re.sub(r"[^A-Za-z]", "", ja)[:12] or "Preprint"
    cn = cn_title(t)
    normalized = f"{ym_fmt}-{ja}-{cn}"
    rec["cn_title"] = cn
    rec["normalized_name"] = normalized
    rec["key"] = make_key(rec)

    authors_bib = " and ".join(rec.get("authors") or [])
    year = (rec.get("date") or "2026")[:4]
    doi = rec.get("doi")
    jt = rec.get("journal") or "preprint"
    if rec["source"] == "arXiv":
        bib = f"""@article{{{rec['key']},
  title   = {{{bibtex_escape(t)}}},
  author  = {{{bibtex_escape(authors_bib)}}},
  journal = {{arXiv preprint arXiv:{rec.get('id','')}}},
  year    = {{{year}}},
  url     = {{https://arxiv.org/abs/{rec.get('id','')}}},
}}"""
    elif "Preprint" in (rec.get("journal") or "") or (rec.get("id") or "").startswith("PPR"):
        bib = f"""@article{{{rec['key']},
  title   = {{{bibtex_escape(t)}}},
  author  = {{{bibtex_escape(authors_bib)}}},
  journal = {{bioRxiv preprint}},
  year    = {{{year}}},
  doi     = {{{doi or ''}}},
  url     = {{https://doi.org/{doi or ''}}},
}}"""
    else:
        bib = f"""@article{{{rec['key']},
  title   = {{{bibtex_escape(t)}}},
  author  = {{{bibtex_escape(authors_bib)}}},
  journal = {{{bibtex_escape(jt)}}},
  year    = {{{year}}},
  doi     = {{{doi or ''}}},{'{}'.format(chr(10) + '  url     = {https://doi.org/' + doi + '},') if doi else ''}
}}"""
    entries.append(bib)
    pts = [p.lower() for p in (rec.get("pubtypes") or [])]
    art_type = "综述/观点" if "review" in pts else "研究论文"
    manifest_rows.append((normalized, t, art_type, rec.get("journal_abbrev") or "Preprint", rec.get("date"), rec.get("corresponding_author") or "-", doi or "-", rec.get("pdf_downloaded"), rec.get("pdf_file") or "-"))

bib_all = "\n\n".join(entries)
open(os.path.join(BASE, "02_BibTeX", "ELM_2026-09_library.bib"), "w", encoding="utf-8").write(bib_all)

# manifest CSV
import csv
with open(os.path.join(BASE, "02_BibTeX", "naming_manifest.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["规范化命名", "英文原题", "文献类型", "期刊", "发表日期", "通讯作者(推定)", "DOI", "PDF已下载", "PDF文件"])
    for row in manifest_rows:
        w.writerow(list(row))

json.dump(db, open(os.path.join(BASE, "literature_database.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# rename downloaded PDFs to normalized naming
PDF_DIR = os.path.join(BASE, "01_PDF")
for rec in db:
    if rec.get("pdf_downloaded") and rec.get("pdf_file"):
        src = os.path.join(PDF_DIR, rec["pdf_file"])
        if os.path.exists(src):
            dst_name = re.sub(r'[<>:"/\\|?*]', "_", rec["normalized_name"]) + ".pdf"
            dst = os.path.join(PDF_DIR, dst_name)
            if src != dst and not os.path.exists(dst):
                shutil.move(src, dst)
                rec["pdf_file"] = dst_name

json.dump(db, open(os.path.join(BASE, "literature_database.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bib entries:", len(entries))
for r in manifest_rows[:70]:
    print(("*" if r[7] else " "), r[0])
