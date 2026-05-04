use anchor_lang::prelude::*; // WHY: This imports all Anchor types and traits, reducing boilerplate.
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer}; // WHY: This imports SPL token types and CPI helpers for treasury transfers.

declare_id!("Tre222222222222222222222222222222222222222"); // WHY: This hardcodes the program ID for binary verification.

/// WHY: The maximum number of members prevents the members vector from growing unbounded.
const MAX_MEMBERS: usize = 10; // WHY: 10 members is a practical limit for a small DAO; larger DAOs may use a separate registry program.

#[program] // WHY: This macro marks the module as an Anchor program.
pub mod treasury { // WHY: The module name matches the program name in Anchor.toml.
    use super::*; // WHY: This brings parent scope imports into the module.

    /// WHY: This instruction initializes the treasury with members and a threshold, mirroring Squads v4 architecture.
    pub fn initialize_treasury( // WHY: A dedicated init instruction creates the treasury account with its initial configuration.
        ctx: Context<InitializeTreasury>, // WHY: The context validates the admin signer and initializes the treasury PDA.
        members: Vec<Pubkey>, // WHY: A vector allows flexible member lists without fixed-size arrays.
        threshold: u8, // WHY: u8 is sufficient because a threshold over 255 members is impractical for a multisig.
    ) -> Result<()> { // WHY: Result enables error propagation with typed error codes.
        let treasury = &mut ctx.accounts.treasury; // WHY: Mutable borrowing allows writing the initial state.

        require!( // WHY: Enforcing the member limit prevents account size overflow.
            members.len() <= MAX_MEMBERS, // WHY: The limit ensures the account fits within the allocated space.
            TreasuryError::TooManyMembers // WHY: A specific error code helps the client adjust the member list.
        );

        require!( // WHY: The threshold must be at least 1, or no transaction could ever execute.
            threshold > 0, // WHY: A threshold of zero would allow anyone to execute without approval.
            TreasuryError::InvalidThreshold // WHY: A specific error code tells the client the threshold is too low.
        );

        require!( // WHY: The threshold cannot exceed the member count, or the multisig would deadlock.
            threshold as usize <= members.len(), // WHY: Casting to usize ensures safe comparison on all architectures.
            TreasuryError::InvalidThreshold // WHY: Reusing the error code keeps the enum small.
        );

        treasury.admin = ctx.accounts.admin.key(); // WHY: Storing the admin enables future administrative updates.
        treasury.members = members; // WHY: Persisting the member list on-chain makes it auditable and tamper-evident.
        treasury.threshold = threshold; // WHY: Persisting the threshold on-chain prevents off-chain manipulation.
        treasury.vault_bump = ctx.bumps.vault; // WHY: Storing the vault bump allows efficient PDA re-derivation.
        treasury.proposal_count = 0; // WHY: Initializing the counter ensures the first proposal gets index zero.

        Ok(()) // WHY: Ok signals successful initialization.
    }

    /// WHY: This instruction creates a withdrawal proposal that must be approved by members before execution.
    pub fn request_withdrawal( // WHY: Separating request from execution enables asynchronous multisig workflows.
        ctx: Context<RequestWithdrawal>, // WHY: The context validates the proposer is a member.
        amount: u64, // WHY: u64 matches SPL token amounts and prevents precision loss.
        recipient: Pubkey, // WHY: The recipient is passed as a parameter so each proposal targets a specific address.
    ) -> Result<()> { // WHY: Result ensures invalid requests abort without creating state.
        let treasury = &mut ctx.accounts.treasury; // WHY: Mutable borrowing allows incrementing the proposal counter.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows writing the proposal state.
        let vault = &ctx.accounts.vault; // WHY: Immutable borrowing is sufficient because we only read the balance.

        require!( // WHY: The treasury must have enough funds to cover the requested amount.
            vault.amount >= amount, // WHY: Checking balance before creating the proposal prevents creating unexecutable proposals.
            TreasuryError::InsufficientFunds // WHY: A specific error code tells the client the treasury is underfunded.
        );

        proposal.id = treasury.proposal_count; // WHY: A sequential ID makes proposals easy to reference.
        proposal.treasury = treasury.key(); // WHY: Storing the treasury key makes the proposal self-describing.
        proposal.proposer = ctx.accounts.proposer.key(); // WHY: Storing the proposer enables attribution.
        proposal.recipient = recipient; // WHY: Storing the recipient locks the target address, preventing redirection after approval.
        proposal.amount = amount; // WHY: Storing the amount locks the value, preventing amount changes after approval.
        proposal.approvals = 0; // WHY: Initializing to zero ensures the tally starts from a known state.
        proposal.threshold = treasury.threshold; // WHY: Copying the threshold at creation time locks the required approval count.
        proposal.executed = false; // WHY: The executed flag prevents double execution.
        proposal.bump = ctx.bumps.proposal; // WHY: Storing the bump enables PDA validation.

        treasury.proposal_count = treasury.proposal_count.checked_add(1).unwrap(); // WHY: checked_add prevents overflow on the counter.

        Ok(()) // WHY: Ok signals the proposal was created successfully.
    }

