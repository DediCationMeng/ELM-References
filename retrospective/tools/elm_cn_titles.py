# -*- coding: utf-8 -*-
"""中文译名工具：打印题名供翻译 / 合并译名 TSV 生成 cn_titles.json。

用法：
  python tools/elm_cn_titles.py print --year 2020
      打印该年 kept 记录（按 date,title 排序）的 index 与完整英文题名
  python tools/elm_cn_titles.py merge
      读取 03_Reports/cn_work/cn_YYYY.tsv（每行 "index<TAB>中文译名"），
      键=题名前 25 字符词头（elm_export_bib.cn_of 用 title.startswith(k) 匹配），
      合并写出 cn_titles.json
"""
import argparse, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_LEN = 25


def load_year(year):
    db = json.load(open(os.path.join(BASE, "literature_database.json"), encoding="utf-8"))
    y = [r for r in db if (r.get("date") or "").startswith(str(year))]
    y.sort(key=lambda r: ((r.get("date") or ""), (r.get("title") or "")))
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["print", "merge"])
    ap.add_argument("--year", type=int, default=None)
    args = ap.parse_args()

    if args.cmd == "print":
        for i, r in enumerate(load_year(args.year), 1):
            rev = any("review" in p.lower() for p in (r.get("pubtypes") or []))
            print(f"{i}\t{'R' if rev else 'S'}\t{r.get('title')}")
        return

    # merge
    cn = {}
    total = 0
    for yr in range(2020, 2027):
        tsv = os.path.join(BASE, "03_Reports", "cn_work", f"cn_{yr}.tsv")
        if not os.path.exists(tsv):
            print(f"!! missing {tsv}")
            continue
        y = load_year(yr)
        trans = {}
        for line in open(tsv, encoding="utf-8-sig"):
            line = line.rstrip("\n")
            if not line.strip() or "\t" not in line:
                continue
            idx, zh = line.split("\t", 1)
            trans[int(idx.strip())] = zh.strip()
        missing = [i for i in range(1, len(y) + 1) if i not in trans]
        if missing:
            print(f"!! {yr}: missing index {missing[:10]}... ({len(missing)})")
        for i, r in enumerate(y, 1):
            if i in trans:
                t = (r.get("title") or "").strip()
                key = t[:KEY_LEN]
                while key in cn and cn[key] != trans[i] and len(key) < len(t):
                    key = t[:len(key) + 5]
                if key and key not in cn:
                    cn[key] = trans[i]
        total += len(trans)
        print(f"{yr}: {len(trans)} translations")

    out = os.path.join(BASE, "cn_titles.json")
    json.dump(cn, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"cn_titles.json written: {len(cn)} entries (from {total} translations)")


if __name__ == "__main__":
    main()
