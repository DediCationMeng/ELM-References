# -*- coding: utf-8 -*-
"""Consolidate Europe PMC + arXiv + web-found records into literature_database.json"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

def clean_title(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return " ".join(t.split())

epmc = json.load(open(os.path.join(BASE, "epmc_raw.json"), encoding="utf-8"))
arxiv = json.load(open(os.path.join(BASE, "arxiv_raw.json"), encoding="utf-8"))

records = {}
def upsert(rec):
    key = (rec.get("doi") or rec.get("title", "")).lower().replace(" ", "")
    if key in records:
        # merge topics
        old = records[key]
        for t in rec.get("topics", []):
            if t not in old["topics"]:
                old["topics"].append(t)
    else:
        records[key] = rec

for topic, items in epmc.items():
    for it in items:
        ji = it.get("journalInfo") or {}
        journal = (ji.get("journal") or {}).get("title", "")
        auths = (it.get("authorList") or {}).get("author", [])
        names = [a.get("fullName", "") for a in auths]
        corr = None
        for a in auths:
            if a.get("authorId") and not corr:
                pass
        # heuristic: last author is corresponding author in biomed
        if names:
            corr = names[-1]
        pubtypes = (it.get("pubTypeList") or {}).get("pubType", [])
        pdf_url = None
        for u in (it.get("fullTextUrlList") or {}).get("fullTextUrl", []):
            if u.get("documentStyle") == "pdf" and u.get("availability") in ("Open access", "Open access available", "Free"):
                pdf_url = u.get("url")
                break
            if not pdf_url and u.get("documentStyle") == "pdf":
                pdf_url = u.get("url")
        upsert({
            "source": "EuropePMC",
            "id": it.get("id"),
            "doi": it.get("doi"),
            "pmid": it.get("pmid"),
            "title": clean_title(it.get("title")),
            "journal": journal or (ji.get("journal", {}) or {}).get("medlineAbbreviation", "") or "Preprint",
            "journal_abbrev": (ji.get("journal", {}) or {}).get("medlineAbbreviation", "") or (journal[:30] if journal else "Preprint"),
            "date": it.get("firstPublicationDate"),
            "authors": names,
            "corresponding_author": corr,
            "abstract": " ".join(re.sub(r"<[^>]+>", " ", it.get("abstractText") or "").split()),
            "pubtypes": pubtypes,
            "is_oa": it.get("isOpenAccess") == "Y",
            "pdf_url": pdf_url,
            "topics": [topic],
        })

for topic, items in arxiv.items():
    for it in items:
        upsert({
            "source": "arXiv",
            "id": it["id"].split("/abs/")[-1],
            "doi": None,
            "title": clean_title(it["title"]),
            "journal": "arXiv preprint",
            "journal_abbrev": "arXiv",
            "date": it["published"],
            "authors": it["authors"],
            "corresponding_author": it["authors"][-1] if it["authors"] else None,
            "abstract": it["summary"],
            "pubtypes": ["Preprint"],
            "is_oa": True,
            "pdf_url": it["id"].replace("/abs/", "/pdf/"),
            "topics": [topic],
        })

# Records found via web search not yet in API sets
manual = [
    {"source": "Web", "title": "Volumetric 3D printing of microalgae-based engineered living materials",
     "journal": "Trends in Biotechnology", "journal_abbrev": "Trends Biotechnol", "date": "2026-09-08",
     "doi": None, "authors": ["Windisch et al."], "corresponding_author": None,
     "abstract": "Adaptation of volumetric 3D printing to photosynthetically active green microalgae-based engineered living materials (ELMs), addressing fabrication challenges of light scattering/absorption in cell-laden materials; expands fabrication toolbox for geometrically complex ELMs.",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM", "Bioprinting"]},
    {"source": "Web", "title": "Controlling viscoelastic behavior and microstructural organization in engineered living materials using synthetic adhesins and rheometry",
     "journal": "Acta Biomaterialia", "journal_abbrev": "Acta Biomater", "date": "2026-09-13",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Uses synthetic cell-cell adhesins to systematically characterize how rheological/viscoelastic properties of multicellular bacterial ELMs are tuned by adhesion strength, cell size, cell shape and adhesion logic; rheology used to shape microscopic structure of ELMs (cell aggregation, pore formation).",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM"]},
    {"source": "Web", "title": "Rewiring lactobacilli: challenges, opportunities, and the translational path to therapeutics",
     "journal": "review (see issue 2026-09-13)", "journal_abbrev": "Review", "date": "2026-09-10",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Review on genetic rewiring of Lactobacillus for therapeutic applications, covering challenges and translational path.",
     "pubtypes": ["Review"], "is_oa": False, "pdf_url": None, "topics": ["LBP", "Probiotics"]},
    {"source": "Web", "title": "Tailored living mycelium macerate for reproducible flexible actuators",
     "journal": "see issue 2026-09-13", "journal_abbrev": "Biofabrication", "date": "2026-09-12",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Living mycelium-based flexible actuators with tailored macerate for reproducible actuation; ELM application in soft robotics.",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM"]},
    {"source": "Web", "title": "Biohybrid microalgae living hydrogel with self-oxygenation and green-synthesized zinc nanoparticles to combat multidrug-resistant infections via transcriptional reprogramming",
     "journal": "see issue 2026-09-13", "journal_abbrev": "Biohybrid", "date": "2026-09-12",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Microalgae living hydrogel with self-oxygenation plus green-synthesized ZnO nanoparticles; combats MDR infections via transcriptional reprogramming.",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM", "LBP"]},
    {"source": "Web", "title": "Living Biohybrid Hydrogels for Co-Delivery of Oxygen, Anti-Cancer Drugs, and Probiotics: Effects on Cancer and Healthy Cell Viability",
     "journal": "see issue 2026-09-13", "journal_abbrev": "Biohybrid", "date": "2026-09-12",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Living biohybrid hydrogels co-delivering oxygen, anticancer drugs and probiotics; viability effects on cancer vs healthy cells.",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM", "LBP"]},
    {"source": "Web", "title": "Granular Hydrogel Composites as Matrices for Engineered Living Materials",
     "journal": "ACS Applied Polymer Materials", "journal_abbrev": "ACS Appl Polym Mater", "date": "2026-09-25",
     "doi": "10.1021/acsapm.6c03807", "authors": ["Adelani SO", "Riffe MB", "Burdick JA", "Bay RK"],
     "corresponding_author": "Bay RK",
     "abstract": "Granular hydrogel composite of hydrogel microparticles + E. coli + photo-crosslinkable polymer as ELM matrix; larger bacterial colonies with rough morphology; compressive modulus tunable by matrix composition; 3D printable, sustained bacterial release, chemotactic migration gradients fixable by crosslinking.",
     "pubtypes": ["Journal Article"], "is_oa": False, "pdf_url": None, "topics": ["ELM"]},
    {"source": "Web", "title": "The Archibiome: Extending Engineered Living Materials to Multiscale Built Environments",
     "journal": "Frontiers in Systems Biology", "journal_abbrev": "Front Syst Biol", "date": "2026-09-18",
     "doi": "10.3389/fsysb.2026.1943876", "authors": ["Sandak A", "Pajerski P", "Gubensek I", "Butina Ogorelec A", "Cernosa A"],
     "corresponding_author": "Sandak A",
     "abstract": "Opinion paper introducing 'archibiome' - extending ELMs from discrete material components to interconnected architectural environments; buildings as dynamic microbial ecosystems; addresses stability, environmental variability, biosafety, regulation.",
     "pubtypes": ["Review"], "is_oa": True, "pdf_url": "https://www.frontiersin.org/journals/systems-biology/articles/10.3389/fsysb.2026.1943876/pdf", "topics": ["ELM"]},
    {"source": "Web", "title": "A light-responsive engineered probiotic system to alleviate (NIR-triggered)",
     "journal": "Frontiers in Bioengineering and Biotechnology", "journal_abbrev": "Front Bioeng Biotechnol", "date": "2026-10-08",
     "doi": None, "authors": ["(see article)"], "corresponding_author": None,
     "abstract": "Near-infrared light-responsive engineered bacteria system with controllable release for disease alleviation (IBD model expected).",
     "pubtypes": ["Journal Article"], "is_oa": True, "pdf_url": "https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2026.1864003/pdf", "topics": ["Probiotics"]},
]
for m in manual:
    upsert(m)

lst = list(records.values())
lst.sort(key=lambda r: r.get("date") or "")
json.dump(lst, open(os.path.join(BASE, "literature_database.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total unique:", len(lst))
for r in lst:
    print(r["date"], "|", (r["journal_abbrev"] or "?")[:22], "|", r["title"][:95])
