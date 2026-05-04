# What Is Oracle Resolution?

## The Problem

A prediction market smart contract cannot observe the real world. It does not know whether it rained, who won an election, or if a stock price crossed a threshold. Without a reliable mechanism to bring external truth on-chain, shares can never be settled, and the market collapses into a speculative bubble with no exit.

## Definition

**Oracle resolution** is the process by which an off-chain, trusted entity (or a decentralized network of entities) reports the outcome of a real-world event to a smart contract. This report triggers the settlement phase, allowing winning shares to be redeemed and the market to close. The oracle is the bridge between objective reality and the deterministic logic of the blockchain.

## How It Works (6 Steps)

1. **Oracle Registration**: Before the market opens, the smart contract stores a list of authorized oracle public keys. Only signatures from these keys are accepted for resolution.
2. **Event Observation**: After the event concludes, the oracle independently verifies the outcome using reputable off-chain sources (for example, official election results, weather APIs, or sports league websites).
3. **Signed Attestation**: The oracle creates a signed message containing the market identifier and the winning outcome. The signature proves the message originated from the trusted oracle and has not been tampered with.
4. **On-chain Submission**: Anyone can submit the signed attestation to the smart contract. The contract verifies the signature against the stored oracle public keys.
5. **Dispute Period**: After the initial resolution, a timelock period begins (for example, 24 hours). During this window, participants can challenge the outcome by posting a bond. If no successful challenge occurs, the resolution is finalized.
6. **Finalization**: Once the dispute period expires, the market state changes to "Resolved." Winning shares become redeemable, and the oracle may receive a fee for its service.

## Real-life Analogy

Imagine a boxing match where the prize money is locked in a safe. The safe has multiple locks, and each judge holds one key. After the fight, the judges independently declare the winner. When enough judges agree and turn their keys, the safe opens and the winner collects the prize. If one judge disagrees, an arbitration period allows for a review before the prize is released.

## Tiny Numeric Example with Shares and Payouts

- A market asks, "Will the temperature exceed 30 degrees Celsius on July 1?"
- 1000 USDC is locked as collateral, generating 1000 YES and 1000 NO shares.
- On July 2, the trusted weather oracle checks the official weather station data.
- The recorded high was 32 degrees, so the oracle signs a message: "Market ID 42, Outcome = YES."
- The contract verifies the signature and sets the resolution to YES.
- A 24-hour dispute period begins. No one challenges the outcome.
- After finalization, holders of YES shares burn them to receive 1 USDC each. A holder of 50 YES shares receives 50 USDC.
- The oracle is paid a 5 USDC fee from the collateral pool for its service.

## Common Confusion

- No, the oracle is not a single all-powerful entity in all designs. Decentralized oracles use multiple reporters and consensus mechanisms to reduce trust.
- No, the oracle cannot change the outcome after finalization. Once the dispute period ends, the resolution is immutable.
- No, the oracle does not hold the collateral. The collateral remains in the smart contract; the oracle only provides the signal to unlock it.
- No, resolution does not happen automatically when the event occurs. Someone must submit the signed attestation on-chain and pay transaction fees.
- No, a wrong oracle report cannot be reversed instantly. It requires a successful dispute with evidence and a new resolution process.
- No, the oracle is not paid upfront in most designs. The fee is usually drawn from the market collateral after successful resolution to align incentives.

## Key Properties

1. **Trust Minimization**: Using cryptographic signatures and dispute windows reduces the need to trust any single party completely.
2. **Timeliness**: Oracles must report promptly after the event to prevent capital from being trapped indefinitely.
3. **Transparency**: The resolution data and signatures are stored on-chain, allowing anyone to audit the process.
4. **Economic Security**: Dispute bonds and oracle fees create financial skin-in-the-game, discouraging false reports.
5. **Decentralization Spectrum**: Oracle designs range from single trusted signers (fast, simple) to decentralized networks (robust, complex).

## Where It Appears

- **Chainlink**: Decentralized oracle network providing price feeds and custom data for smart contracts across multiple blockchains.
- **UMA**: Optimistic oracle that uses a dispute and verification game to resolve arbitrary off-chain events.
- **Augur**: Decentralized oracle where REP token holders report and dispute outcomes in a multi-round process.
- **Pyth Network**: High-frequency financial data oracle used for on-chain trading and prediction markets.
- **Polymarket**: Uses UMA's optimistic oracle to resolve real-world event markets with economic guarantees.
