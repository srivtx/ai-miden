use solana_program::{ // WHY: We import the Solana SDK as a single block so all on-chain runtime types are available in this module.
    account_info::{next_account_info, AccountInfo}, // WHY: next_account_info and AccountInfo let us iterate over and inspect the accounts passed by the transaction.
    entrypoint, // WHY: The entrypoint macro is required to register the program's sole external entry point for the BPF loader.
    entrypoint::ProgramResult, // WHY: ProgramResult is the standard Solana return type that signals success or an on-chain error.
    msg, // WHY: msg lets us emit log messages that explorers and developers can read for debugging and audit trails.
    program::{invoke, invoke_signed}, // WHY: invoke and invoke_signed let us execute Cross-Program Invocations to the System and SPL Token programs.
    program_error::ProgramError, // WHY: ProgramError is the canonical error type returned to the Solana runtime when an instruction fails.
    pubkey::Pubkey, // WHY: Pubkey is the fundamental address type used to identify accounts, programs, and PDAs on Solana.
    sysvar::{clock::Clock, Sysvar}, // WHY: Clock and Sysvar let us read on-chain time so time-based checks are objective and trustless.
    system_instruction, // WHY: system_instruction provides constructors for System Program instructions like create_account and transfer.
    program_pack::Pack, // WHY: Pack is required in scope so we can call TokenAccount::unpack to parse SPL token account data.
}; // WHY: End of Solana SDK imports.

use spl_token::state::Account as TokenAccount; // WHY: We alias spl_token::state::Account to TokenAccount so we can parse SPL token balances during claims.

use borsh::{BorshDeserialize, BorshSerialize}; // WHY: Borsh provides compact binary serialization for our custom structs because Solana account data is a raw byte slice.

use thiserror::Error; // WHY: thiserror lets us derive descriptive error variants with minimal boilerplate so debugging on-chain failures is easier.

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // WHY: Deriving Borsh traits lets Project be packed into account data; Debug and Clone aid testing.
pub struct Project { // WHY: A dedicated struct groups all project metadata into one on-chain account so sale parameters live at a single deterministic address.
    pub admin: Pubkey, // WHY: Storing the admin pubkey inside the account lets us verify the caller later without relying solely on PDAs.
    pub token_mint: Pubkey, // WHY: We record the SPL token mint so the program knows exactly which token to distribute to participants.
    pub hard_cap: u64, // WHY: hard_cap is the maximum SOL the project may raise; it protects buyers from infinite dilution.
    pub soft_cap: u64, // WHY: soft_cap is the minimum raise required for success; below this, refunds must be available.
    pub sale_end: i64, // WHY: sale_end is a Unix timestamp so the program can objectively determine when the sale window closes using the Clock sysvar.
    pub total_raised: u64, // WHY: total_raised tracks cumulative SOL contributions so we can enforce caps and evaluate soft-cap success.
    pub is_finalized: bool, // WHY: is_finalized prevents double-claims or double-refunds once the project enters its terminal state.
} // WHY: End of Project struct definition.

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // WHY: Borsh traits let Tier be serialized into account data; Debug and Clone aid local simulation.
pub struct Tier { // WHY: Tiers separate participants into groups with different prices and allocations, enabling structured fundraising rounds.
    pub project: Pubkey, // WHY: Storing the parent project pubkey links every tier back to exactly one project, preventing cross-project confusion.
    pub tier_id: u8, // WHY: tier_id is a small integer so multiple tiers can be derived deterministically from the same project via PDA seeds.
    pub price: u64, // WHY: price defines how many lamports one token unit costs, establishing the exchange rate for this tier.
    pub allocation: u64, // WHY: allocation caps the total token supply available in this tier so no single round can drain the project reserve.
    pub sold: u64, // WHY: sold tracks how many tokens have already been purchased in this tier, enabling real-time availability checks.
    pub whitelist: Vec<Pubkey>, // WHY: whitelist stores allowed participant pubkeys because some tiers must be restricted to private investors.
} // WHY: End of Tier struct definition.

#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)] // WHY: Borsh serialization is required to store participant records on-chain; Debug and Clone help validation scripts.
pub struct Participant { // WHY: Each participant gets their own account so individual contribution and claim status persist immutably on-chain.
    pub user: Pubkey, // WHY: Storing the user pubkey lets us verify that only the rightful owner can claim tokens or request a refund.
    pub project: Pubkey, // WHY: Linking to the project PDA prevents a participant record from being reused across different sales.
    pub tier_id: u8, // WHY: tier_id remembers which pricing tier the user entered, because different tiers have different token allocations.
    pub contributed: u64, // WHY: contributed records lamports sent by the user so we can compute token entitlement or refund amount exactly.
    pub claimed: bool, // WHY: claimed is a boolean gate ensuring tokens are distributed only once per participant.
} // WHY: End of Participant struct definition.

#[derive(BorshSerialize, BorshDeserialize, Debug)] // WHY: The instruction enum must deserialize from the instruction_data payload so the entrypoint can dispatch correctly.
pub enum LaunchpadInstruction { // WHY: An enum captures all possible program operations in one type, which is the standard BPF entrypoint pattern.
    RegisterProject { // WHY: RegisterProject creates the initial sale configuration so there is a canonical on-chain record before any money moves.
        token_mint: Pubkey, // WHY: The token mint parameter tells the project which SPL token it will later distribute to backers.
        hard_cap: u64, // WHY: hard_cap is supplied at creation so the fundraising ceiling is immutable and trustworthy from the start.
        soft_cap: u64, // WHY: soft_cap is set at registration so participants can inspect the minimum success threshold on-chain.
        sale_end: i64, // WHY: sale_end is provided upfront so the program has an objective deadline without relying on off-chain clocks.
    }, // WHY: End of RegisterProject payload.
    SetTier { // WHY: SetTier configures a specific pricing round because a single project often needs multiple investor tiers.
        tier_id: u8, // WHY: tier_id lets the caller reference which round is being configured without ambiguity.
        price: u64, // WHY: price is supplied per-tier because different rounds offer different discounts to different investor classes.
        allocation: u64, // WHY: allocation limits how many tokens this tier can sell, preventing oversubscription.
        whitelist: Vec<Pubkey>, // WHY: whitelist is passed at setup so private rounds can be restricted before the sale opens.
    }, // WHY: End of SetTier payload.
    Participate { // WHY: Participate is the buy instruction so users can send SOL and record their commitment on-chain.
        tier_id: u8, // WHY: tier_id tells the program which pricing rules to apply for this purchase.
        amount: u64, // WHY: amount is the quantity of token units the buyer wants, letting them specify exact purchase size.
    }, // WHY: End of Participate payload.
    ClaimTokens, // WHY: ClaimTokens lets buyers receive their SPL tokens after the sale succeeds, separating purchase from delivery.
    Refund, // WHY: Refund exists so participants can recover SOL if the sale fails to hit its soft cap, protecting their capital.
    AdminWithdraw, // WHY: AdminWithdraw allows the project owner to collect raised SOL only after a successful sale, enforcing trust.
} // WHY: End of LaunchpadInstruction enum.

