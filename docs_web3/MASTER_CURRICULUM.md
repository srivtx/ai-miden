# Web3 on Solana: The Complete Master Curriculum

> **From Zero to Production-Ready Solana Programs**
>
> Every concept. Every pattern. Every "why."
> Built from scratch in Rust.
> No shortcuts. Nothing skipped.
> Focus: Backend, APIs, Smart Contracts, Real Projects.

---

## How to Read This Map

Each phase has:
- **The Natural Question** — what the student asks after finishing the previous phase
- **New Concepts** — what is introduced (usually 1-3)
- **Why It Is Needed** — the problem this phase solves
- **What We Build** — the actual code project
- **The Analogy** — how to think about it intuitively
- **Connects To** — which future phases build on this

---

## Phase 0: Absolute Zero — What Is Web3?

**The Question:** "What even is Web3?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Web3 | Decentralized internet where users own their data and assets | Instead of renting an apartment (Web2), you own the house (Web3) |
| Blockchain | A shared, tamper-proof ledger that everyone can verify | A public bulletin board where every post is permanent and signed |
| Decentralization | No single company controls the system | A farmers market instead of a Walmart — many sellers, no central owner |
| Trustlessness | You do not need to trust anyone; math guarantees correctness | A vending machine — you put money in, you get a soda, no cashier needed |

**What We Build:** A conceptual map of Web3 vs Web2 vs Web1.

**Leads To:** "How do blockchains actually work under the hood?"

---

## Phase 1: Blockchain Fundamentals (COMPLETED)

**The Question:** "How does a blockchain actually store data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Block | A batch of transactions grouped together | A page in a ledger book |
| Hash | A fingerprint of data; change one bit, hash changes completely | A DNA test for data |
| Chain | Each block contains the previous block's hash, creating an unbreakable link | A pearl necklace where each pearl is welded to the next |
| Immutable | Once written, data cannot be changed without invalidating the entire chain | Etching in stone vs writing in pencil |

**What We Build:** A toy blockchain in Rust — blocks, hashes, chaining.

**Connects To:** Phase 2 (how do you prove ownership on a blockchain?)

---

## Phase 2: Cryptography — Keys and Signatures

**The Question:** "How do you prove you own something without revealing your password?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Private Key | A secret number that proves ownership | Your signature — only you can produce it |
| Public Key | Derived from private key; can be shared safely | Your name — everyone knows it, but they cannot forge your signature |
| Digital Signature | Mathematical proof that a message was signed by a specific private key | A wax seal on a letter — proves it came from the sender |
| Hash Function | One-way function that maps any data to a fixed-size fingerprint | A meat grinder — you can grind meat, but you cannot ungrind it |

**What We Build:** Generate keypairs, sign messages, verify signatures in Rust.

**Connects To:** Phase 3 (how does Solana use these ideas?)

---

## Phase 3: Solana Architecture

**The Question:** "Solana claims to be fast. What makes it different from Ethereum?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Proof of History (PoH) | A cryptographic clock that orders transactions before consensus | A teacher timestamping homework as students turn it in, so the order is known before grading |
| Tower BFT | Solana's consensus mechanism that uses PoH for fast finality | A jury that votes quickly because the timeline of events is already agreed upon |
| Parallel Execution | Solana processes non-overlapping transactions simultaneously | Multiple checkout lanes at a grocery store — different customers, same registers |
| Gulf Stream | Forwarding transactions to validators before the previous block is confirmed | A restaurant kitchen that starts prep work as soon as an order is placed, not when the previous table is served |

**What We Build:** Simulate PoH with a hash chain and measure throughput.

**Connects To:** Phase 4 (where is data actually stored?)

---

## Phase 4: The Accounts Model

**The Question:** "On Ethereum, data lives in contracts. Where does data live on Solana?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Account | Everything on Solana is an account — programs, wallets, token balances | Every file on your computer has an address and contents |
| Program Account | Stores executable code but NO state | A recipe book — it has instructions, but no ingredients |
| Data Account | Stores state but NO code | A pantry — it holds ingredients, but cannot cook |
| Rent | Accounts must pay rent (or be rent-exempt) to exist | Storage unit fees — pay monthly or lose your stuff |
| Lamport | Smallest unit of SOL (1 SOL = 1 billion lamports) | A penny to a dollar |

