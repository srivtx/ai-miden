#!/bin/bash
# WHY: The shebang tells the operating system to execute this script with bash, ensuring consistent behavior across environments.
set -euo pipefail
# WHY: set -e exits immediately if any command fails, preventing partial deployments.
# WHY: set -u treats unset variables as errors, catching typos and missing configuration.
# WHY: set -o pipefail propagates errors through pipelines, ensuring the script fails if any piped command fails.

# WHY: These variables define the project paths so the script can find the Anchor workspace and built artifacts.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# WHY: SCRIPT_DIR resolves the absolute path of this script, making the script runnable from any working directory.
GOVERNANCE_DIR="${SCRIPT_DIR}/governance"
# WHY: GOVERNANCE_DIR points to the Anchor workspace containing the programs.
TARGET_DIR="${GOVERNANCE_DIR}/target"
# WHY: TARGET_DIR is where Anchor places build outputs, IDLs, and deployable binaries.

# WHY: This function prints a message with a timestamp so the operator can follow the deployment progress.
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
    # WHY: date formats the current time for human-readable logs.
    # WHY: $* expands all function arguments into a single string for the log message.
}

# WHY: This function checks that required tools are installed before attempting to build or deploy.
check_dependencies() {
    log "Checking dependencies..."
    # WHY: Logging the step name helps the operator understand what the script is doing.

    command -v anchor >/dev/null 2>&1 || { log "Error: anchor CLI not found. Install with: avm install latest"; exit 1; }
    # WHY: command -v checks if the anchor binary exists in PATH.
    # WHY: Redirecting to /dev/null suppresses output; the || clause runs only if the command fails.
    # WHY: Exiting with code 1 signals a dependency failure to CI systems.

    command -v solana >/dev/null 2>&1 || { log "Error: solana CLI not found. Install from https://docs.solana.com/cli/install"; exit 1; }
    # WHY: The solana CLI is needed for keypair management and cluster configuration.

    command -v rustc >/dev/null 2>&1 || { log "Error: Rust not found. Install from https://rustup.rs"; exit 1; }
    # WHY: rustc is the Rust compiler; Anchor invokes it during the build process.

    log "All dependencies found."
    # WHY: Confirmation logging reassures the operator that the environment is ready.
}

# WHY: This function ensures the deployer wallet exists and is funded for deployment fees.
setup_wallet() {
    log "Setting up deployer wallet..."
    # WHY: Deployment requires a funded keypair to pay for program account rent and transaction fees.

    local wallet_path="${HOME}/.config/solana/id.json"
    # WHY: The default Solana CLI wallet path is used for consistency with Anchor.toml.

    if [ ! -f "$wallet_path" ]; then
        # WHY: Checking file existence prevents errors when the wallet does not exist.
        log "Wallet not found at ${wallet_path}. Generating new keypair..."
        solana-keygen new --no-passphrase -o "$wallet_path"
        # WHY: solana-keygen creates a new Ed25519 keypair for the deployer.
        # WHY: --no-passphrase is used for automated deployments; production should use a secure passphrase.
    fi

    local balance
    balance=$(solana balance --keypair "$wallet_path" 2>/dev/null || echo "0")
    # WHY: solana balance returns the wallet's SOL balance; echo "0" handles RPC failures gracefully.

    if (( $(echo "$balance < 2" | bc -l) )); then
        # WHY: 2 SOL is a safe minimum for devnet deployment of two programs plus rent exemptions.
        log "Wallet balance is ${balance} SOL. Requesting airdrop..."
        solana airdrop 2 --keypair "$wallet_path"
        # WHY: solana airdrop requests devnet SOL from the faucet.
    fi

    log "Deployer wallet ready at ${wallet_path} with balance $(solana balance --keypair "$wallet_path") SOL"
    # WHY: Logging the final balance confirms the wallet is sufficiently funded.
}

# WHY: This function builds the Anchor programs and generates the IDL files.
build_programs() {
    log "Building Anchor programs..."
    # WHY: Building compiles the Rust source to BPF bytecode and emits the IDL JSON.

    cd "$GOVERNANCE_DIR"
    # WHY: Changing to the Anchor workspace directory ensures anchor build finds Anchor.toml.

    anchor build
    # WHY: anchor build invokes cargo build-bpf, generates the IDL, and verifies the program binary.

    log "Build complete. Artifacts in ${TARGET_DIR}"
    # WHY: Logging the output directory helps the operator locate binaries and IDLs.
}

