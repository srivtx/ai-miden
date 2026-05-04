# What is a Blink?

## The Problem

Before blinks, every blockchain interaction required users to leave their current context. If a creator posted a donation link on Twitter, followers had to click through to a separate dApp, wait for it to load, connect their wallet, find the donation button, and finally sign. This friction destroyed conversion rates and fragmented user attention across dozens of bookmarked dApps.

## Definition

A blink (blockchain link) is a shareable, metadata-rich URL that turns any Solana Action into an embeddable transaction interface. It allows users to preview, sign, and send blockchain transactions without ever navigating away from the surface where they discovered the link.

## How It Works

1. **Create action**: A developer builds an API endpoint that returns metadata and signable transactions.
2. **Register metadata**: The developer hosts an `actions.json` file at the root of their domain to map website paths to Action API paths.
3. **Generate blink URL**: A client or interstitial site creates a URL with an `action` query parameter containing a URL-encoded `solana-action:` link.
4. **User clicks**: A user encounters the blink on social media, a website, or in a chat message.
5. **Wallet opens**: An Action-aware client (wallet extension, bot, or dApp) detects the blink, decodes the Action URL, and renders an interactive UI.
6. **Signs transaction**: The client fetches the transaction from the Action API, presents it for preview, and the user signs directly in their wallet.

## Real-life analogy

Imagine receiving a birthday gift card in the mail that already has a pen attached. Instead of driving to the store, finding the item, and paying at the register, you simply sign the card and mail it back. The item ships to you. A blink is that pre-addressed, pre-stamped card: everything needed to complete the action is embedded in the link itself.

## Tiny numeric example

A developer hosts a donation Action at `https://alice.com/actions/donate`. The blink URL shared on Twitter looks like this:

```
https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Falice.com%2Factions%2Fdonate
```

When decoded, the `action` parameter resolves to:

```
solana-action:https://alice.com/actions/donate
```

The client makes a GET request to `https://alice.com/actions/donate` and receives a 312-byte JSON payload describing the donation. After the user enters 0.1 SOL and clicks Donate, the client POSTs to the same URL with the user's account public key. The server returns a 1,247-byte base64-encoded transaction. The wallet decodes it, the user signs, and the transaction lands on-chain in 400 ms.

## Common confusion

- No. A blink is not a smart contract. It is a client-side URL primitive that points to an Action API.
- No. Blinks do not store private keys. They are merely links; signing always happens in the user's wallet.
- No. Not every URL is a blink. Only URLs that contain an `action` parameter with a valid `solana-action:` scheme are blinks.
- No. Blinks do not execute transactions automatically. They require explicit user approval and signature in a wallet.
- No. A blink cannot bypass the Action API. The link is useless without the corresponding GET and POST endpoints.
- No. Blinks are not limited to Twitter. Any surface that can display a URL can embed a blink: Discord bots, QR codes, mobile apps, and email newsletters.

## Key properties

1. **Shareable by design**: Any blink URL can be copied, pasted, or embedded across any web surface.
2. **Metadata-rich**: The Action API returns icons, titles, and descriptions that clients render as rich cards.
3. **Wallet-agnostic**: Any Action-aware client can unfurl a blink; there is no single gatekeeper.
4. **Context-preserving**: Users complete transactions without leaving the app or website where they found the link.
5. **Chainable**: A blink can link to a sequence of actions, guiding users through multi-step workflows.
