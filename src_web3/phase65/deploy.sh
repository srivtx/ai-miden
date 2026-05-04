#!/bin/bash
# WHY: This script automates environment setup so students do not manually hunt for dependencies.
set -e
# WHY: Exit immediately if any command fails to prevent partial or broken installations.
echo "Setting up Drift Protocol Phase 65 environment..."
# WHY: Provide user feedback so the operator knows the script has started.
cd "$(dirname "$0")"
# WHY: Ensure subsequent commands run relative to this script's directory, not the caller's CWD.
if [ ! -f "../../package.json" ]; then
# WHY: Check whether a package.json exists two levels up to decide if we are in a Node project.
  echo "Initializing Node project..."
# WHY: Inform the user that a new Node project is being created because none was found.
  npm init -y
# WHY: Generate a default package.json so npm can install dependencies into this folder.
fi
# WHY: Close the conditional block after handling the missing package.json case.
echo "Installing Drift SDK and dependencies..."
# WHY: Notify the user before the long-running install step begins.
npm install @drift-labs/sdk@latest
# WHY: Install the official Drift SDK to access real on-chain program interfaces and account parsers.
npm install @solana/web3.js@latest
# WHY: Install Solana web3.js to create RPC connections, wallets, and transaction signers.
npm install @solana/spl-token@latest
# WHY: Install SPL token library to handle USDC and other token accounts during liquidations.
npm install express@latest
# WHY: Install Express to build the REST API that exposes position and liquidation endpoints.
npm install dotenv@latest
# WHY: Install dotenv to load private keys and RPC URLs from a .env file instead of hardcoding secrets.
npm install typescript@latest ts-node@latest
# WHY: Install TypeScript and ts-node so students can run .ts files directly without pre-compilation.
npm install @types/express@latest @types/node@latest
# WHY: Install type definitions for Express and Node so the TypeScript compiler validates API code.
echo "Creating .env template..."
# WHY: Inform the user that a configuration template is being generated.
if [ ! -f "../../.env" ]; then
# WHY: Only create the template if no .env exists to avoid overwriting existing secrets.
  cat > ../../.env << 'EOF'
# WHY: This file stores secrets and configuration outside of source control.
DRIFT_RPC_URL=https://api.devnet.solana.com
# WHY: Point the bot at Solana devnet so students can test without risking mainnet funds.
DRIFT_PRIVATE_KEY="[YOUR_BASE58_KEY_HERE]"
# WHY: Provide the bot's wallet key so it can sign liquidation transactions on-chain.
DRIFT_ENV=devnet
# WHY: Explicitly tag the environment so the SDK loads the correct program IDs and market configs.
EOF
# WHY: Write the template content to disk so the operator knows which variables to fill in.
fi
# WHY: Close the conditional after writing the template.
echo "Setup complete."
# WHY: Confirm success so the user knows all packages are installed and the project is ready.
echo "Next steps:"
# WHY: Guide the user toward the immediate next actions to start using the code.
echo "1. Fill in DRIFT_PRIVATE_KEY inside ../../.env"
# WHY: The bot cannot sign transactions until a valid private key is provided.
echo "2. Run: npx ts-node keeper_bot.ts"
# WHY: Provide the exact command to launch the keeper bot for quick verification.
echo "3. Run: npx ts-node drift_api.ts"
# WHY: Provide the exact command to launch the Express API for endpoint testing.
