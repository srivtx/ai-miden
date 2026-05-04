# Phase 37 Summary: Token Vesting with Cliffs

## Overview

Phase 37 explores how blockchain projects retain talent and stabilize token supply through time-locked grants. Vesting schedules prevent immediate sell-offs by releasing tokens gradually, cliffs ensure minimum commitment periods, and linear vesting creates fair and predictable unlock curves. Together these mechanisms turn a simple token transfer into a long-term alignment tool.

## Key Concepts Recap

A vesting schedule is the master plan that defines when tokens become available. A cliff is an initial no-unlock period that tests commitment. Linear vesting is the steady release of equal increments over time. All three work together: the cliff delays the start, and linear vesting distributes the grant evenly afterward.

## Code Deliverables

The TypeScript API in `src_web3/phase37/vesting_api.ts` models token grants with configurable cliffs and linear schedules. It supports creating a grant, querying vested amounts at any timestamp, claiming unlocked tokens, and revoking unvested tokens by the grantor when permitted.

## Relationships Between Concepts

The vesting schedule is the contract. The cliff is a condition inside the contract. Linear vesting is the mathematical function the contract uses to compute unlocked amounts. Without a schedule, there is no structure. Without a cliff, early departures drain value. Without linearity, unlocks become unpredictable and may harm market stability.

## Practical Takeaways

Always use a cliff for new contributors unless they are founders with years of prior commitment. Document grant terms on-chain immutably so disputes are resolved by code, not lawyers. Cap total grants per wallet to prevent a single compromised key from unlocking excessive supply. Test boundary cases such as claiming exactly at the cliff boundary, claiming after full vesting, and attempting to claim twice in rapid succession.

## Conclusion

Vesting is one of the most economically important primitives in token design. It transforms speculation into commitment and aligns the incentives of builders, investors, and communities. Phase 37 builds the foundation for understanding time-locked value, which reappears in governance, staking, and streaming payments throughout the rest of the curriculum.