#[derive(Error, Debug, Copy, Clone)] // WHY: Custom errors give descriptive failure reasons instead of opaque numeric ProgramError codes.
pub enum LaunchpadError { // WHY: Grouping errors under one enum makes the codebase self-documenting and easier to audit.
    #[error("Unauthorized")] // WHY: Unauthorized clearly signals when a signer does not match the expected admin or participant.
    Unauthorized, // WHY: This variant is returned when an account signer lacks permission for the requested operation.
    #[error("Sale not ended")] // WHY: SaleNotEnded prevents premature claims or refunds before the deadline has objectively passed.
    SaleNotEnded, // WHY: Used when the current Clock timestamp is still earlier than the registered sale_end.
    #[error("Sale ended")] // WHY: SaleEnded blocks new participation after the deadline so no late money enters the raise.
    SaleEnded, // WHY: Used when a Participate instruction arrives after sale_end.
    #[error("Soft cap not met")] // WHY: SoftCapNotMet stops admin withdrawal when the raise failed to reach the minimum threshold.
    SoftCapNotMet, // WHY: Used during AdminWithdraw if total_raised is below soft_cap.
    #[error("Soft cap met")] // WHY: SoftCapMet stops refunds when the sale succeeded, because refunds are only for failed raises.
    SoftCapMet, // WHY: Used during Refund if total_raised is at or above soft_cap.
    #[error("Tier not found")] // WHY: TierNotFound protects against typos or malicious tier_ids that do not correspond to existing accounts.
    TierNotFound, // WHY: Returned when the derived tier PDA does not match the provided account.
    #[error("Allocation exceeded")] // WHY: AllocationExceeded prevents selling more tokens than were allocated to a specific tier.
    AllocationExceeded, // WHY: Returned when a purchase would push tier.sold past tier.allocation.
    #[error("Not whitelisted")] // WHY: NotWhitelisted enforces private-round access control for tiers that have a non-empty whitelist.
    NotWhitelisted, // WHY: Returned when a buyer's pubkey is missing from the tier whitelist.
    #[error("Already claimed")] // WHY: AlreadyClaimed prevents double-spending of the participant's token entitlement.
    AlreadyClaimed, // WHY: Returned when ClaimTokens is invoked on a Participant with claimed == true.
    #[error("Project not finalized")] // WHY: ProjectNotFinalized ensures claims only happen after the program explicitly marks the sale as done.
    ProjectNotFinalized, // WHY: Returned when ClaimTokens runs before the project enters its finalized state.
} // WHY: End of LaunchpadError enum.

impl From<LaunchpadError> for ProgramError { // WHY: Implementing From lets our custom errors convert automatically into ProgramError for Solana runtime compatibility.
    fn from(e: LaunchpadError) -> Self { // WHY: This function signature is required by the From trait so the compiler knows how to perform the conversion.
        ProgramError::Custom(e as u32) // WHY: Solana expects custom errors as u32 codes inside ProgramError::Custom so explorers can decode them.
    } // WHY: End of From conversion function.
} // WHY: End of From impl.

entrypoint!(process_instruction); // WHY: The entrypoint macro registers process_instruction as the BPF program's sole external entry point.

pub fn process_instruction( // WHY: This function is the router that receives every transaction; it must be public so the Solana runtime can call it.
    program_id: &Pubkey, // WHY: program_id is the current program's address so we can verify that derived accounts belong to this program.
    accounts: &[AccountInfo], // WHY: accounts is the ordered list of accounts passed by the client, which we must manually validate.
    instruction_data: &[u8], // WHY: instruction_data carries the serialized LaunchpadInstruction so we know which operation to execute.
) -> ProgramResult { // WHY: ProgramResult is the standard Solana return type that signals success or an on-chain error.
    let instruction = LaunchpadInstruction::try_from_slice(instruction_data) // WHY: We deserialize the payload first because all downstream logic depends on which instruction variant is requested.
        .map_err(|_| ProgramError::InvalidInstructionData)?; // WHY: If deserialization fails we return InvalidInstructionData so malformed transactions are rejected immediately.

    match instruction { // WHY: A match expression dispatches to the correct handler based on the deserialized enum variant.
        LaunchpadInstruction::RegisterProject { token_mint, hard_cap, soft_cap, sale_end } => { // WHY: We destructure the payload fields so they are available as local variables in the handler.
            process_register_project(program_id, accounts, token_mint, hard_cap, soft_cap, sale_end) // WHY: We forward arguments to the dedicated handler to keep the entrypoint readable and modular.
        } // WHY: End of RegisterProject arm.
        LaunchpadInstruction::SetTier { tier_id, price, allocation, whitelist } => { // WHY: Destructuring SetTier fields makes them directly usable in the handler without re-parsing.
            process_set_tier(program_id, accounts, tier_id, price, allocation, whitelist) // WHY: Delegating to a named function keeps the match block short and preserves single-responsibility.
        } // WHY: End of SetTier arm.
        LaunchpadInstruction::Participate { tier_id, amount } => { // WHY: We extract tier_id and amount so the participate handler knows what to buy and how much.
            process_participate(program_id, accounts, tier_id, amount) // WHY: Isolating purchase logic prevents accidental mixing with claim or refund code paths.
        } // WHY: End of Participate arm.
        LaunchpadInstruction::ClaimTokens => { // WHY: ClaimTokens has no payload because all necessary state is already stored in on-chain accounts.
            process_claim_tokens(program_id, accounts) // WHY: We route to the claim handler so the entrypoint stays a pure dispatcher.
        } // WHY: End of ClaimTokens arm.
        LaunchpadInstruction::Refund => { // WHY: Refund has no payload because the participant account already records how much SOL to return.
            process_refund(program_id, accounts) // WHY: Routing to a dedicated refund handler keeps the code maintainable and auditable.
        } // WHY: End of Refund arm.
        LaunchpadInstruction::AdminWithdraw => { // WHY: AdminWithdraw has no payload because the project account already knows the total_raised amount.
            process_admin_withdraw(program_id, accounts) // WHY: Delegating to a named handler prevents mixing withdrawal logic with participant-facing operations.
        } // WHY: End of AdminWithdraw arm.
    } // WHY: End of match on instruction.
} // WHY: End of process_instruction entrypoint.

