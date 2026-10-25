#!/usr/bin/env python3
"""Download GitHub Release attachments listed in catalog/ALL_RELEASE_ASSETS.json.
Uses stdlib only, records files by release tag, verifies expected byte count.
This is not an asset-content/license validation or archive extraction tool.
"""
import argparse
import json
import pathlib
import shutil
import urllib.request
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog" / "ALL_RELEASE_ASSETS.json"

def safe(text):
    if not text or text in (".", "..") or "/" in text or "\\\\" in text or chr(92) in text:
        raise ValueError("Unsafe release tag or asset name")
    return text

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--out", type=pathlib.Path, default=ROOT / "downloads" / "release-assets")
    args=p.parse_args()
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    tags=set(args.tag)
    if not args.all and not tags and not args.list:
        p.error("Choose --all, --tag TAG, or --list")
    for release in data["releases"]:
        tag=safe(release["tag"])
        if tags and tag not in tags: continue
        for asset in release["assets"]:
            name=safe(asset["name"])
            url=asset["url"]
            if not url.startswith("https://github.com/") or "/releases/download/" not in url:
                raise ValueError("Unexpected URL for "+name)
            target=args.out/tag/name
            expected=asset["bytes"]
            if args.list:
                print(tag, name, expected, url, sep=" | ")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.stat().st_size==expected:
                print("SKIP", target)
                continue
            temp=target.with_name(target.name+".part")
            # Restart interrupted partial downloads safely; do not trust partial files.
            if temp.exists(): temp.unlink()
            try:
                print("GET", tag, name, expected, flush=True)
                req=urllib.request.Request(url, headers={"User-Agent":"image-asset-library-downloader/1.0"})
                with urllib.request.urlopen(req, timeout=120) as response, temp.open("wb") as out:
                    shutil.copyfileobj(response, out, length=1024*1024)
                if temp.stat().st_size!=expected:
                    raise IOError(f"Wrong size for {name}: got {temp.stat().st_size}, expected {expected}")
                temp.replace(target)
            except Exception as exc:
                print("FAILED", name, repr(exc), file=sys.stderr)
                if temp.exists(): temp.unlink()
                return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
