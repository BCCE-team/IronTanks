#!/usr/bin/env python3
"""Validate legacy, modern, and 26.X independent Stonecutter build roots."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from source_layout import ROOT, generation_config_paths, generation_targets, load_properties, target_ids, target_layout

ACTIVE_RE = re.compile(r'^\s*stonecutter\s+active\s+"([^"]+)"', re.MULTILINE)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def prop(props: dict[str, str], target: str, key: str) -> str:
    value = props.get(f"target.{target}.{key}", props.get(f"common.{key}", "")).strip()
    if not value:
        fail(f"{target}: missing property {key}")
    return value


def wrapper_version(root: Path) -> str:
    path = root / "gradle/wrapper/gradle-wrapper.properties"
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    match = re.search(r"gradle-([0-9.]+)-bin\.zip", path.read_text(encoding="utf-8"))
    if not match:
        fail(f"cannot determine Gradle version from {path.relative_to(ROOT)}")
    return match.group(1)


def validate_generation(name: str, targets: list[str], props: dict[str, str]) -> str:
    root = generation_config_paths()[name].parent
    required = [
        "settings.gradle.kts", "stonecutter.gradle.kts", "targets.properties", "gradle.properties",
        "gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar", "gradle/wrapper/gradle-wrapper.properties",
    ]
    for rel in required:
        if not (root / rel).is_file():
            fail(f"{name}: missing {root.relative_to(ROOT) / rel}")

    settings = (root / "settings.gradle.kts").read_text(encoding="utf-8")
    controller = (root / "stonecutter.gradle.kts").read_text(encoding="utf-8")
    if 'file("../..").canonicalFile' not in settings:
        fail(f"{name}: settings does not resolve the repository root")
    if 'id("dev.kikugie.stonecutter") version "0.7.11"' not in settings:
        fail(f"{name}: Stonecutter 0.7.11 is not pinned")
    if 'kotlinController = true' not in settings:
        fail(f"{name}: kotlinController is not enabled")
    if 'tasks.register("buildAndCollect")' not in controller:
        fail(f"{name}: controller has no buildAndCollect task")

    active_match = ACTIVE_RE.search(controller)
    if not active_match or active_match.group(1) not in targets:
        fail(f"{name}: invalid active Stonecutter target")

    for target in targets:
        layout = target_layout(target, props)
        if layout.generation != name:
            fail(f"{target}: generation mismatch {layout.generation!r} != {name!r}")
        loader = target.rsplit('-', 1)[1]
        if layout.platform != loader:
            fail(f"{target}: source platform {layout.platform!r} != loader {loader!r}")
        if layout.family != name:
            fail(f"{target}: source family {layout.family!r} != generation {name!r}")
        for layer in layout.layers:
            if not layer.is_dir():
                fail(f"{target}: missing source layer {layer.relative_to(ROOT)}")

        script = root / f"build.{loader}.gradle"
        if not script.is_file():
            fail(f"{target}: missing {script.relative_to(ROOT)}")
        text = script.read_text(encoding="utf-8")
        impl = (ROOT / f'build-logic/{loader}-target.gradle').read_text(encoding='utf-8') if loader in ('neoforge', 'fabric') else text
        for token in ("sourceLayoutScript", "prepareEffectiveSource", "effectiveSourceRoot", "buildAndCollect"):
            if token not in impl:
                fail(f"{script.relative_to(ROOT)}: missing build behavior {token}")
        if loader == 'neoforge' and "apply from: new File(rootProject.file('../..').canonicalFile, 'build-logic/neoforge-target.gradle')" not in text:
            fail(f"{script.relative_to(ROOT)}: must apply the shared NeoForge build logic")
        if loader == 'fabric' and "apply from: new File(rootProject.file('../..').canonicalFile, 'build-logic/fabric-target.gradle')" not in text:
            fail(f'{script.relative_to(ROOT)}: must apply Fabric build logic')
        if loader == 'fabric' and "id 'net.fabricmc.fabric-loom' version '1.18.4'" not in text:
            fail(f'{script.relative_to(ROOT)}: Fabric Loom 1.18.4 must be pinned')
        if loader == "forge" and "id 'net.minecraftforge.gradle' version '6.0.54'" not in text:
            fail(f"{script.relative_to(ROOT)}: ForgeGradle 6.0.54 is not pinned")
        if loader == 'neoforge':
            mdg = '2.0.148' if name == '26.X' else '2.0.143'
            if f"id 'net.neoforged.moddev' version '{mdg}'" not in text:
                fail(f'{script.relative_to(ROOT)}: ModDevGradle {mdg} is not pinned')

        for key in (
            "deps.minecraft", "java.version", "source.root", "source.platform_root", "source.overlay_root",
            "loader.version_range", "minecraft.version_range", "deps.buildcraft.modrinth_project",
            "buildcraft.version", "buildcraft.version_range", "pack.format", "pack.resource_format", "pack.data_format",
        ):
            prop(props, target, key)
        if loader == 'fabric':
            for key in ('deps.fabric_loader', 'deps.fabric_api', 'deps.energy'):
                prop(props, target, key)
        else:
            prop(props, target, 'deps.forge' if loader == 'forge' else 'deps.neoforge')
        if name == '26.X' and prop(props, target, 'java.version') != '25':
            fail(f'{target}: Minecraft 26.X must use Java 25')

    gradle = wrapper_version(root)
    expected_gradle = '9.8.1' if name == '26.X' else '8.8'
    if gradle != expected_gradle:
        fail(f'{name}: expected Gradle {expected_gradle}, got {gradle}')
    return gradle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-targets", action="store_true")
    parser.add_argument("--generation", choices=tuple(generation_config_paths()))
    parser.add_argument("--loader")
    args = parser.parse_args()

    props = load_properties()
    targets = target_ids(props)
    generations = generation_targets(props)

    if args.list_targets:
        for target in targets:
            layout = target_layout(target, props)
            if args.generation and layout.generation != args.generation:
                continue
            if args.loader and layout.platform != args.loader:
                continue
            print(target)
        return

    if props.get("behaviorReference") != "1.19.2-forge":
        fail("behaviorReference must be 1.19.2-forge")

    for obsolete in (
        "settings.gradle.kts", "stonecutter.gradle.kts", "build.forge.gradle", "build.neoforge.gradle",
        "gradle.properties", "gradlew", "gradlew.bat", "gradle", "versions", "version-resources", "src",
    ):
        if (ROOT / obsolete).exists():
            fail(f"obsolete monolithic build/source path remains: {obsolete}")

    for name in ("build-all.sh", "build-all.ps1", "build-all.bat"):
        if not (ROOT / name).is_file():
            fail(f"missing build orchestrator {name}")

    required_targets = {
        '1.19.2-forge', '1.20.1-forge', '1.21.1-neoforge', '1.21.11-neoforge',
        '26.1.2-neoforge', '26.2-neoforge', '26.3-neoforge', '26.3-fabric',
    }
    if set(targets) != required_targets:
        fail(f"production target matrix mismatch: {targets}")

    reports = []
    for generation, items in generations.items():
        reports.append(f"{generation}=Gradle {validate_generation(generation, items, props)} ({', '.join(items)})")
    print("Stonecutter build generations OK: " + "; ".join(reports))


if __name__ == "__main__":
    main()
