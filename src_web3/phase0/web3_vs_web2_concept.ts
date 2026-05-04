import { createHash } from "crypto"; // We import createHash to generate content-addressable identifiers for Web3 data integrity proofs.

// PHASE 0: Web3 vs Web2 Concept in TypeScript
// This file demonstrates the paradigm shift using Node.js types and hashing.

/// Represents a Web2 platform API where a single company owns all state.
/// We use a class because Web2 platforms encapsulate hidden business logic.
class Web2Platform {
    private owner: string; // The owner field stores the entity that can unilaterally change rules or ban users.
    private userData: Map<string, string>; // A private Map simulates the hidden corporate database users cannot audit.
    private revenueSharePercent: number; // Revenue share is private because Web2 platforms do not disclose terms transparently.

    constructor(owner: string) { // Constructor establishes centralized control at the moment of creation.
        this.owner = owner; // Stores the owner string for later reference.
        this.userData = new Map(); // Initializes empty Map because no users exist yet.
        this.revenueSharePercent = 50.0; // Sets default extraction rate.
    }

    storeData(username: string, data: string): void { // Stores user data in the central Map to simulate a server-side database write.
        this.userData.set(username, data); // Adds the key-value pair to the centralized map.
    }

    getRevenueShare(): number { // Returns revenue share so we can expose extraction rates for comparison.
        return this.revenueSharePercent; // Returns the stored percentage.
    }

    getOwner(): string { // Returns the owner to show who has administrative power over the data.
        return this.owner; // Returns the stored owner string.
    }
}

/// Represents a Web3 peer where users hold their own keys and data.
/// We use a class to encapsulate the peer's local state and cryptographic identity.
class Web3Peer {
    publicKey: string; // Public key acts as pseudonymous identity without requiring email or KYC.
    localData: Map<string, string>; // Local Map simulates self-custody: only this peer controls this data.
    protocolFeePercent: number; // Protocol fee is public and immutable to demonstrate transparent economics.

    constructor(publicKey: string) { // Constructor creates a peer with a cryptographic address, not a username.
        this.publicKey = publicKey; // Stores the public key string for later reference.
        this.localData = new Map(); // Initializes empty Map because the peer starts with no data.
        this.protocolFeePercent = 2.0; // Sets minimal transparent fee.
    }

    storeData(data: string): string { // Stores data locally under a SHA-256 hash to demonstrate content-addressable storage.
        const hash = createHash("sha256").update(data).digest("hex").slice(0, 16); // We hash the content so the key is derived from the data itself, proving integrity.
        this.localData.set(hash, data); // Adds the hash-data pair to the local map.
        return hash; // Returns the hash so the caller can verify the content later.
    }

    getProtocolFee(): number { // Returns the low protocol fee for direct numeric comparison with Web2.
        return this.protocolFeePercent; // Returns the stored percentage.
    }
}

const web2 = new Web2Platform("BigTech Inc"); // Instantiate a Web2 platform to represent a typical cloud service.
web2.storeData("alice", "alice's photos and messages"); // Store user data centrally so we can later contrast ownership models.

const web3Peer = new Web3Peer("0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"); // Instantiate a Web3 peer with a hexadecimal address string.
const contentHash = web3Peer.storeData("alice's encrypted content"); // Store data locally and capture the content hash for verification.

console.log(`Web2 platform takes ${web2.getRevenueShare()}% of revenue`); // Log revenue extraction so the economic difference is immediately visible.
console.log(`Web3 protocol takes ${web3Peer.getProtocolFee()}% of revenue`); // Log the low Web3 fee for direct contrast.

const savingsMultiplier = web2.getRevenueShare() / web3Peer.getProtocolFee(); // Compute savings multiplier to quantify the benefit for creators.
console.log(`Creator keeps ${savingsMultiplier.toFixed(1)}x more in Web3`); // Output the computed savings multiplier.

console.log(`Web2 data controlled by: ${web2.getOwner()}`); // Verify ownership models by printing the controlling entity for each system.
console.log(`Web3 data controlled by: ${web3Peer.publicKey}`); // Print the Web3 peer's public key to show user control.
console.log(`Content hash (integrity proof): ${contentHash}`); // Print the content hash to demonstrate content-addressing.
