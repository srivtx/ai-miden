#!/bin/bash
# WHY: This script automates environment setup so students do not miss steps.

set -e
# WHY: Exit immediately on error to prevent partial setup.

echo "=== Phase 61: Production Infrastructure Setup ==="
# WHY: Inform the user which phase is being configured.

PROJECT_DIR="/Users/zen/Desktop/building-ai/ai-miden"
# WHY: Define the absolute project path for consistency.

cd "$PROJECT_DIR"
# WHY: Ensure all commands run from the project root.

if [ ! -f package.json ]; then
  # WHY: Check if npm has been initialized to avoid creating nested projects.
  echo "Initializing npm project..."
  npm init -y
  # WHY: Create package.json with defaults.
fi

echo "Installing dependencies..."
npm install @solana/web3.js express dotenv
# WHY: Install Solana web3.js for blockchain interaction, Express for API, dotenv for secrets.

npm install -D typescript ts-node @types/express @types/node
# WHY: Install TypeScript toolchain for type safety and ts-node for direct execution.

if [ ! -f tsconfig.json ]; then
  # WHY: Generate tsconfig.json only if absent to avoid overwriting custom config.
  npx tsc --init --outDir dist --rootDir src_web3 --esModuleInterop --resolveJsonModule --module commonjs --target es2020
  # WHY: Configure TypeScript compiler for Node.js with CommonJS output.
fi

mkdir -p src_web3/phase61 docs_web3/phase61
# WHY: Ensure directory structure exists even if previous files were not created.

if [ ! -f .env ]; then
  # WHY: Create .env template if missing to guide secret configuration.
  cat > .env << 'ENVEOF'
# WHY: Store secrets outside version control.
HELIUS_API_KEY=your_helius_api_key_here
# WHY: Helius API key for authenticated RPC and webhook access.
SOLANA_PRIVATE_KEY=your_base58_encoded_private_key_here
# WHY: Fee payer private key for signing transactions.
WEBHOOK_SECRET=your_webhook_secret_here
# WHY: Shared secret to verify incoming Helius webhook signatures.
ENVEOF
  echo ".env file created. Edit it with your actual secrets before running."
  # WHY: Warn the user that placeholder values must be replaced.
fi

echo "=== Setup complete ==="
# WHY: Signal successful completion.
echo "Next steps:"
# WHY: Guide the user to the next actions.
echo "1. Edit .env with your Helius API key and private key."
echo "2. Run the demo: npx ts-node src_web3/phase61/infra_demo.ts"
echo "3. Start the API: npx ts-node src_web3/phase61/infra_api.ts"
