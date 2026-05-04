# Phase 65 Architecture: Drift Protocol Patterns

## Step 1: Design the Sub-Account Model

**Why:** Drift allows each user to create up to 20 sub-accounts. Without this design, every trade, deposit, and liquidation for a single wallet would hit one global account. A catastrophic trade in one market would wipe out unrelated positions. Sub-accounts isolate risk so that a liquidation in Account 3 does not touch the hedged positions in Account 7. This mirrors traditional brokerage segregation and is essential for any serious trader.

**Implementation:** Each user has a master `UserStats` account and a map of `User` accounts indexed by sub-account ID. The keeper bot must iterate across all sub-accounts for every wallet, computing margin independently. The API must expose routes that accept both `user` (wallet) and `subAccountId` parameters.

## Step 2: Implement the Keeper Incentive Structure

**Why:** Keepers are not altruistic. They burn SOL on transaction fees, RPC costs, and server infrastructure. If the protocol does not offer a liquidation reward that exceeds these costs by a reliable margin, keepers shut down. When keepers shut down, underwater positions fester, bad debt grows, and the exchange becomes insolvent. The incentive structure is therefore the liveness guarantee of the entire system.

**Implementation:** The protocol defines a liquidation fee percentage (e.g., 2.5%) and a minimum liquidation reward in USD terms. The keeper bot simulates every liquidation before submission, checking that `expected_reward > tx_cost + priority_fee + opportunity_cost`. The API exposes a `/liquidate` endpoint that returns the simulated profit before execution, letting keepers make informed bids.

## Step 3: Add JIT Auction for Liquidations

**Why:** Instant liquidation at a fixed discount is brutal for users. In a flash crash, the oracle price may lag or exaggerate the true market, and the user loses far more than necessary. JIT auctions introduce competition among liquidators, letting market forces determine the discount. The user recovers more collateral, the protocol absorbs less bad debt, and the system appears fairer. On Solana, the 400ms slot time makes a 5-10 slot auction feasible without exposing the protocol to prolonged risk.

**Implementation:** When the keeper detects a large liquidation (above a notional threshold), it does not immediately call `liquidatePerp`. Instead, it calls `beginLiquidation` to open an auction slot window. Bidders watch the auction account and submit `placeLiquidationBid` transactions. The keeper bot includes a bidding module that evaluates whether the auction discount is better than an instant liquidation, and submits bids accordingly. The API tracks active auctions and exposes them via `GET /auctions`.

## Step 4: Build the Cross-Collateral Margin Engine

**Why:** Traders hold portfolios, not single assets. Forcing conversion to one collateral token creates friction, tax events, and missed upside from holding appreciated assets. Cross collateral maximizes capital efficiency by letting a trader's entire portfolio back their trades. However, not all assets are equally safe. A memecoin cannot be treated like USDC. The engine must apply haircuts to reflect real volatility and liquidity.

**Implementation:** The margin engine maintains a whitelist of collateral assets and their weights (e.g., USDC = 1.0, SOL = 0.9, WBTC = 0.95). For each user sub-account, it computes `sum(deposit_amount * oracle_price * weight)` and divides by `sum(position_notional * maintenance_requirement)`. If the ratio is below 1.0, the account is flagged. The liquidation logic follows a fixed priority: seize USDC first, then other stables, then volatile assets by liquidity rank. The API exposes `GET /margin` to return the real-time calculation.

## Step 5: Create the Liquidation Bot

**Why:** Theory is irrelevant without execution. The bot is the physical manifestation of the keeper network. It must be fast, reliable, and profitable. A slow bot is a losing bot. A buggy bot drains SOL on failed transactions. A bot without simulation support is flying blind. Building the bot forces students to confront the real-world constraints of MEV, priority fees, RPC reliability, and transaction land rates.

**Implementation:** The bot is written in TypeScript using the official `@drift-labs/sdk`. It connects to a dedicated RPC with WebSocket support, subscribes to all `User` accounts, maintains an in-memory cache of margin ratios, detects underwater accounts, simulates liquidations, and submits transactions with dynamic priority fees. It logs every decision and outcome for later analysis. The bot runs as a daemon process and exposes health metrics on a local port.

## Step 6: Test on Devnet

**Why:** Mainnet liquidation bots handle real money. A single bug can cost thousands of dollars in gas or missed liquidations. Devnet provides a risk-free environment where students can observe real Drift program behavior, interact with devnet oracles, and verify that their bot logic matches the on-chain math. Testing on devnet also reveals RPC latency issues, transaction serialization bugs, and SDK version mismatches before real capital is at stake.

**Implementation:** The bot and API are configured to target Drift's devnet deployment (`dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH` on devnet). Students fund a devnet wallet with devnet SOL, create a devnet margin account, open a small leveraged position, and manually push the oracle price (via devnet manipulation or by waiting for volatility) to trigger liquidation. The bot should detect, simulate, and optionally execute the liquidation. All transactions are inspected on the Solana explorer to confirm correct instruction data and fee burns.