**What We Build:** Create accounts, inspect their structure, understand rent.

**Connects To:** Phase 5 (how do I write code for Solana?)

---

## Phase 5: Development Environment

**The Question:** "What tools do I need to build on Solana?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Solana CLI | Command-line tool to interact with the blockchain | A Swiss Army knife for Solana |
| Rust | Systems language for writing Solana programs | The language of Solana smart contracts |
| Anchor | Framework that makes Solana development easier | Rails for Ruby, Anchor for Solana |
| Local Validator | A simulated blockchain running on your laptop | A flight simulator for blockchain development |

**What We Build:** Install toolchain, start a local validator, airdrop SOL.

**Connects To:** Phase 6 (how do I send my first transaction?)

---

## Phase 6: Your First Transaction

**The Question:** "How do I actually move SOL from one wallet to another?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Transaction | A signed message that instructs the blockchain to do something | A signed check that tells the bank to transfer money |
| Instruction | A single operation inside a transaction | One line item on a check |
| Payer | The account that pays for transaction fees | The person who pays for postage |
| Recent Blockhash | A reference to a recent block that prevents replay attacks | A timestamp on a contract that makes it expire if not processed soon |

**What We Build:** A Rust client that creates a wallet, airdrops SOL, and sends a transfer.

**Connects To:** Phase 7 (how do I read data from the blockchain?)

---

## Phase 7: Reading Blockchain Data

**The Question:** "How do I query balances, transaction history, and account data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| RPC Node | A server that answers questions about the blockchain | A librarian who knows every book in the library |
| JSON-RPC | The protocol for asking questions | The language you speak to the librarian |
| Commitment Level | How "sure" you want the answer to be (processed, confirmed, finalized) | "Is the check cleared?" vs "Has the check been deposited?" vs "Is the money in my account?" |

**What We Build:** A Rust RPC client that queries balances, account info, and transaction history.

**Connects To:** Phase 8 (how do I write my own program?)

---

## Phase 8: Writing Your First Program

**The Question:** "Can I write code that runs on the blockchain?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Program | Smart contract on Solana — code that runs on-chain | A vending machine's internal logic — deterministic, tamper-proof |
| Entrypoint | The function that Solana calls when your program is invoked | The "main" function of a smart contract |
| Processor | The function that handles the logic | The brain of the vending machine |

**What We Build:** A "Hello World" program that logs a message when called.

**Connects To:** Phase 9 (how do I store data?)

---

## Phase 9: Program State with Accounts

**The Question:** "My program needs to remember things. Where does it store data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| State Account | An account owned by a program that stores persistent data | A database row that belongs to your application |
| Serialization | Converting Rust structs to bytes for storage | Packing clothes into a suitcase for travel |
| Borsh | Binary serialization format used on Solana | A specific packing method — efficient and predictable |

**What We Build:** A counter program that increments and stores a number.

**Connects To:** Phase 10 (how do I create predictable addresses?)

---

## Phase 10: Program Derived Addresses (PDA)

**The Question:** "How do I create an address that is guaranteed to be unique and controlled by my program?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| PDA | An address derived from a program ID and seeds, not from a private key | A PO Box — the post office controls it, not a person |
| Bump | A number that ensures the derived address is off the elliptic curve | A retry counter — try 1, try 2, until you find a valid address |
| Seeds | Arbitrary data used to derive a PDA | Your PO Box number — unique to you |

**What We Build:** A program that creates a PDA and stores data in it.

**Connects To:** Phase 11 (how do programs call other programs?)

---

## Phase 11: Cross-Program Invocation (CPI)

**The Question:** "Can my program call another program, like the token program?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| CPI | One program calling another program on-chain | A general contractor hiring subcontractors |
| Program ID | The unique address of a deployed program | A company's business license number |
| Invoke Signed | A CPI that uses a PDA to sign on behalf of a program | A power of attorney — the program acts on behalf of the PDA |

**What We Build:** A program that CPIs into the system program to create an account.

**Connects To:** Phase 12 (how do tokens work?)

---

