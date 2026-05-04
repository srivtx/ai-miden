#!/bin/bash # WHY: The shebang tells the operating system to execute this script with the Bash shell.
set -e # WHY: Exit immediately if any command fails so the environment is never left in a partially configured state.

echo "Building AI Miden Jupiter API Integration Phase 60" # WHY: Log the start so the operator knows which phase is being deployed.

cd "$(dirname "$0")" # WHY: Change to the script's directory so all relative paths resolve correctly regardless of invocation location.

cd ../../src_web3 # WHY: Move to the src_web3 directory where package.json exists so npm can locate and install dependencies.
echo "Installing Node.js dependencies..." # WHY: Announce the step so the operator can follow the deployment progress.
npm install # WHY: Install all Node dependencies specified in package.json including @solana/web3.js, express, and bs58.

cd phase60 # WHY: Return to the phase60 directory where the application code and environment configuration live.

if [ ! -f .env ]; then # WHY: Check whether a .env file already exists so we do not overwrite existing configuration.
    echo "Creating .env file with placeholder environment variables..." # WHY: Inform the operator that we are generating a new environment file.
    cat > .env <<EOF # WHY: Use a heredoc to create the .env file with documented placeholder variables.
# Jupiter API key (optional for devnet, recommended for production rate limits) # WHY: Document that a key is optional for basic devnet usage but important for production.
JUPITER_API_KEY=your_jupiter_api_key_here # WHY: Provide a placeholder so the operator knows what value to set for Jupiter API access.
# Devnet wallet private key (base58 encoded) used for signing transactions # WHY: Document the expected key format and purpose so the operator generates the correct secret.
DEVNET_WALLET_PRIVATE_KEY=your_devnet_private_key_here # WHY: Provide a placeholder so the operator knows to set a test wallet private key.
EOF # WHY: Close the heredoc.
    echo ".env file created. Please edit it with your actual values." # WHY: Instruct the operator to fill in secrets before running the code.
else # WHY: Branch to handle the case where .env already exists.
    echo ".env file already exists. Skipping creation." # WHY: Inform the operator that existing configuration is preserved.
fi # WHY: Close the conditional block.

echo "Exporting environment variables..." # WHY: Announce that we are loading the environment variables into the current shell session.
export $(grep -v '^#' .env | xargs) # WHY: Source the .env file by exporting each variable so the API and swap script can read them without dotenv.

echo "Setup complete." # WHY: Signal that the deployment script has finished successfully.

echo "" # WHY: Print a blank line for readability.
echo "To start the Express API on port 3068, run:" # WHY: Provide clear instructions so the operator knows how to launch the server.
echo "  cd src_web3/phase60 && npx ts-node jupiter_api.ts" # WHY: Print the exact command so the operator can copy and paste it.
echo "" # WHY: Print a blank line for readability.
echo "To run the standalone swap script, run:" # WHY: Provide clear instructions for running the demo script.
echo "  cd src_web3/phase60 && npx ts-node jupiter_swap.ts" # WHY: Print the exact command for the swap demo.
