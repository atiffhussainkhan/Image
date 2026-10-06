# Full audit checks

These scripts record the exhaustive checks run for the 6 October 2026 report in `catalog/audits/2026-10-06/REPORT.md`. They inspect images, all archive members (including nested ZIPs), every tracked Git blob, source/editor data, animation frame cells, search records and preview tiles.

They require the prepared workspace layout used by the report: `work/Image`, `work/animation`, release inventory JSON, downloaded release archives under `work/full-audit/downloads`, and the cleaned library under `outputs/game-art-library`. Python/Pillow and the ImageMagick/Ghostscript runtime are required. The original-archive hash check records the source folder on the audit host; adjust it when reproducing elsewhere. These are verification scripts, not a general downloader or a game-engine importer. No credentials are included.

For ordinary game import, use the active library index and `safe-import-policy.json`; an original source archive's availability is distinct from the usability of every member.
