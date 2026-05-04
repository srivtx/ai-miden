use anchor_lang::prelude::*; // WHY: This imports all commonly used Anchor types and traits, reducing boilerplate in every file.
use anchor_spl::token::{self, Mint, Token, TokenAccount}; // WHY: This imports SPL token types and CPI helpers, enabling typed token operations instead of raw program invocations.

declare_id!("Gov111111111111111111111111111111111111111"); // WHY: This hardcodes the program ID so Anchor can verify the program address matches the deployed binary.

/// WHY: The maximum description length prevents account bloat and ensures the proposal account size fits within the declared space.
const MAX_DESCRIPTION_LENGTH: usize = 256; // WHY: 256 bytes is enough for a concise proposal summary while keeping rent costs predictable.

/// WHY: The maximum number of voters per proposal prevents the `has_voted` vector from growing unbounded and exceeding account size limits.
const MAX_VOTERS: usize = 1000; // WHY: 1000 voters is a practical limit for an MVP; production systems may use bitmaps or merkle trees instead.

#[program] // WHY: This macro marks the module as an Anchor program, automatically generating the entrypoint and instruction dispatcher.
pub mod governance { // WHY: The module name must match the program name in Anchor.toml for the build system to link correctly.
    use super::*; // WHY: This brings all imports from the parent scope into the module so instruction functions can use them.

    /// WHY: This instruction initializes the global governance configuration, which stores parameters shared across all proposals.
    pub fn initialize_governance( // WHY: The function name becomes the instruction name in the IDL, so it must be descriptive and unique.
        ctx: Context<InitializeGovernance>, // WHY: The Context type wraps all accounts, the program ID, and remaining accounts for the instruction.
        quorum: u64, // WHY: The quorum is the minimum total vote weight required for a proposal to be executable.
        timelock_delay: i64, // WHY: The timelock delay in seconds ensures a waiting period between vote completion and execution.
    ) -> Result<()> { // WHY: Anchor instructions return Result<()> so errors can propagate with automatic logging and program failure.
        let config = &mut ctx.accounts.config; // WHY: Mutable borrowing allows updating the config account fields after initialization.
        config.admin = ctx.accounts.admin.key(); // WHY: Storing the admin pubkey enables admin-only instructions via constraint checks later.
        config.governance_mint = ctx.accounts.governance_mint.key(); // WHY: Storing the mint address ensures all votes reference the correct governance token.
        config.quorum = quorum; // WHY: Persisting the quorum on-chain prevents off-chain manipulation of the execution threshold.
        config.timelock_delay = timelock_delay; // WHY: Persisting the delay on-chain makes it transparent and auditable by all participants.
        config.proposal_count = 0; // WHY: Initializing the counter to zero ensures the first proposal gets index zero.
        Ok(()) // WHY: Returning Ok signals successful execution to the Solana runtime, allowing the transaction to commit.
    }

