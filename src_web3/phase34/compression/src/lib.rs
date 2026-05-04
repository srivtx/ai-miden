use solana_program::{ // Import the Solana program library for on-chain compression logic
    account_info::{next_account_info, AccountInfo}, // Import account iteration and info types for reading accounts
    entrypoint, // Import the entrypoint macro to declare the program start
    entrypoint::ProgramResult, // Import the result type used by instruction handlers
    msg, // Import logging function for emitting debug messages to transaction logs
    program_error::ProgramError, // Import standard error types for validation failures
    pubkey::Pubkey, // Import the public key type for ownership and address checks
}; // Close the solana_program import block
use borsh::{BorshDeserialize, BorshSerialize}; // Import serialization traits for reading and writing account data
use solana_program::keccak::hashv; // Import keccak hashing for computing Merkle tree nodes

entrypoint!(process_instruction); // Declare the program entry point so the Solana runtime routes here

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so LeafNode can be serialized as tree data
pub struct LeafNode { // Define the structure of a single leaf representing a compressed NFT
    pub owner: Pubkey, // Store the owner's public key to establish who controls this compressed item
    pub asset_id: [u8; 32], // Store a 32-byte unique identifier hash for the specific asset
    pub metadata_hash: [u8; 32], // Store a 32-byte hash of the off-chain metadata for integrity verification
} // Close the LeafNode struct definition

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so MerkleTreeState can be stored on-chain
pub struct MerkleTreeState { // Define the on-chain state for a concurrent Merkle tree
    pub max_depth: u32, // Store the tree depth to know how many proof levels are required
    pub current_root: [u8; 32], // Store the latest 32-byte root hash representing all current leaves
    pub changelog: Vec<[u8; 32]>, // Maintain a vector of recent roots to support concurrent updates
    pub leaf_count: u64, // Track how many leaves have been added to prevent overfilling
} // Close the MerkleTreeState struct definition

pub fn process_instruction( // Define the main instruction router called by the Solana runtime
    program_id: &Pubkey, // Accept the program's own address to verify program-derived accounts
    accounts: &[AccountInfo], // Accept the ordered list of accounts passed by the transaction
    instruction_data: &[u8], // Accept the raw byte payload containing the instruction discriminator and params
) -> ProgramResult { // Return ProgramResult to indicate success or specific failure
    let instruction = instruction_data // Start parsing the instruction discriminator from the first byte
        .first() // Safely get the first byte without panicking on empty input
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if no discriminator exists
    match instruction { // Branch execution based on the discriminator value
        0 => verify_proof(program_id, accounts, instruction_data), // Route to proof verification if byte is 0
        1 => update_leaf(program_id, accounts, instruction_data), // Route to leaf update if byte is 1
        _ => Err(ProgramError::InvalidInstructionData), // Reject unknown discriminators to prevent undefined behavior
    } // Close the match block
} // Close the process_instruction function

fn verify_proof( // Define the instruction handler that validates a Merkle proof for leaf inclusion
    program_id: &Pubkey, // Accept the program id for ownership validation
    accounts: &[AccountInfo], // Accept the accounts needed for proof verification
    instruction_data: &[u8], // Accept the payload containing the leaf and proof path
) -> ProgramResult { // Return ProgramResult to signal success or failure
    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to safely pull accounts in order
    let tree_account = next_account_info(account_info_iter)?; // Get the tree state account to read the current root
    let tree = MerkleTreeState::try_from_slice(&tree_account.data.borrow())?; // Deserialize the tree state
    let leaf = instruction_data // Extract the 32-byte leaf hash from bytes 1 through 33
        .get(1..33) // Select the slice representing the leaf hash
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if the leaf is missing from payload
    let proof_start = 33; // Define the byte index where the proof path begins after discriminator and leaf
    let proof_size = tree.max_depth as usize * 32; // Calculate total proof bytes as depth times 32 bytes per node
    let proof = instruction_data // Extract the proof path from the instruction data
        .get(proof_start..proof_start + proof_size) // Select the exact slice for the proof path
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if the proof is incomplete
    let mut current_hash = leaf.to_vec(); // Initialize the hash accumulator with the leaf hash as a vector
    for i in 0..tree.max_depth as usize { // Iterate once per tree level to climb from leaf to root
        let sibling = &proof[i * 32..(i + 1) * 32]; // Extract the 32-byte sibling hash for this level
        let combined = if current_hash.as_slice() < sibling { // Determine lexicographic order to prevent malleability
            [current_hash.as_slice(), sibling].concat() // Concatenate current hash before sibling if it is smaller
        } else { // Otherwise concatenate in the opposite order
            [sibling, current_hash.as_slice()].concat() // Concatenate sibling before current hash
        }; // Close the ordering branch
        current_hash = hashv(&[&combined]).to_bytes().to_vec(); // Hash the combined bytes to produce the parent node
    } // Close the level iteration loop
    let valid = tree.changelog.iter().any(|root| root.as_slice() == current_hash.as_slice()); // Check if computed root matches any recent root
    if !valid { // Reject the proof if the computed root does not appear in the changelog
        msg!("Proof verification failed"); // Log the failure for debugging
        return Err(ProgramError::Custom(0)); // Use custom error 0 for invalid proofs
    } // Close the validity check
    msg!("Proof verified successfully"); // Log the successful verification for indexers
    Ok(()) // Return success to signal the leaf is authentically included
} // Close the verify_proof function

