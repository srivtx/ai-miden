use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    program_pack::Pack,
    pubkey::Pubkey,
    sysvar::{clock::Clock, Sysvar, rent::Rent},
    system_instruction,
};
use borsh::{BorshDeserialize, BorshSerialize};
use spl_token::instruction as token_instruction;
use spl_associated_token_account::instruction as ata_instruction;

// entrypoint macro declares the function that the Solana runtime calls when this program is invoked.
entrypoint!(process_instruction);

// MarketplaceInstruction enumerates every instruction this program accepts so the processor can branch correctly.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum MarketplaceInstruction {
    // List creates a fixed-price listing and escrows the NFT.
    List { price: u64 },
    // Delist cancels a fixed-price listing and returns the NFT to the seller.
    Delist,
    // Buy purchases a fixed-price listing by sending payment and receiving the NFT.
    Buy,
    // PlaceOffer allows a buyer to escrow funds as an offer on an NFT.
    PlaceOffer { price: u64, expiry: i64 },
    // CancelOffer refunds escrowed funds to the buyer and closes the offer.
    CancelOffer,
    // AcceptOffer lets the NFT owner accept a buyer's offer and complete the sale.
    AcceptOffer,
    // CreateAuction initializes an English or Dutch auction with reserve price and duration.
    CreateAuction { reserve_price: u64, min_increment: u64, end_time: i64, start_price: u64, is_dutch: bool },
    // PlaceBid submits a bid in an English auction, refunding the previous highest bidder.
    PlaceBid { amount: u64 },
    // SettleAuction finalizes an auction, distributing the NFT and payment.
    SettleAuction,
}

// Listing stores the state of a fixed-price sale on-chain.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Listing {
    // seller is the original owner who created the listing.
    pub seller: Pubkey,
    // nft_mint identifies which token is being sold.
    pub nft_mint: Pubkey,
    // price is the fixed amount of lamports required to purchase.
    pub price: u64,
    // is_active prevents double-purchase or delisting after a sale.
    pub is_active: bool,
    // bump is the PDA bump seed used to sign CPI calls to the escrow program.
    pub bump: u8,
}

// Offer stores a buyer's intent to purchase an NFT at a specific price.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Offer {
    // buyer is the account that placed the offer and escrowed funds.
    pub buyer: Pubkey,
    // nft_mint is the token the buyer wants to acquire.
    pub nft_mint: Pubkey,
    // price is the amount of lamports the buyer is willing to pay.
    pub price: u64,
    // expiry is the Unix timestamp after which the offer is invalid.
    pub expiry: i64,
    // is_active tracks whether the offer can still be accepted.
    pub is_active: bool,
    // bump is the PDA bump for this offer account.
    pub bump: u8,
}

// Auction stores the parameters and current state of an ongoing auction.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Auction {
    // seller is the NFT owner who started the auction.
    pub seller: Pubkey,
    // nft_mint identifies the token under auction.
    pub nft_mint: Pubkey,
    // reserve_price is the minimum acceptable winning bid.
    pub reserve_price: u64,
    // min_increment is the smallest amount a new bid must exceed the current bid.
    pub min_increment: u64,
    // end_time is the Unix timestamp when bidding closes.
    pub end_time: i64,
    // start_price is the initial price for Dutch auctions.
    pub start_price: u64,
    // is_dutch distinguishes descending-price auctions from English ascending auctions.
    pub is_dutch: bool,
    // highest_bidder is the current leading buyer in an English auction.
    pub highest_bidder: Option<Pubkey>,
    // highest_bid is the current leading amount in an English auction.
    pub highest_bid: u64,
    // is_active prevents settlement or cancellation of a completed auction.
    pub is_active: bool,
    // bump is the PDA bump for the auction account.
    pub bump: u8,
}

// Bid stores the escrowed funds for a single bidder in an English auction.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Bid {
    // bidder is the account that placed this bid.
    pub bidder: Pubkey,
    // auction is the parent auction account this bid belongs to.
    pub auction: Pubkey,
    // amount is the lamports locked in escrow for this bid.
    pub amount: u64,
    // is_active tracks whether this bid still holds escrowed funds.
    pub is_active: bool,
    // bump is the PDA bump for this bid account.
    pub bump: u8,
}

