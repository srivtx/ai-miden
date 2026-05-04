# Architecture: Step-by-Step Build

This document describes how to build the complete NFT marketplace from an empty directory to a deployed system. Each step explains why the component exists and how it connects to the others.

---

## Step 1: Design NFT Escrow Account

### What You Build

Define the escrow account structure that will hold NFTs and payments during trades. This includes a Program Derived Address (PDA) seeded by the seller's public key, the NFT mint, and a nonce. The account stores the seller, the buyer (if known), the NFT mint, the payment amount, the state (active, released, returned), and an authority bump.

### Why This Step First

Escrow is the trust layer. Every other feature, whether a fixed-price listing or an auction, depends on the ability to lock assets in a neutral account. If escrow is not designed first, you will have to retrofit custody logic into listing and auction code later, leading to duplicated state and security holes. Starting with escrow forces you to answer: who can deposit, who can release, and under what conditions.

### Key Decisions

- Use a PDA so the program can sign releases without a private key.
- Store the NFT in an associated token account owned by the PDA, not the PDA itself, because token accounts hold balances while PDAs hold program state.
- Store payment as native SOL in the PDA account or in a separate SPL token account depending on whether you accept wrapped SOL.

---

## Step 2: Implement Fixed-Price Listing

### What You Build

A marketplace instruction that allows a seller to list an NFT at a fixed price. The instruction creates a listing account, transfers the NFT into escrow custody, and sets the price. A separate buy instruction allows a buyer to send the exact payment, which triggers the escrow release: NFT to buyer, payment minus royalties to seller.

### Why This Feature Second

Fixed-price listings are the simplest sale model. They exercise the escrow mechanism with a single buyer, a single price, and no time logic. By building this first, you validate that escrow deposit, validation, and release work correctly before adding the complexity of auctions and offers.

### Key Decisions

- The listing account is a separate PDA from the escrow account to separate business logic from custody.
- The buy instruction must be atomic: payment in, NFT out, royalties distributed, all in one transaction.
- If the buyer sends too much or too little, the transaction aborts before any transfer occurs.

---

## Step 3: Add English Auction

### What You Build

Auction instructions: create_auction, place_bid, and settle_auction. The create instruction initializes an auction account with a reserve price, minimum bid increment, and end timestamp. The place_bid instruction locks the bidder's SOL in a bid escrow account and refunds the previous highest bidder. The settle instruction runs after the end timestamp and transfers the NFT to the winner and the winning bid to the seller.

### Why This Feature Third

English auctions add time-based logic and multi-user state management. They are the natural next step after fixed-price listings because they reuse the same escrow patterns but introduce a competitive bidding layer. Building this now forces you to handle clock validation, refund logic, and winner resolution before adding the price-descent model.

### Key Decisions

- Each bid gets its own escrow account to prevent overwriting and to allow easy refunds.
- The previous highest bidder is refunded atomically when a new higher bid is placed.
- Settlement can be triggered by anyone after the end time to ensure the auction does not stall if the seller is offline.

---

## Step 4: Add Dutch Auction

### What You Build

A variant of the auction creation instruction where the start price is high and the price decays linearly over time based on the Solana clock. An accept instruction allows a buyer to purchase at the current computed price. Unlike the English auction, there is no bidding war; the first acceptor wins.

### Why This Feature Fourth

Dutch auctions are conceptually similar to English auctions but invert the buyer behavior from bidding up to buying down. Adding them now reuses the auction account structure and escrow release logic while introducing a mathematical price curve. This tests your ability to compute on-chain values deterministically and safely.

### Key Decisions

- The price is computed as a pure function of start price, end price, start time, end time, and current clock timestamp.
- There are no bid accounts; the buyer sends the exact computed price directly.
- If no one accepts before the auction reaches its floor price, the seller can cancel and reclaim the NFT.

---

## Step 5: Build Offer System

### What You Build

