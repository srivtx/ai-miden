use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount};

// Declare the program ID so Solana runtime routes transactions to this program.
declare_id!("Market22222222222222222222222222222222222222");

// Define the program module containing all marketplace instructions.
#[program]
pub mod nft_marketplace {
    use super::*;

    // The list instruction places an NFT into escrow and records the asking price.
    pub fn list(ctx: Context<List>, price: u64) -> Result<()> {
        // Prevent zero-price listings because they would allow theft of valuable NFTs.
        require!(price > 0, ErrorCode::PriceMustBeGreaterThanZero);

        // Transfer the NFT from the seller's token account into the program escrow account.
        let cpi_accounts = token::Transfer {
            from: ctx.accounts.seller_token_account.to_account_info(),
            to: ctx.accounts.escrow_token_account.to_account_info(),
            authority: ctx.accounts.seller.to_account_info(),
        };
        // Use the token program to perform the cross-program transfer securely.
        let cpi_program = ctx.accounts.token_program.to_account_info();
        // Create a CPI context so the token program can verify the seller's signature.
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        // Execute the transfer, moving exactly one NFT into escrow.
        token::transfer(cpi_ctx, 1)?;

        // Populate the listing account with trade details for buyers to discover.
        let listing = &mut ctx.accounts.listing;
        listing.seller = ctx.accounts.seller.key();
        listing.mint = ctx.accounts.mint.key();
        listing.price = price;
        listing.is_active = true;

        // Return Ok to confirm the listing was created successfully.
        Ok(())
    }

    // The buy instruction executes a sale by swapping SOL for the escrowed NFT.
    pub fn buy(ctx: Context<Buy>) -> Result<()> {
        // Load the listing account mutably so we can deactivate it after sale.
        let listing = &mut ctx.accounts.listing;
        // Ensure the listing is still active so buyers cannot purchase already-sold items.
        require!(listing.is_active, ErrorCode::ListingNotActive);

        // Calculate the marketplace platform fee as 2% of the sale price for sustainability.
        let platform_fee = listing.price.checked_mul(2).unwrap().checked_div(100).unwrap();
        // Calculate the royalty payment as 5% of the sale price for creator compensation.
        let royalty = listing.price.checked_mul(5).unwrap().checked_div(100).unwrap();
        // The seller receives everything left after platform and royalty deductions.
        let seller_proceeds = listing.price.checked_sub(platform_fee).unwrap().checked_sub(royalty).unwrap();

        // Transfer platform fee from buyer to the fee destination account.
        let platform_transfer = anchor_lang::solana_program::system_instruction::transfer(
            &ctx.accounts.buyer.key(),
            &ctx.accounts.fee_destination.key(),
            platform_fee,
        );
        anchor_lang::solana_program::program::invoke(
            &platform_transfer,
            &[
                ctx.accounts.buyer.to_account_info(),
                ctx.accounts.fee_destination.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
            ],
        )?;

        // Transfer royalty from buyer to the creator account to honor secondary sales.
        let royalty_transfer = anchor_lang::solana_program::system_instruction::transfer(
            &ctx.accounts.buyer.key(),
            &ctx.accounts.creator.key(),
            royalty,
        );
        anchor_lang::solana_program::program::invoke(
            &royalty_transfer,
            &[
                ctx.accounts.buyer.to_account_info(),
                ctx.accounts.creator.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
            ],
        )?;

        // Transfer the remaining proceeds from buyer to the original seller.
        let seller_transfer = anchor_lang::solana_program::system_instruction::transfer(
            &ctx.accounts.buyer.key(),
            &listing.seller,
            seller_proceeds,
        );
        anchor_lang::solana_program::program::invoke(
            &seller_transfer,
            &[
                ctx.accounts.buyer.to_account_info(),
                ctx.accounts.seller.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
            ],
        )?;

        // Transfer the NFT from escrow to the buyer's token account atomically with payment.
        let cpi_accounts = token::Transfer {
            from: ctx.accounts.escrow_token_account.to_account_info(),
            to: ctx.accounts.buyer_token_account.to_account_info(),
            authority: ctx.accounts.escrow_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        // Sign on behalf of the program-derived address that owns the escrow account.
        let seeds = &[b"escrow", listing.mint.as_ref(), &[ctx.bumps.escrow_authority]];
        let signer = &[&seeds[..]];
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);
        token::transfer(cpi_ctx, 1)?;

        // Mark the listing as inactive so no one else can buy the same item.
        listing.is_active = false;

        // Return Ok to signal the atomic swap completed without errors.
        Ok(())
    }

    // The cancel instruction allows the seller to withdraw their NFT if it has not sold.
    pub fn cancel(ctx: Context<Cancel>) -> Result<()> {
        // Load the listing to verify the caller is the original seller.
        let listing = &ctx.accounts.listing;
        require!(listing.seller == ctx.accounts.seller.key(), ErrorCode::Unauthorized);

        // Transfer the NFT from escrow back to the seller's token account.
        let cpi_accounts = token::Transfer {
            from: ctx.accounts.escrow_token_account.to_account_info(),
            to: ctx.accounts.seller_token_account.to_account_info(),
            authority: ctx.accounts.escrow_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        // Use the program-derived address seeds to authorize the return transfer.
        let seeds = &[b"escrow", listing.mint.as_ref(), &[ctx.bumps.escrow_authority]];
        let signer = &[&seeds[..]];
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);
        token::transfer(cpi_ctx, 1)?;

        // Return Ok to confirm the NFT was returned to the seller successfully.
        Ok(())
    }
}

