Why it exists
-------------
Traditional infrastructure is built and maintained by large corporations.
Telecom towers, cloud servers, mapping databases, and energy grids are
controlled by a handful of giants. This creates single points of failure,
high costs, censorship risk, and slow innovation. DePIN exists to solve
this by decentralizing the ownership and operation of physical
infrastructure. Instead of a company building cell towers, a network of
individuals deploys small devices and earns tokens for providing coverage.
Instead of a cloud monopoly storing files, a global mesh of hard drives
competes on price and reliability. DePIN turns physical infrastructure into
a peer-to-peer marketplace where participants are owners, not customers.

Definition
----------
DePIN stands for Decentralized Physical Infrastructure Networks. It refers
to blockchain-based systems that incentivize individuals to deploy and
operate physical hardware that provides real-world services. These services
can include wireless connectivity, geolocation, data storage, compute power,
and energy distribution. Participants earn cryptocurrency rewards for
contributing hardware and maintaining service quality. Smart contracts
manage coordination, payment, and reputation. DePIN combines the economic
incentives of crypto with the tangible utility of physical infrastructure.

Real-life analogy
-----------------
Imagine a city where all the taxis are owned by one company. The company
sets prices, decides which neighborhoods get service, and keeps all the
profits. Now imagine a rideshare platform where anyone with a car can sign
up, set their own schedule, and earn fare revenue. The platform handles
matching, payment, and reputation, but the drivers own the cars and share
the income. DePIN does the same thing for cell towers, solar panels, hard
drives, and GPS beacons. The platform coordinates, but the community owns
the hardware and earns the rewards.

Tiny numeric example
--------------------
A decentralized wireless network operates in a city:
- 1,000 individuals install small hotspot devices on their rooftops.
- Each hotspot provides coverage to a 300-meter radius.
- Users pay 0.001 tokens per megabyte of data transferred.
- Hotspot owners earn 70% of the fees from traffic routed through their
devices.
- The network protocol automatically measures coverage quality and penalizes
  hotspots that are offline or misconfigured.

In one month, Alice's hotspot handles 50 GB of traffic. She earns 0.001 *
50,000 * 0.70 = 35 tokens. Bob's hotspot is poorly placed and handles only
5 GB. He earns 3.5 tokens. The network did not need a telecom company. It
bootstrapped itself through token incentives and community ownership.

Common confusion
----------------
- DePIN is not just crypto for crypto's sake. It provides real physical
  services like internet, storage, and location data.
- DePIN participants are not passive investors. They actively deploy and
  maintain hardware.
- DePIN tokens are not only speculative. They represent payment for actual
  utility consumption.
- DePIN does not eliminate infrastructure costs. It distributes them across
  many participants and replaces corporate margins with token incentives.
- DePIN networks are not unregulated. They still operate within local laws
  regarding radio spectrum, zoning, and safety.
- DePIN is not the same as IoT. IoT connects devices to the internet. DePIN
  creates economic networks around physical infrastructure ownership.
- DePIN quality depends on participation density. A network with ten nodes
  is not useful. A network with ten thousand nodes can rival incumbents.

Where it appears in our code
----------------------------
`src_web3/phase50/depin_api.ts` implements an Express API that simulates
DePIN node registration, coverage mapping, proof-of-location verification,
decentralized storage accounting, and token reward distribution.

Key properties
--------------
- Community-owned: Infrastructure is deployed and owned by individuals.
- Token-incentivized: Rewards drive participation and maintenance.
- Service-oriented: Networks provide real-world utility like bandwidth and
  storage.
- Quality-measured: On-chain metrics track uptime, coverage, and
  performance.
- Scalable: Networks grow organically as more participants join.
- Resilient: No single point of failure because ownership is distributed.
