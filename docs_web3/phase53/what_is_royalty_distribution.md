# What Is Royalty Distribution?

## The Problem

Digital artists and creators traditionally earn income only on the primary sale of their work. Once a piece is sold on the secondary market, the creator receives nothing even if the resale price increases tenfold. This mirrors the physical art world where only the gallery and collector profit from appreciation. A mechanism is needed that automatically sends a percentage of every secondary sale back to the original creators without relying on the honesty of the new seller.

## Definition

Royalty distribution is an automatic payment splitting mechanism encoded in a smart contract or token standard. Every time an NFT changes hands through a supported marketplace, a predetermined percentage of the sale price is deducted and sent to one or more creator addresses before the seller receives the remainder.

## How It Works (6 Steps)

1. **Minting Registration.** When the NFT is first created, the minter stores royalty metadata on-chain: one or more recipient addresses and their respective percentage shares. This data is typically attached to the token metadata account.

2. **Sale Trigger.** A buyer executes a purchase, offer acceptance, or auction settlement transaction that invokes the marketplace program.

3. **Price Extraction.** The marketplace program reads the sale price from the transaction context, whether it is a fixed listing price, a winning bid, or an accepted offer amount.

4. **Royalty Calculation.** The program multiplies the sale price by each creator's percentage. For example, a 5% royalty on a 10.0 SOL sale equals 0.5 SOL. If multiple creators exist, the total royalty is the sum of all individual shares.

5. **Atomic Transfer.** During the same transaction, the program transfers the calculated royalty amounts directly to the creator addresses from the buyer's payment. This happens before the remaining balance is forwarded to the seller.

6. **Ownership Transfer.** After all royalty payments succeed, the program transfers the NFT to the buyer. If any step fails, the entire transaction reverts, ensuring creators are never skipped.

## Real-Life Analogy

Imagine a musician who records a song and configures a digital rights management system. Every time the song is played on a streaming service, the platform automatically deducts a small fee and deposits it in the musician's bank account. The musician does not need to call the streaming service or send an invoice; the split happens programmatically every single time.

## Tiny Numeric Example

- Sale price: 10.0 SOL
- Creator 1 royalty: 4%
- Creator 2 royalty: 1%
- Total royalty: 5%

Distribution:
- Creator 1 receives: 10.0 * 0.04 = 0.4 SOL
- Creator 2 receives: 10.0 * 0.01 = 0.1 SOL
- Seller receives: 10.0 - 0.4 - 0.1 = 9.5 SOL
- Marketplace fee (optional 2%): 0.2 SOL
- Final seller proceeds: 9.3 SOL

If the NFT later resells for 50.0 SOL:
- Creator 1 receives: 50.0 * 0.04 = 2.0 SOL
- Creator 2 receives: 50.0 * 0.01 = 0.5 SOL
- This demonstrates how creators benefit from appreciation.

## Common Confusion

- "Does royalty distribution work on peer-to-peer transfers?" No. It only executes when a sale occurs through a marketplace program that respects the royalty metadata.

- "Can the seller avoid paying royalties by using a different marketplace?" No. A well-designed marketplace enforces royalties at the program level and refuses to complete a sale without them.

- "Are royalties taken from the seller's balance or the buyer's payment?" No. Royalties are deducted from the gross sale amount, effectively paid by the buyer and collected by creators before the seller receives net proceeds.

- "Can creators change royalty percentages after minting?" No. The percentages are typically immutable to protect buyers from unexpected fee increases.

- "Do royalties compound on every sale?" No. Each sale is independent; the percentage is applied to that sale's price, not accumulated across sales.

- "Is there a global registry of royalty recipients?" No. Each NFT stores its own royalty metadata, so enforcement depends on the token standard and marketplace compliance.

## Key Properties (5)

1. **Automation.** Payments occur without human intervention, invoice generation, or off-chain reconciliation.

2. **Composability.** Royalty metadata is public, so any marketplace can read and enforce it without special partnerships.

3. **Immutability.** Once set at mint, percentages cannot be altered, giving buyers predictable cost structures.

4. **Fairness.** Creators participate in the long-term value of their work rather than being limited to primary sale revenue.

5. **Atomicity.** Royalty transfers and ownership changes happen in a single transaction, preventing partial execution or skipped payments.

## Where It Appears

- NFT marketplaces such as OpenSea, Magic Eden, and Blur
- Music NFT platforms like Sound.xyz and Royal
- Gaming asset marketplaces in Axie Infinity and Star Atlas
- Digital art platforms like SuperRare and Foundation
- Real-world asset tokenization platforms paying dividends or revenue shares
