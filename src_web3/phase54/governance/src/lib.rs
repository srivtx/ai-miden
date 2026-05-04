use solana_program::{ // Import the Solana runtime API so the program can validate accounts and read sysvars.
    account_info::{next_account_info, AccountInfo}, // next_account_info iterates safely over the accounts slice; AccountInfo holds all on-chain account metadata.
    entrypoint, // entrypoint macro marks the function Solana calls when this program is invoked.
    entrypoint::ProgramResult, // ProgramResult is the standard return type that maps to Solana success or error codes.
    msg, // msg logs to the transaction log so developers and auditors can trace execution.
    program_error::ProgramError, // ProgramError enumerates common on-chain failures so callers receive meaningful error codes.
    pubkey::Pubkey, // Pubkey is the 32-byte address type used to identify accounts and programs.
    clock::Clock, // Clock provides access to the current slot so voting periods and timelocks are deterministic.
    sysvar::Sysvar, // Sysvar trait allows fetching runtime sysvars like Clock without passing them as explicit accounts.
    program_pack::{Pack, Sealed}, // Pack defines serialization for account state; Sealed marks a type with a fixed size.
    borsh0_10::try_from_slice_unchecked, // try_from_slice_unchecked deserializes Borsh without length checks for known-size account data.
};
use borsh::{BorshDeserialize, BorshSerialize}; // Borsh provides compact binary serialization used by Solana account state.

entrypoint!(process_instruction); // Register process_instruction as the BPF entrypoint so the runtime knows where to begin.

