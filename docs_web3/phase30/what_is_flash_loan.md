# What is a Flash Loan?

## Why It Exists

Traditional loans require collateral because lenders fear borrowers will disappear with the money.
But on blockchains, transactions are atomic: every step succeeds or the entire transaction reverts.
Flash loans exploit this property by lending billions of dollars with zero collateral, as long as the borrower repays principal plus a fee in the very same transaction.
This enables strategies that would be impossible with traditional finance.
No bank would lend a billion dollars without collateral, but a smart contract can.
This unlocks capital efficiency at a scale never seen before.
Flash loans represent one of the most unique innovations in decentralized finance.

## Definition

A flash loan is an uncollateralized loan that must be borrowed and repaid within a single blockchain transaction.
If the borrower fails to repay by the end of the transaction, the entire transaction reverts and the loan never happened.
The lender is never at risk because the blockchain enforces repayment automatically.
The loan either completes in full or never existed.
There is no default risk because default is impossible by design.
This makes flash loans one of the safest lending mechanisms ever invented.

## Real-Life Analogy

Imagine a magical vending machine that dispenses $1 million in cash, but the machine is inside a locked room that only stays open for ten seconds.
You can grab the money, run across the street to buy a painting you know is undervalued, sell it instantly to a waiting buyer for a profit, run back, and stuff the original $1 million plus a small fee back into the machine before the door slams shut.

If you are even one second late, the room resets.
The money vanishes, the painting unpurchases itself, and nobody is out anything.
That is a flash loan.
The room is the blockchain transaction.
The door slamming is the transaction finalizing.
The vending machine is the liquidity pool.

## Tiny Numeric Example

A trader spots an arbitrage opportunity:

| Step | Action | Amount |
|---|---|---|
| 1 | Borrow 10,000 SOL | +10,000 SOL |
| 2 | Swap SOL for USDC on DEX A | +225,000 USDC |
| 3 | Swap USDC for SOL on DEX B | +10,100 SOL |
| 4 | Repay flash loan + 0.09% fee | -10,009 SOL |
| Net Profit | | 91 SOL |

If step 3 had only returned 9,500 SOL, the repayment in step 4 would fail.
The entire transaction would revert, and the lender would never have been at risk.
The trader only loses the transaction fee.
This is why flash loans are risk-free for lenders.
The entire process completes in a single atomic transaction, ensuring no funds are ever at risk.
The trader needs no capital except for gas fees.
Flash loans democratize access to institutional-scale capital for retail participants.

## Common Confusion

- **"How can you borrow without collateral?"** The blockchain enforces repayment atomically. The loan only exists for the duration of the transaction.
- **"Does the borrower need capital?"** Only for transaction fees, usually a few cents. The borrowed amount itself requires no upfront capital.
- **"What if the borrower runs away with the funds?"** Impossible. The transaction will not finalize unless repayment is included. The runtime enforces this.
- **"Are flash loans only for arbitrage?"** No. They are also used for collateral swaps, liquidations, and refinancing positions.
- **"Can anyone get a flash loan?"** Yes. Flash loans are permissionless. Any address can request any amount the pool has available.
- **"What happens if a protocol bug prevents repayment?"** The transaction reverts. The lender loses nothing, but the borrower pays gas fees for the failed attempt.
- **"Are flash loans risky for the lender?"** No. The lender either gets repaid or the transaction never happened. There is no default risk.
- **"What is the typical fee?"** Usually 0.09% to 0.3% of the borrowed amount, depending on the protocol.
- **"Can flash loans be used for attacks?"** Yes. Attackers have used flash loans to manipulate prices and exploit protocol bugs, which is why security audits are critical.

## Key Properties

- **Atomicity:** The entire loan lifecycle must complete within a single transaction or fully revert.
- **Zero Collateral:** Borrowers need no upfront capital beyond transaction fees to access massive liquidity.
- **Permissionless:** Any address can request a flash loan without approval, credit checks, or KYC.
- **Risk-Free Lending:** Lenders face no default risk because unpaid loans cause automatic transaction reversion.
- **Instant Liquidity:** Provides immediate access to large capital for arbitrage, liquidations, and refinancing.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase30/flash_loan_api.ts` implements an Express API that simulates flash loan execution with pool liquidity checks, fee calculation, and atomic success/failure logic.
