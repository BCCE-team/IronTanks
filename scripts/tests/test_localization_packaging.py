"""Dependency-free tests for external Iron Tanks translation import and JAR checks."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import embed_localizations as loc


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.source = self.root / 'Localizations'
        self.english = self.root / 'en_us.json'
        self.guide = self.root / 'guide-en_us.json'
        self.staged = self.root / 'stage'
        self.jar = self.root / 'test.jar'
        self.save(self.english, {'item.irontanks.test': 'Test tank'})
        self.save(self.guide, {'format': 1, 'language': 'en_us', 'pages': {'irontanks/test': ['Test']}})
        self.save(self.source / 'irontanks/lang/ru_ru.json', {'item.irontanks.test': 'Бак'})
        self.save(self.source / 'irontanks/guide/text/ru_ru.json',
                  {'format': 1, 'language': 'ru_ru', 'pages': {'irontanks/test': ['Тест']}})
        self.save(self.source / 'irontanks/guide/languages.json', {
            'format': 1, 'default': 'en_us',
            'languages': {
                'en_us': {'name': 'English (US)', 'fallback': []},
                'ru_ru': {'name': 'Русский', 'fallback': ['en_us']},
            },
            'aliases': {'ru_ua': 'ru_ru'},
        })

    @staticmethod
    def save(path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def stage_localizations(self, source: Path | None = None) -> int:
        return loc.main(['stage', '--root', str(self.root), '--cache', str(self.root / 'cache'),
                         '--source', str(source or self.source), '--output', str(self.staged),
                         '--english', str(self.english), '--english-guide', str(self.guide)])

    def make_jar(self, extra: dict[str, bytes] | None = None, duplicate: bool = False):
        resources = loc.resource_files(self.source, self.english, self.guide)
        resources.update(loc.english_files(self.english, self.guide))
        with ZipFile(self.jar, 'w') as jar:
            for dest, path in resources.items():
                jar.writestr(dest, loc.packaged_resource_bytes(dest, path))
            for dest, data in (extra or {}).items():
                jar.writestr(dest, data)
            if duplicate:
                jar.writestr('assets/irontanks/lang/ru_ru.json', b'{}')

    def verify(self):
        return loc.main(['verify-jar', '--source', str(self.source),
                         '--english', str(self.english), '--english-guide', str(self.guide),
                         '--jar', str(self.jar)])

    def test_staging_keeps_canonical_english_and_guide_language_index(self):
        self.assertEqual(self.stage_localizations(), 0)
        self.assertFalse((self.staged / 'assets/irontanks/lang/en_us.json').exists())
        self.assertFalse((self.staged / 'assets/irontanks/guide/text/en_us.json').exists())
        self.assertEqual(
            (self.staged / 'assets/irontanks/lang/ru_ru.json').read_bytes(),
            (self.source / 'irontanks/lang/ru_ru.json').read_bytes())
        self.assertEqual(
            (self.staged / 'assets/irontanks/guide/languages.json').read_bytes(),
            (self.source / 'irontanks/guide/languages.json').read_bytes())
        self.assertEqual(json.loads(self.english.read_text())['item.irontanks.test'], 'Test tank')

    def test_jar_contains_exactly_the_requested_localizations(self):
        self.make_jar()
        self.assertEqual(self.verify(), 0)

    def test_missing_or_stale_resources_fail_verification(self):
        self.make_jar({'assets/irontanks/lang/zz_zz.json': b'{}'})
        self.assertEqual(self.verify(), 1)

    def test_buildcraft_translations_must_not_leak(self):
        self.make_jar({'assets/buildcraft/lang/ru_ru.json': b'{}'})
        self.assertEqual(self.verify(), 1)

    def test_duplicate_jar_resources_fail(self):
        self.make_jar(duplicate=True)
        self.assertEqual(self.verify(), 1)

    def test_duplicate_json_keys_fail(self):
        (self.source / 'irontanks/lang/ru_ru.json').write_text(
            '{"item.irontanks.test":"one","item.irontanks.test":"two"}', encoding='utf-8')
        self.assertEqual(self.stage_localizations(), 1)

    def test_guide_locale_and_manifest_must_match(self):
        self.save(self.source / 'irontanks/guide/text/ru_ru.json',
                  {'format': 1, 'language': 'de_de', 'pages': {}})
        self.assertEqual(self.stage_localizations(), 1)

    def test_pages_only_guide_translation_is_normalized_for_game_and_verified(self):
        # BCCE-team/Localizations/irontanks/guide/text/lt_lt.json currently has
        # just {"pages": ...}, without "format" or "language".
        self.save(self.source / 'irontanks/lang/lt_lt.json', {'item.irontanks.test': 'Bakas'})
        pages = {'irontanks/test': ['Bandymas']}
        self.save(self.source / 'irontanks/guide/text/lt_lt.json', {'pages': pages})
        index = json.loads((self.source / 'irontanks/guide/languages.json').read_text(encoding='utf-8'))
        index['languages']['lt_lt'] = {'name': 'Lietuvių', 'fallback': ['en_us']}
        self.save(self.source / 'irontanks/guide/languages.json', index)

        self.assertEqual(self.stage_localizations(), 0)
        staged = json.loads((self.staged / 'assets/irontanks/guide/text/lt_lt.json').read_text('utf-8'))
        self.assertEqual(staged, {'format': 1, 'language': 'lt_lt', 'pages': pages})
        self.assertEqual(json.loads((self.source / 'irontanks/guide/text/lt_lt.json').read_text('utf-8')),
                         {'pages': pages})  # do not rewrite upstream checkout
        self.make_jar()
        self.assertEqual(self.verify(), 0)

    def test_raw_pages_only_json_in_jar_fails_verification(self):
        self.save(self.source / 'irontanks/guide/text/ru_ru.json',
                  {'pages': {'irontanks/test': ['Тест']}})
        resources = loc.resource_files(self.source, self.english, self.guide)
        resources.update(loc.english_files(self.english, self.guide))
        with ZipFile(self.jar, 'w') as jar:
            for dest, path in resources.items():
                jar.write(path, dest)  # intentionally bypass compatibility normalization
        self.assertEqual(self.verify(), 1)

    def test_partial_or_incorrect_guide_header_is_still_rejected(self):
        for malformed in (
            {'language': 'ru_ru', 'pages': {}},
            {'format': 1, 'pages': {}},
            {'format': 2, 'language': 'ru_ru', 'pages': {}},
            {'format': 1, 'language': 'de_de', 'pages': {}},
            {'pages': {'irontanks/test': 'not a list'}},
            {'pages': {'irontanks/test': [42]}},
        ):
            with self.subTest(malformed=malformed):
                self.save(self.source / 'irontanks/guide/text/ru_ru.json', malformed)
                self.assertEqual(self.stage_localizations(), 1)

    def test_no_other_mod_translations_are_copied(self):
        self.save(self.source / 'buildcraft/lang/ru_ru.json', {'anything': 'not iron tanks'})
        self.assertEqual(self.stage_localizations(), 0)
        self.assertEqual(len(list(self.staged.rglob('*.json'))), 3)

    def test_offline_mode_requires_checkout(self):
        self.assertEqual(loc.main(['stage', '--root', str(self.root),
                                   '--output', str(self.staged), '--cache', str(self.root / 'cache'),
                                   '--english', str(self.english), '--english-guide', str(self.guide),
                                   '--offline']), 1)

    def test_build_gradle_integration_and_release_separation(self):
        for path in ('builds/legacy/build.forge.gradle', 'build-logic/neoforge-target.gradle'):
            gradle = (ROOT / path).read_text(encoding='utf-8')
            for required in ('stageIronTanksLocalizations', 'localizationOutput',
                             'resources.setSrcDirs([localizationOutput.get().asFile,',
                             'dependsOn stageIronTanksLocalizations', 'DuplicatesStrategy.EXCLUDE'):
                self.assertIn(required, gradle)
        ci = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        publish = (ROOT / '.github/workflows/publish.yml').read_text(encoding='utf-8')
        self.assertNotIn('Kira-NT/mc-publish', ci)
        self.assertIn('Kira-NT/mc-publish@v3', publish)
        self.assertEqual(publish.count('uses: Kira-NT/mc-publish@v3'), 7)
        self.assertIn('ref: ${{ needs.metadata.outputs.localizations_sha }}', publish)
        self.assertIn('MODRINTH_DEPENDENCIES:', publish)
        self.assertIn('CURSEFORGE_DEPENDENCIES:', publish)
        for generation in ('legacy', 'modern', '26.X'):
            self.assertIn(f'irontanks-release-{generation}', publish)
            self.assertIn(f'builds/{generation}/gradlew', ci)
        for target in ('26.1.2', '26.2', '26.3'):
            self.assertIn(f'Publish {target} NeoForge', publish)



if __name__ == '__main__':
    unittest.main()
