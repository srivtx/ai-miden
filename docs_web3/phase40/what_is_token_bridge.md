# What Is a Token Bridge

## Why It Exists

Each blockchain has its own native assets, but users want to deploy capital where opportunities exist. A trader might want to use Bitcoin as collateral on Ethereum, or a gamer might want to spend Solana-based tokens in a Polygon game. Token bridges make this possible by locking an asset on its home chain and issuing a representative token on the destination chain. This preserves the asset's value while making it usable in foreign ecosystems.

## Definition

A token bridge is a cross-chain protocol that locks native tokens in a contract on one blockchain and mints equivalent wrapped tokens on another. When the wrapped tokens are burned, the native tokens are released, maintaining a one-to-one backing.

## Real-Life Analogy

Think of a coat check at a theater. You hand over your coat and receive a numbered ticket. The coat stays in the check room, but the ticket represents your ownership. Inside the theater, you can trade the ticket with a friend, and whoever holds it can claim the coat at the end of the show. The ticket is the wrapped token, the coat is the native asset, and the coat check attendant is the bridge contract.

## Tiny Numeric Example

A bridge connects Chain A and Chain B with a 1:1 backing requirement.

| Event | Chain A Native | Chain B Wrapped | Bridge Holdings | Notes |
|-------|---------------:|----------------:|-----------------|-------|
| Initial | 10,000 | 0 | 0 | Empty bridge |
| User locks 500 | 9,500 | 500 | 500 | Bridge holds native |
| User burns 200 | 9,500 | 300 | 300 | Bridge releases 200 |
| User locks 1,000 | 8,500 | 1,300 | 1,300 | Bridge holds more native |

The wrapped supply on Chain B always equals the native tokens held by the bridge on Chain A. If the bridge is hacked and drained, the wrapped tokens become unbacked.

## Common Confusion

- A token bridge is not a decentralized exchange; it does not swap assets, it locks and mints equivalents.
- Wrapped tokens are not stablecoins; their value tracks the native asset, not a fiat currency.
- Bridges do not create new supply; they move existing supply across chains by locking on one side and minting on the other.
- Not all bridges are two-way immediately; some require a waiting period or additional validator steps for withdrawals.
- Bridge fees are not network gas; they are protocol fees paid to validators, relayers, or liquidity providers.
- A wrapped token on Chain B is not interchangeable with the native token on Chain A; it must be bridged back to become native again.
- Bridge security is the weakest link; if the bridge contract is compromised, all wrapped tokens lose their backing simultaneously.

## Key Properties

## Where It Appears in Our Code

The token bridge is implemented in `src_web3/phase40/bridge_api.ts` through endpoints that lock native assets, mint wrapped equivalents with guardian attestation, burn wrapped tokens, and release the original collateral.