fn process_register_project( // WHY: This handler isolates project creation logic so the entrypoint does not become a monolithic block.
    program_id: &Pubkey, // WHY: We need program_id to verify that the project PDA is derived from this program.
    accounts: &[AccountInfo], // WHY: The handler receives the same account slice so it can validate and mutate the project account.
    token_mint: Pubkey, // WHY: token_mint is taken as a parameter so the project permanently records which SPL token it will distribute.
    hard_cap: u64, // WHY: hard_cap is passed explicitly so the project account stores an immutable fundraising ceiling.
    soft_cap: u64, // WHY: soft_cap is passed explicitly so the on-chain record reflects the minimum viable raise from day one.
    sale_end: i64, // WHY: sale_end is passed explicitly so the deadline is transparent and verifiable by all participants.
) -> ProgramResult { // WHY: ProgramResult lets us return custom errors if any validation check fails during registration.
    let account_info_iter = &mut accounts.iter(); // WHY: We create a mutable iterator because Solana handlers consume account_info items in a strict order.
    let admin_account = next_account_info(account_info_iter)?; // WHY: The first account must be the admin signer so we can enforce permission checks.
    let project_account = next_account_info(account_info_iter)?; // WHY: The second account is the uninitialized project PDA that will hold the serialized Project struct.
    let system_program = next_account_info(account_info_iter)?; // WHY: We need the System Program to create and allocate lamports for the new project account.

    if !admin_account.is_signer { // WHY: We verify the admin signed because only the intended creator should initialize a project and control its funds.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Returning early with Unauthorized prevents unauthorized project creation.
    } // WHY: End of signer check.

    let clock = Clock::get()?; // WHY: Fetching the Clock lets us validate that the sale_end is in the future.
    if sale_end <= clock.unix_timestamp { // WHY: A sale_end in the past would make the sale immediately expired, which is a configuration error.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects misconfigured deadlines.
    } // WHY: End of future deadline check.

    if hard_cap == 0 { // WHY: A hard cap of zero means no funds can be raised, making the project useless.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects non-viable fundraising configurations.
    } // WHY: End of hard cap validation.

    if soft_cap > hard_cap { // WHY: soft_cap must not exceed hard_cap because the minimum cannot be greater than the maximum.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects logically impossible cap configurations.
    } // WHY: End of cap consistency check.

    let (project_pda, project_bump) = Pubkey::find_program_address( // WHY: We derive the project PDA so its address is deterministic and not controlled by any private key.
        &[b"project", admin_account.key.as_ref()], // WHY: The seed combines a static string and the admin pubkey so every admin gets exactly one project.
        program_id, // WHY: We scope the derivation to this program so other programs cannot squat the same PDA.
    ); // WHY: End of PDA derivation.

    if project_pda != *project_account.key { // WHY: We verify the client passed the correct PDA so malicious callers cannot substitute a fake account.
        return Err(ProgramError::InvalidSeeds); // WHY: InvalidSeeds is the standard Solana error for PDA mismatches.
    } // WHY: End of PDA verification.

    let project = Project { // WHY: We construct the Project struct in memory before writing it to the account so all fields are validated first.
        admin: *admin_account.key, // WHY: We copy the admin pubkey so the project permanently remembers its owner.
        token_mint, // WHY: We store the provided token_mint so later instructions know which SPL token to transfer.
        hard_cap, // WHY: We store hard_cap so no future instruction can raise more than this ceiling.
        soft_cap, // WHY: We store soft_cap so refund and withdraw logic have an objective success threshold.
        sale_end, // WHY: We store sale_end so time-based checks do not depend on off-chain oracles.
        total_raised: 0, // WHY: total_raised starts at zero because no contributions exist at registration time.
        is_finalized: false, // WHY: is_finalized starts false because the sale has not yet occurred.
    }; // WHY: End of Project construction.

    let project_size = project.try_to_vec()?.len(); // WHY: We compute the serialized size so we allocate exactly enough space and avoid wasting rent.
    let rent = solana_program::rent::Rent::get()?; // WHY: We fetch the Rent sysvar to know the minimum lamports needed for rent exemption.
    let required_lamports = rent.minimum_balance(project_size); // WHY: minimum_balance computes the exact rent-exempt amount so the account persists indefinitely.

    invoke_signed( // WHY: invoke_signed is required when creating a PDA because the program must sign on behalf of the PDA, which has no private key.
        &system_instruction::create_account( // WHY: create_account allocates space and assigns ownership to our program in a single atomic System Program call.
            admin_account.key, // WHY: The admin pays for account creation because they initiated the transaction and should bear the cost.
            project_account.key, // WHY: The project PDA is the account being created; it will hold the serialized Project data.
            required_lamports, // WHY: We fund the account with exactly the rent-exempt minimum so it stays alive without ongoing rent payments.
            project_size as u64, // WHY: The size parameter tells the System Program how many bytes to allocate for our serialized struct.
            program_id, // WHY: Assigning ownership to our program ensures only this program can mutate the project account data.
        ), // WHY: End of create_account instruction.
        &[admin_account.clone(), project_account.clone(), system_program.clone()], // WHY: We clone references because invoke_signed needs owned AccountInfo references for its internal checks.
        &[&[b"project", admin_account.key.as_ref(), &[project_bump]]], // WHY: The signer seeds prove the program derived this PDA correctly, authorizing the creation.
    )?; // WHY: The ? propagates any System Program failure immediately so we do not continue with a half-created account.

    project.serialize(&mut &mut project_account.data.borrow_mut()[..])?; // WHY: We serialize the Project struct into the newly allocated account data so it persists on-chain.

    msg!("Project registered: {}", project_pda); // WHY: Logging the PDA helps explorers and developers confirm that registration succeeded at the expected address.
    Ok(()) // WHY: Returning Ok signals to the Solana runtime that the instruction executed successfully.
} // WHY: End of process_register_project.

