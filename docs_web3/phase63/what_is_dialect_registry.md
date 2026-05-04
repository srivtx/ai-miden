# What is the Dialect Registry?

## The Problem

Because Solana Actions and blinks are permissionless, any malicious actor can host an Action API that tricks users into signing drain transactions. If wallets and social platforms automatically unfurled every blink URL, users would be exposed to phishing attacks disguised as donations, swaps, or NFT mints. There must be a mechanism to distinguish legitimate providers from scams.

## Definition

The Dialect Registry is a public, community-maintained directory of verified Solana Action providers. Developed by Dialect in collaboration with the Solana Foundation, it acts as a trust layer that client applications can query before rendering a blink as an interactive card.

## How It Works

1. **Deploy action**: A developer builds a Solana Action, hosts it on a stable HTTPS domain, and ensures it returns valid CORS headers.
2. **Apply for verification**: The developer submits their domain and action details through `dial.to/register`.
3. **Community review**: Dialect and ecosystem reviewers inspect the Action for safety, verify the developer's identity, and test the transactions.
4. **Registry inclusion**: Upon approval, the action's domain and metadata are added to the public registry database.
5. **Client lookup**: When a user posts a blink on a supported platform, the client checks the URL against the Dialect registry.
6. **Conditional unfurling**: If the provider is verified, the blink expands into a rich, interactive card. If not, the link remains a plain text URL that users must click at their own risk.

## Real-life analogy

Think of the Dialect Registry as a notary public's ledger. Anyone can write a contract, but only contracts stamped and recorded by the notary are automatically trusted by banks and courts. The registry does not prevent you from using an unstamped contract, but it warns you that you are operating without verified trust.

## Tiny numeric example

A developer registers `https://alice.com` in the Dialect registry. The registry record contains:

- Domain: `alice.com`
- Verified at: 1715000000 (Unix timestamp)
- Category: `donation`
- Registry status: `verified`

When Alice posts the blink `https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Falice.com%2Factions%2Fdonate` on Twitter, the Twitter client's blink parser performs a registry lookup in ~45 ms. Because `alice.com` is listed, the tweet unfurls into a 320x200 pixel interactive card showing Alice's icon, title, and a Donate button. If Bob posts an unregistered domain `https://scam.io`, the lookup returns `unverified` and the link renders as static text with no interactive elements.

## Common confusion

- No. The Dialect registry is not a smart contract on Solana. It is an off-chain curated database operated by Dialect.
- No. Being unregistered does not mean an Action is malicious. It simply means the provider has not been verified yet.
- No. The registry does not block transactions. It only controls whether a client unfurls a blink into an interactive UI.
- No. Registration is not automatic. Developers must actively apply and pass review before their actions are listed.
- No. The registry is not the only trust model. Wallets and clients can maintain their own allow-lists or use additional verification layers.
- No. Blinks on `dial.to` itself do not require registry verification. Dialect's interstitial site renders all blinks for testing and debugging purposes.

## Key properties

1. **Public good**: Free for developers and clients to use, funded by ecosystem grants rather than user fees.
2. **Permissionless base layer**: Actions work without the registry; verification is an optional trust enhancement.
3. **Client-enforced**: Each wallet or platform decides whether to query the registry and how to handle unverified links.
4. **Identity-linked**: Registration ties Action providers to real-world identity, increasing accountability.
5. **Dynamic**: Providers can be removed from the registry if they later violate safety guidelines.
