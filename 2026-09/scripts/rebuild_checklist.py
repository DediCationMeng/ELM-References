# -*- coding: utf-8 -*-
"""Rebuild 手动下载Checklist.md: research/review sections, tri-state marks ([x]/[ ]/[x]).
Preserves user-set marks from the previous checklist."""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
old_path = os.path.join(BASE, '03_Reports', '手动下载Checklist.md')
old = open(old_path, encoding='utf-8').read()

# --- recover previous user marks: name -> '[x]' / '[ ]' / '[x]' ---
prev_marks = {}
for m in re.finditer(r'- \[([ x×X])\] \*\*(.+?)\*\*', old):
    mark, name = m.group(1), m.group(2)
    prev_marks[name] = mark.lower() if mark.lower() in ('x', '×') else ' '

PUNCT = re.compile(r'[\s：:？?、，,。（）()《》“”"\'\-_/\\]')
def norm_cn(s):
    return PUNCT.sub('', s)

def prev_mark_for(rec):
    n = rec['normalized_name']
    if n in prev_marks:
        return prev_marks[n]
    # fuzzy: cn part
    cn = norm_cn(n.split('-', 3)[-1])
    for k, v in prev_marks.items():
        if norm_cn(k.split('-', 3)[-1]) == cn:
            return v
    return None

def art_type(rec):
    pts = [p.lower() for p in (rec.get('pubtypes') or [])]
    return 'review' if 'review' in pts else 'research'

PRIO = {'Nat Microbiol':1,'Gut':1,'Cell Host Microbe':1,'Cell Rep Med':1,'Lancet Oncol':1,'BMC Med':1,
        'Adv Sci (Weinh)':2,'Bioact Mater':2,'Biomaterials':2,'Small':2,'Adv Healthc Mater':2,
        'Mater Horiz':2,'Mater Today Bio':2,'J Control Release':2,'Trends Biotechnol':2,
        'Acta Biomater':2,'Biofabrication':2,'Lab Chip':2,'Infect Immun':2,'Genetics':2,'Langmuir':3}

def entry_lines(rec):
    mark = 'x' if rec.get('pdf_downloaded') else (prev_mark_for(rec) or ' ')
    disp = '×' if mark == '×' else mark
    doi = rec.get('doi')
    ja = rec.get('journal_abbrev') or rec.get('journal') or 'Preprint'
    out = [f"- [{disp}] **{rec['normalized_name']}**"]
    out.append(f"  - 期刊：{ja}｜日期：{rec.get('date')}｜类型：{'综述/观点' if art_type(rec)=='review' else '研究论文'}｜通讯作者(推定)：{rec.get('corresponding_author') or '见原文'}")
    out.append(f"  - 英文原标题：{rec['title']}")
    out.append(f"  - 下载入口：<https://doi.org/{doi}>" if doi else "  - 下载入口：暂无 DOI，请按英文原题检索")
    if rec.get('pdf_downloaded'):
        out.append(f"  - 状态：已获取（01_PDF/{rec.get('pdf_file') or ''}）")
    else:
        out.append("  - 建议渠道：机构图书馆/校园网；若未订阅请将本条标记为 [×]")
    return out

research = [r for r in db if art_type(r) == 'research']
review = [r for r in db if art_type(r) == 'review']
def sort_key(r):
    got = 0 if r.get('pdf_downloaded') else 1
    return (got, PRIO.get(r.get('journal_abbrev') or '', 4), r.get('date') or '')
research.sort(key=sort_key)
review.sort(key=sort_key)

n_have = sum(1 for r in db if r.get('pdf_downloaded'))
n_miss = len(db) - n_have

lines = []
lines.append('# 论文获取 Checklist（2026-09-09 至 2026-10-09 检索窗口）')
lines.append('')
lines.append('更新于 2026-10-09：DOI 已全量补全（66/66）；已导入下载文件夹中手动下载的 PDF 45 篇。')
lines.append('')
lines.append('**三态标记说明**：')
lines.append('- `[x]` = 已获取 PDF（已按规范化命名存入 `01_PDF/`）')
lines.append('- `[ ]` = 待下载（可通过 DOI 入口下载）')
lines.append('- `[×]` = 高校图书馆机构未订阅、无法下载 —— 请手动把 `[ ]` 改为 `[×]` 以标记，后续不再追踪')
lines.append('')
lines.append(f'**当前统计**：已获取 {n_have} 篇｜待获取 {n_miss} 篇（研究论文 {len(research)} 篇、综述/观点 {len(review)} 篇）')
lines.append('')

def emit_section(title, recs):
    lines.append(f'## {title}（{len(recs)} 篇）')
    lines.append('')
    for r in recs:
        lines.extend(entry_lines(r))
        lines.append('')

emit_section('一、研究论文（含预印本）', research)
emit_section('二、综述 / 观点', review)

open(old_path, 'w', encoding='utf-8').write('\n'.join(lines))
print('checklist rebuilt')
print('research:', len(research), '| review:', len(review))
print('have:', n_have, '| missing:', n_miss)
kept = sum(1 for r in db if not r.get('pdf_downloaded') and prev_mark_for(r) == '×')
print('preserved user [x] marks on missing items:', kept)
