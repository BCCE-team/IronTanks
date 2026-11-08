#!/usr/bin/env python3
"""Stage Iron Tanks translations from BCCE-team/Localizations and verify production JARs.

The English UI/guide strings remain canonical in this repository. All non-English
JSON and the Guide Book language index are taken from the separate Localizations
repository at build time, never committed to the Iron Tanks source tree.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zipfile import BadZipFile, ZipFile

REMOTE = 'https://github.com/BCCE-team/Localizations.git'
LOCALE = re.compile(r'[a-z]{2,3}_[a-z]{2,3}\Z')
RESOURCE_PAIRS = (
    ('irontanks/lang', 'assets/irontanks/lang'),
    ('irontanks/guide/text', 'assets/irontanks/guide/text'),
)
GUIDE_INDEX = 'assets/irontanks/guide/languages.json'


class LocalizationError(Exception):
    """Human-readable error for invalid localization input or a broken build."""


def json_object(path: Path) -> dict:
    def unique_keys(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise LocalizationError(f'Duplicate JSON key {key!r} in {path}')
            result[key] = value
        return result

    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LocalizationError(f'Invalid JSON in {path}: {exc}') from exc
    if not isinstance(data, dict):
        raise LocalizationError(f'Expected a JSON object in {path}')
    return data


def english_files(ui: Path, guide: Path) -> dict[str, Path]:
    for path in (ui, guide):
        if not path.is_file():
            raise LocalizationError(f'Missing canonical English localization: {path}')
    ui_json = json_object(ui)
    if not ui_json or not all(isinstance(k, str) and isinstance(v, str) for k, v in ui_json.items()):
        raise LocalizationError(f'Invalid canonical UI translations: {ui}')
    guide_json = json_object(guide)
    if guide_json.get('format') != 1 or guide_json.get('language') != 'en_us':
        raise LocalizationError(f'Invalid canonical English Guide Book translations: {guide}')
    return {
        'assets/irontanks/lang/en_us.json': ui,
        'assets/irontanks/guide/text/en_us.json': guide,
    }


def resource_files(source: Path, english_ui: Path, english_guide: Path) -> dict[str, Path]:
    english_files(english_ui, english_guide)
    if not (source / 'irontanks/lang').is_dir():
        raise LocalizationError(f'Missing irontanks/lang in localization checkout: {source}')

    resources: dict[str, Path] = {}
    locales: dict[str, set[str]] = {'lang': set(), 'text': set()}
    for from_dir, to_dir in RESOURCE_PAIRS:
        directory = source / from_dir
        if not directory.is_dir():
            raise LocalizationError(f'Missing localization directory: {directory}')
        for path in sorted(directory.iterdir()):
            if not path.is_file() or path.suffix.lower() != '.json':
                continue
            if not LOCALE.fullmatch(path.stem):
                raise LocalizationError(f'Unexpected localization filename: {path}')
            if path.stem == 'en_us':
                # Iron Tanks owns its authoritative English resources.
                continue
            data = json_object(path)
            if from_dir.endswith('/lang'):
                if not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
                    raise LocalizationError(f'Non-string UI translation in {path}')
                locales['lang'].add(path.stem)
            else:
                pages = data.get('pages')
                valid_pages = isinstance(pages, dict) and all(
                    isinstance(k, str) and isinstance(v, list) and
                    all(isinstance(line, str) for line in v)
                    for k, v in pages.items()
                )
                # Some older translation contributions (notably lt_lt) contain only
                # the pages object. They are valid content but must be wrapped with
                # format/language metadata before shipping to the Guide Book.
                pages_only = set(data) == {'pages'}
                valid_header = data.get('format') == 1 and data.get('language') == path.stem
                if not valid_pages or not (pages_only or valid_header):
                    raise LocalizationError(f'Invalid Iron Tanks Guide Book language pack: {path}')
                locales['text'].add(path.stem)
            resources[f'{to_dir}/{path.name}'] = path

    if not locales['lang'] or not locales['text']:
        raise LocalizationError('No non-English Iron Tanks UI/Guide Book localizations found')
    if locales['lang'] != locales['text']:
        raise LocalizationError(
            f'UI/Guide Book language mismatch: UI-only={sorted(locales["lang"] - locales["text"])}; '
            f'Guide-only={sorted(locales["text"] - locales["lang"])}'
        )

    index_path = source / 'irontanks/guide/languages.json'
    if not index_path.is_file():
        raise LocalizationError(f'Missing Guide Book language index: {index_path}')
    index = json_object(index_path)
    languages = index.get('languages')
    if index.get('format') != 1 or index.get('default') != 'en_us' or not isinstance(languages, dict):
        raise LocalizationError(f'Invalid Guide Book language index: {index_path}')
    if set(languages) != locales['lang'] | {'en_us'}:
        raise LocalizationError(
            f'Guide Book language index does not match translation languages: {index_path}'
        )
    if not all(LOCALE.fullmatch(k) and isinstance(v, dict) and
               isinstance(v.get('name'), str) and isinstance(v.get('fallback'), list)
               and all(isinstance(x, str) and x in languages for x in v['fallback'])
               for k, v in languages.items()):
        raise LocalizationError(f'Invalid Guide Book language names/fallbacks: {index_path}')
    aliases = index.get('aliases', {})
    if not isinstance(aliases, dict) or not all(
        isinstance(k, str) and LOCALE.fullmatch(k) and isinstance(v, str) and v in languages
        for k, v in aliases.items()
    ):
        raise LocalizationError(f'Invalid Guide Book language aliases: {index_path}')
    resources[GUIDE_INDEX] = index_path
    return resources


def packaged_resource_bytes(name: str, path: Path) -> bytes:
    """Package legacy pages-only Guide Book translations with required metadata.

    Other resources are copied byte-for-byte. In particular, a fully formed
    locale must not be silently rewritten or have its declared language fixed.
    This function is called only after resource_files validated its input.
    """
    if name.startswith('assets/irontanks/guide/text/'):
        data = json_object(path)
        if set(data) == {'pages'}:
            normalized = {'format': 1, 'language': path.stem, 'pages': data['pages']}
            return (json.dumps(normalized, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return path.read_bytes()


def git(*args: str, cwd: Path | None = None) -> str:
    try:
        process = subprocess.run(
            ['git', *args], cwd=cwd, capture_output=True, encoding='utf-8',
            errors='replace', timeout=120, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LocalizationError(f'Git unavailable: {exc}') from exc
    if process.returncode:
        raise LocalizationError(f'git {" ".join(args[:3])} failed: {process.stderr.strip()}')
    return process.stdout.strip()


def discover(root: Path) -> Path | None:
    for path in (
        root / 'build/external/localizations',  # CI: checkout pinned to a SHA.
        root.parent / 'Localizations',
        root.parent / 'Localizations-main',
        root / 'localizations',
    ):
        if (path / 'irontanks/lang').is_dir():
            return path.resolve()
    return None


def source_checkout(args: argparse.Namespace) -> Path:
    if args.source:
        path = Path(args.source).expanduser()
        if not path.is_absolute():
            path = args.root / path
        path = path.resolve()
        if not (path / 'irontanks/lang').is_dir():
            raise LocalizationError(
                f'Invalid translation checkout: {path}. Pass '
                '-PirontanksLocalizationsDir=<path> or IRONTANKS_LOCALIZATIONS_DIR.'
            )
        return path
    found = discover(args.root)
    if found is not None:
        return found

    cache = args.cache.resolve()
    if (cache / '.git').exists():
        if not args.offline:
            git('fetch', '--quiet', '--no-tags', '--depth=1', 'origin', args.ref, cwd=cache)
            git('checkout', '--quiet', '--detach', '--force', 'FETCH_HEAD', cwd=cache)
        return cache
    if cache.exists():
        raise LocalizationError(f'Localization cache exists but is not a Git checkout: {cache}')
    if args.offline:
        raise LocalizationError(
            'Translations are unavailable offline. Clone BCCE-team/Localizations beside '
            'IronTanks or set -PirontanksLocalizationsDir=<path>.'
        )

    cache.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='irontanks-localizations-', dir=cache.parent) as temp:
        checkout = Path(temp) / 'checkout'
        git('init', '--quiet', str(checkout))
        git('remote', 'add', 'origin', args.remote, cwd=checkout)
        git('fetch', '--quiet', '--no-tags', '--depth=1', 'origin', args.ref, cwd=checkout)
        git('checkout', '--quiet', '--detach', '--force', 'FETCH_HEAD', cwd=checkout)
        shutil.move(str(checkout), cache)
    return cache


def stage(args: argparse.Namespace) -> None:
    source = source_checkout(args)
    resources = resource_files(source, args.english, args.english_guide)
    output = args.output.resolve()
    if source == output or source in output.parents or output in source.parents or output == args.root:
        raise LocalizationError('Translation stage directory must not overwrite the source checkout')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='irontanks-lang-stage-', dir=output.parent) as tmp:
        staged = Path(tmp) / 'resources'
        for name, original in resources.items():
            dest = staged / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(packaged_resource_bytes(name, original))
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(staged), output)
    print(f'Iron Tanks: staged {len(resources) - 1} non-English localization JSON files '
          f'and the Guide Book language index from {source}')
    normalized = sorted(path.stem for name, path in resources.items()
                        if name.startswith('assets/irontanks/guide/text/')
                        and set(json_object(path)) == {'pages'})
    if normalized:
        print(f'Normalized pages-only Guide Book translations: {", ".join(normalized)}')
    if (source / '.git').exists():
        print(f'Pinned translation revision: {git("rev-parse", "HEAD", cwd=source)}')


def verify_jar(args: argparse.Namespace) -> None:
    source = args.source.resolve()
    resources = resource_files(source, args.english, args.english_guide)
    resources.update(english_files(args.english, args.english_guide))
    if not args.jar.is_file():
        raise LocalizationError(f'Built JAR does not exist: {args.jar}')
    with ZipFile(args.jar) as archive:
        names = archive.namelist()
        duplicates = [name for name, count in Counter(names).items() if count > 1 and
                      name.startswith('assets/irontanks/')]
        if duplicates:
            raise LocalizationError(f'Duplicate Iron Tanks resources in JAR: {sorted(duplicates)}')
        paths = set(names)
        for name, source_path in resources.items():
            if name not in paths:
                raise LocalizationError(f'JAR lacks required localization: {name}')
            if archive.read(name) != packaged_resource_bytes(name, source_path):
                raise LocalizationError(f'JAR localization differs from normalized source: {name}')
        actual = {x for x in paths if x.startswith(('assets/irontanks/lang/', 'assets/irontanks/guide/text/'))
                  and x.endswith('.json')}
        expected = {x for x in resources if x.startswith(('assets/irontanks/lang/', 'assets/irontanks/guide/text/'))}
        if actual != expected:
            raise LocalizationError(f'Unexpected/missing localization files: {sorted(actual ^ expected)}')
        if any(x.startswith(('assets/buildcraft/lang/', 'assets/buildcraft/guide/text/')) for x in paths):
            raise LocalizationError('BuildCraft translations must not be included in Iron Tanks')
    print(f'Verified {len(resources)} Iron Tanks localizations/index resources in {args.jar}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    stage_parser = commands.add_parser('stage', help='download/discover and stage translations')
    stage_parser.add_argument('--root', type=Path, required=True)
    stage_parser.add_argument('--output', type=Path, required=True)
    stage_parser.add_argument('--cache', type=Path, required=True)
    stage_parser.add_argument('--english', type=Path, required=True)
    stage_parser.add_argument('--english-guide', type=Path, required=True)
    stage_parser.add_argument('--source', default=None)
    stage_parser.add_argument('--ref', default='main')
    stage_parser.add_argument('--remote', default=REMOTE)
    stage_parser.add_argument('--offline', action='store_true')
    verify_parser = commands.add_parser('verify-jar', help='check localization packaging against checkout')
    verify_parser.add_argument('--source', type=Path, required=True)
    verify_parser.add_argument('--english', type=Path, required=True)
    verify_parser.add_argument('--english-guide', type=Path, required=True)
    verify_parser.add_argument('--jar', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'stage':
            args.root = args.root.resolve()
            stage(args)
        else:
            verify_jar(args)
    except (LocalizationError, OSError, ValueError, BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
