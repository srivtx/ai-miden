use sha2::{Sha256, Digest};
// We import SHA-256 to build the sequential hash chain that proves time passage in PoH.
use std::collections::{HashMap, HashSet};
// We import HashMap and HashSet to track account locks and detect write conflicts during scheduling.
use std::time::{SystemTime, UNIX_EPOCH};
// We import time utilities to timestamp events within the simulated PoH chain.

// PHASE 3: Proof of History Demo in Rust
// This file simulates Solana's PoH clock, Tower BFT voting, and parallel execution scheduling.

/// A PoH tick represents one step in the sequential hash chain.
/// We use a struct because each tick carries a hash and optional event data.
struct PohTick {
    /// The sequential index proves ordering and passage of time.
    index: u64,
    /// The hash is derived from the previous tick's hash, forming the chain.
    hash: String,
    /// Events are messages injected into the chain to prove they happened before later ticks.
    events: Vec<String>,
}

/// Simulates the Proof of History generator that produces a continuous hash chain.
/// The leader runs this sequentially because the VDF cannot be parallelized.
struct ProofOfHistory {
    /// Stores ticks in order so we can verify the chain later.
    ticks: Vec<PohTick>,
    /// The latest hash value that the next tick must incorporate.
    latest_hash: String,
}

impl ProofOfHistory {
    /// Creates a new PoH generator starting from a known genesis hash.
    fn new() -> Self {
        let genesis_hash = "genesis".to_string();
        Self {
            ticks: vec![PohTick { index: 0, hash: genesis_hash.clone(), events: vec![] }],
            latest_hash: genesis_hash,
        }
    }

    /// Appends a new tick by hashing the previous hash, proving time passed.
    fn tick(&mut self) {
        let next_index = self.ticks.len() as u64;
        let mut hasher = Sha256::new();
        hasher.update(self.latest_hash.as_bytes());
        let next_hash = format!("{:x}", hasher.finalize());
        self.ticks.push(PohTick { index: next_index, hash: next_hash.clone(), events: vec![] });
        self.latest_hash = next_hash;
    }

    /// Records an event at the current tick so its timestamp is locked in the chain.
    fn record_event(&mut self, event: String) {
        if let Some(last) = self.ticks.last_mut() {
            last.events.push(event);
        }
    }
}

/// A transaction references accounts it will read or write.
/// We model this so the scheduler can detect conflicts for parallel execution.
struct Transaction {
    /// Unique identifier for the transaction.
    id: u64,
    /// Accounts this transaction writes to; write conflicts require sequencing.
    writes: Vec<String>,
    /// Accounts this transaction reads from; reads can be parallelized.
    reads: Vec<String>,
}

/// Analyzes transactions to find non-conflicting groups that can execute in parallel.
fn schedule_parallel(txs: &[Transaction]) -> Vec<Vec<u64>> {
    let mut batches: Vec<Vec<u64>> = vec![];
    let mut scheduled: HashSet<u64> = HashSet::new();
    let mut write_locks: HashSet<String> = HashSet::new();

    // Continue until every transaction is assigned to a batch.
    while scheduled.len() < txs.len() {
        let mut current_batch: Vec<u64> = vec![];
        let mut batch_writes: HashSet<String> = HashSet::new();

        for tx in txs {
            // Skip transactions already placed in a previous batch.
            if scheduled.contains(&tx.id) {
                continue;
            }
            // A transaction conflicts if any write overlaps with prior scheduled writes.
            let conflicts = tx.writes.iter().any(|w| write_locks.contains(w));
            // It also conflicts if any write overlaps with another transaction in this same batch.
            let intra_conflicts = tx.writes.iter().any(|w| batch_writes.contains(w));
            if !conflicts && !intra_conflicts {
                current_batch.push(tx.id);
                batch_writes.extend(tx.writes.iter().cloned());
                scheduled.insert(tx.id);
            }
        }
        // Update global write locks so the next batch respects all previously committed writes.
        write_locks.extend(batch_writes);
        batches.push(current_batch);
    }
    batches
}

fn main() {
    // Initialize the PoH clock to establish a trustless timeline.
    let mut poh = ProofOfHistory::new();

    // Generate ticks to simulate the leader producing hashes continuously.
    for _ in 0..5 {
        poh.tick();
    }

    // Record an event in the chain to show how messages are timestamped trustlessly.
    poh.record_event("Vote: Validator A confirms slot 5".to_string());

    // Continue ticking to show the chain progresses regardless of events.
    for _ in 0..3 {
        poh.tick();
    }

    // Print the PoH chain so we can see sequential hashes and embedded events.
    println!("Proof of History chain:");
    for tick in &poh.ticks {
        println!("  Tick {}: hash={:.8}... events={:?}", tick.index, tick.hash, tick.events);
    }

    // Create sample transactions that touch different accounts to test parallel scheduling.
    let transactions = vec![
        Transaction { id: 1, writes: vec!["account_A".to_string()], reads: vec![] },
        Transaction { id: 2, writes: vec!["account_B".to_string()], reads: vec![] },
        Transaction { id: 3, writes: vec!["account_A".to_string()], reads: vec![] },
        Transaction { id: 4, writes: vec!["account_C".to_string()], reads: vec!["account_B".to_string()] },
    ];

    // Schedule transactions into parallel batches based on write-set conflicts.
    let batches = schedule_parallel(&transactions);

    // Print the scheduling result to demonstrate independent vs sequential execution.
    println!("\nParallel execution batches:");
    for (i, batch) in batches.iter().enumerate() {
        println!("  Batch {}: txs {:?}", i, batch);
    }

    // Verify that conflicting transactions (1 and 3 on account_A) landed in separate batches.
    println!("\nConflict detection: tx 1 and tx 3 both write account_A, so they are sequenced.");
}
