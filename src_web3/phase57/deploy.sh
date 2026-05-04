#!/bin/bash
# WHY: This script automates building and deploying both Solana programs so students do not have to run multiple commands manually.

set -e # WHY: Exit immediately if any command fails so we do not deploy a partially built or broken program.

# WHY: Define the project root relative to the script location so it works regardless of where the user invokes it.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# WHY: Define the Anchor workspace or program directories so the build commands know where to look.
MARKET_DIR="$ROOT_DIR/market"
ORACLE_DIR="$ROOT_DIR/oracle"

# WHY: Define the target deployment cluster; default to localnet for safe development and testing.
CLUSTER="${1:-localnet}"

echo "=== Building Oracle Program ===" # WHY: Inform the user which step is running.
cd "$ORACLE_DIR" # WHY: Change to the oracle program directory so Cargo and Anchor resolve the correct dependencies.

# WHY: Build the oracle program as a BPF shared object for Solana deployment.
cargo build-bpf --manifest-path "$ORACLE_DIR/Cargo.toml" # WHY: build-bpf compiles Rust to Solana's Berkeley Packet Filter bytecode, which is the on-chain execution format.

# WHY: Deploy the oracle program to the selected cluster and capture the program ID.
ORACLE_PROGRAM_ID=$(solana program deploy "$ORACLE_DIR/target/deploy/oracle_resolution.so" --url "$CLUSTER" --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/')
echo "Oracle Program ID: $ORACLE_PROGRAM_ID" # WHY: Print the deployed program ID so the user can update their client code and IDL.

echo "=== Building Market Program ===" # WHY: Inform the user which step is running.
cd "$MARKET_DIR" # WHY: Change to the market program directory.

# WHY: Build the market program as a BPF shared object.
cargo build-bpf --manifest-path "$MARKET_DIR/Cargo.toml" # WHY: Same reason as the oracle build: compile Rust to Solana BPF bytecode.

# WHY: Deploy the market program to the selected cluster and capture the program ID.
MARKET_PROGRAM_ID=$(solana program deploy "$MARKET_DIR/target/deploy/prediction_market.so" --url "$CLUSTER" --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/')
echo "Market Program ID: $MARKET_PROGRAM_ID" # WHY: Print the deployed program ID for client configuration.

echo "=== Generating IDLs ===" # WHY: Inform the user which step is running.

# WHY: Generate the Anchor IDL for the oracle program so TypeScript clients can interact with it.
anchor idl init --filepath "$ORACLE_DIR/target/idl/oracle_resolution.json" "$ORACLE_PROGRAM_ID" --provider.cluster "$CLUSTER" || true # WHY: Use || true because IDL init fails if it already exists; we ignore the error for redeploys.
anchor idl upgrade --filepath "$ORACLE_DIR/target/idl/oracle_resolution.json" "$ORACLE_PROGRAM_ID" --provider.cluster "$CLUSTER" || true # WHY: Upgrade the IDL if it already exists so the on-chain metadata matches the latest build.

# WHY: Generate the Anchor IDL for the market program so TypeScript clients can interact with it.
anchor idl init --filepath "$MARKET_DIR/target/idl/prediction_market.json" "$MARKET_PROGRAM_ID" --provider.cluster "$CLUSTER" || true
anchor idl upgrade --filepath "$MARKET_DIR/target/idl/prediction_market.json" "$MARKET_PROGRAM_ID" --provider.cluster "$CLUSTER" || true

echo "=== Deployment Complete ===" # WHY: Inform the user that all steps finished successfully.
echo "Market Program: $MARKET_PROGRAM_ID"
echo "Oracle Program: $ORACLE_PROGRAM_ID"
echo "Cluster: $CLUSTER"

# WHY: Write the deployed program IDs to a local JSON file so the API server can read them at runtime.
cat > "$ROOT_DIR/program_ids.json" <<EOF
{
  "marketProgramId": "$MARKET_PROGRAM_ID",
  "oracleProgramId": "$ORACLE_PROGRAM_ID",
  "cluster": "$CLUSTER"
}
EOF
