#!/usr/bin/env python3
# Computes: composition statistics of a record (files and bytes per folder and extension, sources, licences, sizes, tools).
# Reads: MANIFEST.tsv of Zenodo record 23112969 (CC0 set, version 1.1) or of any other record of this repository.
"""Composition statistics of a published corpus record from its MANIFEST.tsv.

    python manifest_stats.py <MANIFEST.tsv>

Standard library only. Licence of this script: MIT (see LICENSE). Prints files and bytes per archive folder, per file
extension, generated vs unmodified, source hosts, licences, size range and median, and the manifest rows that name
each encoder.
"""
import collections
import csv
import os
import re
import sys

TOOLS = ["bc7enc_rdo", "astcenc", "ktx create", "texconv", "etcpak", "texassemble", "tarfile"]


def main(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    print(f"rows {len(rows)}; columns {len(rows[0])}: {', '.join(rows[0])}")
    print(f"total bytes {sum(int(r['bytes']) for r in rows):,}")
    files, size = collections.Counter(), collections.Counter()
    for r in rows:
        folder = r["path"].split("/")[1]
        files[folder] += 1
        size[folder] += int(r["bytes"])
    for k in sorted(files, key=lambda k: -size[k]):
        print(f"  {k:16s} {files[k]:5d} files {size[k]:15,d} bytes")
    print("extensions", dict(collections.Counter(os.path.splitext(r["path"])[1].lower() for r in rows)))
    print("generated", sum(1 for r in rows if r["generation"].strip()),
          "unmodified", sum(1 for r in rows if not r["generation"].strip()))
    print("source hosts", dict(collections.Counter(re.sub(r"https?://([^/]+).*", r"\1", r["source_url"]) or "(none)"
                                                   for r in rows)))
    print("licences", dict(collections.Counter(r["licence"] for r in rows)))
    sizes = sorted(int(r["bytes"]) for r in rows)
    print(f"size min {sizes[0]:,} median {sizes[len(sizes) // 2]:,} max {sizes[-1]:,}")
    print("rows naming each tool", {t: sum(1 for r in rows if t in r["generation"]) for t in TOOLS})


if __name__ == "__main__":
    main(sys.argv[1])
