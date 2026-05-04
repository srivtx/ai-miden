# What Is Wormhole

## Why It Exists

Moving assets between blockchains used to require centralized exchanges, which introduced custodial risk, KYC delays, and withdrawal limits. Developers needed a decentralized way to pass messages and tokens across chains without trusting a single company. Wormhole is a generic messaging protocol that connects multiple blockchains through a network of guardian nodes. It enables not just token transfers but also cross-chain governance, NFT bridging, and data propagation.

## Definition

Wormhole is a cross-chain messaging protocol that uses a decentralized guardian network to observe events on one chain and attest to them on another. It supports token transfers, arbitrary message passing, and NFT bridging across multiple Layer-1 and Layer-2 networks.

## Real-Life Analogy

Imagine a postal system run by a council of independent couriers. When you send a letter from City A, every courier watches the post office log. Once a majority agrees the letter was sent, one courier delivers a certified copy to City B. The cities do not talk to each other directly; they trust the courier council because no single courier can forge a message without being caught by the others. Wormhole is that courier council, but for blockchains.

## Tiny Numeric Example

A user bridges 1,000 USDC from Ethereum to Solana via Wormhole.

| Step | Actor | Action | Result |
|------|-------|--------|--------|
| 1 | User | Lock 1,000 USDC in Wormhole contract on Ethereum | Ethereum contract holds 1,000 USDC |
| 2 | Guardians | Observe the lock event and sign an attestation | 13 of 19 guardians produce signatures |
| 3 | Relayer | Submit the signed attestation to Solana | Solana verifies the guardian signatures |
| 4 | Wormhole Solana | Mint 1,000 wormhole-USDC to user | User receives wrapped token on Solana |

The guardians act as decentralized notaries. The relayer is a permissionless actor who pays gas to move the message. The user never trusts a single entity.

## Common Confusion

- Wormhole is not a blockchain itself; it is a protocol that sits between blockchains.
- Guardians are not miners; they do not produce blocks, they only observe and attest to events.
- Wormhole tokens are not native assets; they are wrapped representations backed by locked collateral on the source chain.
- The protocol is not free; users pay gas on both the source and destination chains, and relayers may charge fees.
- A guardian set can be upgraded; the list of trusted nodes is not permanently fixed, though changes require governance.
- Wormhole supports more than tokens; developers can pass arbitrary payloads to trigger contract calls across chains.
- Past exploits do not mean the concept is broken; they highlight the importance of rigorous guardian security and contract auditing.

## Key Properties

## Where It Appears in Our Code

Wormhole-style attestation is simulated in `src_web3/phase40/bridge_api.ts` where the `/attest` endpoint collects mock guardian signatures before allowing a mint, and the `/mint` endpoint checks that a threshold of attestations has been reached.
