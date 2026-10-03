Records appear here only after the record is published on Zenodo: MANIFEST.tsv (published files only), SHA256SUMS.txt, licence_table.tsv and LICENSES/.

Archives of every record are STORED zip files written with Python's `zipfile`:
- members in name order (byte-wise sort of the member paths), no directory entries;
- method STORED;
- date and time 1980-01-01 00:00:00;
- external attributes `0644 << 16` (Unix permission bits rw-r--r--);
- the Zip64 extra field forced on every member (version needed to extract 4.5);
- host-system field 0 (MS-DOS / FAT, the value `zipfile` writes on Windows);
- no data descriptors, no comment.

`../scripts/zip_rebuild_check.py` rebuilds an archive from its own members with these parameters and compares SHA-256.
