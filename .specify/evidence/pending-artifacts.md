# Formula artifact requirements

The tap contains an installable formula for published CLI artifacts. Formula
changes must use the actual release version, artifact URLs and checksums, and
pass macOS/Linux install tests through a reviewed PR. The protected branch rejects
direct publishing pushes. See docs/release-status.md for this remaining automation gap.

Homebrew is not the Windows installation path; use CLI release assets there.
