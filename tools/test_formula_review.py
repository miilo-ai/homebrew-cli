"""Release approval rejects changed artifacts, extra files, stale heads and forks."""
import copy
import unittest

from formula_review_policy import candidate, verify_release, REPOSITORY, SOURCE, FORMULA
from review_release_formula import review


def pull_request():
    return {'number':7, 'state':'open', 'draft':False, 'changed_files':1,
            'title':'chore: update Miilo to 0.4.0',
            'base':{'repo':{'full_name':REPOSITORY}, 'ref':'main', 'sha':'b'*40},
            'head':{'repo':{'full_name':REPOSITORY}, 'ref':'release/miilo-v0.4.0', 'sha':'a'*40}}


def release():
    return {'tag_name':'v0.4.0', 'draft':False, 'prerelease':False,
            'html_url':'https://github.com/' + SOURCE + '/releases/tag/v0.4.0'}


FILES = [{'filename':FORMULA, 'status':'modified'}]
BASE = '\n'.join('url https://example.invalid/releases/download/v0.3.1/file' for _ in range(4))


class FakeGitHub:
    def __init__(self):
        self.pull = pull_request()
        self.changed = False
        self.calls = 0
        self.approvals = []
        self.output = 'qualified formula'
        self.downloads = 0
        self.release_value = release()

    def pr(self, number):
        self.calls += 1
        value = copy.deepcopy(self.pull)
        if self.changed and self.calls > 1:
            value['head']['sha'] = 'c'*40
        return value

    def files(self, number): return copy.deepcopy(FILES)
    def release(self, tag): return self.release_value
    def content(self, sha): return BASE if sha == 'b'*40 else self.output
    def canonical(self, source): return source
    def approve(self, item): self.approvals.append(item)

    def expected(self, tag):
        self.downloads += 1
        return 'qualified formula'


class ReleaseReview(unittest.TestCase):
    def test_official_formula_is_approved_at_the_exact_commit(self):
        github = FakeGitHub()
        item = review(github, 7)
        self.assertEqual(github.approvals, [item])
        self.assertEqual(item.sha, 'a'*40)

    def test_audit_of_merged_release_has_no_write(self):
        github = FakeGitHub()
        github.pull.update(state='closed', merged_at='2026-10-19T00:00:00Z')
        review(github, 7, audit=True)
        self.assertEqual(github.approvals, [])
        with self.assertRaises(ValueError): review(github, 7)

    def test_fork_and_wrong_target_do_not_get_reviewed(self):
        for side in ('head', 'base'):
            value = pull_request()
            value[side]['repo']['full_name'] = 'outside/homebrew-cli'
            with self.assertRaises(ValueError): candidate(value, FILES)
        value = pull_request()
        value['base']['ref'] = 'unprotected'
        with self.assertRaises(ValueError): candidate(value, FILES)

    def test_draft_closed_and_extra_changes_are_rejected(self):
        for change in ({'draft':True}, {'state':'closed'}, {'changed_files':2}):
            value = pull_request()
            value.update(change)
            with self.assertRaises(ValueError): candidate(value, FILES)
        for files in ([], FILES + [{'filename':'tools/publish.py'}],
                      [{'filename':'.github/workflows/test.yml','status':'modified'}],
                      [{'filename':FORMULA,'status':'renamed','previous_filename':'evil.rb'}]):
            with self.assertRaises(ValueError): candidate(pull_request(), files)

    def test_only_stable_release_branch_title_and_sha_are_accepted(self):
        for branch in ('feature/v0.4.0', 'release/miilo-v0.4.0-rc.1',
                       'release/miilo-v00.4.0', 'release/miilo-v0.4.0\nrun=bad'):
            value = pull_request()
            value['head']['ref'] = branch
            with self.assertRaises(ValueError): candidate(value, FILES)
        for sha in ('main', '../bad', 'a'*39):
            value = pull_request()
            value['head']['sha'] = sha
            with self.assertRaises(ValueError): candidate(value, FILES)
        value = pull_request()
        value['title'] = 'Another change'
        with self.assertRaises(ValueError): candidate(value, FILES)

    def test_release_metadata_must_be_published_stable_and_canonical(self):
        item = candidate(pull_request(), FILES)
        for change in ({'draft':True}, {'prerelease':True}, {'tag_name':'v0.5.0'},
                       {'html_url':'https://example.invalid/release'}):
            value = release()
            value.update(change)
            with self.assertRaises(ValueError): verify_release(item, value, BASE, 'ok', 'ok')

    def test_same_version_downgrades_and_ambiguous_base_are_rejected(self):
        item = candidate(pull_request(), FILES)
        for base in (BASE.replace('v0.3.1', 'v0.4.0'), BASE.replace('v0.3.1', 'v1.0.0'),
                     '', BASE + '\n/releases/download/v0.1.0/'):
            with self.assertRaises(ValueError): verify_release(item, release(), base, 'ok', 'ok')

    def test_changed_ruby_or_checksum_requires_manual_review(self):
        github = FakeGitHub()
        github.output += '\nsystem("untrusted command")'
        with self.assertRaisesRegex(ValueError, 'differs'): review(github, 7)
        self.assertEqual(github.approvals, [])

    def test_head_race_does_not_approve_new_code(self):
        github = FakeGitHub()
        github.changed = True
        with self.assertRaisesRegex(ValueError, 'changed during'): review(github, 7)
        self.assertEqual(github.approvals, [])

    def test_unpublished_release_is_rejected_before_preparing_artifact(self):
        github = FakeGitHub()
        github.release_value['draft'] = True
        with self.assertRaises(ValueError): review(github, 7)
        self.assertEqual(github.downloads, 0)
        self.assertEqual(github.approvals, [])


if __name__ == '__main__':
    unittest.main()
