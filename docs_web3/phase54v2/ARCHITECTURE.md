# Phase 54v2 Architecture: Step-by-Step Build

This document walks through building the governance system from scratch using Anchor. Each step explains WHY the step is necessary, not just WHAT to do.

## Step 1: Install Anchor and Initialize Project

Install the Anchor CLI and create a new workspace. Run `avm install latest` and `avm use latest` to get the Anchor CLI. Then run `anchor init governance` to create the project structure. This generates `Anchor.toml`, `Cargo.toml`, and the `programs/` directory with a starter program.

**WHY:** Anchor is a framework, not just a library. It needs a specific workspace structure so the CLI can find your programs, generate IDLs, and manage dependencies. Starting with `anchor init` ensures all paths and config files are correct. Without this structure, the `anchor build` and `anchor deploy` commands will fail.

## Step 2: Define Governance Accounts with Anchor Constraints

Create the governance state accounts: `GovernanceConfig`, `Proposal`, and `VoterRecord`. Use `#[account]` to mark them as Anchor accounts. Add fields for creator, description, quorum, votes, deadline, and execution status. Define constraints like `#[account(mut)]` for writable accounts and `#[account(init, payer = ..., space = ...)]` for new accounts.

**WHY:** In raw Rust, you define structs and then manually serialize them with Borsh. Anchor combines struct definition, serialization, and validation into one system. The `#[account]` macro derives the `AccountSerialize` and `AccountDeserialize` traits. The `init` attribute tells Anchor to create the account via CPI to the system program. The `space` attribute ensures rent exemption. Without these constraints, you would write 30+ lines of boilerplate per account.

## Step 3: Implement Proposal Creation with PDA

Write the `create_proposal` instruction. It takes a description, quorum, and deadline as parameters. Use a PDA seeded with `b"proposal"` and the creator's public key. Store the proposal state in the PDA. Increment a global proposal counter if you track one.

**WHY:** A PDA (Program Derived Address) is an account address that is derived deterministically from seeds and the program ID. It has no private key, so only the program can sign for it. This is essential for governance because the proposal account must be owned and controlled by the program, not by any user. Using a PDA also makes the address predictable: anyone can derive the proposal address off-chain without querying the chain.

## Step 4: Add Token-Weighted Voting with SPL Token Checks

Write the `cast_vote` instruction. It takes the voter's token account, the governance mint, and the proposal. Add constraints: `voter_token_account.owner == voter.key()`, `voter_token_account.mint == governance_mint.key()`. Read `voter_token_account.amount` as the vote weight. Add it to `votes_for` or `votes_against`. Prevent double voting with a `VoterRecord` PDA.

**WHY:** Using lamports for voting is dangerous because SOL is not the protocol's governance token. A user could buy SOL, vote, and sell SOL in the same block. Using an SPL token requires the user to hold the specific governance token, which represents real stake in the protocol. The `owner` and `mint` constraints prevent a voter from passing a random token account. The `VoterRecord` PDA ensures each voter only votes once per proposal.

## Step 5: Build Squads Treasury Integration

Create a treasury program with a `Treasury` account storing members and a threshold. Implement `request_withdrawal`, `approve_withdrawal`, and `execute_withdrawal`. The request creates a proposal PDA. Approval increments an approval counter. Execution checks that approvals meet the threshold, then transfers funds via CPI to the token program.

**WHY:** A single-key treasury is a catastrophic risk. If the deployer loses their key or is compromised, all funds are gone. A multisig ensures that no single person can move funds. The Squads pattern separates proposal, approval, and execution into distinct instructions. This allows asynchronous workflows: members can vote over days, and execution happens only when consensus is reached. The CPI transfer ensures the treasury PDA, not a user wallet, signs the transfer.

## Step 6: Add Timelock and Execution

Add a `timelock_delay` field to `GovernanceConfig`. In the `execute_proposal` instruction, check that the current timestamp is at least `proposal.deadline + config.timelock_delay`. Only then allow the proposal's embedded instruction to be executed.

**WHY:** Timelocks protect against governance attacks. If an attacker passes a malicious proposal through bribery or a flash loan, the timelock gives honest users time to review the outcome and exit the protocol before execution. This is standard practice in Ethereum DAOs (e.g., Compound, Uniswap) and is equally important on Solana. Without a timelock, a passed proposal executes immediately, leaving no reaction time.

## Step 7: Generate IDL and Build TypeScript Client

Run `anchor build`. This compiles the Rust programs and outputs an IDL JSON file in `target/idl/`. Copy this IDL into your TypeScript project. Initialize an Anchor `Program` object with the IDL, a `Provider` (connection + wallet), and the program ID.

**WHY:** The IDL is the contract between on-chain and off-chain code. It contains every instruction name, every account name, and every type definition. The Anchor TypeScript client uses this to provide autocomplete and type checking. Without the IDL, you would manually construct instruction data buffers and account metas, which is error-prone and hard to maintain. The IDL makes integration as simple as calling a typed method.

## Step 8: Test on Devnet

Deploy the programs to devnet using `anchor deploy --provider.cluster devnet`. Fund your deployer wallet with devnet SOL from the faucet. Run integration tests that create a governance config, mint governance tokens, create a proposal, vote with token accounts, and execute after the timelock.

**WHY:** Local testing with `anchor test` uses a local validator, which is fast but does not replicate network latency, compute unit limits, or rent costs. Devnet testing validates that your programs work in a real Solana environment with real RPC nodes. It also lets you test the TypeScript client against real accounts. Governance is high-stakes code. You must test on devnet before mainnet.