fn process_set_tier( // WHY: This handler isolates tier configuration so entrypoint dispatch remains clean.
    program_id: &Pubkey, // WHY: program_id is needed to derive the tier PDA scoped to this program.
    accounts: &[AccountInfo], // WHY: The handler needs the admin signer, project account, and tier account to validate and write state.
    tier_id: u8, // WHY: tier_id identifies which round is being configured so multiple tiers can exist under one project.
    price: u64, // WHY: price sets the cost per token unit for this specific tier.
    allocation: u64, // WHY: allocation caps the number of tokens available in this tier.
    whitelist: Vec<Pubkey>, // WHY: whitelist restricts participation to specific addresses for private or seed rounds.
) -> ProgramResult { // WHY: ProgramResult allows us to return validation errors before writing any state.
    let account_info_iter = &mut accounts.iter(); // WHY: A mutable iterator lets us pull accounts in the expected client-supplied order.
    let admin_account = next_account_info(account_info_iter)?; // WHY: The first account must be the admin signer so unauthorized tier changes are rejected.
    let project_account = next_account_info(account_info_iter)?; // WHY: The second account is the project PDA so we can verify admin ownership.
    let tier_account = next_account_info(account_info_iter)?; // WHY: The third account is the tier PDA that will store the new Tier struct.
    let system_program = next_account_info(account_info_iter)?; // WHY: The System Program is required to create the tier account if it does not yet exist.

    if !admin_account.is_signer { // WHY: Only the admin should be able to modify project tiers because they control the fundraising terms.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Early return prevents any state changes when the signer is invalid.
    } // WHY: End of signer check.

    let project_data = Project::try_from_slice(&project_account.data.borrow())?; // WHY: We deserialize the project account to confirm the admin matches and the sale is still open.
    if project_data.admin != *admin_account.key { // WHY: We verify the signer is the stored admin so no one else can hijack the project's tiers.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting here protects project integrity.
    } // WHY: End of admin verification.

    if price == 0 { // WHY: A price of zero would make tokens free and cause division by zero during claims.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects nonsensical pricing.
    } // WHY: End of price validation.

    if allocation == 0 { // WHY: A tier with zero allocation cannot sell any tokens, making it pointless.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects unusable tier configurations.
    } // WHY: End of allocation validation.

    let (tier_pda, tier_bump) = Pubkey::find_program_address( // WHY: Deriving the tier PDA makes its address deterministic and linkable to the project and tier_id.
        &[b"tier", project_account.key.as_ref(), &[tier_id]], // WHY: These seeds tie the tier uniquely to one project and one tier index.
        program_id, // WHY: Scoping to this program prevents address collisions.
    ); // WHY: End of PDA derivation.

    if tier_pda != *tier_account.key { // WHY: The client must pass the correct tier PDA; otherwise we could write to an unrelated account.
        return Err(ProgramError::InvalidSeeds); // WHY: InvalidSeeds is the precise error for a PDA mismatch.
    } // WHY: End of PDA verification.

    let tier = Tier { // WHY: We build the Tier struct in memory so all fields are present before serialization.
        project: *project_account.key, // WHY: Storing the project pubkey links this tier back to its parent project immutably.
        tier_id, // WHY: We store tier_id inside the account so explorers can read it without re-deriving seeds.
        price, // WHY: Storing price on-chain makes the exchange rate transparent and immutable for this tier.
        allocation, // WHY: Storing allocation on-chain lets the program enforce caps during the Participate instruction.
        sold: 0, // WHY: sold starts at zero because no purchases have occurred yet.
        whitelist, // WHY: Storing the whitelist on-chain enforces access control without relying on off-chain databases.
    }; // WHY: End of Tier construction.

    let tier_size = tier.try_to_vec()?.len(); // WHY: We compute serialized size to allocate exact rent-exempt space.
    let rent = solana_program::rent::Rent::get()?; // WHY: We fetch Rent to know the minimum lamports for rent exemption.
    let required_lamports = rent.minimum_balance(tier_size); // WHY: minimum_balance tells us the exact lamports needed for the account to be rent-exempt.

    invoke_signed( // WHY: invoke_signed lets the program authorize creation of the tier PDA, which has no private key.
        &system_instruction::create_account( // WHY: We use create_account to allocate space and assign ownership atomically.
            admin_account.key, // WHY: The admin pays for the tier account because they are configuring their own project.
            tier_account.key, // WHY: The tier PDA receives the allocation and will store the serialized Tier data.
            required_lamports, // WHY: We fund it with exactly the rent-exempt minimum.
            tier_size as u64, // WHY: We allocate precisely enough bytes for the serialized Tier struct.
            program_id, // WHY: Assigning ownership to this program ensures only our code can mutate the tier data.
        ), // WHY: End of create_account instruction.
        &[admin_account.clone(), tier_account.clone(), system_program.clone()], // WHY: Cloning references satisfies the invoke signature.
        &[&[b"tier", project_account.key.as_ref(), &[tier_id], &[tier_bump]]], // WHY: The signer seeds authorize the program to create this specific PDA.
    )?; // WHY: Propagating errors prevents partially created tier accounts.

    tier.serialize(&mut &mut tier_account.data.borrow_mut()[..])?; // WHY: Writing the serialized struct to the account makes the tier configuration durable on-chain.

    msg!("Tier {} set for project {}", tier_id, project_account.key); // WHY: Logging aids debugging and gives users confirmation of the tier creation.
    Ok(()) // WHY: Ok signals successful completion of the tier setup.
} // WHY: End of process_set_tier.

