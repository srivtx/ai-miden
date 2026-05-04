# Architecture and Build Instructions

This document explains how to rebuild the Phase 51 DEX from an empty directory. Do not just copy the files. Read the WHY in each step so you understand the purpose of every layer.

## Prerequisites

Before you begin, ensure you have the following installed and configured on your machine:

1. **Rust**: The Solana programs are written in Rust. Install it from rustup.rs.
2. **Solana CLI**: You need `solana-keygen` and `solana program deploy`. Install from docs.solana.com.
3. **Node.js and TypeScript**: The API server is written in TypeScript. Install Node.js, then run `npm install -g typescript ts-node`.
4. **A Solana Wallet**: Generate a devnet wallet with `solana-keygen new --outfile ~/.config/solana/id.json` and airdrop yourself SOL with `solana airdrop 2`.
5. **Basic Knowledge**: You should understand public/private keys, accounts, and the concept of a transaction on Solana.

## Step 1: Design the AMM Pool

**WHY we do it**: Every DEX needs a place where tokens actually trade. The AMM pool is the foundational primitive. Without it, there is no price discovery and no liquidity.

**WHAT we build**: A Solana program that owns token accounts for two assets and enforces the constant product formula `x * y = k`.

**Implementation details**:
- Define a `PoolState` account to store token mints, vault addresses, total liquidity shares, and the fee numerator.
- Define a `LiquidityProvider` account to track how many shares each user owns.
- Implement `initialize_pool` to create the pool state and associated token accounts.
- Implement `deposit_liquidity` to accept both tokens, mint LP shares proportionally, and update reserves.
- Implement `swap` to take one token, calculate the output using the constant product formula minus fees, and transfer the output token.
- Implement `withdraw_liquidity` to burn LP shares and return the proportional reserves.

**WHAT could go wrong**:
- **Integer overflow**: Solana Rust does not panic on overflow by default in older program versions. Always use `checked_mul`, `checked_div`, and `checked_sub`.
- **Rounding errors**: If you round down the output token amount too aggressively, traders receive zero on small swaps. Always add a minimum output check.
- **Reentrancy**: Although Solana's parallel execution model reduces reentrancy risk compared to Ethereum, improperly sequenced account updates can still lead to inconsistent state.
- **Authority confusion**: If the pool's token account authority is not the program-derived address (PDA), anyone could drain the vaults.

## Step 2: Implement Swap Logic

**WHY we do it**: The swap is the only function traders care about. It must be mathematically correct, fair, and resistant to manipulation.

**WHAT we build**: The core invariant logic inside the `swap` instruction.

**Implementation details**:
- Fetch the current reserves `x` and `y` from the token vault accounts.
- Calculate the new reserve after the input is added: `x' = x + amount_in`.
- Calculate the new output reserve: `y' = k / x'`.
- Calculate the output amount: `amount_out = y - y'`.
- Apply the fee by reducing `amount_in` before it enters the formula, or by taking the fee from the output. We choose to take it from the input so `k` only grows over time, benefiting LPs.
- Ensure `amount_out >= min_amount_out` to protect against frontrunning and slippage.

**WHAT could go wrong**:
- **Frontrunning**: A malicious actor sees your transaction in the mempool and submits a trade before you to move the price against you. The `min_amount_out` check mitigates this by reverting your transaction if the price shifts too far.
- **Price manipulation in shallow pools**: If a pool has very little liquidity, a small trade moves the price massively. The router should warn users or split the trade.
- **Fee miscalculation**: If the fee is taken after the output is calculated instead of before, the invariant breaks and LPs lose money.

## Step 3: Add Limit Order Book

**WHY we do it**: AMMs offer immediacy but not precision. Traders need a way to buy or sell at a specific price without babysitting the chain. Limit orders fill this gap.

**WHAT we build**: A Solana program that stores orders, locks collateral, and allows execution when a price threshold is crossed.

