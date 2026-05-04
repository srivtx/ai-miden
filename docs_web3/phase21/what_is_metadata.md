# What Is Metadata?

## Why it exists (THE PROBLEM)

A blockchain token is fundamentally just a number in a ledger.

Without descriptive information, wallets and marketplaces cannot display names, images, attributes, or creator details.

Users would see only opaque account addresses and balances, making NFTs meaningless and impossible to browse, verify, or trade with confidence.

Metadata bridges the gap between raw blockchain data and human understanding.

## Definition

Metadata is structured descriptive data attached to an NFT that defines its name, image URI, attributes, creators, and royalty information.

On Solana, this is typically stored as a JSON file referenced by an on-chain Metaplex metadata account.

This creates a bridge between the raw token and human-readable content that wallets can render.

## Real-life analogy

Imagine buying a house where the deed only says "Plot 8472" with no address, square footage, photos, or owner history.

You would have no idea what you purchased or if it is valuable.

Metadata is the real estate listing that adds photos, descriptions, room counts, school districts, and price history to that bare deed.

It transforms an abstract identifier into something humans can understand, evaluate, and trade with confidence.

Without metadata, every NFT would be a faceless serial number, and digital collecting would be impossible.

## Tiny numeric example

Here is a minimal metadata JSON for a digital trading card:

```json
{
  "name": "Cyber Dragon #42",
  "symbol": "CD",
  "description": "A legendary fire-breathing cyber beast.",
  "image": "https://arweave.net/abc123.../dragon.png",
  "attributes": [
    { "trait_type": "Element", "value": "Fire" },
    { "trait_type": "Power", "value": 95 },
    { "trait_type": "Rarity", "value": "Legendary" }
  ],
  "properties": {
    "creators": [{ "address": "7xKX...", "share": 100 }],
    "royalty": 500
  }
}
```

The `royalty` field of 500 means 5.00% of every secondary sale goes to the creator automatically.

The `attributes` array lets marketplaces filter and sort by traits.

Collectors can search for all Legendary dragons without inspecting each token individually.

## Common confusion

- "Metadata is stored entirely on-chain."
  Usually only a URI pointer is on-chain.
  The JSON itself is off-chain to save rent costs, though some projects use on-chain storage for permanence.

- "I can update metadata whenever I want."
  Update authority is typically limited to the creator.
  Once revoked, metadata becomes immutable and cannot be changed.

- "Metadata and the image file are the same thing."
  The metadata is a JSON description.
  The image is a separate media file referenced by URI within that JSON.

- "All wallets read metadata the same way."
  While Metaplex is the standard, some wallets may cache, truncate, or fail to display certain fields depending on their implementation.

- "Metadata guarantees the NFT is authentic."
  Metadata can be spoofed or copied.
  Authenticity comes from the original mint address and verified creator signatures on-chain.

- "Royalties in metadata are automatically enforced."
  The metadata specifies royalties, but marketplaces must voluntarily enforce them.
  Some platforms ignore or bypass them entirely.

- "Metadata does not affect value."
  Rarity traits, provenance, and creator reputation encoded in metadata directly influence market prices and collector demand.

## Where it appears in our code

- `src_web3/phase21/nft_mint/src/lib.rs`
  Rust program initializes a Metaplex metadata account pointing to off-chain JSON that describes the NFT.

- `src_web3/phase21/nft_api.ts`
  Express API generates, uploads to Arweave, and validates metadata JSON before calling the mint program.
