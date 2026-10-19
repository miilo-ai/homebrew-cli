"""Inspect PR data through GitHub; never check out or execute PR code."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

from formula_review_policy import FORMULA, REPOSITORY, SOURCE, candidate, published_release, verify_release
from prepare_formula import prepare


class GitHub:
    def run(self, *args):
        result = subprocess.run(args, text=True, capture_output=True, timeout=120, check=False)
        if result.returncode:
            raise RuntimeError('GitHub/qualification operation failed: ' + result.stderr.strip())
        return result.stdout

    def api(self, path, *args):
        return json.loads(self.run('gh', 'api', path, *args))

    def pr(self, number):
        return self.api(f'repos/{REPOSITORY}/pulls/{number}')

    def files(self, number):
        return self.api(f'repos/{REPOSITORY}/pulls/{number}/files?per_page=2')

    def content(self, sha):
        value = self.api(f'repos/{REPOSITORY}/contents/{FORMULA}?ref={sha}')
        if value.get('type') != 'file' or value.get('encoding') != 'base64' or value['size'] > 131072:
            raise ValueError('Unexpected formula content')
        return base64.b64decode(value['content'], validate=False).decode('utf8')

    def release(self, tag):
        return self.api(f'repos/{SOURCE}/releases/tags/{tag}')

    def expected(self, tag):
        with tempfile.TemporaryDirectory() as temporary:
            self.run('gh', 'release', 'download', tag, '--repo', SOURCE,
                     '--pattern', 'miilo.rb', '--dir', temporary)
            path = Path(temporary)/'miilo.rb'
            if path.stat().st_size > 131072:
                raise ValueError('Official formula is too large')
            path.write_text(prepare(path.read_text(), tag))
            return path.read_text()

    def canonical(self, source):
        parser = Path(__file__).with_name('formula_syntax.rb')
        result = subprocess.run(['ruby', str(parser)], input=source, text=True,
                                capture_output=True, timeout=15, check=False)
        if result.returncode:
            raise ValueError('Formula syntax validation failed')
        return result.stdout.strip()

    def approve(self, item):
        self.api(f'repos/{REPOSITORY}/pulls/{item.number}/reviews', '--method', 'POST',
                 '-f', 'event=APPROVE', '-f', 'commit_id=' + item.sha,
                 '-f', 'body=Verified formula-only update against the prepared official '
                 + item.tag + ' release artifact. Required CI checks remain enforced by GitHub.')


def review(github, number, audit=False):
    pr = github.pr(number)
    item = candidate(pr, github.files(number), audit)
    release = github.release(item.tag)
    published_release(item, release)
    expected = github.expected(item.tag)
    verify_release(item, release, github.content(pr['base']['sha']),
                   github.canonical(expected), github.canonical(github.content(item.sha)))
    current = github.pr(number)
    if current['head']['sha'] != item.sha or current['base']['sha'] != pr['base']['sha']:
        raise ValueError('PR changed during verification; wait for a fresh review')
    candidate(current, github.files(number), audit)
    if not audit:
        github.approve(item)
    print(('Audited' if audit else 'Approved') + f' formula-only {item.tag} at {item.sha}')
    return item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int)
    parser.add_argument('--audit', action='store_true', help='Read-only qualification, including a merged PR')
    args = parser.parse_args()
    if args.number < 1:
        raise ValueError('Expected a positive PR number')
    if os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') != REPOSITORY:
        raise ValueError('Automated review is restricted to the canonical tap')
    review(GitHub(), args.number, args.audit)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        raise SystemExit(str(error)) from None
