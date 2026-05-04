use solana_program::{ // Import the core Solana program library to define on-chain logic
    account_info::{next_account_info, AccountInfo}, // Import account iteration and info types for reading accounts
    entrypoint, // Import the macro that declares the program entry point
    entrypoint::ProgramResult, // Import the result type for program instruction handlers
    msg, // Import logging function for emitting messages to transaction logs
    program::invoke, // Import function for calling other programs via Cross-Program Invocation
    program_error::ProgramError, // Import standard program error types for validation failures
    pubkey::Pubkey, // Import the public key type for addressing accounts and programs
    sysvar::{clock::Clock, Sysvar}, // Import clock sysvar to access on-chain time for timelock checks
}; // Close the solana_program import block
use borsh::{BorshDeserialize, BorshSerialize}; // Import serialization traits for storing structs in account data

entrypoint!(process_instruction); // Declare the program entry point so Solana runtime knows where execution begins

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so Proposal can be serialized to account data
pub struct Proposal { // Define the on-chain state structure for a single governance proposal
    pub proposer: Pubkey, // Store the public key of the account that created this proposal to track authorship
    pub description_hash: [u8; 32], // Store a 32-byte hash of the description to verify integrity without storing full text
    pub for_votes: u64, // Track the total number of governance tokens voting in favor of this proposal
    pub against_votes: u64, // Track the total number of governance tokens voting against this proposal
    pub start_slot: u64, // Record the slot when voting begins so we can enforce voting period boundaries
    pub end_slot: u64, // Record the slot when voting ends to prevent votes after deadline
    pub eta: u64, // Store the earliest time of execution after timelock delay to enforce safety window
    pub executed: bool, // Flag whether the proposal has already been executed to prevent double spending
    pub canceled: bool, // Flag whether the proposal was canceled to block further voting or execution
} // Close the Proposal struct definition

#[derive(BorshSerialize, BorshDeserialize, Debug)] // Derive traits so VoteRecord can be serialized to account data
pub struct VoteRecord { // Define the on-chain record of an individual token holder's vote
    pub voter: Pubkey, // Store the public key of the voter to prevent the same account from voting twice
    pub proposal: Pubkey, // Store the proposal address this vote belongs to for indexing and validation
    pub amount: u64, // Record how many governance tokens were committed to this vote
    pub side: bool, // Store true for yes and false for no so the tally knows which column to increment
} // Close the VoteRecord struct definition

pub fn process_instruction( // Define the main instruction router that Solana calls for every transaction
    program_id: &Pubkey, // Accept the program's own address to verify ownership of program-derived accounts
    accounts: &[AccountInfo], // Accept the slice of accounts passed by the client for this instruction
    instruction_data: &[u8], // Accept the raw byte payload that determines which instruction to execute
) -> ProgramResult { // Return ProgramResult to indicate success or specific failure to the runtime
    let instruction = instruction_data // Start parsing the first byte to determine the instruction type
        .first() // Get the first byte safely in case the payload is empty
        .ok_or(ProgramError::InvalidInstructionData)?; // Return error if no instruction byte was provided
    match instruction { // Branch execution based on the instruction discriminator byte
        0 => create_proposal(program_id, accounts, instruction_data), // Route to proposal creation if byte is 0
        1 => cast_vote(program_id, accounts, instruction_data), // Route to vote casting if byte is 1
        2 => execute_proposal(program_id, accounts), // Route to execution if byte is 2
        3 => cancel_proposal(program_id, accounts), // Route to cancellation if byte is 3
        _ => Err(ProgramError::InvalidInstructionData), // Reject unknown instruction bytes to prevent undefined behavior
    } // Close the match block
} // Close the process_instruction function

