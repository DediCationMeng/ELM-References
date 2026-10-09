# ELM References

工程活体材料（Engineered Living Materials, ELMs）· 生物 3D 打印（Bioprinting / bioink）· 微生物活药（Live Biotherapeutics）· 工程化益生菌（Engineered Probiotics）——**月度文献情报库**，长期维护。

每期产出：规范化命名的论文清单、Zotero 可导入的 BibTeX、月度摘要报告（含批判性思考）、TOP3 精读报告、PDF 获取状态 Checklist。

---

## 目录约定（每月一期）

```
ELM-References/
├── README.md                  ← 本文件（项目规范与维护流程）
├── .gitignore                 ← PDF 不入库（版权 + 体积），本地自行管理
└── YYYY-MM/                   ← 月度目录（如 2026-09/）
    ├── 02_BibTeX/
    │   ├── ELM_YYYY-MM_library.bib    ← Zotero 直接导入
    │   └── naming_manifest.csv        ← 规范化命名总清单（含英文原题/类型/DOI）
    ├── 03_Reports/
    │   ├── YYYY-MM月度文献摘要报告.md   ← 全量论文摘要+批判性思考
    │   ├── 手动下载Checklist.md        ← PDF 获取状态（三态标记）
    │   └── 精读报告N-….md              ← 每月 TOP3 深度精读
    ├── literature_database.json       ← 元数据库（66+ 字段全量）
    ├── download_status.json           ← PDF 下载尝试记录
    ├── raw/                           ← API 原始返回（epmc/arxiv，恢复源）
    └── scripts/                       ← 检索与整理流水线脚本（可跨月复用）
```

> **PDF 说明**：出版商 PDF 受版权保护且体积大，**不进入本仓库**。已下载 PDF 按规范化命名保存在本地 `01_PDF/`（已在 .gitignore 中排除）。

## 规范化命名

`年月-期刊简写-论文中文名`，例如：

```
2026-09-NatMicrobiol-编码前噬菌体的工程菌实现预防性裂解噬菌体疗法
```

完整映射见各期 `02_BibTeX/naming_manifest.csv`。

## Checklist 三态标记

| 标记 | 含义 |
|---|---|
| `[x]` | 已获取 PDF（已按规范化命名存入本地 `01_PDF/`） |
| `[ ]` | 待下载（条目内附 DOI 直达入口） |
| `[×]` | 高校图书馆机构未订阅、无法下载（手动标记，后续不再追踪） |

Checklist 按**研究论文（含预印本）**与**综述/观点**分节呈现；每条目附英文原标题、DOI、文献类型。

## 月度维护流程

1. **检索**：`scripts/search_epmc.py`（Europe PMC API，覆盖 PubMed + bioRxiv）+ arXiv API + 学术搜索引擎补充；
2. **入库**：`scripts/build_db.py` 合并去重为 `literature_database.json`；
3. **DOI 补全**：CrossRef 标题反查 → PMC 页面 meta 提取 → arXiv 标准 DOI（`10.48550/arXiv.<id>`），确保 100% DOI 覆盖；
4. **命名与 BibTeX**：`scripts/build_manifest_bib.py` 生成规范化命名、`ELM_YYYY-MM_library.bib`、`naming_manifest.csv`；
5. **PDF 管理**：自动下载开放获取 PDF；手动下载的 PDF 用 `scripts/import_manual_pdfs.py` 从下载文件夹匹配入库（pypdf 首页 DOI/标题三级匹配）；剩余按 `手动下载Checklist.md` 追踪；
6. **报告**：月度摘要报告（每篇：通讯作者、摘要、结论、创新点、科学问题、批判性思考）+ TOP3 精读报告（按影响因子 × 科学问题新颖性遴选）；
7. **归档**：新一期目录 `YYYY-MM/` 提交至本仓库，BibTeX 在上期基础上增量更新。

## 文献类型判定

以 Europe PMC `pubtypes` 为准：含 `Review` → 综述/观点；其余（含预印本）→ 研究论文。

## GitHub 归档与上传

每期完成后将文本产物上传至本仓库（PDF 永不上传——出版商版权，且体量大）：

1. **优先 `git push`**（`github.com` 可达时）；
2. 否则经 **`api.github.com` REST 通道**（网络受限环境通常可达）：使用 `tools/upload_rest.py`（Git Data API 单次原子提交；空仓库需先用 Contents API 建初始提交，否则 git/blobs 返回 409）；
3. 凭证：Fine-grained PAT（Repository access 仅限本仓库，Permissions → **Contents: Read and write**），一次性使用，用毕即在 GitHub 设置中删除；
4. 上传后经 API 核验文件清单完整性。

> 注意：WorkBuddy 的 GitHub 连接器对本仓库无 Contents 写权限（403 "Resource not accessible by integration"），读取可用、写入勿依赖。

## 引用管理

`02_BibTeX/*.bib` 按 Zotero 直接导入格式维护（File → Import → 选择 .bib）。条目含作者、期刊、年份、DOI、URL。
