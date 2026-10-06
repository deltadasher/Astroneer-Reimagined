"""Original opaque materials from the artist manifest, via UE4.27 editor API."""
import json
import math
import re


def read_materials(repo):
    paths = sorted((repo / 'assets').rglob('asset_manifest.json'))
    if len(paths) != 1:
        raise ValueError('Expected one original asset_manifest.json under assets/')
    entries = json.loads(paths[0].read_text(encoding='utf-8'))['materials']
    names = set()
    for entry in entries:
        name = entry['name']
        if not re.fullmatch(r'M_[A-Za-z0-9_]+', name) or name in names:
            raise ValueError('Unsafe or duplicate material name: ' + name)
        names.add(name)
        color = entry['base_color_linear']
        if len(color) != 4 or color[3] != 1:
            raise ValueError('Only opaque RGBA materials are supported')
        for value in color + [entry['roughness'], entry['metallic']]:
            if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError('Material values must be finite numbers from 0 to 1')
    if not entries:
        raise ValueError('No materials in manifest')
    return entries


def create_materials(ue, tools, root, entries):
    result = {}
    library = ue.MaterialEditingLibrary
    for entry in entries:
        name = entry['name']
        material = tools.create_asset(name, root + '/Models/Materials', ue.Material, ue.MaterialFactoryNew())
        if material is None:
            raise RuntimeError('MaterialFactoryNew failed: ' + name)
        color = library.create_material_expression(material, ue.MaterialExpressionConstant3Vector, -400, 0)
        color.set_editor_property('constant', ue.LinearColor(*entry['base_color_linear']))
        if not library.connect_material_property(color, '', ue.MaterialProperty.MP_BASE_COLOR):
            raise RuntimeError('Could not connect base color: ' + name)
        for index, (key, target) in enumerate((('roughness', ue.MaterialProperty.MP_ROUGHNESS),
                                               ('metallic', ue.MaterialProperty.MP_METALLIC))):
            node = library.create_material_expression(material, ue.MaterialExpressionConstant, -400, 180 + index * 120)
            node.set_editor_property('r', entry[key])
            if not library.connect_material_property(node, '', target):
                raise RuntimeError('Could not connect ' + key + ': ' + name)
        library.recompile_material(material)
        result[name] = material
    return result


def assign_materials(mesh, materials):
    slots = mesh.get_editor_property('static_materials')
    if not slots:
        raise RuntimeError('Imported mesh has no material slots: ' + mesh.get_name())
    for index, slot in enumerate(slots):
        name = str(slot.get_editor_property('imported_material_slot_name'))
        if name not in materials:
            name = str(slot.get_editor_property('material_slot_name'))
        if name not in materials:
            raise RuntimeError('Unmapped material slot on ' + mesh.get_name() + ': ' + name)
        mesh.set_material(index, materials[name])
