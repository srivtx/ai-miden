# What is Token-2022 Rewards?

## The Problem

SPL Token cannot do transfer hooks. The original SPL Token program on Solana is immutable and lacks the ability to execute custom logic during token transfers. This means you cannot automatically distribute rewards, apply fees, or enforce restrictions at the moment tokens move between accounts. Phase 55 used stubbed reward calculations because there was no hook mechanism to trigger reward distribution on every stake or unstake action.

## Definition

Token-2022 is an extended token program on Solana that introduces transfer hooks, confidential transfers, interest-bearing tokens, and other extensions. A transfer hook is a CPI (Cross-Program Invocation) call from the token program to a custom program whenever tokens are transferred, enabling automatic reward distribution, fee collection, or access control at the protocol level.

## How It Works (6 Steps)

1. **Create Mint with Extension**: The protocol initializes a Token-2022 mint with the `TransferHook` extension enabled, specifying the program ID that will receive hook calls.

2. **Initialize Hook Program**: The protocol deploys a separate program that implements the `Execute` instruction, which the Token-2022 program will CPI into on every transfer.

3. **Stake Tokens**: When a user stakes tokens into the farm, the farm program initiates a Token-2022 transfer from the user's wallet to the farm vault. The Token-2022 program CPIs into the hook program.

4. **Hook Updates Rewards**: The hook program receives the transfer context and updates the reward-per-share accumulator for the farm pool, ensuring rewards are calculated from the exact moment of deposit.

5. **Claim Rewards**: When claiming, the farm program calculates pending rewards using the reward-per-share accumulator and initiates a real Token-2022 transfer from the reward vault to the user's wallet.

6. **Unstake with Hook**: On unstake, the reverse transfer occurs (farm vault to user wallet), and the hook again updates state, ensuring rewards are paid up to the exact second of withdrawal.

## Real-life Analogy

Imagine a smart parking garage where every time you drive in or out, the gate automatically notifies the billing system. With the old system (SPL Token), the gate just opens and closes with no record sent to billing. With Token-2022, the gate is connected to the billing computer by a direct phone line (the transfer hook), so every entry and exit instantly updates your parking bill with perfect accuracy.

## Tiny Numeric Example with Actual Token-2022 Code

```rust
// Create a Token-2022 mint with transfer hook extension
use anchor_spl::token_2022::Token2022;
use spl_token_2022::extension::transfer_hook::instruction::initialize;

// Reward rate: 100 reward tokens per staked token per second
let reward_rate: u64 = 100;

// User A stakes 1,000 tokens at time T=0
// User B stakes 2,000 tokens at time T=10
// At T=20, total rewards distributed = reward_rate * 20 = 2,000
// Reward per share at T=20 = 2,000 / 3,000 = 0.666666...
// Stored as u128: 666_666_666_666_666_666 (with 1e18 precision)

// When User A claims at T=20:
// User A reward debt = 1,000 * 0 = 0 (staked at start)
// User A earned = 1,000 * 0.666666... - 0 = 666.666... reward tokens
// Farm program initiates real CPI transfer of 666 reward tokens

// The CPI call looks like this:
let cpi_accounts = TransferChecked {
    from: ctx.accounts.reward_vault.to_account_info(),      // WHY: Source of reward tokens
    mint: ctx.accounts.reward_mint.to_account_info(),       // WHY: Reward token mint for decimals check
    to: ctx.accounts.user_reward_account.to_account_info(), // WHY: Destination is user's reward ATA
    authority: ctx.accounts.farm_authority.to_account_info(), // WHY: PDA must sign as vault authority
};
let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: Token-2022 program ID
let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);       // WHY: Build CPI context for cross-program call
anchor_spl::token_2022::transfer_checked(cpi_ctx, reward_amount, 6)?; // WHY: Execute real transfer with 6 decimals
```

## Common Confusion (6 Bullets with "No.")

- No, Token-2022 is not a replacement for SPL Token. Both programs exist on mainnet and devnet. Token-2022 is an additional program with more features, not a drop-in replacement that makes SPL Token obsolete.

- No, transfer hooks do not make transactions slower by a meaningful amount. The CPI call adds approximately 2,000 compute units, which is less than 1% of the 1.4 million compute unit budget per transaction.

- No, you cannot add a transfer hook to an existing SPL Token mint. The extension must be configured at mint creation time. You cannot retroactively upgrade a standard SPL Token to Token-2022 functionality.

- No, the hook program cannot reject a transfer after it has occurred. The hook executes atomically within the same transaction. If the hook fails, the entire transaction (including the transfer) is reverted. There is no race condition.

- No, Token-2022 tokens are not incompatible with standard wallets. Phantom, Solflare, and other major wallets support Token-2022 accounts. The user experience is identical to SPL Token from the user's perspective.

- No, you do not need to use confidential transfers to use transfer hooks. Extensions are modular. You can enable only the transfer hook extension without enabling confidential transfers, interest-bearing, or any other extension.

## Key Properties (5)

1. **Atomic Execution**: The transfer and hook execute in the same transaction. Either both succeed or both fail. There is no intermediate state where tokens moved but hooks did not fire.

2. **Composable Extensions**: You can combine transfer hooks with other Token-2022 extensions like metadata (on-chain name/symbol), permanent delegate, or interest-bearing tokens without writing additional code.

3. **Program-Driven Authority**: The hook program can enforce that only specific programs (like your farm) can trigger transfers, preventing front-running or unauthorized reward claims through direct token transfers.

4. **Deterministic Cost**: Hook CPI costs are predictable and metered. You know exactly how many compute units a transfer hook adds, making gas estimation reliable for production deployments.

5. **Backward-Compatible Tooling**: Anchor's `anchor-spl` crate supports Token-2022 through the `token_2022` module. You use `Token2022` instead of `Token` in your account validations, and the rest of the Anchor workflow remains identical.