fn process_participate( // WHY: This handler isolates the purchase logic so the entrypoint remains a simple router.
    program_id: &Pubkey, // WHY: program_id is required to verify participant PDA derivation belongs to this program.
    accounts: &[AccountInfo], // WHY: The handler needs buyer, project, tier, participant accounts, and SPL token accounts.
    tier_id: u8, // WHY: tier_id determines which pricing and allocation rules apply to this purchase.
    amount: u64, // WHY: amount is the number of token units the buyer wants to acquire.
) -> ProgramResult { // WHY: ProgramResult lets us enforce business rules like caps, whitelists, and deadlines.
    let account_info_iter = &mut accounts.iter(); // WHY: We iterate mutably because next_account_info consumes items sequentially.
    let buyer_account = next_account_info(account_info_iter)?; // WHY: The buyer must be the first account so we can verify their signature and whitelist status.
    let project_account = next_account_info(account_info_iter)?; // WHY: The project account provides hard_cap, soft_cap, and sale_end for validation.
    let tier_account = next_account_info(account_info_iter)?; // WHY: The tier account provides price, allocation, sold, and whitelist for this round.
    let participant_account = next_account_info(account_info_iter)?; // WHY: The participant PDA will record this user's contribution and claim status.
    let system_program = next_account_info(account_info_iter)?; // WHY: The System Program is needed to create the participant account if it is the first purchase.

    if !buyer_account.is_signer { // WHY: Only the buyer can authorize spending their lamports, so we require their signature.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting unsigned purchases prevents theft of user funds.
    } // WHY: End of signer check.

    if amount == 0 { // WHY: A zero purchase would waste compute and create a useless participant record.
        return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects no-op purchases.
    } // WHY: End of amount check.

    let mut project = Project::try_from_slice(&project_account.data.borrow())?; // WHY: Deserializing the project lets us enforce time and cap constraints.
    let clock = Clock::get()?; // WHY: We fetch the Clock sysvar to get the current on-chain Unix timestamp.
    if clock.unix_timestamp > project.sale_end { // WHY: Comparing the current time to sale_end objectively closes the fundraising window.
        return Err(LaunchpadError::SaleEnded.into()); // WHY: Returning SaleEnded prevents any new money from entering after the deadline.
    } // WHY: End of sale deadline check.

    if project.total_raised >= project.hard_cap { // WHY: Checking total_raised against hard_cap prevents any contribution once the ceiling is reached.
        return Err(LaunchpadError::AllocationExceeded.into()); // WHY: AllocationExceeded is the appropriate error because the project itself is capped.
    } // WHY: End of hard cap check.

    let mut tier = Tier::try_from_slice(&tier_account.data.borrow())?; // WHY: Deserializing the tier lets us enforce tier-specific price and allocation rules.
    if tier.project != *project_account.key || tier.tier_id != tier_id { // WHY: We verify the tier belongs to this project and matches the requested tier_id to prevent mismatched accounts.
        return Err(LaunchpadError::TierNotFound.into()); // WHY: TierNotFound is the precise error for an invalid tier reference.
    } // WHY: End of tier verification.

    if !tier.whitelist.is_empty() && !tier.whitelist.contains(buyer_account.key) { // WHY: If a whitelist exists, the buyer must be in it; empty whitelist means public access.
        return Err(LaunchpadError::NotWhitelisted.into()); // WHY: NotWhitelisted enforces private-round access control.
    } // WHY: End of whitelist check.

    let cost = tier.price.checked_mul(amount).ok_or(ProgramError::Overflow)?; // WHY: We use checked_mul to prevent u64 overflow when calculating total lamport cost.
    if tier.sold.checked_add(amount).ok_or(ProgramError::Overflow)? > tier.allocation { // WHY: checked_add prevents overflow and the comparison enforces the tier allocation cap.
        return Err(LaunchpadError::AllocationExceeded.into()); // WHY: Rejecting here prevents overselling this specific tier.
    } // WHY: End of tier allocation check.

    let (participant_pda, participant_bump) = Pubkey::find_program_address( // WHY: Deriving the participant PDA makes it deterministic per user and project.
        &[b"participant", project_account.key.as_ref(), buyer_account.key.as_ref()], // WHY: These seeds tie the participant account to exactly one buyer and one project.
        program_id, // WHY: Scoping to this program prevents collisions.
    ); // WHY: End of PDA derivation.

    if participant_pda != *participant_account.key { // WHY: The client must pass the correct participant PDA to prevent writing to the wrong account.
        return Err(ProgramError::InvalidSeeds); // WHY: InvalidSeeds signals a derivation mismatch.
    } // WHY: End of PDA verification.

    let mut participant: Participant; // WHY: We declare participant here so it is in scope for both the creation and update branches.
    if participant_account.data_is_empty() { // WHY: If the account is empty, this is the user's first purchase and we must create and fund the account.
        participant = Participant { // WHY: We initialize a new Participant struct for first-time buyers.
            user: *buyer_account.key, // WHY: We store the buyer pubkey so future claims and refunds know the rightful owner.
            project: *project_account.key, // WHY: We link to the project so the record cannot be reused across sales.
            tier_id, // WHY: We record the tier so the claim handler knows which price rules applied.
            contributed: cost, // WHY: We store the lamport cost so refunds can return the exact amount later.
            claimed: false, // WHY: claimed starts false because the buyer has not yet received any tokens.
        }; // WHY: End of new Participant construction.

        let participant_size = participant.try_to_vec()?.len(); // WHY: We compute the serialized size to allocate exact space.
        let rent = solana_program::rent::Rent::get()?; // WHY: We fetch Rent to know the minimum lamports for rent exemption.
        let required_lamports = rent.minimum_balance(participant_size); // WHY: minimum_balance gives the exact rent-exempt amount.

        invoke_signed( // WHY: invoke_signed authorizes the program to create the participant PDA on behalf of the buyer.
            &system_instruction::create_account( // WHY: create_account atomically allocates space and assigns ownership.
                buyer_account.key, // WHY: The buyer pays for their own participant account because it stores their personal state.
                participant_account.key, // WHY: The participant PDA is the account being initialized.
                required_lamports, // WHY: We fund it with the rent-exempt minimum.
                participant_size as u64, // WHY: We allocate exactly enough bytes for the serialized Participant.
                program_id, // WHY: Assigning ownership to our program ensures only our code can mutate this record.
            ), // WHY: End of create_account instruction.
            &[buyer_account.clone(), participant_account.clone(), system_program.clone()], // WHY: Cloning references satisfies the invoke signature.
            &[&[b"participant", project_account.key.as_ref(), buyer_account.key.as_ref(), &[participant_bump]]], // WHY: The signer seeds prove the program owns this PDA.
        )?; // WHY: Propagating errors prevents half-created participant accounts.
    } else { // WHY: If the account already exists, we update the existing contribution instead of creating a duplicate.
        participant = Participant::try_from_slice(&participant_account.data.borrow())?; // WHY: Deserializing the existing record lets us add to the prior contributed amount.
        if participant.tier_id != tier_id { // WHY: Changing tiers mid-sale is disallowed to keep accounting simple and prevent confusion.
            return Err(ProgramError::InvalidInstructionData); // WHY: InvalidInstructionData rejects multi-tier purchases from the same account.
        } // WHY: End of tier change check.
        participant.contributed = participant.contributed.checked_add(cost).ok_or(ProgramError::Overflow)?; // WHY: checked_add prevents u64 overflow when summing multiple purchases.
    } // WHY: End of participant creation vs update branch.

    participant.serialize(&mut &mut participant_account.data.borrow_mut()[..])?; // WHY: Writing the updated Participant struct to the account persists the new contribution total.

    tier.sold = tier.sold.checked_add(amount).ok_or(ProgramError::Overflow)?; // WHY: We increment tier.sold so subsequent buyers see reduced availability.
    tier.serialize(&mut &mut tier_account.data.borrow_mut()[..])?; // WHY: Persisting the updated tier sold count enforces the allocation cap for future purchases.

    project.total_raised = project.total_raised.checked_add(cost).ok_or(ProgramError::Overflow)?; // WHY: We increment total_raised so the project tracks cumulative SOL and can evaluate soft cap success.
    project.serialize(&mut &mut project_account.data.borrow_mut()[..])?; // WHY: Persisting total_raised makes the value visible to all other instructions and off-chain clients.

    invoke( // WHY: We use a standard invoke (not signed) because the buyer themselves is transferring their own lamports.
        &system_instruction::transfer( // WHY: system_instruction::transfer moves native SOL from the buyer to the project account.
            buyer_account.key, // WHY: The lamports come from the buyer's wallet.
            project_account.key, // WHY: The lamports go to the project PDA so the admin can later withdraw the raise.
            cost, // WHY: We transfer exactly the computed cost so buyers are never overcharged.
        ), // WHY: End of transfer instruction.
        &[buyer_account.clone(), project_account.clone()], // WHY: Both accounts must be passed to the System Program so it can debit and credit lamports.
    )?; // WHY: Propagating transfer errors prevents the participant record from being updated if payment fails.

    msg!("Buyer {} participated in tier {} for {} tokens", buyer_account.key, tier_id, amount); // WHY: Logging provides an audit trail for each purchase.
    Ok(()) // WHY: Ok confirms the purchase completed successfully.
} // WHY: End of process_participate.

