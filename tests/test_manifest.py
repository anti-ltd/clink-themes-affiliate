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
