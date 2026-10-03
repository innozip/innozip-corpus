# innozip-corpus

Public part of the INNOZIP compression test corpus: the list of published files, their licences, the recipes that
generated them, and a script that downloads a record from Zenodo and verifies it byte for byte. The data itself lives in
the Zenodo records listed below; this repository holds no corpus files.

## Records

| record | DOI (always the newest version) | version DOIs | files | licence |
|---|---|---|---:|---|
| game assets, CC0 set | [10.5281/zenodo.23110891](https://doi.org/10.5281/zenodo.23110891) | version 1: [10.5281/zenodo.23110892](https://doi.org/10.5281/zenodo.23110892); version 1.1: [10.5281/zenodo.23112969](https://doi.org/10.5281/zenodo.23112969) | 744 | CC0 1.0 |
| game assets, attribution set | [10.5281/zenodo.23112971](https://doi.org/10.5281/zenodo.23112971) | version 1: [10.5281/zenodo.23112972](https://doi.org/10.5281/zenodo.23112972) | 13 | CC BY 4.0 |

Per record, `records/<record>/` holds:

- `MANIFEST.tsv`: every published file with its path, bytes, SHA-256, licence, source, inputs and generation command.
- `SHA256SUMS.txt`: the same list as checksums.
- `licence_table.tsv`: the sources, each with its licence page and the statement that grants redistribution.
- `LICENSES/`: the licence texts.
- `ATTRIBUTION.md` (attribution set): the credit every re-use must give.

`recipes/` describes how the generated files were made.

Cite the data as:
- Spivak, E. (2026). *INNOZIP compression corpus: game assets, CC0 set* [Data set]. Zenodo.
  https://doi.org/10.5281/zenodo.23110891
- Spivak, E. (2026). *INNOZIP compression corpus: game assets, attribution set* [Data set]. Zenodo.
  https://doi.org/10.5281/zenodo.23112971

This repository: https://github.com/innozip/innozip-corpus

## Fetch and verify

```
git clone https://github.com/innozip/innozip-corpus
cd innozip-corpus
python scripts/fetch_verify.py 23110891 --out corpus
```

`23110891` is the record's concept id: Zenodo resolves it to the newest version.

The script:

- downloads every file of the record (three attempts each) and checks Zenodo's MD5;
- checks the SHA-256 of each zip against its line in `SHA256SUMS.txt`;
- after unpacking, checks every file's SHA-256 and size against `MANIFEST.tsv`. A file missing from the zips, or a
  member `MANIFEST.tsv` does not list, counts as a failure. The per-file lines of `SHA256SUMS.txt` carry the same
  checksums for `sha256sum -c`.

It uses the Python standard library only (3.8 or later). `--local <folder>` verifies a record that is already downloaded.

## Credits

The files of the attribution set are CC BY 4.0: re-use must give the credit in
`records/game-assets-attribution-v1/ATTRIBUTION.md` (Cesium; PixelMannen, tomkranis, @AsoboStudio and @scurest).

The files of the CC0 set are CC0; credit is not required and is given with thanks to Poly Haven
(polyhaven.com), ambientCG (ambientCG.com), Kenney (kenney.nl) and the Khronos glTF-Sample-Assets contributors as their
model READMEs name them: Microsoft (Avocado, BarramundiFish, BoomBox, SheenCloth; Lantern), sbtron (Lantern, initial
version), Frank Galligan (Lantern, Draco compression), Guido Odendahl and Eric Chadwick (ToyCar).

## Licences of this repository

Scripts: MIT (`LICENSE`). Documentation and tables: CC BY 4.0 (`LICENSE-docs`). Corpus files: as stated per file in
each record's `MANIFEST.tsv`.

INNOZIP is a trademark of Eugen Spivak.
