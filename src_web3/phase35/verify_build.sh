#!/bin/bash
# This script verifies that a deployed Solana program matches a given source code build artifact

set -euo pipefail # Exit immediately on error, treat unset variables as errors, and fail pipelines if any command fails

PROGRAM_ID="${1:-}" # Accept the on-chain program address as the first required argument
BUILD_PATH="${2:-target/verifiable/}" # Accept the local build directory as the second argument with a default path

if [ -z "$PROGRAM_ID" ]; then # Check if the program id argument was provided
    echo "Usage: $0 <PROGRAM_ID> [BUILD_PATH]" # Print usage instructions so the operator knows the required parameters
    exit 1 # Abort because verification cannot proceed without knowing which on-chain program to inspect
fi # Close the program id check

SOLANA_CLI="solana" # Define the Solana CLI binary name for consistent invocation
CLUSTER="${3:-mainnet}" # Accept the cluster as the third argument, defaulting to mainnet for verification

$SOLANA_CLI config set --url $CLUSTER # Switch the CLI to the target cluster for fetching on-chain data

echo "Fetching on-chain program data for $PROGRAM_ID..." # Inform the operator that chain data retrieval is starting
ON_CHAIN_DATA=$(mktemp) # Create a temporary file to store the fetched binary without cluttering the workspace
$SOLANA_CLI program dump "$PROGRAM_ID" "$ON_CHAIN_DATA" # Download the deployed program bytecode to the temporary file

ON_CHAIN_HASH=$(sha256sum "$ON_CHAIN_DATA" | awk '{print $1}')" # Compute the SHA-256 hash of the on-chain binary
echo "On-chain hash: $ON_CHAIN_HASH" # Log the on-chain hash for manual comparison and audit trails

LOCAL_SO=$(find "$BUILD_PATH" -name "*.so" | head -n 1) # Search the build directory for the first compiled shared object
if [ -z "$LOCAL_SO" ] || [ ! -f "$LOCAL_SO" ]; then # Check whether a local binary was found at the expected path
    echo "No local .so file found in $BUILD_PATH" # Log the missing artifact so the operator knows to build first
    rm -f "$ON_CHAIN_DATA" # Clean up the temporary file before exiting
    exit 1 # Abort because there is nothing to compare against the on-chain data
fi # Close the local artifact check

LOCAL_HASH=$(sha256sum "$LOCAL_SO" | awk '{print $1}')" # Compute the SHA-256 hash of the local build artifact
echo "Local build hash: $LOCAL_HASH" # Log the local hash for comparison

if [ "$ON_CHAIN_HASH" == "$LOCAL_HASH" ]; then # Compare the two hashes to determine if they match exactly
    echo "VERIFICATION PASSED: On-chain program matches local build" # Report success because the deployment is authentic
    echo "Program: $PROGRAM_ID" # Echo the program id for the verification record
    echo "Cluster: $CLUSTER" # Echo the cluster for the verification record
    echo "Build artifact: $LOCAL_SO" # Echo the local path for the verification record
    echo "Hash: $LOCAL_HASH" # Echo the matching hash for the verification record
else # If the hashes do not match
    echo "VERIFICATION FAILED: Hash mismatch detected" # Report failure because the deployment may not match the source
    echo "On-chain hash: $ON_CHAIN_HASH" # Display the on-chain hash to help diagnose the discrepancy
    echo "Local hash:    $LOCAL_HASH" # Display the local hash to help diagnose the discrepancy
    echo "Possible causes: uncommitted changes, different toolchain, or modified deployment" # Suggest common reasons for mismatch
    rm -f "$ON_CHAIN_DATA" # Clean up the temporary file before exiting
    exit 1 # Abort with failure status so CI pipelines can reject the build
fi # Close the hash comparison

rm -f "$ON_CHAIN_DATA" # Remove the temporary on-chain data file to keep the workspace clean
echo "Verification complete" # Log completion so operators and automation know the script finished
