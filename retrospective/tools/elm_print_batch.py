# -*- coding: utf-8 -*-
"""打印指定年份白名单条目题名+摘要供双重审查。
用法: elm_print_batch.py <year> <start> <end> [char_limit]
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

YEAR = sys.argv[1] if len(sys.argv) > 1 else '2025'
START = int(sys.argv[2]) if len(sys.argv) > 2 else 1
END = int(sys.argv[3]) if len(sys.argv) > 3 else 40
LIM = int(sys.argv[4]) if len(sys.argv) > 4 else 700

db = json.load(open('literature_database.json', encoding='utf-8'))
ys = [it for it in db if (it.get('year') or (it.get('date') or '')[:4]) == YEAR]
print(f'{YEAR} 白名单共 {len(ys)} 条（顺序=库内顺序=白名单顺序）')
for i, it in enumerate(ys, 1):
    if not (START <= i <= END):
        continue
    ab = (it.get('abstract') or '').replace('\n', ' ')
    print(f"\n#{i} [{it.get('date')}] {it.get('journal_abbrev') or it.get('journal')}")
    print(f"  T: {it.get('title')}")
    print(f"  DOI: {it.get('doi')} | topics={it.get('topics')} | pubtypes={','.join(it.get('pubtypes') or [])[:100]}")
    print(f"  A: {ab[:LIM]}")
