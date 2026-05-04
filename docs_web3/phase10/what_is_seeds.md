## What Are Seeds?

**The Problem:**
You need a way to generate unique, deterministic addresses for different users, different assets, or different purposes within your program.
How do you parametrize PDA derivation so that Alice gets one address, Bob gets another, and a global config gets yet another?
All of these must be derived predictably from public inputs.
Without seeds, every PDA would look the same and collide.

**Definition:**
**Seeds** are arbitrary byte arrays used as inputs to PDA derivation.
They act as identifiers that make each PDA unique.
Common seed patterns include user public keys, string literals (like counter or metadata), token mint addresses, and numeric identifiers.
The combination of seeds and program_id determines the final PDA.

**Common seed patterns:**
- [user_pubkey, b"counter"] — Per-user counter
- [mint_pubkey, b"metadata"] — Per-token metadata
- [b"global_config"] — Global program configuration (one per program)
- [user_pubkey, mint_pubkey, b"token_account"] — Per-user, per-token account

**Real-life analogy:**
Seeds are like the address fields on a mailing label.
A post office (program) can deliver to many PO Boxes (PDAs), but each box must have a unique address.
The address label contains multiple fields: recipient name (user pubkey), department code (string literal like counter), and building number (program_id).
Two people named John Smith will not receive each other's mail because their full addresses include apartment numbers and zip codes.
Similarly, two users will never collide on the same PDA because their public keys are unique.
A global config PDA is like the post office's main administration box.
It has no recipient name, just a department code like global_config.

**Tiny numeric example:**
```rust
let program_id = my_program;
let alice = Pubkey::from_str("Alice111111111111111111111111111111111111111")?;
let bob   = Pubkey::from_str("Bob11111111111111111111111111111111111111111")?;

// WHY: Alice's counter PDA uses her pubkey as the primary seed.
let (alice_pda, _) = Pubkey::find_program_address(
    &[alice.as_ref(), b"counter"],
    &program_id
);
// Result: G7xK... (unique to Alice)

// WHY: Bob's counter PDA uses his pubkey, producing a different address.
let (bob_pda, _) = Pubkey::find_program_address(
    &[bob.as_ref(), b"counter"],
    &program_id
);
// Result: H8yL... (unique to Bob)

// WHY: Global config has no user key, just a fixed string.
let (global_pda, _) = Pubkey::find_program_address(
    &[b"global_config"],
    &program_id
);
// Result: J9zM... (one per program)
```

**Seed composition rules:**
- Seeds must be byte arrays (&[u8])
- You can use 1 to 16 seeds per derivation
- Total seed length must not exceed 32 bytes per seed in some contexts
- Public keys are 32 bytes and make excellent unique seeds

**Common confusion:**
- **"Seeds are secret passwords."**
  No. Seeds are public inputs.
  Anyone can see them in the transaction.
  Security comes from program_id enforcement, not secrecy.
- **"Any seed combination works."**
  Yes, but you must use the exact same seeds when deriving and when invoking.
  A single byte difference produces a completely different PDA.
- **"Seeds must be strings."**
  No. Seeds are raw bytes.
  Strings are just one convenient way to produce deterministic bytes.
- **"I need a user's private key as a seed."**
  Never. Seeds are public.
  Using a private key as a seed would expose it on-chain forever.
- **"More seeds make the PDA more secure."**
  Not directly.
  More seeds increase uniqueness and organization, but security comes from the program logic, not seed complexity.
- **"Seeds can be dynamic at runtime."**
  The seeds used in invoke_signed must be reconstructible from the transaction context.
  You cannot use external oracle data as a seed without passing it in the transaction.
- **"All seeds must be the same length."**
  No. Seeds can be different lengths.
  The hash function handles variable-length inputs.
- **"Seeds are optional for PDA derivation."**
  No. You must provide at least one seed.
  Without seeds, the PDA would be predictable and collide easily.
- **"I can use timestamps as seeds."**
  You can, but then the PDA is not reproducible later.
  Use deterministic inputs only.

**Where it appears in our code:**
`src_web3/phase10/pda_demo/src/lib.rs` — Uses [user.key.as_ref(), b"counter"] as seeds to derive a per-user PDA.
`src_web3/phase10/pda_api.ts` — Express API demonstrates deriving PDAs with different seed patterns for users and global state.