# WHY: This function deploys the built programs to the Solana devnet.
deploy_programs() {
    log "Deploying programs to devnet..."
    # WHY: Devnet is the public test network; it behaves like mainnet without requiring real funds.

    cd "$GOVERNANCE_DIR"
    # WHY: The anchor deploy command must run from the workspace root.

    anchor deploy --provider.cluster devnet
    # WHY: --provider.cluster devnet tells Anchor to target the devnet RPC endpoint.
    # WHY: anchor deploy creates a buffer account, writes the BPF bytecode, and sets the program account authority.

    log "Deployment complete."
    # WHY: Confirmation logging signals that the programs are live on-chain.
}

# WHY: This function updates the program IDs in source files and config to match the deployed addresses.
update_program_ids() {
    log "Updating program IDs in source code..."
    # WHY: Program IDs must match the deployed addresses or transaction validation will fail.

    local gov_idl="${TARGET_DIR}/idl/governance.json"
    local tre_idl="${TARGET_DIR}/idl/treasury.json"
    # WHY: The IDL files contain the deployed program addresses after anchor deploy.

    local gov_address
    gov_address=$(jq -r '.metadata.address' "$gov_idl")
    # WHY: jq extracts the address field from the IDL metadata.
    local tre_address
    tre_address=$(jq -r '.metadata.address' "$tre_idl")

    if [ "$gov_address" != "null" ] && [ -n "$gov_address" ]; then
        # WHY: Checking for null and non-empty ensures the deployment actually emitted an address.
        log "Governance program ID: ${gov_address}"
        sed -i.bak "s/declare_id!(\"Gov111111111111111111111111111111111111111\")/declare_id!(\"${gov_address}\")/g" \
            "${GOVERNANCE_DIR}/programs/governance/src/lib.rs"
        # WHY: sed replaces the placeholder program ID with the real deployed address.
        # WHY: -i.bak creates a backup file in case the replacement needs to be reverted.
    fi

    if [ "$tre_address" != "null" ] && [ -n "$tre_address" ]; then
        log "Treasury program ID: ${tre_address}"
        sed -i.bak "s/declare_id!(\"Tre222222222222222222222222222222222222222\")/declare_id!(\"${tre_address}\")/g" \
            "${GOVERNANCE_DIR}/programs/treasury/src/lib.rs"
        # WHY: The treasury program ID is updated similarly to the governance program ID.
    fi

    log "Program IDs updated."
    # WHY: Confirmation logging signals that the source code is synchronized with the deployment.
}

# WHY: This function verifies the deployment by fetching the program accounts from the cluster.
verify_deployment() {
    log "Verifying deployment on devnet..."
    # WHY: Verification ensures the programs were actually uploaded and are executable.

    local gov_idl="${TARGET_DIR}/idl/governance.json"
    local tre_idl="${TARGET_DIR}/idl/treasury.json"

    local gov_address
    gov_address=$(jq -r '.metadata.address' "$gov_idl")
    local tre_address
    tre_address=$(jq -r '.metadata.address' "$tre_idl")

    solana program show "$gov_address" --url devnet >/dev/null 2>&1 || { log "Error: Governance program not found on devnet"; exit 1; }
    # WHY: solana program show verifies the program account exists and is marked as executable.
    # WHY: Redirecting output to /dev/null keeps logs clean; the || clause catches verification failures.

    solana program show "$tre_address" --url devnet >/dev/null 2>&1 || { log "Error: Treasury program not found on devnet"; exit 1; }

    log "Deployment verified successfully."
    # WHY: Confirmation logging signals that both programs are live and executable.
}

# WHY: This is the main execution flow that orchestrates the build and deployment pipeline.
main() {
    log "Starting Phase 54v2 deployment pipeline..."
    # WHY: A clear startup message helps the operator identify which deployment is running.

    check_dependencies
    # WHY: Dependencies must be verified first to avoid cryptic failures later.

    setup_wallet
    # WHY: A funded wallet is required before any on-chain operations.

    build_programs
    # WHY: Programs must be compiled before they can be deployed.

    deploy_programs
    # WHY: Deployment uploads the binaries to the cluster.

    update_program_ids
    # WHY: Source code must reference the deployed addresses for the client to work.

    verify_deployment
    # WHY: Verification confirms the deployment succeeded and the programs are executable.

    log "Phase 54v2 deployment pipeline complete."
    # WHY: A clear completion message signals success to the operator and CI systems.
}

# WHY: Calling main runs the deployment pipeline when the script is executed directly.
main "$@"
# WHY: "$@" passes all script arguments to main, allowing future extensibility (e.g., --cluster mainnet).