    /// WHY: This instruction creates a new governance proposal as a PDA, making it immutable and deterministic.
    pub fn create_proposal( // WHY: Separating proposal creation into its own instruction keeps the instruction size small and focused.
        ctx: Context<CreateProposal>, // WHY: The context validates that the creator is a signer and the proposal PDA does not already exist.
        description: String, // WHY: The description is passed as a parameter and stored on-chain for transparency and auditability.
        deadline: i64, // WHY: The deadline is an absolute Unix timestamp, preventing timezone ambiguity and off-chain clock manipulation.
    ) -> Result<()> { // WHY: Result propagation ensures any validation failure aborts the transaction atomically.
        let config = &mut ctx.accounts.config; // WHY: Mutable borrowing allows incrementing the global proposal counter.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows writing the initial proposal state into the new PDA.

        require!( // WHY: Explicit validation with require! is more readable than inline if statements and integrates with Anchor error codes.
            description.len() <= MAX_DESCRIPTION_LENGTH, // WHY: Enforcing the length limit prevents account size overflow and excessive rent costs.
            GovernanceError::DescriptionTooLong // WHY: A typed error code provides a human-readable message to the client when validation fails.
        );

        let clock = Clock::get()?; // WHY: Fetching the on-chain clock ensures the deadline is compared against the validator's timestamp, not the client's.
        require!( // WHY: The deadline must be in the future so the proposal has a valid voting period.
            deadline > clock.unix_timestamp, // WHY: Using the validator clock prevents clients from passing expired deadlines.
            GovernanceError::InvalidDeadline // WHY: A specific error code helps clients distinguish between different failure modes.
        );

        proposal.id = config.proposal_count; // WHY: Assigning a sequential ID makes proposals easy to reference off-chain via a simple integer.
        proposal.creator = ctx.accounts.creator.key(); // WHY: Storing the creator enables filtering and attribution in the client UI.
        proposal.description = description; // WHY: Storing the description on-chain guarantees it cannot be altered after creation.
        proposal.quorum = config.quorum; // WHY: Copying the quorum at creation time locks the threshold, preventing admin changes from affecting active votes.
        proposal.votes_for = 0; // WHY: Initializing to zero ensures the tally starts from a known state.
        proposal.votes_against = 0; // WHY: Initializing to zero ensures the tally starts from a known state.
        proposal.deadline = deadline; // WHY: Persisting the deadline on-chain makes it enforceable by the program logic.
        proposal.executed = false; // WHY: The executed flag prevents double execution and allows client UIs to filter active proposals.
        proposal.bump = ctx.bumps.proposal; // WHY: Storing the bump seed allows future instructions to re-derive the PDA without recalculating.

        config.proposal_count = config.proposal_count.checked_add(1).unwrap(); // WHY: checked_add prevents integer overflow on the proposal counter.

        Ok(()) // WHY: Ok signals that the proposal was created successfully and all state changes should be committed.
    }

    /// WHY: This instruction allows a token holder to cast a vote weighted by their SPL token balance at vote time.
    pub fn cast_vote( // WHY: Separating voting into its own instruction allows atomic vote recording without affecting other proposal state.
        ctx: Context<CastVote>, // WHY: The context validates the voter, proposal, token account, and voter record PDA in one struct.
        vote_for: bool, // WHY: A boolean is the simplest representation for a binary yes/no vote.
    ) -> Result<()> { // WHY: Result ensures any validation failure rolls back the vote and prevents partial state updates.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows updating the proposal's vote tally.
        let voter_token_account = &ctx.accounts.voter_token_account; // WHY: Immutable borrowing is sufficient because we only read the token balance.
        let voter_record = &mut ctx.accounts.voter_record; // WHY: Mutable borrowing allows marking the voter as having voted.
        let config = &ctx.accounts.config; // WHY: Immutable borrowing is sufficient because we only read the governance mint for validation.

        let clock = Clock::get()?; // WHY: The validator clock ensures the deadline check is not manipulable by the client.
        require!( // WHY: Enforcing the deadline prevents late votes from altering the outcome after the voting period ends.
            clock.unix_timestamp < proposal.deadline, // WHY: Strictly less than ensures voting stops exactly at the deadline timestamp.
            GovernanceError::VotingPeriodEnded // WHY: A specific error code allows the client to show a "voting closed" message.
        );

        require!( // WHY: Preventing double voting is fundamental to election integrity.
            !voter_record.has_voted, // WHY: The voter record PDA is keyed by (proposal, voter), so it is unique per voter per proposal.
            GovernanceError::AlreadyVoted // WHY: A specific error code helps the client explain why the transaction was rejected.
        );

        require!( // WHY: The token account must belong to the voter so users cannot vote with someone else's tokens.
            voter_token_account.owner == ctx.accounts.voter.key(), // WHY: The owner field in a token account is the authority that can transfer tokens.
            GovernanceError::InvalidTokenAccount // WHY: A specific error code helps debug account configuration issues in the client.
        );

        require!( // WHY: The token account must match the governance mint so users cannot vote with random SPL tokens.
            voter_token_account.mint == config.governance_mint, // WHY: The mint field identifies which token type the account holds.
            GovernanceError::InvalidTokenAccount // WHY: Reusing the error code keeps the error enum small while covering related failures.
        );

        let vote_weight = voter_token_account.amount; // WHY: The amount field is the live token balance, which represents the voter's current stake.
        require!( // WHY: A voter with zero tokens has no stake and therefore no right to influence the outcome.
            vote_weight > 0, // WHY: Zero-weight votes would waste compute units and clutter the voter record without affecting the tally.
            GovernanceError::NoVotingPower // WHY: A specific error code tells the client the voter needs to acquire governance tokens first.
        );

        if vote_for { // WHY: The boolean determines whether the weight is added to the for or against tally.
            proposal.votes_for = proposal.votes_for.checked_add(vote_weight).unwrap(); // WHY: checked_add prevents integer overflow on the vote tally.
        } else {
            proposal.votes_against = proposal.votes_against.checked_add(vote_weight).unwrap(); // WHY: checked_add prevents integer overflow on the vote tally.
        }

        voter_record.voter = ctx.accounts.voter.key(); // WHY: Storing the voter pubkey in the record makes it easy to query who voted.
        voter_record.proposal = proposal.key(); // WHY: Storing the proposal key ensures the record is self-describing and audit-friendly.
        voter_record.weight = vote_weight; // WHY: Storing the weight at vote time enables historical analysis of voting power distribution.
        voter_record.vote_for = vote_for; // WHY: Storing the direction enables building vote breakdown UIs and dispute resolution.
        voter_record.has_voted = true; // WHY: Setting the flag prevents any future vote attempts by the same voter on this proposal.
        voter_record.bump = ctx.bumps.voter_record; // WHY: Storing the bump allows future instructions to validate the PDA address efficiently.

        Ok(()) // WHY: Ok signals that the vote was recorded and all state changes should be committed.
    }

