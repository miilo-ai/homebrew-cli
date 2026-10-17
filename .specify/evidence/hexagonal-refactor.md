# Architecture boundary checkpoint

Domain/application code depends on explicit ports; executable/runtime adapters
compose concrete infrastructure. `.specify/architecture.json` and its CI workflow
check inward dependencies and module sizes. Negative tests prove reversed imports
and silent size growth are rejected. Empty layer matches fail instead of passing.

Behavioral tests and native consumer qualification remain separate from these
lexical source checks. This checkpoint does not certify release, native UI, hosted
identity or every uninspected file. No release has been made.

## Implemented boundary

The repository remains packaging-only. Architecture CI rejects application source/crates/packages here. No observation logic or runtime was added.
