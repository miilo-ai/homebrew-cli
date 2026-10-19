# Parse formula syntax as data; never evaluate the downloaded or proposed Ruby.
require "json"
require "ripper"

source = STDIN.read
abort "Formula is too large" if source.bytesize > 131_072
# Homebrew's formatter freezes this generated hash and adds a trailing comma.
source = source.sub(/^  BINARY_ALIASES = \{.*?^  \}(?!\.freeze)/m) { |part| part + ".freeze" }
tree = Ripper.sexp(source)
abort "Invalid Ruby formula syntax" unless tree

def without_locations(node)
  return node unless node.is_a?(Array)

  if node.first.is_a?(Symbol) && node.first.to_s.start_with?("@")
    return node.first(2)
  end

  node.map { |child| without_locations(child) }
end

puts JSON.generate(without_locations(tree))
