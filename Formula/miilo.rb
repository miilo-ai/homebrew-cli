class Miilo < Formula
  desc "Private-by-default terminal observer for Miilo"
  homepage "https://miilo.tech"
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.2.2/miilo-cli-aarch64-apple-darwin.tar.xz"
      sha256 "ea2a04b626210a3829d4caa197a11f2b6dff591eb050012cc1d169c74d2047b3"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.2.2/miilo-cli-x86_64-apple-darwin.tar.xz"
      sha256 "5d7d81b98bcca10694c1ba29cec84a6cd5ec19ec98426442a76c702dab04f4cc"
    end
  end
  if OS.linux?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.2.2/miilo-cli-aarch64-unknown-linux-gnu.tar.xz"
      sha256 "6d33e7700e86d87b12c666b775b068cf759340d6047e9e032fa6725c458a61e2"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.2.2/miilo-cli-x86_64-unknown-linux-gnu.tar.xz"
      sha256 "acb3f519e9292c0abb0f01de1062626516d16c816fd6a98d220143bdb7190384"
    end
  end
  license "Apache-2.0"

  BINARY_ALIASES = {
    "aarch64-apple-darwin":      {},
    "aarch64-unknown-linux-gnu": {},
    "x86_64-apple-darwin":       {},
    "x86_64-pc-windows-gnu":     {},
    "x86_64-unknown-linux-gnu":  {},
  }.freeze

  def target_triple
    cpu = Hardware::CPU.arm? ? "aarch64" : "x86_64"
    os = OS.mac? ? "apple-darwin" : "unknown-linux-gnu"

    "#{cpu}-#{os}"
  end

  def install_binary_aliases!
    BINARY_ALIASES[target_triple.to_sym].each do |source, dests|
      dests.each do |dest|
        bin.install_symlink bin/source.to_s => dest
      end
    end
  end

  def install
    if OS.mac? && Hardware::CPU.arm?
      bin.install "miilo", "miilo-local"
    end
    if OS.mac? && Hardware::CPU.intel?
      bin.install "miilo", "miilo-local"
    end
    if OS.linux? && Hardware::CPU.arm?
      bin.install "miilo", "miilo-local"
    end
    if OS.linux? && Hardware::CPU.intel?
      bin.install "miilo", "miilo-local"
    end

    install_binary_aliases!

    # Homebrew will automatically install these, so we don't need to do that
    doc_files = Dir["README.*", "readme.*", "LICENSE", "LICENSE.*", "CHANGELOG.*"]
    leftover_contents = Dir["*"] - doc_files

    # Install any leftover files in pkgshare; these are probably config or
    # sample files.
    pkgshare.install(*leftover_contents) unless leftover_contents.empty?
  end
  test do
    assert_match version.to_s, shell_output("#{bin}/miilo --version")
    assert_match version.to_s, shell_output("#{bin}/miilo-local --version")
  end
end
