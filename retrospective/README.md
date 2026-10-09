# ELM 文献回顾库（2020–2026）

工程活体材料（Engineered Living Materials, ELM）七年回顾性文献库。按日历年分批检索（2026 批为部分年，2026-01-01 ~ 2026-10-09），"优中选优"期刊白名单 + 题名+摘要双重审查。

## 总量

**747 篇**（研究 606 + 综述/观点 141，综述单独成节不计入年度研究数目）

| 年份 | 研究 | 综述/观点 | 小计 |
|------|------|-----------|------|
| 2020 | 51 | 13 | 64 |
| 2021 | 57 | 11 | 68 |
| 2022 | 68 | 11 | 79 |
| 2023 | 79 | 18 | 97 |
| 2024 | 106 | 24 | 130 |
| 2025 | 146 | 41 | 187 |
| 2026（部分年） | 99 | 23 | 122 |

## 目录结构（retrospective/）

- `literature_database.json` — 最终入库 747 条（kept，含 journal_group/pubtypes/note）
- `literature_database_all.json` — 全量原始库（含被剔除记录，审计溯源用）
- `relevance_drops.json` — 审查判定留档（drop 132 / flag 52 / restored 12，逐条注明理由）
- `cn_titles.json` — 中文译名库（747 条全覆盖，零待译）
- `02_BibTeX/` — 分年 BibTeX 库 + naming_manifest（含中文名列）
- `03_Reports/` — 分年年度统计、年度综评、TOP 精读、跨年发展时间线
- `tools/` — 检索/过滤/审查/导出全流程脚本（可复现）

## 版权红线

出版商 PDF **永不上传**（`01_PDF/`、`raw/` 原始数据均排除在本仓库之外）。

## 检索口径摘要

- Europe PMC 7 组查询（ELM / Bioprinting / LBP / Probiotics / FUNGAL / YEAST / LIVINGFORMS）+ arXiv + Web 顶级期刊双保险补漏
- 期刊白名单 A–F 组（Nature/Science/Cell 家族、Adv 系、JACS/Angew/Biomaterials、Cell Systems、Materials Today、ACS Synth Biol、Mater Today Bio、Adv Healthc Mater 等）
- 相关度口径：活菌本身成药/原位生产=收；细胞工厂产化合物=剔；酵母展示系统=收（基于酵母的活药递送平台）
