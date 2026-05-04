use anchor_lang::prelude::*;
use anchor_spl::token::{self, Mint, Token, TokenAccount};
use mpl_token_metadata::state::DataV2;
use mpl_token_metadata::instruction::{create_metadata_accounts_v3};

// Declare the program ID so Solana knows which deployed program this code belongs to.
declare_id!("NFTMint1111111111111111111111111111111111111");

// Define the program module that contains all instruction handlers.
#[program]
pub mod nft_mint {
    use super::*;

    // The mint_nft instruction creates a new NFT with metadata attached.
    pub fn mint_nft(
        ctx: Context<MintNft>,
        name: String,
        symbol: String,
        uri: String,
    ) -> Result<()> {
        // Verify the provided name is not empty so wallets can display the NFT properly.
        require!(!name.is_empty(), ErrorCode::NameRequired);
        // Verify the URI is not empty so metadata can be fetched by explorers and wallets.
        require!(!uri.is_empty(), ErrorCode::UriRequired);

        // Mint exactly one token because NFTs by definition have a supply of one.
        let cpi_accounts = token::MintTo {
            mint: ctx.accounts.mint.to_account_info(),
            to: ctx.accounts.token_account.to_account_info(),
            authority: ctx.accounts.mint_authority.to_account_info(),
        };
        // Use the token program to perform the cross-program invocation safely.
        let cpi_program = ctx.accounts.token_program.to_account_info();
        // Create the CPI context to pass signer seeds if needed.
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        // Execute the mint instruction to create the single token representing ownership.
        token::mint_to(cpi_ctx, 1)?;

        // Build the metadata data struct expected by Metaplex Token Metadata program.
        let data_v2 = DataV2 {
            name: name.clone(),
            symbol: symbol.clone(),
            uri: uri.clone(),
            seller_fee_basis_points: 500, // 5% royalty for secondary sales to support creators.
            creators: None,               // Simplified: no verified creators list in this demo.
            collection: None,             // Simplified: not part of a certified collection.
            uses: None,                   // Simplified: no usage limits on this NFT.
        };

        // Prepare the instruction to create the on-chain Metaplex metadata account.
        let create_metadata_ix = create_metadata_accounts_v3(
            mpl_token_metadata::ID,                  // Metaplex program ID target.
            ctx.accounts.metadata_account.key(),     // The metadata account to initialize.
            ctx.accounts.mint.key(),                 // The mint this metadata describes.
            ctx.accounts.mint_authority.key(),       // Authority that can update metadata.
            ctx.accounts.payer.key(),                // Account paying rent for metadata account.
            ctx.accounts.payer.key(),                // Update authority for metadata.
            data_v2.name,                            // Pass the name into the instruction.
            data_v2.symbol,                          // Pass the symbol into the instruction.
            data_v2.uri,                             // Pass the URI into the instruction.
            Some(ctx.accounts.mint_authority.key()), // Creator verified flag placeholder.
            data_v2.seller_fee_basis_points,         // Royalty percentage in basis points.
            true,  // is_mutable: allow updates initially so creators can fix errors.
            true,  // update_authority_is_signer: require signature for metadata changes.
            None,  // collection_details: no collection size tracking for this simple NFT.
            None,  // uses: no usage constraints.
            None,  // collection: no parent collection.
        );

        // Execute the Metaplex metadata creation via cross-program invocation.
        anchor_lang::solana_program::program::invoke(
            &create_metadata_ix,
            &[
                ctx.accounts.metadata_account.to_account_info(),
                ctx.accounts.mint.to_account_info(),
                ctx.accounts.mint_authority.to_account_info(),
                ctx.accounts.payer.to_account_info(),
                ctx.accounts.token_metadata_program.to_account_info(),
                ctx.accounts.system_program.to_account_info(),
                ctx.accounts.rent.to_account_info(),
            ],
        )?;

        // Freeze mint authority so no additional tokens can ever be minted, enforcing scarcity.
        let freeze_accounts = token::SetAuthority {
            current_authority: ctx.accounts.mint_authority.to_account_info(),
            account_or_mint: ctx.accounts.mint.to_account_info(),
        };
        let freeze_ctx = CpiContext::new(ctx.accounts.token_program.to_account_info(), freeze_accounts);
        token::set_authority(freeze_ctx, token::spl_token::instruction::AuthorityType::MintTokens, None)?;

        // Return Ok to signal the instruction completed successfully.
        Ok(())
    }
}

// Define the accounts required by the mint_nft instruction.
#[derive(Accounts)]
pub struct MintNft<'info> {
    // The mint account must be initialized and owned by the token program.
    #[account(
        init,
        payer = payer,
        mint::decimals = 0,           // NFTs must have zero decimals because they are indivisible.
        mint::authority = mint_authority, // Only mint_authority can create new tokens.
    )]
    pub mint: Account<'info, Mint>,

    // The token account holds the minted NFT for the owner.
    #[account(
        init,
        payer = payer,
        token::mint = mint,           // Must match the mint we just created.
        token::authority = payer,     // The payer will own this token account.
    )]
    pub token_account: Account<'info, TokenAccount>,

    // The metadata account stores the Metaplex metadata for this NFT.
    #[account(mut)]
    pub metadata_account: UncheckedAccount<'info>,

    // The payer funds all account creation rent and transaction fees.
    #[account(mut)]
    pub payer: Signer<'info>,

    // The mint authority signs the mint operation and freeze.
    pub mint_authority: Signer<'info>,

    // The official Metaplex Token Metadata program ID.
    pub token_metadata_program: Program<'info, Token>,

    // The Solana Token program is needed for mint_to and set_authority calls.
    pub token_program: Program<'info, Token>,

    // The system program is required for account creation and rent payments.
    pub system_program: Program<'info, System>,

    // The rent sysvar is needed when creating accounts with rent exemption.
    pub rent: Sysvar<'info, Rent>,
}

// Define custom error codes for clearer debugging when preconditions fail.
#[error_code]
pub enum ErrorCode {
    // Returned when the user tries to mint an NFT without providing a name.
    #[msg("NFT name is required")]
    NameRequired,
    // Returned when the user tries to mint an NFT without providing a metadata URI.
    #[msg("Metadata URI is required")]
    UriRequired,
}
