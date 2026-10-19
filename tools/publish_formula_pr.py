"""Publish only a qualified formula on a review branch; never write main."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

REPO = 'miilo-ai/homebrew-cli'
FORMULA = 'Formula/miilo.rb'


def run(*args, check=True):
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError(f'{args[0]} operation failed: {result.stderr.strip()}')
    return result


def stable_tag(value):
    if not re.fullmatch(r'v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', value):
        raise ValueError('Expected a stable CLI version tag')
    return value


def plan_tag(plan):
    versions = [item['app_version'] for item in plan['releases']
                if 'miilo.rb' in item.get('artifacts', [])]
    if len(versions) != 1:
        raise ValueError('Expected exactly one Miilo formula release')
    return stable_tag('v' + versions[0])


def remote_head(branch):
    result = run('git', 'ls-remote', '--exit-code', 'origin', 'refs/heads/' + branch, check=False)
    if result.returncode == 2:
        return None
    if result.returncode:
        raise RuntimeError('Cannot inspect the tap branch; check HOMEBREW_TAP_TOKEN access')
    run('git', 'fetch', '--no-tags', 'origin', 'refs/heads/' + branch)
    return run('git', 'rev-parse', 'FETCH_HEAD').stdout.strip()


def prepare(tag):
    tag = stable_tag(tag)
    base = run('git', 'show', 'origin/main:' + FORMULA).stdout
    old_tags = re.findall(r'/releases/download/(v[0-9]+\.[0-9]+\.[0-9]+)/', base)
    if old_tags and tuple(map(int, tag[1:].split('.'))) < max(
            tuple(map(int, old[1:].split('.'))) for old in old_tags):
        raise ValueError('Refusing to downgrade the published formula')
    staged = run('git', 'diff', '--cached', '--name-only').stdout.splitlines()
    if any(path != FORMULA for path in staged):
        raise ValueError('Refusing to stage unrelated changes')
    run('git', 'switch', '-c', 'release/miilo-' + tag)
    run('git', 'add', '--', FORMULA)
    changed = bool(run('git', 'diff', '--cached', '--name-only').stdout.strip())
    if changed:
        run('git', 'commit', '-m', 'chore: update Miilo formula to ' + tag[1:])
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a') as file:
            file.write('changed=' + str(changed).lower() + '\n')
    if not changed:
        print('Formula is already current; no pull request needed.')
    return changed


def publish(tag, preflight=False):
    tag = stable_tag(tag)
    branch = 'release/miilo-' + tag
    ref = 'refs/heads/' + branch
    existing = remote_head(branch)
    if preflight:
        result = run('git', 'push', '--dry-run', 'origin', (existing or 'HEAD') + ':' + ref, check=False)
        if result.returncode:
            raise RuntimeError('Tap write preflight failed. HOMEBREW_TAP_TOKEN needs Contents and '
                               'Pull requests read/write for miilo-ai/homebrew-cli; main is never pushed.')
        print('Tap branch write preflight passed; no remote ref changed.')
        return None
    if run('git', 'status', '--porcelain', '--untracked-files=no').stdout.strip():
        raise ValueError('Refusing to publish an uncommitted formula')
    changes = run('git', 'diff', 'origin/main...HEAD', '--name-only').stdout.splitlines()
    if not changes:
        print('Formula is already current; no pull request needed.')
        return None
    if changes != [FORMULA]:
        raise ValueError('Refusing to publish changes outside Formula/miilo.rb')
    if existing:
        previous = run('git', 'show', existing + ':' + FORMULA).stdout
        if previous != Path(FORMULA).read_text():
            raise ValueError('Existing release branch differs; refusing to overwrite it')
        changed = run('git', 'diff', 'origin/main...' + existing, '--name-only').stdout.splitlines()
        if changed != [FORMULA]:
            raise ValueError('Existing release branch contains unrelated changes')
    else:
        run('git', 'push', '--set-upstream', 'origin', 'HEAD:' + ref)
    prs = json.loads(run('gh', 'pr', 'list', '--repo', REPO, '--head', branch,
                         '--base', 'main', '--state', 'all', '--json', 'url,state,headRepository').stdout)
    prs = [pr for pr in prs if (pr.get('headRepository') or {}).get('nameWithOwner') == REPO]
    opened = [pr for pr in prs if pr['state'] == 'OPEN']
    if opened:
        url = opened[0]['url']
    elif prs:
        raise ValueError('Release PR is already closed; inspect it before retrying')
    else:
        body = (f'Update the generated Miilo formula from the official [{tag} release]'
                f'(https://github.com/miilo-ai/miilo-cli/releases/tag/{tag}).\n\n'
                'The formula must pass the tap\'s required macOS/Linux installation checks '
                'and maintainer review before merging. No branch protection is bypassed.\n')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md') as file:
            file.write(body)
            file.flush()
            url = run('gh', 'pr', 'create', '--repo', REPO, '--base', 'main', '--head', branch,
                      '--title', 'chore: update Miilo to ' + tag[1:], '--body-file', file.name).stdout.strip()
    print('Formula update PR: ' + url)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as file:
            file.write(f'Homebrew update awaits review: {url}\n')
    return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag')
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--print-tag', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    tag = plan_tag(json.loads(os.environ['PLAN'])) if args.plan else stable_tag(args.tag or '')
    if args.print_tag:
        print(tag)
    elif args.prepare:
        prepare(tag)
    else:
        publish(tag, args.preflight)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(str(error)) from None
