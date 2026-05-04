# What Is a Tiered Sale?

## The Problem

In a standard token sale, every participant pays the same price regardless of when they discovered the project or how much they contributed to the community. This creates three major problems. First, it punishes early believers who spent months testing products and providing feedback, because they receive no price advantage over strangers who arrive on the last day. Second, it encourages last-minute FOMO and gas wars, where bots and whales flood the contract in the final seconds, driving up transaction fees and pricing out smaller supporters. Third, a flat price provides no mechanism for projects to reward specific groups such as beta testers, strategic partners, or long-term community members. Everyone is treated identically, which removes the incentive to engage early and deeply. A tiered sale solves these problems by creating multiple participation levels with different prices, maximum allocations, and whitelist requirements.

## Definition

A tiered sale is a token sale structure that divides participants into distinct groups, called tiers, where each tier receives a different token price, allocation limit, and entry requirement. Instead of one public price for everyone, the project offers better terms to earlier or more committed participants. For example, the earliest supporters might pay 0.30 USDC per token, community members might pay 0.40 USDC, and the general public might pay 0.50 USDC. Each tier also has a maximum amount that any single wallet can contribute, preventing whales from monopolizing the supply. Tiers are enforced by smart contract logic that checks a buyer's whitelist status and allocation limits before accepting their payment.

## How It Works (6 Steps)

**Step 1: Tier Design.** The project team decides how many tiers to create and what distinguishes them. Typical distinctions include early access timing, community role, KYC completion, or holding a specific NFT. Each tier is assigned a unique price per token, a maximum contribution per wallet, and a number of available slots or tokens.

**Step 2: Whitelist Assignment.** Users register or apply for a tier through an off-chain form or on-chain mechanism. The project team or an automated oracle reviews applications and adds approved wallet addresses to a whitelist mapping stored in the smart contract. Each address is tagged with its assigned tier level.

**Step 3: Tier Verification During Purchase.** When a user attempts to buy tokens, the smart contract checks three conditions in sequence. First, it verifies that the user's wallet address exists in the whitelist. Second, it confirms that the user's requested contribution does not exceed their tier's maximum allocation. Third, it ensures that the total tokens sold across all tiers does not exceed the overall hard cap.

**Step 4: Price Application.** The smart contract uses the tier tag associated with the buyer's address to determine the correct price. If a Tier 1 buyer sends 1,000 USDC at a price of 0.40 USDC per token, they receive 2,500 tokens. If a Tier 3 buyer sends the same 1,000 USDC at a price of 0.50 USDC per token, they receive only 2,000 tokens. The price logic is deterministic and identical for every address in the same tier.

**Step 5: Allocation Tracking.** The contract maintains a running total of how much each wallet has contributed and how many tokens remain in each tier's pool. If a tier has 100,000 tokens reserved and 95,000 have been sold, the next Tier 1 buyer can only purchase up to the remaining 5,000 tokens or their personal allocation limit, whichever is smaller.

**Step 6: Finalization and Distribution.** After the sale ends, the contract finalizes the results. Participants claim their tokens according to the project's distribution rules, which may include immediate delivery or vesting. The tier structure does not affect the post-sale mechanics, only the price and quantity each buyer received during the sale.

## Real-life Analogy

Imagine a bookstore launching a limited edition of a highly anticipated novel. They create three customer tiers. Founding Members, who joined the bookstore's loyalty program two years ago, can pre-order up to five copies at 30 dollars each. Newsletter Subscribers, who joined within the last six months, can order up to three copies at 40 dollars each. The General Public can buy one copy at 60 dollars during the official release week. The bookstore maintains a physical list of Founding Members and Newsletter Subscribers at the register. When a customer approaches, the cashier checks the list to determine which price and limit apply. If someone who is not on either list tries to buy during the pre-order period, they are turned away. This is exactly how a tiered token sale operates, except the smart contract acts as the cashier, the blockchain address acts as the customer ID, and the whitelist acts as the loyalty list.

## Tiny Numeric Example With Tier Math

**Project:** GalaxyDAO Token (GDAO)
**Total Tokens for Sale:** 2,000,000 GDAO
**Hard Cap:** 1,000,000 USDC

| Tier | Price per GDAO | Max Allocation per Wallet | Slots Available | Tokens Reserved |
|------|---------------|---------------------------|-----------------|-----------------|
| Tier 1: Founders | 0.30 USDC | 5,000 USDC | 100 wallets | 1,000,000 GDAO |
| Tier 2: Early Community | 0.40 USDC | 2,000 USDC | 200 wallets | 600,000 GDAO |
| Tier 3: Public | 0.50 USDC | 1,000 USDC | Unlimited | 400,000 GDAO |

**Purchase Scenario:**
- Alice is Tier 1. She contributes 3,000 USDC.
  - Tokens received: 3,000 / 0.30 = 10,000 GDAO.
  - Remaining Tier 1 allocation for Alice: 5,000 - 3,000 = 2,000 USDC.
