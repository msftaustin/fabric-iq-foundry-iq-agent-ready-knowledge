import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

import demos  # noqa: E402


class DemoToolTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(REPOSITORY / "templates", self.root / "templates")
        (self.root / "demos").mkdir()
        shutil.copy(REPOSITORY / "demos" / "README.md", self.root / "demos" / "README.md")
        demos.synchronize_catalog(self.root, check=False)

    def tearDown(self):
        self.temporary.cleanup()

    def test_template_produces_valid_demo(self):
        created = demos.create_demo(self.root, "sample-demo", "Sample Demo")
        self.assertEqual([], demos.validate_demo(created))
        manifest = demos.read_manifest(created)
        self.assertEqual("sample-demo", manifest["id"])
        self.assertIn("Sample Demo", (created / "README.md").read_text(encoding="utf-8"))
        self.assertTrue(demos.synchronize_catalog(self.root, check=True))

    def test_invalid_id_title_and_duplicate_are_rejected(self):
        with self.assertRaises(ValueError):
            demos.create_demo(self.root, "Not_Valid", "Demo")
        with self.assertRaises(ValueError):
            demos.create_demo(self.root, "valid", 'Unsafe "title"')
        demos.create_demo(self.root, "duplicate", "First")
        with self.assertRaises(ValueError):
            demos.create_demo(self.root, "duplicate", "Second")

    def test_invalid_manifest_and_missing_structure_are_reported(self):
        created = demos.create_demo(self.root, "broken-demo", "Broken Demo")
        (created / "docs" / "EXTENDING.md").unlink()
        manifest_file = created / "demo.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest["id"] = "wrong-id"
        manifest["owners"] = []
        manifest["deploy"]["guide"] = "../../README.md"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        errors = "\n".join(demos.validate_demo(created))
        self.assertIn("required file is missing", errors)
        self.assertIn("must match the demo folder", errors)
        self.assertIn("must contain at least one string", errors)
        self.assertIn("must reference a file inside the demo", errors)

    def test_template_tokens_are_reported(self):
        created = demos.create_demo(self.root, "token-demo", "Token Demo")
        (created / "src" / "README.md").write_text("{{UNFINISHED_TOKEN}}", encoding="utf-8")
        self.assertIn(
            "template token remains in src/README.md",
            demos.validate_demo(created),
        )

    def test_catalog_detects_manifest_changes(self):
        created = demos.create_demo(self.root, "catalog-demo", "Catalog Demo")
        manifest_file = created / "demo.json"
        manifest = demos.read_manifest(created)
        manifest["summary"] = "Changed | summary"
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

        self.assertFalse(demos.synchronize_catalog(self.root, check=True))
        demos.synchronize_catalog(self.root, check=False)
        catalog = (self.root / "demos" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Changed \\| summary", catalog)

    def test_repository_demo_contract(self):
        for directory in demos.demo_directories(REPOSITORY):
            with self.subTest(demo=directory.name):
                self.assertEqual([], demos.validate_demo(directory))
        self.assertTrue(demos.synchronize_catalog(REPOSITORY, check=True))


if __name__ == "__main__":
    unittest.main()
