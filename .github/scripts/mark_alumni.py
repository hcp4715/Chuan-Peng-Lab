#!/usr/bin/env python3
"""Mark team members as Alumni in both en and zh content trees.

Usage:
    python mark_alumni.py <folder>... [--start "Sep. 2023"] [--end "2026"] [--dry-run] [--site-dir /path]
"""

import argparse
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
    fm_end = end
    front_matter = text[fm_start:fm_end]
    body_start = end + len("\n---")
    if body_start < len(text) and text[body_start] == "\n":
        body_start += 1
    body = text[body_start:]
    return front_matter, body


def extract_summary_range(summary_value):
    if "~" not in summary_value:
        return None, None
    parts = summary_value.split("~", 1)
    return parts[0].strip(), parts[1].strip()


def replace_tags_block(fm):
    pattern = re.compile(
        r"^(tags:\s*\n(?:[ \t]*- .+\n?)*)",
        re.MULTILINE,
    )
    m = pattern.search(fm)
    if not m:
        return None, None
    old_block = m.group(1)
    tag_values = re.findall(r"^[ \t]*- (.+)$", old_block, re.MULTILINE)
    old_tags_str = ", ".join(t.strip() for t in tag_values) if tag_values else "(empty)"

    new_block = "tags:\n- Alumni\n"
    new_fm = fm[:m.start()] + new_block + fm[m.end():]
    return new_fm, old_tags_str


def replace_summary_range(fm, new_start, new_end):
    pattern = re.compile(
        r"^(summary:\s*)__(.+?)__",
        re.MULTILINE,
    )
    m = pattern.search(fm)
    if not m:
        return None, None, None

    old_range = m.group(2).strip()
    new_range = f"{new_start} ~ {new_end}"
    new_fm = fm[:m.start()] + m.group(1) + "__" + new_range + "__" + fm[m.end():]
    return new_fm, old_range, new_range


def process_file(filepath, start, end, dry_run):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    parsed = parse_front_matter(text)
    if parsed is None:
        raise ValueError(f"No front matter found in {filepath}")

    fm, body = parsed
    changed = False
    reports = []

    new_fm, old_tags_str = replace_tags_block(fm)
    if new_fm is None:
        raise ValueError(f"No tags: block found in {filepath}")
    if old_tags_str.strip() == "Alumni":
        reports.append("tags already Alumni")
    else:
        reports.append(f"tags {old_tags_str} -> Alumni")
        fm = new_fm
        changed = True

    summary_match = re.search(r"^summary:\s*__(.+?)__", fm, re.MULTILINE)
    if not summary_match:
        raise ValueError(f"No __...__ time range found in summary of {filepath}")

    current_start, current_end = extract_summary_range(summary_match.group(1))

    resolved_start = start if start else current_start
    resolved_end = end if end else current_end

    if resolved_start is None or resolved_end is None:
        raise ValueError(f"Cannot resolve start/end for summary in {filepath}")

    new_fm, old_range, new_range = replace_summary_range(fm, resolved_start, resolved_end)
    if new_fm is None:
        raise ValueError(f"No __...__ time range found in summary of {filepath}")

    if old_range == new_range:
        reports.append(f"summary __{old_range}__ unchanged")
    else:
        reports.append(f"summary __{old_range}__ -> __{new_range}__")
        fm = new_fm
        changed = True

    new_text = "---\n" + fm + "\n---\n" + body

    if changed and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_text)

    return "; ".join(reports), changed


def main():
    parser = argparse.ArgumentParser(
        description="Mark team members as Alumni in both en and zh content trees."
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="Member folder names (e.g., wjq, zrz)",
    )
    parser.add_argument(
        "--start",
        default=None,
        help='New start label (e.g., "Sep. 2023"). Auto-extracted from current summary if omitted.',
    )
    parser.add_argument(
        "--end",
        default=None,
        help='New end label (e.g., "2026"). Uses current value if omitted.',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing.",
    )
    parser.add_argument(
        "--site-dir",
        default=None,
        help="Path to site root (default: auto-detect from script location or cwd).",
    )
    args = parser.parse_args()

    if args.site_dir:
        site_root = os.path.abspath(args.site_dir)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.dirname(os.path.dirname(script_dir))
        if os.path.isdir(os.path.join(candidate, "content")):
            site_root = candidate
        else:
            site_root = os.getcwd()

    errors = []
    any_changed = False

    for folder in args.folders:
        for lang in ("en", "zh"):
            rel = os.path.join("content", lang, "project", folder, "index.md")
            filepath = os.path.join(site_root, rel)
            if not os.path.isfile(filepath):
                errors.append(f"ERROR: {rel} not found")
                continue

            try:
                report, changed = process_file(filepath, args.start, args.end, args.dry_run)
                prefix = "[DRY-RUN] " if args.dry_run else ""
                print(f"{prefix}{rel}: {report}")
                if changed:
                    any_changed = True
            except ValueError as e:
                errors.append(f"ERROR: {e}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(1)

    if args.dry_run and not any_changed:
        print("No changes needed.")

    sys.exit(0)


if __name__ == "__main__":
    main()
