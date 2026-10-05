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
