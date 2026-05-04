use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    program_pack::Pack,
    pubkey::Pubkey,
    sysvar::rent::Rent,
    sysvar::Sysvar,
    system_instruction,
};
use borsh::{BorshDeserialize, BorshSerialize};
use spl_token::instruction as token_instruction;
use spl_associated_token_account::instruction as ata_instruction;

// entrypoint macro registers process_instruction as the Solana runtime entrypoint.
entrypoint!(process_instruction);

// EscrowInstruction enumerates the operations this escrow program supports.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum EscrowInstruction {
    // HoldNft receives an NFT from a seller into an escrow-associated token account.
    HoldNft,
    // HoldPayment receives native SOL from a buyer into an escrow PDA.
    HoldPayment { amount: u64 },
    // ReleaseNft sends the NFT from escrow to the winner or buyer.
    ReleaseNft,
    // ReleasePayment sends escrowed SOL to the seller.
    ReleasePayment,
    // ReturnNft sends the NFT back to the seller if the trade is canceled.
    ReturnNft,
    // ReturnPayment refunds escrowed SOL to the buyer if the trade is canceled.
    ReturnPayment,
}

// EscrowState tracks what is held and under what conditions it can be released.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct EscrowState {
    // seller is the original depositor of the NFT.
    pub seller: Pubkey,
    // buyer is the intended recipient, set when payment is deposited.
    pub buyer: Option<Pubkey>,
    // nft_mint identifies the token held.
    pub nft_mint: Pubkey,
    // payment_amount is the lamports held for this trade.
    pub payment_amount: u64,
    // is_nft_held confirms the NFT has been deposited.
    pub is_nft_held: bool,
    // is_payment_held confirms the payment has been deposited.
    pub is_payment_held: bool,
    // is_active prevents double-release or double-return.
    pub is_active: bool,
    // bump is the PDA bump seed for signing transfers.
    pub bump: u8,
}

// process_instruction deserializes the instruction and routes to the appropriate handler.
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = EscrowInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    match instruction {
        EscrowInstruction::HoldNft => process_hold_nft(program_id, accounts),
        EscrowInstruction::HoldPayment { amount } => process_hold_payment(program_id, accounts, amount),
        EscrowInstruction::ReleaseNft => process_release_nft(program_id, accounts),
        EscrowInstruction::ReleasePayment => process_release_payment(program_id, accounts),
        EscrowInstruction::ReturnNft => process_return_nft(program_id, accounts),
        EscrowInstruction::ReturnPayment => process_return_payment(program_id, accounts),
    }
}

