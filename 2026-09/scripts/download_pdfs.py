# -*- coding: utf-8 -*-
"""Download open-access PDFs via Unpaywall + direct links; produce download checklist."""
import json, os, re, time, urllib.request, ssl, csv

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE, "01_PDF")
os.makedirs(PDF_DIR, exist_ok=True)

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
db = json.load(open(os.path.join(BASE, "literature_database.json"), encoding="utf-8"))

def safe_name(s, maxlen=80):
    s = re.sub(r'[<>:"/\\\\|?*]', "_", s)
    return s[:maxlen].strip()

def unpaywall(doi):
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=research@example.com"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            d = json.loads(r.read().decode())
        best = d.get("best_oa_location") or {}
        return best.get("url_for_pdf"), d.get("is_oa"), d.get("oa_status")
    except Exception as e:
        return None, None, str(e)[:60]

import urllib.parse

results = []
for i, rec in enumerate(db):
    title = rec["title"]
    doi = rec.get("doi")
    pdf, is_oa, status = (None, rec.get("is_oa"), None)
    if doi:
        pdf, is_oa, status = unpaywall(doi)
    if not pdf:
        pdf = rec.get("pdf_url")
    fn = None
    downloaded = False
    if pdf:
        try:
            req = urllib.request.Request(pdf, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                data = r.read()
            if data[:4] == b"%PDF":
                tag = rec.get("date", "")[:7].replace("-", "")
                fn = f"{tag}_{safe_name(title)}.pdf"
                open(os.path.join(PDF_DIR, fn), "wb").write(data)
                downloaded = True
                print(f"[{i}] OK {fn[:70]} ({len(data)//1024} KB)")
            else:
                print(f"[{i}] NOT-PDF: {title[:50]}")
        except Exception as e:
            print(f"[{i}] FAIL {title[:50]} | {str(e)[:60]}")
        time.sleep(1)
    rec["pdf_file"] = fn
    rec["pdf_downloaded"] = downloaded
    rec["oa_status"] = status
    results.append({"title": title, "doi": doi, "pdf_url": pdf, "downloaded": downloaded, "file": fn, "oa_status": status})

json.dump(db, open(os.path.join(BASE, "literature_database.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ok = [r for r in results if r["downloaded"]]
need = [r for r in results if not r["downloaded"]]
print(f"\nDownloaded: {len(ok)} / {len(results)}; Need manual: {len(need)}")
json.dump({"downloaded": ok, "manual": need}, open(os.path.join(BASE, "download_status.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
