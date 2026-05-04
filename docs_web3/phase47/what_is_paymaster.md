Why it exists
-------------
Gas fees are one of the biggest barriers to blockchain adoption. New users
must buy the native token before they can do anything. They cannot pay fees
in stablecoins or loyalty points. They cannot try a dApp without first
navigating an exchange. Paymasters exist to solve this by allowing a third
party to sponsor transaction fees on behalf of users. With a paymaster, a
user can interact with a blockchain without ever holding ETH or SOL. The
paymaster covers the gas, often in exchange for payment in an ERC-20 token,
fiat, or as a marketing subsidy. This removes the onboarding cliff that
stops mainstream users from trying decentralized applications.

Definition
----------
A paymaster is a smart contract or service that pays blockchain transaction
fees on behalf of users. In account abstraction systems like ERC-4337, the
paymaster is a contract that the EntryPoint calls during UserOperation
validation. The paymaster verifies whether it is willing to sponsor the fee,
perhaps by checking a signature, a token balance, or an off-chain approval.
If accepted, the paymaster deposits ETH into the EntryPoint to cover the gas.
Users can then pay the paymaster back in ERC-20 tokens or simply enjoy a
sponsored experience. Paymasters decouple fee payment from transaction
execution.

Real-life analogy
-----------------
Imagine a ride-sharing app that pays the toll bridge fee for you. Normally,
you need cash in your car to cross the bridge. The app says "we will handle
the toll." When your car reaches the bridge, the app automatically pays the
toll operator. You never touch cash. Later, the app might charge your credit
card for the toll, or it might waive the fee as a new-user promotion. The
toll still gets paid, but the payment is abstracted away from your immediate
experience. A paymaster does the same for blockchain gas: the network still
gets paid, but the user does not need to hold the native token.

Tiny numeric example
--------------------
Carol wants to mint an NFT on a chain where she holds USDC but no ETH. She
submits a UserOperation to mint the NFT. The operation includes a paymaster
address that sponsors gas.

The paymaster contract logic:
- Check if Carol has at least 10 USDC in her wallet.
- If yes, sponsor the gas, which costs 0.001 ETH equivalent.
- Deduct 5 USDC from Carol as the paymaster fee.

Carol mints the NFT without ever buying ETH. The paymaster deposits 0.001
ETH into the EntryPoint to cover gas. Carol's USDC balance drops by 5, and
she receives the NFT. The paymaster later converts the 5 USDC to ETH to
replenish its deposit. If Carol had no USDC, the paymaster would reject the
sponsorship and Carol would need to find another paymaster or buy ETH.

Common confusion
----------------
- Paymasters do not make gas free. They shift who pays and in what currency.
- Paymasters are not magic money printers. They must have deposited funds in
  the EntryPoint to cover the gas they sponsor.
- Paymasters do not control user transactions. They only decide whether to
  pay the fee. The user still signs the operation.
- Paymasters are not limited to ERC-20 payments. They can use any logic:
  fiat subscriptions, NFT ownership, whitelist status, or loyalty points.
- Not all paymasters are centralized. A DAO can run a community paymaster
  funded by treasury assets.
- Paymasters do not eliminate the need for gas entirely. They abstract the
  payer identity away from the transaction sender.
- Paymasters can be rate-limited or capped. A sponsor might pay for 10
  transactions per user per day to prevent abuse.

Where it appears in our code
----------------------------
`src_web3/phase47/account_abstraction_api.ts` implements an Express API with
a paymaster simulation that validates user token balances, sponsors gas for
eligible operations, and tracks paymaster deposits and usage.

Key properties
--------------
- Fee abstraction: Users do not need to hold the native gas token.
- Flexible payment: Users can pay in stablecoins, points, or not at all.
- On-chain deposit: Paymasters must prefund the EntryPoint to operate.
- Validation logic: Each paymaster defines its own acceptance criteria.
- Sponsor-friendly: Applications can subsidize onboarding by covering gas.
- Replenishment: Paymasters must manage reserves to avoid running dry.
