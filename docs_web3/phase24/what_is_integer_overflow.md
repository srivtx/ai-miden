# What Is Integer Overflow?

## Why it exists (THE PROBLEM)

Computers store numbers in fixed-size variables.

When arithmetic exceeds the maximum value that can be represented, the number wraps around to the minimum value, turning a large positive number into a tiny or negative one.

Attackers exploit this to manipulate balances, bypass limits, or mint infinite tokens out of thin air.

## Definition

Integer overflow occurs when an arithmetic operation produces a value outside the range that can be represented by the variable type, causing the value to wrap around silently.

Underflow is the equivalent phenomenon when subtracting below zero, producing an enormous positive number instead of a negative one.

Both are silent killers that bypass normal error handling in release builds.

## Real-life analogy

Imagine an old car odometer with only five digits that rolls over from 99999 to 00000.

If you could somehow add miles without the car actually moving, you could exploit the rollover to make a high-mileage car appear brand new.

Integer overflow is that same mechanical rollover in software.

Adding to a maximum value does not create an error.

It silently resets to zero, which attackers can use to erase debts, inflate balances, or bypass caps that were supposed to protect the system.

## Tiny numeric example

Using a u8 variable that can only hold 0 to 255:

| Operation | Expected | Actual (u8) | Consequence |
|-----------|----------|-------------|-------------|
| 255 + 1 | 256 | 0 | Balance resets to zero |
| 0 - 1 | -1 | 255 | Debt becomes massive credit |
| 200 + 100 | 300 | 44 | Deposit shrinks unexpectedly |

In a DeFi context, a u64 balance of 18 quintillion plus one would wrap to zero, erasing a user's entire deposit or allowing them to mint unlimited tokens.

Auditors always prioritize arithmetic checks because the impact is immediate and total.

Every mathematical operation in a smart contract deserves scrutiny and explicit overflow protection.

Developers should never assume inputs will stay within expected ranges.

## Common confusion

- "Rust prevents all integer overflows."
  Rust panics in debug mode but wraps silently in release mode unless you explicitly use checked arithmetic.

- "Overflow only matters for balances."
  Any numeric field, timestamps, counters, array indices, or loop variables can be vulnerable to exploitation.

- "Using a larger type fixes overflow."
  A u128 still has a maximum.
  The correct fix is checked math, not merely bigger types that postpone the problem.

- "Underflow is less dangerous than overflow."
  Underflow can turn a small debt into a massive positive balance, which is equally catastrophic for financial contracts.

- "Anchor handles overflow automatically."
  Anchor does not automatically check arithmetic.
  Developers must use checked_add, checked_sub, and checked_mul everywhere.

- "Overflow is only a theoretical concern."
  Multiple blockchain exploits have stolen millions by exploiting integer wraparound in lending, staking, and governance contracts.

- "Saturating arithmetic is just as good as checked."
  Saturating math prevents wrap but may hide logic errors.
  Checked math forces explicit error handling.

## Where it appears in our code

- `src_web3/phase24/vulnerable_program.rs`
  Uses standard + and - operators that wrap on overflow in release builds without any protection.

- `src_web3/phase24/secure_program.rs`
  Uses checked_add and checked_sub to abort transactions on overflow and underflow with clear error messages.
