#!/usr/bin/env python3
"""Build the verified manifest for a Clink theme release."""
import hashlib
import json
import os
import pathlib

root = pathlib.Path(__file__).resolve().parents[1]
repository = os.environ.get("GITHUB_REPOSITORY", "anti-ltd/clink-themes-affiliate")
files = []
for path in sorted((root / "Themes").glob("*.clinktheme")):
    # macOS can create AppleDouble sidecars on external volumes.
    if not path.name.startswith("."):
        files.append((path, path.read_bytes()))

# Each distinct set of bytes gets a permanent release URL. A cached manifest
# must never point at a newer file with a different checksum.
identity = json.dumps([(path.name, hashlib.sha256(raw).hexdigest())
                       for path, raw in files], separators=(",", ":"))
version = "themes-" + hashlib.sha256(identity.encode()).hexdigest()
# Optional per-theme links, keyed by theme id. An affiliate is advertising in
# somebody else's app, so the destination belongs to the repository rather than
# to the theme document: only a publisher can attach one, and a theme that
# travels by file or QR code carries no link at all. Most themes have none.
# An entry is either a bare URL or {"url": ..., "description": ...}. The
# description is what the app shows before it sends anyone off to the site, so
# it is capped and kept to a single paragraph.
DESCRIPTION_LIMIT = 240
links = {}
links_path = root / "links.json"
if links_path.exists():
    raw_links = json.loads(links_path.read_text())
    known = {path.stem for path, _ in files}
    for theme_id, entry in sorted(raw_links.items()):
        if theme_id not in known:
            raise SystemExit(f"links.json names {theme_id!r}, which is not in Themes/")
        if isinstance(entry, str):
            entry = {"url": entry}
        if not isinstance(entry, dict):
            raise SystemExit(f"links.json entry for {theme_id!r} must be a URL or an object")
        extra = set(entry) - {"url", "description"}
        if extra:
            raise SystemExit(f"links.json entry for {theme_id!r} has unknown keys: {sorted(extra)}")
        url = entry.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise SystemExit(f"links.json entry for {theme_id!r} must be an https:// URL")
        description = entry.get("description")
        if description is not None:
            if not isinstance(description, str) or not description.strip():
                raise SystemExit(f"links.json description for {theme_id!r} must be non-empty text")
            if len(description) > DESCRIPTION_LIMIT:
                raise SystemExit(f"links.json description for {theme_id!r} is over {DESCRIPTION_LIMIT} characters")
            if "\n" in description:
                raise SystemExit(f"links.json description for {theme_id!r} must be a single paragraph")
        links[theme_id] = entry

themes = []
for path, raw in files:
    theme = json.loads(raw)
    entry = {
        "id": path.stem,
        "name": theme["name"],
        "version": version,
        "preview": theme,
        "asset": {
            "path": path.name,
            "url": f"https://github.com/{repository}/releases/download/{version}/{path.name}",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byteCount": len(raw),
        },
    }
    if path.stem in links:
        entry["link"] = links[path.stem]["url"]
        if links[path.stem].get("description"):
            entry["description"] = links[path.stem]["description"]
    themes.append(entry)
(root / "manifest.json").write_text(json.dumps({"version": version, "themes": themes}, indent=2) + "\n")
