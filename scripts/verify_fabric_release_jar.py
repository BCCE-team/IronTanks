#!/usr/bin/env python3
"""Release preflight for Iron Tanks 26.3 Fabric artifact (stdlib only).

This is a structural guard, not a substitute for Minecraft registry loading or GameTests.
It catches invalid packaged metadata, lost recipe overlays and the ingredient-list
regression that previously crashed clients when opening a world.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

RECIPE_ROOT = 'data/irontanks/recipe/'
COMPAT_TAG_ROOT = 'data/irontanks/tags/item/compat/'
EXPECTED_RECIPES = 30
OPTIONAL_METALS = {
    'c:ingots/silver', 'c:ingots/titanium',
    'c:ingots/aluminium', 'c:ingots/aluminum',
    'c:ingots/stainlesssteel', 'c:ingots/stainless_steel',
    'c:ingots/tungstensteel', 'c:ingots/tungsten_steel',
}


class ReleaseJarError(ValueError):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseJarError(message)


def decode_json(jar: ZipFile, name: str):
    try:
        return json.loads(jar.read(name).decode('utf-8'))
    except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseJarError(f'Invalid or missing JSON in {name}: {exc}') from exc


def guarded_tag(conditions, tag: str) -> bool:
    """Check that a missing optional tag cannot be used by an enabled recipe."""
    if not isinstance(conditions, list):
        return False
    for condition in conditions:
        if not isinstance(condition, dict):
            continue
        kind = condition.get('condition')
        if kind == 'fabric:tags_populated' and tag in condition.get('values', []):
            return True
        if kind == 'fabric:and' and guarded_tag(condition.get('values'), tag):
            return True
    return False


def validate(jar_path: Path, version: str) -> int:
    check(jar_path.is_file(), f'Fabric release JAR does not exist: {jar_path}')
    try:
        with ZipFile(jar_path) as jar:
            names = jar.namelist()
            members = set(names)
            check(len(names) == len(members), 'Duplicate JAR entries detected')
            check(jar.testzip() is None, 'Fabric release JAR contains a corrupt ZIP member')
            check('fabric.mod.json' in members, 'Missing fabric.mod.json')
            meta = decode_json(jar, 'fabric.mod.json')
            check(meta.get('id') == 'irontanks', 'Wrong Fabric mod ID')
            check(meta.get('version') == f'{version}+26.3+fabric',
                  'Fabric mod version does not match release tag')
            deps = meta.get('depends')
            check(isinstance(deps, dict), 'Missing Fabric dependency declarations')
            check(deps.get('minecraft') == '26.3', 'Wrong Minecraft version in Fabric metadata')
            check(deps.get('java') == '>=25', 'Fabric mod must require Java 25')
            check('buildcraftlib' in deps, 'Missing required BuildCraft dependency')
            check('fabric-api' in deps, 'Missing required Fabric API dependency')
            check(isinstance(meta.get('entrypoints', {}).get('main'), list),
                  'Fabric main entrypoint missing')

            recipes = sorted(p for p in members if p.startswith(RECIPE_ROOT) and p.endswith('.json'))
            check(len(recipes) == EXPECTED_RECIPES,
                  f'Expected {EXPECTED_RECIPES} Fabric recipes, found {len(recipes)}')
            seen_tags: set[str] = set()
            for recipe_file in recipes:
                recipe = decode_json(jar, recipe_file)
                check(recipe.get('type') == 'minecraft:crafting_shaped',
                      f'Unexpected recipe type: {recipe_file}')
                key = recipe.get('key')
                pattern = recipe.get('pattern')
                check(isinstance(key, dict) and isinstance(pattern, list) and pattern,
                      f'Missing crafting key/pattern: {recipe_file}')
                check(all(isinstance(row, str) and len(row) == len(pattern[0]) for row in pattern),
                      f'Invalid crafting pattern: {recipe_file}')
                check(all(isinstance(ingredient, str) for ingredient in key.values()),
                      f'Unsupported list/object ingredient in {recipe_file}')
                check(set(''.join(pattern)) - {' '} <= set(key),
                      f'Crafting pattern refers to undefined ingredient in {recipe_file}')
                for ingredient in key.values():
                    if ingredient.startswith('#irontanks:compat/'):
                        seen_tags.add(ingredient.removeprefix('#irontanks:compat/'))
                    if ingredient.startswith('#') and ingredient[1:] in OPTIONAL_METALS:
                        check(guarded_tag(recipe.get('fabric:load_conditions'), ingredient[1:]),
                              f'Unguarded optional metal tag {ingredient} in {recipe_file}')
            for name in sorted(seen_tags):
                tag_file = f'{COMPAT_TAG_ROOT}{name}.json'
                check(tag_file in members, f'Missing referenced Iron Tanks tag {tag_file}')
                definition = decode_json(jar, tag_file)
                check(isinstance(definition.get('values'), list) and definition['values'],
                      f'Empty/invalid tag {tag_file}')
            print(f'Fabric release JAR OK: {jar_path.name}; '
                  f'{len(recipes)} recipes; {len(seen_tags)} referenced compatibility tags')
            return 0
    except BadZipFile as exc:
        raise ReleaseJarError(f'Not a valid JAR/ZIP: {jar_path}: {exc}') from exc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, required=True)
    parser.add_argument('--version', required=True, help='GitHub release tag, e.g. 3.0.4')
    args = parser.parse_args(argv)
    try:
        return validate(args.jar, args.version)
    except ReleaseJarError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
