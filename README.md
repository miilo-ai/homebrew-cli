# Miilo for Homebrew

**The shortest path from a shell to Miilo.**

[![Formula tests](https://github.com/miilo-ai/homebrew-tap/actions/workflows/test.yml/badge.svg)](https://github.com/miilo-ai/homebrew-tap/actions/workflows/test.yml)

```bash
brew install miilo-ai/tap/miilo
miilo doctor
```

This tap is intentionally boring. Every formula is generated from an attested
GitHub Release in its source repository, formatted, audited, installed on macOS,
and committed here by release automation. Formulae are not maintained by hand.

The first `miilo` formula appears when `miilo-ai/miilo-cli` publishes its first
stable release. Until then there is nothing fake to install.

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