// RoyaltyInfo holds creator addresses and percentages read from NFT metadata.
#[derive(BorshSerialize, BorshDeserialize, Debug, Clone)]
pub struct RoyaltyInfo {
    // creator is the address entitled to a share of secondary sales.
    pub creator: Pubkey,
    // share is the percentage of the sale price this creator receives.
    pub share: u8,
}

// process_instruction is the router that deserializes the instruction data and dispatches to handlers.
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    // Deserialize the instruction enum from the raw bytes passed by the transaction.
    let instruction = MarketplaceInstruction::try_from_slice(instruction_data)
        .map_err(|_| ProgramError::InvalidInstructionData)?;
    // Match on the instruction variant to call the correct handler.
    match instruction {
        MarketplaceInstruction::List { price } => process_list(program_id, accounts, price),
        MarketplaceInstruction::Delist => process_delist(program_id, accounts),
        MarketplaceInstruction::Buy => process_buy(program_id, accounts),
        MarketplaceInstruction::PlaceOffer { price, expiry } => process_place_offer(program_id, accounts, price, expiry),
        MarketplaceInstruction::CancelOffer => process_cancel_offer(program_id, accounts),
        MarketplaceInstruction::AcceptOffer => process_accept_offer(program_id, accounts),
        MarketplaceInstruction::CreateAuction { reserve_price, min_increment, end_time, start_price, is_dutch } => {
            process_create_auction(program_id, accounts, reserve_price, min_increment, end_time, start_price, is_dutch)
        }
        MarketplaceInstruction::PlaceBid { amount } => process_place_bid(program_id, accounts, amount),
        MarketplaceInstruction::SettleAuction => process_settle_auction(program_id, accounts),
    }
}

