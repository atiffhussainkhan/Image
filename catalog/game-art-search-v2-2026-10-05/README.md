# Cleaned game artwork library

This is the active, searchable version of the four user-supplied artwork archives. Unreadable, unconvertible, wholly transparent and uniform images are excluded. Original archives remain a historical backup; their inventory is superseded by this library.

## Find and import an image

1. Download `game-art-gallery.zip` from the [cleaned release](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05) and extract it.
2. In the extracted folder run `python3 -m http.server 8000`, then open `http://localhost:8000`. Search by subject, original name, collection, format or estimated colour. Open a picture to see its engine file and the exact bundle download.
3. Download that cleaned ZIP part, extract it and import the indexed PNG/JPEG path into Unity, Godot, Unreal, Phaser or another engine. Dimensions, transparency, hashes and animation frame timing are in the full record. Engine import settings remain project-specific.

Each original path has a stable asset ID. Byte-identical originals share one engine file. Duplicate aliases remain searchable; the gallery can hide duplicate entries. Every file name in cleaned bundles is ASCII and derived from its original SHA-256, avoiding damaged legacy names and cross-platform path conflicts.

## Search from any engine or automation

Download and extract `game-art-search-data.zip`. It includes a SQLite FTS5 index, gzip JSON/JSONL records, CSV and `search.py`. Keyword search uses the Python standard library:

```sh
python3 search.py "sheep" --limit 10
python3 search.py --id ASSET_ID
python3 search.py --id ASSET_ID --bundles ./downloaded-parts --extract-to ./game-assets
```

Results are JSON records containing the exact bundle URL and image path. Use these from editor tools, asset import scripts, or an AI agent. `assets.jsonl.gz` supports streaming without loading the entire index. SQLite contains an `assets` table with full JSON records and a `search` FTS5 table.

For natural-language visual search, also extract `game-art-semantic-search.zip` beside the search data and install `numpy onnxruntime tokenizers`:

```sh
python3 search.py "a red dragon with wings" --semantic --models models --vectors vectors --limit 10
```

The semantic bundle contains the text encoder and image embeddings. The vision encoder is required only to rebuild the index and is identified in `model-provenance.json`. CLIP suggestions and cosine scores are estimates, not verified descriptions or probabilities. Original filename/category keywords are kept alongside visual suggestions. Estimated colours describe rendered pixels, not verified object colours.

## Conversion and verification

- Raster images retain their decoded resolution; EXIF orientation is applied. Compatible ICC profiles are converted to sRGB. Unchanged JPEGs retain their original compression.
- EPS is rasterised from its bounding box to a 1024-pixel longest side. The source vector remains in the historical archive. WMF is imported through LibreOffice Draw, external white margins cropped, and capped at 1024 pixels. WMF exports retain white backgrounds; they are not claimed to have original transparency.
- Animated GIFs include decoded PNG frame sequences, durations and loop metadata. A nonempty frame is used as the preview when the first frame is empty. Blank timing frames within a valid animation are retained as part of that animation. All 411 inspected TIFF sources were single-page RGB photographs.
- Every generated engine image and thumbnail was decoded. Every thumbnail atlas was decoded and checked for the expected dimensions. ZIP CRC and membership checks were run. `quality-report.json` records counts and every excluded source; `bundle-manifest.json` records byte sizes and SHA-256 checksums.
- Small images have enlarged previews for inspection; tiny bitmap icons use nearest-pixel scaling, and other previews use Lanczos scaling. Engine files retain their recorded native dimensions.
- Full-resolution checks distinguish empty images from faint artwork and white silhouettes with meaningful alpha masks. Human preview review is a reproducible sample across formats, not a claim to have inspected every picture manually.

## Rights and source history

Licences for these user-supplied archives remain **unverified**. Conversion and indexing do not grant reuse rights. This collection remains separate from the repository's approved, licence-clear packs. Model files have their own provenance and licence; the CLIP licence does not apply to the artwork.

The historical source release is [workplace-art-unverified-2026-10-05](https://github.com/atiffhussainkhan/Image/releases/tag/workplace-art-unverified-2026-10-05). The active cleaned library excludes all sources listed in `quality-report.json`.