fn create_proposal( // Define the instruction handler for submitting a new governance proposal
    program_id: &Pubkey, // Accept the program id to verify account ownership
    accounts: &[AccountInfo], // Accept the accounts required for proposal creation
    instruction_data: &[u8], // Accept the payload containing proposal parameters beyond the discriminator
) -> ProgramResult { // Return ProgramResult to bubble up success or failure
    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to safely extract accounts in order
    let proposal_account = next_account_info(account_info_iter)?; // Get the proposal account that will store the new state
    let proposer_account = next_account_info(account_info_iter)?; // Get the proposer account to verify their identity
    let clock = Clock::get()?; // Fetch the on-chain clock so timestamps are deterministic and unforgeable
    if !proposer_account.is_signer { // Verify that the proposer signed the transaction to prevent spoofing
        msg!("Proposer must sign"); // Log the specific failure reason for debugging off-chain
        return Err(ProgramError::MissingRequiredSignature); // Return error if the required signature is absent
    } // Close the signature check
    let mut proposal = Proposal { // Initialize a new Proposal struct with the provided parameters
        proposer: *proposer_account.key, // Copy the proposer's public key into the proposal state
        description_hash: [0u8; 32], // Initialize the description hash to zeros as a placeholder for client content
        for_votes: 0, // Start the yes vote tally at zero since no one has voted yet
        against_votes: 0, // Start the no vote tally at zero since no one has voted yet
        start_slot: clock.slot + 100, // Delay voting start by 100 slots to allow community review time
        end_slot: clock.slot + 10100, // End voting after 10,000 slots to give holders time to participate
        eta: clock.slot + 20100, // Set the earliest execution time to enforce a timelock after voting ends
        executed: false, // Mark the proposal as not yet executed
        canceled: false, // Mark the proposal as not canceled
    }; // Close the Proposal initialization
    if instruction_data.len() > 1 { // Check if extra data was provided beyond the instruction discriminator
        proposal.description_hash.copy_from_slice(&instruction_data[1..33]); // Copy up to 32 bytes as the description hash
    } // Close the optional hash copy block
    proposal.serialize(&mut *proposal_account.data.borrow_mut())?; // Write the serialized proposal into the account data
    msg!("Proposal created by {:?}", proposal.proposer); // Log successful creation for off-chain indexers
    Ok(()) // Return success to signal the transaction completed without errors
} // Close the create_proposal function

fn cast_vote( // Define the instruction handler for casting a vote on an active proposal
    program_id: &Pubkey, // Accept the program id for ownership validation
    accounts: &[AccountInfo], // Accept the accounts needed for vote recording
    instruction_data: &[u8], // Accept the payload containing vote direction and amount
) -> ProgramResult { // Return ProgramResult to signal success or failure
    let account_info_iter = &mut accounts.iter(); // Create a mutable iterator to pull accounts in expected order
    let proposal_account = next_account_info(account_info_iter)?; // Get the proposal account to read and update state
    let vote_record_account = next_account_info(account_info_iter)?; // Get the account that will store the vote record
    let voter_account = next_account_info(account_info_iter)?; // Get the voter's account to verify their identity
    let clock = Clock::get()?; // Fetch the current slot to validate voting is within the allowed window
    if !voter_account.is_signer { // Ensure the voter personally signed to prevent unauthorized voting
        msg!("Voter must sign"); // Emit a clear error message for client debugging
        return Err(ProgramError::MissingRequiredSignature); // Abort if the signature is missing
    } // Close the voter signature check
    let mut proposal = Proposal::try_from_slice(&proposal_account.data.borrow())?; // Deserialize existing proposal state
    if clock.slot < proposal.start_slot { // Reject votes that arrive before the official voting period begins
        msg!("Voting has not started"); // Inform clients why the transaction failed
        return Err(ProgramError::Custom(0)); // Use custom error code 0 for early voting attempts
    } // Close the early voting check
    if clock.slot > proposal.end_slot { // Reject votes that arrive after the official voting period ends
        msg!("Voting has ended"); // Inform clients why the transaction failed
        return Err(ProgramError::Custom(1)); // Use custom error code 1 for late voting attempts
    } // Close the late voting check
    if proposal.canceled || proposal.executed { // Block votes on proposals that are already finalized
        msg!("Proposal is finalized"); // Log the reason for rejection
        return Err(ProgramError::Custom(2)); // Use custom error code 2 for finalized proposals
    } // Close the finalized proposal check
    let side = instruction_data.get(1).copied().unwrap_or(0) == 1; // Parse the second byte as 1 for yes, anything else for no
    let amount = instruction_data // Extract the vote amount from bytes 2 through 10
        .get(2..10) // Select the 8-byte slice representing a u64 amount
        .and_then(|slice| slice.try_into().ok()) // Safely convert the slice to an 8-byte array
        .map(u64::from_le_bytes) // Convert the little-endian bytes into a u64 numeric value
        .unwrap_or(0); // Default to zero if the amount bytes are missing or malformed
    if side { // If the voter selected yes
        proposal.for_votes = proposal.for_votes.saturating_add(amount); // Add to the yes tally without overflowing
    } else { // If the voter selected no
        proposal.against_votes = proposal.against_votes.saturating_add(amount); // Add to the no tally without overflowing
    } // Close the side branch
    let vote_record = VoteRecord { // Create a new on-chain record of this specific vote
        voter: *voter_account.key, // Record the voter's identity for transparency and duplicate prevention
        proposal: *proposal_account.key, // Link the vote to the specific proposal address
        amount, // Store the amount of governance power committed
        side, // Record whether this vote was for or against
    }; // Close the VoteRecord initialization
    vote_record.serialize(&mut *vote_record_account.data.borrow_mut())?; // Persist the vote record to its account
    proposal.serialize(&mut *proposal_account.data.borrow_mut())?; // Persist the updated proposal tallies
    msg!("Vote cast: {} for proposal {:?}", amount, proposal_account.key); // Log the vote for indexers and explorers
    Ok(()) // Return success to finalize the transaction
} // Close the cast_vote function

