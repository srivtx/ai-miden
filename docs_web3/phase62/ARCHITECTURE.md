# Phase 62 Architecture: Token-2022 Extensions

## Step 1: Create Token-2022 Mint
Allocate a new mint account and assign ownership to the real Token-2022 program `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`. Reserve extra space for extensions.

**WHY:** The mint must be owned by Token-2022 to use extensions, and extra space is required to store the extension data.

## Step 2: Add Transfer Hook Extension
Initialize the transfer hook extension on the mint and store the program ID of the hook validator.

**WHY:** Without this extension, Token-2022 will not CPI into an external program on transfer, so no custom validation can occur.

## Step 3: Implement Hook Program
Write an Anchor program that implements the transfer hook interface. On `execute_hook`, load the sender and reject if the address matches a blacklist.

**WHY:** This is the actual enforcement layer. Token-2022 delegates transfer validation to this program, so the hook must contain the business rules.

## Step 4: Add Metadata Pointer
Initialize the metadata pointer extension on the mint and store the public key of a separate metadata account.

**WHY:** Wallets and explorers need a standardized way to discover metadata. Storing the pointer natively removes external dependencies.

## Step 5: Mint and Test Transfers
Create token accounts, mint tokens to a user, and attempt a transfer. Verify that transfers from a non-blacklisted address succeed.

**WHY:** You must confirm the basic happy path works before testing enforcement edge cases.

## Step 6: Verify Hook Execution
Attempt a transfer from the blacklisted address and confirm the transaction fails with the custom hook error.

**WHY:** This proves the transfer hook extension is active and that Token-2022 correctly CPIs into the hook program on every transfer.
