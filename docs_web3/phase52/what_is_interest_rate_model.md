# Interest Rate Model

## The Problem

If a lending protocol charges a flat interest rate regardless of demand, the market becomes inefficient. When almost all deposits are borrowed, lenders face high risk of bank runs and low liquidity. When utilization is low, borrowers pay too much and lenders earn too little. An Interest Rate Model dynamically adjusts rates to balance supply and demand.

## Definition

An Interest Rate Model is an algorithmic formula used by a lending protocol to calculate the borrowing rate and the lending yield based on the current utilization rate of the pool. Higher utilization leads to higher borrow rates, which incentivizes repayment and new deposits.

## How It Works

1. **Calculate utilization rate**: The protocol divides total borrowed tokens by total deposited tokens.
2. **Define rate curves**: The protocol sets a base rate, slope 1, slope 2, and an optimal utilization point.
3. **Apply piecewise function**: Below optimal utilization, rates rise slowly with slope 1. Above optimal utilization, rates rise steeply with slope 2.
4. **Set borrow rate**: The computed rate becomes the annual percentage borrowers pay.
5. **Set supply rate**: The protocol derives the lending yield by taking a portion of the total interest paid, after reserving a protocol fee.
6. **Update on every state change**: Deposits, borrows, repays, and liquidations all trigger a re-calculation so rates are always current.

## Real-life Analogy

Imagine an airline pricing tickets. When the plane is mostly empty, ticket prices are low to attract buyers. As seats fill up, prices climb because demand is high and supply is scarce. The pricing algorithm is the interest rate model, the seats are the pool liquidity, and the passengers are the borrowers.

## Tiny Numeric Example with Liquidation Math

Pool state:
- Total deposits: 1,000,000 USDC
- Total borrowed: 700,000 USDC
- Utilization rate: 700,000 / 1,000,000 = 0.70 or 70 percent

Rate parameters:
- Base rate: 0 percent
- Optimal utilization: 80 percent
- Slope 1: 4 percent
- Slope 2: 75 percent
- Reserve factor: 10 percent

Borrow rate calculation:
Because 70 percent is below optimal 80 percent:
- Borrow rate = Base rate + (Utilization * Slope 1)
- Borrow rate = 0 + (0.70 * 0.04) = 0.028 or 2.8 percent annually

Supply rate calculation:
- Supply rate = Borrow rate * Utilization * (1 - Reserve factor)
- Supply rate = 0.028 * 0.70 * 0.90 = 0.01764 or 1.764 percent annually

Now assume a sudden liquidation event reduces total borrowed to 600,000:
- New utilization: 600,000 / 1,000,000 = 0.60
- New borrow rate: 0 + (0.60 * 0.04) = 0.024 or 2.4 percent
- New supply rate: 0.024 * 0.60 * 0.90 = 0.01296 or 1.296 percent

## Common Confusion

- No, the interest rate model does not set fixed rates for all users forever.
- No, high utilization does not mean lenders cannot withdraw; it means withdrawing is more expensive for borrowers.
- No, the supply rate is not identical to the borrow rate because the protocol takes a reserve cut.
- No, utilization above 100 percent is impossible; it is capped by total deposits.
- No, interest does not compound continuously on-chain unless the protocol explicitly implements compound accrual per block.
- No, the model does not depend on the borrower's individual health factor.

## Key Properties

1. **Demand-responsive**: Rates rise as more capital is borrowed.
2. **Algorithmic**: No manual intervention is needed to adjust rates.
3. **Dual-purpose**: Balances incentives for both lenders and borrowers.
4. **Piecewise linear**: Typically uses a kinked curve to separate low and high stress zones.
5. **On-chain transparent**: The formula and parameters are visible and auditable.

## Where It Appears

Interest rate models appear in Compound, Aave, Solend, Venus, and virtually every pool-based lending market.
