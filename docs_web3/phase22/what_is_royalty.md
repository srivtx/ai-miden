# What Is a Royalty?

## Why it exists (THE PROBLEM)

In traditional art, creators earn money only on the first sale and receive nothing when their work appreciates and resells for millions on the secondary market.

Digital artists faced the same problem.

Once an NFT sold, the original creator had no mechanism to capture ongoing value from their work's popularity or cultural significance.

This disincentivized long-term creative investment and allowed speculators to capture all upside.

## Definition

A royalty is a percentage of the sale price that is automatically routed to the original creator or rights holders every time an NFT is resold on a secondary market.

On Solana, this is typically encoded in the Metaplex metadata as seller_fee_basis_points and honored by marketplace smart contracts.

## Real-life analogy

Imagine a novelist who writes a bestseller.

In the old model, the publisher pays a one-time advance and the author never sees another cent even if the book becomes a classic.

Modern publishing solved this with ongoing royalties per copy sold.

NFT royalties apply the same concept to digital goods.

The creator writes their royalty percentage into the token's DNA, and every time the book changes hands, a small slice automatically goes back to the author.

No one writes a check or sends an invoice.

The blockchain becomes an automated accountant that never forgets to pay the creator.

## Tiny numeric example

An artist mints an NFT with a 7.5% royalty and sells it for 10 SOL.

Later buyers resell it twice:

| Event | Sale Price | Royalty (7.5%) | Artist Earns | Cumulative Artist Earnings |
|-------|-----------|----------------|--------------|---------------------------|
| Primary sale | 10 SOL | 0.75 SOL | 0.75 SOL | 0.75 SOL |
| Secondary sale 1 | 50 SOL | 3.75 SOL | 3.75 SOL | 4.50 SOL |
| Secondary sale 2 | 200 SOL | 15.00 SOL | 15.00 SOL | 19.50 SOL |

The artist earned 19.50 SOL total, with 18.75 SOL coming from secondary markets.

Without royalties, the speculators would have captured all that upside.

## Common confusion

- "Royalties are enforced by the blockchain automatically."
  The blockchain records the royalty rate, but marketplaces must voluntarily implement and honor the split in their smart contracts.

- "Zero-royalty marketplaces hurt creators."
  Some platforms allow buyers to bypass royalties, reducing creator income and sparking debate about long-term sustainability of creative ecosystems.

- "Royalties go to the current owner."
  Royalties always flow to the original creators defined in the metadata, not the seller who is reselling the item.

- "Royalty percentages can be changed after minting."
  Typically the update authority sets royalties at mint and can only change them if they retain update control.
  Otherwise they are locked forever.

- "Royalties are paid in the same token as the sale."
  Yes, the marketplace program deducts the percentage from the payment token before forwarding the remainder to the seller.

- "High royalties guarantee more income."
  Excessive royalties can discourage trading and reduce overall volume.
  This paradoxically lowers creator earnings by killing liquidity.

- "Royalties are unique to NFTs."
  Traditional music, book, and patent royalties have existed for centuries.
  NFTs simply automate and enforce them on a global ledger.

## Where it appears in our code

- `src_web3/phase22/nft_marketplace/src/lib.rs`
  Purchase instruction reads seller_fee_basis_points and transfers the royalty portion to the creator before sending the remainder to the seller.

- `src_web3/phase22/marketplace_api.ts`
  API displays expected royalty splits and verifies creator payment in transaction simulation before the buyer signs.
