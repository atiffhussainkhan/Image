# GitHub-first asset storage and discovery policy

Canonical destination: https://github.com/atiffhussainkhan/Image

## Storage
- Store approved, redistributable asset binaries in GitHub Releases (large archives) or tracked `assets/` paths (suitable small files).
- Keep metadata, searchable catalogues, source attribution, SHA-256 hashes and retrieval instructions in this GitHub repository.
- Do not establish ChatGPT conversations, ChatGPT Library, or temporary chat attachments as an archival destination.
- Processing tools may require ephemeral working files, but publication is not complete until GitHub upload succeeds and links and hashes are checked.
- Do not mark a discovery candidate, URL, or catalogue record as uploaded binary data.
- Never publish third-party assets with unclear redistribution permission in a public Release. Record those as unverified candidates only.

## Discovery
- Start at `ASSET_ACCESS.md`, `AI_ASSET_INDEX.md`, and `catalog/ALL_RELEASE_ASSETS.json`.
- Use `python3 scripts/search_game_assets.py "search terms" --scope all` for indexed filenames and metadata.
- For the cleaned image gallery, follow `catalog/game-art-search-v2-2026-10-05/README.md`. Its technical image search index does not establish licences.
- Searchable text catalogues and semantic indexes are distinct from access to actual pixels: retrieve the relevant Release files for binary use.
- Index every newly published pack with filename, category, tags, format, byte size, source URL, licence evidence, redistribution status, content SHA-256, exact GitHub Release asset link and verification status.
- Never claim universal visual/semantic search or full binary accessibility merely because filenames appear in an index.

## Acquisition gate
1. Verify publisher and exact file licence plus redistribution rights.
2. Download and scan archives without following symlinks or unsafe paths; enforce size limits.
3. Hash archive and extracted files; remove exact duplicates while retaining legitimate variants.
4. Publish approved binaries to the repository/Releases.
5. Update GitHub catalogue and search index.
6. Verify live GitHub links and stored byte count/hash before marking status as stored.

This policy does not claim that pending discoveries have been downloaded or approved.
