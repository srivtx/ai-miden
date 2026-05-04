use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    pubkey::Pubkey,
    system_instruction,
    sysvar::{rent::Rent, Sysvar},
};
use spl_token::instruction as token_instruction;

// Define the program entrypoint so the Solana runtime routes instructions here
entrypoint!(process_instruction);

// Main instruction dispatcher for the multisig program
pub fn process_instruction(
    program_id: &Pubkey,      // Public key of this deployed multisig program
    accounts: &[AccountInfo], // All accounts provided in the instruction
    instruction_data: &[u8],  // Serialized instruction type and parameters
) -> ProgramResult {
    // Deserialize the instruction variant from raw bytes
    let instruction = MultisigInstruction::unpack(instruction_data)?;

    // Route to the appropriate handler based on the instruction variant
    match instruction {
        MultisigInstruction::CreateMultisig { threshold, signers } => {
            // Initialize a new multisig config with a signer set and threshold
            process_create_multisig(program_id, accounts, threshold, signers)
        }
        MultisigInstruction::CreateProposal => {
            // Create a new proposal account to track approvals
            process_create_proposal(program_id, accounts)
        }
        MultisigInstruction::Approve => {
            // Record an approval from a signer in the signer set
            process_approve(program_id, accounts)
        }
        MultisigInstruction::Execute { amount } => {
            // Execute the proposal if threshold approvals have been reached
            process_execute(program_id, accounts, amount)
        }
    }
}

// Enumeration of all instructions supported by the multisig program
pub enum MultisigInstruction {
    CreateMultisig {
        threshold: u8,          // Minimum signers required to execute
        signers: Vec<Pubkey>,   // List of authorized signer public keys
    },
    CreateProposal,             // Initialize a new proposal for voting
    Approve,                    // Record a signer's approval for a proposal
    Execute { amount: u64 },    // Execute the proposal action if threshold met
}

