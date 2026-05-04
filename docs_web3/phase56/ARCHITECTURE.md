# Phase 56: Cross-Chain Bridge Architecture — Step-by-Step Build

## Step 1: Design Lock Contract on Source Chain

**What**: Create a smart contract on the source chain (e.g., Ethereum) that accepts ERC-20 tokens and emits a structured `LockEvent`.

**Why**: The lock contract is the entry point of the bridge. Without a deterministic event that guardians can observe, there is no objective proof that tokens were deposited. The contract must emit the user's target address, the token amount, the token address, and a unique nonce so that guardians can construct an unambiguous attestation message. We also deduct a fee here to fund relayers later.

Key components:
- `lock(address token, uint256 amount, bytes32 targetRecipient, uint256 nonce)` function
- Transfer tokens from user to a PDA or contract-controlled vault
- Emit `LockEvent(token, amount, targetRecipient, nonce, blockNumber)`
- Enforce minimum amounts to prevent spam

## Step 2: Design Mint Contract on Target Chain

**What**: Build a Solana program that mints wrapped SPL tokens after verifying guardian threshold signatures.

**Why**: The target chain cannot trust any single off-chain actor. It must independently verify that a threshold of guardians agreed a lock occurred. The mint contract stores guardian public keys, validates each signature in an aggregated proof, checks nonces against a `consumed_nonces` map, and only then invokes the SPL token program to mint wrapped tokens to the user.

Key components:
- Instruction: `MintWrapped { amount: u64, nonce: u64, signatures: Vec<Signature> }`
- PDA for `BridgeState` tracking total minted and consumed nonces
- CPI to `spl_token::mint_to` using a bridge-controlled mint authority
- Fee distribution to the submitting relayer account

## Step 3: Implement Guardian Attestation

**What**: Deploy a guardian registry program where validators register, stake collateral, and sign attestations.

**Why**: Decentralization requires independent validators with economic skin in the game. A registry ensures only registered guardians can contribute to the threshold. Stake creates a slashing condition: if a guardian signs an invalid event, anyone can prove fraud and the guardian loses their stake. Without stake, guardians have no cost to lying.

Key components:
- `RegisterGuardian { stake: u64 }` instruction
- `GuardianAccount` storing pubkey, stake amount, and active status
- `AttestEvent { event_hash: [u8; 32] }` off-chain signing standard
- On-chain `VerifyThreshold` function checking signatures against registry

## Step 4: Build Relayer Network

**What**: Create a standalone TypeScript service that listens to source chain events, queries guardian APIs for signatures, and submits proofs to Solana.

**Why**: Guardians sign messages but do not pay gas on the target chain. Relayers perform the actual transaction submission. A competitive relayer network ensures liveness: if one relayer goes offline, another picks up the event. Relayers are economically motivated by fees locked in Step 1. The relayer must parse events, construct the instruction data, fetch signatures from a quorum of guardians, and handle transaction retry logic.

Key components:
- RPC websocket subscription to source chain `LockEvent` logs
- HTTP polling of guardian endpoints: `GET /attest?eventHash=0x...`
- Proof construction: bundle signatures and guardian indices
- Solana transaction submission with priority fees
- Confirmation polling and duplicate detection

## Step 5: Add Fee Mechanism

**What**: Integrate fee collection during lock, fee escrow in a PDA, and fee release during mint.

**Why**: Without fees, relayers have no revenue and will stop operating, causing the bridge to freeze. Fees must be collected in a token that relayers value (e.g., USDC or the native gas token). Escrowing the fee in a PDA ensures the relayer is paid only upon successful delivery, preventing payment for failed transactions. The fee rate must be high enough to cover worst-case gas and infrastructure costs.

Key components:
- Lock contract deducts 0.3% from transfer amount
- `FeeVault` PDA holds fees per bridge direction
- Mint instruction releases fee to the `relayer` account passed in the instruction
- Optional: burn a portion of the fee for deflationary tokenomics

## Step 6: Implement Burn and Release

**What**: Add the reverse direction: burn wrapped tokens on Solana to unlock original tokens on the source chain.

**Why**: A bridge must be two-way. If users can only move assets in, the system is a black hole. The burn-and-release path ensures users can exit. It also maintains the 1:1 backing invariant: burning wrapped tokens must decrease the wrapped supply before the source chain releases the original collateral. This requires the same guardian attestation pattern in reverse: guardians observe a `BurnEvent` on Solana and attest to the source chain contract.

Key components:
- Instruction: `BurnWrapped { amount: u64, nonce: u64 }`
- CPI to `spl_token::burn` from user's token account
- Emit `BurnEvent(amount, sourceRecipient, nonce)`
- Source chain contract verifies guardian threshold for burn, then transfers from vault to `sourceRecipient`

## Step 7: Add Guardian Rotation

**What**: Implement a governance mechanism to add, remove, or replace guardians and update the signing threshold.

**Why**: Guardians may need to rotate keys due to compromise, hardware failure, or organizational changes. A static guardian set is a long-term liability. However, rotation is a high-privilege operation: if an attacker can unilaterally add their own guardian, they control the bridge. Therefore, rotation must itself require a threshold of existing guardians or a time-locked DAO vote. The bridge program must support updating the stored guardian list and threshold without redeploying the program.

Key components:
- `ProposeRotation { new_guardians: Vec<Pubkey>, new_threshold: u8 }` instruction
- `RotationProposal` PDA with voting state
- Existing guardians vote by signing the proposal hash
- Once threshold is met, execute rotation and update `GuardianRegistry`
- Timelock delay (e.g., 48 hours) before execution for community review

## Step 8: Test Full Round-Trip

**What**: Write end-to-end integration tests that simulate a user locking on the source chain, minting on Solana, burning on Solana, and releasing on the source chain.

**Why**: Unit tests on individual programs do not catch integration failures: nonce desynchronization, signature encoding mismatches, fee calculation errors, or CPI reversion. A full round-trip test validates the entire system invariant: `locked_amount - released_amount == minted_amount - burned_amount`. It also tests failure modes like invalid signatures, double-spend attempts, and rate limit breaches.

Key components:
- Local test validator (solana-test-validator) running the bridge and guardian programs
- Mock source chain event emitter (a test program or script)
- Guardian mock service producing deterministic test signatures
- Relayer simulation script
- Assertion checks for token balances, nonce states, and fee vault balances
- Fuzz test: submit invalid signatures and verify rejection
