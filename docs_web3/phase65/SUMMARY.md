# Phase 65 Summary: Drift Protocol Patterns

## What We Learned

This phase dissected the architecture of Drift, the leading perpetual DEX on Solana. Students studied three core mechanisms that allow Drift to process billions in monthly volume while remaining fully on-chain and non-custodial.

## Core Concepts

### Keeper Network

We learned that smart contracts are reactive, not proactive. They cannot wake themselves. Keeper networks fill this gap by providing a decentralized, permissionless layer of off-chain bots that monitor margin health and execute liquidations. These bots compete in a winner-takes-all race, spending their own gas for a chance at protocol-defined liquidation fees. The economic incentive ensures liveness: as long as there is profit in liquidating, someone will show up to do it.

### JIT Auction

Standard liquidations force the protocol to accept a fixed oracle discount, which can destroy user equity during volatility. JIT auctions solve this by inserting a 5-10 slot competitive bidding window into the liquidation flow. Third-party liquidators bid to take over the position, and the best bid wins. This on-chain price discovery reduces bad debt, preserves more collateral for the liquidated user, and ensures the protocol does not become a forced seller at the worst possible moment.

### Cross Collateral

Isolated margin chains traders to a single collateral asset, wasting capital and concentrating risk. Cross collateral allows a unified margin basket of multiple whitelisted assets, each weighted by a protocol-defined haircut. All assets jointly back all positions. The margin engine monitors total weighted collateral against total maintenance requirement, and liquidations follow a fixed asset-priority seizure order. The result is higher capital efficiency and diversified collateral risk.

## Architecture Takeaways

1. **Sub-account model.** Drift isolates risk across multiple sub-accounts per user, preventing a single bad trade from wiping out an entire wallet.
2. **Keeper incentives.** Liquidation fees must exceed gas costs by a healthy margin, or rational keepers disappear and protocol solvency decays.
3. **Auction speed.** JIT auctions resolve in seconds because Solana's 400ms slot time makes on-chain bidding practical. This design would be impossible on slower chains.
4. **Margin weights.** Cross collateral without haircuts is dangerous. Governance must continuously update weights as market conditions change.
5. **Bot infrastructure.** Real production keepers require WebSocket streaming, priority-fee optimization, Jito bundle support, and redundant RPC endpoints.

## Connection to Miden

While Drift runs on Solana's account model, the lessons apply directly to Miden's UTXO-based rollup:

- **Off-chain execution.** Keepers on Miden will operate similarly: monitoring on-chain state (or in Miden's case, off-chain notes), detecting triggers, and submitting transactions.
- **JIT logic.** Miden's private accounts can still expose liquidation hints or zero-knowledge proofs of underwater status, enabling competitive auctions without full state visibility.
- **Cross collateral.** A Miden account can hold multiple asset notes. A smart contract can define weighted aggregation rules in Miden VM, producing the same capital-efficiency benefits with native privacy.

## Next Steps

Phase 66 will extend these patterns by building a complete liquidation bot with Jito bundle support, priority-fee strategies, and sub-account iteration. Students will deploy to devnet and measure keeper profitability under simulated volatility.
