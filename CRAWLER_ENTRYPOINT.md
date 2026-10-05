# CRAWLER ENTRYPOINT

Canonical machine-readable search list: `catalog/MASTER_ASSET_INDEX.json`

Tabular search list: `catalog/MASTER_ASSET_INDEX.csv`

Human semantic index: `AI_ASSET_INDEX.md`

Storage truth file: `catalog/storage_status.json`

## Crawler rule
Treat an item as locally usable only when:
- `availability = "stored"`
- `stored_copy = true`
- `release_asset` is non-empty

Do not treat `reference_only` or `pending_copy` entries as uploaded assets.

## Suggested crawler query fields
`id`, `name`, `record_type`, `availability`, `license`, `categories`, `search_terms`, `release_asset`, `source_url`.

## Active cleaned artwork library

The [cleaned search gallery](catalog/game-art-search-v2-2026-10-05/README.md) is the active index for the four user-supplied archives. Unreadable, empty and unconvertible sources are excluded from its searchable records and cleaned PNG/JPEG packs. Use `catalog/user-artwork-active-library.json` for machine discovery. JSON/JSONL, SQLite, CSV and natural-language search are available in the [cleaned release](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05). Original archives remain historical backups; licences remain unverified.