fn process_claim_tokens( // WHY: This handler isolates token distribution so the entrypoint stays a pure dispatcher.
    program_id: &Pubkey, // WHY: program_id is needed to verify PDAs belong to this program.
    accounts: &[AccountInfo], // WHY: The handler needs the participant, project, tier, token accounts, and SPL token program.
) -> ProgramResult { // WHY: ProgramResult lets us enforce that claims only happen after a successful, finalized sale.
    let account_info_iter = &mut accounts.iter(); // WHY: A mutable iterator consumes accounts in the expected client order.
    let buyer_account = next_account_info(account_info_iter)?; // WHY: The buyer must sign to prove they own the tokens being claimed.
    let participant_account = next_account_info(account_info_iter)?; // WHY: The participant PDA records how much the user contributed and whether they already claimed.
    let project_account = next_account_info(account_info_iter)?; // WHY: The project account tells us if the sale is finalized and which token mint to use.
    let tier_account = next_account_info(account_info_iter)?; // WHY: The tier account lets us verify the participant's tier and calculate token entitlement.
    let project_token_account = next_account_info(account_info_iter)?; // WHY: This is the project's SPL token account that holds the tokens to be distributed.
    let buyer_token_account = next_account_info(account_info_iter)?; // WHY: This is the buyer's SPL token account that will receive the claimed tokens.
    let token_program = next_account_info(account_info_iter)?; // WHY: The SPL Token Program must be invoked to execute the actual token transfer.

    if !buyer_account.is_signer { // WHY: Only the token owner should be able to claim their distribution.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting unsigned claims prevents theft.
    } // WHY: End of signer check.

    let project = Project::try_from_slice(&project_account.data.borrow())?; // WHY: Deserializing the project lets us check finalization and token mint.
    if !project.is_finalized { // WHY: Tokens should only be released after the admin finalizes the successful sale.
        return Err(LaunchpadError::ProjectNotFinalized.into()); // WHY: ProjectNotFinalized prevents premature distribution.
    } // WHY: End of finalization check.

    let mut participant = Participant::try_from_slice(&participant_account.data.borrow())?; // WHY: Deserializing the participant record lets us check prior claims and compute entitlement.
    if participant.user != *buyer_account.key { // WHY: We verify the signer matches the stored user so no one else can claim this allocation.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting mismatched owners protects user funds.
    } // WHY: End of owner verification.

    if participant.claimed { // WHY: Checking claimed prevents double-spending the same allocation.
        return Err(LaunchpadError::AlreadyClaimed.into()); // WHY: AlreadyClaimed stops duplicate claims.
    } // WHY: End of claimed check.

    let clock = Clock::get()?; // WHY: We fetch the Clock sysvar to verify the sale has ended.
    if clock.unix_timestamp < project.sale_end { // WHY: Claims should only be possible after the sale_end timestamp has passed.
        return Err(LaunchpadError::SaleNotEnded.into()); // WHY: SaleNotEnded prevents claims during an active sale.
    } // WHY: End of sale end check.

    let tier = Tier::try_from_slice(&tier_account.data.borrow())?; // WHY: Deserializing the tier lets us use its price to calculate the exact token entitlement.
    if tier.project != *project_account.key || tier.tier_id != participant.tier_id { // WHY: We verify the tier matches the participant's recorded tier_id and project to prevent account substitution.
        return Err(LaunchpadError::TierNotFound.into()); // WHY: TierNotFound rejects mismatched tier accounts.
    } // WHY: End of tier verification.

    participant.claimed = true; // WHY: We mark claimed before the transfer so a retry cannot issue tokens twice.
    participant.serialize(&mut &mut participant_account.data.borrow_mut()[..])?; // WHY: Persisting claimed == true immediately makes the state durable even if the SPL transfer fails later.

    let token_amount = participant.contributed.checked_div(tier.price).unwrap_or(0); // WHY: Dividing contributed lamports by price per token yields the number of token units the buyer is owed.
    if token_amount == 0 { // WHY: If the computed amount is zero, there is nothing to transfer and we return early to save compute.
        return Ok(()); // WHY: Returning Ok is safe because no tokens are owed.
    } // WHY: End of zero-amount check.

    let project_token = TokenAccount::unpack(&project_token_account.data.borrow())?; // WHY: Unpacking the project's SPL token account lets us verify it holds the mint we expect.
    if project_token.mint != project.token_mint { // WHY: We verify the token account's mint matches the project's registered token_mint to prevent distributing wrong tokens.
        return Err(ProgramError::InvalidAccountData); // WHY: InvalidAccountData is the standard error for a mint mismatch.
    } // WHY: End of mint verification.

    let (_project_pda, project_bump) = Pubkey::find_program_address( // WHY: We re-derive the project PDA to obtain the bump seed for signing.
        &[b"project", project.admin.as_ref()], // WHY: These seeds must match the original registration seeds.
        program_id, // WHY: Derivation is scoped to this program.
    ); // WHY: End of PDA derivation.

    invoke_signed( // WHY: invoke_signed is required because the project PDA must sign the SPL token transfer, and PDAs have no private key.
        &spl_token::instruction::transfer( // WHY: spl_token::transfer moves SPL tokens from the project's token account to the buyer's token account.
            token_program.key, // WHY: The SPL Token Program is the program that actually executes the token ledger update.
            project_token_account.key, // WHY: The source account is the project's token holdings.
            buyer_token_account.key, // WHY: The destination account is the buyer's associated token account.
            project_account.key, // WHY: The project PDA is the authority that owns the source tokens.
            &[], // WHY: No additional signers are needed beyond the project PDA authority.
            token_amount, // WHY: We transfer exactly the computed entitlement.
        )?, // WHY: The ? propagates any SPL Token program error immediately.
        &[project_account.clone(), project_token_account.clone(), buyer_token_account.clone(), token_program.clone()], // WHY: All involved accounts must be passed to the SPL Token Program CPI.
        &[&[b"project", project.admin.as_ref(), &[project_bump]]], // WHY: The signer seeds authorize the project PDA to move its own tokens.
    )?; // WHY: Propagating errors ensures we do not continue if the token transfer fails.

    msg!("Buyer {} claimed {} tokens", buyer_account.key, token_amount); // WHY: Logging creates an on-chain audit trail of the distribution.
    Ok(()) // WHY: Ok signals the claim completed successfully.
} // WHY: End of process_claim_tokens.

