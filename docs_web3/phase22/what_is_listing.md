# What Is a Listing?

## Why it exists (THE PROBLEM)

Without a formal listing mechanism, NFT owners would have to manually find buyers, negotiate prices, and coordinate simultaneous transfers.

This friction destroys liquidity and makes price discovery nearly impossible for digital collectibles.

Every sale becomes a bespoke negotiation that most participants abandon.

## Definition

A listing is an on-chain record or escrow state that indicates a specific NFT is available for purchase at a defined price.

It typically locks the NFT in a program-controlled account and stores the seller's desired payment amount and accepted currency.

Buyers can discover and execute trades atomically.

This removes the need for trust between parties because the blockchain enforces the swap.

## Real-life analogy

Imagine placing a classified ad in a newspaper to sell your car.

The ad includes the model, year, mileage, asking price, and your phone number.

A listing is the blockchain equivalent of that ad, except it is tamper-proof, globally visible, and automatically enforceable.

When a buyer agrees to the price, the newspaper itself becomes a robot that hands over the title and deposits the cash in your bank account.

Neither of you lifts a finger or trusts each other.

## Tiny numeric example

Here is how a single listing is structured on-chain:

| Field | Value | Purpose |
|-------|-------|---------|
| NFT mint | 7xKX...t3Fg | Identifies which token is for sale |
| Seller | 9yLM...u5Hj | Original owner who will receive payment |
| Price | 15 SOL | Amount buyer must pay |
| Currency | SOL | Payment token accepted |
| State | Active | Indicates the listing is open |

If the seller changes their mind, they can cancel the listing and the NFT returns to their wallet.

If a buyer pays exactly 15 SOL, the listing state flips to Sold and the NFT transfers automatically without further seller action.

## Common confusion

- "Listing an NFT means selling it immediately."
  Listing only makes it available.
  A buyer must still execute the purchase by submitting a buy transaction.

- "Listings expire automatically."
  Most on-chain listings remain active until cancelled or purchased unless the program implements an explicit expiration timestamp or oracle.

- "You can list the same NFT multiple times at once."
  A properly designed program prevents double-listing by tracking the NFT's escrow state and rejecting duplicate listings.

- "Cancelling a listing burns the NFT."
  Cancelling simply returns the token to the seller's wallet.
  Nothing is destroyed and the listing account is closed to reclaim rent.

- "The listing price is stored in the NFT metadata."
  The price lives in the marketplace program's listing account, not the Metaplex metadata which is meant for descriptive content.

- "Listings are free to create."
  Creating a listing costs rent for the new account and transaction fees, though the amounts are small compared to the value of traded NFTs.

- "Listings are public immediately."
  While on-chain data is public, some marketplaces may take time to index new listings into their search and display systems.

## Where it appears in our code

- `src_web3/phase22/nft_marketplace/src/lib.rs`
  Defines the Listing account struct and instructions to create, fill, and cancel listings using PDA escrows.

- `src_web3/phase22/marketplace_api.ts`
  API endpoint that constructs and submits listing transactions for client wallets to sign.
