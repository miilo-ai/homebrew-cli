"""Decide whether an official, formula-only release update may receive bot review."""
from dataclasses import dataclass
import re

REPOSITORY = 'miilo-ai/homebrew-cli'
SOURCE = 'miilo-ai/miilo-cli'
FORMULA = 'Formula/miilo.rb'
STABLE = r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'


@dataclass(frozen=True)
class Candidate:
    number: int
    sha: str
    tag: str


def candidate(pr, files, audit=False):
    if pr.get('state') != 'open' and not (audit and pr.get('merged_at')):
        raise ValueError('Only open release PRs can receive automated review')
    if pr.get('draft') or pr.get('changed_files') != 1:
        raise ValueError('Expected a non-draft, formula-only update')
    for side in ('base', 'head'):
        if pr.get(side, {}).get('repo', {}).get('full_name') != REPOSITORY:
            raise ValueError('Fork and cross-repository PRs require maintainer review')
    if pr['base']['ref'] != 'main':
        raise ValueError('Expected the protected main target')
    branch = pr['head']['ref']
    match = re.fullmatch('release/miilo-(' + STABLE + ')', branch)
    if not match:
        raise ValueError('Not an automated stable release branch')
    sha = pr['head']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Invalid head commit')
    if len(files) != 1 or files[0].get('filename') != FORMULA or files[0].get('status') != 'modified':
        raise ValueError('Only modification of Formula/miilo.rb is permitted')
    if files[0].get('previous_filename'):
        raise ValueError('Renamed files require maintainer review')
    tag = match.group(1)
    if pr.get('title') != 'chore: update Miilo to ' + tag[1:]:
        raise ValueError('Unexpected release PR title')
    return Candidate(pr['number'], sha, tag)


def published_release(item, release):
    if release.get('draft') or release.get('prerelease') or release.get('tag_name') != item.tag:
        raise ValueError('Expected the published stable CLI release')
    canonical = 'https://github.com/' + SOURCE + '/releases/tag/' + item.tag
    if release.get('html_url') != canonical:
        raise ValueError('Unexpected release origin')


def verify_release(item, release, base, expected, proposed):
    published_release(item, release)
    versions = re.findall(r'/releases/download/(v\d+\.\d+\.\d+)/', base)
    if len(versions) != 4 or len(set(versions)) != 1:
        raise ValueError('Cannot establish the current published formula version')
    version = lambda tag: tuple(map(int, tag[1:].split('.')))
    if version(item.tag) <= version(versions[0]):
        raise ValueError('Refusing a downgrade or same-version replacement')
    if not expected or proposed != expected:
        raise ValueError('Formula differs from the prepared official release artifact')
    return item
