# What Is Wormhole

**The Problem:**

Moving assets between blockchains used to require centralized exchanges, which introduced custodial risk, KYC delays, and withdrawal limits. Developers needed a decentralized way to pass messages and tokens across chains without trusting a single company. Wormhole is a generic messaging protocol that connects multiple blockchains through a network of guardian nodes. It enables not just token transfers but also cross-chain governance, NFT bridging, and data propagation.

**Definition:**

Wormhole is a cross-chain messaging protocol that uses a decentralized guardian network to observe events on one chain and attest to them on another. It supports token transfers, arbitrary message passing, and NFT bridging across multiple Layer-1 and Layer-2 networks.

**How It Works (Step-by-Step):**

1. **Lock on source chain.** The user deposits tokens into a Wormhole smart contract on the source blockchain. The contract holds the tokens as collateral and emits a locked event containing the amount, token type, and destination address.
2. **Guardian attestation.** Guardian nodes independently observe the source chain. Once a supermajority of guardians confirms the lock event, they each cryptographically sign an attestation. Guardians act as decentralized notaries; they only observe and sign, never custody funds.
3. **Relay and mint on target chain.** A relayer, which is a permissionless actor, collects the guardian signatures and submits them to the Wormhole contract on the target chain. The relayer pays the destination gas fees but cannot forge the message because it cannot produce valid guardian signatures. The target chain contract verifies the signatures and mints wrapped tokens to the user's destination address. These wrapped tokens are backed one-to-one by the collateral locked on the source chain.
4. **Use wrapped tokens.** The user can now trade, stake, or spend the wrapped tokens within the target chain ecosystem. The wrapped tokens behave like native assets on that chain while the original collateral remains locked.
5. **Burn on target chain.** When the user wants to move assets back, they send the wrapped tokens to the Wormhole contract on the target chain. The contract burns the wrapped tokens and emits a burn event.
6. **Release on source chain.** Guardians observe the burn event, sign a new attestation, and a relayer delivers it to the source chain. The source chain contract verifies the signatures and releases the original collateral tokens back to the user.

**Real-life analogy:**

Imagine a postal system run by a council of independent couriers. When you send a letter from City A, every courier watches the post office log. Once a majority agrees the letter was sent, one courier delivers a certified copy to City B. The cities do not talk to each other directly; they trust the courier council because no single courier can forge a message without being caught by the others. Wormhole is that courier council, but for blockchains.

**Tiny numeric example:**

A user bridges 1,000 USDC from Ethereum to Solana and back via Wormhole.

| Step | Actor | Action | Result |
|------|-------|--------|--------|
| 1 | User | Lock 1,000 USDC in Wormhole contract on Ethereum | Ethereum contract holds 1,000 USDC |
| 2 | Guardians | Observe the lock event and sign an attestation | 13 of 19 guardians produce signatures |
| 3 | Relayer | Submit the signed attestation to Solana | Solana verifies the guardian signatures |
| 4 | Wormhole Solana | Mint 1,000 wormhole-USDC to user | User receives wrapped token on Solana |
| 5 | User | Use wormhole-USDC in a Solana DeFi protocol | Tokens remain backed by Ethereum collateral |
| 6 | User | Burn 1,000 wormhole-USDC on Solana | Wrapped tokens are destroyed |
| 7 | Guardians | Observe the burn event and sign a release attestation | 13 of 19 guardians confirm the burn |
| 8 | Relayer | Submit the release attestation to Ethereum | Ethereum verifies the signatures |
| 9 | Wormhole Ethereum | Release 1,000 original USDC to user | User receives original tokens back |

The guardians act as decentralized notaries. The relayer is a permissionless actor who pays gas to move the message. The user never trusts a single entity, and the full lifecycle demonstrates that wrapped tokens are only destroyed when the original collateral is released.

**Common confusion:**

- No, Wormhole is not a blockchain itself; it is a protocol that sits between blockchains.
- No, guardians are not miners; they do not produce blocks, they only observe and attest to events.
- No, Wormhole tokens are not native assets; they are wrapped representations backed by locked collateral on the source chain.
- No, the protocol is not free; users pay gas on both the source and destination chains, and relayers may charge fees.
- No, a guardian set cannot change arbitrarily; the list of trusted nodes is upgradable, but changes require governance.
- No, Wormhole is not limited to tokens; developers can pass arbitrary payloads to trigger contract calls across chains.

**Key properties:**

- Decentralized attestation through a multi-signature guardian network prevents single points of failure.
- Relaying is permissionless; anyone can pay gas to deliver a validated message.
- Wrapped tokens are backed one-to-one by locked collateral on the source chain.
- The protocol is chain-agnostic and supports arbitrary message passing, not just asset transfers.
- Guardian security and contract auditing are critical because exploits can drain locked collateral.

**Where it appears in our code:**

Wormhole-style attestation is simulated in `src_web3/phase40/bridge_api.ts` where the `/attest` endpoint collects mock guardian signatures before allowing a mint, and the `/mint` endpoint checks that a threshold of attestations has been reached.
