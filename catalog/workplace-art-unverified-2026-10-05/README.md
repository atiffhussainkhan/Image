# Workplace artwork audit — 5 October 2026

102,393 files inspected across four archives. Original archives remain untouched. This directory indexes locally supplied artwork; it does not grant rights to the artwork.

| Archive | Files | Technical suitability |
|---|---:|---|
| PNG Icon Pack | 10,632 | 10,621 PNGs decode; 10,620 have an alpha channel/transparency metadata. 9,031 are 128×128. Suitable for small UI/icons, with mixed visual styles. 2,332 duplicate files within the pack. Not a high-resolution sprite collection. |
| Clipart | 3,374 | 692 rasters decode; 86 have transparency capability. 726 WMF and 1,723 DRW files need conversion or legacy software. Mix of illustrations, scans and backgrounds; includes Disney work described as ripped from print software. |
| EPS Clipart | 80,418 | 80,413 EPS files with numeric bounding boxes; 80,412 have the expected EPS header. Useful editable source candidates for props/UI/illustrations. Header checks do not verify successful rendering. Requires raster/vector conversion and visual review. |
| Samples | 7,969 | 6,178 WMF vectors and 1,547 successfully decoded rasters, mostly photos; 34 JPG files are empty. Useful candidates for references/textures and converted illustrations. No animation readiness established. |

## Quality limits
All raster files were decoded with Pillow. Sample contact sheets were visually inspected for PNG, Clipart and Samples. Vector rendering was not verified because no EPS/WMF renderer is installed. Proprietary DRW/MPF/WPG formats were inventoried, not fully decoded. Technical suitability does not establish legal reuse. There is no shared palette, sprite scale, animation naming or tileset grid established across these packs.

Fourteen Clipart TAR entries had invalid legacy filename bytes. They were recovered locally with invalid characters normalized to underscores. The original TAR preserves the original bytes.

## Search
Open `index.html`. If opened directly, choose `assets.json` in its file picker. Search filenames/categories and filter by pack, format and readiness. When served over HTTP, the compressed search shards load automatically. Example: `python3 -m http.server 8000` from this directory, then open `http://localhost:8000/index.html`.

`assets.csv` and `assets.json` are the full local inventories: original paths, categories, keyword tags, dimensions, transparency capability, SHA-256, duplicate references and technical readiness. The repository search shards contain the searchable path/format/readiness fields; full inventories are prepared locally for release upload. Original descriptive names are preserved; numeric names are searchable by their category path. No semantic labels inferred from unseen artwork have been invented.

## Provenance and licences
The user says these files came from workplace users. No actual reusable licence documents or traceable original download pages were found. A PNG named README or EPS named Copyright/License is an icon or drawing, not a licence document. This audit assigns `unverified`, not CC0, MIT or a fabricated licence. Third-party authors retain their rights. The Clipart pack includes a note stating that Disney images were ripped from print software.

The user requested storage despite unverified provenance. Keep these collections separate from `assets/` and the repository's approved/licence-clear catalogue. Neither the audit nor workplace possession confirms permission to use or redistribute the artwork. Source/licence review remains needed before treating them as approved production assets.

## Storage

All four original archives and the complete CSV/JSON inventory are uploaded to [the artwork release](https://github.com/atiffhussainkhan/Image/releases/tag/workplace-art-unverified-2026-10-05). Archive sizes and SHA-256 digests were verified against the local originals. The full index and sample contact sheets are also committed in this directory. `archive-manifest.json` contains download URLs, checksums and exact stored status. Licence status remains unverified.
