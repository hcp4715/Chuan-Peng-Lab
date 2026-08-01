#!/usr/bin/env python3
"""CI guard: validate Alumni members have proper end-date time ranges and en/zh consistency."""

import glob
import os
import re
import sys


def parse_front_matter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm_start = text.index("\n", 0) + 1
    return text[fm_start:end]


def get_tags(fm):
    pattern = re.compile(r"^(tags:\s*\n(?:[ \t]*- .+\n?)*)", re.MULTILINE)
    m = pattern.search(fm)
    if not m:
        return []
    return [t.strip() for t in re.findall(r"^[ \t]*- (.+)$", m.group(1), re.MULTILINE)]


def get_summary(fm):
    m = re.search(r"^summary:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip()


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.dirname(os.path.dirname(script_dir))
    if os.path.isdir(os.path.join(candidate, "content")):
        site_root = candidate
    else:
        site_root = os.getcwd()

    en_pattern = os.path.join(site_root, "content", "en", "project", "*", "index.md")
    en_files = sorted(glob.glob(en_pattern))

    violations = []

    for en_file in en_files:
        folder = os.path.basename(os.path.dirname(en_file))
        rel = os.path.join("content", "en", "project", folder, "index.md")

        with open(en_file, "r", encoding="utf-8") as f:
            text = f.read()

        fm = parse_front_matter(text)
        if fm is None:
            continue

        tags = get_tags(fm)
        if "Alumni" not in tags:
            continue

        summary = get_summary(fm)

        if "~" not in summary:
            violations.append(f"ERROR {rel}: missing time range")
            continue

        range_match = re.search(r"__\s*(.+?)\s*__", summary)
        if range_match:
            range_text = range_match.group(1)
            if "Now" in range_text or "至今" in range_text:
                violations.append(f"ERROR {rel}: end date not set")

        zh_file = os.path.join(site_root, "content", "zh", "project", folder, "index.md")
        if not os.path.isfile(zh_file):
            violations.append(f"ERROR {rel}: en/zh mismatch (zh folder missing)")
        else:
            with open(zh_file, "r", encoding="utf-8") as f:
                zh_text = f.read()
            zh_fm = parse_front_matter(zh_text)
            if zh_fm is None:
                violations.append(f"ERROR {rel}: en/zh mismatch (zh has no front matter)")
            else:
                zh_tags = get_tags(zh_fm)
                if "Alumni" not in zh_tags:
                    violations.append(f"ERROR {rel}: en/zh mismatch (zh tags: {', '.join(zh_tags)})")

    if violations:
        for v in violations:
            print(v)
        sys.exit(1)

    print(f"check_alumni: all Alumni members OK ({len(en_files)} members scanned)")
    sys.exit(0)


if __name__ == "__main__":
    main()
