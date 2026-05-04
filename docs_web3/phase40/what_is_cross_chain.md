# What Is Cross-Chain

## Why It Exists

Blockchains are powerful but isolated. A user who owns Bitcoin cannot directly spend it on an Ethereum smart contract. A decentralized application on Solana cannot read the state of a Polygon contract. This fragmentation forces users to manage multiple wallets, bridges, and exchanges, creating friction and security risks. Cross-chain technology solves this by enabling communication, asset transfer, and state sharing between distinct blockchains, turning a collection of islands into a connected archipelago.

## Definition

Cross-chain refers to any technology, protocol, or mechanism that allows independent blockchains to exchange data, verify state, or transfer assets without relying on a centralized intermediary.

## Real-Life Analogy

Imagine two countries with different currencies and no direct banking relationship. A tourist cannot spend their home currency in the foreign country without an exchange. A cross-chain bridge is like an international bank that holds deposits in both countries. The tourist deposits money at home, the bank issues foreign currency abroad, and both ledgers stay synchronized. When the tourist returns, they reverse the process. Cross-chain technology is that international bank, but run by code and validator consensus instead of tellers.

## Tiny Numeric Example

A user wants to move 5 ETH from Ethereum to Solana.

| Step | Action | Ethereum State | Solana State | Bridge Holds |
|------|--------|----------------|--------------|--------------|
| 1 | User sends 5 ETH to bridge | User: -5 ETH | No change | Ethereum: +5 ETH |
| 2 | Bridge validators confirm | Confirmed | No change | Ethereum: +5 ETH |
| 3 | Bridge mints wrapped token | Confirmed | User: +5 wETH | Ethereum: +5 ETH |
| 4 | User burns wETH on Solana | Confirmed | User: 0 wETH | Ethereum: +5 ETH |
| 5 | Bridge releases ETH on Ethereum | User: +5 ETH | User: 0 wETH | Ethereum: 0 ETH |

The user's balance is preserved across chains, but the asset form changes from native ETH to a wrapped representation and back.

## Common Confusion

- Cross-chain is not the same as multi-chain; multi-chain means a dApp exists on several chains independently, while cross-chain means the chains interact.
- Wrapped tokens are not identical to native tokens; they carry bridge risk and may trade at slight discounts.
- Cross-chain does not mean instant; validators must observe and confirm transactions, which can take minutes.
- Bridges are not trustless by default; many rely on a federation of validators that could collude.
- Atomic swaps do not require a bridge; they use hash time-locked contracts to exchange assets directly between two parties.
- Cross-chain messaging is not limited to tokens; it can include arbitrary data, governance votes, and oracle proofs.
- Security on one chain does not protect the other; a hack of the bridge contract can drain funds on all connected chains.

## Key Properties

## Where It Appears in Our Code

Cross-chain concepts are modeled in `src_web3/phase40/bridge_api.ts` where the `/lock` endpoint records a deposit on the source chain, the `/mint` endpoint issues a wrapped representation on the destination chain, and the `/release` endpoint burns the wrapped token to unlock the original asset.
