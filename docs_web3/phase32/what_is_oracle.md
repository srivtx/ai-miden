# What Is an Oracle

## Why It Exists

Blockchains are deterministic closed systems that cannot directly access external websites, stock markets, or weather APIs.
Without a bridge to off-chain reality, smart contracts cannot settle insurance claims based on rainfall.
They cannot liquidate loans based on asset prices or settle sports bets based on game outcomes.
An oracle solves this isolation by securely importing external data onto the chain.
Contracts can then act upon that data automatically and transparently.
Without oracles, decentralized finance would be limited to trading tokens that already exist on-chain.
Real-world utility would be impossible because the blockchain would have no awareness of events outside its own ledger.

## Definition

An oracle is any service, smart contract, or network node that fetches, verifies, and relays off-chain information to on-chain programs.
It acts as a data bridge between the real world and the deterministic execution environment of a blockchain.
The oracle must ensure data integrity through cryptographic signatures or consensus mechanisms.
Without such verification, smart contracts would have no way to trust the information they receive.

## Real-Life Analogy

Imagine a medieval king locked inside a castle with no windows who must decide tax rates based on the harvest.
Messengers ride to the fields, count the grain, and return with signed scrolls attesting to the yield.
The king does not see the fields himself, but he trusts the sealed message enough to adjust taxes.
The messengers are the oracle, the scroll is the signed data, and the king is the smart contract.

If a messenger arrives without a seal or with a seal from an unknown smith, the king rejects the report.
Multiple messengers may be sent to different regions, and the king averages their findings to avoid fraud.
This redundancy mirrors how decentralized oracle networks operate today.
Multiple independent nodes report data, and outliers are discarded through statistical aggregation.

## Tiny Numeric Example

An oracle network reports the price of SOL in USD:

| Source | Reported Price | Deviation | Included? |
|--------|---------------|-----------|-----------|
| Exchange A | $24.50 | 0.0% | Yes |
| Exchange B | $24.75 | 1.0% | Yes |
| Exchange C | $27.00 | 10.2% | No (outlier) |
| Exchange D | $24.60 | 0.4% | Yes |

The oracle aggregates the included sources to produce a median of $24.60.
It filters out the outlier from Exchange C because it deviates too far from the cluster.
This aggregation protects smart contracts from single-source manipulation or exchange errors.
A lending protocol using this price can safely liquidate positions knowing the value reflects broad market consensus.

## Common Confusion

- An oracle is not a magical source of truth.
  It is only as reliable as its data sources and aggregation logic.
- A single-node oracle is not decentralized.
  It introduces the same trust assumptions as a traditional centralized server.
- Oracles do not guarantee future prices.
  They report snapshots of data that may change in the next block.
- Free public APIs are not suitable for production oracles.
  They lack uptime guarantees and cryptographic attestation.
- Oracle data is not instantly available.
  Updates are batched or pushed on intervals to save gas costs.
- An oracle network is not immune to manipulation.
  Colluding nodes can report false data if the quorum is too low.
- On-chain programs cannot verify oracle data by themselves.
  They rely on signature checks and reputation staking.

## Key Properties
## Where It Appears in Our Code

Oracle consumption logic is implemented in `src_web3/phase32/oracle/src/lib.rs`.
The program verifies the oracle account signature before extracting the reported price.
It also checks the staleness of the data to prevent actions based on outdated information.
The TypeScript API in `src_web3/phase32/price_feed_api.ts` fetches and validates price updates for client applications.
