#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
from pathlib import Path


HEADER_RE = re.compile(r"^\s*#\s*@pattern\s+id=(\S+)\s+keywords=(.*)$")


def split_blocks(text):
    lines = text.splitlines()
    starts = []
    for i, line in enumerate(lines):
        match = HEADER_RE.match(line)
        if match:
            starts.append((i, match.group(1), match.group(2)))

    blocks = []
    for idx, (start, pattern_id, keywords) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        blocks.append(
            {
                "id": pattern_id,
                "keywords": keywords,
                "text": "\n".join(lines[start:end]).rstrip(),
            }
        )
    return blocks


def score_block(block, terms):
    haystack = f"{block['id']} {block['keywords']} {block['text']}".lower()
    return sum(1 for term in terms if term and term.lower() in haystack)


def main():
    parser = argparse.ArgumentParser(description="Select matching transfer-pattern blocks.")
    parser.add_argument("library", help="Path to transfer-patterns.yaml")
    parser.add_argument("terms", nargs="*", help="Search terms")
    parser.add_argument("--max", type=int, default=5, help="Maximum blocks to print")
    parser.add_argument("--index", action="store_true", help="Print only pattern index lines")
    args = parser.parse_args()

    path = Path(args.library)
    text = path.read_text(encoding="utf-8")
    blocks = split_blocks(text)

    if args.index:
        for block in blocks:
            print(f"# @pattern id={block['id']} keywords={block['keywords']}")
        return 0

    terms = [term.strip() for term in args.terms if term.strip()]
    ranked = []
    for block in blocks:
        score = score_block(block, terms)
        if score > 0:
            ranked.append((score, block["id"], block["text"]))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    for i, (_, _, block_text) in enumerate(ranked[: args.max]):
        if i:
            print()
        print(block_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
