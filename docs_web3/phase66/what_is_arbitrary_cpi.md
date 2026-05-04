# What Is Arbitrary CPI

## The Problem
An attacker can invoke malicious programs through Cross-Program Invocation (CPI) when the destination program ID is not validated. This allows an attacker to route protocol instructions to arbitrary contracts, bypassing intended security controls and potentially draining funds or corrupting state.

## Definition
Arbitrary CPI occurs when a Solana program performs a cross-program invocation without restricting which program can be called. Instead of invoking a known, trusted program, the code accepts any account as the CPI target, effectively delegating execution to user-controlled addresses.

## How It Works
1. Identify the CPI call: Locate `invoke` or `invoke_signed` in the program.
2. Check program ID whitelist: Verify that the target program ID is compared against an allowed set of programs.
3. Validate account ownership: Ensure the target account is actually a program and owned by the loader.
4. Verify instruction data: Confirm the instruction data passed to CPI does not contain unauthorized operations.
5. Restrict permissions: Limit which instructions within the target program can be invoked.
6. Audit: Review the full call graph for indirect CPI paths that might skip validation.

## Real-life analogy
Imagine a bank teller who accepts transfer requests without checking which financial institution receives the money. A customer asks to wire funds to "any account at this address," and the teller sends the money to a fraudulent institution because there is no whitelist of approved banks.

## Tiny numeric example with exploit payload
A program holds 1,000,000 lamports in a vault. An attacker creates a malicious program that transfers all lamports to the attacker's wallet when invoked. The vulnerable program accepts the attacker's program as the CPI target and forwards a `WithdrawAll` instruction. The payload executes via CPI, draining the 1,000,000 lamports.

## Common confusion
- "Passing the program ID as an argument is enough validation." No. Arguments are user-controlled and must be checked against a hardcoded whitelist.
- "The invoked program will revert if the instruction is invalid." No. A malicious program intentionally accepts harmful instructions.
- "Only the program owner can specify CPI targets." No. Any transaction signer can provide arbitrary accounts.
- "Checking account ownership on the target is unnecessary." No. The target must be a real program account owned by the BPF loader.
- "Instruction data is safe because it is opaque bytes." No. Opaque bytes can encode destructive operations when interpreted by a malicious program.
- "CPI calls are sandboxed and cannot steal lamports." No. CPI inherits the privileges of the calling program and can perform transfers on its behalf.

## Key properties
1. The CPI target program ID must be explicitly whitelisted or hardcoded.
2. Unchecked `AccountInfo` used as a CPI destination is a critical vulnerability.
3. Instruction data forwarded to CPI should be validated or constructed by the program, not blindly passed from users.
4. Programs should verify that the target account is executable and owned by the BPF loader.
5. Arbitrary CPI often pairs with missing signer checks to escalate privileges.
