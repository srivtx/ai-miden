# Phase 21 Summary: NFT Minting

## What We Built

This phase implemented a complete NFT minting pipeline on Solana. We created documentation explaining NFTs, Metaplex, and metadata, then built a Rust Anchor program and a TypeScript Express API that can mint non-fungible tokens with attached metadata.

## Key Concepts

- **NFTs**: Unique tokens with a supply of one and zero decimals that represent ownership of a digital or physical asset.
- **Metaplex**: The standard protocol suite that defines how Solana NFTs store names, images, attributes, and royalties.
- **Metadata**: Off-chain JSON referenced by an on-chain account, enabling wallets and marketplaces to display rich information.

## Files Created

### Documentation
- `docs_web3/phase21/what_is_nft.md`
- `docs_web3/phase21/what_is_metaplex.md`
- `docs_web3/phase21/what_is_metadata.md`

### Code
- `src_web3/phase21/nft_mint/src/lib.rs` — Anchor program that mints one token, creates Metaplex metadata, and freezes the mint.
- `src_web3/phase21/nft_mint/Cargo.toml` — Rust dependencies for Anchor, SPL Token, and Metaplex.
- `src_web3/phase21/nft_api.ts` — Express API with POST /mint and GET /nft/:mint endpoints.

## How It Works

1. The client sends a POST request with name, symbol, and uri.
2. The API creates a new SPL mint with zero decimals.
3. It mints exactly one token to the payer's associated token account.
4. The Rust program (or API equivalent) creates a Metaplex metadata account pointing to the off-chain JSON.
5. Mint authority is revoked so the NFT supply can never increase.

## Next Steps

Phase 22 will build on this by creating a marketplace where these NFTs can be listed, bought, and sold with royalty enforcement.
