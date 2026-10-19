class Miilo < Formula
  desc "Private-by-default terminal observer for Miilo"
  homepage "https://miilo.tech"
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.4.0/miilo-cli-aarch64-apple-darwin.tar.xz"
      sha256 "2f68af314583dc0e290e0f45c073fd3c78752c361ffebd57ada47d316a708744"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.4.0/miilo-cli-x86_64-apple-darwin.tar.xz"
      sha256 "60898dd2a3e6e2335aede4df2cdd7553fbaf90e3a9f9592697dc6cf0d983e288"
    end
  end
  if OS.linux?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.4.0/miilo-cli-aarch64-unknown-linux-gnu.tar.xz"
      sha256 "248709e9aa65d4557c83c07b1d63941486b31586214c2d7364203edb505f8dbd"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.4.0/miilo-cli-x86_64-unknown-linux-gnu.tar.xz"
      sha256 "7629b345da31f4aad8b75d3e04c237b0a60006323a78bf03ee882cb6f7b7cbb6"
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
