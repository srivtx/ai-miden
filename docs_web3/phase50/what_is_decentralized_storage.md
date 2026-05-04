Why it exists
-------------
Centralized cloud storage providers control vast amounts of human data. They
can raise prices, censor content, lose files to hacks, or shut down
services on a whim. Users have no real ownership of where their data lives.
Decentralized storage exists to solve this by distributing files across a
network of independent nodes. No single entity controls the data. Redundancy
protects against hardware failure. Cryptography protects against tampering.
Incentives ensure nodes stay online and honest. Without decentralized
storage, the internet remains vulnerable to the same concentration risks that
plague traditional finance and infrastructure.

Definition
----------
Decentralized storage is a system where data is split, encrypted, and
distributed across many independent nodes in a peer-to-peer network. Instead
of uploading a file to one company's server, the file is broken into chunks,
each chunk is encrypted, and copies are stored on multiple nodes. Smart
contracts or cryptographic protocols manage access control, payment, and
redundancy. When the owner wants to retrieve the file, the protocol
reassembles the chunks from the available nodes. Decentralized storage
combines resilience, censorship resistance, and user sovereignty.

Real-life analogy
-----------------
Imagine a library where every book is stored in one giant warehouse. If the
warehouse burns down, every book is lost. If the owner decides certain books
are forbidden, they simply remove them. Now imagine a decentralized library
where every book is photocopied into a hundred fragments, and each fragment
is stored in a different person's home. To read the book, you ask the
network to send you the fragments, and you reassemble them. No single home
has the whole book, so no single person can censor it. If ten homes burn
down, you still have ninety copies. Decentralized storage works the same
way: fragmentation, distribution, and redundancy replace central control.

Tiny numeric example
--------------------
Alice uploads a 10 MB photo to a decentralized storage network:
- The network splits the photo into 100 chunks of 0.1 MB each.
- Each chunk is encrypted with Alice's public key.
- The network stores 3 copies of each chunk on different nodes, for a total
  of 300 chunk copies.
- Alice pays 0.01 tokens per month per gigabyte stored.
- Nodes earn 0.003 tokens per month per gigabyte they store, paid by the
  network from Alice's fee.

Bob operates one node with 500 GB of free space. He stores 50 of Alice's
chunk copies and earns 0.003 * 0.005 = 0.000015 tokens per month from
Alice alone. If the network has 1,000 users like Alice, Bob earns 0.015
tokens per month. Alice can download her photo at any time by requesting
the chunks from the network and decrypting them with her private key.

Common confusion
----------------
- Decentralized storage is not the same as a decentralized database. Storage
  holds files. Databases hold structured queryable records.
- Decentralized storage does not mean files are public. Encryption ensures
  only the owner can read the contents.
- Decentralized storage is not free. Users pay nodes for storage space and
  bandwidth, though costs may be lower than centralized alternatives.
- Decentralized storage is not instant. Retrieving fragments from many nodes
  can be slower than downloading from a centralized CDN.
- Nodes cannot read your files if encryption is done correctly. They store
  opaque chunks without the decryption key.
- Decentralized storage does not guarantee infinite persistence. If no one
  pays for storage, nodes may delete chunks to free space.
- Decentralized storage networks use different mechanisms. Some use proof of
  replication, some use proof of spacetime, and some use simple contracts.

Where it appears in our code
----------------------------
`src_web3/phase50/depin_api.ts` implements an Express API that simulates
decentralized storage node registration, file chunk tracking, retrieval
requests, and storage fee accounting.

Key properties
--------------
- Distributed: Files are spread across many independent nodes.
- Encrypted: Contents are unreadable without the owner's key.
- Redundant: Multiple copies protect against node failure.
- Incentivized: Nodes earn tokens for storing and serving data.
- Censorship-resistant: No central authority can delete or block files.
- Programmable: Smart contracts manage access, payment, and persistence.