    /// WHY: This instruction allows a token holder to delegate their voting power to another address.
    pub fn delegate_vote( // WHY: Delegation is essential for representative governance, allowing passive holders to entrust active participants.
        ctx: Context<DelegateVote>, // WHY: The context validates the delegator, delegatee, and delegation record accounts.
        delegatee: Pubkey, // WHY: The delegatee is passed as a parameter so the delegator can choose any valid Solana address.
    ) -> Result<()> { // WHY: Result ensures invalid delegations (e.g., self-delegation) abort the transaction.
        let delegation = &mut ctx.accounts.delegation_record; // WHY: Mutable borrowing allows writing the delegation state.
        let delegator = &ctx.accounts.delegator; // WHY: Immutable borrowing is sufficient because we only need the pubkey.

        require!( // WHY: Self-delegation is meaningless and would waste on-chain state.
            delegatee != delegator.key(), // WHY: Comparing pubkeys prevents the delegator from delegating to themselves.
            GovernanceError::SelfDelegation // WHY: A specific error code helps the client catch this input error early.
        );

        delegation.delegator = delegator.key(); // WHY: Storing the delegator makes the record self-describing and auditable.
        delegation.delegatee = delegatee; // WHY: Storing the delegatee defines who is authorized to vote on behalf of the delegator.
        delegation.active = true; // WHY: An active flag allows future revocation without deleting the account.
        delegation.bump = ctx.bumps.delegation_record; // WHY: Storing the bump enables efficient PDA validation in future instructions.

        Ok(()) // WHY: Ok signals that the delegation was recorded successfully.
    }