- Bob is Tier 2. He contributes 2,000 USDC.
  - Tokens received: 2,000 / 0.40 = 5,000 GDAO.
  - Remaining Tier 2 allocation for Bob: 0 USDC.
- Carol is Tier 3. She contributes 1,000 USDC.
  - Tokens received: 1,000 / 0.50 = 2,000 GDAO.
  - Remaining Tier 3 allocation for Carol: 0 USDC.

**Total Sale Outcome:**
- Tier 1 sells out: 100 wallets * 5,000 USDC = 500,000 USDC raised, 1,000,000 GDAO distributed.
- Tier 2 sells out: 200 wallets * 2,000 USDC = 400,000 USDC raised, 600,000 GDAO distributed.
- Tier 3 sells 100,000 USDC worth: 100,000 / 0.50 = 200,000 GDAO distributed.
- Total raised: 1,000,000 USDC (hard cap reached). Total distributed: 1,800,000 GDAO.
- 200,000 GDAO from Tier 3 remain unsold and are returned to the project treasury.

## Common Confusion (6 Bullets With "No.")

- **Does a tiered sale mean higher tiers get more tokens for the same money?** No. Higher tiers pay a higher price per token, which means they receive fewer tokens for the same contribution. Tier 1 is the most favorable price, not Tier 3. The numbering convention can be confusing because in some contexts "higher tier" implies better rewards, but in token sales it usually means later access and worse pricing.

- **Can a buyer participate in multiple tiers with the same wallet?** No. A single wallet address is typically assigned to exactly one tier in the whitelist. If a user wants to participate at a different price level, they must use a different wallet address that has been whitelisted for that tier. The contract enforces this by looking up the tier for the specific address initiating the transaction.

- **Does a tiered sale guarantee that every tier will sell out?** No. Tiers are allocation limits, not purchase guarantees. If only ten people apply for Tier 1 spots, then only ten spots are filled. The remaining tokens in that tier may roll over to a lower tier, remain unallocated, or be burned, depending on the project's specific smart contract rules.

- **Is the tier price the only cost a buyer pays?** No. Buyers must also pay blockchain transaction fees, commonly called gas fees. On a congested network, a gas fee might cost more than the token purchase itself for very small contributions. The tier price is the cost of the token only, not the total cost of participation.

- **Can the project change tier prices after the sale starts?** No. In a properly designed smart contract, tier prices are immutable once the sale begins. If an admin could change prices mid-sale, they could exploit early participants by raising prices after commitments are made. Immutability is a core security property of decentralized tiered sales.

- **Does a tiered sale prevent whales from dominating the token supply?** No. While per-wallet allocation limits reduce the impact of individual whales, a determined actor can simply create multiple wallets and seek whitelist spots for each one. Sybil resistance requires additional mechanisms such as KYC, soulbound tokens, or minimum reputation scores. Tiers alone do not solve whale problems completely.

## Key Properties (5)

1. **Price Discrimination by Commitment.** Tiered sales use price as a tool to reward early and committed supporters. Those who contribute the most to the project before the sale receive the best financial terms. This aligns economic incentives with community building.

2. **Deterministic Access Control.** The whitelist and tier mapping create a deterministic gate. The smart contract does not use randomness or speed-based competition. If you are on the list for Tier 1, you are guaranteed access at that price until the tier's token pool is exhausted.

3. **Bounded Individual Impact.** Each tier enforces a maximum allocation per wallet. This prevents any single participant from purchasing an overwhelmingly large percentage of the supply, promoting broader token distribution and reducing centralization risk.

4. **Composability With Other Mechanisms.** Tiered sales integrate cleanly with vesting schedules, refund mechanisms, and cliff periods. The tier only affects the purchase phase. After purchase, the tokens can flow into a vesting contract or become subject to refund conditions just like tokens bought at any other price.

5. **Transparent Favoritism.** Because tier assignments are stored on-chain, anyone can audit which addresses received preferential pricing. This transparency forces projects to justify their whitelist decisions publicly, reducing the risk of secret insider deals that are common in opaque traditional finance.

## Where It Appears

Tiered sales appear in almost every major token launchpad protocol. On Ethereum, Polkastarter and DAO Maker use tiered systems where token holders of the platform's native token unlock higher allocation tiers. On Solana, Solstarter and Raydium AcceleRaytor implement whitelist-based tiers for project-specific sales. Binance Launchpad operates a lottery tier system where BNB holdings determine ticket eligibility. Beyond dedicated launchpads, many NFT mints use tiered pricing where allowlist members pay less than public minters. In decentralized autonomous organizations, governance token sales often feature contributor tiers that reward early DAO members with better prices. Any blockchain fundraising scenario that involves more than one buyer group and seeks to reward early participation is a candidate for a tiered sale structure.
