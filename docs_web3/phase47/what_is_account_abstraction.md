Why it exists
-------------
Traditional blockchain accounts are controlled by a single private key. If you
lose the key, you lose your funds. If someone steals it, they can drain
everything. There is no way to recover, no way to set spending limits, and
no way to pay fees in a token other than the native gas token. Account
abstraction exists to solve this by turning every user account into a smart
contract. This allows programmable access rules, social recovery, multi-
signature security, and sponsored transactions. Without account abstraction,
mass adoption is nearly impossible because the user experience is too
unforgiving for everyday people.

Definition
----------
Account abstraction is a blockchain design pattern that replaces externally
owned accounts with smart contract accounts. Instead of signing transactions
with a private key, users submit UserOperations to a mempool. Bundlers
package these operations into transactions, and an EntryPoint contract
validates and executes them on the smart contract account. The account
contract can enforce any logic: multi-signature rules, daily limits,
recovery mechanisms, or alternate authentication methods. This makes the
account programmable and far more flexible than a traditional keypair.

Real-life analogy
-----------------
Imagine your bank account is a metal safe with one key. Lose the key and
your money is gone forever. Account abstraction is like replacing that safe
with a digital vault. You can set it to require two fingerprints and a PIN.
You can designate three trusted friends who can help you reset the lock if
you forget the PIN. You can set a daily withdrawal limit so a thief cannot
clean you out in one go. The bank itself can even pay the processing fee for
small transfers. The vault is still yours, but the rules around accessing it
are flexible and human-friendly.

Tiny numeric example
--------------------
Alice deploys a smart contract wallet with account abstraction rules:
- Two-factor authentication: both her phone key and her hardware wallet must
  sign any transaction over 1 ETH.
- Daily spending limit: up to 0.5 ETH can be spent with only her phone key.
- Social recovery: three guardians can vote to reset the owner if she loses
  both keys.

Alice wants to send 2 ETH to Bob. She creates a UserOperation and signs it
with both keys. The EntryPoint contract checks the signatures, verifies the
amount exceeds the daily limit, confirms both signatures are present, and
executes the transfer. If Alice had only sent 0.3 ETH, her phone key alone
would suffice. If Alice loses her hardware wallet, she asks two of three
guardians to approve a recovery, and the wallet updates its owner address.

Common confusion
----------------
- Account abstraction does not mean there are no private keys. It means the
  keys are managed by a smart contract instead of the protocol layer.
- UserOperations are not normal transactions. They are structure messages
  that bundlers wrap into actual blockchain transactions.
- Account abstraction does not eliminate gas fees. It allows someone else,
  called a paymaster, to pay the gas on your behalf.
- Smart contract wallets are not the same as multi-sig wallets. Multi-sig is
  one possible configuration, but account abstraction enables much more.
- Not all blockchains support account abstraction natively. Ethereum uses
  ERC-4337 as a layer on top. Some newer chains build it into the protocol.
- Bundlers are not miners. They are specialized nodes that collect
  UserOperations and submit them to the EntryPoint.
- Account abstraction does not make accounts less secure. It makes them more
  secure by allowing programmable guards that traditional accounts lack.

Where it appears in our code
----------------------------
`src_web3/phase47/account_abstraction_api.ts` implements an Express API that
simulates UserOperation submission, bundler packaging, signature validation,
smart contract wallet rules, and paymaster-sponsored transactions.

Key properties
--------------
- Programmable: Accounts can enforce arbitrary access rules and recovery.
- UserOperation-based: Users submit intent-like operations instead of raw
  transactions.
- Bundler-mediated: Specialized nodes package operations for on-chain
  execution.
- Gas abstraction: Paymasters can sponsor gas fees or accept payment in
  ERC-20 tokens.
- Recovery-friendly: Social recovery and multi-factor auth are native
  capabilities.
