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
and committed here by release automation. Formulae are not maintained by hand.

The `miilo` formula installs both `miilo` and `miilo-local` from CLI 0.2.2.
Published archives support Apple Silicon and Intel Macs, plus ARM64 and x64 Linux.

## How a release arrives

```text
miilo-cli tag
  → native macOS and Linux archives
  → checksums and provenance
  → generated Formula/miilo.rb
  → audit and installation test in this repository
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