## Phase 12: SPL Tokens

**The Question:** "How do I create my own cryptocurrency on Solana?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| SPL Token | Solana's token standard (like ERC-20 on Ethereum) | A standardized form for creating new currencies |
| Mint | The account that defines a token (supply, decimals) | A government mint that prints money |
| Token Account | Holds a balance of a specific token for a specific owner | Your wallet — holds a specific currency |
| Associated Token Account (ATA) | A deterministic token account derived from owner + mint | Your default checking account for a specific currency |

**What We Build:** Create a token, mint tokens, and query balances.

**Connects To:** Phase 13 (how do I build a token vault?)

---

## Phase 13: Token Vault Program

**The Question:** "How do I build a secure place for users to deposit and withdraw tokens?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Vault | A program-controlled account that holds user deposits | A bank vault — customers deposit, the bank secures |
| Authority | Who is allowed to do what | A bank manager with a keycard |
| Deposit/Withdraw | Moving tokens into and out of program control | Depositing cash at the teller, withdrawing from the ATM |

**What We Build:** A vault program where users deposit SPL tokens and withdraw later.

**Connects To:** Phase 14 (how do I build an escrow?)

---

## Phase 14: Escrow Program

**The Question:** "How do two people trade without trusting each other?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Escrow | A third party holds assets until conditions are met | A real estate escrow — money is held until the deed is transferred |
| Atomic Swap | Both sides of a trade happen together or not at all | A simultaneous exchange — I hand you the bike, you hand me the cash, at the exact same moment |
| Trade Matching | Finding a buyer and seller who agree on terms | A dating app for trades |

**What We Build:** An escrow program where Alice deposits Token A, Bob deposits Token B, and the program swaps them atomically.

**Connects To:** Phase 15 (how do multiple people control one account?)

---

## Phase 15: Multi-Signature Program

**The Question:** "How can a group of people control a treasury together?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Multi-Sig | Requires M out of N signatures to execute a transaction | A nuclear launch requiring two keys turned simultaneously |
| Threshold | The minimum number of signers required | "3 out of 5 board members must approve" |
| Signer Set | The list of addresses allowed to sign | The board of directors |

**What We Build:** A multi-sig program where 2-of-3 signers must approve any spend.

**Connects To:** Phase 16 (how do I add time locks?)

---

## Phase 16: Time-Locked Vault

**The Question:** "How do I lock funds until a specific time?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Time Lock | Funds are inaccessible until a certain time or block | A timed safe that opens only at 9 AM |
| Clock Sysvar | Solana's on-chain clock that programs can read | The blockchain's wristwatch |
| Vesting | Releasing tokens gradually over time | A 401k that vests over 4 years |

**What We Build:** A vault that locks SOL until a future timestamp.

**Connects To:** Phase 17 (how do decentralized exchanges work?)

---

## Phase 17: Automated Market Maker (AMM)

**The Question:** "How do decentralized exchanges set prices without an order book?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| AMM | Uses a mathematical formula (x*y=k) to price assets | A vending machine that prices soda based on how much is left |
| Constant Product | x * y = k ensures liquidity is always available | A seesaw — as one side goes up, the other goes down |
| Liquidity Provider | Someone who deposits both tokens to earn fees | A market maker at a stock exchange |
| Slippage | Price change between quote and execution | The difference between the sticker price and what you actually pay |

**What We Build:** A simple AMM program with x*y=k pricing.

**Connects To:** Phase 18 (how do liquidity pools work?)

---

## Phase 18: Liquidity Pool

**The Question:** "How do I create a pool where people can deposit tokens and earn fees?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Liquidity Pool | A smart contract holding two tokens for trading | A currency exchange booth at an airport |
| LP Token | Receipt given to liquidity providers representing their share | A share certificate in a company |
| Fee Accrual | Trading fees are distributed to LPs proportionally | Dividends paid to shareholders |
| Impermanent Loss | LPs can lose money compared to just holding | A two-horse race where you bet on both, but one wins by a lot |

**What We Build:** A liquidity pool program with fee collection and LP tokens.

**Connects To:** Phase 19 (how does staking work?)

---

## Phase 19: Staking Program

