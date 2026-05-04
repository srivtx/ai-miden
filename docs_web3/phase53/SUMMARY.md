# Phase 53: Complete NFT Marketplace

## Overview

Phase 53 implements a production-grade NFT marketplace on Solana. The system supports fixed-price listings, time-bound offers, English auctions, Dutch auctions, automatic royalty distribution, and NFT escrow. It is composed of two on-chain programs (marketplace and escrow), one Express API server, and comprehensive documentation. Every component is designed to demonstrate trustless peer-to-peer trade without relying on centralized custody.

## Architecture Diagram

```
                        +------------------+
                        |   User Wallet    |
                        |  (Phantom/Solflare)|
                        +--------+---------+
                                 |
                                 | Signs transactions
                                 v
                        +--------+---------+
                        |  Express API     |
                        |  Port 3057       |
                        |  marketplace_api.ts|
                        +--------+---------+
                                 |
                                 | RPC calls / Transaction building
                                 v
                        +--------+---------+
                        |  Solana Network  |
                        |  Devnet / Mainnet|
                        +--------+---------+
                                 |
            +--------------------+--------------------+
            |                    |                    |
            v                    v                    v
   +--------+---------+ +--------+---------+ +--------+---------+
   | Marketplace      | | Escrow           | | SPL Token Program|
   | Program          | | Program          | |                  |
   | src/lib.rs       | | src/lib.rs       | |                  |
   |                  | |                  | |                  |
   | - list/delist    | | - hold NFT       | | - transfer tokens|
   | - buy            | | - hold payment   | | - approve        |
   | - offer/accept   | | - release NFT    | | - freeze         |
   | - auction        | | - release payment| |                  |
   | - royalty split  | | - return assets  | |                  |
   +--------+---------+ +--------+---------+ +--------+---------+
            |                    |
            | CPI calls          | CPI calls
            v                    v
   +--------+---------+ +--------+---------+
   | Listing accounts | | Escrow PDA       |
   | Auction accounts | | Payment vault    |
   | Offer accounts   | | Bid accounts     |
   +------------------+ +------------------+
```

## File Map

```
/docs_web3/phase53/
  what_is_auction_engine.md       -- English and Dutch auction theory
  what_is_royalty_distribution.md -- Automatic royalty split theory
  what_is_escrow_nft.md           -- NFT escrow custody theory
  SUMMARY.md                      -- This file: overview and map
  ARCHITECTURE.md                 -- Step-by-step build guide

/src_web3/phase53/
  marketplace/
    Cargo.toml                    -- Solana program dependencies
    src/lib.rs                    -- Main marketplace program
  escrow/
    Cargo.toml                    -- Solana program dependencies
    src/lib.rs                    -- Escrow custody program
  marketplace_api.ts              -- Express REST API server
  deploy.sh                       -- Build and deploy script
```

## Key Concepts Covered

- **Fixed-Price Listings:** Seller sets a price; buyer pays and receives the NFT atomically.
- **Offers:** Buyer locks funds in escrow; seller can accept to complete the sale.
- **English Auction:** Price ascends; highest bidder wins at auction end.
- **Dutch Auction:** Price descends over time; first acceptor wins.
- **Royalty Distribution:** Creators receive a percentage of every secondary sale automatically.
- **Escrow:** Neutral program custody prevents either party from defaulting.

## Integration Flow

1. The frontend or client calls the Express API endpoints.
2. The API constructs and signs transactions, then submits them to Solana RPC.
3. The Marketplace program validates business logic and invokes the Escrow program via Cross-Program Invocation (CPI) to hold or release assets.
4. The Escrow program holds NFTs and payments in PDAs, releasing them only when the Marketplace program authorizes it.
5. On every successful sale, the Marketplace program reads royalty metadata from the NFT token account and distributes splits atomically.

## Testing Strategy

- Unit tests in each Rust program verify state transitions.
- Integration tests via the API exercise end-to-end flows: list, offer, accept, auction, bid, settle, royalty check.
- Scripts simulate time travel for auction expiration using local test validators.

## Security Considerations

- All escrow accounts are Program Derived Addresses so only the escrow program can sign their releases.
- The marketplace program verifies ownership and account constraints before any state mutation.
- Royalty percentages are read from immutable on-chain metadata, not user input.
- Re-entrancy is impossible because Solana's runtime does not support recursive CPI loops beyond a fixed depth.
