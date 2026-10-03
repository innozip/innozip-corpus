# Recipe: game assets, CC0 set (version 1)

Record: https://doi.org/10.5281/zenodo.23110892. The exact command for each generated file is in the record's
`MANIFEST.tsv`, column `generation`; this page describes the procedure around those commands.

## 1. Sources

CC0 images downloaded from their publishers (URL and SHA-256 of each source in `MANIFEST.tsv`, column `inputs`):
Poly Haven textures (rock_boulder_cracked, brick_wall_005, wood_planks_grey, brown_leather, blue_metal_plate; 1k and 2k)
and one HDRI (kloofendal_48d_partly_cloudy_puresky, 1k); ambientCG materials (Tiles141, Ground112, PavingStones151, 1K
PNG); the Kenney UI Pack 2.0 (129 PNG sprites). One procedural image: fBm value noise, 1024 x 1024 RGB, numpy, seed
20261001.

## 2. Work images

Each source was converted once to an 8-bit RGBA work image, which the encoders read. The Kenney sprites are
shelf-packed into one 2048 x 2048 RGBA atlas with transparency.

## 3. Mip chains

- bc7enc_rdo and etcpak files: the generator's own chain -- box filter on RGBA8 (colour averaged in the stored sRGB
  encoding; normals averaged as vectors and renormalised), each level padded to a multiple of 4 by edge replication,
  a level below 4 x 4 is one block; level payloads concatenated into a DX10 DDS or wrapped by `ktx create --raw`.
- texconv: its own chain (`-m 0`), sRGB handled with `-srgb` and the `_SRGB` formats.
- astcenc `.astc` files: level 0 only (the format has no mip chain).
- `ktx create`: `--generate-mipmap` (lanczos4); `--assign-tf srgb` for colour, `--assign-tf linear` for linear data.

## 4. Encoders and settings

| encoder | version | licence | formats and settings |
|---|---|---|---|
| bc7enc_rdo | b943862 (bc7enc v1.08) | MIT or Unlicense | BC7 `-u4` modes 1/5/6/7: lambda 0, `-e`, `-z0.5`, `-z1`, `-z2`; BC1 `-1`, BC3 `-3`, BC4 `-4`, BC5 `-5` |
| DirectXTex texconv / texassemble | 2026.5.8.1 | MIT | BC1-BC7 and BC6H with `-nogpu` (CPU codecs); cube (6 x 512), array (4 x 1024), volume (8 x 256) assembled uncompressed, then compressed to BC7 and BC1 |
| astcenc | 5.7.0 | Apache-2.0 | ASTC 4x4 / 6x6 / 8x8, `-medium` and `-thorough`; `-cl` linear, `-cs` sRGB, `-ch` HDR |
| etcpak | 0.9.15 (pip wheel) | MIT (Python wrapper) over BSD-3-Clause | ETC2 RGB / RGBA, BC1 / BC3 / BC4 / BC5 |
| KTX-Software `ktx create` | 4.4.2 | Apache-2.0 | KTX2 from raw payloads (BC7, ETC2), ASTC 6x6 via the library encoder, UASTC (q2, with and without RDO 1.0), BasisLZ (clevel 1, qlevel 128), zstd levels 5 and 19 |

Wrappers: six subjects x {raw RGBA8, raw BC7 (bc7enc_rdo payloads), ASTC 6x6} x {none, zstd 5, zstd 19},
plus UASTC {none, zstd 5, zstd 19}, UASTC RDO {none, zstd 5} and BasisLZ.

## 5. Unmodified files

glTF-Sample-Assets models (Avocado, BarramundiFish, BoomBox, Lantern, SheenCloth, ToyCar; variants glTF, glTF-Binary,
glTF-Draco, glTF-Quantized as published; separate image files not included). Kenney Impact Sounds, Interface Sounds and
RPG Audio: five Ogg files per pack as published, and one ustar tar per pack of all its Ogg files (no compression,
mtime 0, members sorted).

## 6. Archives

The record's zip files are written with Python's `zipfile` with these parameters:
- members in name order (byte-wise sort of the member paths), one entry per file, no directory entries;
- method STORED (no compression);
- date and time 1980-01-01 00:00:00 on every member;
- external attributes `0644 << 16` (Unix permission bits rw-r--r--);
- the Zip64 extra field forced on every member (version needed to extract 4.5);
- host-system field 0 (MS-DOS / FAT, the value `zipfile` writes on Windows);
- no data descriptors, no comment.

`scripts/zip_rebuild_check.py` rebuilds every published archive from its own members with these parameters and
compares SHA-256. It does so for all seven archives of records 23112969 and 23112972. With the Zip64 extra not forced,
or with host-system field 3 (Linux / macOS), the rebuilt archives differ.

## 7. Verification

Every file was verified against its source before publication.

## Errata to the record's MANIFEST.tsv (version 1)

The copy in `records/game-assets-cc0-v1/MANIFEST.tsv` here is corrected; the data files and their checksums are
unchanged.

1. Column `generation` gives etcpak's licence as "BSD-3-Clause" (94 rows). The pip wheel is the MIT-licensed Python
   wrapper over the BSD-3-Clause etcpak library; the record's README states this correctly. Neither licence places a
   condition on the encoder's output.
2. Column `inputs` of the six cube / array / volume container files referred to an internal note for the source
   checksums. The copy here lists each source image with its SHA-256 instead.
3. Column `generation` of the 53 ETC2 KTX2 files split the `ktx create` format name around the tool note (for example
   "`--format ETC2_R8G8B8_` (KTX-Software 4.4.2)UNORM_BLOCK"). The copy here gives the command as it runs:
   `ktx create --raw --format ETC2_R8G8B8_UNORM_BLOCK` (or `ETC2_R8G8B8A8_SRGB_BLOCK` etc.), then the tool note.
4. Column `generation` of the three Kenney tar archives named the generating script instead of the public tool. The copy
   here states it: Python 3 `tarfile`, POSIX ustar, no compression, mtime 0, uid / gid 0, empty owner names, mode 0644,
   members sorted by name.
5. Column `generation` of 15 KTX2 wrapper files is reworded to describe how each file was written.

Version 1.1 of the record (concept DOI 10.5281/zenodo.23110891) carries this corrected MANIFEST.tsv.