**Implementation details**:
- Define an `Order` account containing the owner, input mint, output mint, input amount, limit price, and a boolean `is_active`.
- Implement `place_order` to transfer the input tokens from the user to a program-owned escrow account and create the `Order` account.
- Implement `cancel_order` to verify the caller is the owner, refund the escrowed tokens, and close the order account.
- Implement `execute_order` to check if the current AMM pool price satisfies the limit condition, then perform the transfer and close the order.

**WHAT could go wrong**:
- **Keeper centralization**: If only one bot can call `execute_order`, that bot can censor users. Design the permission so anyone can trigger execution, perhaps with a small incentive.
- **State bloat**: Every order is a separate account. If users place millions of orders, validators store too much data. Charge rent or require a deposit that is refunded on closure.
- **Stale price execution**: If the price crosses the limit for only one block and then reverses, the keeper might miss it. Encourage keepers to monitor continuously.

## Step 4: Build the Router

**WHY we do it**: Liquidity is fragmented. A trader swapping A for C should not have to know whether the best path is direct or through B. The router abstracts this complexity.

**WHAT we build**: Off-chain pathfinding logic inside the Express API.

**Implementation details**:
- Maintain an in-memory graph of pools. Each token is a node; each pool is a weighted edge.
- For a given swap request, run a shortest-path algorithm (like Dijkstra) where edge weight is the inverse of the expected output.
- Consider both direct pools and multi-hop routes up to a maximum depth (e.g., 3 hops) to keep computation fast.
- Return the best path, the expected output, and the minimum output after slippage tolerance.

**WHAT could go wrong**:
- **Stale graph data**: The router's in-memory graph might not reflect a recent pool deposit or withdrawal. Refresh pool data frequently or query it on-demand.
- **Computation explosion**: If you allow unlimited hops, pathfinding becomes too slow. Cap the depth and prune low-liquidity edges.
- **Race condition**: The router finds a great path, but by the time the transaction lands, another trade changes the pool reserves. Always use slippage protection.

## Step 5: Wire Everything Together

**WHY we do it**: Individual programs are useless if users cannot reach them through a single, consistent interface. The API is the product.

**WHAT we build**: An Express server on port 3055 that exposes REST endpoints for every operation.

**Implementation details**:
- Initialize a Solana connection to devnet.
- Load the deployer's keypair to pay for and sign transactions.
- Load the program IDs for both the AMM and limit order programs.
- Create routes that parse request bodies, build transactions, send them to the cluster, and return the signatures.
- Handle errors gracefully, returning 400 for bad input and 500 for chain failures.

**WHAT could go wrong**:
- **Keypair exposure**: If the server's private key is hardcoded or logged, attackers can drain the deployer's wallet. Use environment variables and never log secrets.
- **Rate limiting**: A public API can be spammed. Add basic rate limiting or run it behind a reverse proxy.
- **CORS misconfiguration**: If the API is meant to serve a frontend, improper CORS headers will block browser requests.

## Step 6: Test and Deploy

**WHY we do it**: Code that has not been executed is just a theory. You must prove the math works, the accounts are correct, and the integration is seamless.

**WHAT we build**: A deployment script and a manual testing checklist.

**Implementation details**:
- Write `deploy.sh` to build both Rust programs with `cargo build-bpf`, extract the `.so` binaries, and deploy them to devnet using `solana program deploy`.
- Record the deployed program IDs and update the API's configuration.
- Test sequence:
  1. Initialize a pool.
  2. Deposit liquidity.
  3. Perform a swap and verify the output matches the constant product math.
  4. Place a limit order.
  5. Execute the limit order after moving the pool price.
  6. Query the router for a best path.

**WHAT could go wrong**:
- **Devnet instability**: Devnet is a test network. It can be slow or reset. If deployment fails, retry or switch to localnet.
- **Rent exemption**: Solana accounts must hold enough lamports to be rent-exempt. If your initialization transaction fails with an insufficient funds error, you may need to allocate more lamports.
- **Program size limit**: Solana programs have a maximum deployed size. If your binary is too large, you may need to optimize or split logic across multiple programs.
