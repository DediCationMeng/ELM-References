# -*- coding: utf-8 -*-
"""2024 Web 补漏双保险：EPMC 直查疑似漏检候选。"""
import json, sys, io, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

QUERIES = [
    'JOURNAL:"Nature reviews. Bioengineering" AND FIRST_PDATE:[2024-01-01 TO 2024-12-31] AND (TITLE_ABS:"living material" OR TITLE_ABS:"bioprinting")',
    'JOURNAL:"Cell systems" AND FIRST_PDATE:[2024-01-01 TO 2024-12-31] AND (TITLE_ABS:"living" OR TITLE_ABS:"bacteria")',
    'TITLE_ABS:"living material" AND FIRST_PDATE:[2024-01-01 TO 2024-12-31] AND (JOURNAL:"Nature" OR JOURNAL:"Science" OR JOURNAL:"Cell")',
]

for q0 in QUERIES:
    q = urllib.parse.quote(q0)
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json&pageSize=15'
    d = json.load(urllib.request.urlopen(url, timeout=40))
    print('==', q0[:80], '... hits:', d.get('hitCount'))
    for r in d['resultList']['result']:
        print('-', r.get('firstPublicationDate'), '|', (r.get('title') or '')[:95])
        print('   doi:', r.get('doi'), '| journal:', r.get('journalInfo', {}).get('journal', {}).get('title'), '| types:', r.get('pubTypeList', {}).get('pubType'))
    print()
