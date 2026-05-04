#!/bin/bash                                            # WHY: Declares that this script should be executed with the Bash shell interpreter.
set -e                                                 # WHY: Exits immediately if any command fails so partial deployments do not occur.
set -o pipefail                                        # WHY: Ensures that pipeline failures (e.g., anchor build | tee) cause the script to exit with an error.

echo "Building Anchor program..."                      # WHY: Prints a status message so the operator knows the build step has started.
anchor build                                           # WHY: Compiles the Rust program to BPF, runs the linter, and generates the IDL JSON file.

echo "Running tests..."                                # WHY: Prints a status message so the operator knows the test suite is executing.
anchor test                                            # WHY: Starts a local validator, deploys the program, and runs the TypeScript tests against it.

echo "Deploying to devnet..."                          # WHY: Prints a status message so the operator knows the devnet deployment step has begun.
anchor deploy --provider.cluster devnet                # WHY: Deploys the compiled BPF binary to Solana devnet using the devnet provider configuration.

echo "Deployment complete!"                            # WHY: Prints a success message so the operator knows all steps finished without errors.
