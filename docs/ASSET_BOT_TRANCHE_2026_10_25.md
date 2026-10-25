# Asset Bot tranche - 2026-10-25

Eleven source streams collected by an automated asset bot, published as one GitHub
Release. Every file was licence-checked before download: only assets permitting
**commercial use and derivative works** were kept. NC (non-commercial) and
ND (no-derivatives) assets, and assets whose licence could not be verified, were
excluded at source.

- **Release:** [asset-bot-tranche-2026-10-25](https://github.com/atiffhussainkhan/Image/releases/tag/asset-bot-tranche-2026-10-25)
- **Files:** 38,234
- **Archive bytes:** 1,573,216,544 (1500.3 MB)
- **Sources:** 11

## Verification

| check | result |
|---|---|
| every indexed file present on disk | pass |
| every raster file decodes (PNG/JPG/GIF/TGA/PSD) | pass |
| every `.blend` file carries a valid Blender header | pass |
| zero-byte files | none |
| release asset byte count matches local | pass |
| release asset sha256 matches local after re-download | pass |

## Published packs

| archive | files | size | sha256 | licence | source |
|---|---|---|---|---|---|
| `kenney-cc0-game-art-packs.zip` | 7,031 | 41.1 MB | `7a98218bae9d05fb` | CC0-1.0 | https://kenney.nl |
| `polyhaven-cc0-hdris-textures-models.zip` | 80 | 105.2 MB | `9163d87133a0a0b1` | CC0-1.0 | https://polyhaven.com |
| `ambientcg-cc0-pbr-materials.zip` | 80 | 114.9 MB | `09dcdfbb9c1691cc` | CC0-1.0 | https://ambientcg.com |
| `godot-asset-library-3d-animation.zip` | 51 | 1.5 MB | `d1fdd2a50ea64031` | PER_ASSET | https://godotengine.org/asset-library |
| `lpc-rpg-character-sprites.zip` | 5,804 | 28.3 MB | `bc9c9292c84f2658` | CC-BY-SA-3.0 | https://github.com/OpenGameArt/LiberatedPixelCup |
| `game-icons-svg-icon-set.zip` | 4,242 | 4.0 MB | `350a5fa6b1846515` | CC-BY-3.0 | https://game-icons.net |
| `archive-org-cc0-texture-sprite-packs.zip` | 6,916 | 621.8 MB | `e526d78f8aeef0d8` | MIXED | https://archive.org |
| `opengameart-cc0-2d-art.zip` | 13,822 | 168.6 MB | `c9cf0eb68725a023` | CC0-1.0;CC-BY | https://opengameart.org |
| `cleveland-museum-cc0-artwork.zip` | 75 | 267.8 MB | `303dd6ec60e25826` | CC0-1.0 | https://www.clevelandart.org/art |
| `openverse-cc0-imagery.zip` | 79 | 15.0 MB | `d51c2bf7dc7304b0` | CC0-1.0;PDM | https://openverse.org |
| `nasa-public-domain-space-imagery.zip` | 54 | 132.1 MB | `f77de07d04a45d0f` | PUBLIC-DOMAIN | https://images.nasa.gov |

## Layout inside each archive

```
assets/<source>/...            the assets
assets/<source>/ATTRIBUTION.csv  title, author, licence, licence URL, source page
assets/<source>/SOURCE.txt      provenance note for the stream
```

Upstream `README` / `LICENSE` files are preserved inside the archives.

## Attribution

CC-BY and CC-BY-SA assets require credit. `ATTRIBUTION.csv` inside each archive is
the per-file credit list. `catalog/MASTER_ASSET_INDEX.csv` carries the pack-level
record.

## Re-running the collector

The collector lives outside this repository and is not archived here. It reads the
same licence policy as `docs/LICENSE_POLICY.md`: CC0/public-domain preferred,
MIT/BSD only with their notice retained, and nothing with unclear terms.

## Themed library bundles

The same files, regrouped by what you would actually look for. These are an alternate
view of the per-source archives above - the underlying files are identical, so do not
count them twice. Grab only the bundle you need instead of the full 1.5 GB.

| bundle | size | contains |
|---|---|---|
| `character-and-icon-kit.tar.gz` | 225.6 MB | characters, icons, ui, 2d, sprites |
| `3d-model-kit.tar.gz` | 40.1 MB | 3d, models, props, kits, animation |
| `world-building-kit.tar.gz` | 479.3 MB | tiles, tilesets, backgrounds, textures, hdris, skyboxes, 2d |
| `audio-fx-kit.tar.gz` | 152.2 MB | audio, sfx, music |

Inside each bundle the tree is organised by category:

```
characters/  3d-models/  animation/  textures/  hdris-skyboxes/
icons-ui/  tiles-sprites/  backgrounds/  audio/  reference/
```
