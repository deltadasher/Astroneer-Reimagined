"""UE 4.27.2 editor-only asset authoring. Not a runtime mod or Python gameplay.

Run from the Unreal Python console:
  import sys; sys.path.insert(0, r'C:/src/Astroneer-Reimagined/authoring')
  import build_resonance; build_resonance.build(r'C:/src/Astroneer-Reimagined')

Requires the pinned ModdingKit, Python Editor Script Plugin and Editor Scripting
Utilities. Creates NEW assets only; refuses to overwrite any existing mod asset.
The Unreal steps have not been executed on this cloud machine.
"""
import json
from pathlib import Path
from materials import read_materials, create_materials, assign_materials

ROOT = '/Game/Mods/deltadasher/AstroneerReimagined/Resonance'
KIT_COMMIT = 'e7f4d47eb368f72887dc32100600ba8ab3072184'
MODEL_NAMES = ('SM_TuningLens', 'SM_EchoGlass', 'SM_ResonanceSite_Base',
               'SM_ResonanceSite_Dormant', 'SM_ResonanceSite_Active')
ITEMS = (('EchoGlass', 'Echo Glass', 'A resonant glass material. Production is not yet bound.'),
         ('TuningLens', 'Tuning Lens', 'A reusable resonance instrument. Interaction is not yet bound.'))
# Native reflected names and their expected Python aliases, NOT invented SDK APIs.
# Native spellings include genuine SDK typos. Probe both and fail closed on mismatch.
PROPS = {
    'missionId': 'mission_id', 'MissionCatagory': 'mission_catagory',
    'Decription': 'decription', 'PrerequisitMissions': 'prerequisit_missions',
    'MissionsData': 'missions_data', 'DLCEntitlementLock': 'dlc_entitlement_lock',
    'bAutoActivate': 'auto_activate', 'bAutoCompleteOnExistingGames': 'auto_complete_on_existing_games',
    'bReclaimableReward': 'reclaimable_reward', 'RequiresGlitchWalkersEntitlement': 'requires_glitch_walkers_entitlement',
    'RequiresMegatechEntitlement': 'requires_megatech_entitlement',
    'PickupActor': 'pickup_actor', 'ItemComponent': 'item_component',
    'StaticMeshComponent': 'static_mesh_component', 'ItemType': 'item_type',
    'AllCapsName': 'all_caps_name', 'TooltipSubtitle': 'tooltip_subtitle',
    'ConstructionRecipe': 'construction_recipe', 'StartingAmount': 'starting_amount',
    'ObjectiveType': 'objective_type', 'CustomTag': 'custom_tag',
    'NextMissions': 'next_missions', 'ByteRewardValue': 'byte_reward_value',
    'ProgressNotifyThreshold': 'progress_notify_threshold', 'ProgressType': 'progress_type',
    'StartingValue': 'starting_value', 'bIsOptional': 'is_optional',
    'bIsHiddenObjective': 'is_hidden_objective', 'bIsPlanetExclude': 'is_planet_exclude',
}


def prop_name(obj, native):
    errors = []
    for candidate in dict.fromkeys((native, PROPS.get(native, native.lower()))):
        try:
            obj.get_editor_property(candidate)
            return candidate
        except Exception as error:
            errors.append(str(error))
    raise RuntimeError('Reflection mismatch {}.{}: {}'.format(type(obj).__name__, native, errors))


def get(obj, native):
    return obj.get_editor_property(prop_name(obj, native))


def put(obj, native, value):
    obj.set_editor_property(prop_name(obj, native), value)


def blueprint(ue, tools, relative, parent):
    path = ROOT + '/' + relative
    factory = ue.BlueprintFactory()
    factory.set_editor_property('parent_class', parent)
    asset = tools.create_asset(path.rsplit('/', 1)[1], path.rsplit('/', 1)[0], None, factory)
    if asset is None:
        raise RuntimeError('BlueprintFactory failed: ' + path)
    cls = ue.EditorAssetLibrary.load_blueprint_class(path)
    if cls is None:
        raise RuntimeError('Generated class unavailable; compile in editor: ' + path)
    return asset, cls, ue.get_default_object(cls)


