# =============================================================================
# Homebrew Formula for JPAPI
# =============================================================================
# Usage: brew install fanduel/jpapi/jpapi
# =============================================================================

class Jpapi < Formula
  desc "JAMF Pro API Toolkit - Enterprise-grade CLI for JAMF Pro management"
  homepage "https://github.com/fanduel/jpapi"
  url "https://github.com/fanduel/jpapi/archive/refs/heads/main.zip"
  sha256 "" # Will be updated on release
  license "MIT"
  head "https://github.com/fanduel/jpapi.git", branch: "main"

  depends_on "python@3.11"
  depends_on "jq"

  def install
    # Create virtual environment
    venv = virtualenv_create(libexec, "python3.11")
    
    # Install dependencies
    system libexec/"bin/pip", "install", "-e", "."
    
    # Create symlinks
    bin.install_symlink libexec/"bin/jpapi"
  end

  test do
    # Test basic functionality
    system "#{bin}/jpapi", "--version"
  end
end
