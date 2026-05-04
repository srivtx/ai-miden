# What is Helius?

## The Problem

Default public RPC endpoints drop transactions under load, enforce strict rate limits (typically 100 requests per 10 seconds), provide no archival data access, and offer zero visibility into why transactions fail. When you build on `api.mainnet-beta.solana.com`, you compete with every other developer for the same scarce connection pool. Your dApp experiences timeouts, stale data, and failed transaction submissions that you cannot debug.

## Definition

Helius is a managed RPC infrastructure provider for Solana that offers staked connections, enhanced APIs, webhook-based indexing, transaction optimization, archival data access, and analytics dashboards. It replaces the default public RPC with a production-grade endpoint that scales with your application.

## How It Works

1. **Staked connection**: Helius runs validators with staked SOL, giving their RPC nodes higher priority in the network gossip protocol and faster access to leaders.
2. **Enhanced APIs**: Provides enriched endpoints like `getPriorityFeeEstimate`, `getAsset`, and `getTokenAccounts` that return computed data the base RPC does not expose.
3. **Webhook indexing**: Instead of polling, you configure webhooks that push account changes, transaction events, and NFT updates to your server in real time.
4. **Transaction optimization**: The `sendSmartTransaction` API bundles priority fees, simulation, and retry logic into a single call.
5. **Archival data**: Queries historical account states and transactions without running your own archival node.
6. **Analytics**: Dashboards showing RPC usage, error rates, and webhook delivery latency.

## Real-life analogy

Think of the default public RPC as a crowded post office with one clerk. Helius is a courier service with dedicated lanes, real-time tracking, and insured delivery. You still send mail, but it arrives faster and you know exactly what happened if it does not.

## Tiny numeric example

A request to `https://mainnet.helius-rpc.com/?api-key=YOUR_KEY` with the body:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getPriorityFeeEstimate",
  "params": [
    {
      "accountKeys": ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"],
      "options": { "includeAllPriorityFeeLevels": true }
    }
  ]
}
```

Returns:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "priorityFeeLevels": {
      "min": 0,
      "low": 1000,
      "medium": 10000,
      "high": 50000,
      "veryHigh": 100000,
      "unsafeMax": 1000000
    }
  },
  "id": 1
}
```

The `medium` level of 10,000 micro-lamports means you attach a priority fee of 0.00001 SOL per compute unit to land your transaction ahead of unfee’d transactions.

## Common confusion

- No. Helius is not a validator you delegate stake to. It is an RPC and indexing infrastructure provider.
- No. Using Helius does not make your transactions free. You still pay Solana network fees and priority fees.
- No. Helius webhooks are not the same as WebSocket subscriptions. Webhooks push to your HTTPS endpoint; WebSockets stream over a persistent connection.
- No. The `getPriorityFeeEstimate` endpoint does not submit transactions. It only returns a recommended fee.
- No. Helius archival data is not stored forever for free. Retention depends on your pricing tier.
- No. Switching to Helius does not require changing your program IDs or instruction formats. You only change the RPC URL.

## Key properties

1. **Staked RPC nodes**: Higher network priority than unstaked public RPCs.
2. **Enhanced APIs**: Computed endpoints that extend the base Solana JSON-RPC spec.
3. **Webhook indexing**: Push-based real-time data instead of polling.
4. **Transaction optimization**: Bundled simulation, priority fees, and retry logic.
5. **Analytics dashboard**: Observability into RPC usage and error rates.
