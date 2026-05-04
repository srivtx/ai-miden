# What Is NFT Escrow?

## The Problem

In a direct peer-to-peer NFT trade, the seller must send the NFT before receiving payment, or the buyer must send payment before receiving the NFT. Neither party wants to act first because the other might default. Without a neutral third party to hold both assets during the exchange, trades collapse due to mistrust, especially between anonymous users on a blockchain.

## Definition

NFT escrow is a smart contract mechanism that temporarily holds an NFT and optionally the buyer's payment in a neutral on-chain account during a transaction. The escrow program releases the NFT to the buyer and the payment to the seller only when all agreed conditions are met, such as payment receipt, auction conclusion, or offer acceptance.

## How It Works (6 Steps)

1. **Deposit.** The seller initiates a listing, auction, or offer and instructs the escrow program to take custody of the NFT. The program moves the NFT from the seller's wallet into a Program Derived Address (PDA) owned by the escrow program.

2. **Locking.** The escrow account records the seller's address, the NFT mint, the intended sale conditions (price, duration, auction type), and optionally the buyer's expected payment amount. These parameters are immutable while the escrow is active.

3. **Bid / Payment Collection.** In an auction, bidders send SOL to separate escrow bid accounts. In a fixed-price or offer scenario, the buyer sends the exact payment amount into the main escrow account or a payment vault.

4. **Condition Verification.** Before any release, the program checks: Is the payment amount correct? Has the auction ended? Has the seller accepted the offer? Is the buyer the authorized winner? Any failed check aborts the transaction.

5. **Release.** If conditions pass, the program atomically transfers the NFT from escrow to the buyer and the payment from escrow to the seller, minus any royalties or fees. This atomicity guarantees neither party can receive their asset without the other also receiving theirs.

6. **Return.** If conditions are never met, such as an auction expiring with no valid bids or a seller canceling an active listing, the program returns the NFT from escrow to the seller and refunds any locked payments to bidders or buyers.

## Real-Life Analogy

Imagine buying a house. You do not hand cash directly to the seller and hope they hand over the keys. Instead, both parties use an escrow agent: you deposit the money, the seller deposits the deed, and the agent only swaps them after inspections and title checks pass. If the deal falls through, the agent returns your money and the seller keeps the deed.

## Tiny Numeric Example

- NFT listed for: 5.0 SOL
- Buyer sends: 5.0 SOL to escrow
- Royalty: 5% (0.25 SOL)

Escrow holds:
- 1 NFT (from seller)
- 5.0 SOL (from buyer)

Upon successful sale:
- NFT moves to buyer's wallet
- 0.25 SOL moves to creator's wallet
- 4.75 SOL moves to seller's wallet
- Escrow account closes, reclaiming rent

If buyer cancels before sale:
- NFT returns to seller
- 5.0 SOL returns to buyer
- Escrow account closes

## Common Confusion

- "Does escrow mean the marketplace owns the NFT?" No. The escrow program holds it under programmatic rules; no human or centralized entity controls the account.

- "Can the seller withdraw the NFT after a buyer has paid?" No. Once payment is deposited, the program enforces completion or refund; the seller cannot unilaterally retrieve the NFT.

- "Is escrow only used for auctions?" No. Escrow is used for fixed-price listings, offers, auctions, and any trade where simultaneous exchange is required.

- "Does escrow earn interest on held funds?" No. The program does not invest or lend held SOL; it simply stores it until release conditions are triggered.

- "Can a buyer inspect the NFT while it is in escrow?" No. The NFT is locked in a program account; buyers verify metadata before bidding or buying, not during escrow custody.

- "Is escrow the same as staking?" No. Staking locks tokens to earn rewards; escrow locks assets only to facilitate a trade and releases them upon settlement or cancellation.

## Key Properties (5)

1. **Trustlessness.** Parties trade without knowing each other because the program enforces the deal rather than reputation.

2. **Atomicity.** Either both the NFT and payment transfer successfully, or neither does, preventing partial losses.

3. **Immutability.** Escrow conditions are fixed at creation and cannot be altered to disadvantage either party.

4. **Transparency.** Anyone can inspect the escrow account on-chain to verify what is held and under what conditions.

5. **Efficiency.** Escrow eliminates the need for lawyers, banks, or manual dispute resolution for standard trades.

## Where It Appears

- NFT marketplaces for fixed-price listings and auctions
- Peer-to-peer NFT swap protocols
- Decentralized exchange order books holding assets before matching
- Real estate tokenization platforms holding property deeds during sales
- Gaming marketplaces trading in-game items for cryptocurrency
