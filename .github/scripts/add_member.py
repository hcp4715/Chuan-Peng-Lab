#!/usr/bin/env python3
"""从成员提交区自动添加成员（en/zh）。

用法:
    python .github/scripts/add_member.py templates/member/ [--dry-run]
    python .github/scripts/add_member.py templates/member/xxx.md [--dry-run]

- 扫描提交区内所有 .md（跳过 _done/）；逐个解析 front matter
- 自动对比 content/{en,zh}/project/ 是否已存在同名/同文件夹成员，已存在则跳过
- 未添加则生成 en/zh 文件夹，并把提交区同名 featured.* 图片一并复制
- 处理成功的文件移到提交区 _done/ 子目录
"""

import argparse
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALLOWED_ROLES = {
    "Principal Investigator", "Research Assistants",
    "Postgraduate", "Undergraduate", "Alumni",
}


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
        return None, None
    end = txt.find("\n---", 3)
    if end == -1:
        return None, None
    fm = txt[3:end]
    body = txt[end + 4:].lstrip("\n")
    try:
        return load_yaml(fm), body
    except SystemExit:
        return None, None


def find_md_files(target):
    if os.path.isdir(target):
        return [os.path.join(target, f) for f in sorted(os.listdir(target))
                if f.endswith(".md") and not f.startswith("_")], True
    return [target], False


def derive_folder(name_en):
    tokens = name_en.strip().split()
    if len(tokens) >= 2:
        return "".join(t.strip().replace("-", "") for t in [tokens[-1]] + tokens[:-1])
    return "".join(t.strip().replace("-", "") for t in tokens)


def member_exists(folder, name_en, name_zh):
    for lang in ("en", "zh"):
        base = os.path.join(ROOT, "content", lang, "project")
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            if d == folder:
                return True
            idx = os.path.join(base, d, "index.md")
            if os.path.exists(idx):
                try:
                    t = open(idx, encoding="utf-8").read()
                except Exception:
                    continue
                if (name_en and name_en in t) or (name_zh and name_zh in t):
                    return True
    return False


def build_index(data, body, lang):
    name = data["name_en"] if lang == "en" else data["name_zh"]
    start = data.get("start") or "Now"
    links = []
    if data.get("github"):
        links.append(f'- icon: github\n  icon_pack: fab\n  name: Follow\n  url: https://github.com/{data["github"]}')
    if data.get("twitter"):
        links.append(f'- icon: twitter\n  icon_pack: fab\n  name: Follow\n  url: https://twitter.com/{data["twitter"]}')
    links_block = "links:\n" + "\n".join(links) if links else "links:"
    return f"""---
date: "{data.get('date', '2026-01-01')}T00:00:00Z"
external_link: ""
image:
  caption: {name}
  focal_point: Smart
{links_block}
slides: example
summary: __{start} ~ Now__ <br/> 
tags:
- {data['role']}
title: {name}
url_code: ""
url_pdf: ""
url_slides: ""
url_video: ""
---
{body}
"""


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
    ap.add_argument("target", help="提交区目录（templates/member/）或单个 md 文件")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files, is_dir = find_md_files(args.target)
    if not files:
        sys.exit(f"ERROR: {args.target} 下没有 .md 文件")
    if is_dir:
        print(f"扫描提交区，发现 {len(files)} 个 .md 文件")

    for path in files:
        data, body = parse_md(path)
        if data is None:
            print(f"跳过（无有效 front matter）: {path}")
            continue
        name_en = (data.get("name_en") or "").strip()
        name_zh = (data.get("name_zh") or "").strip()
        role = (data.get("role") or "").strip()
        if not name_en or not name_zh or not role:
            print(f"跳过（缺少 name_en/name_zh/role）: {path}")
            continue
        if role not in ALLOWED_ROLES:
            print(f"跳过（非法角色 {role}）: {path}")
            continue
        folder = (data.get("folder") or "").strip() or derive_folder(name_en)
        if not re.match(r"^[A-Z][A-Za-z]+$", folder):
            print(f"跳过（文件夹名非法 {folder}）: {path}，请在模板填 folder 字段")
            continue
        if member_exists(folder, name_en, name_zh):
            print(f"跳过（已存在）: {name_en} / {name_zh}")
            continue
        print(f"添加成员: {name_en} ({name_zh}) -> {folder}/")
        if args.dry_run:
            print("  [DRY-RUN] 不写入")
            continue
        for lang in ("en", "zh"):
            d = os.path.join(ROOT, "content", lang, "project", folder)
            os.makedirs(d, exist_ok=False)
            with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
                f.write(build_index(data, body, lang))
            imgs = copy_images(os.path.dirname(path), d, os.path.splitext(os.path.basename(path))[0])
            print(f"  ✓ {lang}/project/{folder}/" + (f" (+图片 {imgs})" if imgs else ""))
        if is_dir:
            done = os.path.join(os.path.dirname(path), "_done")
            moved = archive_files(os.path.dirname(path), done, path)
            print(f"  → 已归档到 {done}: {moved}")

    print("\n完成。请运行 front matter 校验与中英同步检查。")


if __name__ == "__main__":
    main()
