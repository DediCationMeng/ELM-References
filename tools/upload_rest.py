# -*- coding: utf-8 -*-
"""Upload ELM-References to GitHub via REST API (api.github.com) using a fine-grained PAT.
Single atomic commit via Git Data API (blobs -> tree -> commit -> ref).
Token source: env GITHUB_TOKEN, or a local token file path as argv[1]."""
import base64, json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OWNER, REPO, BRANCH = 'DediCationMeng', 'ELM-References', 'main'
API = 'https://api.github.com'

def get_token():
    t = os.environ.get('GITHUB_TOKEN')
    if t:
        return t.strip()
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return open(sys.argv[1], encoding='utf-8').read().strip()
    sys.exit('missing token: set GITHUB_TOKEN or pass a token file path')

TOKEN = get_token()

def api(method, path, payload=None):
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
        'User-Agent': 'elm-uploader',
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read() or b'{}')
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'ignore')[:300]
            if e.code in (429, 502, 503) and attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError(f'{e.code} {method} {path}: {body}')
        except urllib.error.URLError:
            if attempt < 3:
                time.sleep(3 * (attempt + 1))
                continue
            raise

def collect_files():
    out = []
    skip = {'.git', '__pycache__'}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in sorted(files):
            if f in ('upload_rest.py', 'push_via_connector.py', 'probe_write.py'):
                continue  # tooling, not project content
            p = os.path.join(root, f)
            rel = os.path.relpath(p, ROOT).replace('\\', '/')
            out.append((rel, p))
    return sorted(out)

files = collect_files()
print(f'uploading {len(files)} files to {OWNER}/{REPO}@{BRANCH} ...')

# empty repos reject git/blobs (409) -> create the initial commit via Contents API first
head_sha = None
try:
    ref = api('GET', f'/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}')
    head_sha = ref['object']['sha']
    empty = False
except RuntimeError:
    empty = True

if empty:
    with open(os.path.join(ROOT, 'README.md'), 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode('ascii')
    res = api('PUT', f'/repos/{OWNER}/{REPO}/contents/README.md',
              {'message': 'Initialize ELM-References', 'content': b64, 'branch': BRANCH})
    head_sha = res['commit']['sha']
    print('initial commit created (empty repo bootstrap)')

tree = []
for rel, p in files:
    with open(p, 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode('ascii')
    blob = api('POST', f'/repos/{OWNER}/{REPO}/git/blobs', {'content': b64, 'encoding': 'base64'})
    tree.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    print('  blob ok:', rel)

tr = api('POST', f'/repos/{OWNER}/{REPO}/git/trees', {'tree': tree})
commit = api('POST', f'/repos/{OWNER}/{REPO}/git/commits', {
    'message': 'ELM literature library: 2026-09 monthly archive (66 papers: BibTeX, reports, checklist, pipeline scripts, metadata)',
    'tree': tr['sha'],
    'parents': [head_sha] if head_sha else [],
})
try:
    api('POST', f'/repos/{OWNER}/{REPO}/git/refs', {'ref': f'refs/heads/{BRANCH}', 'sha': commit['sha']})
    print('branch created')
except RuntimeError as e:
    if '422' in str(e):  # ref exists -> update
        try:
            api('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}', {'sha': commit['sha']})
        except RuntimeError as e2:
            if 'fast forward' in str(e2):
                api('PATCH', f'/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}',
                    {'sha': commit['sha'], 'force': True})
            else:
                raise
        print('branch updated')
    else:
        raise
print('DONE ->', f'https://github.com/{OWNER}/{REPO}')
