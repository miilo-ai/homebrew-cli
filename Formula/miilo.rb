class Miilo < Formula
  desc "Private-by-default terminal observer for Miilo"
  homepage "https://miilo.tech"
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.0/miilo-cli-aarch64-apple-darwin.tar.xz"
      sha256 "ea07f293bfdf97cc39cc728221e0727b3aba0ad3cf5209a277ad33003008b3f4"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.0/miilo-cli-x86_64-apple-darwin.tar.xz"
      sha256 "b363d359686a3b28dc7f564172e61fe235601ff4aee6197e9f5dee33b84d40b0"
    end
  end
  if OS.linux?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.0/miilo-cli-aarch64-unknown-linux-gnu.tar.xz"
      sha256 "6fef7130821d71ce0356646788a51dcce5ffd9500b1f8b6b6274087a08e67350"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.0/miilo-cli-x86_64-unknown-linux-gnu.tar.xz"
      sha256 "a6f02bd3d59431ed440f9e43e69816fb0c4079a6a736e2ce83b985279a1dbaa9"
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
