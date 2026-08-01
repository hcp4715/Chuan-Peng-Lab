#!/usr/bin/env python3
"""Validate front matter in all Markdown/Rmd content files.

Recursively scans content/en/ and content/zh/ for *.md and *.Rmd files,
parses YAML (---) or TOML (+++) front matter, and reports parse errors.

Exit code 0 if all files parse successfully, 1 if any errors found.
"""

import os
import sys
import tomllib
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIRS = [
    REPO_ROOT / "content" / "en",
    REPO_ROOT / "content" / "zh",
]
EXTENSIONS = {".md", ".rmd"}


def find_content_files():
    files = []
    for content_dir in CONTENT_DIRS:
        if not content_dir.is_dir():
            continue
        for root, _dirs, filenames in os.walk(content_dir):
            for fname in filenames:
                if Path(fname).suffix.lower() in EXTENSIONS:
                    files.append(Path(root) / fname)
    files.sort()
    return files


def extract_front_matter(filepath):
    """Return (content_str, delimiter, end_line) or (None, None, None).

    delimiter is '---' (YAML) or '+++' (TOML).
    end_line is the 1-based line number of the closing delimiter.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return None, None, None

    first_line = lines[0].strip()
    if first_line not in ("---", "+++"):
        return None, None, None

    delimiter = first_line

    for i in range(1, len(lines)):
        if lines[i].strip() == delimiter:
            content = "".join(lines[1:i])
            end_line = i + 1
            return content, delimiter, end_line

    return None, None, None


def validate_file(filepath):
    """Return None on success, or an error message string on failure."""
    content, delimiter, _end_line = extract_front_matter(filepath)

    if content is None:
        return None

    rel_path = filepath.resolve().relative_to(REPO_ROOT)

    if delimiter == "---":
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            line_num = 1
            if hasattr(e, "problem_mark") and e.problem_mark is not None:
                # PyYAML lines are 0-based relative to parsed string;
                # add 2: +1 for 0→1-based, +1 for the opening --- line.
                line_num = e.problem_mark.line + 2
            msg = str(e).split("\n")[0]
            return f"ERROR {rel_path}:{line_num}: {msg}"
    elif delimiter == "+++":
        try:
            tomllib.loads(content)
        except tomllib.TOMLDecodeError as e:
            line_num = 1
            if hasattr(e, "lineno"):
                # tomllib lineno is 1-based relative to TOML content;
                # add 1 for the opening +++ line.
                line_num = e.lineno + 1
            else:
                line_num = 2
            msg = str(e).split("\n")[0]
            return f"ERROR {rel_path}:{line_num}: {msg}"

    return None


def main():
    files = find_content_files()
    errors = []
    validated = 0

    for filepath in files:
        content, _, _ = extract_front_matter(filepath)
        if content is None:
            continue
        validated += 1
        error = validate_file(filepath)
        if error:
            errors.append(error)
            print(error)

    print(f"\nValidated {validated} files, {len(errors)} errors")

    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
