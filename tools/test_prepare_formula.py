import unittest
from prepare_formula import prepare


def fixture():
    urls = ''.join('  url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.2.2/' + target + '.tar.xz"\n' for target in ['mac-arm', 'mac-intel', 'linux-arm', 'linux-intel'])
    return 'class Miilo < Formula\n  version "0.2.2"\n' + urls + 'end\n'


class FormulaImport(unittest.TestCase):
    def test_generated_formula_becomes_auditable_and_idempotent(self):
        result = prepare(fixture(), 'v0.2.2')
        self.assertNotIn('  version "', result)
        self.assertIn('miilo --version', result)
        self.assertIn('miilo-local --version', result)
        self.assertEqual(prepare(result, 'v0.2.2'), result)

    def test_other_hosts_versions_and_prereleases_fail(self):
        for source, tag in [(fixture(), 'v0.2.3'), (fixture(), 'v0.2.2-beta'), (fixture().replace('github.com', 'example.invalid'), 'v0.2.2')]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                prepare(source, tag)