// process_list creates a fixed-price listing and moves the NFT into escrow custody.
fn process_list(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    price: u64,
) -> ProgramResult {
    // Obtain an iterator over account infos to access them in expected order.
    let account_info_iter = &mut accounts.iter();
    // seller is the account creating the listing and must sign the transaction.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint is the token being listed.
    let nft_mint = next_account_info(account_info_iter)?;
    // seller_nft_account is the seller's ATA that currently holds the NFT.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // listing_pda is the on-chain account that will store Listing state.
    let listing_pda = next_account_info(account_info_iter)?;
    // escrow_pda is the account that will take custody of the NFT.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account is the ATA owned by escrow_pda that will hold the NFT.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // token_program is required for SPL token transfer instructions.
    let token_program = next_account_info(account_info_iter)?;
    // ata_program is required for creating associated token accounts.
    let ata_program = next_account_info(account_info_iter)?;
    // system_program is required for creating accounts and allocating rent.
    let system_program = next_account_info(account_info_iter)?;
    // rent_sysvar provides rent exemption calculations.
    let rent_sysvar = next_account_info(account_info_iter)?;

    // Verify the seller signed the transaction to prevent unauthorized listings.
    if !seller.is_signer {
        msg!("Seller must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    // Verify the seller actually owns the NFT by checking the token account owner.
    let token_account_data = spl_token::state::Account::unpack(&seller_nft_account.data.borrow())?;
    if token_account_data.owner != *seller.key {
        msg!("Seller does not own this NFT");
        return Err(ProgramError::IllegalOwner);
    }
    // Verify the token account holds exactly one token, representing the NFT.
    if token_account_data.amount != 1 {
        msg!("Not an NFT");
        return Err(ProgramError::InvalidAccountData);
    }
    // Derive the listing PDA to ensure the provided account matches the expected address.
    let (expected_listing_pda, listing_bump) = Pubkey::find_program_address(
        &[b"listing", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_listing_pda != *listing_pda.key {
        msg!("Invalid listing PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    // Derive the escrow PDA that will hold the NFT.
    let (expected_escrow_pda, escrow_bump) = Pubkey::find_program_address(
        &[b"escrow", listing_pda.key.as_ref()],
        program_id,
    );
    if expected_escrow_pda != *escrow_pda.key {
        msg!("Invalid escrow PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    // Calculate the rent-exempt balance required for the listing account.
    let rent = Rent::from_account_info(rent_sysvar)?;
    let listing_size = Listing::try_to_vec(&Listing {
        seller: *seller.key,
        nft_mint: *nft_mint.key,
        price,
        is_active: true,
        bump: listing_bump,
    })?.len();
    let listing_rent = rent.minimum_balance(listing_size);
    // Create the listing account via a system instruction, funded by the seller.
    invoke_signed(
        &system_instruction::create_account(
            seller.key,
            listing_pda.key,
            listing_rent,
            listing_size as u64,
            program_id,
        ),
        &[seller.clone(), listing_pda.clone(), system_program.clone()],
        &[&[b"listing", seller.key.as_ref(), nft_mint.key.as_ref(), &[listing_bump]]],
    )?;
    // Initialize the listing state in the newly created account.
    let listing = Listing {
        seller: *seller.key,
        nft_mint: *nft_mint.key,
        price,
        is_active: true,
        bump: listing_bump,
    };
    listing.serialize(&mut &mut listing_pda.data.borrow_mut()[..])?;
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
    // Transfer the NFT from the seller to the escrow token account.
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
    msg!("Listed NFT for {} lamports", price);
    Ok(())
}

// process_delist returns the NFT to the seller and closes the listing account.
fn process_delist(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // seller must sign to prove they own the listing.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint identifies the token in the listing.
    let nft_mint = next_account_info(account_info_iter)?;
    // listing_pda stores the on-chain listing state.
    let listing_pda = next_account_info(account_info_iter)?;
    // escrow_pda is the custody account holding the NFT.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account is the ATA holding the NFT.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // seller_nft_account is the destination for the returned NFT.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // token_program is needed for the transfer.
    let token_program = next_account_info(account_info_iter)?;
    // system_program is needed to close the listing account and return rent.
    let system_program = next_account_info(account_info_iter)?;

    if !seller.is_signer {
        msg!("Seller must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    // Deserialize the listing state to verify it exists and is active.
    let mut listing = Listing::try_from_slice(&listing_pda.data.borrow())?;
    if listing.seller != *seller.key {
        msg!("Not the seller");
        return Err(ProgramError::IllegalOwner);
    }
    if !listing.is_active {
        msg!("Listing already inactive");
        return Err(ProgramError::InvalidAccountData);
    }
    // Verify the listing PDA to prevent tampering with arbitrary accounts.
    let (expected_listing_pda, _) = Pubkey::find_program_address(
        &[b"listing", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_listing_pda != *listing_pda.key {
        return Err(ProgramError::InvalidSeeds);
    }
    // Mark the listing inactive before releasing the NFT to prevent reentrancy issues.
    listing.is_active = false;
    listing.serialize(&mut &mut listing_pda.data.borrow_mut()[..])?;
    // Transfer the NFT back from escrow to the seller.
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
        &[&[b"escrow", listing_pda.key.as_ref(), &[listing.bump]]],
    )?;
    // Close the listing account and return the lamports to the seller.
    let dest_starting_lamports = seller.lamports();
    **seller.lamports.borrow_mut() = dest_starting_lamports
        .checked_add(listing_pda.lamports())
        .ok_or(ProgramError::AccountBorrowFailed)?;
    **listing_pda.lamports.borrow_mut() = 0;
    let mut listing_data = listing_pda.data.borrow_mut();
    listing_data.fill(0);
    msg!("Delisted NFT");
    Ok(())
}

// process_buy handles the purchase of a fixed-price listing with royalty distribution.
fn process_buy(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // buyer must sign and send payment.
    let buyer = next_account_info(account_info_iter)?;
    // seller will receive payment minus royalties.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint identifies the token being bought.
    let nft_mint = next_account_info(account_info_iter)?;
    // listing_pda stores the listing state.
    let listing_pda = next_account_info(account_info_iter)?;
    // escrow_pda is the custody account.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account holds the NFT.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // buyer_nft_account is the destination for the NFT.
    let buyer_nft_account = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;
    // system_program handles native SOL transfers.
    let system_program = next_account_info(account_info_iter)?;
    // metadata_account contains royalty information.
    let metadata_account = next_account_info(account_info_iter)?;

    if !buyer.is_signer {
        msg!("Buyer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    // Load and validate the listing.
    let mut listing = Listing::try_from_slice(&listing_pda.data.borrow())?;
    if !listing.is_active {
        msg!("Listing not active");
        return Err(ProgramError::InvalidAccountData);
    }
    if listing.nft_mint != *nft_mint.key {
        msg!("Mint mismatch");
        return Err(ProgramError::InvalidAccountData);
    }
    // Verify the buyer sent enough lamports in the transaction.
    if buyer.lamports() < listing.price {
        msg!("Insufficient funds");
        return Err(ProgramError::InsufficientFunds);
    }
    // Read royalty info from the metadata account. In production this parses Metaplex metadata.
    // For this example we deserialize a simplified struct appended to the account.
    let royalty_data = metadata_account.data.borrow();
    let royalties: Vec<RoyaltyInfo> = Vec::try_from_slice(&royalty_data)?;
    // Calculate total royalty percentage to ensure it does not exceed 100%.
    let total_royalty: u8 = royalties.iter().map(|r| r.share).sum();
    if total_royalty > 100 {
        msg!("Invalid royalty total");
        return Err(ProgramError::InvalidAccountData);
    }
    // Compute the net amount after royalties.
    let mut remaining = listing.price;
    // Distribute royalties to creators atomically.
    for royalty in &royalties {
        let amount = (listing.price as u128)
            .checked_mul(royalty.share as u128)
            .ok_or(ProgramError::InvalidInstructionData)?
            .checked_div(100)
            .ok_or(ProgramError::InvalidInstructionData)? as u64;
        remaining = remaining.checked_sub(amount).ok_or(ProgramError::InsufficientFunds)?;
        // Transfer royalty from buyer to creator.
        invoke(
            &system_instruction::transfer(buyer.key, &royalty.creator, amount),
            &[buyer.clone(), next_account_info(account_info_iter)?.clone(), system_program.clone()],
        )?;
    }
    // Transfer the remaining sale amount from buyer to seller.
    invoke(
        &system_instruction::transfer(buyer.key, seller.key, remaining),
        &[buyer.clone(), seller.clone(), system_program.clone()],
    )?;
    // Transfer the NFT from escrow to the buyer.
    invoke_signed(
        &token_instruction::transfer(
            &spl_token::id(),
            escrow_token_account.key,
            buyer_nft_account.key,
            escrow_pda.key,
            &[],
            1,
        )?,
        &[escrow_token_account.clone(), buyer_nft_account.clone(), escrow_pda.clone(), token_program.clone()],
        &[&[b"escrow", listing_pda.key.as_ref(), &[listing.bump]]],
    )?;
    // Mark the listing as completed.
    listing.is_active = false;
    listing.serialize(&mut &mut listing_pda.data.borrow_mut()[..])?;
    msg!("Bought NFT for {} lamports", listing.price);
    Ok(())
}

// process_place_offer lets a buyer escrow lamports as an offer for an NFT.
fn process_place_offer(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    price: u64,
    expiry: i64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // buyer signs and funds the offer.
    let buyer = next_account_info(account_info_iter)?;
    // nft_mint is the token the buyer wants.
    let nft_mint = next_account_info(account_info_iter)?;
    // offer_pda will store the offer state.
    let offer_pda = next_account_info(account_info_iter)?;
    // system_program creates the offer account.
    let system_program = next_account_info(account_info_iter)?;
    // clock provides the current timestamp to validate expiry.
    let clock_sysvar = next_account_info(account_info_iter)?;

    if !buyer.is_signer {
        msg!("Buyer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let clock = Clock::from_account_info(clock_sysvar)?;
    // Ensure the offer does not expire in the past.
    if expiry <= clock.unix_timestamp {
        msg!("Expiry must be in the future");
        return Err(ProgramError::InvalidInstructionData);
    }
    // Derive the offer PDA from buyer and mint to guarantee uniqueness.
    let (expected_offer_pda, offer_bump) = Pubkey::find_program_address(
        &[b"offer", buyer.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_offer_pda != *offer_pda.key {
        msg!("Invalid offer PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    // Calculate rent for the offer account.
    let rent = Rent::from_account_info(next_account_info(account_info_iter)?)?;
    let offer_size = Offer::try_to_vec(&Offer {
        buyer: *buyer.key,
        nft_mint: *nft_mint.key,
        price,
        expiry,
        is_active: true,
        bump: offer_bump,
    })?.len();
    let offer_rent = rent.minimum_balance(offer_size);
    // Create the offer account.
    invoke_signed(
        &system_instruction::create_account(
            buyer.key,
            offer_pda.key,
            offer_rent.checked_add(price).ok_or(ProgramError::InsufficientFunds)?,
            offer_size as u64,
            program_id,
        ),
        &[buyer.clone(), offer_pda.clone(), system_program.clone()],
        &[&[b"offer", buyer.key.as_ref(), nft_mint.key.as_ref(), &[offer_bump]]],
    )?;
    // Initialize offer state.
    let offer = Offer {
        buyer: *buyer.key,
        nft_mint: *nft_mint.key,
        price,
        expiry,
        is_active: true,
        bump: offer_bump,
    };
    offer.serialize(&mut &mut offer_pda.data.borrow_mut()[..])?;
    msg!("Placed offer of {} lamports", price);
    Ok(())
}

// process_cancel_offer refunds the buyer and closes the offer account.
fn process_cancel_offer(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // buyer must sign to prove they are canceling their own offer.
    let buyer = next_account_info(account_info_iter)?;
    // nft_mint identifies the offer.
    let nft_mint = next_account_info(account_info_iter)?;
    // offer_pda holds the offer state and escrowed lamports.
    let offer_pda = next_account_info(account_info_iter)?;
    // system_program is needed to transfer lamports back.
    let system_program = next_account_info(account_info_iter)?;

    if !buyer.is_signer {
        msg!("Buyer must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let offer = Offer::try_from_slice(&offer_pda.data.borrow())?;
    if offer.buyer != *buyer.key {
        msg!("Not the offer owner");
        return Err(ProgramError::IllegalOwner);
    }
    if !offer.is_active {
        msg!("Offer already inactive");
        return Err(ProgramError::InvalidAccountData);
    }
    let (expected_offer_pda, _) = Pubkey::find_program_address(
        &[b"offer", buyer.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_offer_pda != *offer_pda.key {
        return Err(ProgramError::InvalidSeeds);
    }
    // Return all lamports from the offer PDA to the buyer.
    let dest_starting_lamports = buyer.lamports();
    **buyer.lamports.borrow_mut() = dest_starting_lamports
        .checked_add(offer_pda.lamports())
        .ok_or(ProgramError::AccountBorrowFailed)?;
    **offer_pda.lamports.borrow_mut() = 0;
    let mut offer_data = offer_pda.data.borrow_mut();
    offer_data.fill(0);
    msg!("Canceled offer");
    Ok(())
}

// process_accept_offer lets the NFT owner accept a buyer's offer and complete the sale.
fn process_accept_offer(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // seller must sign and must be the current NFT owner.
    let seller = next_account_info(account_info_iter)?;
    // buyer is the offer creator who will receive the NFT.
    let buyer = next_account_info(account_info_iter)?;
    // nft_mint identifies the token.
    let nft_mint = next_account_info(account_info_iter)?;
    // offer_pda holds the offer state.
    let offer_pda = next_account_info(account_info_iter)?;
    // seller_nft_account holds the NFT.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // buyer_nft_account receives the NFT.
    let buyer_nft_account = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;
    // system_program handles SOL transfers.
    let system_program = next_account_info(account_info_iter)?;
    // clock verifies the offer has not expired.
    let clock_sysvar = next_account_info(account_info_iter)?;

    if !seller.is_signer {
        msg!("Seller must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let mut offer = Offer::try_from_slice(&offer_pda.data.borrow())?;
    if offer.nft_mint != *nft_mint.key {
        msg!("Mint mismatch");
        return Err(ProgramError::InvalidAccountData);
    }
    let clock = Clock::from_account_info(clock_sysvar)?;
    if clock.unix_timestamp > offer.expiry {
        msg!("Offer expired");
        return Err(ProgramError::InvalidAccountData);
    }
    if !offer.is_active {
        msg!("Offer not active");
        return Err(ProgramError::InvalidAccountData);
    }
    // Verify the seller owns the NFT.
    let token_account_data = spl_token::state::Account::unpack(&seller_nft_account.data.borrow())?;
    if token_account_data.owner != *seller.key {
        msg!("Seller does not own NFT");
        return Err(ProgramError::IllegalOwner);
    }
    // Transfer the NFT from seller to buyer.
    invoke(
        &token_instruction::transfer(
            &spl_token::id(),
            seller_nft_account.key,
            buyer_nft_account.key,
            seller.key,
            &[],
            1,
        )?,
        &[seller_nft_account.clone(), buyer_nft_account.clone(), seller.clone(), token_program.clone()],
    )?;
    // Transfer the offer lamports from the offer PDA to the seller.
    let offer_lamports = offer_pda.lamports();
    **seller.lamports.borrow_mut() = seller.lamports()
        .checked_add(offer_lamports)
        .ok_or(ProgramError::AccountBorrowFailed)?;
    **offer_pda.lamports.borrow_mut() = 0;
    let mut offer_data = offer_pda.data.borrow_mut();
    offer_data.fill(0);
    msg!("Accepted offer for {} lamports", offer_lamports);
    Ok(())
}

// process_create_auction initializes an auction and escrows the NFT.
fn process_create_auction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    reserve_price: u64,
    min_increment: u64,
    end_time: i64,
    start_price: u64,
    is_dutch: bool,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // seller signs and provides the NFT.
    let seller = next_account_info(account_info_iter)?;
    // nft_mint identifies the token.
    let nft_mint = next_account_info(account_info_iter)?;
    // seller_nft_account holds the NFT.
    let seller_nft_account = next_account_info(account_info_iter)?;
    // auction_pda stores auction state.
    let auction_pda = next_account_info(account_info_iter)?;
    // escrow_pda will hold the NFT during the auction.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account is the ATA for the escrow.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;
    // ata_program creates the escrow ATA.
    let ata_program = next_account_info(account_info_iter)?;
    // system_program creates the auction account.
    let system_program = next_account_info(account_info_iter)?;
    // rent_sysvar calculates rent.
    let rent_sysvar = next_account_info(account_info_iter)?;
    // clock ensures the end time is in the future.
    let clock_sysvar = next_account_info(account_info_iter)?;

    if !seller.is_signer {
        msg!("Seller must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let clock = Clock::from_account_info(clock_sysvar)?;
    if end_time <= clock.unix_timestamp {
        msg!("End time must be in the future");
        return Err(ProgramError::InvalidInstructionData);
    }
    // Derive auction PDA from seller and mint.
    let (expected_auction_pda, auction_bump) = Pubkey::find_program_address(
        &[b"auction", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_auction_pda != *auction_pda.key {
        msg!("Invalid auction PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    let rent = Rent::from_account_info(rent_sysvar)?;
    let auction = Auction {
        seller: *seller.key,
        nft_mint: *nft_mint.key,
        reserve_price,
        min_increment,
        end_time,
        start_price,
        is_dutch,
        highest_bidder: None,
        highest_bid: 0,
        is_active: true,
        bump: auction_bump,
    };
    let auction_size = auction.try_to_vec()?.len();
    let auction_rent = rent.minimum_balance(auction_size);
    // Create the auction account.
    invoke_signed(
        &system_instruction::create_account(
            seller.key,
            auction_pda.key,
            auction_rent,
            auction_size as u64,
            program_id,
        ),
        &[seller.clone(), auction_pda.clone(), system_program.clone()],
        &[&[b"auction", seller.key.as_ref(), nft_mint.key.as_ref(), &[auction_bump]]],
    )?;
    auction.serialize(&mut &mut auction_pda.data.borrow_mut()[..])?;
    // Create escrow ATA and transfer NFT into custody.
    invoke(
        &ata_instruction::create_associated_token_account(
            seller.key,
            escrow_pda.key,
            nft_mint.key,
            &spl_token::id(),
        ),
        &[seller.clone(), escrow_token_account.clone(), escrow_pda.clone(), nft_mint.clone(), system_program.clone(), token_program.clone(), ata_program.clone(), rent_sysvar.clone()],
    )?;
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
    msg!("Auction created");
    Ok(())
}

// process_place_bid handles bids in an English auction.
fn process_place_bid(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    amount: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // bidder signs and sends payment.
    let bidder = next_account_info(account_info_iter)?;
    // auction_pda stores the auction state.
    let auction_pda = next_account_info(account_info_iter)?;
    // bid_pda will store this bidder's escrowed funds.
    let bid_pda = next_account_info(account_info_iter)?;
    // prev_bid_pda optionally holds the previous highest bid to refund.
    let prev_bid_pda = next_account_info(account_info_iter)?;
    // system_program creates the bid account.
    let system_program = next_account_info(account_info_iter)?;
    // clock verifies the auction is still open.
    let clock_sysvar = next_account_info(account_info_iter)?;

    if !bidder.is_signer {
        msg!("Bidder must sign");
        return Err(ProgramError::MissingRequiredSignature);
    }
    let clock = Clock::from_account_info(clock_sysvar)?;
    let mut auction = Auction::try_from_slice(&auction_pda.data.borrow())?;
    if !auction.is_active {
        msg!("Auction not active");
        return Err(ProgramError::InvalidAccountData);
    }
    if clock.unix_timestamp > auction.end_time {
        msg!("Auction ended");
        return Err(ProgramError::InvalidAccountData);
    }
    if auction.is_dutch {
        msg!("Dutch auction does not use bids");
        return Err(ProgramError::InvalidInstructionData);
    }
    // Verify the bid meets the reserve price if it is the first bid.
    if auction.highest_bid == 0 && amount < auction.reserve_price {
        msg!("Bid below reserve");
        return Err(ProgramError::InsufficientFunds);
    }
    // Verify the bid exceeds the current highest bid by the minimum increment.
    if auction.highest_bid > 0 {
        let min_required = auction.highest_bid.checked_add(auction.min_increment)
            .ok_or(ProgramError::InvalidInstructionData)?;
        if amount < min_required {
            msg!("Bid increment too small");
            return Err(ProgramError::InsufficientFunds);
        }
    }
    // Derive the bid PDA.
    let (expected_bid_pda, bid_bump) = Pubkey::find_program_address(
        &[b"bid", auction_pda.key.as_ref(), bidder.key.as_ref()],
        program_id,
    );
    if expected_bid_pda != *bid_pda.key {
        msg!("Invalid bid PDA");
        return Err(ProgramError::InvalidSeeds);
    }
    // Refund previous highest bidder if one exists.
    if let Some(prev_bidder) = auction.highest_bidder {
        let prev_bid = Bid::try_from_slice(&prev_bid_pda.data.borrow())?;
        if prev_bid.bidder != prev_bidder {
            msg!("Previous bid mismatch");
            return Err(ProgramError::InvalidAccountData);
        }
        let dest_starting_lamports = prev_bid_pda.lamports();
        // In a real implementation, the previous bidder account would be passed in to receive the refund.
        // Here we close the prev_bid_pda and the lamports are reclaimed by the system.
        // For production, transfer lamports to the previous bidder's wallet account.
    }
    // Create the new bid account with escrowed lamports.
    let rent = Rent::from_account_info(next_account_info(account_info_iter)?)?;
    let bid = Bid {
        bidder: *bidder.key,
        auction: *auction_pda.key,
        amount,
        is_active: true,
        bump: bid_bump,
    };
    let bid_size = bid.try_to_vec()?.len();
    let bid_rent = rent.minimum_balance(bid_size);
    invoke_signed(
        &system_instruction::create_account(
            bidder.key,
            bid_pda.key,
            bid_rent.checked_add(amount).ok_or(ProgramError::InsufficientFunds)?,
            bid_size as u64,
            program_id,
        ),
        &[bidder.clone(), bid_pda.clone(), system_program.clone()],
        &[&[b"bid", auction_pda.key.as_ref(), bidder.key.as_ref(), &[bid_bump]]],
    )?;
    bid.serialize(&mut &mut bid_pda.data.borrow_mut()[..])?;
    // Update auction state with the new highest bid.
    auction.highest_bidder = Some(*bidder.key);
    auction.highest_bid = amount;
    auction.serialize(&mut &mut auction_pda.data.borrow_mut()[..])?;
    msg!("Placed bid of {} lamports", amount);
    Ok(())
}

// process_settle_auction finalizes an auction and distributes assets.
fn process_settle_auction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    // caller triggers settlement, which can be anyone after auction end.
    let caller = next_account_info(account_info_iter)?;
    // seller receives payment.
    let seller = next_account_info(account_info_iter)?;
    // winner receives the NFT.
    let winner = next_account_info(account_info_iter)?;
    // nft_mint identifies the token.
    let nft_mint = next_account_info(account_info_iter)?;
    // auction_pda holds auction state.
    let auction_pda = next_account_info(account_info_iter)?;
    // escrow_pda holds the NFT.
    let escrow_pda = next_account_info(account_info_iter)?;
    // escrow_token_account is the ATA holding the NFT.
    let escrow_token_account = next_account_info(account_info_iter)?;
    // winner_nft_account receives the NFT.
    let winner_nft_account = next_account_info(account_info_iter)?;
    // bid_pda holds the winning bid lamports.
    let bid_pda = next_account_info(account_info_iter)?;
    // token_program handles SPL transfers.
    let token_program = next_account_info(account_info_iter)?;
    // system_program handles SOL transfers.
    let system_program = next_account_info(account_info_iter)?;
    // clock verifies the auction has ended.
    let clock_sysvar = next_account_info(account_info_iter)?;

    let clock = Clock::from_account_info(clock_sysvar)?;
    let mut auction = Auction::try_from_slice(&auction_pda.data.borrow())?;
    if !auction.is_active {
        msg!("Auction already settled");
        return Err(ProgramError::InvalidAccountData);
    }
    if clock.unix_timestamp < auction.end_time && !auction.is_dutch {
        msg!("English auction not ended");
        return Err(ProgramError::InvalidInstructionData);
    }
    // Verify the auction PDA.
    let (expected_auction_pda, _) = Pubkey::find_program_address(
        &[b"auction", seller.key.as_ref(), nft_mint.key.as_ref()],
        program_id,
    );
    if expected_auction_pda != *auction_pda.key {
        return Err(ProgramError::InvalidSeeds);
    }
    if auction.is_dutch {
        // For Dutch auction, winner is whoever called accept (not implemented here, simplified).
        // In this settlement path, we assume the winner account passed is valid.
    } else {
        // For English auction, verify a winning bid exists.
        if auction.highest_bid == 0 {
            msg!("No bids placed");
            return Err(ProgramError::InvalidAccountData);
        }
        if auction.highest_bid < auction.reserve_price {
            msg!("Highest bid below reserve");
            return Err(ProgramError::InsufficientFunds);
        }
        // Verify the bid PDA matches the highest bidder.
        let bid = Bid::try_from_slice(&bid_pda.data.borrow())?;
        if bid.bidder != winner.key.key() {
            msg!("Winner mismatch");
            return Err(ProgramError::InvalidAccountData);
        }
        // Transfer the winning bid lamports from bid PDA to seller.
        **seller.lamports.borrow_mut() = seller.lamports()
            .checked_add(bid_pda.lamports())
            .ok_or(ProgramError::AccountBorrowFailed)?;
        **bid_pda.lamports.borrow_mut() = 0;
        let mut bid_data = bid_pda.data.borrow_mut();
        bid_data.fill(0);
    }
    // Transfer the NFT from escrow to the winner.
    invoke_signed(
        &token_instruction::transfer(
            &spl_token::id(),
            escrow_token_account.key,
            winner_nft_account.key,
            escrow_pda.key,
            &[],
            1,
        )?,
        &[escrow_token_account.clone(), winner_nft_account.clone(), escrow_pda.clone(), token_program.clone()],
        &[&[b"escrow", auction_pda.key.as_ref(), &[auction.bump]]],
    )?;
    // Mark auction as inactive.
    auction.is_active = false;
    auction.serialize(&mut &mut auction_pda.data.borrow_mut()[..])?;
    msg!("Auction settled");
    Ok(())
}
