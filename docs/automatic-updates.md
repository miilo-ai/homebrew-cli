# Automatic formula updates

The CLI publisher prepares the official release formula, exercises installation,
opens or reuses `release/miilo-vVERSION`, and requests squash auto-merge bound to
the exact head commit. GitHub still requires the tap's existing status checks
and approving review. No workflow pushes `main` or uses an administrator bypass.

A separate GitHub Actions identity supplies the review. It accepts only a
non-draft PR within `miilo-ai/homebrew-cli`, targeting `main`, modifying exactly
`Formula/miilo.rb`, for a strictly newer published stable CLI release. It compares
the formula's Ruby syntax with the prepared official release asset. Whitespace,
comments, trailing commas and Homebrew's generated-hash freezing are harmless
formatting differences; changed code, strings and checksums are rejected.
Ruby is parsed with Ripper, never evaluated. The workflow checks out only trusted
`main` code and rechecks the head and base before approving that exact commit.

Other contributions still need a maintainer's review. A failing test or refused
artifact review leaves the release PR open rather than silently publishing.

## One-time repository configuration

In `miilo-ai/homebrew-cli`:

- Enable **Allow auto-merge**.
- Under Actions workflow permissions, retain **Read repository contents and
  packages permissions** and enable **Allow GitHub Actions to create and approve
  pull requests**. Only the dedicated reviewer requests Pull requests write.
- Retain required macOS/Linux installation tests, architecture/history checks,
  approving review, stale-review dismissal and branch-update requirements.
- Do not exempt release branches from tests or use an admin bypass in automation.

The CLI's existing `HOMEBREW_TAP_TOKEN` creates the release PR and requests its
merge. Its identity must differ from `github-actions[bot]`, which supplies the
review. The token remains limited to tap Contents and Pull requests read/write.
If GitHub App publishing replaces that token later, use a distinct reviewer
identity. A bot cannot approve its own PR. Adding CODEOWNERS later may also add
an approval requirement; this workflow does not override it.

## Recovery and evidence

The CLI's Homebrew workflow can retry an existing published stable tag without
rebuilding binaries or moving tags. A matching PR is reused and auto-merge is
requested again. Permission failures are reported instead of ignored.

**Review official release formula** also has a manual read-only audit mode. Give
it a PR number to qualify the published artifact without submitting a review.
The local equivalent is `python3 tools/review_release_formula.py NUMBER --audit`.
This can inspect a historical merged release. It is verification evidence, not
proof that a future PR has automatically merged.
