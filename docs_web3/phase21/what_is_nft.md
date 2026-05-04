# What Is an NFT?

## Why it exists (THE PROBLEM)

Digital files can be copied infinitely with perfect fidelity, making it impossible to prove ownership or scarcity of digital art, collectibles, or virtual real estate.

Before NFTs, creators had no reliable way to sell unique digital items because buyers could not verify authenticity, provenance, or the total supply of a given work.

This destroyed the market for digital scarcity and left artists without a mechanism to monetize original digital creations the way painters or sculptors could in the physical world.

Collectors also suffered because they had no way to prove they owned an original rather than a copy, eliminating the prestige and investment value that drives physical art markets.

## Definition

A Non-Fungible Token (NFT) is a unique cryptographic token on a blockchain that represents ownership of a specific digital or physical asset.

Unlike cryptocurrencies such as SOL or USDC, each NFT has distinct properties and cannot be exchanged one-for-one with another NFT, making it non-interchangeable by design.

The blockchain records the token's mint address, current owner, and transaction history immutably.

## Real-life analogy

Imagine a famous painting like the Mona Lisa.

Millions of postcards, posters, and digital images of it exist, but only one original hangs in the Louvre.

The museum holds a certificate of authenticity and provenance showing Leonardo da Vinci painted it and tracing every owner since 1503.

An NFT functions exactly like that certificate for digital items.

You can screenshot an NFT image a thousand times, but only the wallet holding the NFT on the blockchain truly "owns" it and can prove that ownership to anyone in the world instantly.

The blockchain acts as an immutable notary that never sleeps, never forgets, and cannot be bribed.

Just as the Mona Lisa's value comes from its provenance and uniqueness rather than the paint on the canvas, an NFT's value comes from its cryptographic proof of ownership rather than the pixels in the image file.

## Tiny numeric example

Consider a collection of 10,000 unique digital pets:

| Property | Value |
|----------|-------|
| Total supply | 10,000 NFTs |
| Mint price | 2.5 SOL each |
| Unique traits per pet | 7 (fur, eyes, background, hat, accessory, mood, rarity) |
| Rarity tiers | Common (60%), Rare (30%), Epic (9%), Legendary (1%) |

If you own pet #4,237 with Legendary traits, no one else can ever own that exact token.

The blockchain records your wallet address as the owner, and the total supply can never exceed 10,000 because the smart contract enforces scarcity at the protocol level.

A Common pet might resell for 3 SOL while a Legendary could fetch 500 SOL due to provable scarcity.

## Common confusion

- "NFTs are just JPEGs."
  NFTs are ownership certificates living on the blockchain.
  The image file is typically stored off-chain while the token lives on-chain and proves who owns it, similar to how a deed is not the house itself.

- "I can just right-click and save the image, so I own it."
  Saving a copy gives you a duplicate file, not the cryptographic proof of ownership recorded immutably on the blockchain.
  Photographing the Mona Lisa does not make you its owner.

- "All NFTs are worth millions."
  Most NFT collections have little to no value.
  Price depends entirely on demand, utility, community strength, and cultural relevance, just like most physical art.

- "NFTs and cryptocurrencies are the same thing."
  Cryptocurrencies are fungible and interchangeable like dollar bills.
  NFTs are unique and distinct like original paintings or collectible trading cards.

- "Buying an NFT means I own the copyright."
  Typically you only own the token and a license to display the art.
  Intellectual property rights remain with the creator unless explicitly transferred in writing.

- "NFTs are only for digital art."
  They can represent music, virtual real estate, event tickets, domain names, in-game items, academic credentials, and even physical asset deeds.

- "NFTs are bad for the environment."
  Solana NFTs use proof-of-stake consensus and consume a fraction of the energy required by older proof-of-work blockchains.
  A single Solana transaction often uses less energy than a Google search.

## Where it appears in our code

- `src_web3/phase21/nft_mint/src/lib.rs`
  Core Rust program that defines the mint logic and enforces a supply of one to create NFTs on Solana.

- `src_web3/phase21/nft_api.ts`
  Express API endpoint that accepts mint requests from clients, validates metadata fields, and returns the minted NFT address for verification.