fn process_refund( // WHY: This handler isolates refund logic so the entrypoint stays a clean dispatcher.
    program_id: &Pubkey, // WHY: program_id is needed to verify participant and project PDAs belong to this program.
    accounts: &[AccountInfo], // WHY: The handler needs buyer, participant, project accounts, and the System Program to return SOL.
) -> ProgramResult { // WHY: ProgramResult lets us enforce that refunds only happen for failed sales after the deadline.
    let account_info_iter = &mut accounts.iter(); // WHY: A mutable iterator lets us consume accounts in the expected client order.
    let buyer_account = next_account_info(account_info_iter)?; // WHY: The buyer must sign to request a refund of their own contribution.
    let participant_account = next_account_info(account_info_iter)?; // WHY: The participant PDA stores the contributed amount that must be returned.
    let project_account = next_account_info(account_info_iter)?; // WHY: The project PDA holds the raised lamports that will be sent back.
    let system_program = next_account_info(account_info_iter)?; // WHY: The System Program is needed for the lamport transfer from project to buyer.

    if !buyer_account.is_signer { // WHY: Only the original contributor can request their money back.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting unsigned refunds prevents unauthorized withdrawals.
    } // WHY: End of signer check.

    let mut project = Project::try_from_slice(&project_account.data.borrow())?; // WHY: Deserializing the project lets us evaluate soft cap and deadline.
    let clock = Clock::get()?; // WHY: We fetch the Clock sysvar to verify the sale period is over.
    if clock.unix_timestamp < project.sale_end { // WHY: Refunds should not be available until the sale has ended, otherwise active participants could withdraw early.
        return Err(LaunchpadError::SaleNotEnded.into()); // WHY: SaleNotEnded prevents premature refunds.
    } // WHY: End of deadline check.

    if project.total_raised >= project.soft_cap { // WHY: If the soft cap was met, the sale succeeded and refunds are not allowed.
        return Err(LaunchpadError::SoftCapMet.into()); // WHY: SoftCapMet prevents successful projects from being drained by refund requests.
    } // WHY: End of soft cap evaluation.

    let mut participant = Participant::try_from_slice(&participant_account.data.borrow())?; // WHY: Deserializing the participant record gives us the contributed amount and claim status.
    if participant.user != *buyer_account.key { // WHY: We verify the signer matches the stored user so refunds cannot be redirected.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting mismatched owners protects funds.
    } // WHY: End of owner verification.

    if participant.claimed { // WHY: If the user already claimed tokens, they are no longer eligible for a refund.
        return Err(LaunchpadError::AlreadyClaimed.into()); // WHY: AlreadyClaimed prevents users from getting both tokens and their money back.
    } // WHY: End of claimed check.

    let refund_amount = participant.contributed; // WHY: The full contributed amount is refunded because the sale failed to meet its minimum threshold.
    participant.contributed = 0; // WHY: Zeroing the contribution prevents double refunds if the instruction is re-invoked.
    participant.serialize(&mut &mut participant_account.data.borrow_mut()[..])?; // WHY: Persisting the zeroed contribution immediately makes the refund idempotent.

    project.total_raised = project.total_raised.checked_sub(refund_amount).ok_or(ProgramError::InsufficientFunds)?; // WHY: Decrementing total_raised keeps the project's accounting accurate after refunds.
    project.serialize(&mut &mut project_account.data.borrow_mut()[..])?; // WHY: Persisting the updated total_raised prevents the admin from withdrawing funds that were already returned.

    let (_project_pda, project_bump) = Pubkey::find_program_address( // WHY: We re-derive the project PDA to get the bump seed for signing the lamport transfer.
        &[b"project", project.admin.as_ref()], // WHY: Seeds must match the original registration derivation.
        program_id, // WHY: Derivation is scoped to this program.
    ); // WHY: End of PDA derivation.

    invoke_signed( // WHY: invoke_signed is required because the project PDA must authorize the debit of its own lamports.
        &system_instruction::transfer( // WHY: We use a System Program transfer to move SOL from the project PDA back to the buyer.
            project_account.key, // WHY: The source is the project PDA which holds the pooled contributions.
            buyer_account.key, // WHY: The destination is the original buyer's wallet.
            refund_amount, // WHY: We transfer exactly the contributed amount so users are made whole.
        ), // WHY: End of transfer instruction.
        &[project_account.clone(), buyer_account.clone(), system_program.clone()], // WHY: Both source and destination accounts must be passed to the System Program.
        &[&[b"project", project.admin.as_ref(), &[project_bump]]], // WHY: The signer seeds authorize the project PDA to spend its lamports.
    )?; // WHY: Propagating errors ensures we do not continue if the SOL transfer fails.

    msg!("Buyer {} refunded {} lamports", buyer_account.key, refund_amount); // WHY: Logging creates an on-chain record of every refund for transparency.
    Ok(()) // WHY: Ok confirms the refund completed successfully.
} // WHY: End of process_refund.