def expected_packages():
    return ([ROOT + '/Models/Meshes/' + n for n in MODEL_NAMES]
            + [ROOT + '/Items/' + name + suffix for name, _, _ in ITEMS for suffix in ('_BP', '_IT')]
            + [ROOT + '/Resources/ResonantVapour_IT', ROOT + '/Site/ResonanceSite_BP',
               ROOT + '/Missions/DA_ResonanceMissions'])


def read_inputs(repo):
    design = json.loads((repo / 'content/resonance.json').read_text(encoding='utf-8'))
    if design.get('requires_dlc') is not False:
        raise ValueError('This slice must remain DLC-free')
    missions = design['missions']
    ids = [m['id'] for m in missions]
    if len(ids) != 6 or len(set(ids)) != 6:
        raise ValueError('Expected six distinct missions')
    seen = set()
    for mission in missions:
        if not set(mission['requires']).issubset(seen):
            raise ValueError('Mission prerequisites must precede their dependents')
        seen.add(mission['id'])
    files = {}
    for name in MODEL_NAMES:
        matches = sorted((repo / 'assets').rglob(name + '.fbx'))
        if len(matches) != 1:
            raise ValueError('Expected exactly one original FBX under assets/: ' + name)
        files[name] = matches[0]
    return design, files


def import_meshes(ue, tools, files, materials):
    meshes = {}
    for name, source in files.items():
        options = ue.FbxImportUI()
        options.set_editor_property('import_mesh', True)
        options.set_editor_property('import_as_skeletal', False)
        options.set_editor_property('import_materials', False)
        options.set_editor_property('import_textures', False)
        options.set_editor_property('automated_import_should_detect_type', False)
        options.set_editor_property('mesh_type_to_import', ue.FBXImportType.FBXIT_STATIC_MESH)
        data = options.get_editor_property('static_mesh_import_data')
        data.set_editor_property('convert_scene', True)
        data.set_editor_property('convert_scene_unit', True)
        data.set_editor_property('import_uniform_scale', 1.0)
        data.set_editor_property('combine_meshes', True)
        data.set_editor_property('auto_generate_collision', False)
        data.set_editor_property('one_convex_hull_per_ucx', True)
        data.set_editor_property('normal_import_method', ue.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        data.set_editor_property('generate_lightmap_u_vs', True)
        task = ue.AssetImportTask()
        for key, value in {'filename': str(source), 'destination_path': ROOT + '/Models/Meshes',
                           'destination_name': name, 'automated': True,
                           'replace_existing': False, 'save': False, 'options': options}.items():
            task.set_editor_property(key, value)
        tools.import_asset_tasks([task])
        mesh = ue.EditorAssetLibrary.load_asset(ROOT + '/Models/Meshes/' + name)
        if mesh is None or not isinstance(mesh, ue.StaticMesh):
            raise RuntimeError('FBX static mesh import failed: ' + name)
        mesh.set_editor_property('has_navigation_data', False)
        if mesh.get_editor_property('has_navigation_data'):
            raise RuntimeError('Unsafe navigation data remains enabled: ' + name)
        assign_materials(mesh, materials)
        meshes[name] = mesh
    return meshes


def author_missions(ue, tools, design):
    factory = ue.DataAssetFactory()
    factory.set_editor_property('data_asset_class', ue.AstroMissionDataAsset)
    asset = tools.create_asset('DA_ResonanceMissions', ROOT + '/Missions', ue.AstroMissionDataAsset, factory)
    if asset is None:
        raise RuntimeError('Could not create mission data asset')
    rows = []
    for mission in design['missions']:
        row = ue.AstroMissionData()
        objective = ue.AstroMissionObjective()
        tag = 'AR.Resonance.' + mission['id']
        for key, value in {'Description': ue.Text(mission['title']), 'CustomTag': tag,
                           'Value': 1.0, 'StartingValue': 0.0, 'ProgressNotifyThreshold': 1.0,
                           'ObjectiveType': ue.AstroMissionObjectiveType.CUSTOM,
                           'ProgressType': ue.AstroMissionObjectiveProgressType.HIGH_WATER,
                           'Planet': ue.PlanetIdentifier.TERRAN, 'bIsOptional': False,
                           'bIsHiddenObjective': False, 'bIsPlanetExclude': False}.items():
            put(objective, key, value)
        for key, value in {'missionId': 'AR_Resonance_' + mission['id'],
                           'MissionCatagory': 'AR_Resonance', 'Title': ue.Text(mission['title']),
                           'Decription': ue.Text('Resonance field research: ' + mission['title']),
                           'Objectives': [objective],
                           'PrerequisitMissions': ['AR_Resonance_' + x for x in mission['requires']],
                           'NextMissions': ['AR_Resonance_' + x['id'] for x in design['missions'] if mission['id'] in x['requires']],
                           'bAutoActivate': False, 'bAutoCompleteOnExistingGames': False,
                           'bReclaimableReward': False, 'ByteRewardValue': 0,
                           'RequiresGlitchWalkersEntitlement': False, 'RequiresMegatechEntitlement': False}.items():
            put(row, key, value)
        rows.append(row)
    put(asset, 'MissionsData', rows)
    return asset


def build(repo_directory):
    import unreal as ue
    repo = Path(repo_directory).resolve()
    design, files = read_inputs(repo)
    material_entries = read_materials(repo)
    version = ue.SystemLibrary.get_engine_version()
    if not version.startswith('4.27.2'):
        raise RuntimeError('Expected UE 4.27.2, got ' + version)
    # Refuse any existing content, including imported materials, before mutation.
    if ue.EditorAssetLibrary.does_directory_exist(ROOT) and ue.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False):
        raise RuntimeError('Target contains assets; use source control or a fresh kit copy. No overwrite: ' + ROOT)
    for required in ('ItemType', 'PhysicalItem', 'AstroMissionDataAsset', 'AstroMissionData',
                     'AstroMissionObjective', 'ItemRecipeIngredient', 'Recipe',
                     'ItemDLCEntitlementLock', 'AstroMissionObjectiveType',
                     'AstroMissionObjectiveProgressType', 'PlanetIdentifier', 'BlueprintFactory',
                     'DataAssetFactory', 'EditorAssetLibrary', 'AssetToolsHelpers', 'AssetImportTask',
                     'FbxImportUI', 'StaticMesh', 'StaticMeshActor', 'MaterialEditingLibrary',
                     'MaterialFactoryNew', 'Material', 'MaterialExpressionConstant3Vector',
                     'MaterialExpressionConstant', 'MaterialProperty'):
        if not hasattr(ue, required):
            raise RuntimeError('Missing reflected ModdingKit type: unreal.' + required)
    for enum_name, member in (('ItemDLCEntitlementLock', 'NONE'),
                              ('AstroMissionObjectiveType', 'CUSTOM'),
                              ('AstroMissionObjectiveProgressType', 'HIGH_WATER'),
                              ('PlanetIdentifier', 'TERRAN'), ('FBXImportType', 'FBXIT_STATIC_MESH'),
                              ('FBXNormalImportMethod', 'FBXNIM_IMPORT_NORMALS'),
                              ('MaterialProperty', 'MP_BASE_COLOR'), ('MaterialProperty', 'MP_ROUGHNESS'),
                              ('MaterialProperty', 'MP_METALLIC')):
        if not hasattr(getattr(ue, enum_name, None), member):
            raise RuntimeError('Missing reflected enum: unreal.' + enum_name + '.' + member)
    # Probe important reflected native fields before creating anything.
    put_probe = ue.AstroMissionData()
    for native in ('missionId', 'MissionCatagory', 'Decription', 'PrerequisitMissions', 'RequiresMegatechEntitlement'):
        prop_name(put_probe, native)
    tools = ue.AssetToolsHelpers.get_asset_tools()
    materials = create_materials(ue, tools, ROOT, material_entries)
    meshes = import_meshes(ue, tools, files, materials)
    item_classes = {}
    for name, label, description in ITEMS:
        physical, physical_class, physical_cdo = blueprint(ue, tools, 'Items/' + name + '_BP', ue.PhysicalItem)
        item, item_class, item_cdo = blueprint(ue, tools, 'Items/' + name + '_IT', ue.ItemType)
        for key, value in {'Name': ue.Text(label), 'AllCapsName': ue.Text(label.upper()),
                           'TooltipSubtitle': ue.Text('Resonance'), 'Description': ue.Text(description),
                           'PickupActor': physical_class,
                           'DLCEntitlementLock': ue.ItemDLCEntitlementLock.NONE}.items():
            put(item_cdo, key, value)
        component = get(physical_cdo, 'ItemComponent')
        static_mesh = get(physical_cdo, 'StaticMeshComponent')
        if component is None or static_mesh is None:
            raise RuntimeError('Native PhysicalItem default components missing for ' + name)
        put(component, 'ItemType', item_class)
        put(component, 'StartingAmount', 1.0)
        put(component, 'Capacity', 1.0)
        put(component, 'Discrete', True)
        static_mesh.set_editor_property('static_mesh', meshes['SM_' + name])
        item_classes[name] = (item_class, item_cdo)
    # Genuine construction recipe. The lens costs 1 Echo Glass. No free backpack
    # registration is emitted; Echo Glass production and catalog setup are unresolved.
    ingredient = ue.ItemRecipeIngredient()
    put(ingredient, 'ItemType', item_classes['EchoGlass'][0])
    put(ingredient, 'Count', 1.0)
    recipe = ue.Recipe()
    put(recipe, 'Ingredients', [ingredient])
    put(item_classes['TuningLens'][1], 'ConstructionRecipe', recipe)
    # Descriptor only: gas inheritance/container behavior intentionally NOT fabricated.
    _, _, gas_cdo = blueprint(ue, tools, 'Resources/ResonantVapour_IT', ue.ItemType)
    put(gas_cdo, 'Name', ue.Text('Resonant Vapour'))
    put(gas_cdo, 'Description', ue.Text('Unbound custom gas descriptor; not registered or produced.'))
    put(gas_cdo, 'DLCEntitlementLock', ue.ItemDLCEntitlementLock.NONE)
    _, _, site_cdo = blueprint(ue, tools, 'Site/ResonanceSite_BP', ue.StaticMeshActor)
    get(site_cdo, 'StaticMeshComponent').set_editor_property('static_mesh', meshes['SM_ResonanceSite_Base'])
    author_missions(ue, tools, design)
    # Save only generated assets, never game/kit source assets. No gameplay calls.
    actual_assets = ue.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False)
    for path in actual_assets:
        if not ue.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False):
            raise RuntimeError('Save failed: ' + path)
    report = {'schema_version': 1, 'stage': 'authored_uncompiled_unverified',
              'engine': version, 'sdk_commit_expected': KIT_COMMIT,
              'assets': sorted(path.split('.', 1)[0] for path in actual_assets),
              'expected_assets': expected_packages(), 'runtime_ready': False,
              'blockers': ['Blueprint compile/reopen verification', 'catalog/icons/slots/collision verification',
                           'custom gas container and production', 'Echo Glass recipe station',
                           'site interaction, world placement and durable state',
                           'mission event producers and already-awakened Sylva handling',
                           'Windows cook and actual-game multiplayer/save tests']}
    report_path = Path(ue.Paths.project_saved_dir()) / 'AR_Resonance_AuthoringReport.json'
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    ue.log_warning('Resonance assets authored, NOT runtime ready. Compile/reopen and verify. Report: ' + str(report_path))
    return report
