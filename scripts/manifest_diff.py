#!/usr/bin/env python3
# Computes: a cell-by-cell comparison of two versions of a record's MANIFEST.tsv (changed cells, rows, cells per column).
# Reads: MANIFEST.tsv of Zenodo records 23110892 (CC0 set, version 1) and 23112969 (CC0 set, version 1.1).
"""Cell-by-cell comparison of two versions of a record's MANIFEST.tsv.

    python manifest_diff.py <old MANIFEST.tsv> <new MANIFEST.tsv>

Standard library only. Licence of this script: MIT (see LICENSE). Requires the same header and row count; prints
changed cells, changed rows and the changed cells per column.
"""
import collections
import csv
import sys


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))


def main(old_path, new_path):
    old, new = read(old_path), read(new_path)
    if old[0] != new[0] or len(old) != len(new):
        sys.exit("headers or row counts differ; not a cell-by-cell comparable pair")
    header = old[0]
    cells, rows, per_col = 0, set(), collections.Counter()
    for i, (a, b) in enumerate(zip(old[1:], new[1:]), start=1):
        for j, (u, v) in enumerate(zip(a, b)):
            if u != v:
                cells += 1
                rows.add(i)
                per_col[header[j]] += 1
    total = (len(old) - 1) * len(header)
    print(f"changed cells {cells} of {total} ({100 * cells / total:.1f}%) in {len(rows)} of {len(old) - 1} rows")
    print("per column", dict(per_col))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