Instructions for buyers to place offers on NFTs that are not actively listed. A place_offer instruction creates an offer account and locks the buyer's payment in escrow. A cancel_offer instruction refunds the buyer and closes the account. An accept_offer instruction, callable only by the NFT owner, releases the NFT to the buyer and the payment to the seller.

### Why This Feature Fifth

Offers introduce a buyer-initiated flow, which is the inverse of listings and auctions. They are important for market liquidity because buyers can express interest even when sellers have not listed. Building offers now forces you to handle authorization checks where the seller acts on a buyer's escrow, which is a different trust boundary than seller-initiated listings.

### Key Decisions

- Offers are scoped to a specific NFT mint and expire after a set duration to prevent stale escrows.
- Only the NFT owner can accept an offer, preventing unauthorized sales.
- The offer account stores the buyer, the NFT mint, the offer amount, and the expiry timestamp.

---

## Step 6: Implement Royalty Distribution

### What You Build

A royalty distribution module invoked by the buy, settle_auction, and accept_offer instructions. It reads creator metadata from the NFT's token metadata account, calculates percentages of the sale price, and transfers the respective amounts to each creator before sending the remainder to the seller.

### Why This Feature Sixth

Royalty distribution is a cross-cutting concern that affects every sale path. By implementing it after all sale types exist, you can ensure it integrates consistently across fixed-price, auction, and offer settlements. Implementing it earlier would require retrofitting into unfinished instructions.

### Key Decisions

- Royalty data is read from a metadata account that follows the Metaplex Token Metadata standard.
- Distribution is atomic with the sale; if a creator's transfer fails, the entire sale reverts.
- Total royalty percentage is capped at the program level to prevent a malicious metadata account from draining the entire sale amount.

---

## Step 7: Wire Marketplace Frontend API

### What You Build

An Express server on port 3057 that exposes REST endpoints for every marketplace action: list, delist, buy, offer, cancel-offer, accept-offer, auction create, auction bid, auction settle, and read-only endpoints for listings and auctions. The API constructs transactions, adds recent blockhashes, and returns them to the client for signing, or signs with a server keypair for administrative actions.

### Why This Feature Seventh

The API serves as the interface between the blockchain and the user interface. By building it after all on-chain logic is complete, you ensure the API does not need to change when program instructions are modified. The API abstracts RPC complexity from the frontend and can handle caching, rate limiting, and request validation.

### Key Decisions

- The API returns partially constructed transactions for client-side signing to maintain non-custody principles.
- Read endpoints query RPC directly and cache results for a few seconds to reduce load.
- Error responses map Solana program error codes to human-readable messages.

---

## Step 8: Test All Flows

### What You Build

A comprehensive test suite that covers: listing and buying, placing and canceling offers, accepting offers, creating and bidding in English auctions, creating and accepting Dutch auctions, verifying royalty distribution to multiple creators, verifying escrow return on cancellation, and verifying access control on unauthorized actions.

### Why This Step Last

Testing validates the entire integrated system. It must come last because earlier steps test individual units in isolation. End-to-end tests verify that the marketplace program, escrow program, and API server work together correctly under realistic conditions, including clock skew, concurrent bids, and insufficient balances.

### Key Decisions

- Use a local Solana test validator for deterministic block production and time control.
- Automate time advancement for auction expiration tests using warp_to_timestamp.
- Test failure cases as thoroughly as success cases because blockchain transactions are irreversible.

---

## Deployment Order

1. Deploy the Escrow program first because the Marketplace program references its program ID for CPI calls.
2. Deploy the Marketplace program with the Escrow program ID embedded in its configuration.
3. Start the Express API with both program IDs and the RPC endpoint configured.
4. Run the test suite against devnet before pointing the API to mainnet.

## Scaling Considerations

- As the number of listings grows, use off-chain indexing (Helius, QuickNode) for fast queries rather than scanning all on-chain accounts.
- For high-frequency auctions, consider batching refunds or using a pull model where bidders claim refunds rather than automatic push refunds.
- Monitor PDA account rents; close accounts aggressively to return rent to users and keep state minimal.
