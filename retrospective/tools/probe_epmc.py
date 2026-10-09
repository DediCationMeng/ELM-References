# -*- coding: utf-8 -*-
"""Probe: why did the standard queries miss known papers?"""
import json, urllib.parse, urllib.request, ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (research-literature-agent)"}

def hit(q):
    u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "pageSize": "5", "resultType": "core"})
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=45, context=ctx).read().decode("utf-8"))
    except Exception as e:
        return "ERR " + str(e)[:60]
    res = d.get("resultList", {}).get("result", [])
    out = []
    for r in res[:3]:
        out.append({"t": r.get("title", "")[:70], "d": r.get("firstPublicationDate"),
                    "j": (r.get("journalInfo") or {}).get("journal", {}).get("title", "")[:40],
                    "abs": (r.get("abstractText") or "NO-ABSTRACT")[:70]})
    return d.get("hitCount"), out

print("1) DOI direct 10.1038/s41467-020-15508-1:")
print(hit('DOI:"10.1038/s41467-020-15508-1"'))
print()
print("2) LBP phrase in 2020-04:")
print(hit('(TITLE_ABS:"live bacterial therapeut*" OR TITLE_ABS:"live biotherapeutic*") AND FIRST_PDATE:[2020-04-01 TO 2020-04-30]'))
print()
print("3) NBME intravital full query:")
print(hit('(TITLE_ABS:"bioprint*" OR TITLE_ABS:"bioink") AND (TITLE_ABS:cell* OR TITLE_ABS:tissue OR TITLE_ABS:hydrogel) AND FIRST_PDATE:[2020-06-01 TO 2020-07-15] AND TITLE:"intravital"'))
print()
print("4) NBME intravital only bioprint clause:")
print(hit('TITLE_ABS:"bioprint*" AND FIRST_PDATE:[2020-06-01 TO 2020-07-15] AND TITLE:"intravital"'))
print()
print("5) NBME intravital DOI direct:")
print(hit('DOI:"10.1038/s41551-020-0568-z"'))
