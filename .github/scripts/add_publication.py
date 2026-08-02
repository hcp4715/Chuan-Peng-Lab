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


# ---------- 成员自动关联 ----------
PI_FOLDER = "HuChuanpeng"  # PI 不参与自动关联


def _cjk_tokens(v):
    return re.findall(r"[a-z0-9\u4e00-\u9fff]+", v)


def member_variants(folder, title):
    """从成员文件夹名 + 页面 title 生成归一化姓名变体集合。

    处理 'YuKi (Mengzhen Hu)' / 'Helen (Zheng Liu)' 这类别名格式：
    括号内外都提取，并补上"姓在前后/名在前后"两种顺序。
    """
    out = {normalize(folder)}
    base = re.sub(r"\([^)]*\)", "", title or "").strip()
    aliases = re.findall(r"\(([^)]*)\)", title or "")
    for part in [base] + aliases:
        part = part.strip()
        if len(part) < 2:
            continue
        v = normalize(part)
        out.add(v)
        words = _cjk_tokens(v)
        if len(words) >= 2:
            out.add(words[-1] + "".join(words[:-1]))
        for w in part.split():
            wv = normalize(w)
            if len(wv) >= 2 and any("\u4e00" <= c <= "\u9fff" for c in w):
                out.add(wv)
    return out


def build_member_registry():
    """读取 content/{en,zh}/project/ 下所有成员，构建 folder -> 姓名变体集。排除 PI。"""
    registry = {}
    for lang in ("en", "zh"):
        base = os.path.join(ROOT, "content", lang, "project")
        if not os.path.isdir(base):
            continue
        for folder in os.listdir(base):
            if folder == PI_FOLDER:
                continue
            idx = os.path.join(base, folder, "index.md")
            if not os.path.isfile(idx):
                continue
            fm = parse_md(idx)
            if not fm:
                continue
            registry.setdefault(folder, set()).update(
                member_variants(folder, fm.get("title", "")))
    return registry


def is_abbrev(name):
    """判断作者名是否只有首字母缩写（如 'Liu, Y'、'Duan S'、'Hu, C-P'、'Chuan-Peng, H'）。"""
    given = name.split(",", 1)[1] if "," in name else name
    toks = [t for t in re.split(r"[\s\-\.]+", given) if t]
    return any(len(t) == 1 for t in toks)


def family_name(name):
    if "," in name:
        return name.split(",")[0].strip()
    words = name.split()
    if not words:
        return ""
    if len(words) >= 2 and len(words[-1]) == 1:
        return words[0]
    return words[-1]


def name_variants(author):
    """生成作者名的归一化变体（兼容 'Family, Given' 与 'Given Family' 两种写法）。"""
    out = set()
    if "," in author:
        parts = [p.strip() for p in author.split(",")]
        family, given = parts[0], "".join(parts[1:]).strip()
        if family and given:
            out.add(normalize(family + given))
            out.add(normalize(given + family))
    else:
        v = normalize(author)
        out.add(v)
        words = _cjk_tokens(v)
        if len(words) >= 2:
            out.add(words[-1] + "".join(words[:-1]))
    return out


def match_members(authors, registry):
    """返回 (matched_folder列表, hints)：
    - matched：全名匹配成功的成员文件夹（自动写入 projects）
    - hints：缩写作者 -> 可能的成员（仅提示，不自动关联）
    """
    matched, hints = [], []
    for author in (authors or []):
        author = (author or "").strip()
        if not author:
            continue
        if is_abbrev(author):
            fam = normalize(family_name(author))
            cands = [f for f, mv in registry.items()
                     if len(fam) >= 2 and any(v.startswith(fam) for v in mv)]
            if cands:
                hints.append((author, cands))
            continue
        hits = [f for f, mv in registry.items() if name_variants(author) & mv]
        for f in hits:
            if f not in matched:
                matched.append(f)
    return matched, hints


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


def build_index(data, cr, folder, projects=None):
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
    projects_field = ('projects: ""' if not projects
                      else "projects:\n" + "\n".join(f"- {p}" for p in projects))
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
{projects_field}
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

    registry = build_member_registry()
    print(f"成员注册表: {len(registry)} 人（已排除 PI）")

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
        matched, hints = match_members(data["authors"], registry)
        if matched:
            print(f"  ✦ 自动关联成员: {', '.join(matched)}")
        for author, cands in hints:
            print(f"  ? 作者缩写 {author!r} 可能对应: {', '.join(cands)}（未自动关联，请人工确认）")
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
                f.write(build_index(data, cr, folder, matched))
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
