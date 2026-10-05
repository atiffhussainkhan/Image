#!/usr/bin/env python3
import html
import pathlib
import re
import urllib.parse
import urllib.request
import zipfile

PAGE = "https://opengameart.org/content/3d-character-pack"
OUTDIR = pathlib.Path("staging/oga-3d-character-pack")
STATUS = pathlib.Path("release-assets/tranche2-status.txt")
OUTDIR.mkdir(parents=True, exist_ok=True)
STATUS.parent.mkdir(parents=True, exist_ok=True)

def log(message: str) -> None:
    with STATUS.open("a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\n")

try:
    request = urllib.request.Request(PAGE, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", errors="ignore")
except Exception as exc:
    log(f"FAILED,oga-3d-character-pack,{PAGE},page_fetch:{exc}")
    raise SystemExit(0)

hrefs = re.findall(r'''href=["']([^"']+\.zip(?:\?[^"']*)?)["']''', body, flags=re.I)
urls = []
for href in hrefs:
    url = urllib.parse.urljoin(PAGE, html.unescape(href))
    if url not in urls:
        urls.append(url)

downloaded = []
for idx, url in enumerate(urls, 1):
    filename = pathlib.Path(urllib.parse.urlparse(url).path).name or f"character-pack-{idx}.zip"
    destination = OUTDIR / filename
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as f:
            f.write(response.read())
        if destination.stat().st_size > 1024:
            downloaded.append(destination)
        else:
            destination.unlink(missing_ok=True)
    except Exception as exc:
        log(f"FAILED,oga-3d-character-pack,{url},download:{exc}")
        destination.unlink(missing_ok=True)

if not downloaded:
    log(f"FAILED,oga-3d-character-pack,{PAGE},no_zip_files_discovered")
    raise SystemExit(0)

bundle = pathlib.Path("release-assets/oga-3d-character-pack.zip")
with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in downloaded:
        archive.write(path, path.relative_to(pathlib.Path("staging")))

log(f"MIRRORED,oga-3d-character-pack,{PAGE},files={len(downloaded)}")
print(f"Created {bundle} from {len(downloaded)} archive(s)")
