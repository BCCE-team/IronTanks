#!/usr/bin/env python3
"""Repository-level verification for Iron Tanks Community Edition."""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

from source_layout import ROOT, load_properties, materialize_target, target_ids, target_layout

ERRORS: list[str] = []

BLOCK_SPECS = {
    'COPPER_TANK': ('StackableTankBlock', 27, '4.0F', '2.0F'),
    'IRON_TANK': ('StackableTankBlock', 32, '5.0F', '3.0F'),
    'SILVER_TANK': ('StackableTankBlock', 43, '6.0F', '5.0F'),
    'GOLD_TANK': ('StackableTankBlock', 48, '7.0F', '4.0F'),
    'DIAMOND_TANK': ('StackableTankBlock', 64, '8.0F', '6.0F'),
    'OBSIDIAN_TANK': ('StackableTankBlock', 64, '50.0F', '1_200.0F'),
    'EMERALD_TANK': ('StackableTankBlock', 96, '8.0F', '6.0F'),
    'ALUMINIUM_TANK': ('StackableTankBlock', 96, '5.0F', '4.0F'),
    'STAINLESSSTEEL_TANK': ('StackableTankBlock', 128, '9.0F', '8.0F'),
    'TITANIUM_TANK': ('StackableTankBlock', 256, '10.0F', '10.0F'),
    'TUNGSTENSTEEL_TANK': ('StackableTankBlock', 512, '12.0F', '14.0F'),
    'VOID_TANK': ('VoidTankBlock', 8, '5.0F', '6.0F'),
    'CREATIVE_TANK': ('CreativeTankBlock', 1, None, None),
}

UPGRADE_SPECS = {
    'COPPER_IRON_UPGRADE': ('COPPER_TANK', 'IRON_TANK'),
    'COPPER_SILVER_UPGRADE': ('COPPER_TANK', 'SILVER_TANK'),
    'DIAMOND_OBSIDIAN_UPGRADE': ('DIAMOND_TANK', 'OBSIDIAN_TANK'),
    'GLASS_COPPER_UPGRADE': ('BCFactoryBlocks.TANK_BLOCK', 'COPPER_TANK'),
    'GLASS_IRON_UPGRADE': ('BCFactoryBlocks.TANK_BLOCK', 'IRON_TANK'),
    'GOLD_DIAMOND_UPGRADE': ('GOLD_TANK', 'DIAMOND_TANK'),
    'IRON_GOLD_UPGRADE': ('IRON_TANK', 'GOLD_TANK'),
    'SILVER_GOLD_UPGRADE': ('SILVER_TANK', 'GOLD_TANK'),
    'DIAMOND_EMERALD_UPGRADE': ('DIAMOND_TANK', 'EMERALD_TANK'),
    'DIAMOND_ALUMINIUM_UPGRADE': ('DIAMOND_TANK', 'ALUMINIUM_TANK'),
    'EMERALD_STAINLESSSTEEL_UPGRADE': ('EMERALD_TANK', 'STAINLESSSTEEL_TANK'),
    'ALUMINIUM_STAINLESSSTEEL_UPGRADE': ('ALUMINIUM_TANK', 'STAINLESSSTEEL_TANK'),
    'STAINLESSSTEEL_TITANIUM_UPGRADE': ('STAINLESSSTEEL_TANK', 'TITANIUM_TANK'),
    'TITANIUM_TUNGSTENSTEEL_UPGRADE': ('TITANIUM_TANK', 'TUNGSTENSTEEL_TANK'),
}


def fail(message: str) -> None:
    ERRORS.append(message)


def prop(props: dict[str, str], target: str, key: str) -> str:
    return props.get(f'target.{target}.{key}', props.get(f'common.{key}', '')).strip()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'Invalid JSON {path.relative_to(ROOT)}: {exc}')
        return {}


def collect_recipe_tags(value) -> set[str]:
    tags: set[str] = set()
    if isinstance(value, dict):
        tag = value.get('tag')
        if isinstance(tag, str):
            tags.add(tag)
        for child in value.values():
            tags.update(collect_recipe_tags(child))
    elif isinstance(value, list):
        for child in value:
            tags.update(collect_recipe_tags(child))
    elif isinstance(value, str) and value.startswith('#'):
        tags.add(value[1:])
    return tags


