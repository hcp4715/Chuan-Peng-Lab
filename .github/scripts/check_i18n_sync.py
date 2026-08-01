#!/usr/bin/env python3
"""Check that EN and ZH content trees are in sync for key sections.

Compares subdirectory names under content/en/ and content/zh/ for the
sections: project, publication, post.

Exit code 1 if any mismatch is found, 0 if all sections are in sync.
"""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EN_ROOT = REPO_ROOT / "content" / "en"
ZH_ROOT = REPO_ROOT / "content" / "zh"
SECTIONS = ["project", "publication", "post"]
ALLOWLIST_FILE = Path(__file__).resolve().parent / "i18n_allowlist.txt"


def load_allowlist():
    if not ALLOWLIST_FILE.is_file():
        return set()
    return {
        line.strip()
        for line in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def list_subdirs(section_path):
    if not section_path.is_dir():
        return set()
    return {
        entry.name
        for entry in sorted(section_path.iterdir())
        if entry.is_dir()
    }


def main():
    diffs = []

    for section in SECTIONS:
        en_dirs = list_subdirs(EN_ROOT / section)
        zh_dirs = list_subdirs(ZH_ROOT / section)

        en_only = sorted(en_dirs - zh_dirs)
        zh_only = sorted(zh_dirs - en_dirs)

        for d in en_only:
            diffs.append(f"[EN only] {section}/{d}")
        for d in zh_only:
            diffs.append(f"[ZH only] {section}/{d}")

    if diffs:
        allowlist = load_allowlist()
        pending = [d for d in diffs if d not in allowlist]

        if pending:
            print("i18n sync differences found:\n")
            for line in pending:
                print(line)
            print(f"\n{len(pending)} difference(s) found")
            sys.exit(1)
        else:
            print(
                "All non-allowlisted sections are in sync between EN and ZH. "
                f"({len(diffs)} allowlisted difference(s): "
                + ", ".join(diffs)
                + ")"
            )
            sys.exit(0)
    else:
        print("All sections are in sync between EN and ZH.")
        sys.exit(0)


if __name__ == "__main__":
    main()
