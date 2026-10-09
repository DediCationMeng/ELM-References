# -*- coding: utf-8 -*-
"""Add 文献类型 (research/review) annotation to each report entry; update header stats. Idempotent."""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
by_cn = {r['cn_title']: r for r in db if r.get('cn_title')}
ALIAS = {'近红外光响应工程益生菌系统': '光响应工程益生菌系统经肠脑轴缓解焦虑'}
PUNCT = re.compile(r'[\s：:？?、，,。（）()《》“”"\'\-_/\\]')
def norm_cn(s):
    return PUNCT.sub('', s)

def match_rec(name):
    parts = name.split('-', 3)
    cn = parts[3] if len(parts) > 3 else name
    cn = ALIAS.get(cn, cn)
    if cn in by_cn:
        return by_cn[cn]
    best, bs = None, 0.0
    for k, r in by_cn.items():
        a, b = set(norm_cn(cn)), set(norm_cn(k))
        if not a or not b:
            continue
        s = len(a & b) / max(len(a), len(b))
        if norm_cn(k)[:6] == norm_cn(cn)[:6]:
            s += 0.15
        if s > bs:
            bs, best = s, r
    return best if bs >= 0.62 else None

def type_label(rec):
    pts = [p.lower() for p in (rec.get('pubtypes') or [])]
    return '综述 / 观点' if 'review' in pts else '研究论文'

path = os.path.join(BASE, '03_Reports', '2026-09月度文献摘要报告.md')
lines = open(path, encoding='utf-8').read().splitlines()
out, i, added = [], 0, 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^### \d+\.\d+ (.+)$', ln or '')
    if not m:
        out.append(ln)
        i += 1
        continue
    rec = match_rec(m.group(1).strip())
    out.append(ln)
    i += 1
    # collect this entry's leading annotation lines (EN title / DOI / type)
    head = []
    while i < len(lines) and re.match(r'^- \*\*(英文原标题|DOI|文献类型)\*\*：', lines[i] or ''):
        head.append(lines[i])
        i += 1
    head = [h for h in head if '文献类型' not in h]
    if rec:
        head.insert(2 if len(head) >= 2 else len(head), f"- **文献类型**：{type_label(rec)}")
        added += 1
    out.extend(head)
text = '\n'.join(out)

n_res = sum(1 for r in db if type_label(r) == '研究论文')
n_rev = len(db) - n_res
text = text.replace('研究论文 43 篇，综述/观点 23 篇',
                    f'研究论文 {n_res} 篇，综述/观点 {n_rev} 篇（各条目已标注文献类型）')
open(path, 'w', encoding='utf-8').write(text)
print('type labels added:', added, '| research:', n_res, '| review:', n_rev)