def validate_recipe_tags(target: str, resources: Path) -> None:
    modern = target.endswith('neoforge')
    recipe_dir = resources / ('data/irontanks/recipe' if modern else 'data/irontanks/recipes')
    recipes = sorted(recipe_dir.glob('*.json'))
    if len(recipes) != 30:
        fail(f'{target}: expected 30 active crafting recipes, found {len(recipes)}')
        return

    tags: set[str] = set()
    for recipe in recipes:
        tags.update(collect_recipe_tags(read_json(recipe)))

    if modern:
        leaked_forge = sorted(tag for tag in tags if tag.startswith('forge:'))
        if leaked_forge:
            fail(f'{target}: legacy Forge recipe tags leaked into NeoForge recipes: {leaked_forge}')
        obsolete_glass = sorted(tag for tag in tags if tag in {'c:glass', 'c:glass/colorless'})
        if obsolete_glass:
            fail(f'{target}: obsolete NeoForge glass tags remain: {obsolete_glass}')
        for required in (
            'c:glass_blocks', 'c:glass_blocks/colorless',
            'c:glass_panes', 'c:glass_panes/colorless',
        ):
            if required not in tags:
                fail(f'{target}: expected common recipe tag is missing: {required}')
    else:
        leaked_common = sorted(tag for tag in tags if tag.startswith('c:'))
        if leaked_common:
            fail(f'{target}: NeoForge common tags leaked into Forge recipes: {leaked_common}')
        for required in (
            'forge:glass', 'forge:glass/colorless',
            'forge:glass_panes', 'forge:glass_panes/colorless',
        ):
            if required not in tags:
                fail(f'{target}: expected Forge recipe tag is missing: {required}')


def validate_common_resources() -> None:
    resources = ROOT / 'source-shared/src/main/resources/assets/irontanks'
    lang = resources / 'lang/en_us.json'
    guide = resources / 'guide/text/en_us.json'
    if not lang.is_file() or not guide.is_file():
        fail('Missing authoritative en_us localization/guide pack')
        return
    lang_data = read_json(lang)
    guide_data = read_json(guide)
    if len(lang_data) != 87:
        fail(f'en_us translation key count changed: expected 87, got {len(lang_data)}')
    if guide_data.get('format') != 1:
        fail('Guide text pack format must be 1')
    if len(guide_data.get('pages', {})) != 27:
        fail(f'Guide page count changed: expected 27, got {len(guide_data.get("pages", {}))}')

    for base in (ROOT / 'source-shared', ROOT / 'source-families', ROOT / 'source-platforms', ROOT / 'version-src'):
        for path in base.rglob('src/main/resources/assets/irontanks/lang/*.json'):
            if path.name != 'en_us.json':
                fail(f'Non-English locale leaked into main ITCE source: {path.relative_to(ROOT)}')
        for path in base.rglob('src/main/resources/assets/irontanks/guide/text/*.json'):
            if path.name != 'en_us.json':
                fail(f'Non-English guide pack leaked into main ITCE source: {path.relative_to(ROOT)}')


