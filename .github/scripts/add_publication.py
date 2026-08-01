#!/usr/bin/env python3
"""从论文提交区自动添加论文（en/zh，含 Crossref 自动补全）。

用法:
    python .github/scripts/add_publication.py templates/publication/ [--dry-run]
    python .github/scripts/add_publication.py templates/publication/xxx.md [--dry-run]

- 扫描提交区内所有 .md（跳过 _done/）；逐个解析 front matter
- 自动对比 content/{en,zh}/publication/ 是否已存在同 DOI/同标题论文，已存在则跳过
- 用 DOI 查 Crossref 补全卷期号/年份/摘要（并校验标题是否匹配）
- 生成 en/zh 文件夹（index.md + cite.bib），提交区同名 featured.* 图片一并复制
- 处理成功的文件移到提交区 _done/ 子目录
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TYPE_MAP = {"journal": "2", "preprint": "3"}
UA = "ChuanPengLabAddPub/1.0 (mailto:admin@example.com)"


def load_yaml(fm_text):
    try:
        import yaml
    except ImportError:
        sys.exit("ERROR: 需要 PyYAML（用 /tmp/opencode/ci-venv/bin/python 运行）")
    try:
        data = yaml.safe_load(fm_text)
    except Exception as e:
        sys.exit(f"ERROR: front matter 解析失败: {e}")
    if not isinstance(data, dict):
        sys.exit("ERROR: front matter 必须是一个映射（键值对）")
    return data


def parse_md(path):
    txt = open(path, encoding="utf-8").read()
    if not txt.startswith("---"):
        return None
    end = txt.find("\n---", 3)
    if end == -1:
        return None
    try:
        return load_yaml(txt[3:end])
    except SystemExit:
        return None


def find_md_files(target):
    if os.path.isdir(target):
        return [os.path.join(target, f) for f in sorted(os.listdir(target))
                if f.endswith(".md") and not f.startswith("_")], True
    return [target], False


def query_crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    for _ in range(3):
        r = os.popen(f'curl -s --max-time 15 "{url}" -H "User-Agent: {UA}"').read()
        time.sleep(0.5)
        try:
            return json.loads(r)["message"]
        except Exception:
            continue
    return None


def normalize(s):
    s = (s or "").lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", s)


def surname_of(author):
    a = author.strip()
    if "," in a:
        return a.split(",")[0].strip()
    return a.split()[-1].strip() if a.split() else ""


def clean_abstract(raw):
    raw = re.sub(r"<[^>]+>", " ", raw or "")
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')):
        raw = raw.replace(a, b)
    return re.sub(r"\s+", " ", raw).strip()


def pub_exists(data):
    doi = (data.get("doi") or "").strip().lower()
    title = normalize(data.get("title"))
    for lang in ("en", "zh"):
        base = os.path.join(ROOT, "content", lang, "publication")
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            idx = os.path.join(base, d, "index.md")
            if not os.path.exists(idx):
                continue
            t = open(idx, encoding="utf-8").read()
            if doi and doi in t.lower():
                return True
            if title and title and title in normalize(t):
                return True
    return False


def make_folder(data, cr):
    year = data.get("year") or (str(cr.get("issued", {}).get("date-parts", [[None]])[0][0]) if cr else "")
    if not year:
        return None, "缺少 year（且 Crossref 无法确定）"
    prefix = "Publication" if data["type"] == "journal" else "Preprint"
    base = f"{year}_{prefix}_{surname_of(data['authors'][0])}"
    folder = base
    n = 2
    while os.path.exists(os.path.join(ROOT, "content", "en", "publication", folder)):
        folder = f"{base}_{n}"
        n += 1
    return folder, None


def build_index(data, cr, folder):
    title = data["title"]
    abstract = clean_abstract(data.get("abstract") or (cr.get("abstract", "") if cr else ""))
    doi = (data.get("doi") or "").strip()
    journal = data.get("journal") or (cr.get("container-title", [""])[0] if cr else "")
    pubtype = TYPE_MAP[data["type"]]
    year = data.get("year") or (str(cr.get("issued", {}).get("date-parts", [[None]])[0][0]) if cr else "")
    pub = "Preprint" if data["type"] == "preprint" else f"In *{journal}*"
    authors = "\n".join(f"- {a.strip()}" for a in data["authors"])
    date = f"{year}-01-01T00:00:00Z"
    url_source = data.get("url_source") or (cr.get("URL", "") if cr else "")
    return f"""---
abstract: "{abstract}"
authors:
{authors}
date: "{date}"
doi: "{doi}"
featured: false
image:
  caption: ''
  focal_point: ""
  preview_only: false
projects: ""
publication: {pub}
publication_short: {pub}
publication_types:
- "{pubtype}"
publishDate: "{date}"
slides: example
summary: "{abstract[:200]}"
tags: []
title: "{title}"
url_code: ""
url_dataset: ""
url_pdf: ""
url_poster: ""
url_project: ""
url_slides: ""
url_source: "{url_source}"
url_video: ""
---

