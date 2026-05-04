## What Is Program State?

**The Problem:**
Your program needs to remember things between invocations.
It needs to store a counter value, a user's high score, or a token balance.
But programs themselves are stateless.
Where do you store this data, and how do you ensure only your program can modify it?
Without persistent state, every program invocation would start from scratch.

**Definition:**
**Program state** is data stored in accounts that are owned by your program.
Your program can read and write these accounts when explicitly invoked by a transaction.
It cannot access any other account's data without permission.
The data account persists on-chain between invocations, making it the permanent memory of your program.

**How state works:**
1. Your program is deployed as an executable account (read-only bytecode)
2. You create a separate data account and set your program as the owner
3. Your program reads from and writes to the data account when invoked
4. The data account persists between transactions, preserving state
5. Only your program can modify data accounts it owns

**Real-life analogy:**
Program state is like a doctor's patient file cabinet.
The doctor (program) has strict rules about how to treat patients.
Prescribe medicine, record symptoms, schedule follow-ups.
But the doctor does not memorize every patient's history.
Instead, each patient has a file (data account) in a cabinet.
The file cabinet is inside the doctor's office (owned by the program).
When a patient arrives (transaction), the nurse pulls the file (reads account data).
The doctor updates it (mutates state), and the nurse files it back (serializes to account).
The rules (program) never change, but the files (state) change every day.
No other doctor's office can modify these files because they do not have the key.

**Tiny numeric example:**
```rust
// WHY: This struct defines the layout of state in the account.
// Every field has a fixed size so we can serialize predictably.
#[derive(BorshSerialize, BorshDeserialize)]
struct Counter {
    count: u64,  // 8 bytes
}

// State stored in account data before increment:
// [0, 0, 0, 0, 0, 0, 0, 5]  => count = 5

// Transaction: Increment
// 1. Program deserializes account data into Counter { count: 5 }
// 2. Program increments: counter.count = 6
// 3. Program serializes back: [0, 0, 0, 0, 0, 0, 0, 6]
// 4. Validator commits the new account data

// State stored in account data after increment:
// [0, 0, 0, 0, 0, 0, 0, 6]  => count = 6
```

**Common confusion:**
- **"Programs store state internally."**
  No. Programs are read-only bytecode.
  State is in separate data accounts that the program owns.
- **"I need one data account per user."**
  Often yes.
  Each user typically has their own data account, usually a PDA derived from their public key.
- **"Data account size is unlimited."**
  No. You specify size at creation and pay rent.
  The practical maximum is 10MB, but most accounts are under 1KB.
- **"Programs can create accounts themselves."**
  Programs cannot create accounts directly.
  They must invoke the System Program via CPI to allocate space and transfer ownership.
- **"State is automatically persisted."**
  Yes, but only if the transaction succeeds.
  Failed transactions roll back all account mutations.
- **"Any program can read my state."**
  Reading is public on the blockchain.
  But only the owning program can write to a data account.
- **"Account data is human-readable by default."**
  No. Account data is raw bytes.
  You must deserialize it using a schema like Borsh to get meaningful values.
- **"State changes are visible immediately."**
  They are visible after the transaction is processed.
  Other clients may see them at different commitment levels.
- **"I can store state in the program account."**
  No. Program accounts are executable and read-only.
  The runtime prevents writing to them.

**Where it appears in our code:**
`src_web3/phase9/counter/src/lib.rs` — A counter program that stores a u64 count in a data account and increments it.
`src_web3/phase9/state_api.ts` — Express API that initializes accounts, invokes the program, and reads back the updated state.