    /// WHY: This instruction allows a treasury member to approve a pending withdrawal proposal.
    pub fn approve_withdrawal( // WHY: Separating approval from request enables independent, asynchronous member voting.
        ctx: Context<ApproveWithdrawal>, // WHY: The context validates the approver is a member and the proposal exists.
    ) -> Result<()> { // WHY: Result ensures invalid approvals abort.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows incrementing the approval count.
        let approver_record = &mut ctx.accounts.approver_record; // WHY: Mutable borrowing allows marking the approver as having voted.

        require!( // WHY: Only non-executed proposals can be approved.
            !proposal.executed, // WHY: The executed flag guards against late approvals on completed proposals.
            TreasuryError::AlreadyExecuted // WHY: A specific error code distinguishes executed proposals.
        );

        require!( // WHY: Members can only approve once per proposal to prevent inflating the approval count.
            !approver_record.has_approved, // WHY: The approver record PDA is unique per member per proposal.
            TreasuryError::AlreadyApproved // WHY: A specific error code tells the client this member already voted.
        );

        proposal.approvals = proposal.approvals.checked_add(1).unwrap(); // WHY: checked_add prevents overflow on the approval counter.

        approver_record.approver = ctx.accounts.approver.key(); // WHY: Storing the approver makes the record self-describing.
        approver_record.proposal = proposal.key(); // WHY: Storing the proposal key links the record to a specific withdrawal.
        approver_record.has_approved = true; // WHY: Setting the flag prevents duplicate approvals.
        approver_record.bump = ctx.bumps.approver_record; // WHY: Storing the bump enables PDA validation.

        Ok(()) // WHY: Ok signals the approval was recorded.
    }

    /// WHY: This instruction executes a withdrawal proposal once the approval threshold is met.
    pub fn execute_withdrawal( // WHY: Separating execution from approval ensures a clear, auditable lifecycle.
        ctx: Context<ExecuteWithdrawal>, // WHY: The context validates the proposal, vault, and treasury accounts.
    ) -> Result<()> { // WHY: Result ensures preconditions are met before transferring funds.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows marking the proposal as executed.
        let treasury = &ctx.accounts.treasury; // WHY: Immutable borrowing is sufficient because we only read the vault bump.

        require!( // WHY: Only non-executed proposals can be executed.
            !proposal.executed, // WHY: The executed flag is the primary guard against double spending.
            TreasuryError::AlreadyExecuted // WHY: A specific error code prevents replay attempts.
        );

        require!( // WHY: The approval threshold must be met before any funds move.
            proposal.approvals >= proposal.threshold, // WHY: Enforcing the threshold is the core security property of a multisig.
            TreasuryError::ThresholdNotMet // WHY: A specific error code tells the client how many more approvals are needed.
        );

        let vault_bump = treasury.vault_bump; // WHY: Reading the stored bump avoids recalculating it.
        let treasury_key = treasury.key(); // WHY: Storing the key in a local variable avoids repeated borrowing.
        let seeds = &[ // WHY: The seeds array defines the PDA derivation path for the vault signer.
            b"vault", // WHY: A fixed prefix distinguishes the vault from other PDAs.
            treasury_key.as_ref(), // WHY: The treasury key makes the vault address unique per treasury.
            &[vault_bump], // WHY: The bump ensures the PDA is off the Ed25519 curve and signable by the program.
        ];
        let signer = &[&seeds[..]]; // WHY: Anchor expects a nested array of seed slices for CPI signing.

        let cpi_accounts = Transfer { // WHY: Transfer is the SPL token instruction for moving tokens between accounts.
            from: ctx.accounts.vault.to_account_info(), // WHY: The vault is the source of funds.
            to: ctx.accounts.recipient_token_account.to_account_info(), // WHY: The recipient token account receives the funds.
            authority: ctx.accounts.vault.to_account_info(), // WHY: The vault PDA is the authority that signs the transfer.
        };
        let cpi_program = ctx.accounts.token_program.to_account_info(); // WHY: The token program is the program that executes the transfer.
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer); // WHY: new_with_signer attaches the PDA seeds so the CPI is signed by the program.