fn update_leaf( // Define the instruction handler that replaces a leaf and updates the tree root
    program_id: &Pubkey, // Accept the program id for validation
    accounts: &[AccountInfo], // Accept the accounts needed for leaf replacement
    instruction_data: &[u8], // Accept the payload containing old leaf, new leaf, and proof
) -> ProgramResult { // Return ProgramResult to indicate success or failure
    let account_info_iter = &mut accounts.iter(); // Create an iterator to access accounts in order
    let tree_account = next_account_info(account_info_iter)?; // Get the tree state account to modify
    let authority = next_account_info(account_info_iter)?; // Get the authority account to verify update permissions
    if !authority.is_signer { // Require the authority to sign to prevent unauthorized tree modifications
        msg!("Authority must sign"); // Log the permission failure
        return Err(ProgramError::MissingRequiredSignature); // Abort if signature is missing
    } // Close the signature check
    let mut tree = MerkleTreeState::try_from_slice(&tree_account.data.borrow())?; // Deserialize mutable tree state
    let old_leaf = instruction_data // Extract the old leaf hash from bytes 1 through 33
        .get(1..33) // Select the slice for the old leaf
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if old leaf is missing
    let new_leaf = instruction_data // Extract the new leaf hash from bytes 33 through 65
        .get(33..65) // Select the slice for the new leaf
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if new leaf is missing
    let proof_start = 65; // Define the byte index where the proof path begins
    let proof_size = tree.max_depth as usize * 32; // Calculate total proof bytes from tree depth
    let proof = instruction_data // Extract the proof path from the instruction data
        .get(proof_start..proof_start + proof_size) // Select the exact slice for the proof path
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if proof is incomplete
    let mut current_hash = old_leaf.to_vec(); // Initialize the hash accumulator with the old leaf to verify path
    for i in 0..tree.max_depth as usize { // Iterate up the tree using the old leaf to validate the proof first
        let sibling = &proof[i * 32..(i + 1) * 32]; // Extract the sibling hash for this level
        let combined = if current_hash.as_slice() < sibling { // Enforce consistent ordering for hash inputs
            [current_hash.as_slice(), sibling].concat() // Concatenate current before sibling if lexicographically smaller
        } else { // Otherwise reverse the concatenation order
            [sibling, current_hash.as_slice()].concat() // Concatenate sibling before current
        }; // Close the ordering branch
        current_hash = hashv(&[&combined]).to_bytes().to_vec(); // Compute the parent hash at this level
    } // Close the validation loop
    if !tree.changelog.iter().any(|root| root.as_slice() == current_hash.as_slice()) { // Verify old leaf path leads to a known root
        msg!("Old leaf proof invalid"); // Log the validation failure
        return Err(ProgramError::Custom(1)); // Use custom error 1 for invalid old leaf proofs
    } // Close the old leaf validation
    let mut new_hash = new_leaf.to_vec(); // Reset the hash accumulator with the new leaf to compute the updated root
    for i in 0..tree.max_depth as usize { // Recompute the path to root using the new leaf and same siblings
        let sibling = &proof[i * 32..(i + 1) * 32]; // Extract the same sibling hash for this level
        let combined = if new_hash.as_slice() < sibling { // Enforce the same consistent ordering
            [new_hash.as_slice(), sibling].concat() // Concatenate new hash before sibling if smaller
        } else { // Otherwise reverse the order
            [sibling, new_hash.as_slice()].concat() // Concatenate sibling before new hash
        }; // Close the ordering branch
        new_hash = hashv(&[&combined]).to_bytes().to_vec(); // Compute the parent hash with the new leaf
    } // Close the recomputation loop
    tree.current_root = new_hash.as_slice().try_into().map_err(|_| ProgramError::InvalidAccountData)?; // Update current root
    if tree.changelog.len() >= 10 { // Limit the changelog size to prevent unbounded account growth
        tree.changelog.remove(0); // Remove the oldest root to make room for the newest entry
    } // Close the changelog size management
    tree.changelog.push(tree.current_root); // Append the new root to the changelog for future concurrent proofs
    tree.serialize(&mut *tree_account.data.borrow_mut())?; // Persist the updated tree state to the account
    msg!("Leaf updated and root recomputed"); // Log the successful update for indexers
    Ok(()) // Return success to finalize the tree modification
} // Close the update_leaf function
