# What Is a Relayer Incentive?

## The Problem

Cross-chain bridges require an off-chain party to observe events on the source chain and deliver proofs to the target chain. This involves running infrastructure, paying gas fees, and maintaining uptime. Without a clear economic reward, no rational actor will perform this service. If no one relays messages, the bridge is non-functional: user tokens are locked on the source chain, but nothing ever mints on the target chain.

## Definition

A Relayer Incentive is an economic mechanism that compensates off-chain agents (relayers) for the cost and effort of transmitting cross-chain messages. Incentives are typically drawn from user-paid fees, inflationary token rewards, or a combination of both, and are distributed upon successful delivery and verification of a message on the destination chain.

## How It Works

1. **Fee Collection**: When a user initiates a bridge transaction, the source contract deducts a fee from the transferred amount or requires an additional native token payment.
2. **Fee Escrow**: The collected fee is locked in a dedicated vault or program account, earmarked for the specific cross-chain message.
3. **Message Relay**: An off-chain relayer monitors the source chain for new events, constructs the proof, and submits a transaction on the target chain.
4. **Delivery Verification**: The target chain contract verifies the proof and records that the message was successfully delivered by a specific relayer address.
5. **Fee Distribution**: Once delivery is confirmed, the target contract unlocks the fee to the relayer. In some designs, a portion is burned or distributed to guardians.
6. **Competition and Anti-Spam**: Multiple relayers may race to deliver the same message. The first successful submission claims the fee; subsequent submissions revert, preventing double payment and encouraging speed.

## Real-Life Analogy

Imagine a courier service between two islands. Every time someone sends a package, they include a stamped, addressed return envelope with payment. Multiple courier boats watch the outgoing dock. The first boat to deliver the package and present the receipt at the destination island collects the payment in the return envelope. Slow or unmotivated boats earn nothing, so only efficient couriers remain in business.

## Tiny Numeric Example with Signatures and Thresholds

Assume a bridge charges a 0.3% relay fee on a 1,000 USDC transfer.

- User sends 1,000 USDC to the bridge lock contract.
- Bridge deducts 3 USDC (0.3%) as the relayer fee and locks it in a fee vault.
- 997 USDC is locked in the main vault.
- Relayer R1 pays 0.001 SOL in gas to submit the mint proof on Solana.
- The proof is verified and the target contract marks R1 as the deliverer.
- The target contract releases the 3 USDC fee to R1.
- R1 net profit: 3 USDC - 0.001 SOL (cost) - server cost.
- If R2 also tries to submit, the target contract sees the message is already delivered and rejects R2's transaction. R2 loses gas.

If the fee were too low (0.01 USDC), no relayer would participate because gas costs exceed revenue. The 0.3% rate ensures positive expected value.

## Common Confusion

- **No.** The relayer does not need to be a guardian. Relayers and guardians are separate roles; one delivers messages, the other signs attestations.
- **No.** Fees are not paid upfront in cash to a specific relayer. They are locked and released only upon on-chain confirmation of delivery.
- **No.** A relayer cannot steal the user's principal tokens. The relayer only submits proofs; the smart contract controls minting and releasing.
- **No.** Higher fees do not guarantee faster delivery in a centralized way. Fees attract more relayers, which increases competition and reduces average delivery time through market forces.
- **No.** Relayers are not punished for failed transactions due to network congestion. They only lose gas, which is why fee design must cover expected gas costs plus margin.
- **No.** Incentives are not always in the bridged token. They can be in the native gas token of the target chain, a governance token, or a stablecoin, depending on the bridge design.

## Key Properties

1. **Cost Coverage**: The fee must exceed the expected gas cost plus infrastructure overhead, or relayers will exit the market.
2. **First-Past-The-Post**: Most designs reward the first successful delivery to prevent redundant transactions and fee dilution.
3. **No Custodial Risk**: The relayer never holds user assets; they only pay gas to move data and are reimbursed from escrowed fees.
4. **Dynamic Adjustability**: Fee rates can be governed on-chain to respond to gas price volatility, ensuring continuous relaying.
5. **Separation of Concerns**: Incentives are distinct from security. Even if all relayers are malicious, they cannot forge guardian signatures to steal funds.

## Where It Appears

- Wormhole's delivery provider marketplace
- Axelar's gas service and relayer rewards
- LayerZero's relayer-verifier fee split
- Chainlink CCIP execution fee
- Custom bridge front-ends that bundle relaying into user fees
