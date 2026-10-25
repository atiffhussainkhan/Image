# START HERE — AI / Cursor / Grok / Claude / Codex / game engines

**Important:** The ordinary Git tree is only ~440 MB of catalogues, previews and scripts. **It is NOT the whole asset library.** Most binary art is distributed separately through six GitHub Releases (~13.89 GB across 65 release files).

## Read in order
1. `ASSET_ACCESS.md` (this file)
2. `catalog/ALL_RELEASE_ASSETS.json` (complete machine-readable list of 65 downloadable release files with exact bytes and direct links)
3. `catalog/game-art-search-v2-2026-10-05/README.md` (searchable 110,490 unique cleaned master images; 114,852 indexed aliases/entries)
4. `catalog/audits/2026-10-06/REPORT.md`, `catalog/audits/2026-10-06/safe-import-policy.json` and `catalog/catalog-completion-2026-10-06/REPORT.md`

## HOW TO ACCESS ALL BYTES (not merely discover filenames)
Use a terminal/network-enabled agent: `python3 scripts/download_release_assets.py --list` or `python3 scripts/download_release_assets.py --all --out downloads/release-assets`. Requires enough free disk (more than 14 GB, substantially more if extracting archives). The downloader fetches **every listed release attachment**, not the Git tree, with size validation; reruns skip already downloaded files. To retrieve just one release use `--tag TAG`. It does **not** extract or verify artistic quality, licences, gameplay import, all archive members, or checksum provenance. Do not mistake metadata-only access for pixel access. Check file hashes against release SHA256SUMS / audit evidence where available.

Use a local searchable index by downloading `game-art-search-data.zip` (and for visual search `game-art-semantic-search.zip`) from the `game-art-search-v2-2026-10-05` release; download required cleaned ZIP bundle(s) for actual pixel data. Follow the cleaned-gallery README for command examples.

**Important safety / licensing:** The cleaned artwork derived from four user-supplied archives has **unverified redistribution/commercial-use rights**, even though the images passed historic decoding checks. The historic audit includes 2,195 excluded records. Some older packs have conditional/blank/sidecar and non-engine formats. Do not tell users all files are game-ready, or redistribute unverified art as licence-clear.

## Limitations for cloud agents
- Code search, git clone, and standard repository browsing **do not automatically pull Release files**.
- An AI platform may have no network/terminal access, insufficient quota/storage, or an indexing/file-size limit. This guide cannot override that platform.
- To say "the model can access all 14 GB", it must actually download/extract the required archives or have an external mounted asset store / retrieval service.
- A successful Git clone of this repo alone does **not** download Release attachments.
