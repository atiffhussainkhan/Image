#!/usr/bin/env python3
"""Fetch direct-download assets from catalog/assets.json.

Only entries with a direct http(s) download_url are downloaded automatically.
Interactive store pages and folder links are deliberately skipped so licence/source
review remains explicit.
"""
from __future__ import annotations
import json, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "assets.json"
OUT = ROOT / "downloads"
OUT.mkdir(exist_ok=True)

assets = json.loads(CATALOG.read_text(encoding="utf-8"))
for item in assets:
    url = item.get("download_url")
    if not url or "drive.google.com/drive/folders/" in url:
        print(f"SKIP {item['id']}: manual/source-page retrieval required")
        continue
    suffix = pathlib.Path(url.split("?")[0]).suffix or ".bin"
    dest = OUT / f"{item['id']}{suffix}"
    if dest.exists():
        print(f"HAVE {dest.name}")
        continue
    print(f"GET  {item['id']} <- {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"OK   {dest} ({dest.stat().st_size} bytes)")
    except Exception as exc:
        print(f"FAIL {item['id']}: {exc}")
