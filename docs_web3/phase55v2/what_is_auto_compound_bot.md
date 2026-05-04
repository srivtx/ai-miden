# What is an Auto-Compound Bot?

## The Problem

Users forget to claim and restake their rewards. In a yield farm, rewards accrue continuously but only materialize as additional stake when the user manually claims and restakes. Most users do not interact with protocols daily. If a user stakes for a year without compounding, they earn simple interest instead of compound interest, leaving significant returns on the table. Phase 55 had no automation layer, so users were responsible for their own compounding schedule.

## Definition

An auto-compound bot is an off-chain service that monitors on-chain reward accrual and automatically triggers claim-and-restake transactions on behalf of users. The bot watches for when a user's pending rewards exceed a gas-efficiency threshold, constructs a transaction that claims rewards and immediately stakes them back into the pool, and submits the transaction to the network. The bot earns a small performance fee or protocol subsidy for this service.

## How It Works (6 Steps)

1. **Monitor Pools**: The bot runs a loop every N seconds, querying on-chain state for all active pools and users. It checks each user's `pending_reward` by calling the pool's view function or calculating from on-chain data.

2. **Filter Targets**: The bot maintains a whitelist of users who have opted into auto-compounding. For each whitelisted user, it compares pending rewards against a threshold (e.g., the reward must exceed 10x the transaction fee to be economically rational).

3. **Build Transaction**: For eligible users, the bot constructs a single transaction that: (a) calls the pool's `claim` instruction to transfer reward tokens to the user's wallet, and (b) calls the pool's `stake` instruction to transfer those same reward tokens back into the pool as additional stake.

4. **Sign and Submit**: The bot uses a dedicated payer account (funded by the protocol or by user delegation) to sign and submit the transaction. The user does not need to be online or approve each transaction individually because they pre-authorized the bot via a protocol-level delegation.

5. **Verify Settlement**: The bot polls the transaction signature until confirmation. If the transaction fails (e.g., due to network congestion or state changes between simulation and submission), the bot retries with exponential backoff.

6. **Charge Fee**: Upon successful compounding, the bot deducts a small percentage (e.g., 1-3%) of the compounded rewards as a service fee. This fee is transferred to the bot operator's treasury or used to buy back and burn the protocol token.

## Real-life Analogy

Imagine a dividend reinvestment plan (DRIP) at a brokerage. Instead of receiving a cash dividend check in the mail and manually logging in to buy more shares, the brokerage automatically reinvests your dividends into additional shares the moment they are paid. You do not call your broker. You do not sign any paperwork for each dividend. The service runs continuously, and you wake up with more shares than you had yesterday.

## Tiny Numeric Example with Actual Token-2022 Code

```typescript
// Auto-compounder monitoring loop
import { AnchorProvider, Program, Wallet } from "@coral-xyz/anchor";
import { Connection, PublicKey } from "@solana/web3.js";

const MIN_REWARD_THRESHOLD = 1_000_000; // WHY: 1 token with 6 decimals - must exceed tx cost
const COMPOUND_FEE_BPS = 100;           // WHY: 1% fee in basis points (100 = 1%)

async function checkAndCompound(
    program: Program<any>,
    userPubkey: PublicKey,
    poolPubkey: PublicKey,
    botKeypair: any
) {
    // WHY: Fetch on-chain user info to calculate pending rewards
    const userInfo = await program.account.userInfo.fetch(
        deriveUserInfoPDA(userPubkey, poolPubkey) // WHY: PDA derived from seeds
    );
    
    // WHY: Fetch pool state to get current reward_per_share
    const pool = await program.account.pool.fetch(poolPubkey);
    
    // WHY: Calculate pending rewards using same math as on-chain program
    const staked = userInfo.stakedAmount.toNumber();
    const rps = pool.rewardPerShare;
    const debt = userInfo.rewardDebt;
    const pending = (staked * rps) - debt; // WHY: Same formula as smart contract
    
    // WHY: Only compound if reward exceeds gas threshold
    if (pending > MIN_REWARD_THRESHOLD) {
        const fee = pending * COMPOUND_FEE_BPS / 10_000; // WHY: Calculate bot fee
        const compoundAmount = pending - fee;            // WHY: User receives net amount
        
        // WHY: Build compound transaction (claim + restake in one tx)
        const tx = await program.methods
            .compound(new anchor.BN(compoundAmount))
            .accounts({
                pool: poolPubkey,
                user: userPubkey,
                userStakeAccount: deriveStakeATA(userPubkey),
                rewardVault: pool.rewardVault,
                tokenProgram: TOKEN_2022_PROGRAM_ID,
            })
            .transaction(); // WHY: Build unsigned transaction
            
        // WHY: Bot pays for transaction to keep user experience frictionless
        const signature = await program.provider.sendAndConfirm(tx, [botKeypair]);
        console.log(`Compounded ${compoundAmount} for ${userPubkey.toBase58()}: ${signature}`);
    }
}
```

## Common Confusion (6 Bullets with "No.")

- No, the auto-compound bot is not a smart contract. It is an off-chain service. The bot cannot force a transaction without a valid signer. It relies on either protocol subsidized fees or user-delegated signing authority.

- No, auto-compounding does not guarantee higher returns. It guarantees more frequent compounding, but if transaction fees exceed the compounded amount, the user loses money. The bot must enforce a minimum threshold.

- No, the bot does not need the user's private key. The bot uses its own payer account for transaction fees, and the pool program verifies that the user authorized auto-compounding through an on-chain delegation account or whitelisted bot registry.

- No, compounding every block is not optimal. Solana block times are approximately 400ms. Compounding 216,000 times per day would cost more in fees than it generates in rewards for most users. The optimal interval depends on yield rate, stake size, and transaction cost.

- No, the bot cannot steal user funds. The pool program's instructions enforce that staked tokens can only be returned to the original user's wallet. The bot can only trigger claims and restakes; it cannot redirect funds to its own wallet unless the user explicitly opts into a fee structure that the program enforces.

- No, one failed compound does not break the system. The bot uses idempotent logic. If a compound transaction fails, the user's rewards remain unclaimed and continue accruing. The bot will retry on the next monitoring cycle with no loss of funds.

## Key Properties (5)

1. **Economic Rationality**: The bot only executes when the gas cost is a small fraction of the reward. This protects users from negative-value compounding where fees exceed gains.

2. **Permissionless Execution**: Anyone can run a compounding bot. Protocols do not need to operate their own infrastructure. Multiple competing bots create redundancy and prevent centralization of this service layer.

3. **Composable with Boost NFTs**: The bot respects on-chain multipliers. If a user holds a boost NFT that increases their reward rate by 2x, the bot automatically compounds the larger amount because it reads live on-chain state before building transactions.

4. **Non-Custodial**: The bot never holds user funds. At no point does the user's token balance reside in a bot-controlled account. The bot only initiates program instructions that the protocol's smart contracts validate and execute.

5. **Measurable Performance**: Bot operators can prove their value. By comparing a user's stake growth with and without compounding, the exact additional yield attributable to the bot is calculable from on-chain historical data.
