# Asset Discovery & Crawl Strategy

The Image repository is the reusable master game-asset library.

## Parallel discovery lanes
1. 3D characters, creatures, rigs and animation libraries
2. Buildings, houses, interiors, furniture and exterior architecture
3. Environments, terrain, vegetation, roads, skyboxes and backgrounds
4. 2D characters, sprites, tilesets, icons, UI and VFX
5. Materials, PBR textures, HDRIs, props, vehicles, audio and supporting game-design assets

## Storage states
- DISCOVERED: source located, not yet mirrored.
- VERIFIED: licence and source checked.
- MIRRORED: an owned reusable copy exists in this GitHub repository's releases.
- FAILED: automated retrieval failed; reason recorded.
- EXCLUDED: unclear licence, redistribution restriction, duplicate, or unsafe provenance.

## Rules
- Prefer CC0/public-domain and permissive open-source assets.
- Preserve each pack's original licence and provenance.
- Do not call a source collected until a usable copy has been mirrored.
- Deduplicate by source identity plus SHA-256 where binaries are available.
- Do not mix incompatible or unclear licences into a supposedly CC0 pack.
- Large binary collections belong in GitHub Releases rather than normal Git history.

## Current expansion targets
See catalog/discovery_sources.csv. GitHub-hosted collections are mirrored as archives by the expansion workflow. Web-hosted libraries such as Poly Haven, itch.io and Kenney remain source-level discovery targets until their individual downloadable files are verified and retrieved.