    /// WHY: This instruction executes a proposal after the deadline and timelock have passed, if quorum is met.
    pub fn execute_proposal( // WHY: Separating execution from voting ensures a clear lifecycle: propose, vote, wait, execute.
        ctx: Context<ExecuteProposal>, // WHY: The context validates the proposal PDA and ensures it has not already been executed.
    ) -> Result<()> { // WHY: Result ensures execution preconditions are met before any state changes occur.
        let proposal = &mut ctx.accounts.proposal; // WHY: Mutable borrowing allows marking the proposal as executed.
        let config = &ctx.accounts.config; // WHY: Immutable borrowing is sufficient because we only read the timelock delay.

        require!( // WHY: A proposal can only be executed once to prevent duplicate actions.
            !proposal.executed, // WHY: The executed flag is the simplest and most reliable guard against replay.
            GovernanceError::AlreadyExecuted // WHY: A specific error code tells the client the proposal is no longer active.
        );

        let clock = Clock::get()?; // WHY: The validator clock is the authoritative source of time on Solana.
        require!( // WHY: The proposal must have passed its deadline so the voting period is fully concluded.
            clock.unix_timestamp >= proposal.deadline, // WHY: Greater than or equal ensures the exact deadline timestamp is valid for execution.
            GovernanceError::VotingPeriodActive // WHY: A specific error code tells the client to wait before attempting execution.
        );

        let timelock_end = proposal.deadline.checked_add(config.timelock_delay).unwrap(); // WHY: checked_add prevents overflow when calculating the timelock end time.
        require!( // WHY: The timelock ensures a cooling-off period for community review before irreversible actions.
            clock.unix_timestamp >= timelock_end, // WHY: Enforcing the timelock protects against rushed or coerced executions.
            GovernanceError::TimelockActive // WHY: A specific error code tells the client exactly how long to wait.
        );

        let total_votes = proposal.votes_for.checked_add(proposal.votes_against).unwrap(); // WHY: checked_add prevents overflow when summing vote tallies.
        require!( // WHY: The quorum ensures a minimum level of participation before any action can be taken.
            total_votes >= proposal.quorum, // WHY: Without quorum, a small group could pass proposals with negligible participation.
            GovernanceError::QuorumNotMet // WHY: A specific error code tells the client the proposal failed due to low turnout.
        );

        require!( // WHY: The majority must support the proposal for it to execute.
            proposal.votes_for > proposal.votes_against, // WHY: Strict majority prevents ties and ensures clear direction.
            GovernanceError::ProposalRejected // WHY: A specific error code tells the client the proposal lost the vote.
        );

        proposal.executed = true; // WHY: Marking the proposal as executed prevents all future execution attempts.

        Ok(()) // WHY: Ok signals that the proposal passed all checks and its execution effects should be committed.
    }
}

#[derive(Accounts)] // WHY: This macro tells Anchor to generate account validation logic based on the struct fields and attributes.
pub struct InitializeGovernance<'info> { // WHY: A dedicated struct for each instruction keeps validation logic scoped and maintainable.
    #[account(mut)] // WHY: The admin account must be mutable because it pays for the rent of the new config account.
    pub admin: Signer<'info>, // WHY: Signer ensures the admin authorized this transaction with their private key.

    #[account( // WHY: The init attribute tells Anchor to create this account via CPI to the system program.
        init, // WHY: init creates the account if it does not exist; combined with a PDA it ensures idempotent initialization.
        payer = admin, // WHY: The admin pays the rent lamports for the new account.
        space = 8 + 32 + 32 + 8 + 8 + 8, // WHY: 8 bytes for discriminator + 32 for admin + 32 for mint + 8 for quorum + 8 for timelock + 8 for count.
        seeds = [b"config"], // WHY: A fixed seed makes the config address deterministic and easy to reference off-chain.
        bump // WHY: Anchor automatically finds and stores the canonical bump for the PDA.
    )]
    pub config: Account<'info, GovernanceConfig>, // WHY: Account<'info, T> tells Anchor to deserialize this account as a GovernanceConfig.

    pub governance_mint: Account<'info, Mint>, // WHY: Mint is an SPL token type; this ensures the provided account is a valid token mint.

    pub system_program: Program<'info, System>, // WHY: The system program is required for account creation CPI.
}

#[derive(Accounts)] // WHY: This macro generates deserialization and validation for the CreateProposal instruction.
pub struct CreateProposal<'info> { // WHY: A dedicated struct isolates proposal-specific constraints from other instructions.
    #[account(mut)] // WHY: The creator must be mutable because they pay for the new proposal account.
    pub creator: Signer<'info>, // WHY: Signer ensures only the creator can create a proposal in their name.

    #[account(mut)] // WHY: The config must be mutable because the proposal counter is incremented.
    pub config: Account<'info, GovernanceConfig>, // WHY: Account type ensures this address actually holds a GovernanceConfig.

    #[account( // WHY: The init attribute creates the proposal PDA with deterministic addressing.
        init, // WHY: init creates the account; it fails if the account already exists, preventing accidental overwrites.
        payer = creator, // WHY: The creator pays rent, aligning economic incentives against spam proposals.
        space = 8 + 8 + 32 + 4 + MAX_DESCRIPTION_LENGTH + 8 + 8 + 8 + 8 + 1 + 1 + 4 + (32 * MAX_VOTERS), // WHY: Precise space calculation ensures rent exemption without waste.
        seeds = [b"proposal", &config.proposal_count.to_le_bytes()], // WHY: Using the proposal count as a seed guarantees unique addresses for each proposal.
        bump // WHY: Anchor handles the bump calculation automatically.
    )]
    pub proposal: Account<'info, Proposal>, // WHY: This tells Anchor to deserialize the new account as a Proposal struct.

    pub system_program: Program<'info, System>, // WHY: Required for the init CPI that creates the proposal account.
}

