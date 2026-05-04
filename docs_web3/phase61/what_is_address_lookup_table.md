# What is Address Lookup Table?

## The Problem

A Solana transaction has a hard limit of 1,232 bytes. Each account address is 32 bytes. If your transaction needs to interact with 30 accounts (a complex DeFi swap with multiple hops, oracle accounts, and token accounts), just the addresses alone consume 960 bytes. Add instructions, signatures, and metadata, and you exceed the size limit. Without compression, complex transactions are impossible.

## Definition

An Address Lookup Table (LUT) is an on-chain account that stores a list of up to 256 addresses. A versioned transaction (v0) can reference these stored addresses by a 1-byte index instead of the full 32-byte pubkey. This compresses the transaction size, enabling up to 64 unique accounts per transaction.

## How It Works

1. **Create the table**: You allocate a lookup table account with `AddressLookupTableProgram.createLookupTable`, which returns the table address and a creation slot.
2. **Extend the table**: You add addresses using `AddressLookupTableProgram.extendLookupTable`. Each extension instruction can add up to 30 addresses due to transaction size limits during the extend operation.
3. **Activate the table**: After the creation slot has passed and the table is extended, it becomes active and usable in versioned transactions.
4. **Reference in v0 transaction**: When building a versioned transaction, you pass the lookup table addresses to `VersionedTransaction.compile`. The compiler replaces matching accounts with 1-byte table indices.
5. **On-chain resolution**: The Solana runtime reads the lookup table account during transaction processing and expands the indices back into full 32-byte addresses before execution.
6. **Deactivate and close**: If the table is no longer needed, the authority can deactivate it, wait for the deactivation period, and then close it to recover rent.

## Real-life analogy

Think of a warehouse inventory list. Instead of writing the full product description on every shipping label (32 bytes each), you write a barcode (1 byte) that references the master list. The shipping label stays small, but the warehouse still knows exactly which product to pull.

## Tiny numeric example

You have a transaction that references 35 accounts.

- Legacy transaction: 35 accounts * 32 bytes = 1,120 bytes for addresses alone. Remaining space for instructions and metadata: 112 bytes. Likely fails.
- Versioned transaction with 1 LUT: 35 accounts stored in the LUT. On-chain references use 1 byte each. Transaction only needs to include the LUT address (32 bytes) + indices (35 bytes) = 67 bytes for account referencing. Remaining space: 1,165 bytes. Transaction succeeds.

The savings scale linearly: for every account in the LUT, you save 31 bytes.

## Common confusion

- No. Address Lookup Tables are not automatic. You must explicitly create, extend, and reference them.
- No. LUTs do not reduce transaction fees. They reduce transaction size; fees are based on compute units and signatures, not byte size.
- No. You cannot use a LUT in a legacy transaction. Only versioned transactions (v0) support lookup tables.
- No. A lookup table address itself still costs 32 bytes in the transaction. The savings come from the accounts stored inside it.
- No. You do not need to redeploy your program to support LUTs. LUTs are a transaction-layer feature, not a program-layer feature.
- No. LUTs are not shared by default. Anyone can create one, but only the authority can extend or deactivate it.

## Key properties

1. **256-address capacity**: Each lookup table can store up to 256 addresses.
2. **v0 transactions only**: Legacy transactions cannot reference lookup tables.
3. **Rent-exempt**: Creating a lookup table requires a rent-exempt balance in SOL.
4. **1-byte indexing**: Accounts in the table are referenced by a single byte index.
5. **Authority-gated**: Only the designated authority can modify or close the table.
