# What is an Action?

## The Problem

Every on-chain operation today is trapped inside a dApp frontend. If a developer wants to let users vote, donate, or swap from a blog post, a Twitter thread, or a chat bot, they must build an entire web application, host it, and hope users navigate to it. This creates a massive barrier for lightweight, context-specific interactions.

## Definition

A Solana Action is a specification-compliant API endpoint that returns metadata and signable transactions over standard HTTP. It consists of a GET route that describes what the action does and a POST route that returns a base64-encoded transaction for the user's wallet to sign.

## How It Works

1. **Define operation**: The developer decides what on-chain instruction to execute: a token swap, a stake delegation, a SOL payment, or an NFT mint.
2. **Build GET endpoint**: The server responds to GET requests with an `ActionGetResponse` JSON payload containing an icon, title, description, label, and optional linked actions with input parameters.
3. **Build POST endpoint**: The server accepts a JSON body with the user's account public key, constructs the appropriate Solana transaction, sets the fee payer and recent blockhash, and returns it serialized as base64.
4. **Host publicly**: The Action API must be served over HTTPS with valid CORS headers so any client can introspect it.
5. **Client introspection**: An Action-aware client makes a GET request to fetch metadata, renders buttons and input fields, and collects user input.
6. **Transaction delivery**: The client POSTs the user's account to the endpoint, receives the transaction, decodes it, and prompts the wallet to sign and send.

## Real-life analogy

Think of an Action as a self-service kiosk at an airport. You walk up, the screen tells you what flights are available (GET metadata), you enter your passport number and select a seat (user input), and the kiosk prints your boarding pass (POST transaction). You do not need to visit the airline's full website or call an agent. The kiosk is a lightweight, single-purpose interface to a complex backend system.

## Tiny numeric example

Consider a donation Action hosted at `https://charity.org/api/donate`.

GET response (312 bytes):
```json
{
  "type": "action",
  "icon": "https://charity.org/icon.png",
  "title": "Clean Water Fund",
  "description": "Donate SOL to build wells.",
  "label": "Donate",
  "links": {
    "actions": [
      { "label": "Donate 0.1 SOL", "href": "/api/donate?amount=0.1" },
      { "label": "Donate", "href": "/api/donate?amount={amount}", "parameters": [{ "name": "amount", "label": "SOL amount", "type": "number" }] }
    ]
  }
}
```

POST request body:
```json
{ "account": "7fUAJ...9xK2" }
```

POST response (1,247 bytes):
```json
{
  "transaction": "AQIDBAUG...c3Ryk=",
  "message": "Donate 0.5 SOL to Clean Water Fund"
}
```

The base64 string `AQIDBAUG...c3Ryk=` decodes to a 215-byte serialized transaction containing one SystemProgram transfer instruction.

## Common confusion

- No. An Action is not a Solana program. It is an off-chain API that builds transactions targeting on-chain programs.
- No. Actions do not hold custody of funds. They only construct unsigned or partially signed transactions; the user's wallet must sign.
- No. The GET endpoint does not return a transaction. It returns metadata so the client can render a user interface.
- No. Actions are not limited to SOL transfers. Any instruction that can be placed in a Solana transaction can be returned by an Action.
- No. You do not need a frontend to use an Action. Bots, wallets, and mobile apps can introspect Actions directly via HTTP.
- No. Actions cannot force a user to sign. The user always retains full control and must explicitly approve every transaction in their wallet.

## Key properties

1. **REST-like interface**: Uses standard GET/POST HTTP methods and JSON payloads, making it accessible to any HTTP client.
2. **Self-describing**: The GET response carries all metadata needed to render a complete UI without prior knowledge of the endpoint.
3. **Composable**: Multiple linked actions can be offered from a single endpoint, each mapping to different parameters or sub-routes.
4. **Untrusted by default**: Clients must validate all transactions before signing because the server is an untrusted third party.
5. **Chainable**: A POST response can include a `links.next` field to guide the user through a sequence of dependent transactions.
