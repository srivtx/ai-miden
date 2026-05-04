# Liquidation Bot

## The Problem

When a borrower's health factor drops below 1, their position is underwater and threatens the solvency of the entire lending pool. Waiting for manual intervention is too slow and risks bad debt accumulation. A Liquidation Bot automates the detection and liquidation of these positions before losses spread.

## Definition

A Liquidation Bot is an off-chain or hybrid service that continuously monitors borrower health factors in a lending protocol and automatically triggers liquidation transactions when a position becomes eligible. It repays a portion of the borrower's debt in exchange for a discounted portion of their collateral.

## How It Works

1. **Scan all borrower accounts**: The bot queries the protocol or an indexer to retrieve every open lending position.
2. **Fetch oracle prices**: The bot collects current market prices for all collateral and debt assets.
3. **Compute health factors**: For each borrower, the bot calculates collateral value times collateral factor, divided by borrowed value.
4. **Identify underwater positions**: Any health factor below 1.0 is flagged as liquidatable.
5. **Construct and send liquidation transaction**: The bot builds a transaction that repays some debt and seizes collateral plus a liquidation bonus.
6. **Profit and pool protection**: The bot earns the bonus as profit, and the protocol removes risky debt from its books.

## Real-life Analogy

Imagine a parking garage where cars are towed if the owner fails to pay fees. A tow truck company drives through the garage every hour checking license plates against an overdue list. When they find an overdue car, they tow it immediately. The tow company keeps the impound fee as profit, and the garage removes a liability from its space. The tow truck is the liquidation bot.

## Tiny Numeric Example with Liquidation Math

Bob deposits 5 ETH at 2,000 dollars per ETH.

- Collateral value: 5 * 2,000 = 10,000 dollars
- Collateral factor: 80 percent
- Borrowed: 7,000 USDC

Health factor:
- (10,000 * 0.80) / 7,000 = 8,000 / 7,000 = 1.14

ETH price drops to 1,200 dollars:
- New collateral value: 5 * 1,200 = 6,000 dollars
- New health factor: (6,000 * 0.80) / 7,000 = 4,800 / 7,000 = 0.6857

The bot detects health factor is below 1.0.

Liquidation parameters:
- Close factor: 50 percent
- Liquidation bonus: 10 percent

Bot repays 50 percent of debt:
- Repayment = 7,000 * 0.50 = 3,500 USDC

Collateral seized:
- Value to seize = 3,500 * 1.10 = 3,850 dollars
- ETH seized = 3,850 / 1,200 = 3.2083 ETH

Bot profit:
- Cost: 3,500 USDC
- Value received: 3,850 dollars of ETH
- Gross profit: 350 dollars

After liquidation:
- Bob's remaining collateral: 5 - 3.2083 = 1.7917 ETH
- Bob's remaining debt: 7,000 - 3,500 = 3,500 USDC
- New health factor: (1.7917 * 1,200 * 0.80) / 3,500 = 1,720 / 3,500 = 0.491

Because health factor is still below 1, the bot may liquidate again.

## Common Confusion

- No, the liquidation bot does not steal user funds; it follows protocol rules and pays off debt.
- No, any address can run a liquidation bot; it does not require special protocol permissions.
- No, the bot does not seize all collateral at once unless the close factor is 100 percent.
- No, liquidation does not make the borrower whole; it reduces the borrower's position but leaves them with remaining debt.
- No, bots do not need the borrower's permission to liquidate.
- No, running a liquidation bot is not risk-free; front-running and gas costs can erode profit.

## Key Properties

1. **Permissionless**: Anyone can run a liquidation bot.
2. **Time-sensitive**: Speed matters because multiple bots compete for the same opportunity.
3. **Profit-driven**: Bots operate because liquidation bonuses create arbitrage.
4. **Protective**: They keep the protocol solvent by removing bad debt quickly.
5. **Off-chain trigger**: They read on-chain state and send transactions to the chain.

## Where It Appears

Liquidation bots operate around Aave, Compound, MakerDAO, Solend, and every lending protocol with over-collateralized borrowing.