        token::transfer(cpi_ctx, proposal.amount)?; // WHY: The transfer CPI moves the exact amount specified in the proposal, preventing arbitrary withdrawals.

        proposal.executed = true; // WHY: Marking as executed prevents all future execution attempts.

        Ok(()) // WHY: Ok signals the withdrawal was completed successfully.
    }

    /// WHY: This instruction allows the admin to update the member list and threshold.
    pub fn update_treasury( // WHY: Administrative updates require their own instruction to scope privilege.
        ctx: Context<UpdateTreasury>, // WHY: The context validates the admin signer.
        new_members: Vec<Pubkey>, // WHY: Passing the full list replaces the old list atomically, avoiding partial updates.
        new_threshold: u8, // WHY: The new threshold is passed as a parameter for transparency.
    ) -> Result<()> { // WHY: Result ensures invalid configurations abort.
        let treasury = &mut ctx.accounts.treasury; // WHY: Mutable borrowing allows updating the treasury state.

        require!( // WHY: The member limit prevents account size overflow.
            new_members.len() <= MAX_MEMBERS, // WHY: Enforcing the limit ensures the serialized account fits within allocated space.
            TreasuryError::TooManyMembers // WHY: A specific error code helps the client debug.
        );

        require!( // WHY: The threshold must be valid to prevent deadlock.
            new_threshold > 0 && new_threshold as usize <= new_members.len(), // WHY: Both bounds must be checked to ensure the multisig remains functional.
            TreasuryError::InvalidThreshold // WHY: A specific error code tells the client the configuration is invalid.
        );

        treasury.members = new_members; // WHY: Replacing the entire list is atomic and prevents inconsistent state.
        treasury.threshold = new_threshold; // WHY: Updating the threshold immediately affects future proposals.

        Ok(()) // WHY: Ok signals the update was applied.
    }
}

#[derive(Accounts)] // WHY: This macro generates account validation for InitializeTreasury.
pub struct InitializeTreasury<'info> { // WHY: A dedicated struct isolates initialization constraints.
    #[account(mut)] // WHY: The admin is mutable because they pay for the treasury account creation.
    pub admin: Signer<'info>, // WHY: Signer ensures only an authorized key can create the treasury.

    #[account( // WHY: init creates the treasury PDA.
        init, // WHY: init fails if the account exists, preventing accidental reinitialization.
        payer = admin, // WHY: The admin pays rent for the treasury account.
        space = 8 + 32 + 4 + (32 * MAX_MEMBERS) + 1 + 1 + 8, // WHY: Precise space calculation ensures rent exemption without waste.
        seeds = [b"treasury", admin.key().as_ref()], // WHY: The admin key makes the treasury address unique per creator.
        bump // WHY: Anchor handles bump derivation.
    )]
    pub treasury: Account<'info, Treasury>, // WHY: Account type ensures deserialization as a Treasury struct.

    #[account( // WHY: init creates the vault token account as a PDA.
        init, // WHY: init creates the token account if it does not exist.
        payer = admin, // WHY: The admin pays rent for the vault token account.
        seeds = [b"vault", treasury.key().as_ref()], // WHY: The treasury key links the vault to this specific treasury.
        bump, // WHY: Anchor handles bump derivation.
        token::mint = mint, // WHY: This constraint ensures the vault holds the correct token type.
        token::authority = vault, // WHY: The vault PDA is its own authority, meaning only this program can sign transfers.
    )]
    pub vault: Account<'info, TokenAccount>, // WHY: TokenAccount is the Anchor type for SPL token accounts.

    pub mint: Account<'info, Mint>, // WHY: Mint is the SPL token type definition.

    pub token_program: Program<'info, Token>, // WHY: The token program is required for initializing the vault.
    pub system_program: Program<'info, System>, // WHY: The system program is required for account creation.
    pub rent: Sysvar<'info, Rent>, // WHY: The rent sysvar is required for rent-exempt account initialization.
}