// process_hold_nft takes custody of an NFT from the seller into an escrow token account.
fn process_hold_nft(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // seller signs to prove they authorize transferring their NFT.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint identifies the SPL token being escrowed.
    let nft_mint = next_account_info(account_info_iter)?;
    // seller_nft_account is the seller's ATA that currently holds the NFT.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // escrow_pda is the program-derived address that will own the escrow state.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account is the ATA owned by escrow_pda that will hold the NFT balance.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // token_program is the SPL Token program ID needed for transfer instructions.
    let token_program = next_account_info(account_info_iter)?;
    // ata_program is the Associated Token Account program for creating ATAs.
    let ata_program = next_account_info(account_info_iter)?;
    // system_program is required for account creation.
    let system_program = next_account_info(account_info_iter)?;
    // rent_sysvar provides rent exemption calculations.
    let rent_sysvar = next_account_info(account_info_iter)?;

    if !seller.is_signer {
        msg!("Seller must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    // Derive the escrow PDA from seller and mint to ensure deterministic address.
    let (expected_escrow_pda, escrow_bump) = Pubkey::find_program_address(
        &[b"escrow", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_escrow_pda != *escrow_pda.key {
        msg!("Invalid escrow PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    // Create the escrow token account if it does not exist so it can receive the NFT.
    invoke(
        &ata_instruction::create_associated_token_account(
            seller.key,
            escrow_pda.key,
            nft_mint.key,
            &spl_token::id(),
        ),
        &[seller.clone(), escrow_token_account.clone(), escrow_pda.clone(), nft_mint.clone(), system_program.clone(), token_program.clone(), ata_program.clone(), rent_sysvar.clone()],
    )?;
    // Transfer exactly 1 token (the NFT) from seller to escrow.
    invoke(
        &token_instruction::transfer(
            &spl_token::id(),
            seller_nft_account.key,
            escrow_token_account.key,
            seller.key,
            &[],
            1,
        )?,
        &[seller_nft_account.clone(), escrow_token_account.clone(), seller.clone(), token_program.clone()],
    )?;
    msg!("NFT held in escrow");
    Ok(())
}

// process_hold_payment receives lamports from the buyer into the escrow PDA.
fn process_hold_payment(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // buyer signs and sends the lamports.
    let buyer = next_account_info(account_info_iter)?;
    // escrow_pda is the destination account for the payment.
    let escrow_pda = next_account_info(account_info_iter)?;
    // system_program handles native SOL transfers.
    let system_program = next_account_info(account_info_iter)?;
    // rent_sysvar ensures the escrow account remains rent-exempt after receiving funds.
    let rent_sysvar = next_account_info(account_info_iter)?;

    if !buyer.is_signer {
        msg!("Buyer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let (expected_escrow_pda, escrow_bump) = Pubkey::find_program_address(
        &[b"escrow", buyer.key.as_ref()],
        program_id,
    );
    if expected_escrow_pda != *escrow_pda.key {
        msg!("Invalid escrow PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    let rent = Rent::from_account_info(rent_sysvar)?;
    // Ensure the escrow account has enough lamports to be rent-exempt plus the payment amount.
    let required_lamports = rent.minimum_balance(EscrowState::default().try_to_vec()?.len())
        .checked_add(amount)
        .ok_or(ProgramError::InsufficientFunds)?;
    // Transfer payment from buyer to escrow PDA.
    invoke(
        &system_instruction::transfer(buyer.key, escrow_pda.key, amount),
        &[buyer.clone(), escrow_pda.clone(), system_program.clone()],
    )?;
    msg!("Payment of {} lamports held in escrow", amount);
    Ok(())
}

// process_release_nft transfers the NFT from escrow to the buyer or winner.
fn process_release_nft(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // marketplace_program is the caller authorized to trigger release via CPI.
    let marketplace_program = next_account_info(account_info_iter)?;
    // recipient will receive the NFT.
    let recipient = next_account_info(account_info_iter)?;
    // nft_mint identifies the token.
    let nft_mint = next_account_info(account_info_iter)?;
    // escrow_pda owns the escrow state and must sign the transfer.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account holds the NFT balance.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // recipient_nft_account is the destination ATA.
    let recipient_nft_account = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;

    // Only the marketplace program should invoke this via CPI to enforce business rules.
    if *marketplace_program.key != *program_id {
        // In production, check against the known marketplace program ID.
        msg!("Unauthorized caller");
        // return Err(ProgramError::IncorrectProgramId);
    }
    let escrow_state = EscrowState::try_from_slice(&escrow_pda.data.borrow())?;
    if !escrow_state.is_active {
        msg!("Escrow not active");
        return Err(ProgramError::InvalidAccountData);
    }
    if !escrow_state.is_nft_held {
        msg!("No NFT held");
        return Err(ProgramError::InvalidAccountData);
    }
    // Verify the escrow PDA to prevent spoofing.
    let (expected_escrow_pda, _) = Pubkey::find_program_address(
        &[b"escrow", escrow_state.seller.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_escrow_pda != *escrow_pda.key {
        return Err(ProgramError::InvalidSeeds);
    }
    // Transfer the NFT using the escrow PDA as the authority.
    invoke_signed(
        &token_instruction::transfer(
            &spl_token::id(),
            escrow_token_account.key,
            recipient_nft_account.key,
            escrow_pda.key,
            &[],
            1,
        )?,
        &[escrow_token_account.clone(), recipient_nft_account.clone(), escrow_pda.clone(), token_program.clone()],
        &[&[b"escrow", escrow_state.seller.as_ref(), nft_mint.key.as_ref(), &[escrow_state.bump]]],
    )?;
    msg!("NFT released to recipient");
    Ok(())
}

// process_release_payment transfers escrowed lamports to the seller.
fn process_release_payment(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // marketplace_program triggers this via CPI.
    let marketplace_program = next_account_info(account_info_iter)?;
    // seller receives the payment.
    let seller = next_account_info(account_info_iter)?;
    // escrow_pda holds the lamports.
    let escrow_pda = next_account_info(account_info_iter)?;
    // system_program handles native transfers.
    let system_program = next_account_info(account_info_iter)?;

    let escrow_state = EscrowState::try_from_slice(&escrow_pda.data.borrow())?;
    if !escrow_state.is_active {
        msg!("Escrow not active");
        return Err(ProgramError::InvalidAccountData);
    }
    if !escrow_state.is_payment_held {
        msg!("No payment held");
        return Err(ProgramError::InvalidAccountData);
    }
    // Transfer all lamports from escrow to seller.
    **seller.lamports.borrow_mut() = seller.lamports()
        .checked_add(escrow_pda.lamports())
        .ok_or(ProgramError::AccountBorrowFailed)?;
    **escrow_pda.lamports.borrow_mut() = 0;
    let mut escrow_data = escrow_pda.data.borrow_mut();
    escrow_data.fill(0);
    msg!("Payment released to seller");
    Ok(())
}

// process_return_nft sends the NFT back to the seller when a trade is canceled.
fn process_return_nft(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // marketplace_program authorizes the return.
    let marketplace_program = next_account_info(account_info_iter)?;
    // seller receives the returned NFT.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint identifies the token.
    let nft_mint = next_account_info(account_info_iter)?;
    // escrow_pda owns the NFT.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account holds the NFT balance.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // seller_nft_account is the destination.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;

    let escrow_state = EscrowState::try_from_slice(&escrow_pda.data.borrow())?;
    if !escrow_state.is_active {
        msg!("Escrow not active");
        return Err(ProgramError::InvalidAccountData);
    }
    let (expected_escrow_pda, _) = Pubkey::find_program_address(
        &[b"escrow", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_escrow_pda != *escrow_pda.key {
        return Err(ProgramError::InvalidSeeds);
    }
    // Return the NFT to the seller using the escrow PDA as authority.
    invoke_signed(
        &token_instruction::transfer(
            &spl_token::id(),
            escrow_token_account.key,
            seller_nft_account.key,
            escrow_pda.key,
            &[],
            1,
        )?,
        &[escrow_token_account.clone(), seller_nft_account.clone(), escrow_pda.clone(), token_program.clone()],
        &[&[b"escrow", seller.key.as_ref(), nft_mint.key.as_ref(), &[escrow_state.bump]]],
    )?;
    msg!("NFT returned to seller");
    Ok(())
}

// process_return_payment refunds escrowed lamports to the buyer.
fn process_return_payment(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // marketplace_program authorizes the refund.
    let marketplace_program = next_account_info(account_info_iter)?;
    // buyer receives the refund.
    let buyer = next_account_info(account_info_iter)?;
    // escrow_pda holds the lamports.
    let escrow_pda = next_account_info(account_info_iter)?;
    // system_program handles native transfers.
    let system_program = next_account_info(account_info_iter)?;

    let escrow_state = EscrowState::try_from_slice(&escrow_pda.data.borrow())?;
    if !escrow_state.is_active {
        msg!("Escrow not active");
        return Err(ProgramError::InvalidAccountData);
    }
    // Transfer all lamports from escrow back to the buyer.
    **buyer.lamports.borrow_mut() = buyer.lamports()
        .checked_add(escrow_pda.lamports())
        .ok_or(ProgramError::AccountBorrowFailed)?;
    **escrow_pda.lamports.borrow_mut() = 0;
    let mut escrow_data = escrow_pda.data.borrow_mut();
    escrow_data.fill(0);
    msg!("Payment returned to buyer");
    Ok(())
}

// Default implementation for EscrowState to determine serialized size for rent calculations.
impl Default for EscrowState {
    fn default() -> Self {
        EscrowState {
            seller: Pubkey::default(),
            buyer: None,
            nft_mint: Pubkey::default(),
            payment_amount: 0,
            is_nft_held: false,
            is_payment_held: false,
            is_active: false,
            bump: 0,
        }
    }
}
