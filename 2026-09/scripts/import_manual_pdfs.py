# -*- coding: utf-8 -*-
"""Match manually downloaded PDFs in Downloads with the literature DB, copy into 01_PDF/.
Matching priority: DOI exact > title word-overlap > filename word-overlap.
Run with --apply to actually copy; default is dry-run report."""
import json, os, re, sys, shutil, datetime
from pypdf import PdfReader

BASE = os.path.dirname(os.path.abspath(__file__))
DL = r'C:\Users\MZR\Downloads'
PDF_DIR = os.path.join(BASE, '01_PDF')
APPLY = '--apply' in sys.argv

db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))

DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"\'<>,;]+')
STOP = set('the a an of for and in on with to from by via using use based study novel new its it this that is are at as'.split())

def words(s):
    return set(w for w in re.findall(r'[a-z0-9]+', s.lower()) if w not in STOP and len(w) > 2)

def overlap(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))

# index db (keep helper fields OUT of the record dicts - they must never be serialized)
db_words = [words(r['title']) for r in db]
db_dois = [(r.get('doi') or '').lower().rstrip('.') for r in db]

# collect today's PDFs from Downloads
cutoff = datetime.datetime(2026, 10, 9, 0, 0, 0).timestamp()
cands = []
for fn in os.listdir(DL):
    if not fn.lower().endswith('.pdf'):
        continue
    p = os.path.join(DL, fn)
    if os.path.getmtime(p) < cutoff:
        continue  # skip old unrelated files
    cands.append((fn, p))
print('candidate PDFs (downloaded today):', len(cands))

results = []
for fn, p in sorted(cands):
    doi_found, title_guess, first_text = None, None, ''
    try:
        rd = PdfReader(p)
        meta = rd.metadata
        if meta and meta.title and len(meta.title) > 15:
            title_guess = meta.title
        txt = ''
        for pg in rd.pages[:2]:
            txt += (pg.extract_text() or '')[:4000]
        first_text = txt
        for m in DOI_RE.findall(txt):
            m = m.lower().rstrip('.')
            if 'creativecommons' in m or 'crossmark' in m:
                continue
            doi_found = m
            break
    except Exception as e:
        print('READ-ERR', fn[:50], str(e)[:60])

    matched, score, how = None, 0.0, ''
    # 1) DOI exact
    if doi_found:
        for idx, r in enumerate(db):
            if db_dois[idx] and (doi_found == db_dois[idx] or doi_found.startswith(db_dois[idx]) or db_dois[idx].startswith(doi_found)):
                matched, how = r, 'doi'
                score = 1.0
                break
    # 2) title overlap (metadata title or first-page text head)
    if not matched:
        cands_txt = [title_guess or '', ' '.join(first_text.split())[:300]]
        for idx, r in enumerate(db):
            for ct in cands_txt:
                s = overlap(words(ct), db_words[idx])
                if s > score:
                    score, matched, how = s, r, 'title'
        # 3) filename overlap
        for idx, r in enumerate(db):
            s = overlap(words(fn.replace('.pdf', '')), db_words[idx])
            if s > score:
                score, matched, how = s, r, 'filename'
        if score < 0.6:
            matched, how = None, 'nomatch'

    status = f"{how}:{score:.2f}" if matched else f"NO-MATCH(doi={doi_found})"
    if matched:
        print(f"OK  [{status}] {fn[:58]}")
        print(f"     -> {matched['normalized_name'][:75]}")
    else:
        print(f"??  [{status}] {fn[:58]}")
        if title_guess:
            print(f"     meta-title: {title_guess[:80]}")
        head = ' '.join(first_text.split())[:100]
        if head:
            print(f"     page-head: {head}")
    results.append((fn, p, matched, how, score, doi_found))

# summary
ok = [x for x in results if x[2]]
print(f"\nmatched: {len(ok)} / {len(results)}")

if APPLY:
    for fn, p, rec, how, score, doi in ok:
        rec['pdf_manual'] = True
        if rec.get('pdf_downloaded') and rec.get('pdf_file') and os.path.exists(os.path.join(PDF_DIR, rec['pdf_file'])):
            continue  # already have it
        dst_name = re.sub(r'[<>:"/\\|?*]', '_', rec['normalized_name']) + '.pdf'
        dst = os.path.join(PDF_DIR, dst_name)
        if not os.path.exists(dst):
            shutil.copy2(p, dst)
        rec['pdf_file'] = dst_name
        rec['pdf_downloaded'] = True
    json.dump(db, open(os.path.join(BASE, 'literature_database.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied: copied to 01_PDF/ and DB updated')
    # list unmatched db records still without pdf
    still = [r for r in db if not r.get('pdf_downloaded')]
    print('DB records still without PDF:', len(still))