// Accounts required to create a new listing.
#[derive(Accounts)]
#[instruction(price: u64)]
pub struct List<'info> {
    // The seller must sign to prove they authorize transferring their NFT.
    #[account(mut)]
    pub seller: Signer<'info>,

    // The mint account identifies which NFT collection or unique token is being listed.
    pub mint: Account<'info, Mint>,

    // The seller's token account holds the NFT before it moves into escrow.
    #[account(mut, token::mint = mint, token::authority = seller)]
    pub seller_token_account: Account<'info, TokenAccount>,

    // The escrow token account receives the NFT and is owned by a program-derived address.
    #[account(
        init,
        payer = seller,
        token::mint = mint,
        token::authority = escrow_authority,
        seeds = [b"escrow", mint.key().as_ref()],
        bump
    )]
    pub escrow_token_account: Account<'info, TokenAccount>,

    // The escrow authority is a PDA that signs transfers out of escrow.
    #[account(seeds = [b"escrow", mint.key().as_ref()], bump)]
    pub escrow_authority: AccountInfo<'info>,

    // The listing account stores price, seller, and active state for discoverability.
    #[account(
        init,
        payer = seller,
        space = 8 + 32 + 32 + 8 + 1, // discriminator + pubkey + pubkey + u64 + bool
        seeds = [b"listing", mint.key().as_ref()],
        bump
    )]
    pub listing: Account<'info, Listing>,

    // The token program is required for SPL token transfers.
    pub token_program: Program<'info, Token>,

    // The system program is required for creating new accounts.
    pub system_program: Program<'info, System>,

    // Rent sysvar is needed for rent-exempt account creation.
    pub rent: Sysvar<'info, Rent>,
}

// Accounts required to execute a purchase.
#[derive(Accounts)]
pub struct Buy<'info> {
    // The buyer must sign and pay the listed price plus fees.
    #[account(mut)]
    pub buyer: Signer<'info>,

    // The seller receives the proceeds after deductions.
    #[account(mut)]
    pub seller: AccountInfo<'info>,

    // The creator receives the royalty payment.
    #[account(mut)]
    pub creator: AccountInfo<'info>,

    // The fee destination receives the platform commission.
    #[account(mut)]
    pub fee_destination: AccountInfo<'info>,

    // The mint identifies which NFT is being purchased.
    pub mint: Account<'info, Mint>,

    // The buyer's token account receives the NFT after payment.
    #[account(
        init_if_needed,
        payer = buyer,
        token::mint = mint,
        token::authority = buyer,
    )]
    pub buyer_token_account: Account<'info, TokenAccount>,

    // The escrow token account holds the NFT until the swap completes.
    #[account(mut, token::mint = mint, token::authority = escrow_authority)]
    pub escrow_token_account: Account<'info, TokenAccount>,

    // The escrow authority PDA signs the transfer out of escrow.
    #[account(seeds = [b"escrow", mint.key().as_ref()], bump)]
    pub escrow_authority: AccountInfo<'info>,

    // The listing account stores the price and must be marked inactive after sale.
    #[account(mut, seeds = [b"listing", mint.key().as_ref()], bump)]
    pub listing: Account<'info, Listing>,

    // The token program handles SPL token transfers.
    pub token_program: Program<'info, Token>,

    // The system program handles SOL transfers.
    pub system_program: Program<'info, System>,

    // Rent sysvar is needed if the buyer token account must be created.
    pub rent: Sysvar<'info, Rent>,
}

// Accounts required to cancel a listing.
#[derive(Accounts)]
pub struct Cancel<'info> {
    // The seller must sign to prove they are reclaiming their own NFT.
    #[account(mut)]
    pub seller: Signer<'info>,

    // The mint identifies which NFT is being withdrawn.
    pub mint: Account<'info, Mint>,

    // The seller's token account receives the returned NFT.
    #[account(mut, token::mint = mint, token::authority = seller)]
    pub seller_token_account: Account<'info, TokenAccount>,

    // The escrow token account currently holds the NFT.
    #[account(mut, token::mint = mint, token::authority = escrow_authority)]
    pub escrow_token_account: Account<'info, TokenAccount>,

    // The escrow authority PDA signs the return transfer.
    #[account(seeds = [b"escrow", mint.key().as_ref()], bump)]
    pub escrow_authority: AccountInfo<'info>,

    // The listing account is closed after cancellation to reclaim rent.
    #[account(mut, seeds = [b"listing", mint.key().as_ref()], bump, close = seller)]
    pub listing: Account<'info, Listing>,

    // The token program handles SPL token transfers.
    pub token_program: Program<'info, Token>,
}

// The Listing account stores the minimal state needed for a marketplace entry.
#[account]
pub struct Listing {
    // The original seller who will receive proceeds minus fees.
    pub seller: Pubkey,
    // The mint address of the NFT being sold.
    pub mint: Pubkey,
    // The price in lamports that the buyer must pay.
    pub price: u64,
    // Whether the listing is still open for purchase.
    pub is_active: bool,
}

// Custom errors for clearer on-chain failure messages.
#[error_code]
pub enum ErrorCode {
    // Price must be positive to prevent accidental giveaways.
    #[msg("Price must be greater than zero")]
    PriceMustBeGreaterThanZero,
    // Only active listings can be purchased.
    #[msg("Listing is not active")]
    ListingNotActive,
    // Only the original seller can cancel a listing.
    #[msg("Unauthorized")]
    Unauthorized,
}
