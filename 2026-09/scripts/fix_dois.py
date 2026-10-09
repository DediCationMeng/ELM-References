"""Fix missing/wrong DOIs and journal metadata, then regenerate manifest + BibTeX."""
import json, re, ssl, time, urllib.request

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0'}


def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=H)
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                return r.read()
        except Exception as e:
            print('  retry', i + 1, str(e)[:45])
            time.sleep(6 * (i + 1))
    return None


db = json.load(open('literature_database.json', encoding='utf-8'))

# --- 1) Cartilage paper: get formal DOI from PMC page meta ---
for r in db:
    if 'Cartilage-targeting' in r['title']:
        raw = fetch('https://pmc.ncbi.nlm.nih.gov/articles/PMC13635493/')
        if raw:
            html = raw.decode('utf-8', 'ignore')
            dois = re.findall(r'10\.1016/[A-Za-z0-9.\-/]+', html)
            print('cartilage DOI candidates:', sorted(set(dois))[:8])
            for d in sorted(set(dois)):
                if 'mtbio' in d.lower():
                    r['doi'] = d
                    print('CARTILAGE DOI ->', d)
                    break
            else:
                if dois:
                    r['doi'] = sorted(set(dois))[0]
                    print('CARTILAGE DOI (fallback) ->', r['doi'])
            t = re.search(r'<title>(.*?)</title>', html, re.S)
            if t:
                print('PMC page title:', ' '.join(t.group(1).split())[:110])
        # correct journal metadata
        r['journal'] = 'Materials Today Bio'
        r['journal_abbrev'] = 'Mater Today Bio'
        # SSRN preprint DOI is wrong for this record
        if (r.get('doi') or '').startswith('10.2139'):
            print('dropping SSRN preprint DOI for cartilage paper')
            r['doi'] = None

# --- 2) Frontiers paper: fix truncated title + assign DOI ---
for r in db:
    if r['title'].startswith('A light-responsive engineered probiotic system'):
        r['title'] = 'A light-responsive engineered probiotic system to alleviate anxiety via gut-brain axis'
        r['doi'] = '10.3389/fbioe.2026.1864003'
        r['journal'] = 'Frontiers in Bioengineering and Biotechnology'
        r['journal_abbrev'] = 'Front Bioeng Biotechnol'
        print('FRONTIERS fixed ->', r['title'][:80], '|', r['doi'])

# --- 3) Correct journal metadata from verified CrossRef matches ---
journal_fix = {
    'Rewiring lactobacilli': ('Current Opinion in Microbiology', 'Curr Opin Microbiol'),
    'Tailored living mycelium': ('Nature Communications', 'Nat Commun'),
    'Biohybrid microalgae living hydrogel': ('Colloids and Surfaces B: Biointerfaces', 'Colloids Surf B'),
    'Living Biohybrid Hydrogels for Co': ('Macromolecular Bioscience', 'Macromol Biosci'),
    'Volumetric 3D printing of microalgae': ('Trends in Biotechnology', 'Trends Biotechnol'),
    'Controlling viscoelastic behavior': ('Acta Biomaterialia', 'Acta Biomater'),
    'Spectroscopic Insights into Nutrient': ('Langmuir', 'Langmuir'),
}
for r in db:
    for pref, (j, ja) in journal_fix.items():
        if r['title'].startswith(pref):
            r['journal'] = j
            r['journal_abbrev'] = ja

json.dump(db, open('literature_database.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('missing DOI after fix:', sum(1 for r in db if not r.get('doi')))
for r in db:
    if not r.get('doi'):
        print('  STILL MISSING:', r['title'][:90])
