"""Strict developer staging helper; does not cook, pack, install, or prove runtime safety."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil

ROOT = "/Game/Mods/deltadasher/AstroneerReimagined/Resonance/"
CONTENT = "Astro/Content/"
ALLOWED_EXTENSIONS = {".uasset", ".uexp", ".ubulk"}


def package_path(value):
    if not isinstance(value, str) or not value.startswith(ROOT):
        raise ValueError("Mod asset must be under " + ROOT)
    tail = value[len(ROOT):]
    if not tail or any(not re.fullmatch(r"[A-Za-z0-9_]+", p) for p in tail.split("/")):
        raise ValueError("Use a clean package path, not object/class/file path: " + value)
    return CONTENT + value[len("/Game/"):] + ".uasset"


def validate_manifest(manifest):
    """Our staging manifest is NOT an integrator schema or an engine validation report."""
    if manifest.get("format_version") != 1 or manifest.get("author_reviewed") is not True:
        raise ValueError("Require format_version 1 and explicit author_reviewed true")
    md = manifest.get("metadata", {})
    if type(md.get("schema_version")) is not int or md["schema_version"] != 2:
        raise ValueError("Metadata schema_version must be integer 2")
    for field in ("name", "mod_id", "version", "game_build"):
        if not isinstance(md.get(field), str) or not md[field].strip():
            raise ValueError("Missing metadata string: " + field)
    if not re.fullmatch(r"[A-Za-z0-9]+", md["mod_id"]):
        raise ValueError("Use alphanumeric mod_id")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?", md["version"]):
        raise ValueError("Use a semantic version")
    if md.get("sync", "serverclient") not in {"none", "server", "client", "serverclient"}:
        raise ValueError("Invalid sync mode")
    # Intentionally narrow supported schema; no claims of implementing all v2 fields.
    if set(md) - {"schema_version", "name", "mod_id", "version", "game_build", "author", "description", "sync", "integrator", "dependencies"}:
        raise ValueError("Unsupported metadata field")
    if not isinstance(md.get("dependencies", {}), dict):
        raise ValueError("dependencies must be object")
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in md.get("dependencies", {}).items()):
        raise ValueError("This helper supports string dependency requirements only")
    refs = []
    integrator = md.get("integrator", {})
    if not isinstance(integrator, dict) or set(integrator) - {"persistent_actors", "mission_trailheads", "item_list_entries", "linked_actor_components"}:
        raise ValueError("Unsupported integrator structure")
    for key in ("persistent_actors", "mission_trailheads"):
        values = integrator.get(key, [])
        if not isinstance(values, list):
            raise ValueError(key + " must be array")
        refs.extend(values)
    for key in ("linked_actor_components", "item_list_entries"):
        mapping = integrator.get(key, {})
        if not isinstance(mapping, dict):
            raise ValueError(key + " must be object")
        for target, value in mapping.items():
            if not isinstance(target, str) or not re.fullmatch(r"/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+", target):
                raise ValueError("Invalid target package")
            arrays = value.values() if key == "item_list_entries" and isinstance(value, dict) else [value]
            if key == "item_list_entries" and not isinstance(value, dict):
                raise ValueError("item_list_entries target must map field names to arrays")
            for arr in arrays:
                if not isinstance(arr, list):
                    raise ValueError("Integration entries must be arrays")
                refs.extend(arr)
    packages = manifest.get("packages")
    if not isinstance(packages, list) or not packages:
        raise ValueError("List every mod package and dependency in packages")
    files = [package_path(p) for p in packages]
    if len(set(files)) != len(files):
        raise ValueError("Duplicate package")
    for ref in refs:
        if package_path(ref) not in files:
            raise ValueError("Integrator references an unlisted package: " + ref)
    return md, files


def stage(manifest, cooked_root, output):
    md, files = validate_manifest(manifest)
    source = Path(cooked_root).absolute()
    output = Path(output).absolute()
    if source.name != "WindowsNoEditor" or source.parent.name != "Cooked" or source.parent.parent.name != "Saved":
        raise ValueError("Source must be the project's Saved/Cooked/WindowsNoEditor directory")
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Missing or symlinked cook directory")
    source = source.resolve()
    if output == source or source in output.parents or output in source.parents:
        raise ValueError("Output must be outside cooked source")
    copies = []
    for relative in files:
        asset = source / PurePosixPath(relative)
        for candidate in (asset, asset.with_suffix(".uexp"), asset.with_suffix(".ubulk")):
            if candidate == asset or candidate.exists():
                if not candidate.is_file() or candidate.is_symlink() or source not in candidate.resolve().parents:
                    raise ValueError("Missing or unsafe cooked file: " + str(candidate))
                if candidate.stat().st_size == 0:
                    raise ValueError("Empty cooked file: " + str(candidate))
                copies.append((candidate, candidate.relative_to(source)))
    # Atomic reservation: simultaneous and repeated invocations never overwrite a staging tree.
    output.mkdir(parents=False, exist_ok=False)
    try:
        hashes = {}
        for src, relative in copies:
            dst = output / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            hashes[relative.as_posix()] = hashlib.sha256(dst.read_bytes()).hexdigest()
        (output / "metadata.json").write_text(json.dumps(md, indent=2) + "\n", encoding="utf-8")
        # Audit lives beside the tree so it is not accidentally packed into the mod.
        report = {"status": "staged_only_not_runtime_validated", "files": hashes,
                  "suggested_pak_name": "000-" + md["mod_id"] + "-" + md["version"] + "_P.pak"}
        return report
    except BaseException:
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("cooked_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = stage(json.loads(args.manifest.read_text(encoding="utf-8")), args.cooked_root, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