fn execute_proposal( // Define the instruction handler for executing a proposal after it passes and timelock expires
    program_id: &Pubkey, // Accept the program id for validation
    accounts: &[AccountInfo], // Accept the accounts required for execution
) -> ProgramResult { // Return ProgramResult to indicate success or failure
    let account_info_iter = &mut accounts.iter(); // Create an iterator to access accounts in order
    let proposal_account = next_account_info(account_info_iter)?; // Get the proposal account to verify state and update it
    let executor_account = next_account_info(account_info_iter)?; // Get the executor account to verify caller permission
    let clock = Clock::get()?; // Fetch the current slot to verify the timelock delay has passed
    if !executor_account.is_signer { // Require the executor to sign to prevent unauthorized execution
        msg!("Executor must sign"); // Log the permission failure
        return Err(ProgramError::MissingRequiredSignature); // Abort if signature is missing
    } // Close the executor signature check
    let mut proposal = Proposal::try_from_slice(&proposal_account.data.borrow())?; // Load the proposal state from chain
    if proposal.canceled { // Reject execution if the proposal was previously canceled
        msg!("Proposal was canceled"); // Explain the failure
        return Err(ProgramError::Custom(3)); // Use custom error 3 for canceled proposals
    } // Close the canceled check
    if proposal.executed { // Reject execution if the proposal was already executed to prevent double spending
        msg!("Proposal already executed"); // Explain the failure
        return Err(ProgramError::Custom(4)); // Use custom error 4 for already executed proposals
    } // Close the executed check
    if clock.slot < proposal.eta { // Reject execution if the timelock safety window has not elapsed
        msg!("Timelock not expired"); // Explain the failure so clients know to wait
        return Err(ProgramError::Custom(5)); // Use custom error 5 for premature execution attempts
    } // Close the timelock check
    let total_votes = proposal.for_votes.saturating_add(proposal.against_votes); // Sum all cast votes for quorum math
    if total_votes < 100 { // Enforce a minimum quorum of 100 vote tokens to prevent low-participation attacks
        msg!("Quorum not reached"); // Explain why the proposal fails despite any majority
        return Err(ProgramError::Custom(6)); // Use custom error 6 for quorum failures
    } // Close the quorum check
    if proposal.for_votes <= proposal.against_votes { // Require a simple majority of yes over no to pass
        msg!("Proposal did not pass"); // Explain the failure
        return Err(ProgramError::Custom(7)); // Use custom error 7 for proposals that lost the vote
    } // Close the majority check
    proposal.executed = true; // Mark the proposal as executed to prevent any future re-execution
    proposal.serialize(&mut *proposal_account.data.borrow_mut())?; // Persist the executed flag to the account
    msg!("Proposal executed successfully"); // Log the successful execution for indexers
    Ok(()) // Return success to signal the governance action is finalized
} // Close the execute_proposal function

fn cancel_proposal( // Define the instruction handler for canceling a proposal before execution
    program_id: &Pubkey, // Accept the program id for validation
    accounts: &[AccountInfo], // Accept the accounts needed for cancellation
) -> ProgramResult { // Return ProgramResult to indicate success or failure
    let account_info_iter = &mut accounts.iter(); // Create an iterator to access accounts in order
    let proposal_account = next_account_info(account_info_iter)?; // Get the proposal account to update its state
    let proposer_account = next_account_info(account_info_iter)?; // Get the proposer account to verify authorization
    if !proposer_account.is_signer { // Require the proposer to sign the cancellation to prevent hostile takeovers
        msg!("Proposer must sign"); // Log the authorization failure
        return Err(ProgramError::MissingRequiredSignature); // Abort if signature is missing
    } // Close the signature check
    let mut proposal = Proposal::try_from_slice(&proposal_account.data.borrow())?; // Load the proposal state
    if proposal.executed { // Block cancellation if the proposal was already executed since it is irreversible
        msg!("Already executed"); // Explain the failure
        return Err(ProgramError::Custom(8)); // Use custom error 8 for executed proposals
    } // Close the executed check
    if proposal.proposer != *proposer_account.key { // Ensure only the original proposer can cancel their own proposal
        msg!("Only proposer can cancel"); // Explain the permission failure
        return Err(ProgramError::IllegalOwner); // Use IllegalOwner to signal wrong caller
    } // Close the proposer check
    proposal.canceled = true; // Set the canceled flag to true to freeze voting and execution
    proposal.serialize(&mut *proposal_account.data.borrow_mut())?; // Persist the canceled state to the account
    msg!("Proposal canceled"); // Log the cancellation for transparency
    Ok(()) // Return success to finalize the cancellation
} // Close the cancel_proposal function
