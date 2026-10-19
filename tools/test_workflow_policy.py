"""The tap qualifies imports; only the CLI publisher proposes review branches."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkflowPolicy(unittest.TestCase):
    def test_import_has_no_second_publisher_or_opt_in_publication_gate(self):
        source = (ROOT/'.github/workflows/import-release.yml').read_text()
        self.assertIn('workflow_dispatch:', source)
        self.assertNotIn('git push', source)
        self.assertNotIn('  publish:', source)
        self.assertNotIn('contents: write', source)
        self.assertIn('qualified-formula-', source)

    def test_required_formula_ci_runs_import_and_pr_regressions(self):
        source = (ROOT/'.github/workflows/test.yml').read_text()
        self.assertIn("unittest discover -s tools -p 'test_*.py'", source)
        self.assertIn('macos-latest', source)
        self.assertIn('ubuntu-latest', source)
        self.assertIn('brew test', source)


if __name__ == '__main__':
    unittest.main()
