"""Read-only, post-restart Unreal editor validation; does NOT verify gameplay."""
import json
from pathlib import Path
from build_resonance import ROOT, ITEMS, MODEL_NAMES, expected_packages, get


def verify():
    import unreal as ue
    failures = []

    def check(condition, message):
        if not condition:
            failures.append(message)

    def load_class(relative):
        path = ROOT + '/' + relative
        value = ue.EditorAssetLibrary.load_blueprint_class(path)
        if value is None:
            raise RuntimeError('Class failed to load: ' + path)
        return value

    for package in expected_packages():
        check(ue.EditorAssetLibrary.does_asset_exist(package), 'Missing ' + package)
    if failures:
        raise RuntimeError('\n'.join(failures))
    for name in MODEL_NAMES:
        mesh = ue.EditorAssetLibrary.load_asset(ROOT + '/Models/Meshes/' + name)
        check(isinstance(mesh, ue.StaticMesh), 'Not a StaticMesh: ' + name)
        check(not mesh.get_editor_property('has_navigation_data'), 'Navigation enabled: ' + name)
    classes = {}
    for name, _, _ in ITEMS:
        item_class = load_class('Items/' + name + '_IT')
        actor_class = load_class('Items/' + name + '_BP')
        classes[name] = item_class
        item = ue.get_default_object(item_class)
        actor = ue.get_default_object(actor_class)
        check(get(item, 'PickupActor') == actor_class, 'PickupActor mismatch: ' + name)
        check(get(get(actor, 'ItemComponent'), 'ItemType') == item_class, 'ItemType mismatch: ' + name)
        mesh = get(actor, 'StaticMeshComponent').get_editor_property('static_mesh')
        check(mesh == ue.EditorAssetLibrary.load_asset(ROOT + '/Models/Meshes/SM_' + name), 'Mesh mismatch: ' + name)
        check(get(item, 'DLCEntitlementLock') == ue.ItemDLCEntitlementLock.NONE, 'DLC lock enabled: ' + name)
    recipe = get(ue.get_default_object(classes['TuningLens']), 'ConstructionRecipe')
    ingredients = get(recipe, 'Ingredients')
    check(len(ingredients) == 1, 'Lens must require exactly one ingredient')
    if len(ingredients) == 1:
        check(get(ingredients[0], 'ItemType') == classes['EchoGlass'], 'Lens ingredient is not Echo Glass')
        check(get(ingredients[0], 'Count') == 1.0, 'Lens count must be 1')
    missions = ue.EditorAssetLibrary.load_asset(ROOT + '/Missions/DA_ResonanceMissions')
    rows = get(missions, 'MissionsData')
    check(len(rows) == 6, 'Expected six mission rows')
    for row in rows:
        mission_id = str(get(row, 'missionId'))
        check(not get(row, 'bAutoActivate'), 'Unbound mission autoactivates: ' + mission_id)
        check(not get(row, 'RequiresGlitchWalkersEntitlement'), 'Glitchwalkers required: ' + mission_id)
        check(not get(row, 'RequiresMegatechEntitlement'), 'Megatech required: ' + mission_id)
        objectives = get(row, 'Objectives')
        check(len(objectives) == 1, 'Expected one objective: ' + mission_id)
        if len(objectives) == 1:
            check(get(objectives[0], 'ObjectiveType') == ue.AstroMissionObjectiveType.CUSTOM,
                  'Expected custom objective: ' + mission_id)
            check(get(objectives[0], 'Planet') == ue.PlanetIdentifier.TERRAN, 'Wrong planet: ' + mission_id)
    report = {'stage': 'editor_reference_validation', 'passed': not failures,
              'failures': failures, 'runtime_ready': False,
              'does_not_test': ['Blueprint compile status', 'cooking', 'gameplay', 'save/load', 'network authority']}
    path = Path(ue.Paths.project_saved_dir()) / 'AR_Resonance_ReferenceVerification.json'
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if failures:
        raise RuntimeError('\n'.join(failures))
    ue.log('Editor reference checks passed. Gameplay remains unverified. Report: ' + str(path))
    return report
