# Complete repository image audit — 6 October 2026

**The cleaned image library and the animation repository pass exhaustive technical checks. I cannot label the entire repositories “100% usable images”: they also contain original source backups, models, audio, editor files, filesystem metadata, deliberate blank/solid files and catalogue entries without stored downloads.** Binary data is normal for PNG, JPEG, WebP and game models; decoding and content checks establish whether an image is valid.

## Scope and evidence

| Repository | Tracked files checked | Audited commit | Result |
|---|---:|---|---|
| [atiffhussainkhan/Image](https://github.com/atiffhussainkhan/Image) | 1,935 | `3faf784ed92aa9393d33b6d02150d5140d1fc20e` | Every tracked blob matched GitHub |
| [atiffhussainkhan/animation](https://github.com/atiffhussainkhan/animation) | 19 | `cfd2815af72d890a4bbc349c3d8a455831f207ec` | Every tracked blob matched GitHub |

- **54 GitHub release files** verified for size and SHA-256, covering every file in all five Image releases. Four original archive hashes and their earlier complete source audit were reused; original unusable sources remain documented in the exclusion ledger.
- **104 ZIP archives**, including every nested ZIP, completely read. Every member was checked by the ZIP CRC decoder; **408,439 file occurrences** inspected, including repeated packs, metadata and previews. No archive-member CRC failure was found.
- Raster headers, dimensions, full pixel decoding and animation frames checked. SVG XML plus actual rendering checked. PSD/HDR warnings retried with the appropriate renderer. Aseprite header/frame/chunk/cel data checked against the [official format specification](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md).
- All 1,954 tracked Git blobs matched the audited GitHub commits. Metadata corrections and new override files described below were subsequently prepared separately and verified.

## Cleaned artwork — pass

| Check | Full coverage | Result |
|---|---:|---|
| Unique PNG/JPEG master images | **110,490** | Every image decoded; none empty, fully transparent or uniform |
| Search records | **114,852** | Every record matched actual ZIP bytes, size, dimensions, format and member path |
| Additional animation frame files | **4,312** | Every frame matched its stored bytes; six blank/solid timing frames intentionally preserved |
| Occupied preview tiles | **110,490** | Every tile inspected; zero uniform or extremely low-contrast tiles |
| Preview atlases | **1,760** | All decoded and dimensions checked |
| Search shards | All | IDs exactly cover the active index |
| SQLite / semantic vectors | All active entries | Database integrity, vector coverage/norms and extraction checks passed |

**2,195 unusable, unconvertible or non-image entries are excluded** from the active searchable library and cleaned packs. The original archives remain historical backups; their presence does not mean every original member is a usable image. See the [existing removal report](https://github.com/atiffhussainkhan/Image/blob/main/catalog/game-art-search-v2-2026-10-05/quality-report.json).

## Animation repository — pass

All **12 WebP sheets and 132 declared animation frames** decoded and contained visible artwork. Manifest dimensions, byte counts, frame counts, frame rates and grid positions matched. Unused grid cells are expected padding, not missing declared frames.

## Findings and corrections

1. **Four `.png` previews contained JPEG data.** Proper PNG replacements were created; decoded pixels are identical. Use [format-overrides.json](format-overrides.json).
2. **One SVG rendered empty because it lacked a canvas.** All six drawing shapes were measured in the browser; explicit bounds with a 5% margin were added. The [corrected SVG](corrected-previews/gameCharacter.svg) and [engine PNG](corrected-previews/gameCharacter.png) render nonempty, complete artwork without changing the drawing geometry.
3. **Four unreadable PNG sidecars** occur under `__MACOSX/._*` in an older source archive. They are excluded from game-image selection. Other AppleDouble sidecars are also filesystem metadata, not artwork; four apparent Illustrator failures were confirmed as AppleDouble resource forks.
4. **71 raster warnings** were decoder limitations and passed secondary decoding. All **715 Aseprite sources** passed structural/cel checks; all **28 actual Illustrator sources** rendered. Metadata sidecars are excluded from those artwork counts.
5. **One catalogue size was wrong by one byte.** `opengameart-modular-vector-characters.zip` is 71,527,593 bytes. The storage record and both master indexes were corrected.
6. **1,494 SVG occurrences lack explicit canvas dimensions or `viewBox`.** Their vector data is present, but reliable direct import depends on the importer or repaired bounds. One empty default render was corrected; the other entries remain flagged in [conditional-vectors.csv](conditional-vectors.csv).
7. **392 fully transparent and 858 uniform raster occurrences** were found in source/older packs, including four transparent and two solid cleaned-animation timing frames. These files decoded; some are font spaces, neutral textures or padding. They require context and must not be selected automatically as standalone artwork. No such file is a cleaned master-image entry.
8. The two zero-byte files are `.nojekyll` and `.gitkeep`, expected package/website markers—not images.

## Catalogue entries with no stored archive

These eight records are explicitly unavailable; a source link is not a repository-owned asset:

- `quaternius-ultimate-animated-character`: Catalogued and download step ran, but no owned archive is present in any release yet.
- `quaternius-ultimate-animated-animals`: Catalogued; no owned archive present.
- `quaternius-animated-mech`: Catalogued; no owned archive present.
- `kaykit-dungeon`: Original catalogued pack not stored; remastered dungeon pack is stored separately.
- `avramania-nature-terrain`: Catalogued; host did not yield a directly stored archive in current releases.
- `mastjie-household-goods`: Catalogued; host did not yield a directly stored archive in current releases.
- `barnabe-wild-rigged-character`: Catalogued; host did not yield a directly stored archive in current releases.
- `jean-charpentier-lowpoly`: Catalogued; host did not yield a directly stored archive in current releases.

No replacement asset or invented file was inserted to conceal a missing download. The original Dungeon entry is separate from the stored Dungeon Remastered pack.

## What this verifies—and its limits

Use the [cleaned active library](https://github.com/atiffhussainkhan/Image/releases/tag/game-art-search-v2-2026-10-05), the animation pack, the corrected overrides and [safe-import-policy.json](safe-import-policy.json) for future asset selection. Original/older packs remain source archives; metadata, blank contextual files and conditional vectors are not certified standalone engine art.

The audit checked every stored file in scope automatically. Representative previews and the repaired character were inspected visually; this is **not** a claim of manually viewing 408,439 files. Model/audio/editor binaries passed byte/hash/archive integrity, but every gameplay-engine importer was not executed. Semantic labels remain model suggestions, not individually human-verified descriptions. User-supplied artwork licences remain unverified; technical readability does not establish redistribution rights.

## Downloadable detailed evidence

- [Machine-readable final summary](audit-summary.json)
- [Every inspected file, status, dimensions and SHA-256 — compressed JSONL](file-audit.jsonl.gz)
- [Every archive and member count](archives.csv)
- [Every release file and verified checksum](release-files-audit.json)
- [Contextual issues and resolved decoder warnings](issues.csv)
- [Cleaned master-image checks](clean-master-image-audit.json), [index/ZIP crosschecks](index-content-crosscheck.json), [all preview tiles](preview-tile-audit.json)
- [All animation frames](animation-frame-audit.json), [secondary render checks](supplemental-format-audit.json), [editor-source checks](editor-source-audit.json)
- [Format corrections](format-overrides.json), [excluded sidecars](resolved-sidecar-exclusions.json), [conditional vectors](conditional-vectors.csv)
