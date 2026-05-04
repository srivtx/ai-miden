# Phase 22 Summary: NFT Marketplace

## What We Built

This phase implemented a decentralized NFT marketplace on Solana where users can list NFTs for sale, purchase them with automatic royalty distribution, and cancel unsold listings. We documented the marketplace concept, the mechanics of listings, and the economics of royalties.

## Key Concepts

- **Marketplace**: A trustless venue for peer-to-peer NFT trading where the blockchain atomically swaps assets and payments.
- **Listing**: An on-chain record that escrows an NFT and stores the seller's asking price.
- **Royalty**: A percentage of secondary sales automatically routed to creators, encoded in metadata and honored by the marketplace.

## Files Created

### Documentation
- `docs_web3/phase22/what_is_nft_marketplace.md`
- `docs_web3/phase22/what_is_listing.md`
- `docs_web3/phase22/what_is_royalty.md`

### Code
- `src_web3/phase22/nft_marketplace/src/lib.rs` — Anchor program with list, buy, and cancel instructions using PDA escrows.
- `src_web3/phase22/nft_marketplace/Cargo.toml` — Rust dependencies for Anchor and SPL Token.
- `src_web3/phase22/marketplace_api.ts` — Express API exposing POST /list, POST /buy, and POST /cancel endpoints.

## How It Works

1. The seller calls POST /list with a mint and price.
2. The program transfers the NFT into a PDA-owned escrow token account.
3. A Listing account stores the price and seller address.
4. A buyer calls POST /buy, paying the price plus platform and royalty splits.
5. The program atomically transfers SOL to the seller, creator, and fee destination, then moves the NFT to the buyer.
6. If unsold, the seller calls POST /cancel to reclaim the NFT from escrow.

## Next Steps

Phase 23 will explore program upgradeability, showing how deployed Solana programs can be updated via buffer accounts and upgrade authorities.