impl MultisigInstruction {
    // Deserialize raw instruction bytes into a typed instruction variant
    pub fn unpack(input: &[u8]) -> Result<Self, ProgramError> {
        // Require at least one byte for the variant tag
        if input.is_empty() {
            return Err(ProgramError::InvalidInstructionData);
        }
        let (tag, rest) = input.split_first().unwrap();
        match tag {
            0 => {
                // CreateMultisig: first byte is threshold, rest is signers
                if rest.is_empty() {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let threshold = rest[0];
                let signer_count = rest[1] as usize;
                let mut signers = Vec::with_capacity(signer_count);
                let mut offset = 2;
                for _ in 0..signer_count {
                    if rest.len() < offset + 32 {
                        return Err(ProgramError::InvalidInstructionData);
                    }
                    let pk = Pubkey::new(&rest[offset..offset + 32]);
                    signers.push(pk);
                    offset += 32;
                }
                Ok(MultisigInstruction::CreateMultisig { threshold, signers })
            }
            1 => Ok(MultisigInstruction::CreateProposal),
            2 => Ok(MultisigInstruction::Approve),
            3 => {
                // Execute expects 8 bytes for a u64 amount
                if rest.len() != 8 {
                    return Err(ProgramError::InvalidInstructionData);
                }
                let amount = u64::from_le_bytes(rest.try_into().unwrap());
                Ok(MultisigInstruction::Execute { amount })
            }
            _ => Err(ProgramError::InvalidInstructionData),
        }
    }
}

// Borsh-serializable state stored in the multisig config account
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct MultisigState {
    // Minimum number of approvals required to execute a proposal
    pub threshold: u8,
    // Ordered list of authorized signer public keys
    pub signers: Vec<Pubkey>,
    // PDA bump seed for address verification
    pub bump: u8,
    // Whether the multisig has been initialized
    pub is_initialized: bool,
}

// Borsh-serializable state stored in each proposal account
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct ProposalState {
    // The multisig config account this proposal belongs to
    pub multisig: Pubkey,
    // Number of distinct valid approvals received so far
    pub approval_count: u8,
    // Set of signer public keys that have already approved
    pub approvers: Vec<Pubkey>,
    // Whether the proposal has already been executed
    pub is_executed: bool,
    // Whether the proposal has been initialized
    pub is_initialized: bool,
}

// Handler to initialize a new multisig config account
fn process_create_multisig(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    threshold: u8,
    signers: Vec<Pubkey>,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the creation of the multisig config account
    let payer_account = next_account_info(account_info_iter)?;
    // The multisig config account that will store the signer set and threshold
    let multisig_account = next_account_info(account_info_iter)?;
    // Rent sysvar for calculating rent exemption
    let rent_sysvar = next_account_info(account_info_iter)?;
    // System program needed to create the multisig config account
    let system_program = next_account_info(account_info_iter)?;

    // Only the payer can authorize the creation and funding of the account
    if !payer_account.is_signer {
        msg!("Payer must sign to create multisig");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Validate that the threshold is achievable given the signer set size
    if threshold == 0 || threshold as usize > signers.len() {
        msg!("Invalid threshold for signer set size");
        return Err(ProgramError::InvalidArgument);
    }

    // Derive a PDA for the multisig config to make the address predictable
    let multisig_seeds = &[b"multisig", payer_account.key.as_ref()];
    let (expected_multisig_pda, multisig_bump) =
        Pubkey::find_program_address(multisig_seeds, program_id);

    // Reject if the provided account does not match the derived PDA
    if expected_multisig_pda != *multisig_account.key {
        msg!("Invalid multisig account address");
        return Err(ProgramError::InvalidAccountData);
    }

    // Calculate rent-exempt balance for the multisig config account size
    let rent = Rent::from_account_info(rent_sysvar)?;
    // Compute serialized size by creating a temporary state object
    let temp_state = MultisigState {
        threshold,
        signers: signers.clone(),
        bump: multisig_bump,
        is_initialized: true,
    };
    let state_space = temp_state.try_to_vec().unwrap().len();
    let required_lamports = rent.minimum_balance(state_space);

    // CPI to system program to create the multisig config PDA account
    invoke_signed(
        &system_instruction::create_account(
            payer_account.key,
            multisig_account.key,
            required_lamports,
            state_space as u64,
            program_id, // Multisig program owns the config account
        ),
        &[
            payer_account.clone(),
            multisig_account.clone(),
            system_program.clone(),
        ],
        &[&[b"multisig", payer_account.key.as_ref(), &[multisig_bump]]],
    )?;

    // Serialize the multisig state into the account data
    temp_state.serialize(&mut &mut multisig_account.data.borrow_mut()[..])?;

    msg!(
        "Multisig created with threshold {} and {} signers",
        threshold,
        signers.len()
    );
    Ok(())
}

// Handler to create a new proposal for the multisig to vote on
fn process_create_proposal(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // Payer funds the creation of the proposal account
    let payer_account = next_account_info(account_info_iter)?;
    // The proposal account that will track approvals
    let proposal_account = next_account_info(account_info_iter)?;
    // The multisig config this proposal belongs to
    let multisig_account = next_account_info(account_info_iter)?;
    // Rent sysvar for rent exemption calculation
    let rent_sysvar = next_account_info(account_info_iter)?;
    // System program to create the proposal account
    let system_program = next_account_info(account_info_iter)?;

    // Only the payer can authorize the creation of the proposal account
    if !payer_account.is_signer {
        msg!("Payer must sign to create proposal");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the multisig state to link the proposal to it
    let multisig_state = MultisigState::try_from_slice(&multisig_account.data.borrow())?;
    if !multisig_state.is_initialized {
        msg!("Multisig not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Derive a unique PDA for the proposal based on the multisig and payer
    let proposal_seeds = &[
        b"proposal",
        multisig_account.key.as_ref(),
        payer_account.key.as_ref(),
    ];
    let (expected_proposal_pda, proposal_bump) =
        Pubkey::find_program_address(proposal_seeds, program_id);

    // Ensure the provided proposal account matches the derived address
    if expected_proposal_pda != *proposal_account.key {
        msg!("Invalid proposal account address");
        return Err(ProgramError::InvalidAccountData);
    }

    // Calculate rent-exempt balance for the proposal state account
    let rent = Rent::from_account_info(rent_sysvar)?;
    let temp_proposal = ProposalState {
        multisig: *multisig_account.key,
        approval_count: 0,
        approvers: Vec::new(),
        is_executed: false,
        is_initialized: true,
    };
    let proposal_space = temp_proposal.try_to_vec().unwrap().len();
    let required_lamports = rent.minimum_balance(proposal_space);

    // CPI to system program to create the proposal PDA account
    invoke_signed(
        &system_instruction::create_account(
            payer_account.key,
            proposal_account.key,
            required_lamports,
            proposal_space as u64,
            program_id, // Multisig program owns the proposal account
        ),
        &[
            payer_account.clone(),
            proposal_account.clone(),
            system_program.clone(),
        ],
        &[&[
            b"proposal",
            multisig_account.key.as_ref(),
            payer_account.key.as_ref(),
            &[proposal_bump],
        ]],
    )?;

    // Serialize the initial proposal state into the account data
    temp_proposal.serialize(&mut &mut proposal_account.data.borrow_mut()[..])?;

    msg!("Proposal created for multisig {}", multisig_account.key);
    Ok(())
}

// Handler to record an approval from a signer
fn process_approve(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The signer who is approving the proposal
    let signer_account = next_account_info(account_info_iter)?;
    // The proposal account that will record this approval
    let proposal_account = next_account_info(account_info_iter)?;
    // The multisig config account containing the signer set and threshold
    let multisig_account = next_account_info(account_info_iter)?;

    // Verify the signer actually signed this transaction
    if !signer_account.is_signer {
        msg!("Signer must sign to approve");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the multisig state to access the signer set
    let multisig_state = MultisigState::try_from_slice(&multisig_account.data.borrow())?;
    if !multisig_state.is_initialized {
        msg!("Multisig not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Verify the signer is in the authorized signer set
    let is_authorized = multisig_state.signers.contains(signer_account.key);
    if !is_authorized {
        msg!("Signer is not in the multisig signer set");
        return Err(ProgramError::IllegalOwner);
    }

    // Deserialize the proposal state to update approval records
    let mut proposal_state =
        ProposalState::try_from_slice(&proposal_account.data.borrow())?;
    if !proposal_state.is_initialized {
        msg!("Proposal not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Ensure the proposal belongs to the provided multisig config
    if proposal_state.multisig != *multisig_account.key {
        msg!("Proposal does not belong to this multisig");
        return Err(ProgramError::InvalidAccountData);
    }

    // Prevent approving an already executed proposal
    if proposal_state.is_executed {
        msg!("Proposal already executed");
        return Err(ProgramError::InvalidArgument);
    }

    // Prevent the same signer from approving twice
    if proposal_state.approvers.contains(signer_account.key) {
        msg!("Signer has already approved this proposal");
        return Err(ProgramError::InvalidArgument);
    }

    // Record the approval by incrementing the count and adding the signer
    proposal_state.approval_count += 1;
    proposal_state.approvers.push(*signer_account.key);
    proposal_state.serialize(&mut &mut proposal_account.data.borrow_mut()[..])?;

    msg!(
        "Approval recorded. Current count: {} / {}",
        proposal_state.approval_count,
        multisig_state.threshold
    );
    Ok(())
}

// Handler to execute the proposal if the threshold has been reached
fn process_execute(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();

    // The executor who triggers the execution; must be a signer
    let executor = next_account_info(account_info_iter)?;
    // The proposal account to check and mark as executed
    let proposal_account = next_account_info(account_info_iter)?;
    // The multisig config account to read threshold and validate
    let multisig_account = next_account_info(account_info_iter)?;
    // The multisig PDA's token account that holds the treasury funds
    let treasury_ata = next_account_info(account_info_iter)?;
    // The recipient's token account that will receive the funds
    let recipient_ata = next_account_info(account_info_iter)?;
    // SPL Token program for the transfer CPI
    let token_program = next_account_info(account_info_iter)?;

    // Verify the executor signed the transaction
    if !executor.is_signer {
        msg!("Executor must sign to execute proposal");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Deserialize the multisig state to read the threshold
    let multisig_state = MultisigState::try_from_slice(&multisig_account.data.borrow())?;
    if !multisig_state.is_initialized {
        msg!("Multisig not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Deserialize the proposal state to check approvals
    let mut proposal_state =
        ProposalState::try_from_slice(&proposal_account.data.borrow())?;
    if !proposal_state.is_initialized {
        msg!("Proposal not initialized");
        return Err(ProgramError::UninitializedAccount);
    }

    // Ensure the proposal belongs to the provided multisig
    if proposal_state.multisig != *multisig_account.key {
        msg!("Proposal does not belong to this multisig");
        return Err(ProgramError::InvalidAccountData);
    }

    // Reject execution if the proposal was already executed
    if proposal_state.is_executed {
        msg!("Proposal already executed");
        return Err(ProgramError::InvalidArgument);
    }

    // Enforce the threshold: approval count must meet or exceed it
    if proposal_state.approval_count < multisig_state.threshold {
        msg!(
            "Insufficient approvals: {} / {}",
            proposal_state.approval_count,
            multisig_state.threshold
        );
        return Err(ProgramError::Custom(3)); // Custom error for threshold not met
    }

    // Derive the multisig PDA seeds so the program can sign for the treasury
    let multisig_seeds = &[b"multisig", executor.key.as_ref()];
    let (expected_multisig_pda, multisig_bump) =
        Pubkey::find_program_address(multisig_seeds, program_id);

    // Verify the treasury ATA is owned by the multisig PDA
    if *treasury_ata.owner != *token_program.key {
        msg!("Treasury ATA is not a valid token account");
        return Err(ProgramError::InvalidAccountData);
    }

    // CPI to SPL Token program to transfer treasury funds to the recipient
    // Using invoke_signed because the multisig PDA must authorize the transfer
    invoke_signed(
        &token_instruction::transfer(
            token_program.key,
            treasury_ata.key,
            recipient_ata.key,
            &expected_multisig_pda, // Authority is the multisig PDA
            &[],
            amount,
        )?,
        &[
            treasury_ata.clone(),
            recipient_ata.clone(),
            multisig_account.clone(),
            token_program.clone(),
        ],
        &[&[b"multisig", executor.key.as_ref(), &[multisig_bump]]],
    )?;

    // Mark the proposal as executed to prevent replay
    proposal_state.is_executed = true;
    proposal_state.serialize(&mut &mut proposal_account.data.borrow_mut()[..])?;

    msg!(
        "Proposal executed. Transferred {} tokens to recipient.",
        amount
    );
    Ok(())
}