def validate_target(target: str, props: dict[str, str]) -> None:
    output = ROOT / 'build' / 'verify-effective' / target
    materialize_target(target, output, props)
    java_root = output / 'src/main/java'
    resources = output / 'src/main/resources'
    java_paths = sorted(java_root.rglob('*.java'))
    java_text = '\n'.join(path.read_text(encoding='utf-8') for path in java_paths)

    if len(java_paths) != 14:
        fail(f'{target}: expected 14 Java sources, found {len(java_paths)}')
    if 'ct.buildcraft.' in java_text:
        fail(f'{target}: obsolete ct.buildcraft namespace remains')
    if re.search(r'buildcraft\.api\.(?!v2(?:\.|$))', java_text):
        fail(f'{target}: legacy BuildCraft API reference remains')
    if 'buildcraft.lib.internal.' in java_text:
        fail(f'{target}: addon reaches into BuildCraft internal implementation packages')
    for forbidden in ('java.lang.reflect', 'IronTanksTankMenu', 'IronTanksTankScreen', 'IronTanksRuntimeCompat'):
        if forbidden in java_text:
            fail(f'{target}: obsolete compatibility/UI code remains: {forbidden}')

    for required in (
        'new RenderTank(context)', 'newTank.balanceTankFluids()', 'FluidAction.SIMULATE',
        'TRANSFER_PER_TICK = 80', 'BUILDCRAFT_TAB.addItemProvider', 'IronTanksGuide.register()',
        'BuildCraftContent.addon(IronTanks.MODID)', 'GuidePages.item',
    ):
        if required not in java_text:
            fail(f'{target}: missing required port behavior {required!r}')
    if target in ('1.21.11-neoforge', '26.1.2-neoforge', '26.2-neoforge', '26.3-neoforge'):
        if 'Capabilities.Fluid.BLOCK' not in java_text or 'TransferInterop.exportFluids' not in java_text:
            fail(f'{target}: NeoForge resource fluid capability bridge is missing')
        if 'EventBusSubscriber.Bus.MOD' in java_text or 'bus = EventBusSubscriber.Bus.MOD' in java_text:
            fail(f'{target}: removed NeoForge 21.11 EventBusSubscriber bus selector remains')
        if '@EventBusSubscriber(modid = IronTanks.MODID, value = Dist.CLIENT)' not in java_text:
            fail(f'{target}: client mod event subscriber is not using the NeoForge 21.11 annotation shape')
    elif target.endswith('neoforge'):
        if 'Capabilities.FluidHandler.BLOCK' not in java_text:
            fail(f'{target}: NeoForge fluid capability registration is missing')
        if '@EventBusSubscriber(modid = IronTanks.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)' not in java_text:
            fail(f'{target}: legacy NeoForge client events must remain explicitly subscribed to the MOD bus')

    blocks_path = java_root / 'com/indemnity83/irontanks/common/registry/IronTanksBlocks.java'
    items_path = java_root / 'com/indemnity83/irontanks/common/registry/IronTanksItems.java'
    blocks = blocks_path.read_text(encoding='utf-8')
    items = items_path.read_text(encoding='utf-8')
    for field, (class_name, capacity, hardness, resistance) in BLOCK_SPECS.items():
        if target.endswith('neoforge'):
            if field == 'CREATIVE_TANK':
                pattern = rf'{field}\s*=\s*registerTank\("creative_tank",\s*properties\s*->\s*new\s+{class_name}\({capacity},\s*properties\)\)'
            else:
                pattern = rf'{field}\s*=\s*registerTank\("[a-z_]+",\s*properties\s*->\s*new\s+{class_name}\({capacity},\s*{re.escape(hardness)},\s*{re.escape(resistance)},\s*properties\)\)'
        elif field == 'CREATIVE_TANK':
            pattern = rf'{field}\s*=\s*BLOCKS\.register\("creative_tank",\s*\(\)\s*->\s*new\s+{class_name}\({capacity}\)\)'
        else:
            pattern = rf'{field}\s*=\s*BLOCKS\.register\("[a-z_]+",\s*\(\)\s*->\s*new\s+{class_name}\({capacity},\s*{re.escape(hardness)},\s*{re.escape(resistance)}\)\)'
        if not re.search(pattern, blocks):
            fail(f'{target}: tank spec changed or missing for {field}')
    for field, (source, dest) in UPGRADE_SPECS.items():
        if source.startswith('BCFactoryBlocks.'):
            source_expr = re.escape(source)
        else:
            source_expr = rf'IronTanksBlocks\.{source}'
        dest_expr = rf'IronTanksBlocks\.{dest}'
        pattern = rf'{field}\s*=\s*upgrade\("[a-z_]+",\s*{source_expr},\s*{dest_expr}\)'
        if not re.search(pattern, items):
            fail(f'{target}: upgrade graph changed or missing for {field}')

    pack = read_json(resources / 'pack.mcmeta').get('pack', {})
    expected_pack = (
        float(prop(props, target, 'pack.format')),
        float(prop(props, target, 'pack.resource_format')),
        float(prop(props, target, 'pack.data_format')),
    )
    actual_pack = (
        pack.get('pack_format'), pack.get('forge:resource_pack_format'), float(pack.get('forge:data_pack_format'))
    )
    if actual_pack != expected_pack:
        fail(f'{target}: pack formats {actual_pack} != {expected_pack}')

    validate_recipe_tags(target, resources)

    if target in ('1.21.11-neoforge', '26.1.2-neoforge', '26.2-neoforge', '26.3-neoforge'):
        legacy_models = {path.stem for path in (resources / 'assets/irontanks/models/item').glob('*.json')}
        client_items = {path.stem for path in (resources / 'assets/irontanks/items').glob('*.json')}
        if client_items != legacy_models:
            fail(f'{target}: client item definitions do not cover all item models')
        for recipe in (resources / 'data/irontanks/recipe').glob('*.json'):
            recipe_data = read_json(recipe)
            encoded = json.dumps(recipe_data)
            if '"item":' in encoded or '"tag":' in encoded:
                fail(f'{target}: legacy ingredient object remains in {recipe.relative_to(output)}')

    loader = target.rsplit('-', 1)[1]
    metadata_rel = 'META-INF/neoforge.mods.toml' if loader == 'neoforge' else 'META-INF/mods.toml'
    metadata_path = resources / metadata_rel
    if not metadata_path.is_file():
        fail(f'{target}: missing {metadata_rel}')
        return
    metadata = metadata_path.read_text(encoding='utf-8')
    values = {
        'mod_id': prop(props, target, 'mod.id'),
        'mod_name': prop(props, target, 'mod.name'),
        'mod_version': f"{prop(props, target, 'mod.version')}+{target.replace('-', '+')}",
        'mod_license': prop(props, target, 'mod.license'),
        'mod_authors': prop(props, target, 'mod.authors'),
        'mod_description': prop(props, target, 'mod.description'),
        'loader_version_range': prop(props, target, 'loader.version_range'),
        'minecraft_version_range': prop(props, target, 'minecraft.version_range'),
        'buildcraft_version_range': prop(props, target, 'buildcraft.version_range'),
        'forge_version_range': prop(props, target, 'forge.version_range'),
        'neo_version_range': prop(props, target, 'neoforge.version_range'),
    }
    expanded = metadata
    for key, value in values.items():
        expanded = expanded.replace('${' + key + '}', value)
    unresolved = sorted(set(re.findall(r'\$\{([^}]+)\}', expanded)))
    if unresolved:
        fail(f'{target}: unresolved metadata placeholders: {unresolved}')
    else:
        try:
            tomllib.loads(expanded)
        except tomllib.TOMLDecodeError as exc:
            fail(f'{target}: expanded metadata is invalid TOML: {exc}')
    for mod_id in ('buildcraftlib', 'buildcraftcore', 'buildcraftfactory'):
        if f'modId="{mod_id}"' not in metadata:
            fail(f'{target}: missing mandatory dependency on {mod_id}')