**The Question:** "How do I reward users for locking up their tokens?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Staking | Locking tokens to earn rewards | A certificate of deposit at a bank — lock money, earn interest |
| Reward Pool | Tokens set aside for distribution as rewards | A prize pool for a contest |
| APY | Annual percentage yield — the rate of return | Interest rate on a savings account |
| Unstaking | Withdrawing staked tokens (often with a cooldown) | Breaking a CD early — possible, but you might lose some interest |

**What We Build:** A staking program where users lock tokens and earn rewards over time.

**Connects To:** Phase 20 (how does lending work?)

---

## Phase 20: Lending Protocol

**The Question:** "How do I build a bank that lends crypto without human approval?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Collateral | Assets deposited to secure a loan | A house mortgage — the house is collateral |
| Liquidation | Selling collateral when its value drops below a threshold | A pawn shop selling your item if you do not repay |
| Health Factor | Ratio of collateral value to borrowed value | Credit score — above 1.0 is safe, below is danger |
| Flash Loan | Borrow without collateral, repay in the same transaction | A 0% interest credit card that must be paid off the same day |

**What We Build:** A lending program where users deposit collateral and borrow tokens.

**Connects To:** Phase 21 (how do NFTs work on Solana?)

---

## Phase 21: NFT Minting Program

**The Question:** "How do I create unique digital collectibles on Solana?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| NFT | Non-fungible token — unique, non-interchangeable | A one-of-a-kind painting vs. a dollar bill |
| Metaplex | The standard for NFTs on Solana | The art gallery that sets the rules for displaying art |
| Metadata | Information about the NFT (name, image, attributes) | The placard next to a painting in a museum |
| Master Edition | The original NFT that can mint limited copies | A printmaker's plate that can produce numbered prints |

**What We Build:** A program that mints NFTs with metadata.

**Connects To:** Phase 22 (how do I build an NFT marketplace?)

---

## Phase 22: NFT Marketplace Program

**The Question:** "How do people buy and sell NFTs on-chain?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Listing | Putting an NFT up for sale at a specific price | Putting a house on the market |
| Offer | A bid to buy an NFT at a specific price | Making an offer on a house |
| Royalty | A percentage of each sale goes to the original creator | An author earning royalties on book sales |
| Escrow for NFTs | Holding the NFT until payment is confirmed | An art dealer holding the painting until the wire transfer clears |

**What We Build:** A marketplace program where users list, buy, and sell NFTs.

**Connects To:** Phase 23 (how do I update my program?)

---

## Phase 23: Program Upgradeability

**The Question:** "What if I find a bug after deploying? Can I fix it?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Upgrade Authority | The address with permission to update a program | A landlord with the key to your apartment |
| Buffer Account | Temporary storage for the new program binary | A staging area for a software update |
| Immutable Program | A program with no upgrade authority — forever fixed | A tattoo — once done, it is permanent |
| Re-deploy | Replacing the program binary at the same address | Replacing the engine in a car without changing the license plate |

**What We Build:** Deploy a program, upgrade it, and set upgrade authority.

**Connects To:** Phase 24 (how do I prevent bugs?)

---

## Phase 24: Security Best Practices

**The Question:** "What are the most common ways Solana programs get hacked?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Re-entrancy | A program calls itself before finishing, causing loops | A recursive phone call — "Hey, can you do X?" "Sure, but first can you do Y?" "Sure, but first can you do X?" |
| Integer Overflow | Numbers wrap around when they get too big | An odometer rolling over from 999,999 to 0 |
| Account Validation | Verifying that accounts are what you expect | Checking ID before letting someone into a secure building |
| Signer Checks | Ensuring the right person signed the transaction | A bouncer checking the guest list |
| Rent Drain | An attacker drains rent from an account to delete it | A squatter draining the bank account of the person paying the mortgage |

**What We Build:** Analyze vulnerable code and fix each issue.

**Connects To:** Phase 25 (how do I test my programs?)

---

## Phase 25: Testing and Fuzzing

