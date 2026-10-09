# -*- coding: utf-8 -*-
"""Restore literature_database.json after corruption, replaying the full correction chain offline.
Pipeline: build_db -> offline DOI/title/journal fixes -> manifest/naming -> PDF state -> checklist."""
import json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
PY = r'C:\Users\MZR\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe'
VENV_PY = r'C:\Users\MZR\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe'

def run(script, py=PY, args=()):
    print(f'--- run {script} ---')
    r = subprocess.run([py, os.path.join(BASE, script), *args], capture_output=True, text=True, cwd=BASE)
    print((r.stdout or '').strip()[-600:])
    if r.returncode != 0:
        print((r.stderr or '')[-800:])
        sys.exit(1)

# 1) rebuild base DB from raw API dumps
run('build_db.py')

# 2) offline fixes (previously verified via CrossRef/PMC)
db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
FIXES = {
    'Volumetric 3D printing of microalgae': {'doi': '10.1016/j.tibtech.2026.08.016'},
    'An Automated Thickness Evaluation': {'doi': '10.48550/arXiv.2609.12206'},
    'A Physics-Based Closed-Loop Robotic Bioprinting': {'doi': '10.48550/arXiv.2609.12159'},
    'Rewiring lactobacilli': {'doi': '10.1016/j.mib.2026.102826',
                              'journal': 'Current Opinion in Microbiology', 'journal_abbrev': 'Curr Opin Microbiol'},
    'Tailored living mycelium macerate': {'doi': '10.1038/s41467-026-76623-z',
                                          'journal': 'Nature Communications', 'journal_abbrev': 'Nat Commun'},
    'Biohybrid microalgae living hydrogel': {'doi': '10.1016/j.colsurfb.2026.116142',
                                             'journal': 'Colloids and Surfaces B: Biointerfaces', 'journal_abbrev': 'Colloids Surf B'},
    'Living Biohybrid Hydrogels for Co': {'doi': '10.1002/mabi.70233',
                                          'journal': 'Macromolecular Bioscience', 'journal_abbrev': 'Macromol Biosci'},
    'Controlling viscoelastic behavior': {'doi': '10.1016/j.actbio.2026.08.044'},
    'Spectroscopic Insights into Nutrient': {'doi': '10.1021/acs.langmuir.6c01932'},
    'Cartilage-targeting engineered probiotic': {'doi': '10.1016/j.mtbio.2026.103668',
                                                 'journal': 'Materials Today Bio', 'journal_abbrev': 'Mater Today Bio'},
    'A light-responsive engineered probiotic': {
        'doi': '10.3389/fbioe.2026.1864003',
        'title': 'A light-responsive engineered probiotic system to alleviate anxiety via gut-brain axis',
        'abstract': 'Near-infrared light-responsive engineered probiotic system with controllable release; alleviates anxiety-like behavior via the gut-brain axis.'},
}
for r in db:
    for pref, fx in FIXES.items():
        if r['title'].startswith(pref):
            r.update(fx)
json.dump(db, open(os.path.join(BASE, 'literature_database.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('offline fixes applied; missing DOI:', sum(1 for r in db if not r.get('doi')))

# 3) regenerate normalized names + BibTeX + manifest
run('build_manifest_bib.py')

# 4) restore PDF state from 01_PDF/ contents
db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
pdf_dir = os.path.join(BASE, '01_PDF')
files = set(os.listdir(pdf_dir))
for r in db:
    dst = re.sub(r'[<>:"/\\|?*]', '_', r['normalized_name']) + '.pdf'
    if dst in files:
        r['pdf_downloaded'] = True
        r['pdf_file'] = dst
json.dump(db, open(os.path.join(BASE, 'literature_database.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('pdf state restored from 01_PDF:', sum(1 for r in db if r.get('pdf_downloaded')), '/', len(db))

# 5) mark manual downloads (matches today's Downloads PDFs; copy is skipped if already present)
run('import_manual_pdfs.py', py=VENV_PY, args=('--apply',))

# 6) rebuild the checklist (reads previous user marks)
run('rebuild_checklist.py')

db = json.load(open(os.path.join(BASE, 'literature_database.json'), encoding='utf-8'))
print('FINAL: records', len(db), '| with DOI', sum(1 for r in db if r.get('doi')),
      '| with PDF', sum(1 for r in db if r.get('pdf_downloaded')),
      '| manual', sum(1 for r in db if r.get('pdf_manual')))
