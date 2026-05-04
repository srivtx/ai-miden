# What Is Non-Transferability

## Why It Exists

Transferability is the default property of almost every blockchain token because it enables markets, liquidity, and commerce. However, this default becomes problematic when tokens represent personal achievements, identity markers, or trust relationships that should not be commodified. If a token representing five years of honest participation in a community can be sold to a newcomer, the community's trust mechanism collapses because the buyer has not earned the reputation. Non-transferability exists to preserve the integrity of personal and social records on-chain. It ensures that the holder of a token is the same entity that performed the actions that earned it, creating a trustworthy link between history and identity.

## Definition

Non-transferability is the property of a digital token that prevents it from being sent, sold, or moved from one blockchain address to another. This is enforced at the smart contract level by overriding or disabling standard transfer functions. The token remains permanently associated with the address to which it was originally issued. Non-transferable tokens can still be minted by authorized issuers and burned under specific conditions, but they cannot change owners through peer-to-peer transactions.

## Real-Life Analogy

Imagine a driver's license issued by your country's government. The license certifies that you passed the required tests and are legally permitted to drive. You cannot sell your license to a friend who failed the test. You cannot mail it to a stranger in exchange for money. If you move to a new city, the license does not automatically transfer to your new address without government reissue. The license is non-transferable because it represents a credential tied to your identity and your testing history. A non-transferable token operates the same way on a blockchain. It is a license, certificate, or badge that belongs to one specific identity and cannot be separated from it.

## Tiny Numeric Example

A protocol issues three types of tokens to wallet 0xUser:

| Token Type | Transferable? | Balance of 0xUser | Can 0xUser send to 0xFriend? |
|------------|---------------|-------------------|------------------------------|
| Governance Token | Yes | 100 | Yes, 50 sent, balance becomes 50 |
| Reputation Badge | No | 1 | No, transfer reverted by contract |
| Achievement Medal | No | 3 | No, transfer reverted by contract |

When 0xUser attempts to send the Reputation Badge to 0xFriend, the smart contract checks the token type. Because the badge is flagged as non-transferable, the contract reverts the transaction. 0xFriend receives nothing, and 0xUser retains the badge. The contract records show that 0xUser still holds one Reputation Badge, preserving the chain of custody from issuer to original recipient. This enforcement is invisible to the user until they attempt a transfer, at which point the blockchain returns an error.

## Common Confusion

- Non-transferable does not mean non-custodial.
  The token is still held in the user's wallet, but they cannot move it.
- Non-transferability is not a blockchain-wide rule.
  It is enforced by the specific smart contract that minted the token.
- Burning a non-transferable token is not a transfer.
  Destruction is distinct from movement and is typically controlled by the issuer.
- Non-transferable tokens are not locked tokens.
  Locked tokens can become transferable after a vesting period, while soulbound tokens are permanently bound.
- Non-transferability does not prevent theft of the private key.
  If someone steals your wallet, they control your SBTs even though they cannot sell them.
- Non-transferable tokens are not immune to phishing.
  Attackers can trick users into signing malicious transactions that burn or revoke their SBTs.
- Non-transferability does not mean the token has no economic value.
  It may grant access to revenue-sharing, airdrops, or premium features that have financial worth.
- Not all non-transferable tokens are identity tokens.
  Some game items or environmental credits may also be non-transferable by design.

## Key Properties

- Smart contract enforcement that reverts transfer and approval transactions
- Permanent binding to the original recipient address
- Optional burn or revoke functions controlled by the issuer
- Visibility on public ledgers without the ability to change ownership
- Incompatibility with decentralized exchanges and standard NFT marketplaces

## Where It Appears in Our Code

Non-transferability logic is implemented in `src_web3/phase45/sbt_api.ts`.
The API explicitly rejects transfer requests for soulbound tokens and returns an error explaining the restriction.
It maintains a registry of non-transferable token types and validates every movement request against this registry.
