#!/bin/bash
# WHY: specify bash interpreter so the script executes in the correct shell environment
set -e
# WHY: exit immediately if any command fails to prevent partial or broken deployments
cd "$(dirname "$0")"
# WHY: change to the script directory so relative paths resolve correctly regardless of where the script is invoked
npm install
# WHY: install all Node dependencies including Express, CORS, and Solana web3.js listed in package.json
npx ts-node blink_server.ts
# WHY: compile and run the TypeScript blink server directly without a separate build step
