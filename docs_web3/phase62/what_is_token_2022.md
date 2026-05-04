# What Is Token-2022?

## The Problem
Legacy SPL Token is too limited. It supports only basic minting, transferring, and freezing. If a project wants transfer fees, interest-bearing balances, confidential transfers, or on-chain metadata, it must deploy separate programs or rely on off-chain infrastructure. This fragments the ecosystem and increases security risk.

## Definition
Token-2022 is Solana's next-generation token program (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`). It preserves the same account model as SPL Token but adds an extension-based architecture. Each mint can opt into additional features without changing the core program.

## How It Works
1. **Create mint.** A developer initializes a new mint account through the Token-2022 program.
2. **Add extensions.** During creation, the developer selects which extensions to enable, such as transfer hooks or metadata pointers.
3. **Configure hooks.** If a transfer hook extension is enabled, the developer points the mint to an external validation program.
4. **Mint tokens.** The mint authority creates token accounts and issues tokens to users.
5. **Transfer with hooks.** Every transfer triggers the configured hook program, which can approve or reject the transaction.
6. **Manage metadata.** If a metadata pointer extension is enabled, the mint stores the address of an on-chain metadata account.

## Real-life Analogy
Imagine upgrading from a basic calculator to a smartphone. The calculator can only add and subtract. The smartphone still adds and subtracts, but you can install apps, take photos, and browse the web. Token-2022 is the smartphone, and extensions are the apps.

## Tiny Numeric Example
```typescript
import { TOKEN_2022_PROGRAM_ID, createMint } from "@solana/spl-token";
// WHY: Import the real Token-2022 program ID and helper.
const mint = await createMint(
    connection, payer, payer.publicKey, null, 9,
    undefined, undefined, TOKEN_2022_PROGRAM_ID
);
// WHY: Create a mint using Token-2022 program instead of legacy SPL Token.
```
The `9` means 1 token is represented as `1,000,000,000` base units.

## Common Confusion
- **No.** Token-2022 does not automatically replace existing SPL Token mints.
- **No.** Extensions are not mandatory; a plain Token-2022 mint behaves like legacy SPL Token.
- **No.** Token-2022 accounts are not smaller; extra extensions consume more rent.
- **No.** You cannot add most extensions after the mint is created.
- **No.** Not every wallet supports Token-2022 yet.
- **No.** Token-2022 does not change the underlying Solana account model or consensus rules.

## Key Properties
1. **Extension-based.** Features are modular and opt-in.
2. **Backward compatible layout.** Existing integrations work with plain Token-2022 mints.
3. **Transfer hooks.** Custom logic can execute on every transfer.
4. **Built-in metadata pointer.** Native on-chain metadata without external programs.
5. **Single program, multiple behaviors.** All extensions live inside `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`.
