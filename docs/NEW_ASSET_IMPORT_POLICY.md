# Newly discovered game assets — verification and search policy (2026-10-25)

These 24 discovery leads are **NOT downloaded, verified game-ready, or approved for redistribution**. See `catalog/new-asset-candidates-2026-10-25.json`. **Do not describe them as present game binaries.**

Existing stored assets are listed in `catalog/ALL_RELEASE_ASSETS.json` and are downloadable separately from git clone. The existing cleaned image search index is `catalog/game-art-search-v2-2026-10-05/assets.jsonl.gz`; it has 110,490 unique technically decoded images but licence status remains unverified for the user-supplied archives.

Search with `python3 scripts/search_game_assets.py "animated character"` (metadata search, not asset binary retrieval). Search results distinguish discovery candidates, previously stored release attachments, and indexed cleaned imagery.

An asset may be promoted to **approved** only after (1) official source and exact redistribution licence checked; (2) real archive downloaded with SHA256 recorded; (3) archive and file integrity checked; (4) image/rig/animation frames, timing, external dependencies verified; (5) actual preview + engine import/playback tested; (6) tags, stable IDs, previews and exact downloadable paths published; (7) search AND binary-retrieval tested from another independent tool. No access claim can be universal across AI agents without running each agent's test.

Neither links nor metadata are evidence that a model can access the full 14 GB of binary release archives. Keep unverified sources in staging.
