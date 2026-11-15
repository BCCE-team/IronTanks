"""Fabric 26.3 recipe-registry checks.

Minecraft 26.3 eagerly rejects unresolved item tag ingredients and an array of
alternative shaped-crafting key values. Keep the pack bootable with just BCCE,
Fabric API and Energy, while allowing optional metal-containing tiers to become
craftable when material providers supply their tags.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from source_layout import load_properties, materialize_target

RECIPE_REL = Path('src/main/resources/data/irontanks/recipe')
TAG_REL = Path('src/main/resources/data/irontanks/tags/item/compat')
OPTIONAL_METALS = {
    'c:ingots/silver',
    'c:ingots/titanium',
    'c:ingots/aluminum',
    'c:ingots/aluminium',
    'c:ingots/stainless_steel',
    'c:ingots/stainlesssteel',
    'c:ingots/tungsten_steel',
    'c:ingots/tungstensteel',
}


def loads(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def condition_passes(condition: dict, tags: set[str]) -> bool:
    kind = condition['condition']
    if kind == 'fabric:tags_populated':
        assert condition['registry'] == 'minecraft:item'
        return all(tag in tags for tag in condition['values'])
    if kind == 'fabric:or':
        return any(condition_passes(c, tags) for c in condition['values'])
    if kind == 'fabric:and':
        return all(condition_passes(c, tags) for c in condition['values'])
    raise AssertionError(f'Unexpected resource condition: {kind}')


def enabled(recipe: dict, tags: set[str]) -> bool:
    return all(condition_passes(c, tags) for c in recipe.get('fabric:load_conditions', []))


class FabricRecipeLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_properties()
        cls.tmp = tempfile.TemporaryDirectory(prefix='irontanks-fabric-recipes-')
        cls.fabric_root = materialize_target(
            '26.3-fabric', Path(cls.tmp.name) / 'fabric', cls.config
        )
        cls.neoforge_root = materialize_target(
            '26.3-neoforge', Path(cls.tmp.name) / 'neoforge', cls.config
        )
        cls.recipes = {
            f.stem: loads(f) for f in (cls.fabric_root / RECIPE_REL).glob('*.json')
        }
        cls.original_recipes = {
            f.stem: loads(f) for f in
            (cls.neoforge_root / RECIPE_REL).glob('*.json')
        }
        cls.tags = {
            f.relative_to(cls.fabric_root / TAG_REL).with_suffix('').as_posix(): loads(f)
            for f in (cls.fabric_root / TAG_REL).rglob('*.json')
        }

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_30_recipe_results_and_patterns_match_neoforge(self):
        self.assertEqual(len(self.original_recipes), 30)
        self.assertEqual(self.recipes.keys(), self.original_recipes.keys())
        for name, recipe in self.recipes.items():
            with self.subTest(recipe=name):
                original = self.original_recipes[name]
                self.assertEqual(recipe['type'], original['type'])
                self.assertEqual(recipe['pattern'], original['pattern'])
                self.assertEqual(recipe['result'], original['result'])

    def test_fabric_keys_are_valid_string_ingredients(self):
        for name, recipe in self.recipes.items():
            with self.subTest(recipe=name):
                self.assertTrue(all(isinstance(value, str) for value in recipe['key'].values()))
                self.assertTrue(all(isinstance(row, str) for row in recipe['pattern']))
                self.assertTrue(all(len(row) == len(recipe['pattern'][0]) for row in recipe['pattern']))
                self.assertTrue(set(''.join(recipe['pattern'])) - {' '} <= set(recipe['key']))

    def test_every_owned_compat_tag_is_defined_and_has_safe_entries(self):
        self.assertEqual(len(self.tags), 12)
        for name, recipe in self.recipes.items():
            for ingredient in recipe['key'].values():
                if not ingredient.startswith('#irontanks:compat/'):
                    continue
                tag = ingredient.split('compat/', 1)[1]
                with self.subTest(recipe=name, tag=tag):
                    self.assertIn(tag, self.tags)
        for name, data in self.tags.items():
            with self.subTest(tag=name):
                for member in data['values']:
                    if isinstance(member, dict):
                        self.assertEqual(set(member), {'id', 'required'})
                        self.assertTrue(member['id'].startswith('#c:'))
                        self.assertIs(member['required'], False)
                    else:
                        self.assertTrue(member.startswith('minecraft:'))
        self.assertEqual(
            [m for m in self.tags['ingots/stainless_steel']['values'] if isinstance(m, str)],
            [], 'Special alloy tags must not gain substitute vanilla metals')

    def test_vanilla_only_modpack_does_not_load_missing_metal_recipes(self):
        # Missing c:ingots/silver etc. must not reach Minecraft's strict
        # ingredient parser. Vanilla-only materials use own fallback tags.
        available_tags: set[str] = set()
        optional_recipe_names = []
        vanilla_recipe_names = []
        for name, recipe in self.recipes.items():
            input_strings = set(sum((v if isinstance(v, list) else [v]
                                     for v in self.original_recipes[name]['key'].values()), []))
            rare_metals = {s[1:] for s in input_strings if s.startswith('#')
                           and s[1:] in OPTIONAL_METALS}
            if rare_metals:
                optional_recipe_names.append(name)
                self.assertFalse(enabled(recipe, available_tags), name)
            else:
                vanilla_recipe_names.append(name)
                self.assertTrue(enabled(recipe, available_tags), name)
        self.assertGreaterEqual(len(optional_recipe_names), 10)
        self.assertGreaterEqual(len(vanilla_recipe_names), 5)

    def test_optional_metal_recipe_guards_match_original_ingredients(self):
        for name, recipe in self.recipes.items():
            original = self.original_recipes[name]
            alt_requirements = []
            for ingredient in original['key'].values():
                if isinstance(ingredient, list):
                    original_tags = [tag[1:] for tag in ingredient if tag.startswith('#')]
                    if any(tag in OPTIONAL_METALS for tag in original_tags):
                        alt_requirements.append(set(original_tags))
                elif ingredient.startswith('#') and ingredient[1:] in OPTIONAL_METALS:
                    alt_requirements.append({ingredient[1:]})
            for selection in [set(), {'c:ingots/silver'}, {'c:ingots/titanium'},
                              {'c:ingots/aluminium'}, {'c:ingots/aluminum'},
                              {'c:ingots/stainlesssteel'}, {'c:ingots/stainless_steel'},
                              {'c:ingots/tungstensteel'}, {'c:ingots/tungsten_steel'},
                              set(OPTIONAL_METALS)]:
                with self.subTest(recipe=name, tags=sorted(selection)):
                    expected = all(not required.isdisjoint(selection)
                                   for required in alt_requirements)
                    self.assertEqual(enabled(recipe, selection), expected)

    def test_existing_neoforge_recipes_remain_unchanged(self):
        family = ROOT / 'source-families/26.X/src/main/resources/data/irontanks/recipe'
        for name, data in self.original_recipes.items():
            with self.subTest(recipe=name):
                self.assertEqual(data, loads(family / f'{name}.json'))
                self.assertNotIn('fabric:load_conditions', data)


if __name__ == '__main__':
    unittest.main()
