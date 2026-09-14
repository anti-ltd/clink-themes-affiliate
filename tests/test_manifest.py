import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlparse


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        source = Path(__file__).resolve().parents[1]
        (self.root / "tools").mkdir()
        shutil.copyfile(source / "tools/build-manifest.py",
                        self.root / "tools/build-manifest.py")
        (self.root / "Themes").mkdir()
        (self.root / "Themes/keychron-light.clinktheme").write_text(json.dumps({"id": "keychron-light", "name": "Test fixture", "mechanicalInnerRadius": 4}))
        for path in (source / "Themes").glob("*.clinktheme"):
            if not path.name.startswith("."):
                shutil.copyfile(path, self.root / "Themes" / path.name)

    def build(self):
        subprocess.run([sys.executable, str(self.root / "tools/build-manifest.py")],
                       env={**os.environ, "GITHUB_REPOSITORY": "example/themes"}, check=True)
        return json.loads((self.root / "manifest.json").read_text())

    def test_empty_catalog(self):
        for path in (self.root / "Themes").glob("*.clinktheme"):
            path.unlink()
        self.assertEqual(self.build()["themes"], [])

    def test_manifest_verifies_every_asset_and_uses_versioned_repository_urls(self):
        manifest = self.build()
        self.assertTrue(manifest["version"].startswith("themes-"))
        for pack in manifest["themes"]:
            asset = pack["asset"]
            raw = (self.root / "Themes" / asset["path"]).read_bytes()
            self.assertEqual(pack["preview"], json.loads(raw))
            self.assertEqual(pack["id"], pack["preview"]["id"])
            self.assertEqual(pack["version"], manifest["version"])
            self.assertEqual(asset["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(asset["byteCount"], len(raw))
            self.assertLessEqual(len(raw), 128_000)
            self.assertEqual(asset["url"],
                             f'https://github.com/example/themes/releases/download/{manifest["version"]}/{asset["path"]}')

    def test_repeat_builds_and_appledouble_sidecars_do_not_change_release(self):
        first = self.build()
        (self.root / "Themes/._keychron-light.clinktheme").write_bytes(b"not JSON")
        self.assertEqual(first, self.build())

    def test_cached_manifest_still_downloads_its_original_bytes_after_update(self):
        published = {}

        def publish(manifest):
            for pack in manifest["themes"]:
                url = pack["asset"]["url"]
                raw = (self.root / "Themes" / pack["asset"]["path"]).read_bytes()
                if url in published:
                    self.assertEqual(published[url], raw)
                published[url] = raw

        cached = self.build()
        publish(cached)
        path = self.root / "Themes/keychron-light.clinktheme"
        theme = json.loads(path.read_text())
        theme["mechanicalInnerRadius"] += 1
        path.write_text(json.dumps(theme) + "\n")
        updated = self.build()
        publish(updated)
        self.assertNotEqual(cached["version"], updated["version"])
        for manifest in (cached, updated):
            for pack in manifest["themes"]:
                asset = pack["asset"]
                self.assertEqual(hashlib.sha256(published[asset["url"]]).hexdigest(),
                                 asset["sha256"])
                self.assertEqual(len(published[asset["url"]]), asset["byteCount"])
                self.assertIn(manifest["version"], urlparse(asset["url"]).path)

    def test_links_are_optional_per_theme_and_never_touch_the_release(self):
        # A link is repository metadata, not theme bytes: adding one must not
        # move any theme to a new release URL, or cached manifests would stop
        # resolving to the assets they were published with.
        before = self.build()
        self.assertTrue(all("link" not in pack for pack in before["themes"]))
        (self.root / "links.json").write_text(json.dumps(
            {"keychron-light": "https://example.com/keys"}))
        after = self.build()
        self.assertEqual(before["version"], after["version"])
        linked = {pack["id"]: pack.get("link") for pack in after["themes"]}
        self.assertEqual(linked.pop("keychron-light"), "https://example.com/keys")
        self.assertTrue(all(link is None for link in linked.values()),
                        "themes absent from links.json must carry no link")

    def test_a_description_rides_with_its_link_and_is_bounded(self):
        (self.root / "links.json").write_text(json.dumps({"keychron-light": {
            "url": "https://example.com/keys",
            "description": "A shop that sells keyboards and, apparently, themes.",
        }}))
        pack = next(p for p in self.build()["themes"] if p["id"] == "keychron-light")
        self.assertEqual(pack["link"], "https://example.com/keys")
        self.assertEqual(pack["description"], "A shop that sells keyboards and, apparently, themes.")
        # A bare URL is still a valid entry and carries no description.
        (self.root / "links.json").write_text(json.dumps({"keychron-light": "https://example.com/keys"}))
        pack = next(p for p in self.build()["themes"] if p["id"] == "keychron-light")
        self.assertNotIn("description", pack)

    def test_a_description_must_be_one_short_paragraph(self):
        for bad in ({"url": "https://example.com", "description": "x" * 241},
                    {"url": "https://example.com", "description": "two\nlines"},
                    {"url": "https://example.com", "description": "   "},
                    {"url": "https://example.com", "description": 7},
                    {"url": "https://example.com", "blurb": "unknown key"}):
            (self.root / "links.json").write_text(json.dumps({"keychron-light": bad}))
            with self.assertRaises(subprocess.CalledProcessError, msg=repr(bad)):
                self.build()

    def test_a_link_must_name_a_real_theme_and_be_https(self):
        for bad in ({"not-a-theme": "https://example.com"},
                    {"keychron-light": "http://example.com"},
                    {"keychron-light": "javascript:alert(1)"},
                    {"keychron-light": 42}):
            (self.root / "links.json").write_text(json.dumps(bad))
            with self.assertRaises(subprocess.CalledProcessError, msg=repr(bad)):
                self.build()

    def test_byte_only_changes_get_a_new_url_even_if_theme_is_equivalent(self):
        first = self.build()
        path = self.root / "Themes/keychron-light.clinktheme"
        path.write_bytes(path.read_bytes() + b"\n")
        updated = self.build()
        self.assertNotEqual(first["version"], updated["version"])
        self.assertEqual([p["preview"] for p in first["themes"]],
                         [p["preview"] for p in updated["themes"]])


if __name__ == "__main__":
    unittest.main()
