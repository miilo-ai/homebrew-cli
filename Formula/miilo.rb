class Miilo < Formula
  desc "Private-by-default terminal observer for Miilo"
  homepage "https://miilo.tech"
  if OS.mac?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.1/miilo-cli-aarch64-apple-darwin.tar.xz"
      sha256 "f7015a5cdc48abdacc41754f25c69ad27039157454ed5356c380ec3447c27f67"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.1/miilo-cli-x86_64-apple-darwin.tar.xz"
      sha256 "1ed96e06bcc6e5a5e182e399c98bc9f31f1c2555278f37de9c11285fbfd37629"
    end
  end
  if OS.linux?
    if Hardware::CPU.arm?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.1/miilo-cli-aarch64-unknown-linux-gnu.tar.xz"
      sha256 "82fbd43aa873e4a2154eacce2d49cf78cd82fabad8e5d72a9ef8ce15a440cf01"
    end
    if Hardware::CPU.intel?
      url "https://github.com/miilo-ai/miilo-cli/releases/download/v0.3.1/miilo-cli-x86_64-unknown-linux-gnu.tar.xz"
      sha256 "f8af7fe92a89284607a49936928fc43fbd6fda9d07aaa09782b4a3ba1e5e73e2"
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
