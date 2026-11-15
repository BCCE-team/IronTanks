"""Regression guards for the eight-target GitHub Release publishing pipeline."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_fabric_release_jar import main as verify_fabric_jar
from source_layout import load_properties, materialize_target

RELEASE_TARGETS = [
    ('1.19.2', 'forge'), ('1.20.1', 'forge'),
    ('1.21.1', 'neoforge'), ('1.21.11', 'neoforge'),
    ('26.1.2', 'neoforge'), ('26.2', 'neoforge'),
    ('26.3', 'neoforge'), ('26.3', 'fabric'),
]


class ReleaseMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / '.github/workflows/publish.yml').read_text('utf-8')
        cls.ci = (ROOT / '.github/workflows/ci.yml').read_text('utf-8')
        cls.controller = (ROOT / 'builds/26.X/stonecutter.gradle.kts').read_text('utf-8')

    def test_only_release_event_can_publish(self):
        self.assertIn('types: [published]', self.workflow)
        self.assertIn('github.event.release.tag_name', self.workflow)
        self.assertNotIn('Kira-NT/mc-publish@v3', self.ci)
        self.assertEqual(self.workflow.count('uses: Kira-NT/mc-publish@v3'), 8)

    def test_publish_targets_in_correct_order(self):
        actual = re.findall(r'^\s+- name: Publish ([0-9.]+) (Forge|NeoForge|Fabric)$',
                            self.workflow, flags=re.M)
        normalized = [(mc, loader.lower()) for mc, loader in actual]
        self.assertEqual(normalized, RELEASE_TARGETS)
        self.assertIn("targets: '26.1.2-neoforge,26.2-neoforge,26.3-neoforge,26.3-fabric'", self.workflow)
        self.assertIn('"$target" == \'26.3-fabric\'', self.workflow)
        self.assertIn('scripts/verify_fabric_release_jar.py --jar "$jar" --version "$TAG"', self.workflow)

    def test_every_target_has_release_asset_and_matching_loader(self):
        chunks = re.split(r'(?=^\s+- name: Publish [0-9.]+ (?:Forge|NeoForge|Fabric)$)',
                          self.workflow, flags=re.M)
        publish_chunks = [chunk for chunk in chunks if re.search(r'- name: Publish [0-9.]+', chunk)]
        self.assertEqual(len(publish_chunks), 8)
        for (mc, loader), chunk in zip(RELEASE_TARGETS, publish_chunks):
            with self.subTest(mc=mc, loader=loader):
                artifact = f'+{mc}+{loader}.jar'
                self.assertIn(f'files: release/IronTanks-Community-Edition-', chunk)
                self.assertIn(artifact, chunk)
                self.assertIn(f'loaders: {loader}', chunk)
                self.assertIn(f'game-versions: {mc}', chunk)
                self.assertIn('version-type: release', chunk)
                self.assertIn('modrinth-id: ${{ env.MODRINTH_PROJECT_ID }}', chunk)
                self.assertIn('curseforge-id: ${{ env.CURSEFORGE_PROJECT_ID }}', chunk)
                self.assertIn('github-token: ${{ secrets.GITHUB_TOKEN }}', chunk)

    def test_fabric_dependencies_are_specific_to_fabric_release(self):
        fabric = self.workflow.split('- name: Publish 26.3 Fabric', 1)[1]
        self.assertIn('z3Aj5eOl(required)', fabric)
        self.assertIn('1592400(required)', fabric)
        self.assertIn('fabric-api(required)', fabric)
        self.assertIn('306612(required)', fabric)
        for text in self.workflow.split('- name: Publish 26.3 Fabric', 1)[:1]:
            self.assertNotIn('306612(required)', text)

    def test_build_and_ci_cover_fabric_release(self):
        self.assertIn('dependsOn(targets.map { target -> ":$target:buildAndCollect" })', self.controller)
        self.assertNotIn('filterNot { it.endsWith("-fabric") }', self.controller)
        self.assertNotIn('&& continue # Preview', self.ci)
        self.assertIn('scripts/verify_fabric_release_jar.py --jar "$jar" --version "$version"', self.ci)
        self.assertIn('test_fabric_recipe_loading.py', self.ci)
        self.assertIn('test_release_publish_matrix.py', self.workflow)


class FabricReleaseJar(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.jar = Path(self._temp.name) / 'example.jar'
        self.meta = json.loads((ROOT / 'version-src/26.3-fabric/src/main/resources/fabric.mod.json')
                               .read_text('utf-8'))
        self.meta['version'] = '3.0.4+26.3+fabric'
        merged = materialize_target('26.3-fabric', Path(self._temp.name) / 'merged', load_properties())
        resources = merged / 'src/main/resources/data/irontanks'
        self.recipes = resources / 'recipe'
        self.tags = resources / 'tags/item/compat'

    def make_jar(self, mutate=None):
        with ZipFile(self.jar, 'w') as jar:
            jar.writestr('fabric.mod.json', json.dumps(self.meta))
            for file in self.recipes.glob('*.json'):
                contents = json.loads(file.read_text('utf-8'))
                if mutate and file.name == 'glass_iron_tank.json':
                    mutate(contents)
                jar.writestr(f'data/irontanks/recipe/{file.name}', json.dumps(contents))
            for file in self.tags.rglob('*.json'):
                relative = file.relative_to(self.tags).as_posix()
                jar.write(file, f'data/irontanks/tags/item/compat/{relative}')

    def test_valid_fabric_release_passes(self):
        self.make_jar()
        self.assertEqual(verify_fabric_jar(['--jar', str(self.jar), '--version', '3.0.4']), 0)

    def test_wrong_version_fails(self):
        self.meta['version'] = '3.0.4+26.3+neoforge'
        self.make_jar()
        self.assertEqual(verify_fabric_jar(['--jar', str(self.jar), '--version', '3.0.4']), 1)

    def test_invalid_list_ingredient_fails(self):
        self.make_jar(lambda recipe: recipe['key'].update(g=['#c:glass_blocks', '#c:glass_blocks/colorless']))
        self.assertEqual(verify_fabric_jar(['--jar', str(self.jar), '--version', '3.0.4']), 1)

    def test_missing_optional_tag_guard_fails(self):
        def corrupt(recipe):
            recipe['key']['i'] = '#c:ingots/silver'
        self.make_jar(corrupt)
        self.assertEqual(verify_fabric_jar(['--jar', str(self.jar), '--version', '3.0.4']), 1)

    def test_missing_fabric_api_dependency_fails(self):
        self.meta['depends'].pop('fabric-api')
        self.make_jar()
        self.assertEqual(verify_fabric_jar(['--jar', str(self.jar), '--version', '3.0.4']), 1)


if __name__ == '__main__':
    unittest.main()
