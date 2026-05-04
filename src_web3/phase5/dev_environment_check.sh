#!/usr/bin/env bash
# PHASE 5: Development Environment Check
# This script verifies that every required tool for Solana development is installed.

set -euo pipefail
# Exit immediately on error, undefined variables are errors, and pipe failures propagate.
# These flags make the script robust so partial failures do not go unnoticed.

REQUIRED_SOLANA_VERSION="1.18"
# We target the 1.18 branch because it is a stable LTS release used by most production programs.

REQUIRED_RUST_VERSION="1.75"
# Rust 1.75 or newer is needed for modern language features used by Anchor and Solana crates.

echo "=== Solana Development Environment Check ==="
# Print a header so the user knows which phase this script belongs to.

# Check if the Solana CLI is installed by attempting to resolve its binary path.
if command -v solana &> /dev/null; then
    SOLANA_VERSION=$(solana --version | awk '{print $2}')
    # Extract the version string so we can compare it against the required minimum.
    echo "[OK] Solana CLI found: version $SOLANA_VERSION"
    # Verify the version meets our minimum requirement using simple string comparison.
    if [[ "$SOLANA_VERSION" < "$REQUIRED_SOLANA_VERSION" ]]; then
        echo "[WARN] Solana version $SOLANA_VERSION is older than required $REQUIRED_SOLANA_VERSION"
    fi
else
    echo "[MISSING] Solana CLI not found. Install from https://docs.solana.com/cli/install"
    # Provide a direct URL so the user knows exactly how to fix the missing tool.
fi

# Check if Rust is installed by resolving rustc.
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version | awk '{print $2}')
    # Capture the compiler version to ensure compatibility with Solana BPF targets.
    echo "[OK] Rust found: version $RUST_VERSION"
    if [[ "$RUST_VERSION" < "$REQUIRED_RUST_VERSION" ]]; then
        echo "[WARN] Rust version $RUST_VERSION is older than required $REQUIRED_RUST_VERSION"
    fi
else
    echo "[MISSING] Rust not found. Install from https://rustup.rs"
fi

# Check if Cargo is installed because it manages Rust dependencies and builds.
if command -v cargo &> /dev/null; then
    CARGO_VERSION=$(cargo --version | awk '{print $2}')
    echo "[OK] Cargo found: version $CARGO_VERSION"
else
    echo "[MISSING] Cargo not found. Install Rust via rustup to receive Cargo automatically."
fi

# Check for Node.js because TypeScript client code depends on it.
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "[OK] Node.js found: version $NODE_VERSION"
else
    echo "[MISSING] Node.js not found. Install from https://nodejs.org"
fi

# Check for npm or yarn because client dependencies are managed through these tools.
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "[OK] npm found: version $NPM_VERSION"
else
    echo "[MISSING] npm not found. It installs with Node.js by default."
fi

# Check for the Solana BPF target needed to compile on-chain programs.
if rustup target list --installed | grep -q "bpf"; then
    echo "[OK] Solana BPF target installed"
else
    echo "[MISSING] Solana BPF target not installed. Run: rustup target add bpfel-unknown-unknown"
    # Print the exact command so the user can copy-paste to fix the issue.
fi

# Verify that the default Solana config points to a known cluster.
if [ -f "$HOME/.config/solana/cli/config.yml" ]; then
    DEFAULT_CLUSTER=$(solana config get | grep "RPC URL" | awk '{print $3}')
    echo "[OK] Solana config found. Default cluster: $DEFAULT_CLUSTER"
    # Warn if mainnet is selected so developers do not accidentally spend real funds.
    if [[ "$DEFAULT_CLUSTER" == *"mainnet"* ]]; then
        echo "[WARN] Default cluster is mainnet. Switch to devnet for development with: solana config set --url devnet"
    fi
else
    echo "[INFO] No Solana config found. Run 'solana config set --url devnet' to initialize."
fi

# Check for a default keypair, which is needed to sign test transactions.
if [ -f "$HOME/.config/solana/id.json" ]; then
    echo "[OK] Default keypair found at ~/.config/solana/id.json"
else
    echo "[INFO] No default keypair. Generate one with: solana-keygen new"
fi

echo "=== Environment Check Complete ==="
# Print a footer so the user knows the script finished and can review any warnings.