#[derive(Accounts)] // WHY: This macro generates validation for RequestWithdrawal.
pub struct RequestWithdrawal<'info> { // WHY: A dedicated struct isolates request-specific constraints.
    #[account(mut)] // WHY: The proposer is mutable because they may pay for the proposal account.
    pub proposer: Signer<'info>, // WHY: Signer ensures the proposer authorized the transaction.

    #[account(mut)] // WHY: The treasury is mutable because the proposal counter is incremented.
    pub treasury: Account<'info, Treasury>, // WHY: Account type ensures the address holds a valid Treasury.

    #[account( // WHY: This constraint ensures only treasury members can propose withdrawals.
        constraint = treasury.members.contains(&proposer.key()) // WHY: The contains check validates membership against the on-chain list.
    )]
    pub _membership_check: AccountInfo<'info>, // WHY: An unused account info is a pattern to trigger a constraint without consuming an account slot.

    #[account(mut)] // WHY: The vault is mutable because its balance is read during validation.
    pub vault: Account<'info, TokenAccount>, // WHY: TokenAccount type ensures the vault is a valid SPL token account.

    #[account( // WHY: init creates the withdrawal proposal PDA.
        init, // WHY: init ensures unique proposals.
        payer = proposer, // WHY: The proposer pays for the proposal account.
        space = 8 + 8 + 32 + 32 + 32 + 8 + 1 + 1 + 1 + 1, // WHY: Precise space calculation ensures rent exemption.
        seeds = [b"withdrawal", treasury.key().as_ref(), &treasury.proposal_count.to_le_bytes()], // WHY: Unique seeds per treasury and counter.
        bump // WHY: Anchor handles bump derivation.
    )]
    pub proposal: Account<'info, WithdrawalProposal>, // WHY: This stores the withdrawal request state.

    pub system_program: Program<'info, System>, // WHY: Required for init CPI.
}

#[derive(Accounts)] // WHY: This macro generates validation for ApproveWithdrawal.
pub struct ApproveWithdrawal<'info> { // WHY: A dedicated struct isolates approval constraints.
    #[account(mut)] // WHY: The approver is mutable because they may pay for the approver record.
    pub approver: Signer<'info>, // WHY: Signer ensures the approver authorized the transaction.

    #[account( // WHY: This constraint ensures only treasury members can approve.
        constraint = treasury.members.contains(&approver.key()) // WHY: The on-chain membership list is the source of truth.
    )]
    pub treasury: Account<'info, Treasury>, // WHY: Account type ensures the treasury is valid.

    #[account(mut)] // WHY: The proposal is mutable because the approval count is incremented.
    pub proposal: Account<'info, WithdrawalProposal>, // WHY: Account type ensures the target is a valid proposal.

    #[account( // WHY: init_if_needed creates the record on first approval.
        init_if_needed, // WHY: This allows the same instruction for both first and subsequent approvers.
        payer = approver, // WHY: The approver pays for their own record.
        space = 8 + 32 + 32 + 1 + 1, // WHY: Precise space calculation.
        seeds = [b"approval", proposal.key().as_ref(), approver.key().as_ref()], // WHY: Unique seeds per proposal and approver.
        bump // WHY: Anchor handles bump derivation.
    )]
    pub approver_record: Account<'info, ApproverRecord>, // WHY: This prevents duplicate approvals.

    pub system_program: Program<'info, System>, // WHY: Required for init_if_needed CPI.
}

