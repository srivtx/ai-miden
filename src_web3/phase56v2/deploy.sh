#!/bin/bash
# WHY: Specify bash shell for consistent script execution across environments.
set -e
# WHY: Exit immediately if any command fails to prevent partial deployments.
cd "$(dirname "$0")/bridge"
# WHY: Navigate to the bridge program directory where Anchor.toml is located.
anchor build
# WHY: Compile both bridge and guardian programs into BPF bytecode.
anchor deploy
# WHY: Deploy compiled programs to the configured Solana cluster.
echo "Deployment complete"
# WHY: Print confirmation so CI logs or manual runs show success.
