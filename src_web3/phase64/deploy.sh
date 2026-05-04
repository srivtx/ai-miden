#!/bin/bash # WHY: This script installs all Node.js dependencies required for Phase 64 ZK Compression and Light Protocol demos.
set -e # WHY: Exit immediately if any command fails so partial installs do not leave the environment in a broken state.
echo "Installing Light Protocol dependencies..." # WHY: Inform the operator that the setup process has started so they know the script is running.
npm install @lightprotocol/stateless.js @lightprotocol/compressed-token # WHY: Install the Light Protocol RPC client and compressed-token SDK which provide Merkle tree instructions and ZK proof generation.
npm install @solana/web3.js @solana/spl-token # WHY: Install Solana web3.js and SPL token libraries for keypair management, public key validation, and standard token primitives.
npm install express cors dotenv # WHY: Install Express for the REST API, CORS for cross-origin requests, and dotenv for loading RPC endpoints and secret keys from .env files.
npm install -D typescript @types/node @types/express ts-node # WHY: Install TypeScript compiler and type definitions so the demo scripts and API can be written in TypeScript and executed with ts-node.
echo "Setup complete. Set RPC_ENDPOINT, PAYER_SECRET_KEY, and COMPRESSED_MINT in .env before running." # WHY: Remind the operator to configure mandatory environment variables so the scripts connect to the correct cluster and sign transactions.
