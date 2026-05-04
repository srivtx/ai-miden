# Phase 59: Anchor Architecture — Step-by-Step

## Step 1: Install Anchor CLI

**What**: Install the Anchor command-line tool, Rust, Solana CLI, and Node.js dependencies.

**Why**: The Anchor CLI (`anchor`) is the build orchestrator. It compiles Rust programs, generates IDLs, runs tests, and manages deployments. Without it, you cannot invoke the procedural macros that generate boilerplate, nor can you produce the IDL JSON required by clients. The Solana CLI provides the local validator and wallet management. Node.js runs the TypeScript test suite and client code.

**What breaks if skipped**: You cannot run `anchor build` or `anchor test`. You would have to manually invoke `cargo build-bpf`, manually extract discriminators, and manually maintain client types. The development loop becomes impossible.

## Step 2: Initialize Project with `anchor init`

**What**: Run `anchor init <project_name>` to create the standard directory structure: `programs/`, `tests/`, `Anchor.toml`, `Cargo.toml`, and migrations.

**Why**: Anchor enforces a specific project layout so the build system knows where to find program source code, test files, and configuration. The `Anchor.toml` file tells the CLI which programs to build, what cluster to target, and what wallet to use. The `Cargo.toml` workspace ensures the program compiles with the correct Solana BPF target and Anchor dependencies. Standardization allows the `anchor build` and `anchor test` commands to work without manual path configuration.

**What breaks if skipped**: The macro expansion and IDL generation depend on relative paths (`programs/*/src/lib.rs`, `target/idl/`). A custom layout requires rewriting the entire build pipeline. Dependencies will not resolve correctly without the workspace configuration.

## Step 3: Define Program Structure

**What**: Write the `#[program]` module with `use anchor_lang::prelude::*;`, `declare_id!()`, and instruction handler functions.

**Why**: The `#[program]` macro is the entrypoint generator. It creates the BPF entrypoint function that the Solana runtime calls, the instruction discriminator table that routes incoming instructions to the correct handler, and the automatic deserialization of instruction arguments. `declare_id!()` hardcodes the program's public key, enabling compile-time verification and IDL metadata. Without this structure, the runtime cannot route transactions to your logic.

**What breaks if skipped**: Without `#[program]`, your Rust module is just a library. The Solana runtime will reject transactions because no valid entrypoint exists. Without `declare_id!()`, Anchor cannot verify that the program ID matches the deployed binary, and clients cannot target the correct on-chain address.

## Step 4: Add Accounts with Constraints

**What**: Define `#[derive(Accounts)]` structs with typed fields and `#[account(...)]` constraint attributes.

**Why**: Solana's programming model is account-centric. Every instruction must declare which accounts it reads and writes. The `#[derive(Accounts)]` macro generates the `Accounts` trait implementation, which tells Anchor how to deserialize each account and what validation to perform. Constraints like `init`, `mut`, `seeds`, and `bump` replace hundreds of lines of manual validation. This step is where security properties are declared; errors here create vulnerabilities that no amount of handler logic can fix.

**What breaks if skipped**: Without account structs, Anchor cannot deserialize accounts. You would receive raw `AccountInfo` pointers and manually verify ownership, mutability, and signers. Missing `init` would cause uninitialized account errors. Missing `mut` would cause runtime write failures. Incorrect `seeds` would allow account injection attacks.

## Step 5: Implement Instructions

**What**: Write the business logic inside instruction handlers using the validated `Context<T>` and account references.

**Why**: This is the core value of the program. Because Anchor has already validated and deserialized accounts, the handler operates on typed, guaranteed-valid state. You can mutate account data, emit events, and invoke CPI helpers without writing serialization code. Separating validation (Step 4) from logic (Step 5) follows the principle of least privilege and makes the code auditable.

**What breaks if skipped**: There is no program functionality. However, more importantly, mixing validation and logic in raw Rust leads to bugs. Anchor's enforced separation means you cannot accidentally access an account before it is validated.

## Step 6: Write Anchor Tests

**What**: Write TypeScript tests using the `@coral-xyz/anchor` client, loading the IDL and calling program methods.

**Why**: Tests verify that constraints work as intended, that instruction logic produces correct state transitions, and that PDA derivation is deterministic. The Anchor test runner starts a local validator, deploys the program, and executes tests in a clean environment. Using the generated client ensures that your tests match the IDL exactly, catching interface mismatches before production.

**What breaks if skipped**: Undetected bugs in constraints or logic reach devnet or mainnet. A missing signer test might pass locally but fail on devnet. PDA derivation errors are only caught when you attempt to validate an address on-chain. Without automated tests, you must manually verify every instruction path.

## Step 7: Deploy to Devnet

**What**: Run `anchor deploy` targeting the devnet cluster after verifying tests pass locally.

**Why**: Devnet is the public testing environment. Deploying there validates that the program works with real network latency, real rent economics, and real transaction fees. It allows frontend developers and other team members to interact with the program before mainnet deployment. The deployment process also verifies that the binary size is under limits and that the program ID matches `declare_id!()`.

**What breaks if skipped**: Deploying untested code directly to mainnet risks permanent loss of funds. Programs on Solana are immutable once deployed (unless upgradeable). Devnet deployment is the final integration test. Without it, you might discover that your PDA derivation uses different seeds than the client, or that an account is too large for the current rent exemption minimum.
