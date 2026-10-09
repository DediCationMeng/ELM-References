# -*- coding: utf-8 -*-
"""Update report/checklist md files: insert EN titles, fix DOIs, sync names (v3, idempotent)."""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
by_cn = {r['cn_title']: r for r in db if r.get('cn_title')}

PUNCT = re.compile(r'[\s：:？?、，,。（）()《》“”"\'\-_/\\]')

def norm_cn(s):
    return PUNCT.sub('', s)

def match_rec(name):
    parts = name.split('-', 3)
    cn = parts[3] if len(parts) > 3 else name
    cn_n = norm_cn(cn)
    for k, r in by_cn.items():
        if norm_cn(k) == cn_n:
            return r
    best, bs = None, 0.0
    for k, r in by_cn.items():
        kn = norm_cn(k)
        a, b = set(cn_n), set(kn)
        if not a or not b:
            continue
        score = len(a & b) / max(len(a), len(b))
        if kn[:6] == cn_n[:6]:
            score += 0.15
        if score > bs:
            bs, best = score, r
    return best if bs >= 0.62 else None

SKIP_EN = re.compile(r'^\s*[-*] \*{0,2}(英文原标题|DOI)\*{0,2}：')

# ---------- 1) checklist ----------
path1 = os.path.join(BASE, '03_Reports', '手动下载Checklist.md')
lines = open(path1, encoding='utf-8').read().splitlines()
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    if SKIP_EN.match(ln or ''):
        i += 1
        continue
    m = re.match(r'- \[[ x]\] \*\*(.+?)\*\*\s*$', ln or '')
    if not m:
        out.append(ln)
        i += 1
        continue
    rec = match_rec(m.group(1))
    if not rec:
        out.append(ln)
        i += 1
        continue
    out.append(f"- [{'x' if '[x]' in ln else ' '}] **{rec['normalized_name']}**")
    i += 1
    while i < len(lines) and lines[i].startswith('  - '):
        s = lines[i].strip()
        if SKIP_EN.match(lines[i]):
            i += 1
            continue
        if s.startswith('- 期刊：'):
            segs = s[len('- 期刊：'):].split('｜')
            segs[0] = rec.get('journal_abbrev') or segs[0]
            out.append('  - 期刊：' + '｜'.join(segs))
            out.append(f"  - 英文原标题：{rec['title']}")
        elif s.startswith('- 下载入口'):
            doi = rec.get('doi')
            out.append(f"  - 下载入口：<https://doi.org/{doi}>" if doi else
                       "  - 下载入口：暂无 DOI，请按 Google Scholar 检索下方英文原题")
        else:
            out.append(lines[i])
        i += 1
open(path1, 'w', encoding='utf-8').write('\n'.join(out))
print('checklist updated')

# ---------- 2) monthly report ----------
path2 = os.path.join(BASE, '03_Reports', '2026-09月度文献摘要报告.md')
lines2 = open(path2, encoding='utf-8').read().splitlines()
out2, unmatched = [], []
i = 0
while i < len(lines2):
    ln = lines2[i]
    m = re.match(r'^### (\d+\.\d+) (.+)$', ln or '')
    if not m:
        out2.append(ln)
        i += 1
        continue
    num, name = m.group(1), m.group(2).strip()
    rec = match_rec(name)
    if not rec:
        unmatched.append(name)
        out2.append(ln)
        i += 1
        continue
    out2.append(f"### {num} {rec['normalized_name']}")
    out2.append(f"- **英文原标题**：{rec['title']}")
    out2.append(f"- **DOI**：<https://doi.org/{rec['doi']}>" if rec.get('doi')
                else "- **DOI**：暂无（请按英文原题在 Google Scholar 检索）")
    i += 1
    # skip pre-existing EN title / DOI lines right after heading
    while i < len(lines2) and SKIP_EN.match(lines2[i] or ''):
        i += 1
open(path2, 'w', encoding='utf-8').write('\n'.join(out2))
print('report updated')

print('unmatched:', len(unmatched))
for u in unmatched:
    print('  !', u)
print('records missing DOI:', sum(1 for r in db if not r.get('doi')))
