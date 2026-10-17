# Artifact dependency gate

No formula or checksum is invented. CLI cargo-dist plan includes both binaries;
its tap publication gate checks the installed miilo-local version as well as
miilo. AUR recipes install the same compatibility executable. Actual Homebrew
audit/install/test/removal awaits owner-approved upstream artifacts and a tap
credential/public source. Windows uses native CLI release installers, not Homebrew.
