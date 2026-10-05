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
