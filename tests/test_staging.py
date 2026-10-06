import copy
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from tools.stage_mod import ROOT, package_path, stage, validate_manifest


def manifest():
    return {"format_version": 1, "author_reviewed": True,
            "metadata": {"schema_version": 2, "name": "Resonance", "mod_id": "AstroneerReimagined", "version": "0.1.0-dev", "game_build": "1.36.42.0", "integrator": {}},
            "packages": [ROOT + "Items/EchoGlass_IT"]}


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.cook = self.base / "Saved/Cooked/WindowsNoEditor"
        self.asset = self.cook / package_path(manifest()["packages"][0])
        self.asset.parent.mkdir(parents=True)
        self.asset.write_bytes(b"synthetic test fixture, not a UE asset")
        self.asset.with_suffix(".uexp").write_bytes(b"synthetic sidecar")
        self.out = self.base / "stage"

    def test_stages_exact_files_and_utf8_metadata(self):
        report = stage(manifest(), self.cook, self.out)
        self.assertEqual(len(report["files"]), 2)
        self.assertEqual(json.loads((self.out / "metadata.json").read_text()), manifest()["metadata"])
        self.assertFalse((self.out / "metadata.json").read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_repeated_stage_preserves_existing(self):
        stage(manifest(), self.cook, self.out)
        sentinel = self.out / "keep.txt"
        sentinel.write_text("hand edited")
        with self.assertRaises(FileExistsError):
            stage(manifest(), self.cook, self.out)
        self.assertEqual(sentinel.read_text(), "hand edited")

    def test_concurrent_stage_has_one_winner(self):
        def attempt(_):
            try:
                stage(manifest(), self.cook, self.out)
                return True
            except FileExistsError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(attempt, range(2))), [False, True])
        self.assertTrue((self.out / "metadata.json").is_file())

    def test_unlisted_integrator_asset_fails(self):
        data = manifest()
        data["metadata"]["integrator"]["mission_trailheads"] = [ROOT + "Missions/Unimplemented"]
        with self.assertRaises(ValueError):
            validate_manifest(data)

    def test_traversal_and_object_paths_fail(self):
        for value in (ROOT + "../oops", ROOT + "Items/Thing.Thing_C", ROOT + "Items//Thing", "/Game/Other/Thing"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                package_path(value)

    def test_missing_cook_does_not_create_output(self):
        self.asset.unlink()
        with self.assertRaises(ValueError):
            stage(manifest(), self.cook, self.out)
        self.assertFalse(self.out.exists())

    def test_uncooked_directory_rejected(self):
        with self.assertRaises(ValueError):
            stage(manifest(), self.base, self.out)

    def test_symlink_escape_rejected(self):
        self.asset.unlink()
        target = self.base / "elsewhere"
        target.write_bytes(b"unrelated file")
        self.asset.symlink_to(target)
        with self.assertRaises(ValueError):
            stage(manifest(), self.cook, self.out)

    def test_author_review_required(self):
        data = manifest()
        data["author_reviewed"] = False
        with self.assertRaises(ValueError):
            validate_manifest(data)
