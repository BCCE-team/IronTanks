"""Regression guard for materialized Fabric resources under Gradle 9.8+."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
GRADLE = ROOT / "build-logic/fabric-target.gradle"


class FabricGradleResourceDependencies(unittest.TestCase):
    def test_all_process_resources_tasks_depend_on_source_materialization(self):
        script = GRADLE.read_text(encoding="utf-8")
        match = re.search(
            r"tasks\.withType\(ProcessResources\)\.configureEach\s*\{(.*?)\}",
            script, flags=re.S,
        )
        self.assertIsNotNone(match, "ProcessResources hook must include test resources")
        self.assertRegex(match.group(1), r"\bdependsOn\s+prepareEffectiveSource\b")

    def test_test_resources_are_part_of_materialized_source(self):
        script = GRADLE.read_text(encoding="utf-8")
        self.assertIn("new File(effectiveSourceDir, 'src/test/resources')", script)
        self.assertIn("tasks.named('processResources', ProcessResources)", script)


if __name__ == "__main__":
    unittest.main()
