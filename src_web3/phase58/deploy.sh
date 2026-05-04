#!/bin/bash # WHY: The shebang tells the operating system to execute this script with the Bash shell.

set -e # WHY: set -e causes the script to exit immediately if any command fails, preventing partial or corrupted deployments.

echo "Building AI Miden Token Launchpad Phase 58" # WHY: Logging the start of the build provides immediate feedback to the operator.

cd "$(dirname "$0")" # WHY: Changing to the script's directory ensures relative paths resolve correctly regardless of where the script is invoked from.

echo "Building launchpad program..." # WHY: Announcing the current build step helps debug failures by identifying which crate failed.
cd launchpad # WHY: Enter the launchpad crate directory where Cargo.toml is located.
cargo build-bpf # WHY: build-bpf compiles the Solana program into BPF bytecode that the Solana runtime can execute.
cd .. # WHY: Return to the parent directory so the next relative path works correctly.

echo "Building vesting program..." # WHY: Announcing the vesting build step separates the output logs for readability.
cd vesting # WHY: Enter the vesting crate directory where Cargo.toml is located.
cargo build-bpf # WHY: build-bpf compiles the vesting program into deployable BPF bytecode for on-chain execution.
cd .. # WHY: Return to the parent directory.

echo "Deploying programs to devnet..." # WHY: Logging deployment informs the operator that build succeeded and deployment is starting.

solana config get # WHY: Displaying the current Solana config confirms the correct cluster and keypair before deploying.

LAUNCHPAD_PROGRAM_ID=$(solana program deploy target/deploy/ai_miden_launchpad.so --url devnet --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/') # WHY: Deploying the launchpad program to devnet and extracting the program ID allows the API to reference the deployed address.

echo "Launchpad Program ID: $LAUNCHPAD_PROGRAM_ID" # WHY: Printing the program ID is required for updating environment variables and API configuration.

VESTING_PROGRAM_ID=$(solana program deploy target/deploy/ai_miden_vesting.so --url devnet --output json | grep '"programId"' | sed 's/.*: "\(.*\)".*/\1/') # WHY: Deploying the vesting program to devnet and extracting its ID allows the launchpad program to CPI into the vesting contract for token distribution.

echo "Vesting Program ID: $VESTING_PROGRAM_ID" # WHY: Printing the vesting program ID completes the deployment record and enables client configuration.

echo "Installing API dependencies..." # WHY: The off-chain API requires Node.js modules before it can run.

npm install # WHY: npm install fetches Express, Solana web3.js, and other dependencies specified in package.json.

echo "Starting launchpad API on port 3062..." # WHY: Announcing the API startup confirms the deployment sequence is complete.

export LAUNCHPAD_PROGRAM_ID=$LAUNCHPAD_PROGRAM_ID # WHY: Setting the environment variable makes the deployed program ID available to the API process for client initialization.

export VESTING_PROGRAM_ID=$VESTING_PROGRAM_ID # WHY: The vesting program ID must be known to the API for vesting schedule creation and token claim routes.

npx ts-node launchpad_api.ts & # WHY: Running the API in the background allows the same terminal session to continue and receive logs from both programs.

API_PID=$! # WHY: Capturing the process ID enables clean shutdown later if the operator needs to restart the service.

echo "Deployment complete." # WHY: A completion message signals that all components are built, deployed, and running.

echo "Launchpad API PID: $API_PID" # WHY: Logging the PID helps the operator manage or restart the service.

echo "Launchpad Program: $LAUNCHPAD_PROGRAM_ID" # WHY: Repeating the program ID at the end ensures it is visible even when the operator scrolls back through logs.

echo "Vesting Program: $VESTING_PROGRAM_ID" # WHY: Repeating the vesting program ID ensures it is captured in the final summary for client setup.

echo "Cluster: devnet" # WHY: Confirming the cluster prevents confusion between localnet, devnet, and mainnet-beta deployments.

wait # WHY: wait pauses the script until background processes exit, keeping the terminal session active.
