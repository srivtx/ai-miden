## What Is a Bump?

**The Problem:**
When you hash seeds and a program_id together, the result might accidentally land ON the elliptic curve.
That would mean it has a private key.
That would defeat the entire purpose of a PDA.
How do you guarantee the derived address is off-curve and truly has no private key?
You need a mechanism to shift the hash output away from the curve.

**Definition:**
A **bump** is a single byte (u8) appended to the seeds during PDA derivation to shift the hash output off the elliptic curve.
The derivation algorithm starts with bump = 255 and decrements until it finds a hash that is off-curve.
The bump that succeeds is stored alongside the PDA and must be passed to invoke_signed as proof of derivation.

**Why the bump exists:**
- Ed25519 public keys are points on an elliptic curve
- A random hash output has a ~50% chance of being on-curve
- A PDA MUST be off-curve to guarantee no private key exists
- The bump is a brute-force search parameter that nudges the hash off-curve

**Real-life analogy:**
A bump is like adjusting the combination on a safe until it opens.
Imagine a safe with a dial that has 256 positions (0 to 255).
You try position 255 first.
If the safe does not open, you try 254, then 253, and so on.
Eventually, one position works.
That winning number is your bump.
Once found, you write it down because you need to use that exact same position every time you want to open the safe again.
The safe manufacturer (the Solana runtime) designed it so that exactly one position in the range works.
You must prove you know it by turning the dial to that number (passing the bump to invoke_signed).

**Tiny numeric example:**
```rust
let seeds: &[&[u8]] = &[b"counter", user_pubkey.as_ref()];
let program_id = &my_program;

// WHY: The algorithm tries bumps from 255 down to 0.
let mut bump = 255;
loop {
    let full_seeds = [seeds, &[&[bump]]].concat();
    let hash = sha256::hash(&full_seeds, program_id);

    // WHY: Check if the hash represents a valid ed25519 point.
    if !is_on_curve(hash) {
        // WHY: Found it. This hash is off-curve, so it has no private key.
        let pda = Pubkey::from(hash);
        return (pda, bump); // Example: (G7xK..., 255)
    }

    // WHY: Try the next lower bump.
    bump -= 1;
    if bump == 0 {
        panic!("No valid PDA found"); // Practically impossible
    }
}
```

**Bump statistics:**
- Approximately 50% of PDAs use bump = 255
- Approximately 25% use bump = 254
- Approximately 12.5% use bump = 253
- The distribution follows a geometric decay because each bump is an independent 50% trial

**Common confusion:**
- **"The bump is a secret."**
  No. The bump is public.
  Anyone can re-run find_program_address and discover it.
  Security comes from the program_id and seeds, not secrecy.
- **"I can guess any bump and it will work."**
  No. Only the specific bump that produces an off-curve hash is valid.
  Wrong bumps are rejected by the runtime.
- **"The bump is always 255."**
  Usually, but not guaranteed.
  You must use the actual bump returned by find_program_address.
- **"I can skip passing the bump to invoke_signed."**
  No. The runtime recalculates the PDA using the seeds and bump you provide.
  If the bump is wrong, the invocation fails.
- **"Bumps are unique per PDA."**
  Yes. For a given set of seeds and program_id, there is exactly one valid bump (in practice) that produces an off-curve address.
- **"I should hardcode bump = 255."**
  Do not. Always call find_program_address and use the returned bump.
  Hardcoding leads to runtime failures.
- **"The bump changes over time."**
  No. A PDA's bump is fixed forever because the seeds and program_id do not change.
- **"The bump is part of the address."**
  Not exactly. The bump is used during derivation but is not encoded in the address itself.
  You must pass it separately to invoke_signed.
- **"Finding a bump is computationally expensive."**
  No. It usually takes only one hash attempt because 255 works about 50% of the time.

**Where it appears in our code:**
`src_web3/phase10/pda_demo/src/lib.rs` — Calls Pubkey::find_program_address to get the bump, then passes it to invoke_signed to create the PDA account.
`src_web3/phase10/pda_api.ts` — Express API derives the PDA and bump client-side, then includes the bump in transaction instructions.
