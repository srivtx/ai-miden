#!/bin/bash
# WHY: Use bash as the interpreter so the script runs in a compatible shell.
set -e
# WHY: Exit immediately if any command fails to prevent partial deployments.
echo "Building hook program..."
# WHY: Log the current build step so the operator can follow progress.
anchor build --program-name hook
# WHY: Compile the hook program so it is ready for deployment.
echo "Building token program..."
# WHY: Log the current build step for operator visibility.
anchor build --program-name token
# WHY: Compile the token program that manages the Token-2022 mint.
echo "Deploying programs..."
# WHY: Log the deployment start so the operator knows the script reached this stage.
anchor deploy
# WHY: Deploy both compiled programs to the cluster configured in Anchor.toml.
echo "Deployment complete"
# WHY: Print a success message so the operator knows the script finished without errors.
