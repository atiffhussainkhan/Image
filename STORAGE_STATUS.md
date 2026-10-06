# Storage Status

This file answers one question: **is the actual asset pack stored in this GitHub repository's Releases, or is it only catalogued?**

## Stored and reusable now

There are **28 stored asset packs and 1 stored reference catalogue**. All eight formerly unresolved packs are stored in the [catalog completion release](https://github.com/atiffhussainkhan/Image/releases/tag/catalog-completion-2026-10-06). See its [validation report](catalog/catalog-completion-2026-10-06/REPORT.md).

## Still unresolved

None of the eight catalogued asset packs remain unstored.

## Rule for AI agents
- `stored` = safe to locate inside this repository's Releases.
- `unresolved_catalogued` = metadata/provenance only; do not claim the asset itself is present.
- Never use an external source URL as a substitute for a stored pack when the task requires repository-owned assets.

## User-supplied artwork

Four original artwork archives (102,393 indexed files) are stored in the [workplace artwork release](https://github.com/atiffhussainkhan/Image/releases/tag/workplace-art-unverified-2026-10-05). See `catalog/workplace-art-unverified-2026-10-05/archive-manifest.json` for verified checksums and downloads, and its README for game-art suitability. Their licences remain unverified; they are separate from the approved reusable packs.

## Active cleaned artwork library

The [cleaned search gallery](catalog/game-art-search-v2-2026-10-05/README.md) is the active index for the four user-supplied archives. Unreadable, empty and unconvertible sources are excluded from its searchable records and cleaned PNG/JPEG packs. Use `catalog/user-artwork-active-library.json` for machine discovery. JSON/JSONL, SQLite, CSV and natural-language search are available in the [cleaned release](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05). Original archives remain historical backups; licences remain unverified.

## Complete file and image audit

The [6 October 2026 audit](catalog/audits/2026-10-06/REPORT.md) checked Image and animation, all 54 Image release files, 104 ZIPs including nested archives, and 408,439 file occurrences. All 110,490 cleaned master images and all 132 animation frames passed. For older/source packs, consult the [safe import policy](catalog/audits/2026-10-06/safe-import-policy.json) and [corrected preview overrides](catalog/audits/2026-10-06/format-overrides.json): stored availability does not certify every member as standalone engine art.