pub fn process_instruction( // process_instruction is the single entry function that dispatches to handlers based on instruction data.
    program_id: &Pubkey, // program_id is the address of this governance program; we use it to verify ownership of program-derived accounts.
    accounts: &[AccountInfo], // accounts holds all accounts passed by the client; order matters and must match the instruction definition.
    instruction_data: &[u8], // instruction_data is the payload that tells us which instruction to run and what parameters it carries.
) -> ProgramResult { // Return ProgramResult so Solana knows whether to commit or roll back the transaction.
    msg!("Governance program entrypoint invoked"); // Log entry so explorers and debuggers can confirm the program started.
    let instruction = GovernanceInstruction::try_from_slice(instruction_data) // Deserialize the raw bytes into a typed instruction so we can match on it safely.
        .map_err(|_| ProgramError::InvalidInstructionData)?; // Reject the transaction if the payload is malformed to prevent undefined behavior.
    match instruction { // Match on the deserialized instruction to route to the correct handler.
        GovernanceInstruction::CreateProposal { title, description, end_slot, quorum, pass_threshold } => { // Route to proposal creation when the first variant is detected.
            process_create_proposal(program_id, accounts, title, description, end_slot, quorum, pass_threshold) // Forward parameters to the handler that initializes proposal state.
        }
        GovernanceInstruction::Vote { proposal_id, vote_for } => { // Route to voting when a member wants to cast a ballot.
            process_vote(program_id, accounts, proposal_id, vote_for) // Forward vote details to the handler that tallies weighted votes.
        }
        GovernanceInstruction::Delegate { delegate_to } => { // Route to delegation when a token holder wants to assign voting power.
            process_delegate(program_id, accounts, delegate_to) // Forward the target delegate address to the delegation handler.
        }
        GovernanceInstruction::Undelegate {} => { // Route to undelegation when a token holder wants to reclaim voting power.
            process_undelegate(program_id, accounts) // Forward to the handler that clears the delegation record.
        }
        GovernanceInstruction::QueueProposal { proposal_id } => { // Route to queueing when a passed proposal needs to enter the timelock.
            process_queue_proposal(program_id, accounts, proposal_id) // Forward to the handler that validates vote results and sets the execution delay.
        }
        GovernanceInstruction::ExecuteProposal { proposal_id } => { // Route to execution when the timelock has expired.
            process_execute_proposal(program_id, accounts, proposal_id) // Forward to the handler that finalizes the proposal and triggers downstream actions.
        }
        GovernanceInstruction::CancelProposal { proposal_id } => { // Route to cancellation when the guardian needs to stop a queued proposal.
            process_cancel_proposal(program_id, accounts, proposal_id) // Forward to the handler that verifies guardian authority and marks the proposal cancelled.
        }
    }
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so instructions can be serialized across the wire and cloned in memory.
pub enum GovernanceInstruction { // Enumerate all possible instructions so the program has a closed set of operations.
    CreateProposal { title: String, description: String, end_slot: u64, quorum: u64, pass_threshold: u64 }, // CreateProposal stores the proposal text and voting rules on-chain.
    Vote { proposal_id: u64, vote_for: bool }, // Vote records a single ballot with a boolean choice and links it to a proposal.
    Delegate { delegate_to: Pubkey }, // Delegate assigns the caller's voting power to another address.
    Undelegate {}, // Undelegate revokes any existing delegation and returns power to the owner.
    QueueProposal { proposal_id: u64 }, // QueueProposal transitions a succeeded proposal into the timelock waiting state.
    ExecuteProposal { proposal_id: u64 }, // ExecuteProposal finalizes a queued proposal after the delay has passed.
    CancelProposal { proposal_id: u64 }, // CancelProposal allows the guardian to abort a queued proposal during the safety window.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so Proposal can be saved to and loaded from account data.
pub struct Proposal { // Proposal holds the full state of a single governance motion.
    pub proposer: Pubkey, // proposer identifies who created the proposal for accountability and potential slashing.
    pub title: String, // title is a short human-readable name displayed in explorers and dashboards.
    pub description: String, // description contains the full rationale so voters know what they are approving.
    pub start_slot: u64, // start_slot records when voting began so elapsed time can be computed deterministically.
    pub end_slot: u64, // end_slot is the hard deadline after which no more votes are accepted.
    pub quorum: u64, // quorum is the minimum total votes required for the result to be legitimate.
    pub pass_threshold: u64, // pass_threshold is the percentage of yes votes required among all cast votes.
    pub for_votes: u64, // for_votes accumulates the weighted yes votes as they arrive.
    pub against_votes: u64, // against_votes accumulates the weighted no votes as they arrive.
    pub status: u8, // status tracks the proposal lifecycle using small integers to save account space.
    pub queued_at: u64, // queued_at records when the proposal entered the timelock so the delay can be verified.
    pub execute_after: u64, // execute_after is the earliest slot at which execution is allowed.
    pub id: u64, // id is a monotonic counter that gives every proposal a unique identifier.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so VoteRecord can be stored on-chain and inspected by auditors.
pub struct VoteRecord { // VoteRecord prevents double voting and proves a specific user voted a specific way.
    pub voter: Pubkey, // voter identifies the account that cast this ballot.
    pub proposal_id: u64, // proposal_id links this vote to exactly one proposal.
    pub weight: u64, // weight stores the voting power at the time of voting so results are immutable.
    pub vote_for: bool, // vote_for is true for yes and false for no.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so DelegateRecord can be saved to an account and read by the tally logic.
pub struct DelegateRecord { // DelegateRecord stores the assignment of voting power from an owner to a representative.
    pub owner: Pubkey, // owner is the original holder of the tokens who retains custody.
    pub delegate: Pubkey, // delegate is the representative who will vote on the owner's behalf.
    pub amount: u64, // amount is the voting power delegated so the tally can sum it correctly.
}

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // Derive traits so GovernanceConfig can be stored in a singleton account.
pub struct GovernanceConfig { // GovernanceConfig is the global settings account shared by all proposals.
    pub paused: bool, // paused is a circuit breaker that halts all mutable governance actions during emergencies.
    pub guardian: Pubkey, // guardian is the trusted address that can cancel proposals or toggle the pause.
    pub timelock_duration: u64, // timelock_duration is the mandatory delay between queuing and execution.
    pub proposal_count: u64, // proposal_count is incremented atomically to assign unique IDs to new proposals.
}

impl Sealed for Proposal {} // Sealed tells the Pack trait that Proposal has a fixed upper size bound.
impl Pack for Proposal { // Pack defines how Proposal is serialized into and deserialized from account bytes.
    const LEN: usize = 32 + 4 + 200 + 4 + 1000 + 8 + 8 + 8 + 8 + 8 + 8 + 1 + 8 + 8 + 8; // LEN is the maximum account size reserved for a Proposal.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

impl Sealed for VoteRecord {} // Sealed tells the Pack trait that VoteRecord has a fixed upper size bound.
impl Pack for VoteRecord { // Pack defines how VoteRecord is serialized into and deserialized from account bytes.
    const LEN: usize = 32 + 8 + 8 + 1; // LEN is the maximum account size reserved for a VoteRecord.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

impl Sealed for DelegateRecord {} // Sealed tells the Pack trait that DelegateRecord has a fixed upper size bound.
impl Pack for DelegateRecord { // Pack defines how DelegateRecord is serialized into and deserialized from account bytes.
    const LEN: usize = 32 + 32 + 8; // LEN is the maximum account size reserved for a DelegateRecord.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

impl Sealed for GovernanceConfig {} // Sealed tells the Pack trait that GovernanceConfig has a fixed upper size bound.
impl Pack for GovernanceConfig { // Pack defines how GovernanceConfig is serialized into and deserialized from account bytes.
    const LEN: usize = 1 + 32 + 8 + 8; // LEN is the maximum account size reserved for GovernanceConfig.
    fn pack_into_slice(&self, dst: &mut [u8]) { // pack_into_slice writes the struct into the account buffer.
        let mut data = dst; // Create a mutable borrow so Borsh can write into it.
        self.serialize(&mut data).unwrap(); // Serialize with Borsh; unwrap is safe because the buffer is pre-allocated to LEN.
    }
    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> { // unpack_from_slice reads the struct from the account buffer.
        try_from_slice_unchecked(src).map_err(|_| ProgramError::InvalidAccountData) // Return an error if the bytes do not match the expected schema.
    }
}

fn process_create_proposal( // process_create_proposal initializes a new Proposal account with the provided parameters.
    program_id: &Pubkey, // program_id is used to verify that the proposal account is owned by this program.
    accounts: &[AccountInfo], // accounts contains the proposer, the proposal account, and the config account.
    title: String, // title is stored on-chain so explorers can display it without off-chain indexing.
    description: String, // description is stored on-chain so the full proposal text is auditable and immutable.
    end_slot: u64, // end_slot is the vote deadline supplied by the client.
    quorum: u64, // quorum is the minimum participation required for a valid vote.
    pass_threshold: u64, // pass_threshold is the percentage of yes votes needed to pass.
) -> ProgramResult { // Return ProgramResult so Solana commits or rejects the transaction atomically.
    let accounts_iter = &mut accounts.iter(); // Create an iterator so we can consume accounts in a predictable order.
    let proposer = next_account_info(accounts_iter)?; // Extract the proposer account first because they must sign.
    let proposal_account = next_account_info(accounts_iter)?; // Extract the proposal account that will hold the new state.
    let config_account = next_account_info(accounts_iter)?; // Extract the config account to read global settings and increment the proposal counter.
    let clock = Clock::get()?; // Fetch the current slot from the runtime so start_slot is deterministic and not client-supplied.
    if !proposer.is_signer { // Require a signature from the proposer so anonymous or spoofed proposals are impossible.
        msg!("Proposer must sign to prevent spoofed proposals"); // Log the exact failure reason for debugging.
        return Err(ProgramError::MissingRequiredSignature); // Abort the transaction if the signature is missing.
    }
    let mut config = GovernanceConfig::unpack(&config_account.data.borrow())?; // Load the global config so we can check pause status and get the next ID.
    if config.paused { // Reject creation if the governance circuit breaker is active.
        msg!("Creation rejected because governance is paused for emergency protection"); // Explain why the transaction failed.
        return Err(ProgramError::InvalidAccountData); // Abort to enforce the emergency pause.
    }
    if proposal_account.owner != program_id { // Verify program ownership so malicious accounts cannot be substituted.
        msg!("Proposal account must be owned by this program to enforce state integrity"); // Explain the ownership check.
        return Err(ProgramError::IncorrectProgramId); // Abort if the account is not a program-derived address.
    }
    let proposal_id = config.proposal_count; // Assign the current counter value as the unique proposal ID.
    config.proposal_count += 1; // Increment the counter atomically so the next proposal gets a different ID.
    GovernanceConfig::pack(config, &mut config_account.data.borrow_mut())?; // Save the updated config back to its account.
    let proposal = Proposal { // Build the proposal struct with all fields initialized.
        proposer: *proposer.key, // Copy the proposer pubkey so the record is immutable.
        title, // Store the title.
        description, // Store the description.
        start_slot: clock.slot, // Record the current slot as the official start time.
        end_slot, // Store the deadline supplied by the client.
        quorum, // Store the quorum rule.
        pass_threshold, // Store the pass threshold rule.
        for_votes: 0, // Initialize yes votes to zero.
        against_votes: 0, // Initialize no votes to zero.
        status: 1, // Set status to Active (1) so voting can begin immediately.
        queued_at: 0, // Initialize queued timestamp to zero because the proposal is not queued yet.
        execute_after: 0, // Initialize execution timestamp to zero because the vote has not concluded.
        id: proposal_id, // Assign the unique ID extracted from the config counter.
    };
    Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Serialize the proposal into its dedicated account.
    msg!("Proposal {} created by {}", proposal_id, proposer.key); // Log success so explorers show a friendly message.
    Ok(()) // Return success so Solana commits the state changes.
}

fn process_vote( // process_vote records a single weighted ballot and updates proposal totals.
    _program_id: &Pubkey, // program_id is unused because vote validation relies on proposal ownership and signatures.
    accounts: &[AccountInfo], // accounts contains the voter, proposal, vote record, and token account.
    proposal_id: u64, // proposal_id links the vote to a specific proposal.
    vote_for: bool, // vote_for is true for yes and false for no.
) -> ProgramResult { // Return ProgramResult so the vote is either fully recorded or fully rejected.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let voter = next_account_info(accounts_iter)?; // Extract the voter account because they must sign.
    let proposal_account = next_account_info(accounts_iter)?; // Extract the proposal account to update its tally.
    let vote_record_account = next_account_info(accounts_iter)?; // Extract the vote record account to prevent double voting.
    let token_account = next_account_info(accounts_iter)?; // Extract the token account to determine voting power.
    let clock = Clock::get()?; // Fetch the current slot to enforce the voting deadline.
    if !voter.is_signer { // Require a signature from the voter so ballots cannot be cast by third parties.
        msg!("Voter must sign to prevent ballot stuffing by third parties"); // Log the security requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the voter did not sign.
    }
    let mut proposal = Proposal::unpack(&proposal_account.data.borrow())?; // Load the proposal state to verify it is active.
    if proposal.id != proposal_id { // Reject mismatched IDs so votes cannot be redirected to a different proposal.
        msg!("Proposal ID mismatch to prevent voting on the wrong proposal"); // Explain the mismatch failure.
        return Err(ProgramError::InvalidAccountData); // Abort to protect vote integrity.
    }
    if proposal.status != 1 { // Only allow voting while the proposal is Active.
        msg!("Voting only allowed while proposal is Active"); // Explain that the proposal is not open for votes.
        return Err(ProgramError::InvalidAccountData); // Abort because the status check failed.
    }
    if clock.slot > proposal.end_slot { // Reject late votes so the deadline is strictly enforced.
        msg!("Voting period has ended; late votes are rejected to preserve integrity"); // Explain the deadline violation.
        return Err(ProgramError::InvalidAccountData); // Abort because the vote arrived too late.
    }
    let vote_data = vote_record_account.data.borrow(); // Borrow the vote record data to check if it is empty.
    if !vote_data.iter().all(|b| *b == 0) { // If any byte is non-zero, a vote record already exists here.
        msg!("Vote record already exists; double voting is prohibited"); // Explain the double-vote prevention.
        return Err(ProgramError::AccountAlreadyInitialized); // Abort to prevent duplicate ballots.
    }
    drop(vote_data); // Explicitly drop the immutable borrow so we can mutably borrow later.
    let voting_power = token_account.lamports() as u64; // Use lamports as a proxy for token balance because this demo uses native SOL for simplicity.
    if vote_for { // Branch based on the voter's choice.
        proposal.for_votes += voting_power; // Add the voter's weight to the yes tally.
    } else { // If the voter chose no.
        proposal.against_votes += voting_power; // Add the voter's weight to the no tally.
    }
    Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the updated proposal totals.
    let vote_record = VoteRecord { // Build the vote record to prove this voter already participated.
        voter: *voter.key, // Copy the voter address for accountability.
        proposal_id, // Link the record to this proposal.
        weight: voting_power, // Store the weight so the tally is auditable.
        vote_for, // Store the choice so the record is complete.
    };
    VoteRecord::pack(vote_record, &mut vote_record_account.data.borrow_mut())?; // Save the vote record to enforce no double voting.
    msg!("Vote recorded for proposal {} with weight {}", proposal_id, voting_power); // Log success for transparency.
    Ok(()) // Return success so the transaction is committed.
}

fn process_delegate( // process_delegate assigns the caller's voting power to another address.
    _program_id: &Pubkey, // program_id is unused because delegation only touches a new record account.
    accounts: &[AccountInfo], // accounts contains the owner, the delegate record, and the token account.
    delegate_to: Pubkey, // delegate_to is the representative who will gain voting power.
) -> ProgramResult { // Return ProgramResult so delegation is atomic.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let owner = next_account_info(accounts_iter)?; // Extract the owner because they must authorize the delegation.
    let delegate_record_account = next_account_info(accounts_iter)?; // Extract the record account that will store the delegation.
    let token_account = next_account_info(accounts_iter)?; // Extract the token account to measure voting power.
    if !owner.is_signer { // Require owner signature so no one else can delegate the owner's power.
        msg!("Owner must sign to prevent unauthorized delegation of their voting power"); // Explain the authorization requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the owner did not sign.
    }
    let amount = token_account.lamports() as u64; // Measure voting power from the token account balance.
    let record = DelegateRecord { // Build the delegation record.
        owner: *owner.key, // Copy the owner address so the record is traceable.
        delegate: delegate_to, // Store the target delegate address.
        amount, // Store the voting power so tally logic can sum it later.
    };
    DelegateRecord::pack(record, &mut delegate_record_account.data.borrow_mut())?; // Serialize the record into its account.
    msg!("Delegated {} voting power to {}", amount, delegate_to); // Log the delegation for transparency.
    Ok(()) // Return success so the transaction is committed.
}

fn process_undelegate( // process_undelegate revokes delegation and returns voting power to the owner.
    _program_id: &Pubkey, // program_id is unused because undelegation only clears an existing record.
    accounts: &[AccountInfo], // accounts contains the owner and the delegate record to clear.
) -> ProgramResult { // Return ProgramResult so undelegation is atomic.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let owner = next_account_info(accounts_iter)?; // Extract the owner because they must authorize the revocation.
    let delegate_record_account = next_account_info(accounts_iter)?; // Extract the record account to zero out.
    if !owner.is_signer { // Require owner signature so delegates cannot prevent revocation.
        msg!("Owner must sign to reclaim their voting power from the delegate"); // Explain the authorization requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the owner did not sign.
    }
    let mut record = DelegateRecord::unpack(&delegate_record_account.data.borrow())?; // Load the existing record to verify ownership.
    if record.owner != *owner.key { // Reject if the signer does not match the recorded owner.
        msg!("Only the original owner can undelegate this record"); // Explain the ownership restriction.
        return Err(ProgramError::IllegalOwner); // Abort because the signer is not authorized.
    }
    record.amount = 0; // Zero out the delegated amount so the delegate loses voting power.
    record.delegate = Pubkey::default(); // Reset the delegate address to the default to show no active delegation.
    DelegateRecord::pack(record, &mut delegate_record_account.data.borrow_mut())?; // Save the cleared record.
    msg!("Undelegated voting power returned to owner"); // Log success for transparency.
    Ok(()) // Return success so the transaction is committed.
}

fn process_queue_proposal( // process_queue_proposal evaluates vote results and moves a passed proposal into the timelock.
    _program_id: &Pubkey, // program_id is unused because validation relies on proposal state and config.
    accounts: &[AccountInfo], // accounts contains the caller, proposal, and config.
    proposal_id: u64, // proposal_id identifies which proposal to evaluate.
) -> ProgramResult { // Return ProgramResult so queueing is atomic.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let caller = next_account_info(accounts_iter)?; // Extract the caller because they must pay for the queueing transaction.
    let proposal_account = next_account_info(accounts_iter)?; // Extract the proposal to update its status.
    let config_account = next_account_info(accounts_iter)?; // Extract the config to read the timelock duration.
    let clock = Clock::get()?; // Fetch the current slot to verify voting has ended.
    if !caller.is_signer { // Require caller signature so the queueing transaction is authenticated.
        msg!("Caller must sign to queue the proposal"); // Explain the signature requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the caller did not sign.
    }
    let mut proposal = Proposal::unpack(&proposal_account.data.borrow())?; // Load the proposal state to check its status and tallies.
    if proposal.id != proposal_id { // Reject mismatched IDs to prevent queueing the wrong proposal.
        msg!("Proposal ID mismatch prevents queueing the wrong proposal"); // Explain the mismatch failure.
        return Err(ProgramError::InvalidAccountData); // Abort to protect proposal integrity.
    }
    if proposal.status != 1 { // Only Active proposals can be evaluated after voting ends.
        msg!("Only Active proposals can be queued after voting ends"); // Explain the status restriction.
        return Err(ProgramError::InvalidAccountData); // Abort because the proposal is not in the correct state.
    }
    if clock.slot <= proposal.end_slot { // Reject queueing before the deadline so all votes are counted.
        msg!("Voting is still active; queueing is premature"); // Explain that the deadline has not passed.
        return Err(ProgramError::InvalidAccountData); // Abort because the voting period is still open.
    }
    let total_votes = proposal.for_votes + proposal.against_votes; // Sum all cast votes to compute participation.
    if total_votes < proposal.quorum { // Reject if participation is below the minimum threshold.
        msg!("Quorum not reached; proposal is defeated"); // Explain the quorum failure.
        proposal.status = 2; // Mark the proposal as Defeated (2) so no further action is possible.
        Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the defeated status.
        return Ok(()); // Return success because the state transition to Defeated is valid.
    }
    let for_percentage = (proposal.for_votes * 100) / total_votes; // Compute the yes percentage among all votes.
    if for_percentage < proposal.pass_threshold { // Reject if the yes percentage is below the required threshold.
        msg!("Pass threshold not met; proposal is defeated"); // Explain the threshold failure.
        proposal.status = 2; // Mark the proposal as Defeated (2) so no further action is possible.
        Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the defeated status.
        return Ok(()); // Return success because the state transition to Defeated is valid.
    }
    let config = GovernanceConfig::unpack(&config_account.data.borrow())?; // Load the global config to read the timelock duration.
    proposal.status = 3; // Mark the proposal as Queued (3) so it enters the timelock phase.
    proposal.queued_at = clock.slot; // Record the exact slot when queueing occurred.
    proposal.execute_after = clock.slot + config.timelock_duration; // Compute the earliest execution slot by adding the delay.
    Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the updated proposal state.
    msg!("Proposal {} queued for execution after slot {}", proposal_id, proposal.execute_after); // Log success and the execution window.
    Ok(()) // Return success so the transaction is committed.
}

fn process_execute_proposal( // process_execute_proposal finalizes a queued proposal after the timelock expires.
    _program_id: &Pubkey, // program_id is unused because execution relies on proposal state and config.
    accounts: &[AccountInfo], // accounts contains the executor, proposal, and config.
    proposal_id: u64, // proposal_id identifies which proposal to execute.
) -> ProgramResult { // Return ProgramResult so execution is atomic.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let executor = next_account_info(accounts_iter)?; // Extract the executor because they must sign and pay for the transaction.
    let proposal_account = next_account_info(accounts_iter)?; // Extract the proposal to verify its state and update it.
    let config_account = next_account_info(accounts_iter)?; // Extract the config to check the pause status.
    let clock = Clock::get()?; // Fetch the current slot to verify the timelock has expired.
    if !executor.is_signer { // Require executor signature so execution cannot be triggered by anonymous bots.
        msg!("Executor must sign to pay for the execution transaction"); // Explain the signature requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the executor did not sign.
    }
    let mut proposal = Proposal::unpack(&proposal_account.data.borrow())?; // Load the proposal state to check its status.
    if proposal.id != proposal_id { // Reject mismatched IDs to prevent executing the wrong proposal.
        msg!("Proposal ID mismatch prevents executing the wrong proposal"); // Explain the mismatch failure.
        return Err(ProgramError::InvalidAccountData); // Abort to protect proposal integrity.
    }
    if proposal.status != 3 { // Only Queued proposals can be executed.
        msg!("Only Queued proposals can be executed"); // Explain the status restriction.
        return Err(ProgramError::InvalidAccountData); // Abort because the proposal is not in the correct state.
    }
    let config = GovernanceConfig::unpack(&config_account.data.borrow())?; // Load the global config to check the pause flag.
    if config.paused { // Reject execution if the emergency pause is active.
        msg!("Execution blocked because governance is paused for emergency protection"); // Explain the pause enforcement.
        return Err(ProgramError::InvalidAccountData); // Abort because the circuit breaker is engaged.
    }
    if clock.slot <= proposal.execute_after { // Reject execution if the timelock delay has not yet passed.
        msg!("Timelock has not expired; execution is too early"); // Explain the delay enforcement.
        return Err(ProgramError::InvalidAccountData); // Abort because the safety window is still open.
    }
    proposal.status = 4; // Mark the proposal as Executed (4) so it cannot be executed again.
    Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the final status.
    msg!("Proposal {} executed at slot {}", proposal_id, clock.slot); // Log success for transparency.
    Ok(()) // Return success so the transaction is committed.
}

fn process_cancel_proposal( // process_cancel_proposal allows the guardian to abort a queued proposal during the timelock.
    _program_id: &Pubkey, // program_id is unused because cancellation relies on guardian authority and proposal state.
    accounts: &[AccountInfo], // accounts contains the guardian, proposal, and config.
    proposal_id: u64, // proposal_id identifies which proposal to cancel.
) -> ProgramResult { // Return ProgramResult so cancellation is atomic.
    let accounts_iter = &mut accounts.iter(); // Create an iterator to consume accounts in order.
    let guardian = next_account_info(accounts_iter)?; // Extract the guardian because they must sign.
    let proposal_account = next_account_info(accounts_iter)?; // Extract the proposal to update its status.
    let config_account = next_account_info(accounts_iter)?; // Extract the config to verify the guardian address.
    if !guardian.is_signer { // Require guardian signature so only the authorized protector can cancel.
        msg!("Guardian must sign to cancel a proposal"); // Explain the signature requirement.
        return Err(ProgramError::MissingRequiredSignature); // Abort if the guardian did not sign.
    }
    let config = GovernanceConfig::unpack(&config_account.data.borrow())?; // Load the global config to read the designated guardian.
    if *guardian.key != config.guardian { // Reject if the signer is not the configured guardian.
        msg!("Only the designated guardian can cancel proposals"); // Explain the authorization restriction.
        return Err(ProgramError::IllegalOwner); // Abort because the signer lacks the guardian role.
    }
    let mut proposal = Proposal::unpack(&proposal_account.data.borrow())?; // Load the proposal state to check its status.
    if proposal.id != proposal_id { // Reject mismatched IDs to prevent cancelling the wrong proposal.
        msg!("Proposal ID mismatch prevents cancelling the wrong proposal"); // Explain the mismatch failure.
        return Err(ProgramError::InvalidAccountData); // Abort to protect proposal integrity.
    }
    if proposal.status != 3 { // Only Queued proposals can be cancelled; once executed the decision is final.
        msg!("Cancellation only allowed during the queued timelock window"); // Explain the timing restriction.
        return Err(ProgramError::InvalidAccountData); // Abort because the proposal is not in the cancellable state.
    }
    proposal.status = 5; // Mark the proposal as Cancelled (5) so it is permanently excluded from execution.
    Proposal::pack(proposal, &mut proposal_account.data.borrow_mut())?; // Save the cancelled status.
    msg!("Proposal {} cancelled by guardian", proposal_id); // Log the cancellation for transparency.
    Ok(()) // Return success so the transaction is committed.
}
