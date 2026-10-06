# Image — Game Asset Mega Library

A curated library/index of high-quality, licence-clear game-development assets collected for the Mega Repo project.

## Scope
- 2D sprites, transparent PNG animation sequences, vectors
- 3D characters, creatures, models and rigs
- Character animation packs
- UI, icons and VFX
- Environments, terrain, props and textures

## Curation rules
Only assets with a clear reusable licence and a traceable original/source page belong here. Avoid unclear licences, duplicates and low-quality filler. Keep source and licence metadata with every pack.

## Current catalogue
The first restored tranche is in `catalog/assets.csv` and `catalog/assets.json`. It includes the previously identified Quaternius, KayKit, OpenGameArt, Avramania, mastjie, Barnabe Wild, Jean Charpentier and Jam-Ready sources.

## Binary asset policy
Large upstream archives are not silently copied without provenance. Exact source/download locations are recorded. Direct-download assets supported by the retrieval script can be fetched into `downloads/`, which is intentionally ignored by Git until reviewed.

## Repository layout
```
catalog/            machine-readable asset catalogue
docs/               source/licence and curation notes
scripts/            reproducible retrieval helpers
downloads/          local fetched archives (ignored until reviewed)
assets/             reviewed assets intended for repository inclusion
```

## Licence
This repository's own metadata/scripts may be reused, but **each third-party asset retains its own licence**. See `docs/LICENSE_POLICY.md` and each catalogue entry before redistributing an upstream asset.

## AI-first discovery
For future AI agents and project automation, start with:
- `AI_ASSET_INDEX.md` — human-readable semantic search map
- `catalog/storage_status.json` — exact stored-vs-unresolved state
- `catalog/repository_manifest.json` — machine-readable repository purpose and release locations
- `catalog/assets.json` and `catalog/discovery_sources.csv` — provenance and catalogue metadata

**Rule:** external source URLs are provenance only. When a stored release asset exists, AI agents should use the repository-owned copy instead of the external source.

## Workplace artwork collection (unverified)

The [workplace artwork audit](catalog/workplace-art-unverified-2026-10-05/README.md) indexes 102,393 files from four user-supplied archives. It is separate from the approved catalogue above. Sources and redistribution licences are unverified. Use its `index.html` search viewer to filter original filenames/categories, format and technical readiness. The [archive manifest](catalog/workplace-art-unverified-2026-10-05/archive-manifest.json) records exact stored-versus-local status and checksums.

## Active cleaned artwork library

The [cleaned search gallery](catalog/game-art-search-v2-2026-10-05/README.md) is the active index for the four user-supplied archives. Unreadable, empty and unconvertible sources are excluded from its searchable records and cleaned PNG/JPEG packs. Use `catalog/user-artwork-active-library.json` for machine discovery. JSON/JSONL, SQLite, CSV and natural-language search are available in the [cleaned release](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05). Original archives remain historical backups; licences remain unverified.

## Complete file and image audit

The [6 October 2026 audit](catalog/audits/2026-10-06/REPORT.md) checked Image and animation, all 54 Image release files, 104 ZIPs including nested archives, and 408,439 file occurrences. All 110,490 cleaned master images and all 132 animation frames passed. For older/source packs, consult the [safe import policy](catalog/audits/2026-10-06/safe-import-policy.json) and [corrected preview overrides](catalog/audits/2026-10-06/format-overrides.json): stored availability does not certify every member as standalone engine art.

## Catalog completion

All eight formerly unstored packs are now available in the [catalog completion release](https://github.com/atiffhussainkhan/Image/releases/tag/catalog-completion-2026-10-06). Download links, categories and sizes are in the canonical index. [Validation report](catalog/catalog-completion-2026-10-06/REPORT.md).
