#!/usr/bin/env python3
"""Download an INNOZIP corpus record from Zenodo, verify it, and unpack it.

    python fetch_verify.py <zenodo record id> [--out DIR] [--no-extract]
    python fetch_verify.py --local <folder holding the record's files> [--out DIR]   # verify files already downloaded

1. Reads the record's file list from the public Zenodo API (no account needed).
2. Downloads every file (three attempts each), checking each against the MD5 that Zenodo reports.
3. Checks the SHA-256 of every zip archive against its line in SHA256SUMS.txt.
4. Unpacks the STORED zips into DIR and checks every file listed in MANIFEST.tsv: SHA-256 and size of each member, a
   member that MANIFEST.tsv does not list, and a MANIFEST.tsv row that no zip contains all count as failures. (The
   per-file lines of SHA256SUMS.txt repeat MANIFEST.tsv's sha256 column for use with `sha256sum -c`.)

Standard library only; Python 3.8 or later. Licence of this script: MIT (see LICENSE).
"""
import argparse, csv, hashlib, json, sys, time, urllib.request, zipfile
from pathlib import Path, PurePosixPath

API = "https://zenodo.org/api/records/"
ATTEMPTS = 3


def get_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def download(url, dst, want_md5):
    tmp = dst.with_suffix(dst.suffix + ".part")
    last = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            md5 = hashlib.md5()
            with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    md5.update(b); f.write(b)
            if want_md5 and md5.hexdigest() != want_md5:
                raise IOError(f"MD5 mismatch (got {md5.hexdigest()}, Zenodo lists {want_md5})")
            tmp.replace(dst)
            return
        except Exception as e:  # network error, truncated transfer, checksum mismatch
            last = e
            print(f"  attempt {attempt} of {ATTEMPTS} failed for {dst.name}: {e}")
            time.sleep(2 * attempt)
    if tmp.exists():
        tmp.unlink()
    raise SystemExit(f"FAILED: {dst.name} could not be downloaded after {ATTEMPTS} attempts ({last})")


def safe_target(out, name):
    """Refuse absolute names, drive letters and '..': the target must lie inside the output folder."""
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or (p.parts and ":" in p.parts[0]) or "\\" in name:
        raise SystemExit(f"unsafe member name in archive: {name!r}")
    target = (out / Path(*p.parts)).resolve()
    if out.resolve() not in target.parents:
        raise SystemExit(f"member would be written outside the output folder: {name!r}")
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record", nargs="?")
    ap.add_argument("--local", default=None, help="folder that already holds the record's files")
    ap.add_argument("--out", default="corpus")
    ap.add_argument("--no-extract", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    if a.local:
        dl = Path(a.local)
        files = []
    else:
        if not a.record:
            ap.error("give a record id or --local")
        dl = out / "_downloads" / a.record
        dl.mkdir(parents=True, exist_ok=True)
        files = get_json(API + a.record)["files"]
    for f in files:
        key = f["key"]; dst = dl / key
        want = f.get("checksum", "").split(":", 1)[-1]
        if dst.exists() and want and digest(dst, "md5") == want:
            print(f"present  {key}")
            continue
        print(f"download {key} ({f['size']:,} B)")
        download(f["links"]["self"], dst, want)
    sums = {}
    for line in (dl / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        h, name = line.split("  ", 1)
        sums[name] = h
    zips = sorted(dl.glob("*.zip"))
    for z in zips:
        if digest(z, "sha256") != sums.get(z.name):
            raise SystemExit(f"SHA-256 mismatch for {z.name}")
        print(f"ok       {z.name}")
    if a.no_extract:
        return 0
    with open(dl / "MANIFEST.tsv", encoding="utf-8", newline="") as f:
        man = {r["path"]: r for r in csv.DictReader(f, delimiter="\t")}
    out.mkdir(parents=True, exist_ok=True)
    bad, seen = 0, set()
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for zi in zf.infolist():
                target = safe_target(out, zi.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(zi) as src, open(target, "wb") as dst:
                    for b in iter(lambda: src.read(1 << 20), b""):
                        dst.write(b)
                m = man.get(zi.filename)
                if not m:
                    print(f"NOT IN MANIFEST {zi.filename}"); bad += 1
                elif digest(target, "sha256") != m["sha256"] or target.stat().st_size != int(m["bytes"]):
                    print(f"MISMATCH {zi.filename}"); bad += 1
                else:
                    seen.add(zi.filename)
    missing = sorted(set(man) - seen)
    for p in missing[:20]:
        print(f"MISSING  {p}")
    print(f"{len(man)} files in MANIFEST.tsv: {len(seen)} verified, {bad} wrong or unlisted, {len(missing)} missing; "
          f"files under {out}")
    return 1 if bad or missing else 0


if __name__ == "__main__":
    sys.exit(main())
