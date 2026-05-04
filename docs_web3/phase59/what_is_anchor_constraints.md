# What Is Anchor Constraints?

## The Problem

In raw Rust Solana programs, every account must be manually validated. Is the account initialized? Is the signer correct? Does the PDA match the expected seeds? Is the account mutable? Without systematic validation, programs are vulnerable to account injection attacks, unauthorized modifications, and deserialization failures. Raw validation code is repetitive, scattered across functions, and easy to forget.

## Definition

Anchor constraints are declarative validation rules specified inside the `#[account(...)]` attribute on fields within a `#[derive(Accounts)]` struct. They instruct Anchor to perform runtime checks before executing the instruction handler. Constraints cover initialization, mutability, ownership, relationships between accounts, PDA derivation, and token account validation.

## How It Works

1. **Define program**: The instruction handler is declared inside a `#[program]` module with a typed `Context<T>` parameter where `T` is a `#[derive(Accounts)]` struct.

2. **Derive accounts**: Each field in the accounts struct is annotated with its type (`Account<'info, T>`, `Signer<'info>`, `Program<'info, System>`, etc.), telling Anchor how to deserialize and validate it.

3. **Add constraints**: Inside `#[account(...)]`, you add rules like `init`, `mut`, `has_one`, `seeds`, `bump`, `constraint`, `close`. Anchor generates code that runs these checks in a deterministic order before your logic executes.

4. **Implement logic**: After constraint validation succeeds, the handler receives fully validated accounts. You never write `if !account.is_signer { return Err(...) }` because the framework already proved it.

5. **Generate IDL**: Constraints are documented in the IDL as part of account definitions, allowing clients to understand which accounts must be mutable or signers.

6. **Build client**: The TypeScript client reads the IDL and knows which accounts to mark as `isSigner` or `isWritable` in the transaction, matching the constraint declarations exactly.

## Real-life Analogy

Constraints are like airport security checkpoints. Before entering the gate (instruction logic), every passenger (account) must pass through specific checks: ID verification (`has_one`), ticket validation (`constraint`), baggage scan (`init` ensures nothing dangerous exists), and boarding pass mutability (`mut` allows changing seats). The checkpoint runs automatically; the gate agent only handles boarding logic for already-cleared passengers.

## Tiny Numeric Example

Consider a transfer instruction that requires the sender to own the token account.

**Raw Rust validation:**
```rust
if token_account.owner != *owner.key {
    return Err(ProgramError::InvalidAccountData);
}
if !owner.is_signer {
    return Err(ProgramError::MissingRequiredSignature);
}
```

**Anchor constraints:**
```rust
#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut, has_one = owner)]
    pub token_account: Account<'info, TokenAccount>,
    pub owner: Signer<'info>,
}
```

The Anchor version declares two validations in one line. The `mut` constraint ensures the account is writable. The `has_one = owner` constraint verifies that `token_account.owner == owner.key` and automatically returns `ErrorCode::ConstraintHasOne` if false. The `Signer<'info>` type ensures `owner.is_signer == true`. Three separate manual checks collapse into declarative attributes.

## Common Confusion

- `init` creates the account inside the instruction. No. `init` instructs Anchor to create the account via CPI to the System Program before the instruction handler runs. The account must still be passed in as an account parameter; it is created and initialized in the same transaction.

- `mut` on an `Account<'info, T>` means the inner data is mutable. No. `mut` means the Solana account's lamport balance or data can change. Without `mut`, even if you have an `Account<'info, T>`, Anchor marks it as read-only in the transaction and the runtime will reject writes.

- `seeds` alone proves the account is a PDA. No. `seeds` combined with `bump` proves the address is derived from those seeds. Without `bump`, Anchor cannot verify the address was correctly derived because multiple bumps might exist (though Anchor v1 requires bump for PDA validation).

- `has_one` checks the program ID. No. `has_one = target` checks that a field inside the account struct equals the public key of the target account. It does not verify the program that owns the account; that is handled by the `Account<'info, T>` type itself.

- `constraint` is for simple equality only. No. `constraint = expr` can contain any boolean Rust expression. You can call functions, perform arithmetic, or check complex relationships between multiple accounts.

- Constraints are checked in the order they are written. No. Anchor checks constraints in a fixed internal order: signer checks, ownership checks, PDA derivation, initialization, then custom constraints. You cannot reorder this via source code ordering.

## Key Properties

1. **Declarative security**: Security properties are expressed as data structure attributes rather than scattered imperative checks, making audit and review easier.

2. **Compile-time generation**: Constraints expand into optimized Rust code at compile time, with no runtime interpretation overhead.

3. **Composability**: Multiple constraints can be combined in a single `#[account(...)]` attribute, and they interact predictably (e.g., `init` with `seeds` creates a PDA, `mut` with `has_one` validates and permits writes).

4. **Automatic error mapping**: Each constraint failure maps to a specific `anchor_lang::error::ErrorCode` variant, providing informative error messages without manual error definitions.

5. **Runtime determinism**: Constraints are evaluated identically across all nodes in the network because they are part of the deterministic program execution, not off-chain assumptions.
