# Miilo Homebrew tap

This repository is the official Homebrew tap for Miilo's open-source command-line
tools. Formulae are generated from signed GitHub release artifacts in the source
repository; they are not edited by hand.

```bash
brew install miilo-ai/tap/miilo
miilo doctor
```

The first `miilo` formula will appear when `miilo-ai/miilo-cli` publishes its
first stable release. Until then this repository intentionally contains no
installable formula.

## Release ownership

The `miilo-cli` release workflow builds and attests native archives, generates
`Formula/miilo.rb`, and pushes that file here with a narrowly scoped repository
token. See the CLI repository's release guide for the complete process.

Apache-2.0 covers repository automation and documentation. Miilo names and logos
remain trademarks of their respective owner.
