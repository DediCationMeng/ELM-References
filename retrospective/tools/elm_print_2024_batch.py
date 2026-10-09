# -*- coding: utf-8 -*-
"""打印 2024 批白名单条目题名+摘要供双重审查。用法: elm_print_2024_batch.py <start> <end>"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

START = int(sys.argv[1]) if len(sys.argv) > 1 else 112
END = int(sys.argv[2]) if len(sys.argv) > 2 else 146

db = json.load(open('literature_database.json', encoding='utf-8'))
y24 = [it for it in db if (it.get('year') or (it.get('date') or '')[:4]) == '2024']
print(f'2024 白名单共 {len(y24)} 条（顺序=库内顺序=白名单顺序）')
for i, it in enumerate(y24, 1):
    if not (START <= i <= END):
        continue
    ab = (it.get('abstract') or '').replace('\n', ' ')
    print(f"\n#{i} [{it.get('date')}] {it.get('journal_abbrev') or it.get('journal')}")
    print(f"  T: {it.get('title')}")
    print(f"  DOI: {it.get('doi')} | topics={it.get('topics')} | pubtypes={','.join(it.get('pubtypes') or [])[:100]}")
    print(f"  A: {ab[:700]}")
