import { createHash } from 'crypto';

/**
 * Phase 0: Decentralization Demo
 * 
 * This script demonstrates the difference between centralized
 * and decentralized ledgers using a simple Node.js implementation.
 * 
 * Run: npx ts-node src_web3/phase0/decentralization_demo.ts
 */

interface Transaction {
    from: string;
    to: string;
    amount: number;
    timestamp: number;
}

// ============================================================================
// CENTRALIZED LEDGER
// ============================================================================
class CentralizedLedger {
    private transactions: Transaction[] = [];
    private owner: string;

    constructor(owner: string) {
        this.owner = owner;
    }

    addTransaction(tx: Transaction): void {
        // WHY: In a centralized system, one entity controls everything.
        // They can censor, modify, or delete at will.
        if (tx.from === 'banned_user') {
            console.log(`[CENTRALIZED] Transaction from banned user rejected by ${this.owner}`);
            return;
        }
        this.transactions.push(tx);
        console.log(`[CENTRALIZED] Added: ${tx.from} -> ${tx.to}: ${tx.amount}`);
    }

    // The owner can modify history
    modifyTransaction(index: number, newAmount: number): void {
        if (index < this.transactions.length) {
            console.log(`[CENTRALIZED] ${this.owner} modified tx ${index}: ${this.transactions[index].amount} -> ${newAmount}`);
            this.transactions[index].amount = newAmount;
        }
    }

    getTransactions(): Transaction[] {
        return this.transactions;
    }
}

// ============================================================================
// DECENTRALIZED LEDGER (simple consensus)
// ============================================================================
class DecentralizedNode {
    private transactions: Transaction[] = [];
    private nodeId: string;

    constructor(nodeId: string) {
        this.nodeId = nodeId;
    }

    proposeTransaction(tx: Transaction): boolean {
        // In a real blockchain, this would be validated by consensus.
        // For demo, we just check basic validity.
        if (tx.amount <= 0) {
            console.log(`[DECENTRALIZED] Node ${this.nodeId} rejected invalid tx`);
            return false;
        }
        this.transactions.push(tx);
        console.log(`[DECENTRALIZED] Node ${this.nodeId} accepted: ${tx.from} -> ${tx.to}: ${tx.amount}`);
        return true;
    }

    // Nodes independently verify their ledger
    verifyLedger(otherNode: DecentralizedNode): boolean {
        const match = JSON.stringify(this.transactions) === JSON.stringify(otherNode.getTransactions());
        console.log(`[DECENTRALIZED] Node ${this.nodeId} verification against Node ${otherNode.nodeId}: ${match ? 'MATCH' : 'MISMATCH'}`);
        return match;
    }

    getTransactions(): Transaction[] {
        return [...this.transactions];
    }
}

// ============================================================================
// DEMO
// ============================================================================
console.log('=== Phase 0: Centralized vs Decentralized ===\n');

// Centralized demo
console.log('1. CENTRALIZED LEDGER (Bank)');
console.log('   One entity controls everything\n');
const bank = new CentralizedLedger('Bank of America');

bank.addTransaction({ from: 'Alice', to: 'Bob', amount: 100, timestamp: Date.now() });
bank.addTransaction({ from: 'banned_user', to: 'Charlie', amount: 50, timestamp: Date.now() });
bank.modifyTransaction(0, 999); // Bank changes history!

console.log(`   Bank ledger has ${bank.getTransactions().length} transactions`);
console.log(`   Alice's tx amount: ${bank.getTransactions()[0].amount} (was modified!)\n`);

// Decentralized demo
console.log('2. DECENTRALIZED LEDGER (Blockchain)');
console.log('   Many nodes must agree\n');

const node1 = new DecentralizedNode('Node-1');
const node2 = new DecentralizedNode('Node-2');
const node3 = new DecentralizedNode('Node-3');

const tx1 = { from: 'Alice', to: 'Bob', amount: 100, timestamp: Date.now() };
const tx2 = { from: 'Charlie', to: 'Dave', amount: 50, timestamp: Date.now() };

// All nodes agree on transactions
[node1, node2, node3].forEach(node => {
    node.proposeTransaction(tx1);
    node.proposeTransaction(tx2);
});

// Verify consensus
node1.verifyLedger(node2);
node1.verifyLedger(node3);

console.log(`\n   All nodes have ${node1.getTransactions().length} transactions`);
console.log(`   No single node can modify history`);

console.log('\n=== Phase 0 Complete ===');
console.log('Key insight: Decentralization removes single points of failure');
console.log('and censorship, but requires consensus (slower).');
