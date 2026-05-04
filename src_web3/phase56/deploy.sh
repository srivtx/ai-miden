#!/bin/bash
# WHY: The shebang tells the operating system to execute this script with the Bash shell.

set -e
# WHY: set -e causes the script to exit immediately if any command fails, preventing partial or corrupted deployments.

echo "Building AI Miden Cross-Chain Bridge Phase 56"
# WHY: Logging the start of the build provides immediate feedback to the operator.

cd "$(dirname "$0")"
# WHY: Changing to the script's directory ensures relative paths resolve correctly regardless of where the script is invoked from.

echo "Building bridge program..."
# WHY: Announcing the current build step helps debug failures by identifying which crate failed.
cd bridge
# WHY: Enter the bridge crate directory where Cargo.toml is located.
cargo build-bpf
# WHY: build-bpf compiles the Solana program into BPF bytecode that the Solana runtime can execute.
cd ..
# WHY: Return to the parent directory so the next relative path works correctly.

echo "Building guardian program..."
# WHY: Announcing the guardian build step separates the output logs for readability.
cd guardian
# WHY: Enter the guardian crate directory.
cargo build-bpf
# WHY: build-bpf compiles the guardian registry program into deployable BPF bytecode.
cd ..
# WHY: Return to the parent directory.

echo "Deploying programs to local validator..."
# WHY: Logging deployment informs the operator that build succeeded and deployment is starting.

solana config get
# WHY: Displaying the current Solana config confirms the correct cluster (localnet, devnet, or mainnet-beta).

BRIDGE_PROGRAM_ID=$(solana program deploy target/deploy/ai_miden_bridge.so --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/')
# WHY: Deploying the bridge program and extracting the program ID allows the API to reference the deployed address.
echo "Bridge Program ID: $BRIDGE_PROGRAM_ID"
# WHY: Printing the program ID is required for updating environment variables and API configuration.

GUARDIAN_PROGRAM_ID=$(solana program deploy target/deploy/ai_miden_guardian.so --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/')
# WHY: Deploying the guardian program and extracting its ID allows the bridge program to CPI into the correct registry.
echo "Guardian Program ID: $GUARDIAN_PROGRAM_ID"
# WHY: Printing the guardian program ID completes the deployment record.

echo "Installing API dependencies..."
# WHY: The off-chain API requires Node.js modules before it can run.
npm install
# WHY: npm install fetches Express, Solana web3.js, and other dependencies specified in package.json.

echo "Starting bridge API on port 3060..."
# WHY: Announcing the API startup confirms the deployment sequence is complete.
export BRIDGE_PROGRAM_ID=$BRIDGE_PROGRAM_ID
# WHY: Setting the environment variable makes the deployed program ID available to the API process.
export GUARDIAN_PROGRAM_ID=$GUARDIAN_PROGRAM_ID
# WHY: The guardian program ID must be known to the API for guardian registration and attestation routes.
node bridge_api.ts &
# WHY: Running the API in the background allows the same terminal session to continue.
API_PID=$!
# WHY: Capturing the process ID enables clean shutdown later.

echo "Starting relayer service..."
# WHY: Announcing relayer startup informs the operator that the full stack is launching.
node relayer.ts &
# WHY: Running the relayer in the background ensures it monitors events continuously.
RELAYER_PID=$!
# WHY: Capturing the relayer PID enables process management.

echo "Deployment complete."
# WHY: A completion message signals that all components are built, deployed, and running.
echo "Bridge API PID: $API_PID"
# WHY: Logging the PID helps the operator manage or restart the service.
echo "Relayer PID: $RELAYER_PID"
# WHY: Logging the relayer PID helps with monitoring and log rotation.

wait
# WHY: wait pauses the script until background processes exit, keeping the terminal session active.