#[derive(Accounts)] // WHY: This macro generates validation for the CastVote instruction.
pub struct CastVote<'info> { // WHY: Isolating vote constraints prevents them from bleeding into other instructions.
    #[account(mut)] // WHY: The voter is mutable because they may pay for the voter_record account creation.
    pub voter: Signer<'info>, // WHY: Signer ensures the voter authorized this transaction.

    #[account(mut)] // WHY: The proposal must be mutable because vote tallies are updated.
    pub proposal: Account<'info, Proposal>, // WHY: Account type ensures the address holds a valid Proposal.

    pub config: Account<'info, GovernanceConfig>, // WHY: The config is needed to validate the governance mint address.

    #[account( // WHY: These constraints validate that the voter owns this token account and it holds the correct mint.
        constraint = voter_token_account.owner == voter.key(), // WHY: Only the token owner can use their balance for voting.
        constraint = voter_token_account.mint == config.governance_mint, // WHY: Only the designated governance token counts toward voting power.
    )]
    pub voter_token_account: Account<'info, TokenAccount>, // WHY: TokenAccount is the Anchor type for SPL token accounts.

    #[account( // WHY: init_if_needed creates the record on first vote, saving rent for users who never vote.
        init_if_needed, // WHY: This allows the same instruction to work for both first-time and returning voters.
        payer = voter, // WHY: The voter pays for their own record.
        space = 8 + 32 + 32 + 8 + 1 + 1 + 1, // WHY: 8 discriminator + 32 voter + 32 proposal + 8 weight + 1 direction + 1 voted + 1 bump.
        seeds = [b"vote", proposal.key().as_ref(), voter.key().as_ref()], // WHY: Unique seeds per (proposal, voter) prevent double voting.
        bump // WHY: Anchor handles bump derivation.
    )]
    pub voter_record: Account<'info, VoterRecord>, // WHY: This account stores whether this voter has already voted on this proposal.

    pub system_program: Program<'info, System>, // WHY: Required for init_if_needed CPI.
}

#[derive(Accounts)] // WHY: This macro generates validation for the DelegateVote instruction.
pub struct DelegateVote<'info> { // WHY: Delegation requires its own account context to scope constraints.
    pub delegator: Signer<'info>, // WHY: Only the token holder can delegate their own voting power.

    #[account( // WHY: init creates a new delegation record keyed by the delegator.
        init, // WHY: init ensures a fresh delegation; re-delegation requires explicit revocation logic.
        payer = delegator, // WHY: The delegator pays for their own delegation record.
        space = 8 + 32 + 32 + 1 + 1, // WHY: 8 discriminator + 32 delegator + 32 delegatee + 1 active + 1 bump.
        seeds = [b"delegation", delegator.key().as_ref()], // WHY: Fixed seed per delegator makes lookup deterministic.
        bump // WHY: Anchor handles bump derivation.
    )]
    pub delegation_record: Account<'info, DelegationRecord>, // WHY: This account stores the active delegation.

    pub system_program: Program<'info, System>, // WHY: Required for init CPI.
}

#[derive(Accounts)] // WHY: This macro generates validation for the ExecuteProposal instruction.
pub struct ExecuteProposal<'info> { // WHY: Execution requires a minimal context because most checks are state-based, not account-based.
    #[account(mut)] // WHY: The proposal must be mutable because the executed flag is set.
    pub proposal: Account<'info, Proposal>, // WHY: Account type ensures the target is a valid Proposal.

    pub config: Account<'info, GovernanceConfig>, // WHY: The config provides the timelock delay parameter.
}

#[account] // WHY: This macro marks the struct as an Anchor account, deriving serialization and a discriminator.
pub struct GovernanceConfig { // WHY: A dedicated config account avoids storing global state inside individual proposals.
    pub admin: Pubkey, // WHY: The admin can perform privileged operations like updating parameters.
    pub governance_mint: Pubkey, // WHY: Storing the mint on-chain makes the token contract discoverable without off-chain configuration.
    pub quorum: u64, // WHY: The quorum is the minimum participation threshold for valid proposals.
    pub timelock_delay: i64, // WHY: The delay enforces a cooling-off period between vote end and execution.
    pub proposal_count: u64, // WHY: The counter enables unique, sequential proposal IDs.
}