def validate_build_files() -> None:
    for relative in ('builds/legacy/build.forge.gradle', 'build-logic/neoforge-target.gradle'):
        text = (ROOT / relative).read_text(encoding='utf-8')
        for token in (
            "providers.gradleProperty('pythonExecutable')", 'sourceLayoutScript', 'prepareEffectiveSource',
            "requiredProperty('deps.buildcraft.modrinth_project')", "requiredProperty('buildcraft.version')",
            'maven.modrinth', "tasks.register('buildAndCollect'",
        ):
            if token not in text:
                fail(f'{relative}: missing build architecture token {token!r}')
        for forbidden in ('bcce_dependency_mode', 'buildcraft.local_jar', 'localBuildCraftJar'):
            if forbidden in text:
                fail(f'{relative}: obsolete local BCCE dependency token remains: {forbidden!r}')
    forge = (ROOT / 'builds/legacy/build.forge.gradle').read_text(encoding='utf-8')
    if 'implementation fg.deobf(buildCraftCoordinate)' not in forge:
        fail('Forge BCCE Maven dependency is not deobfuscated')
    neo = (ROOT / 'build-logic/neoforge-target.gradle').read_text(encoding='utf-8')
    if 'implementation buildCraftCoordinate' not in neo:
        fail('NeoForge BCCE Maven dependency is not configured as implementation')
    if "createMinecraftArtifacts" not in neo or 'dependsOn prepareEffectiveSource' not in neo:
        fail('NeoForge Minecraft artifact creation is not ordered after source materialization')
    for root in ('builds/modern', 'builds/26.X'):
        script = (ROOT / root / 'build.neoforge.gradle').read_text(encoding='utf-8')
        if "build-logic/neoforge-target.gradle" not in script:
            fail(f'{root}: shared NeoForge build implementation not applied')


def main() -> None:
    # Parse every maintained JSON file, excluding generated build output.
    for base in (ROOT / 'source-shared', ROOT / 'source-families', ROOT / 'source-platforms', ROOT / 'version-src'):
        for path in base.rglob('*.json'):
            read_json(path)

    props = load_properties()
    if prop(props, '1.19.2-forge', 'mod.license') != 'MIT':
        fail('ITCE must preserve the original MIT license')
    if prop(props, '1.19.2-forge', 'deps.buildcraft.modrinth_project') != 'z3Aj5eOl':
        fail('BCCE Modrinth Maven project ID must remain pinned to z3Aj5eOl')
    for target in target_ids(props):
        expected = f"8.0.26+{target.replace('-', '+')}"
        if prop(props, target, 'buildcraft.version') != expected:
            fail(f'{target}: BCCE Maven version must be pinned to {expected}')
        if prop(props, target, 'buildcraft.version_range') != '[8.0.24,)':
            fail(f'{target}: minimum supported BCCE version must be 8.0.24')

    validate_common_resources()
    validate_build_files()
    for target in target_ids(props):
        validate_target(target, props)

    if ERRORS:
        for error in ERRORS:
            print(f'ERROR: {error}', file=sys.stderr)
        raise SystemExit(1)
    print(f'Iron Tanks port verification OK: {len(target_ids(props))} targets, layered source tree, API2 behavior preserved')


if __name__ == '__main__':
    main()
