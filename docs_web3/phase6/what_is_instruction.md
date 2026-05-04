## What Is an Instruction?

**The Problem:**
You know a transaction is a container, but what actually goes inside it?
How do you tell the blockchain precisely which program to run, which accounts to touch, and what parameters to pass?
Without instructions, a transaction would be an empty envelope with no action to perform.
Instructions are the actual commands that change state or trigger logic on the blockchain.
They are the smallest executable unit that a validator processes.
Understanding instructions is essential for writing any on-chain logic.

**Definition:**
An **instruction** is the smallest unit of computation on Solana.
It specifies exactly one operation: which program to invoke, which accounts that program may read or write, and what data to pass as arguments.
A transaction contains one or more instructions that execute sequentially and atomically.
Each instruction is a self-contained command that the runtime routes to the correct program.

**Anatomy of an instruction:**
- **Program ID** — The public key of the program to execute
- **Accounts** — A list of accounts with meta-flags (signer, writable)
- **Data** — Serialized bytes containing instruction-specific parameters

**Real-life analogy:**
An instruction is like a single command on a restaurant order ticket.
The ticket might say: "Table 5, Order: Grilled Salmon, Side: Rice, No Onions."
The chef (program) knows exactly what to cook based on the order details (data).
The waiter (transaction) carries multiple tickets to the kitchen, but each ticket is a distinct instruction.
If one ticket says "Steak" and another says "Salad," both are prepared and delivered together.
If the kitchen is out of salmon, the entire order for Table 5 is rejected — no partial meals are served.
The accounts are the ingredients and the table number.
The signers are the waiter who confirmed the order and the customer who placed it.
The chef follows the recipe (program logic) exactly as written on the ticket.
If an ingredient is missing, the chef cannot improvise; they must reject the order.

**Tiny numeric example:**
```
Instruction 1: System Transfer
  - Program ID: 11111111111111111111111111111111
  - Accounts:
    0. Alice  [signer=true,  writable=true]
    1. Bob    [signer=false, writable=true]
  - Data (8 bytes): [00, 00, 00, 00, 3B, 9A, CA, 00]
    // u64 little-endian: 1,000,000,000 lamports = 1 SOL

Instruction 2: Memo
  - Program ID: MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr
  - Accounts:
    0. Alice [signer=true, writable=false]
  - Data (variable): "Payment for coffee"
```

**Common confusion:**
- **"An instruction is a transaction."**
  No. An instruction is one step inside a transaction.
  A transaction can batch multiple instructions together.
- **"Instructions execute in parallel."**
  No. Instructions inside a single transaction execute sequentially in the order they appear.
- **"Every instruction needs a signer."**
  No. Only instructions that mutate an account owned by a signer require a signature.
  Read-only instructions may need no signers.
- **"Instruction data is always JSON."**
  No. Instruction data is raw bytes.
  You must serialize your parameters using a scheme like Borsh before including them.
- **"Programs can ignore account permissions."**
  No. The runtime enforces that a program cannot write to an account marked read-only.
- **"Instructions can call any program."**
  Yes, but the called program must exist on-chain and the instruction data must match what that program expects.
- **"Account order in instructions does not matter."**
  It matters a great deal.
  Programs expect accounts at specific indices and will fail if they are out of order.
- **"Instruction data can be empty."**
  Yes. Some instructions, like a simple ping, require no extra data beyond the instruction discriminant.
- **"Instructions are free."**
  No. Every instruction consumes compute units, and the total transaction fee covers all instructions in the bundle.
- **"One instruction can only call one program."**
  Yes. Each instruction targets exactly one program ID.

**Where it appears in our code:**
`src_web3/phase6/first_transaction.rs` — Creates a system_instruction::transfer and wraps it in a transaction.
`src_web3/phase6/transaction_api.ts` — Express API builds instructions dynamically based on request parameters.
`src_web3/phase7/rpc_client_demo.rs` — Reads transactions containing multiple instructions from the blockchain.
