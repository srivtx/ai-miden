## What Is an Entrypoint?

**The Problem:**
You have written a program with internal functions and data structures.
But the Solana runtime needs a single, well-defined place to start execution when a transaction invokes your program.
How do you declare the front door of your program so the validator knows where to begin?
Without an entrypoint, the runtime would have no idea which function to call.

**Definition:**
An **entrypoint** is the single function in a Solana program that the runtime calls when the program is invoked by a transaction.
It is the bridge between the outside world (the transaction) and your internal logic (the processor).
Every Solana program must declare exactly one entrypoint using the entrypoint! macro.

**The entrypoint signature:**
```rust
fn process_instruction(
    program_id: &Pubkey,      // The address of this deployed program
    accounts: &[AccountInfo], // All accounts passed in the transaction
    instruction_data: &[u8],  // Raw bytes containing the instruction
) -> ProgramResult
```

**Real-life analogy:**
An entrypoint is like the front door and reception desk of a doctor's office.
No matter what service you need — a checkup, a blood test, or a prescription — you always enter through the same front door.
The receptionist (entrypoint) takes your ID (program_id), your medical records (accounts), and your reason for visiting (instruction_data).
The receptionist does not perform the medical procedure themselves.
They simply validate your paperwork and route you to the correct department (processor).
If your paperwork is invalid, you are turned away before seeing the doctor.
The front door is the only way in.
There are no back doors or side entrances for patients.

**Tiny numeric example:**
```rust
use solana_program::entrypoint;

// WHY: This macro registers process_instruction as the official entrypoint.
// Without this, the runtime has no idea which function to call.
entrypoint!(process_instruction);

// WHY: This function must have exactly this signature.
// The runtime passes three pieces of context automatically.
pub fn process_instruction(
    program_id: &Pubkey,      // "You are at program 7XkY..."
    accounts: &[AccountInfo], // "Here are the 3 accounts you requested"
    instruction_data: &[u8],  // "The user wants instruction 1 with data [42]"
) -> ProgramResult {
    // WHY: The entrypoint's job is to parse and route.
    // Heavy logic belongs in the processor, not here.
    msg!("Entrypoint reached. Program: {}", program_id);
    msg!("Accounts provided: {}", accounts.len());
    msg!("Instruction data length: {}", instruction_data.len());

    // WHY: Route to the processor based on the first byte of data.
    match instruction_data.get(0) {
        Some(0) => process_initialize(program_id, accounts),
        Some(1) => process_increment(program_id, accounts),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}
```

**Common confusion:**
- **"The entrypoint is where all logic lives."**
  No. The entrypoint should be thin.
  Its job is parsing and routing.
  Business logic belongs in the processor functions.
- **"I can have multiple entrypoints."**
  No. A program can only declare one entrypoint.
  If you need multiple operations, use instruction data to route internally.
- **"The entrypoint can ignore the program_id."**
  You can, but it is useful for verifying that an account truly belongs to your program and not an impostor.
- **"Entrypoints are optional."**
  No. Without an entrypoint, your program is not callable by transactions.
  It is dead code on-chain.
- **"The entrypoint runs before transaction validation."**
  No. The runtime validates signatures, account permissions, and blockhash before calling your entrypoint.
- **"Entrypoints can return custom error types directly."**
  They must return ProgramResult, which is Result<(), ProgramError>.
  Custom errors must map to ProgramError::Custom(u32).
- **"Instruction_data is always structured."**
  It is always raw bytes.
  It is your responsibility to deserialize it into meaningful types like enums or structs.
- **"The entrypoint can allocate heap memory freely."**
  No. Programs have strict compute unit and heap limits enforced by the runtime.
- **"Entrypoints automatically log all parameters."**
  No. You must explicitly call msg!() to emit logs.

**Where it appears in our code:**
`src_web3/phase8/hello_world/src/lib.rs` — Declares entrypoint!(process_instruction) and logs a greeting.
`src_web3/phase9/counter/src/lib.rs` — Uses the entrypoint to route between Initialize and Increment instructions.
`src_web3/phase10/pda_demo/src/lib.rs` — Entrypoint routes to PDA creation and PDA increment logic.