**The Question:** "How do I make sure my program works before deploying real money?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Unit Test | Testing individual functions in isolation | Testing a car's brake system before testing the whole car |
| Integration Test | Testing the whole program end-to-end | A test drive |
| Fuzzing | Throwing random inputs at your program to find edge cases | A crash test dummy — hitting the car in unexpected ways |
| Code Coverage | Measuring how much of your code is tested | A map showing which roads you have driven |

**What We Build:** A comprehensive test suite for our escrow program.

**Connects To:** Phase 26 (how do I build a custom API?)

---

## Phase 26: Building a Custom RPC API Service

**The Question:** "How do I build a backend API that interacts with Solana for my app?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| API Service | A server that abstracts blockchain complexity for frontend apps | A translator who speaks both English and Blockchain |
| Rate Limiting | Preventing too many requests from overwhelming the service | A toll booth that limits traffic |
| Caching | Storing frequently requested data to reduce RPC calls | A photo album — instead of taking a new photo, you show the old one |
| Webhooks | Notifications when on-chain events occur | A doorbell — rings when someone arrives |

**What We Build:** A Rust/Actix API that wraps Solana RPC calls with caching and rate limiting.

**Connects To:** Phase 27 (how do I index on-chain data?)

---

## Phase 27: Indexing On-Chain Data

**The Question:** "Querying the blockchain for every request is slow. How do I build a database of on-chain events?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Indexer | A service that listens to blockchain events and stores them in a database | A court stenographer who transcribes every word into a searchable document |
| Event Parser | Decoding on-chain transaction data into human-readable events | A translator converting shorthand to full sentences |
| Database Sync | Keeping an off-chain database in sync with the blockchain | A shadow — it moves exactly with you |
| GraphQL | A query language for APIs | Asking a librarian for specific books instead of reading the entire catalog |

**What We Build:** An indexer that listens for token transfers and stores them in PostgreSQL.

**Connects To:** Phase 28 (how do I build a payment gateway?)

---

## Phase 28: Payment Gateway

**The Question:** "How do I accept SOL and USDC payments on my website?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Payment Intent | A request to pay a specific amount | An invoice |
| Payment Verification | Confirming the payment on-chain | A cashier checking that the $20 bill is real |
| Webhook Notification | Alerting your server when payment is confirmed | A receipt printer — it prints when the payment goes through |
| Refund | Returning funds to the payer | A return policy at a store |

**What We Build:** A payment gateway API that generates payment addresses, verifies receipts, and handles webhooks.

**Connects To:** Phase 29 (how do programs compose together?)

---

## Phase 29: Cross-Program Composability Patterns

**The Question:** "How do I build a protocol that uses multiple other protocols?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Composability | Programs can be combined like LEGO blocks | A smartphone — camera + GPS + music player, all in one device |
| Interface | A standard that programs agree to implement | A USB port — any device with a USB plug works with any USB port |
| Permissionless Integration | Anyone can use your program without asking | A public library — anyone can borrow a book |
| Building Blocks | Small, focused programs that do one thing well | Screws, nuts, and bolts — simple pieces that build complex machines |

**What We Build:** A yield aggregator that composes staking, lending, and AMM protocols.

**Connects To:** Phase 30 (how do flash loans work?)

---

## Phase 30: Flash Loans

**The Question:** "How can someone borrow millions with no collateral and pay it back in seconds?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Flash Loan | Borrow any amount, use it, repay it — all in one transaction | Borrowing your friend's car for 5 minutes to move a couch |
| Arbitrage | Buying low on one exchange and selling high on another | Buying sneakers for $100 at one store and selling them for $150 on eBay |
| Atomicity | The entire transaction succeeds or fails as a whole | An all-or-nothing bet — either you win everything or lose nothing |
| MEV (Maximal Extractable Value) | Profit extracted by reordering transactions | A ticket scalper who buys front-row seats before anyone else |

**What We Build:** A flash loan receiver program that performs arbitrage.

**Connects To:** Phase 31 (how does governance work?)

---

## Phase 31: Governance and DAOs

**The Question:** "How do decentralized organizations make decisions?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| DAO | Decentralized Autonomous Organization — rules encoded in smart contracts | A co-op grocery store where members vote on what to stock |
| Proposal | A suggested change to the protocol | A ballot measure |
| Vote | Token holders cast votes proportional to their holdings | Shareholders voting at a board meeting |
| Quorum | Minimum participation required for a vote to be valid | A minimum number of board members must be present |
| Timelock | Delay between vote passing and execution | A cooling-off period before a law goes into effect |

