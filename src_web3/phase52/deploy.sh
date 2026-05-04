#!/bin/bash
# WHY: This script automates the build and deployment process so students do not miss steps.

# WHY: Exit immediately if any command fails to prevent partial or broken deployments.
set -e

# WHY: Print each command to stdout so the operator can follow the script progress.
set -x

echo "========================================"
echo "Phase 52: Lending Protocol Deployment"
echo "========================================"

# WHY: Step 1 builds the interest oracle program so it is ready for deployment.
echo "Step 1: Build interest oracle program"
cd src_web3/phase52/interest_oracle
# WHY: Compile to BPF bytecode because Solana programs must run inside the BPF virtual machine.
cargo build-bpf
# WHY: Return to the project root so subsequent relative paths are correct.
cd ../../..

# WHY: Step 2 deploys the compiled oracle program to the cluster.
echo "Step 2: Deploy interest oracle program"
solana program deploy src_web3/phase52/interest_oracle/target/deploy/phase52_interest_oracle.so

# WHY: Step 3 builds the lending program.
echo "Step 3: Build lending program"
cd src_web3/phase52/lending
# WHY: Compile to BPF bytecode for deployment to the Solana runtime.
cargo build-bpf
cd ../../..

# WHY: Step 4 deploys the compiled lending program.
echo "Step 4: Deploy lending program"
solana program deploy src_web3/phase52/lending/target/deploy/phase52_lending.so

# WHY: Step 5 reminds the operator to initialize the market via the API.
echo "Step 5: Initialize the lending market"
echo "Use the API or a client script to call InitializeMarket with your desired parameters."

# WHY: Step 6 reminds the operator to set an initial price in the oracle.
echo "Step 6: Initialize and update the oracle"
echo "Use the oracle client or API to set the initial collateral price."

# WHY: Step 7 starts the Express API so users can interact with the protocol.
echo "Step 7: Start the API"
echo "Run: npx ts-node src_web3/phase52/lending_api.ts"

# WHY: Step 8 starts the liquidator bot so underwater positions are automatically closed.
echo "Step 8: Start the liquidator bot"
echo "Run: npx ts-node src_web3/phase52/liquidator.ts"

echo "========================================"
echo "Deployment complete."
echo "========================================"