{{% callout note %}}
Click the _Cite_ button above to demo the feature to enable visitors to import publication metadata into their reference management software.
{{% /callout %}}
"""


def build_citebib(data, cr, folder):
    entry = "misc" if data["type"] == "preprint" else "article"
    auth = " and ".join(a.strip() for a in data["authors"])
    bib = [f"@{entry}{{{folder},", f"  title = {{{data['title']}}},",
           f"  author = {{{auth}}},"]
    if data["type"] == "journal":
        bib.append(f"  journal = {{{data.get('journal') or ''}}},")
    if cr and cr.get("volume"):
        bib.append(f"  volume = {{{cr['volume']}}},")
    if cr and cr.get("issue"):
        bib.append(f"  number = {{{cr['issue']}}},")
    if cr and cr.get("page"):
        bib.append(f"  pages = {{{cr['page']}}},")
    if data.get("doi"):
        bib.append(f"  doi = {{{data['doi']}}},")
    year = data.get("year") or (str(cr.get("issued", {}).get("date-parts", [[None]])[0][0]) if cr else "")
    bib.append(f"  year = {{{year}}},")
    if data.get("url_source"):
        bib.append(f"  url = {{{data['url_source']}}},")
    bib.append("}")
    return "\n".join(bib) + "\n"


def copy_images(src_dir, dest_dir, basename):
    copied = []
    for c in ("featured.jpg", "featured.png", "featured.jpeg",
              basename + ".jpg", basename + ".png", basename + ".jpeg"):
        p = os.path.join(src_dir, c)
        if os.path.exists(p):
            ext = os.path.splitext(c)[1]
            shutil.copy(p, os.path.join(dest_dir, "featured" + ext))
            copied.append(c)
    return copied


def archive_files(src_dir, done_dir, path):
    os.makedirs(done_dir, exist_ok=True)
    moved = [os.path.basename(path)]
    shutil.move(path, os.path.join(done_dir, os.path.basename(path)))
    base = os.path.splitext(os.path.basename(path))[0]
    for c in ("featured.jpg", "featured.png", "featured.jpeg",
              base + ".jpg", base + ".png", base + ".jpeg"):
        p = os.path.join(src_dir, c)
        if os.path.exists(p):
            shutil.move(p, os.path.join(done_dir, c))
            moved.append(c)
    return moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="提交区目录（templates/publication/）或单个 md 文件")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files, is_dir = find_md_files(args.target)
    if not files:
        sys.exit(f"ERROR: {args.target} 下没有 .md 文件")
    if is_dir:
        print(f"扫描提交区，发现 {len(files)} 个 .md 文件")

    for path in files:
        data = parse_md(path)
        if data is None:
            print(f"跳过（无有效 front matter）: {path}")
            continue
        if not data.get("title") or data.get("type") not in TYPE_MAP or not data.get("authors"):
            print(f"跳过（缺少 title/type/authors）: {path}")
            continue
        if pub_exists(data):
            print(f"跳过（已存在相同 DOI/标题）: {data['title'][:60]}")
            continue
        print(f"处理论文: {data['title'][:60]}...")
        cr = None
        if data.get("doi"):
            print("  查询 Crossref...")
            cr = query_crossref(data["doi"])
            if cr is None:
                print(f"  WARN: DOI {data['doi']} 在 Crossref 无记录，按模板内容生成")
            elif normalize(cr.get("title", [""])[0]) and normalize(data["title"]) != normalize(cr.get("title", [""])[0]):
                print(f"  WARN: DOI 标题与模板不一致！\n    Crossref: {(cr.get('title') or [''])[0][:60]}\n    模板:    {data['title'][:60]}")
        folder, err = make_folder(data, cr)
        if err:
            print(f"  跳过: {err}")
            continue
        print(f"  → {folder}/")
        if args.dry_run:
            print("  [DRY-RUN] 不写入")
            continue
        for lang in ("en", "zh"):
            d = os.path.join(ROOT, "content", lang, "publication", folder)
            os.makedirs(d, exist_ok=False)
            with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
                f.write(build_index(data, cr, folder))
            with open(os.path.join(d, "cite.bib"), "w", encoding="utf-8") as f:
                f.write(build_citebib(data, cr, folder))
            imgs = copy_images(os.path.dirname(path), d, os.path.splitext(os.path.basename(path))[0])
            print(f"  ✓ {lang}/publication/{folder}/" + (f" (+图片 {imgs})" if imgs else ""))
        if is_dir:
            done = os.path.join(os.path.dirname(path), "_done")
            moved = archive_files(os.path.dirname(path), done, path)
            print(f"  → 已归档到 {done}: {moved}")

    print("\n完成。请运行 front matter 校验与中英同步检查。")


if __name__ == "__main__":
    main()
