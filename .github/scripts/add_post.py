#!/usr/bin/env python3
"""从博客提交区自动添加博客文章。

用法:
    python .github/scripts/add_post.py templates/post/ [--dry-run]
    python .github/scripts/add_post.py templates/post/xxx.md [--dry-run]

front matter: title / date(YYYY-MM-DD) / summary / tags / bilingual(true|false)
- bilingual=true  : 创建 content/{en,zh}/post/{date}-{slug}/index.md
- bilingual=false : 只创建英文版，并自动把差异加入 .github/scripts/i18n_allowlist.txt
- 自动对比是否已存在同 date-title 文章；提交区同名图片一并复制；处理完归档到 _done/
"""

import argparse
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALLOWLIST = os.path.join(ROOT, ".github", "scripts", "i18n_allowlist.txt")


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
    try:
        return load_yaml(txt[3:end]), txt[end + 4:].lstrip("\n")
    except SystemExit:
        return None, None


def find_md_files(target):
    if os.path.isdir(target):
        return [os.path.join(target, f) for f in sorted(os.listdir(target))
                if f.endswith(".md") and not f.startswith("_")], True
    return [target], False


def slugify(title):
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", title.strip().lower()).strip("-")
    return s or "post"


def post_exists(folder):
    for lang in ("en", "zh"):
        if os.path.exists(os.path.join(ROOT, "content", lang, "post", folder)):
            return True
    return False


def build_index(data, body):
    tags = "\n".join(f"- {t}" for t in (data.get("tags") or []))
    return f"""---
title: {data['title']}
date: "{data['date']}T00:00:00Z"
summary: {data.get('summary', '')}
tags:
{tags}
---
{body}
"""


def add_allowlist(line):
    if not os.path.exists(ALLOWLIST):
        open(ALLOWLIST, "w", encoding="utf-8").write("")
    cur = open(ALLOWLIST, encoding="utf-8").read()
    if line not in cur:
        with open(ALLOWLIST, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(f"  ✓ 已加入豁免名单: {line}")


def copy_images(src_dir, dest_dir, basename):
    copied = []
    for c in sorted(os.listdir(src_dir)):
        if c.startswith("_") or not os.path.isfile(os.path.join(src_dir, c)):
            continue
        if c.lower().endswith((".jpg", ".png", ".jpeg", ".gif", ".webp", ".svg")):
            shutil.copy(os.path.join(src_dir, c), os.path.join(dest_dir, c))
            copied.append(c)
    return copied


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="提交区目录（templates/post/）或单个 md 文件")
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
        if not data.get("title") or not re.match(r"^\d{4}-\d{2}-\d{2}$", data.get("date", "")):
            print(f"跳过（缺少 title 或 date 格式错误）: {path}")
            continue
        folder = f"{data['date']}-{slugify(data['title'])}"
        if post_exists(folder):
            print(f"跳过（已存在）: {folder}")
            continue
        bilingual = data.get("bilingual", True)
        langs = ("en", "zh") if bilingual else ("en",)
        print(f"添加文章: {folder}/" + ("（en+zh）" if bilingual else "（仅 en）"))
        if args.dry_run:
            print("  [DRY-RUN] 不写入")
            continue
        for lang in langs:
            d = os.path.join(ROOT, "content", lang, "post", folder)
            os.makedirs(d, exist_ok=False)
            with open(os.path.join(d, "index.md"), "w", encoding="utf-8") as f:
                f.write(build_index(data, body))
            imgs = copy_images(os.path.dirname(path), d, os.path.splitext(os.path.basename(path))[0])
            print(f"  ✓ {lang}/post/{folder}/" + (f" (+图片 {imgs})" if imgs else ""))
        if not bilingual:
            add_allowlist(f"[ZH only] post/{folder}")
        if is_dir:
            done = os.path.join(os.path.dirname(path), "_done")
            os.makedirs(done, exist_ok=True)
            moved = [os.path.basename(path)]
            shutil.move(path, os.path.join(done, os.path.basename(path)))
            for c in sorted(os.listdir(os.path.dirname(path))):
                if c.startswith("_") or not os.path.isfile(os.path.join(os.path.dirname(path), c)):
                    continue
                if c.lower().endswith((".jpg", ".png", ".jpeg", ".gif", ".webp", ".svg")):
                    shutil.move(os.path.join(os.path.dirname(path), c), os.path.join(done, c))
                    moved.append(c)
            print(f"  → 已归档到 {done}: {moved}")

    print("\n完成。请运行 front matter 校验与中英同步检查。")


if __name__ == "__main__":
    main()
