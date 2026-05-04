# What Is a Boost NFT?

## The Problem

Standard yield farming treats all capital equally. A whale with $10 million and a retail user with $1,000 receive the same APR. Protocols want to reward long-term commitment, community participation, or specific actions without changing the base economic model. Boost NFTs solve this by giving multipliers to users who hold qualifying NFTs.

## Definition

A boost NFT is a non-fungible token that, when held in a user's wallet and registered with a yield farm, increases that user's effective stake for reward calculations. The boost is expressed as a multiplier applied to the user's base stake amount. Only valid, unexpired, whitelisted NFTs provide boosts.

## How It Works

1. **NFT minting**: The protocol or a partner project mints boost NFTs with embedded metadata including boost multiplier, expiration timestamp, and tier level. This creates scarce, non-fungible incentives.

2. **User acquisition**: Users obtain boost NFTs through airdrops, purchases, achievements, or governance participation. The NFT resides in their wallet as a standard SPL token.

3. **Registration**: The user calls the farm's apply_boost instruction, passing their boost NFT mint. The farm program verifies ownership and validates the NFT against an on-chain whitelist. This links the NFT to the user's farming position.

4. **Reward calculation**: When computing pending rewards, the farm program multiplies the user's staked amount by the NFT's boost factor. A 1.5x boost on 100 tokens means rewards are calculated as if the user staked 150 tokens.

5. **Validation on claim**: Every claim and unstake operation re-verifies NFT ownership. If the NFT has been transferred or burned, the boost is removed immediately. This prevents gaming the system.

6. **Expiration handling**: The protocol checks the NFT's expiration timestamp during each operation. Expired NFTs are automatically ignored, ensuring boosts are temporary and create urgency.

## Real-life Analogy

Imagine a gym membership with loyalty tiers. Everyone pays the same base fee, but members who attend 100 classes receive a gold card that doubles their guest pass allotment. If they lose the card or stop qualifying, the bonus stops. The gym did not change prices for everyone; it added a conditional multiplier.

## Tiny Numeric Example

User A stakes 100 LP tokens. The pool emits 1,000 reward tokens per day. Total pool stake is 1,000 tokens. Without boost, User A earns 100 / 1,000 * 1,000 = 100 reward tokens per day.

User A holds a boost NFT with 2.0x multiplier. Effective stake becomes 100 * 2.0 = 200 tokens.

New total effective stake: 900 (other users) + 200 (boosted) = 1,100.

User A's daily reward: 200 / 1,100 * 1,000 = 181.82 reward tokens.

Other users' rewards are diluted proportionally. The boost redistributes rewards from non-holders to holders.

## Common Confusion

- Does the boost NFT increase my actual token balance? No. It only increases the amount used for reward calculation. Your staked principal remains unchanged.

- Can I use multiple boost NFTs at once? No. The protocol enforces one active boost per user per pool to prevent exponential stacking.

- Is the boost permanent? No. Most boost NFTs have expiration dates or are tied to specific seasons. Check the NFT metadata.

- Can I sell my boost NFT while staking? No. If you transfer the NFT, the next claim or unstake will detect the missing NFT and remove your boost.

- Does the boost affect other users' principal? No. Other users' principal is safe. The boost only affects the reward distribution ratio.

- Are boost NFTs standard SPL tokens? No. They are SPL token mints with supply = 1 and decimals = 0, implementing the Metaplex NFT standard.

## Key Properties

1. **Non-transferable utility**: The boost is tied to ownership at the time of reward calculation, not to the stake itself.

2. **Whitelist enforcement**: Only approved NFT collections are accepted, preventing counterfeit boosts.

3. **Time-bound incentives**: Expiration creates scarcity and drives engagement within specific windows.

4. **Composability**: Boost NFTs can be traded on secondary markets, creating a price discovery mechanism for the utility.

5. **Fair launch compatible**: Protocols can distribute boosts to early supporters without altering tokenomics for everyone.

## Where It Appears

- PancakeSwap NFT profile boosts
- Osmosis superfluid staking with NFT badges
- Various Solana farm protocols with partner NFT integrations
- Gaming-fi projects where in-game NFTs boost yield
