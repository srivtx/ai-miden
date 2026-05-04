#!/bin/bash
# This script automates the continuous integration and deployment pipeline for Solana programs

set -euo pipefail # Exit immediately on error, treat unset variables as errors, and fail pipelines if any command fails

PROGRAM_NAME="${1:-governance}" # Accept the program name as the first argument, defaulting to governance if missing
ENVIRONMENT="${2:-devnet}" # Accept the target environment as the second argument, defaulting to devnet
SOLANA_CLI="solana" # Define the Solana CLI binary name to ensure consistent command invocation
ANCHOR_CLI="anchor" # Define the Anchor CLI binary name for program building

echo "Starting deployment pipeline for $PROGRAM_NAME to $ENVIRONMENT" # Log the start so operators know which program and target are active

$SOLANA_CLI --version # Verify the Solana CLI is installed and print its version for build reproducibility
$ANCHOR_CLI --version # Verify the Anchor CLI is installed and print its version for debugging

$SOLANA_CLI config set --url $ENVIRONMENT # Switch the CLI configuration to the target cluster for all subsequent commands

CURRENT_KEYPAIR="$($SOLANA_CLI config get keypair | awk '{print $3}')" # Extract the current keypair path from Solana config for logging
echo "Using keypair: $CURRENT_KEYPAIR" # Log the keypair so operators can verify they are deploying from the correct identity

$SOLANA_CLI balance # Check the deployer balance to ensure sufficient SOL exists for rent and transaction fees

echo "Running linter and formatter..." # Inform the operator that code quality checks are beginning
cargo clippy --all-targets --all-features -- -D warnings # Run Clippy linter with strict warnings-as-errors to catch common Rust mistakes
cargo fmt --all -- --check # Verify that all Rust code follows standard formatting without modifying files

echo "Running unit tests..." # Inform the operator that local tests are starting
cargo test --lib # Execute unit tests in the library to validate internal logic without deploying

echo "Building release binary..." # Inform the operator that optimized compilation is starting
$ANCHOR_CLI build --verifiable # Build with verifiable settings so the output can be reproduced and hash-matched later

BUILD_OUTPUT="target/verifiable/${PROGRAM_NAME}.so" # Define the expected path for the compiled shared object binary
if [ ! -f "$BUILD_OUTPUT" ]; then # Check whether the build produced the expected artifact
    echo "Build failed: $BUILD_OUTPUT not found" # Log the specific failure so the operator knows what is missing
    exit 1 # Abort the pipeline because subsequent steps depend on the compiled binary
fi # Close the build artifact check

BUILD_HASH=$(sha256sum "$BUILD_OUTPUT" | awk '{print $1}')" # Compute the SHA-256 hash of the build artifact for verification
echo "Build hash: $BUILD_HASH" # Log the hash so it can be compared later against on-chain data

if [ "$ENVIRONMENT" == "devnet" ]; then # Check if the target is devnet for integration testing
    echo "Deploying to devnet for smoke tests..." # Inform the operator that devnet deployment is beginning
    $ANCHOR_CLI deploy --program-name $PROGRAM_NAME --provider.cluster devnet # Deploy the program to devnet
    sleep 5 # Wait briefly for the cluster to confirm and propagate the deployment
    echo "Running integration tests against devnet..." # Inform the operator that external tests are starting
    npm run test:integration -- --cluster devnet --program $PROGRAM_NAME # Run the integration test suite against the devnet deployment
fi # Close the devnet-specific block

if [ "$ENVIRONMENT" == "mainnet" ]; then # Check if the target is mainnet for production promotion
    echo "Promoting to mainnet..." # Inform the operator that production deployment is beginning
    read -p "Are you sure you want to deploy to mainnet? (yes/no): " CONFIRM # Require manual confirmation to prevent accidental production changes
    if [ "$CONFIRM" != "yes" ]; then # Validate that the operator explicitly typed yes
        echo "Mainnet deployment aborted" # Log the cancellation for audit trails
        exit 0 # Exit gracefully without deploying
    fi # Close the confirmation check
    $ANCHOR_CLI deploy --program-name $PROGRAM_NAME --provider.cluster mainnet # Deploy the program to mainnet
fi # Close the mainnet-specific block

echo "Deployment pipeline completed successfully" # Log successful completion so CI systems know the stage passed
