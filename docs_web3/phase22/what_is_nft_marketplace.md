# What Is an NFT Marketplace?

## Why it exists (THE PROBLEM)

After minting an NFT, owners need a trustworthy venue to discover buyers and execute sales.

Without a marketplace, they must rely on private negotiations or escrow intermediaries.

Peer-to-peer trading is risky because either the buyer or seller must send their asset first, creating opportunities for fraud and chargebacks.

This eliminates price transparency and destroys liquidity.

Without a marketplace, the entire NFT economy becomes a series of isolated, high-trust private deals.

## Definition

An NFT marketplace is a decentralized application or smart contract system that allows users to list non-fungible tokens for sale, browse available listings, and execute trustless peer-to-peer trades.

The blockchain atomically swaps the NFT for payment in a single transaction that cannot be half-completed.

## Real-life analogy

Think of an art auction house like Sotheby's.

Sellers consign paintings, experts verify authenticity, catalogues display items with reserve prices, and on auction day the house manages payment and transfer so neither party can cheat.

An NFT marketplace is Sotheby's encoded in software.

It holds the item in escrow, displays the price, collects the funds, distributes royalties to the original artist, and transfers ownership.

All of this happens without human intermediaries or geographic restrictions, operating twenty-four hours a day.

## Tiny numeric example

Consider a marketplace processing three sales in one day:

| Sale | Price | Royalty (5%) | Platform Fee (2%) | Seller Receives |
|------|-------|-------------|-------------------|-----------------|
| Cyber Dragon | 100 SOL | 5 SOL | 2 SOL | 93 SOL |
| Pixel House | 20 SOL | 1 SOL | 0.4 SOL | 18.6 SOL |
| Virtual Land | 500 SOL | 25 SOL | 10 SOL | 465 SOL |

The marketplace smart contract automatically splits each payment across three parties in a single atomic transaction.

Either all transfers succeed or the entire transaction reverts with no partial state changes.

## Common confusion

- "Marketplaces store the NFTs themselves."
  Marketplaces only hold listings in escrow.
  The NFT remains on the blockchain in a program-derived address, not in a central database.

- "You need a separate marketplace for every NFT collection."
  Most marketplaces support any standard Metaplex NFT, not just specific collections or whitelisted projects.

- "Marketplaces set the prices."
  Sellers set their own prices.
  Marketplaces merely display and execute the trade at the seller's chosen price.

- "Buying an NFT on a marketplace transfers copyright."
  Only the token ownership transfers.
  Intellectual property terms are defined in the license, not the sale.

- "All marketplaces charge the same fees."
  Platform fees, royalty enforcement policies, and supported currencies vary significantly between Magic Eden, Tensor, OpenSea, and others.

- "Decentralized marketplaces cannot be shut down."
  While the smart contracts persist on-chain, the front-end website and API servers can be taken offline by hosting providers or regulators.

- "Marketplaces guarantee the NFT is not a scam."
  Marketplaces display tokens but rarely verify the legitimacy of collections.
  Buyers must do their own research.

## Where it appears in our code

- `src_web3/phase22/nft_marketplace/src/lib.rs`
  Rust program handling listing creation, purchase execution, royalty distribution, and fund settlement.

- `src_web3/phase22/marketplace_api.ts`
  Express API exposing list, buy, and cancel endpoints that prepare transactions for client signing.
