## What Is JSON-RPC?

**The Problem:**
Your application needs to talk to a Solana node, but the node runs low-level blockchain software.
How do you format your requests so the node understands them?
You need a standardized protocol for asking questions and receiving answers in a structured format.
This standard must work across languages and platforms.
Without this standard, every developer would invent their own message format, leading to chaos and incompatibility.

**Definition:**
**JSON-RPC** is a lightweight remote procedure call protocol that uses JSON as its data format.
Solana RPC nodes expose a JSON-RPC API over HTTP and WebSocket.
Every request is a JSON object containing a method name, parameters, and an ID.
The response is a JSON object containing the result or an error.

**Structure of a JSON-RPC request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getBalance",
  "params": ["AlicePubkeyHere", {"commitment": "confirmed"}]
}
```

**Structure of a JSON-RPC response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "context": {"slot": 123456789},
    "value": 5000000000
  }
}
```

**Real-life analogy:**
JSON-RPC is like a standardized form at a government office.
The form (request) has fixed fields: "Form Version" (jsonrpc), "Reference Number" (id), "Service Requested" (method), and "Details" (params).
You fill out the form and hand it to the clerk (RPC node).
The clerk processes it and hands back a response form with fields: "Reference Number" (id), "Result" (result), or "Reason for Rejection" (error).
Because every form follows the same template, you can request any service using the same paperwork structure.
Passport renewal, license application, and tax inquiry all use the same form.
The clerk never has to guess what you are asking for.

**Tiny numeric example:**
```
Request:
  POST https://api.devnet.solana.com
  Content-Type: application/json
  Body:
    {"jsonrpc":"2.0","id":1,"method":"getSlot","params":[]}

Response:
  {"jsonrpc":"2.0","id":1,"result":123456789}

Request:
  POST https://api.devnet.solana.com
  Body:
    {"jsonrpc":"2.0","id":2,"method":"getBalance",
     "params":["9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"]}

Response:
  {"jsonrpc":"2.0","id":2,"result":{"context":{"slot":123456790},
   "value":1000000000}}
  // 1,000,000,000 lamports = 1 SOL
```

**Common confusion:**
- **"JSON-RPC is the same as REST."**
  No. REST uses URLs and HTTP verbs (GET, POST, PUT, DELETE).
  JSON-RPC uses a single URL and encodes the action in the request body under the "method" field.
- **"I need to construct raw JSON-RPC manually."**
  You can, but client libraries like @solana/web3.js and solana-client handle serialization for you.
- **"The 'id' field is optional."**
  It is required.
  The ID lets you match responses to requests when sending multiple requests asynchronously.
- **"JSON-RPC only works over HTTP."**
  No. Solana also supports WebSocket JSON-RPC for subscriptions like account changes and slot notifications.
- **"Errors are returned as HTTP 500."**
  No. JSON-RPC errors are returned with HTTP 200 and an "error" field in the JSON body.
  HTTP errors indicate transport problems, not application errors.
- **"All methods require parameters."**
  No. Methods like getSlot and getVersion take empty parameter lists.
- **"I can send multiple requests in one HTTP call."**
  Yes. This is called batching.
  Send a JSON array of request objects, and you receive a JSON array of responses.
- **"JSON-RPC responses always include both result and error."**
  No. A response includes exactly one of "result" or "error," never both.
- **"JSON-RPC is specific to Solana."**
  No. JSON-RPC is a general-purpose protocol used by many blockchains and services.

**Where it appears in our code:**
`src_web3/phase7/rpc_client_demo.rs` — Uses solana_client::rpc_client::RpcClient which wraps JSON-RPC calls in typed Rust methods.
`src_web3/phase7/block_explorer_api.ts` — Express API makes raw JSON-RPC requests and formats the responses for frontend consumption.