fn process_admin_withdraw( // WHY: This handler isolates admin withdrawal so the entrypoint stays a clean dispatcher.
    program_id: &Pubkey, // WHY: program_id is needed to verify the project PDA belongs to this program.
    accounts: &[AccountInfo], // WHY: The handler needs the admin signer, project account, destination wallet, and System Program.
) -> ProgramResult { // WHY: ProgramResult lets us enforce that withdrawals only happen after a successful sale.
    let account_info_iter = &mut accounts.iter(); // WHY: A mutable iterator consumes accounts in the expected client order.
    let admin_account = next_account_info(account_info_iter)?; // WHY: The admin must sign because only the project owner should access raised funds.
    let project_account = next_account_info(account_info_iter)?; // WHY: The project PDA holds the pooled lamports and the sale configuration.
    let destination_account = next_account_info(account_info_iter)?; // WHY: The destination is the wallet where the admin wants to receive the SOL.
    let system_program = next_account_info(account_info_iter)?; // WHY: The System Program executes the lamport transfer from project to destination.

    if !admin_account.is_signer { // WHY: Only the admin should be able to withdraw; requiring their signature enforces this.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting unsigned withdrawals prevents fund theft.
    } // WHY: End of signer check.

    let mut project = Project::try_from_slice(&project_account.data.borrow())?; // WHY: Deserializing the project lets us verify admin identity and sale success.
    if project.admin != *admin_account.key { // WHY: We verify the signer is the stored admin so no one else can drain the project.
        return Err(LaunchpadError::Unauthorized.into()); // WHY: Rejecting non-admin signers protects the raised capital.
    } // WHY: End of admin verification.

    let clock = Clock::get()?; // WHY: We fetch the Clock sysvar to verify the sale period has concluded.
    if clock.unix_timestamp < project.sale_end { // WHY: Withdrawing before the sale ends would be premature and could strand participants.
        return Err(LaunchpadError::SaleNotEnded.into()); // WHY: SaleNotEnded prevents early withdrawal.
    } // WHY: End of deadline check.

    if project.total_raised < project.soft_cap { // WHY: If the soft cap was not met, the sale failed and participants are entitled to refunds, not the admin.
        return Err(LaunchpadError::SoftCapNotMet.into()); // WHY: SoftCapNotMet stops the admin from taking funds from a failed raise.
    } // WHY: End of soft cap evaluation.

    if project.is_finalized { // WHY: If the project is already finalized, the admin may have already withdrawn or distributed tokens.
        return Err(ProgramError::InvalidAccountData); // WHY: InvalidAccountData prevents double-withdrawal after finalization.
    } // WHY: End of finalization check.

    project.is_finalized = true; // WHY: We mark finalized before the transfer so a retry cannot withdraw twice.
    project.serialize(&mut &mut project_account.data.borrow_mut()[..])?; // WHY: Persisting is_finalized immediately makes the state durable.

    let withdraw_amount = project.total_raised; // WHY: The admin withdraws the entire total_raised because all contributions represent successful backing.
    if withdraw_amount == 0 { // WHY: If nothing was raised, there is nothing to withdraw and we return early.
        return Ok(()); // WHY: Returning Ok is safe when no funds are available.
    } // WHY: End of zero-amount check.

    let (_project_pda, project_bump) = Pubkey::find_program_address( // WHY: We re-derive the project PDA to obtain the bump seed for signing.
        &[b"project", project.admin.as_ref()], // WHY: Seeds must match the original registration derivation.
        program_id, // WHY: Derivation is scoped to this program.
    ); // WHY: End of PDA derivation.

    invoke_signed( // WHY: invoke_signed is required because the project PDA must authorize the debit of its own lamports.
        &system_instruction::transfer( // WHY: System Program transfer moves SOL from the project PDA to the admin's destination wallet.
            project_account.key, // WHY: The source is the project PDA which holds all contributed lamports.
            destination_account.key, // WHY: The destination is the admin's chosen wallet.
            withdraw_amount, // WHY: We transfer exactly the total_raised amount so the admin receives the full raise.
        ), // WHY: End of transfer instruction.
        &[project_account.clone(), destination_account.clone(), system_program.clone()], // WHY: All involved accounts must be passed to the System Program.
        &[&[b"project", project.admin.as_ref(), &[project_bump]]], // WHY: The signer seeds authorize the project PDA to spend its lamports.
    )?; // WHY: Propagating errors prevents state from being considered finalized if the transfer fails.

    msg!("Admin withdrew {} lamports to {}", withdraw_amount, destination_account.key); // WHY: Logging provides transparency for the community and auditors.
    Ok(()) // WHY: Ok confirms the withdrawal and finalization completed successfully.
} // WHY: End of process_admin_withdraw.
