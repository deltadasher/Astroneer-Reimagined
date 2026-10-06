"""Offline source contract checks, NOT a mock substitute for Unreal execution."""
import importlib.util
import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'authoring'))
spec = importlib.util.spec_from_file_location('build_resonance', ROOT / 'authoring/build_resonance.py')
author = importlib.util.module_from_spec(spec)
spec.loader.exec_module(author)


class ReflectionObject:
    def __init__(self, properties):
        self.properties = dict(properties)

    def get_editor_property(self, name):
        return self.properties[name]

    def set_editor_property(self, name, value):
        if name not in self.properties:
            raise KeyError(name)
        self.properties[name] = value


class AuthoringContractTests(unittest.TestCase):
    def test_native_spelling_and_python_alias(self):
        for spelling in ('MissionCatagory', 'mission_catagory'):
            obj = ReflectionObject({spelling: 'old'})
            author.put(obj, 'MissionCatagory', 'AR_Resonance')
            self.assertEqual(author.get(obj, 'MissionCatagory'), 'AR_Resonance')

    def test_reflection_does_not_silently_skip_missing_property(self):
        with self.assertRaisesRegex(RuntimeError, 'Reflection mismatch'):
            author.put(ReflectionObject({}), 'PickupActor', None)

    def test_packages_stay_in_mod_namespace_and_unique(self):
        paths = author.expected_packages()
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all(p.startswith(author.ROOT + '/') for p in paths))
        self.assertEqual(len(paths), 12)

    def make_inputs(self, folder):
        (folder / 'content').mkdir()
        (folder / 'assets').mkdir()
        design = json.loads((ROOT / 'content/resonance.json').read_text())
        (folder / 'content/resonance.json').write_text(json.dumps(design))
        for name in author.MODEL_NAMES:
            (folder / 'assets' / (name + '.fbx')).write_bytes(b'test path fixture; not FBX')
        return design

    def test_input_paths_and_mission_topology(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.make_inputs(folder)
            design, files = author.read_inputs(folder)
            self.assertFalse(design['requires_dlc'])
            self.assertEqual(set(files), set(author.MODEL_NAMES))

    def test_missing_and_ambiguous_model_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.make_inputs(folder)
            path = folder / 'assets' / (author.MODEL_NAMES[0] + '.fbx')
            path.unlink()
            with self.assertRaises(ValueError):
                author.read_inputs(folder)
            path.write_bytes(b'test')
            (folder / 'assets/duplicate').mkdir()
            (folder / 'assets/duplicate' / path.name).write_bytes(b'test')
            with self.assertRaises(ValueError):
                author.read_inputs(folder)

    def test_material_manifest_values_and_names(self):
        import materials
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'assets').mkdir()
            entry = {'name': 'M_Test', 'base_color_linear': [0.1, 0.2, 0.3, 1],
                     'roughness': 0.55, 'metallic': 0.05}
            manifest = folder / 'assets/asset_manifest.json'
            manifest.write_text(json.dumps({'materials': [entry]}))
            self.assertEqual(materials.read_materials(folder), [entry])
            for bad in ('../Bad', 'M_../Bad', ''):
                entry['name'] = bad
                manifest.write_text(json.dumps({'materials': [entry]}))
                with self.assertRaises(ValueError):
                    materials.read_materials(folder)

    def test_material_manifest_rejects_nonfinite_and_duplicate(self):
        import materials
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / 'assets').mkdir()
            entry = {'name': 'M_Test', 'base_color_linear': [0.1, 0.2, 0.3, 1],
                     'roughness': float('nan'), 'metallic': 0.05}
            manifest = folder / 'assets/asset_manifest.json'
            manifest.write_text(json.dumps({'materials': [entry]}))
            with self.assertRaises(ValueError):
                materials.read_materials(folder)
            entry['roughness'] = 0.55
            manifest.write_text(json.dumps({'materials': [entry, entry]}))
            with self.assertRaises(ValueError):
                materials.read_materials(folder)

    def test_dlc_and_forward_dependency_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            design = self.make_inputs(folder)
            target = folder / 'content/resonance.json'
            design['requires_dlc'] = True
            target.write_text(json.dumps(design))
            with self.assertRaises(ValueError):
                author.read_inputs(folder)
            design['requires_dlc'] = False
            design['missions'][0]['requires'] = ['retune']
            target.write_text(json.dumps(design))
            with self.assertRaises(ValueError):
                author.read_inputs(folder)


if __name__ == '__main__':
    unittest.main()
