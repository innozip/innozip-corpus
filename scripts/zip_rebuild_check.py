#!/usr/bin/env python3
# Computes: rebuilds each STORED zip archive from its own members with the published writer parameters and compares SHA-256.
# Reads: the zip archives of Zenodo records 23112969 (CC0 set, version 1.1; the same archives as 23110892) and 23112972.
"""Rebuild published STORED zip archives from their own members and compare SHA-256.

    python zip_rebuild_check.py <archive.zip> [<archive.zip> ...]

Standard library only. Licence of this script: MIT (see LICENSE). For each archive, three rebuilds are compared with
the original:
  A  members sorted by name, STORED, date 1980-01-01 00:00:00, external attributes 0644 << 16,
     Zip64 extra field forced on every member, create_system left at this platform's default
  B  as A, without forcing the Zip64 extra field
  C  as A, with create_system = 3 (the value CPython writes on Linux and macOS)
Each rebuild is written to one temporary file, which is deleted at the end.
"""
import hashlib
import os
import sys
import tempfile
import zipfile

DATE = (1980, 1, 1, 0, 0, 0)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rebuild(src, dst, force_zip64=True, create_system=None):
    with zipfile.ZipFile(src) as z, zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as w:
        for name in sorted(i.filename for i in z.infolist()):
            zi = zipfile.ZipInfo(name, DATE)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o644 << 16
            if create_system is not None:
                zi.create_system = create_system
            with z.open(name) as s, w.open(zi, "w", force_zip64=force_zip64) as d:
                for chunk in iter(lambda: s.read(1 << 20), b""):
                    d.write(chunk)


def main(paths):
    print(f"python {sys.version.split()[0]} on {sys.platform}; default create_system "
          f"{zipfile.ZipInfo('x').create_system}")
    print("archive\tbytes\tA_match\tB_match\tB_bytes_diff\tC_match")
    fd, tmp = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    try:
        for p in paths:
            orig = sha256(p)
            rebuild(p, tmp)
            a = sha256(tmp) == orig
            rebuild(p, tmp, force_zip64=False)
            b = sha256(tmp) == orig
            b_diff = os.path.getsize(p) - os.path.getsize(tmp)
            rebuild(p, tmp, create_system=3)
            c = sha256(tmp) == orig
            print(f"{os.path.basename(p)}\t{os.path.getsize(p)}\t{a}\t{b}\t{b_diff}\t{c}")
    finally:
        os.remove(tmp)


if __name__ == "__main__":
    main(sys.argv[1:])
