use std::collections::HashMap; // We import HashMap to store key-value data for Web2 and Web3 models.

// PHASE 0: Web3 vs Web2 Concept in Rust
// This file demonstrates why Web3 architectures differ from Web2 using concrete data structures.

/// Represents a traditional Web2 platform where one company owns and controls all user data.
/// We use a struct to group related fields because Web2 platforms have centralized state.
struct Web2Platform {
    owner: String, // The single owner has unilateral power to modify any state; this is the root of trust issues.
    user_data: HashMap<String, String>, // A centralized HashMap stores all user data because there is only one database.
    revenue_share_percent: f64, // The company keeps 100% of revenue distribution logic hidden from users.
}

impl Web2Platform {
    fn new(owner: &str) -> Self { // Creates a new Web2 platform to show how power concentrates at initialization.
        Self {
            owner: owner.to_string(), // Converts the input string to an owned String for storage.
            user_data: HashMap::new(), // Initializes empty HashMap because no users exist yet.
            revenue_share_percent: 50.0, // Users typically keep less than half.
        }
    }

    fn store_data(&mut self, username: &str, data: &str) { // Stores data under a username to simulate a platform writing to its central database.
        self.user_data.insert(username.to_string(), data.to_string()); // Inserts a cloned key-value pair into the centralized map.
    }

    fn get_revenue_share(&self) -> f64 { // Returns revenue share so we can expose the platform's extraction rate numerically.
        self.revenue_share_percent // Returns the stored percentage for comparison with Web3.
    }
}

/// Represents a Web3 protocol where users control their own data through cryptographic keys.
/// We model a peer with its own state to reflect that no central database exists.
struct Web3Peer {
    public_key: String, // The public key serves as identity because there are no usernames or email registrations.
    local_data: HashMap<String, String>, // Each peer stores only its own data locally, mirroring self-custody in real wallets.
    protocol_fee_percent: f64, // Protocol-level revenue share is transparent and immutable, unlike hidden Web2 terms.
}

impl Web3Peer {
    fn new(public_key: &str) -> Self { // Creates a peer with a cryptographic identity to demonstrate pseudonymous ownership.
        Self {
            public_key: public_key.to_string(), // Converts the input string to an owned String for storage.
            local_data: HashMap::new(), // Initializes empty HashMap because the peer starts with no data.
            protocol_fee_percent: 2.0, // Minimal protocol fee visible to everyone.
        }
    }

    fn store_data(&mut self, content_hash: &str, data: &str) { // Stores data locally under a content hash to simulate content-addressable storage.
        self.local_data.insert(content_hash.to_string(), data.to_string()); // Inserts a cloned key-value pair into the local map.
    }

    fn get_protocol_fee(&self) -> f64 { // Returns the low protocol fee so callers can compare extraction directly with Web2.
        self.protocol_fee_percent // Returns the stored percentage for comparison with Web2.
    }
}

fn main() {
    let mut web2 = Web2Platform::new("BigTech Inc"); // Initialize a Web2 platform to represent a typical social network.
    web2.store_data("alice", "alice's photos and messages"); // Store user data centrally so we can show who controls it later.

    let mut web3_peer = Web3Peer::new("0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"); // Initialize a Web3 peer using a hexadecimal public key string.
    web3_peer.store_data("QmYwAPJzv5CZsnAzt8auVZRn8dPpcXq", "alice's encrypted content"); // Store data locally under a hash to show content-addressing instead of username lookup.

    println!("Web2 platform takes {:.1}% of revenue", web2.get_revenue_share()); // Print revenue extraction comparison so the numeric advantage is visible.
    println!("Web3 protocol takes {:.1}% of revenue", web3_peer.get_protocol_fee()); // Print the low Web3 fee for direct contrast.

    let savings_multiplier = web2.get_revenue_share() / web3_peer.get_protocol_fee(); // Calculate the multiplier of savings to make the benefit concrete.
    println!("Creator keeps {:.1}x more in Web3", savings_multiplier); // Output the computed savings multiplier.

    println!("Web2 data controlled by: {}", web2.owner); // Verify data ownership: in Web2 the platform owns the mapping.
    println!("Web3 data controlled by: {}", web3_peer.public_key); // In Web3 the peer holds the keys.
}
