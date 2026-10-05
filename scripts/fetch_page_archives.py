#!/usr/bin/env python3
import html
import pathlib
import re
import sys
import urllib.parse
import urllib.request
import zipfile

SOURCES = {
    "quaternius-ultimate-animated-animals": "https://quaternius.com/packs/ultimateanimatedanimals.html",
    "quaternius-animated-mech": "https://quaternius.com/packs/animatedmech.html",
    "kaykit-dungeon": "https://kaylousberg.itch.io/kaykit-dungeon-pack",
    "avramania-nature-terrain": "https://avramania.itch.io/nature-terrain",
    "mastjie-household-goods": "https://mastjie.itch.io/low-poly-household-goods",
    "barnabe-wild-rigged-character": "https://barnabe-wild.itch.io/low-poly-rigged-character",
    "jean-charpentier-lowpoly": "https://jeancharpentier.itch.io/cc0-lowpoly-pack",
    "opengameart-modular-vector-characters": "https://opengameart.org/content/free-cc0-modular-animated-vector-characters-2d",
}

root = pathlib.Path("staging/packs")
release = pathlib.Path("release-assets")
logs = pathlib.Path("staging/logs")
root.mkdir(parents=True, exist_ok=True)
release.mkdir(parents=True, exist_ok=True)
logs.mkdir(parents=True, exist_ok=True)
failure_log = logs / "failed_sources.txt"

def fail(msg: str):
    with failure_log.open("a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")

for slug, page in SOURCES.items():
    dest = root / slug
    dest.mkdir(parents=True, exist_ok=True)
    source_page = dest / "SOURCE_PAGE.html"
    try:
        req = urllib.request.Request(page, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            source_page.write_bytes(r.read())
    except Exception as exc:
        fail(f"{slug} | {page} | source page unavailable: {exc}")
        continue

    txt = source_page.read_text(errors="ignore")
    hrefs = [html.unescape(x) for x in re.findall(r'''href=["']([^"']+)["']''', txt, flags=re.I)]
    candidates = []
    for href in hrefs:
        url = urllib.parse.urljoin(page, href)
        low = url.lower().split("?")[0]
        if any(low.endswith(ext) for ext in (".zip",".7z",".rar",".tar.gz",".tgz")):
            candidates.append(url)

    downloaded = []
    for i, url in enumerate(dict.fromkeys(candidates), 1):
        suffix = pathlib.Path(urllib.parse.urlparse(url).path).suffix or ".bin"
        out = dest / f"download-{i}{suffix}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r, out.open("wb") as f:
                f.write(r.read())
            if out.stat().st_size >= 1024:
                downloaded.append(out)
            else:
                out.unlink(missing_ok=True)
        except Exception:
            out.unlink(missing_ok=True)

    if not downloaded:
        fail(f"{slug} | {page} | no directly downloadable archive discovered")
        continue

    zpath = release / f"{slug}.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in dest.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(root))
    print(f"PACKAGED {slug} -> {zpath}")
