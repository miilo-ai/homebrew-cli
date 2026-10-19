"""The static Ruby parser allows formatting but detects code/checksum changes."""
from pathlib import Path
import tempfile
import unittest

from review_release_formula import GitHub


class FormulaSyntax(unittest.TestCase):
    def test_only_formatting_and_generated_constant_freezing_are_ignored(self):
        original = 'class Miilo < Formula\n  BINARY_ALIASES = {\n    "arm": {}\n  }\nend\n'
        formatted = '# Generated comment\n' + original.replace('"arm": {}', '"arm": {},').replace('  }', '  }.freeze')
        github = GitHub()
        self.assertEqual(github.canonical(original), github.canonical(formatted))
        self.assertNotEqual(github.canonical(original), github.canonical(original.replace('arm', 'other')))
        self.assertNotEqual(github.canonical(original), github.canonical(original + 'puts "extra code"\n'))

    def test_checksums_and_string_whitespace_are_not_normalized(self):
        github = GitHub()
        a = 'class Miilo < Formula\n  sha256 "aaa"\nend\n'
        self.assertNotEqual(github.canonical(a), github.canonical(a.replace('aaa', 'bbb')))
        self.assertNotEqual(github.canonical(a), github.canonical(a.replace('aaa', 'aaa ')))

    def test_invalid_syntax_is_refused_and_ruby_is_never_executed(self):
        github = GitHub()
        with self.assertRaises(ValueError): github.canonical('class MissingEnd')
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary)/'must-not-exist'
            github.canonical(f'File.write({str(marker)!r}, "unexpected")\n')
            self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
