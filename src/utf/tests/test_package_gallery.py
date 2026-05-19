
import json
import tempfile
import unittest
from pathlib import Path

import thirsty_lang.package_manager as pm
from thirsty_lang.cli import run_source


class PackageAndGalleryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pm.REGISTRY_HOME = self.tmp / "registry"
        pm.PACKAGES_HOME = self.tmp / "packages"
        pm.GALLERY_INDEX = pm.REGISTRY_HOME / "great_wells.json"
        pm.ensure_hydration_dirs()

    def _make_package(self, name: str, source: str, version: str = "1.0.0"):
        pkg = self.tmp / name
        pkg.mkdir()
        (pkg / "src").mkdir()
        (pkg / "src" / "main.thirsty").write_text(source, encoding="utf-8")
        pm.manifest_path(pkg).write_text(json.dumps({
            "name": name,
            "version": version,
            "entry": "src/main.thirsty",
            "description": f"{name} from the Great Wells",
            "tags": ["great-well", "hydrated"],
        }), encoding="utf-8")
        return pkg

    def test_publish_install_and_import_package(self):
        pkg = self._make_package("coolpkg", "glass answer() -> Int { return 42; }\n")
        entry = pm.publish_package(pkg)
        self.assertEqual(entry["name"], "coolpkg")

        app = self.tmp / "app"
        app.mkdir()
        (app / "src").mkdir()
        result = pm.install_package(app, "coolpkg")
        self.assertEqual(result["name"], "coolpkg")

        src = """
import "coolpkg" as cool;
glass main() -> Int {
  pour(cool.answer());
  return 0;
}
"""
        out = run_source(src, str(app / "src" / "main.thirsty"))
        self.assertEqual(out, ["42"])

    def test_gallery_search_and_show(self):
        pkg = self._make_package("well_of_echoes", "glass ping() -> String { return \"pong\"; }\n")
        pm.publish_package(pkg)
        items = pm.search_gallery("echoes")
        self.assertTrue(any(item["name"] == "well_of_echoes" for item in items))
        shown = pm.show_gallery_item("well_of_echoes")
        self.assertIsNotNone(shown)
        self.assertEqual(shown["name"], "well_of_echoes")
