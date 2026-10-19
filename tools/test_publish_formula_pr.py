"""Exercise branch publication against a real disposable Git remote, with a fake GH API."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import publish_formula_pr as publisher


class FormulaPullRequest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        root = Path(self.folder.name)
        self.remote, self.repo = root/'remote.git', root/'checkout'
        subprocess.run(['git', 'init', '--bare', '-q', '--initial-branch=main', self.remote], check=True)
        subprocess.run(['git', 'clone', '-q', str(self.remote), str(self.repo)], check=True, capture_output=True)
        self.original = Path.cwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self.original)
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        Path('Formula').mkdir()
        Path('Formula/miilo.rb').write_text('old formula\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'initial formula')
        self.git('push', '-qu', 'origin', 'main')
        self.base = self.git('rev-parse', 'HEAD')
        self.calls, self.open_pr = [], False
        self.real_run = publisher.run
        self.addCleanup(patch.stopall)
        patch.object(publisher, 'run', side_effect=self.command).start()

    def git(self, *args):
        return subprocess.check_output(['git', *args], text=True, stderr=subprocess.DEVNULL).strip()

    def command(self, *args, **kwargs):
        self.calls.append(args)
        if args[0] != 'gh':
            return self.real_run(*args, **kwargs)
        if args[1:3] == ('pr', 'list'):
            data = [{'state':'OPEN', 'url':'https://example.invalid/pr/1'}] if self.open_pr else []
            return SimpleNamespace(stdout=json.dumps(data), returncode=0)
        self.open_pr = True
        return SimpleNamespace(stdout='https://example.invalid/pr/1\n', returncode=0)

    def prepare_change(self):
        Path('Formula/miilo.rb').write_text('qualified formula\n')
        self.assertTrue(publisher.prepare('v0.3.1'))

    def test_opens_one_pr_without_writing_main_and_retry_reuses_it(self):
        publisher.publish('v0.3.1', preflight=True)
        self.prepare_change()
        first = publisher.publish('v0.3.1')
        second = publisher.publish('v0.3.1')
        self.assertEqual(first, second)
        self.assertEqual(self.git('ls-remote', 'origin', 'refs/heads/main').split()[0], self.base)
        self.assertTrue(self.git('ls-remote', 'origin', 'refs/heads/release/miilo-v0.3.1'))
        creates = [call for call in self.calls if call[:3] == ('gh', 'pr', 'create')]
        self.assertEqual(len(creates), 1)
        self.assertTrue(any('--body-file' in call for call in creates))
        for call in self.calls:
            if call[:2] == ('git', 'push'):
                self.assertNotIn('--force', call)
                self.assertTrue(call[-1].endswith(':refs/heads/release/miilo-v0.3.1'))

    def test_preflight_leaves_no_branch_and_failure_is_actionable(self):
        publisher.publish('v0.3.1', preflight=True)
        self.assertEqual(self.git('ls-remote', 'origin', 'refs/heads/release/miilo-v0.3.1'), '')
        def denied(*args, **kwargs):
            if args[:2] == ('git', 'push'):
                return SimpleNamespace(returncode=128, stderr='denied', stdout='')
            return self.command(*args, **kwargs)
        with patch.object(publisher, 'run', side_effect=denied):
            with self.assertRaisesRegex(RuntimeError, 'HOMEBREW_TAP_TOKEN'):
                publisher.publish('v0.3.1', preflight=True)

    def test_pr_creation_failure_can_retry_without_another_push(self):
        self.prepare_change()
        def denied(*args, **kwargs):
            if args[:3] == ('gh', 'pr', 'create'):
                raise RuntimeError('PR permission denied')
            return self.command(*args, **kwargs)
        with patch.object(publisher, 'run', side_effect=denied):
            with self.assertRaisesRegex(RuntimeError, 'PR permission denied'):
                publisher.publish('v0.3.1')
        self.assertEqual(publisher.publish('v0.3.1'), 'https://example.invalid/pr/1')
        pushes = [call for call in self.calls if call[:2] == ('git', 'push')]
        self.assertEqual(len(pushes), 1)

    def test_no_change_needs_no_pr(self):
        self.assertFalse(publisher.prepare('v0.3.1'))
        self.assertIsNone(publisher.publish('v0.3.1'))
        self.assertFalse(any(call[0] == 'gh' for call in self.calls))

    def test_unrelated_changes_are_rejected_before_commit(self):
        Path('unexpected').write_text('unrelated')
        self.git('add', '.')
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            publisher.prepare('v0.3.1')
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.base)

    def test_existing_release_branch_is_never_overwritten(self):
        self.prepare_change()
        publisher.publish('v0.3.1')
        head = self.git('ls-remote', 'origin', 'refs/heads/release/miilo-v0.3.1')
        Path('Formula/miilo.rb').write_text('different formula\n')
        self.git('commit', '-qam', 'different candidate')
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            publisher.publish('v0.3.1')
        self.assertEqual(self.git('ls-remote', 'origin', 'refs/heads/release/miilo-v0.3.1'), head)

    def test_older_release_cannot_downgrade_current_formula(self):
        Path('Formula/miilo.rb').write_text('url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.2/file"\n')
        self.git('commit', '-qam', 'newer version')
        self.git('push', '-q', 'origin', 'main')
        Path('Formula/miilo.rb').write_text('old candidate\n')
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            publisher.prepare('v0.3.1')

    def test_plan_and_tags_reject_ambiguous_or_unsafe_values(self):
        self.assertEqual(publisher.plan_tag({'releases':[{'app_version':'0.3.1', 'artifacts':['miilo.rb']}]}), 'v0.3.1')
        for tag in ['v01.2.3', 'v0.3.1-rc.1', 'v0.3.1\nwrite=bad', '../main']:
            with self.assertRaises(ValueError): publisher.stable_tag(tag)
        for plan in [{'releases':[]}, {'releases':[{'app_version':'0.3.1','artifacts':['../miilo.rb']}]}]:
            with self.assertRaises(ValueError): publisher.plan_tag(plan)


if __name__ == '__main__':
    unittest.main()
