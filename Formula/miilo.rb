class Miilo < Formula
  desc "Private-by-default terminal observer for Miilo"
  homepage "https://miilo.tech"
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.5.0/miilo-cli-aarch64-apple-darwin.tar.xz"
      sha256 "b82675793d804b1150992cd305984dc9ae88005270546372864a4ae7f1af9cbe"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.5.0/miilo-cli-x86_64-apple-darwin.tar.xz"
      sha256 "f849684f50a2d459fc3f3387a298343a050bbe54dde423f0501302569be50486"
    end
  end
  if OS.linux?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.5.0/miilo-cli-aarch64-unknown-linux-gnu.tar.xz"
      sha256 "41f00c3a412d62bdf6acb88356e500deacdbe5e642010fb93a9f6056dc5f4f5a"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.5.0/miilo-cli-x86_64-unknown-linux-gnu.tar.xz"
      sha256 "d27006ff20bdcc01cc09c0703eae6156d718ab62ac63036fb6f59fc715d47b0c"
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