**What We Build:** A governance program where token holders create proposals, vote, and execute changes.

**Connects To:** Phase 32 (how do oracles work?)

---

## Phase 32: Oracle Integration

**The Question:** "How do smart contracts know the price of Bitcoin or the weather in Tokyo?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Oracle | A bridge between the blockchain and the real world | A reporter who calls the blockchain from the outside world |
| Price Feed | Real-time asset prices pushed on-chain | A stock ticker |
| Pyth / Chainlink | Decentralized oracle networks | A jury of reporters — consensus determines the truth |
| Data Verification | Ensuring oracle data is accurate and untampered | Cross-referencing facts across multiple newspapers |

**What We Build:** A program that reads a price feed and executes trades based on it.

**Connects To:** Phase 33 (how do I protect against MEV?)

---

## Phase 33: MEV Protection

**The Question:** "How do I prevent bots from front-running my users' transactions?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Front-Running | Seeing a pending transaction and submitting yours first with higher fees | A line-cutter who sees you ordering and jumps ahead |
| Sandwich Attack | Front-running a buy, then back-running a sell | Buying a stock before someone else, then selling it to them at a higher price |
| Private Mempool | A hidden queue where transactions are not visible to bots | A VIP entrance where no one can see who is coming |
| Slippage Protection | Limiting how much the price can move against the user | A price ceiling on a contract — you will not pay more than X |

**What We Build:** A swap program with slippage protection and private transaction routing.

**Connects To:** Phase 34 (how do I compress account data?)

---

## Phase 34: Account Compression

**The Question:** "Storing data on-chain is expensive. How do I store millions of items cheaply?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Merkle Tree | A tree of hashes that allows efficient verification of membership | A family tree where you can verify ancestry by checking a few branches |
| Concurrent Merkle Tree | A Merkle tree that supports multiple updates at once | A shared family tree where multiple relatives can add new members |
| Compressed NFTs | NFTs stored off-chain with only a Merkle root on-chain | A library catalog — the books are in storage, but the catalog is at the front desk |
| Light Client | A client that verifies transactions without storing all data | Reading a book summary instead of the whole book |

**What We Build:** A compressed NFT mint using concurrent Merkle trees.

**Connects To:** Phase 35 (how do I deploy to production?)

---

## Phase 35: Production Deployment & CI/CD

**The Question:** "How do I deploy my program to mainnet safely and reliably?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Devnet / Testnet / Mainnet | Three networks for development, testing, and production | A dress rehearsal, a preview show, and opening night |
| Program ID | The permanent address of a deployed program | A business's permanent address |
| Verified Build | A program binary that matches the open-source code | A certified organic label — third-party verified |
| CI/CD Pipeline | Automated testing and deployment | An assembly line that builds and tests every car |
| Mainnet Checklist | Steps to verify before deploying real money | A pilot's pre-flight checklist |

**What We Build:** A CI/CD pipeline that builds, tests, and deploys a program to devnet, then mainnet.

---

## Summary

Through **36 phases** (0-35), you will go from "What is a blockchain?" to deploying production-grade Solana programs:

1. **Web3 Foundations (0-5)** — Blockchain, cryptography, Solana architecture, accounts, dev environment
2. **First Transactions (6-7)** — Sending SOL, reading blockchain data
3. **First Programs (8-11)** — Hello World, state storage, PDAs, CPI
4. **Token Projects (12-14)** — SPL tokens, vault, escrow
5. **Advanced Programs (15-20)** — Multi-sig, time locks, AMM, liquidity, staking, lending
6. **NFTs (21-22)** — Minting, marketplace
7. **Operations (23-25)** — Upgrades, security, testing
8. **Backend APIs (26-28)** — RPC service, indexing, payment gateway
9. **DeFi Deep Dive (29-30)** — Composability, flash loans
10. **Advanced Topics (31-35)** — Governance, oracles, MEV protection, compression, deployment

**This is not a tutorial. This is a complete education in Solana backend development.**