#[account] // WHY: This macro marks the struct as an Anchor account with automatic serialization.
pub struct Proposal { // WHY: Each proposal is stored in its own PDA for independent lifecycle management.
    pub id: u64, // WHY: A numeric ID is easier for clients to reference than a 32-byte pubkey.
    pub creator: Pubkey, // WHY: Storing the creator enables attribution and filtering.
    pub description: String, // WHY: The description is the human-readable content of the proposal.
    pub quorum: u64, // WHY: Copying quorum at creation time locks the threshold for this proposal.
    pub votes_for: u64, // WHY: The for tally is stored as u64 to match SPL token amounts.
    pub votes_against: u64, // WHY: The against tally is stored as u64 for symmetry.
    pub deadline: i64, // WHY: Unix timestamp is the standard time representation on Solana.
    pub executed: bool, // WHY: A boolean is the most space-efficient guard against double execution.
    pub bump: u8, // WHY: Storing the bump enables efficient PDA re-derivation.
}

#[account] // WHY: This macro marks the struct as an Anchor account.
pub struct VoterRecord { // WHY: A separate record per voter per proposal prevents double voting without unbounded arrays.
    pub voter: Pubkey, // WHY: Storing the voter makes the record self-describing.
    pub proposal: Pubkey, // WHY: Storing the proposal key makes the record self-describing.
    pub weight: u64, // WHY: Storing the weight enables historical analysis and dispute resolution.
    pub vote_for: bool, // WHY: Storing the direction enables vote breakdown UIs.
    pub has_voted: bool, // WHY: The boolean flag is the guard against double voting.
    pub bump: u8, // WHY: Storing the bump enables PDA validation.
}

#[account] // WHY: This macro marks the struct as an Anchor account.
pub struct DelegationRecord { // WHY: A dedicated record per delegator enables lookup without scanning all proposals.
    pub delegator: Pubkey, // WHY: Storing the delegator makes the record self-describing.
    pub delegatee: Pubkey, // WHY: Storing the delegatee defines who can vote on behalf of the delegator.
    pub active: bool, // WHY: The active flag allows soft deletion via revocation without closing the account.
    pub bump: u8, // WHY: Storing the bump enables PDA validation.
}

#[error_code] // WHY: This macro generates a custom error enum with automatic message propagation to clients.
pub enum GovernanceError { // WHY: Typed errors are safer than magic numbers and provide better debugging information.
    #[msg("Description exceeds maximum length")] // WHY: Human-readable messages help developers debug without reading source code.
    DescriptionTooLong, // WHY: A specific variant for each error condition enables precise handling.
    #[msg("Deadline must be in the future")]
    InvalidDeadline, // WHY: A specific variant distinguishes deadline errors from other validation failures.
    #[msg("Voting period has ended")]
    VotingPeriodEnded, // WHY: A specific variant tells the client voting is closed.
    #[msg("Already voted on this proposal")]
    AlreadyVoted, // WHY: A specific variant prevents duplicate vote attempts.
    #[msg("Invalid token account")]
    InvalidTokenAccount, // WHY: A specific variant helps debug account configuration issues.
    #[msg("No voting power")]
    NoVotingPower, // WHY: A specific variant tells the user they need governance tokens.
    #[msg("Cannot delegate to self")]
    SelfDelegation, // WHY: A specific variant catches a common input mistake.
    #[msg("Proposal already executed")]
    AlreadyExecuted, // WHY: A specific variant prevents duplicate execution.
    #[msg("Voting period is still active")]
    VotingPeriodActive, // WHY: A specific variant tells the client to wait.
    #[msg("Timelock is still active")]
    TimelockActive, // WHY: A specific variant tells the client exactly why execution is blocked.
    #[msg("Quorum not met")]
    QuorumNotMet, // WHY: A specific variant distinguishes low turnout from other failures.
    #[msg("Proposal was rejected")]
    ProposalRejected, // WHY: A specific variant indicates the majority voted against it.
}
