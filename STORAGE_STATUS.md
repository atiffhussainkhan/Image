# Storage Status

This file answers one question: **is the actual asset pack stored in this GitHub repository's Releases, or is it only catalogued?**

## Stored and reusable now
There are **21 stored pack archives** across the three releases. Future AI agents should use `catalog/storage_status.json` and `AI_ASSET_INDEX.md` before selecting assets.

## Still unresolved
The following catalogued packs do **not** yet have a corresponding owned archive in the releases:
- **quaternius-ultimate-animated-character** — Catalogued and download step ran, but no owned archive is present in any release yet.
- **quaternius-ultimate-animated-animals** — Catalogued; no owned archive present.
- **quaternius-animated-mech** — Catalogued; no owned archive present.
- **kaykit-dungeon** — Original catalogued pack not stored; remastered dungeon pack is stored separately.
- **avramania-nature-terrain** — Catalogued; host did not yield a directly stored archive in current releases.
- **mastjie-household-goods** — Catalogued; host did not yield a directly stored archive in current releases.
- **barnabe-wild-rigged-character** — Catalogued; host did not yield a directly stored archive in current releases.
- **jean-charpentier-lowpoly** — Catalogued; host did not yield a directly stored archive in current releases.

These must not be treated as locally available until a release asset exists.

## Rule for AI agents
- `stored` = safe to locate inside this repository's Releases.
- `unresolved_catalogued` = metadata/provenance only; do not claim the asset itself is present.
- Never use an external source URL as a substitute for a stored pack when the task requires repository-owned assets.
