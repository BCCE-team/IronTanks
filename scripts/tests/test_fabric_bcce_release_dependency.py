"""Guard the canonical BCCE 26.3 Fabric GitHub release dependency.

The Modrinth Maven version ID used by the 3.0.5 release was not resolvable
on a clean GitHub Actions runner. The authoritative 8.0.30 Fabric JAR is
available on the upstream BuildCraft GitHub Release instead.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
GRADLE = (ROOT / 'build-logic/fabric-target.gradle').read_text(encoding='utf-8')
CONFIG = (ROOT / 'builds/26.X/targets.properties').read_text(encoding='utf-8')


class FabricBuildCraftDependency(unittest.TestCase):
    def test_release_version_matches_upstream_release_asset(self):
        self.assertIn('target.26.3-fabric.buildcraft.version=8.0.30+26.3+fabric', CONFIG)
        self.assertIn("bcceReleaseTag = bcceExpectedVersion.tokenize('+').first()", GRADLE)
        self.assertIn('"${bcceReleaseTag}+${minecraftVersion}+fabric"', GRADLE)
        self.assertIn("artifact '[revision]/BuildCraft-Community-Edition-[revision]+26.3+fabric.[ext]'", GRADLE)
        self.assertIn("url = 'https://github.com/BCCE-team/BuildCraft/releases/download'", GRADLE)
        self.assertIn("bcce.github.release:buildcraft:${bcceReleaseTag}@jar", GRADLE)

    def test_repository_is_exclusive_and_artifact_only(self):
        self.assertIn('exclusiveContent {', GRADLE)
        self.assertIn('metadataSources { artifact() }', GRADLE)
        self.assertIn("includeGroup 'bcce.github.release'", GRADLE)
        self.assertIn('implementation bcceCoordinate', GRADLE)
        self.assertIn('bcceFabricArtifact bcceCoordinate', GRADLE)
        self.assertNotIn('XTATlTsu', GRADLE + CONFIG)
        self.assertNotIn('buildcraft.maven_version', GRADLE + CONFIG)
        self.assertNotIn('https://api.modrinth.com/maven', GRADLE)

    def test_exact_upstream_sha256_is_verified_before_compilation(self):
        sha = re.search(r'^target\.26\.3-fabric\.buildcraft\.sha256=([a-f0-9]{64})$', CONFIG, flags=re.M)
        self.assertIsNotNone(sha)
        self.assertEqual(sha.group(1), '38b3ebdb7bf0b1f2b145fd82ce23604c123d0c5e5e1e50b8206b81a6e888ae51')
        self.assertIn("MessageDigest.getInstance('SHA-256')", GRADLE)
        self.assertIn('actualSha256 != bcceExpectedSha256', GRADLE)
        self.assertIn('json.version != bcceExpectedVersion', GRADLE)
        self.assertIn("tasks.named('compileJava') { dependsOn verifyBCCE263FabricArtifact }", GRADLE)


if __name__ == '__main__':
    unittest.main()
