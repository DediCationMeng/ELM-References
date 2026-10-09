# -*- coding: utf-8 -*-
"""Probe 2: isolate why phrase+wildcard queries miss known records."""
import json, urllib.parse, urllib.request, ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0 (research-literature-agent)"}

def hit(q):
    u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "pageSize": "3", "resultType": "core"})
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=45, context=ctx).read().decode("utf-8"))
    except Exception as e:
        return "ERR " + str(e)[:60]
    return d.get("hitCount")

D1 = 'DOI:"10.1038/s41551-020-0568-z"'   # Intravital 3D bioprinting (NBME)
D2 = 'DOI:"10.1038/s41467-020-15508-1"'  # live bacterial therapeutics (Nat Commun)

tests = [
    ("NBME: TITLE_ABS phrase bioprint*  +DOI", f'(TITLE_ABS:"bioprint*") AND {D1}'),
    ("NBME: TITLE_ABS plain bioprint*    +DOI", f'(TITLE_ABS:bioprint*) AND {D1}'),
    ("NBME: ANY phrase bioprint*         +DOI", f'("bioprint*") AND {D1}'),
    ("NBME: ANY plain bioprint*          +DOI", f'(bioprint*) AND {D1}'),
    ("NBME: TITLE_ABS phrase bioprinting +DOI", f'(TITLE_ABS:"bioprinting") AND {D1}'),
    ("NBME: TITLE_ABS phrase 3D print*   +DOI", f'(TITLE_ABS:"3D print*") AND {D1}'),
    ("NatCom: TITLE_ABS live bacterial therapeut* +DOI", f'(TITLE_ABS:"live bacterial therapeut*") AND {D2}'),
    ("NatCom: TITLE_ABS plain therapeut* +DOI", f'(TITLE_ABS:therapeut*) AND {D2}'),
    ("NatCom: ANY phrase live bacterial therapeut* +DOI", f'("live bacterial therapeut*") AND {D2}'),
    ("NatCom: TITLE_ABS engineered live +DOI", f'(TITLE_ABS:"engineered live") AND {D2}'),
]
for name, q in tests:
    print(f"{hit(q)!s:>6}  <- {name}")