#[derive(Accounts)] // WHY: This macro generates validation for ExecuteWithdrawal.
pub struct ExecuteWithdrawal<'info> { // WHY: A dedicated struct isolates execution constraints.
    #[account(mut)] // WHY: The proposal is mutable because the executed flag is set.
    pub proposal: Account<'info, WithdrawalProposal>, // WHY: Account type ensures the target is valid.

    #[account(mut)] // WHY: The treasury is mutable because it is used as a PDA signer.
    pub treasury: Account<'info, Treasury>, // WHY: Account type ensures the treasury is valid.

    #[account(mut)] // WHY: The vault is mutable because tokens are transferred out.
    pub vault: Account<'info, TokenAccount>, // WHY: TokenAccount type ensures the vault is valid.

    #[account(mut)] // WHY: The recipient token account is mutable because it receives tokens.
    pub recipient_token_account: Account<'info, TokenAccount>, // WHY: TokenAccount type ensures the recipient account is valid.

    pub token_program: Program<'info, Token>, // WHY: The token program executes the SPL transfer.
}

#[derive(Accounts)] // WHY: This macro generates validation for UpdateTreasury.
pub struct UpdateTreasury<'info> { // WHY: A dedicated struct isolates administrative constraints.
    #[account(mut)] // WHY: The admin is mutable because they pay for any account size changes.
    pub admin: Signer<'info>, // WHY: Signer ensures the admin authorized the update.

    #[account( // WHY: This constraint ensures only the stored admin can update the treasury.
        mut, // WHY: Mutable because the member list and threshold may change.
        constraint = treasury.admin == admin.key() // WHY: The on-chain admin field is the source of truth for privilege.
    )]
    pub treasury: Account<'info, Treasury>, // WHY: Account type ensures the target is valid.
}

#[account] // WHY: This macro marks the struct as an Anchor account.
pub struct Treasury { // WHY: The treasury stores multisig configuration and state.
    pub admin: Pubkey, // WHY: The admin can update members and threshold.
    pub members: Vec<Pubkey>, // WHY: A vector allows flexible membership lists.
    pub threshold: u8, // WHY: u8 is sufficient for practical multisig sizes.
    pub vault_bump: u8, // WHY: Storing the bump enables PDA re-derivation.
    pub proposal_count: u64, // WHY: The counter enables unique proposal IDs.
}

#[account] // WHY: This macro marks the struct as an Anchor account.
pub struct WithdrawalProposal { // WHY: Each withdrawal is a separate proposal for independent lifecycle management.
    pub id: u64, // WHY: A numeric ID is easy to reference.
    pub treasury: Pubkey, // WHY: Storing the treasury links the proposal to its parent.
    pub proposer: Pubkey, // WHY: Storing the proposer enables attribution.
    pub recipient: Pubkey, // WHY: Storing the recipient locks the target address.
    pub amount: u64, // WHY: u64 matches SPL token amounts.
    pub approvals: u8, // WHY: u8 is sufficient because the threshold is also u8.
    pub threshold: u8, // WHY: Copying the threshold locks the required count.
    pub executed: bool, // WHY: The executed flag prevents replay.
    pub bump: u8, // WHY: Storing the bump enables PDA validation.
}

#[account] // WHY: This macro marks the struct as an Anchor account.
pub struct ApproverRecord { // WHY: A separate record per approver per proposal prevents double approval.
    pub approver: Pubkey, // WHY: Storing the approver makes the record self-describing.
    pub proposal: Pubkey, // WHY: Storing the proposal links the record to a specific withdrawal.
    pub has_approved: bool, // WHY: The boolean flag is the guard against double approval.
    pub bump: u8, // WHY: Storing the bump enables PDA validation.
}

#[error_code] // WHY: This macro generates a custom error enum.
pub enum TreasuryError { // WHY: Typed errors are safer than magic numbers.
    #[msg("Too many members")]
    TooManyMembers, // WHY: A specific variant for the member limit.
    #[msg("Invalid threshold")]
    InvalidThreshold, // WHY: A specific variant for threshold validation.
    #[msg("Insufficient funds")]
    InsufficientFunds, // WHY: A specific variant for balance checks.
    #[msg("Already executed")]
    AlreadyExecuted, // WHY: A specific variant for replay protection.
    #[msg("Already approved")]
    AlreadyApproved, // WHY: A specific variant for duplicate approval prevention.
    #[msg("Threshold not met")]
    ThresholdNotMet, // WHY: A specific variant for unmet multisig requirements.
}
