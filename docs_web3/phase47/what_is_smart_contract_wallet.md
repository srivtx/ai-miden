Why it exists
-------------
Traditional wallets are simple key holders. They store a private key, sign
transactions, and nothing more. This is dangerous because a single stolen
key means total loss. Users also cannot set spending limits, schedule
payments, or recover access if they forget their seed phrase. Smart contract
wallets exist to solve this by embedding the wallet logic directly into a
blockchain program. The wallet itself becomes a programmable entity that can
enforce rules, require multiple approvals, and recover from disaster. This
transforms a wallet from a dumb key container into an intelligent financial
agent.

Definition
----------
A smart contract wallet is a blockchain account implemented as a smart
contract rather than a simple keypair. It stores assets and executes
transactions according to programmable rules defined in its code. These
rules can include multi-signature requirements, daily spending limits,
session keys, social recovery, and dead switches. When a user wants to act,
they send a request to the wallet contract, which validates the request
against its rules before executing. This makes the wallet behavior explicit,
auditable, and upgradeable.

Real-life analogy
-----------------
Think of a traditional wallet as a physical wallet in your pocket. If someone
steals it, they have everything inside. Now imagine a smart safe instead.
The safe can be programmed to open only with two different keys turned at the
same time. It can be programmed to dispense only $100 per day. It can be
programmed to call three trusted friends if you forget the combination. And
it can be programmed to forward its contents to your children if you do not
open it for five years. The safe is still yours, but it behaves according to
rules you chose. A smart contract wallet is that safe, running on the
blockchain.

Tiny numeric example
--------------------
Bob deploys a smart contract wallet with these rules:
- Two-of-three multi-sig: any transaction needs two signatures from Bob,
  his hardware wallet, and a trusted friend.
- Daily limit: transactions under 0.2 ETH need only Bob's signature.
- Recovery: if Bob does not sign anything for 90 days, his sister and his
  lawyer can jointly transfer ownership.

Bob sends 0.1 ETH to a merchant using only his phone key. The wallet checks
the amount, sees it is under the daily limit, and executes immediately. Later,
Bob wants to send 1 ETH to an exchange. He signs with his phone key and his
hardware wallet. The wallet verifies both signatures, confirms the two-of-
three rule is met, and executes the transfer. If Bob loses both devices, he
waits 90 days, and his sister and lawyer perform recovery to move funds to a
new wallet.

Common confusion
----------------
- Smart contract wallets are not the same as browser extension wallets like
  MetaMask. MetaMask manages keys. A smart contract wallet is the account
  itself, living on-chain.
- Smart contract wallets do not eliminate private keys. They use keys as
  inputs to programmable rules rather than as direct controllers.
- Smart contract wallets cost more gas to deploy because they are programs,
  not simple accounts. The extra cost is the price of programmability.
- Not every dApp supports smart contract wallets out of the box. Some older
  contracts assume the caller is an externally owned account.
- Smart contract wallets can be upgraded if designed with proxy patterns.
  This is a feature, not a bug, because it allows security patches.
- Smart contract wallets are not inherently less secure. Their security
  depends on the quality of the code and the rules chosen by the owner.
- Smart contract wallets can hold any token or NFT that a normal address can
  hold because they are valid blockchain addresses.

Where it appears in our code
----------------------------
`src_web3/phase47/account_abstraction_api.ts` implements an Express API that
simulates smart contract wallet deployment, rule validation, multi-signature
checking, and recovery workflows.

Key properties
--------------
- Programmable rules: Owners define how transactions are authorized.
- Multi-signature: Multiple keys can be required for sensitive actions.
- Recovery: Guardians can restore access if keys are lost.
- Session keys: Temporary limited permissions can be granted to apps.
- Upgradeable: Wallet logic can be improved without changing the address.
- Gas overhead: Each action involves contract execution, which costs more
  than a simple transfer.
