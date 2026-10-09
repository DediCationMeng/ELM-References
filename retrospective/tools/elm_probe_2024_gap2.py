# -*- coding: utf-8 -*-
"""抓取 2024 补漏候选的全文摘要定夺。"""
import json, sys, io, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DOIS = [
    '10.1016/j.cels.2024.02.003',  # bacteria-assisted living grafting
    '10.1016/j.cels.2024.11.002',  # Turing gene circuit patterns
    '10.1016/j.cels.2024.11.015',  # Turing patterns comment
    '10.1016/j.cels.2024.02.004',  # sustainable protein regeneration comment
]

for doi in DOIS:
    q = urllib.parse.quote(f'DOI:{doi}')
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json'
    d = json.load(urllib.request.urlopen(url, timeout=40))
    for r in d['resultList']['result']:
        print('==', doi, '|', r.get('firstPublicationDate'), '|', r.get('title'))
        print('types:', r.get('pubTypeList', {}).get('pubType'))
        print((r.get('abstractText') or 'NO ABSTRACT')[:900])
        print()
