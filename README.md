<h1 align="center">Miilo for Homebrew</h1>

<p align="center">
  <img alt="Homebrew" src="https://img.shields.io/badge/Homebrew-805522?style=flat-square&amp;logo=homebrew&amp;logoColor=white" />
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-2088ff?style=flat-square&amp;logo=githubactions&amp;logoColor=white" />
  <img alt="macOS" src="https://img.shields.io/badge/macOS-444444?style=flat-square&amp;logo=apple&amp;logoColor=white" />
  <img alt="Linux" src="https://img.shields.io/badge/Linux-343434?style=flat-square&amp;logo=linux&amp;logoColor=white" />
</p>

<p align="center">
  <a href="https://github.com/miilo-ai/homebrew-cli/actions/workflows/test.yml"><img alt="Formula tests" src="https://github.com/miilo-ai/homebrew-cli/actions/workflows/test.yml/badge.svg" /></a>
</p>

**The shortest path from a shell to Miilo.**

```bash
brew install miilo-ai/cli/miilo
miilo local discover /path/to/project
```

Each formula is generated from an attested
GitHub Release in its source repository, formatted, audited, installed on macOS and Linux,
and proposed here by release automation as a pull request. Required checks and
verification against the official release artifact precede automatic merging.
Ordinary contributions still require maintainer review. Formulae are not maintained by hand.

The `miilo` formula installs both `miilo` and `miilo-local` from the version declared in `Formula/miilo.rb`.
Published archives support Apple Silicon and Intel Macs, plus ARM64 and x64 Linux.

## How a release arrives

```text
miilo-cli tag
  → native macOS and Linux archives
  → checksums and provenance
  → generated Formula/miilo.rb
  → release/miilo-vVERSION pull request
  → required macOS/Linux installation tests and artifact verification
  → automatic merge into main
```

Report CLI or installation defects in
[`miilo-ai/miilo-cli`](https://github.com/miilo-ai/miilo-cli). See
[`CONTRIBUTING.md`](CONTRIBUTING.md) before changing tap automation.

Apache-2.0 covers this repository's documentation and automation. The license
does not grant rights to the Miilo name or marks.

The repository follows Homebrew’s `homebrew-<tap>` convention;
`miilo-ai/cli` is its standard Homebrew tap name. CLI archives include
both `miilo` and `miilo-local`. Formula publication requires qualified upstream
release assets and passing native installation checks.

## Architecture checks

The [engineering constitution](.specify/memory/constitution.md) defines the
boundaries. Run `python3 tools/check_architecture.py` and
`python3 tools/test_architecture.py`; CI qualification runs both. These are
development checks, not runtime dependencies.

Installed CLI qualification includes `tools/test-archive-install.sh`: gzip,
Brotli and zstd export/inspect/exact restore, with an existing-output refusal
check. No compression command or external codec package is required from Brew;
the native Miilo binary contains its codecs. No formula is created before a
qualified upstream release exists. Windows uses the CLI release installers,
not Homebrew.

Release scope and remaining validation: [release status](docs/release-status.md).


## Recovery and credentials

Automatic formula PR creation is owned by the CLI repository's
`publish-homebrew.yml` workflow. Its `HOMEBREW_TAP_TOKEN` must be a fine-grained
token for resource owner `miilo-ai`, selected repository `homebrew-cli`, with
Contents and Pull requests read/write permissions. It needs no branch-rule bypass
or workflow-write permission. A GitHub App with equivalent repository permissions
is a future alternative. Store the credential only in GitHub Actions secrets,
never in the formula, Git remote URL or a public issue.

After a GitHub release exists, a maintainer can rerun just the import from the CLI
repository's **Homebrew update pull request** workflow, selecting `main` and its
published stable tag. This does not rebuild binaries or replace the release.
The workflow checks branch write access before installation tests, opens or
reuses a version-specific PR, and never pushes `main` or force-updates a branch.
A successful publisher run means **auto-merge requested**, not yet **formula
available to users**. GitHub merges after required checks and the dedicated bot
review pass. Failed checks keep the PR open. There is no admin bypass.

The bot runs only trusted `main` code and reads the proposed Ruby as data. It
approves only formula-only updates in this tap that match a newer official stable
release, allowing Homebrew formatting and generated-constant freezing. Forks,
extra files, altered Ruby/checksums, drafts and stale verification are refused.
See [automation setup](docs/automatic-updates.md) for required repository settings.

This tap's **Qualify CLI release import** workflow is an independent, read-only
installation qualification tool. It accepts a stable tag and uploads qualified
formula artifacts; it does not publish or write a branch. There is one automatic
publisher, in the CLI repository.
