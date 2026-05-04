use anchor_lang::prelude::*; // WHY: Anchor framework simplifies Solana program development with macros and boilerplate reduction.
use anchor_spl::token::{self, Mint, Token, TokenAccount, Transfer, MintTo, Burn}; // WHY: SPL token instructions are required to mint, burn, and transfer outcome shares and collateral.
use anchor_lang::solana_program::program::invoke_signed; // WHY: invoke_signed is required for CPI calls so the market program can sign on behalf of its PDA accounts.

// WHY: Declare the program ID so Anchor knows which program this code belongs to on-chain.
declare_id!("MarketProgram11111111111111111111111111111111");

// WHY: The main module groups all instructions, accounts, and errors under one program entrypoint.
#[program]
pub mod prediction_market {
    use super::*; // WHY: Brings the outer scope (imports, accounts, errors) into the program module so instructions can reference them.

    // WHY: This instruction initializes a new prediction market with YES/NO outcomes and an AMM pool.
    pub fn create_market(
        ctx: Context<CreateMarket>,
        question: String, // WHY: Stores the human-readable event description on-chain so clients can display it without off-chain indexing.
        expiration: i64, // WHY: Defines when the market is eligible for resolution, preventing premature oracle calls.
    ) -> Result<()> {
        // WHY: We enforce a maximum question length to avoid account bloat and excessive rent costs.
        require!(question.len() <= 200, MarketError::QuestionTooLong);
        // WHY: Expiration must be in the future so the market is not instantly resolvable.
        require!(expiration > Clock::get()?.unix_timestamp, MarketError::InvalidExpiration);

        let market = &mut ctx.accounts.market; // WHY: Mutably borrow the market account so we can initialize its fields.
        market.creator = ctx.accounts.creator.key(); // WHY: Record the creator so we can restrict certain admin actions or refund dust later.
        market.question = question; // WHY: Persist the question string so the market is self-describing.
        market.collateral_mint = ctx.accounts.collateral_mint.key(); // WHY: Track which token backs the shares to prevent mixing different collateral types.
        market.expiration = expiration; // WHY: Store expiration on-chain so the oracle program and AMM can reference it atomically.
        market.resolution_state = ResolutionState::Unresolved; // WHY: Markets start unresolved; this state machine prevents claims before resolution.
        market.winning_outcome = 255; // WHY: Use an invalid sentinel value (255) because no outcome index is valid yet; this catches uninitialized reads.
        market.yes_mint = ctx.accounts.yes_mint.key(); // WHY: Store the YES share mint so buy/sell/claim instructions know which token to use.
        market.no_mint = ctx.accounts.no_mint.key(); // WHY: Store the NO share mint for the same reason as YES.
        market.collateral_vault = ctx.accounts.collateral_vault.key(); // WHY: Track the vault account so we can verify collateral transfers in every instruction.
        market.yes_reserve = 0; // WHY: AMM starts with zero YES shares in the pool; LPs will seed it.
        market.no_reserve = 0; // WHY: AMM starts with zero NO shares in the pool.
        market.collateral_reserve = 0; // WHY: AMM starts with zero collateral in the pool.
        market.lp_mint = ctx.accounts.lp_mint.key(); // WHY: Track the LP token mint so liquidity instructions mint and burn the correct token.
        market.total_lp_supply = 0; // WHY: Initialize total LP supply to zero so the first deposit can set the initial price ratio.
        market.fee_bps = 30; // WHY: A 0.3% trading fee is industry standard (Uniswap) and compensates LPs without discouraging traders.
        market.bump = ctx.bumps.market; // WHY: Store the PDA bump seed so future instructions can re-derive the market address cheaply.

        // WHY: Mint an initial fixed supply of YES and NO shares to the market escrow so the AMM has inventory once liquidity is added.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]]; // WHY: Construct the PDA seeds so the market account can sign for minting via invoke_signed.
        let signer = &[&seeds[..]]; // WHY: Anchor expects a slice of seed slices for CPI signer invocation.

        // WHY: Mint 1,000,000 YES shares to the market escrow to provide deep initial liquidity and avoid division by zero.
        token::mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: Pass the token program so the runtime knows which program to invoke for SPL token operations.
                MintTo {
                    mint: ctx.accounts.yes_mint.to_account_info(), // WHY: Specify the YES mint so the runtime knows which token to create.
                    to: ctx.accounts.yes_escrow.to_account_info(), // WHY: Send minted shares to the program-owned escrow, not the creator, to maintain pool neutrality.
                    authority: ctx.accounts.market.to_account_info(), // WHY: The market PDA is the mint authority because it created the mint.
                },
                signer, // WHY: Provide the PDA seeds so the runtime can verify the market account is authorized to sign this mint.
            ),
            1_000_000, // WHY: One million shares provides granular pricing and avoids rounding to zero on small trades.
        )?;

        // WHY: Mint 1,000,000 NO shares to the market escrow so the initial YES/NO ratio is balanced.
        token::mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: Same reason as above: SPL token program is the executor.
                MintTo {
                    mint: ctx.accounts.no_mint.to_account_info(), // WHY: Specify the NO mint for this operation.
                    to: ctx.accounts.no_escrow.to_account_info(), // WHY: Send to the NO escrow account owned by the market.
                    authority: ctx.accounts.market.to_account_info(), // WHY: Market PDA is the mint authority for the NO mint as well.
                },
                signer, // WHY: PDA seeds authorize the market to sign on behalf of the mint authority.
            ),
            1_000_000, // WHY: Match the YES supply so the initial probability is 50/50 before any trading occurs.
        )?;

        Ok(()) // WHY: Return success so the runtime commits the state changes.
    }

    // WHY: Traders buy outcome shares from the AMM; this instruction handles collateral in and shares out.
    pub fn buy_shares(
        ctx: Context<BuyShares>,
        outcome_index: u8, // WHY: 0 = YES, 1 = NO; using a u8 saves space compared to a string and is easy to match on.
        collateral_amount: u64, // WHY: The trader specifies how much collateral to spend, making the UX predictable ("I want to spend 10 USDC").
    ) -> Result<()> {
        let market = &mut ctx.accounts.market; // WHY: Mutably borrow the market to update AMM reserves after the trade.
        // WHY: Trading is only allowed while the market is unresolved; once resolved, prices are meaningless.
        require!(market.resolution_state == ResolutionState::Unresolved, MarketError::MarketNotOpen);

        // WHY: Transfer the trader's collateral into the market vault so the AMM backing increases.
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                Transfer {
                    from: ctx.accounts.trader_collateral_account.to_account_info(), // WHY: Debit the trader's personal token account.
                    to: ctx.accounts.collateral_vault.to_account_info(), // WHY: Credit the market's vault account.
                    authority: ctx.accounts.trader.to_account_info(), // WHY: The trader must sign because their tokens are leaving their wallet.
                },
            ),
            collateral_amount, // WHY: Move exactly the amount the trader specified.
        )?;

        // WHY: Calculate the trading fee and deduct it from the collateral amount before computing share output.
        let fee = (collateral_amount as u128)
            .checked_mul(market.fee_bps as u128) // WHY: Use u128 for intermediate math to prevent overflow on large numbers.
            .unwrap()
            .checked_div(10000) // WHY: fee_bps is in basis points (1/100 of a percent), so divide by 10,000 to get the decimal fee.
            .unwrap() as u64; // WHY: Cast back to u64 because token amounts are u64.
        let collateral_in = collateral_amount - fee; // WHY: Only the collateral net of fees goes into the AMM pricing formula; fees stay in the vault for LPs.

        // WHY: Compute how many shares the trader receives using the constant-product formula.
        let shares_out = if outcome_index == 0 {
            // WHY: Buy YES shares: we treat the pool as collateral_reserve * yes_reserve = k.
            let k = (market.collateral_reserve as u128)
                .checked_mul(market.yes_reserve as u128) // WHY: k is the constant product; it must remain invariant before fees.
                .unwrap();
            let new_collateral = (market.collateral_reserve as u128)
                .checked_add(collateral_in as u128) // WHY: Add the trader's collateral (net of fee) to the reserve.
                .unwrap();
            let new_yes = k.checked_div(new_collateral).unwrap(); // WHY: Solve for new YES reserve: yes_new = k / collateral_new.
            let yes_out = (market.yes_reserve as u128).checked_sub(new_yes).unwrap() as u64; // WHY: Shares out = old reserve - new reserve.
            yes_out
        } else {
            // WHY: Buy NO shares using the same constant-product logic but on the NO reserve.
            let k = (market.collateral_reserve as u128)
                .checked_mul(market.no_reserve as u128)
                .unwrap();
            let new_collateral = (market.collateral_reserve as u128)
                .checked_add(collateral_in as u128)
                .unwrap();
            let new_no = k.checked_div(new_collateral).unwrap();
            let no_out = (market.no_reserve as u128).checked_sub(new_no).unwrap() as u64;
            no_out
        };

        // WHY: Reject zero-output trades because they waste gas and could be used to grief the market.
        require!(shares_out > 0, MarketError::ZeroShares);

        // WHY: Update the AMM reserves atomically so the next trade sees the new state.
        market.collateral_reserve += collateral_in; // WHY: The fee stays in the vault but is not counted in the AMM reserve because it belongs to LPs, not traders.
        if outcome_index == 0 {
            market.yes_reserve -= shares_out; // WHY: Decrease the YES reserve because shares left the pool.
        } else {
            market.no_reserve -= shares_out; // WHY: Decrease the NO reserve for the same reason.
        }

        // WHY: Transfer the computed shares from the market escrow to the trader's wallet.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]];
        let signer = &[&seeds[..]];
        let (mint, escrow) = if outcome_index == 0 {
            (ctx.accounts.yes_mint.to_account_info(), ctx.accounts.yes_escrow.to_account_info())
        } else {
            (ctx.accounts.no_mint.to_account_info(), ctx.accounts.no_escrow.to_account_info())
        };
        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                Transfer {
                    from: escrow, // WHY: Debit the program-owned escrow that holds the shares.
                    to: ctx.accounts.trader_outcome_account.to_account_info(), // WHY: Credit the trader's personal outcome token account.
                    authority: ctx.accounts.market.to_account_info(), // WHY: The market PDA is the escrow authority.
                },
                signer, // WHY: PDA seeds authorize the market to move shares out of escrow.
            ),
            shares_out, // WHY: Move exactly the amount computed by the AMM formula.
        )?;

        Ok(()) // WHY: Return success to commit the trade.
    }

    // WHY: Traders sell outcome shares back to the AMM for collateral.
    pub fn sell_shares(
        ctx: Context<SellShares>,
        outcome_index: u8, // WHY: 0 = YES, 1 = NO; same encoding as buy_shares for consistency.
        shares_amount: u64, // WHY: The trader specifies how many shares to sell, making the UX predictable.
    ) -> Result<()> {
        let market = &mut ctx.accounts.market; // WHY: Mutably borrow the market to update reserves.
        // WHY: Selling is only allowed while the market is unresolved.
        require!(market.resolution_state == ResolutionState::Unresolved, MarketError::MarketNotOpen);

        // WHY: Compute how much collateral the trader receives using the constant-product formula.
        let collateral_out = if outcome_index == 0 {
            let k = (market.collateral_reserve as u128)
                .checked_mul(market.yes_reserve as u128)
                .unwrap();
            let new_yes = (market.yes_reserve as u128)
                .checked_add(shares_amount as u128) // WHY: The pool receives YES shares, increasing the YES reserve.
                .unwrap();
            let new_collateral = k.checked_div(new_yes).unwrap(); // WHY: Solve for new collateral: collateral_new = k / yes_new.
            (market.collateral_reserve as u128).checked_sub(new_collateral).unwrap() as u64 // WHY: Collateral out = old reserve - new reserve.
        } else {
            let k = (market.collateral_reserve as u128)
                .checked_mul(market.no_reserve as u128)
                .unwrap();
            let new_no = (market.no_reserve as u128)
                .checked_add(shares_amount as u128)
                .unwrap();
            let new_collateral = k.checked_div(new_no).unwrap();
            (market.collateral_reserve as u128).checked_sub(new_collateral).unwrap() as u64
        };

        // WHY: Deduct the trading fee from the collateral output so LPs earn revenue on sells too.
        let fee = (collateral_out as u128)
            .checked_mul(market.fee_bps as u128)
            .unwrap()
            .checked_div(10000)
            .unwrap() as u64;
        let collateral_to_trader = collateral_out - fee; // WHY: The trader receives the collateral net of fees.

        // WHY: Reject trades that result in zero collateral to prevent griefing.
        require!(collateral_to_trader > 0, MarketError::ZeroCollateral);

        // WHY: Update AMM reserves: collateral decreases, outcome shares increase.
        market.collateral_reserve -= collateral_out; // WHY: We subtract the gross collateral_out because the fee portion remains in the vault for LPs.
        if outcome_index == 0 {
            market.yes_reserve += shares_amount; // WHY: Pool receives YES shares.
        } else {
            market.no_reserve += shares_amount; // WHY: Pool receives NO shares.
        }

        // WHY: Burn the trader's shares because they are being sold back to the pool and removed from circulation.
        token::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the burn.
                Burn {
                    mint: if outcome_index == 0 {
                        ctx.accounts.yes_mint.to_account_info() // WHY: Burn the YES mint if selling YES.
                    } else {
                        ctx.accounts.no_mint.to_account_info() // WHY: Burn the NO mint if selling NO.
                    },
                    from: ctx.accounts.trader_outcome_account.to_account_info(), // WHY: Debit the trader's personal token account.
                    authority: ctx.accounts.trader.to_account_info(), // WHY: The trader must sign to burn their own tokens.
                },
            ),
            shares_amount, // WHY: Burn exactly the amount the trader specified.
        )?;

        // WHY: Transfer collateral from the market vault to the trader.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]];
        let signer = &[&seeds[..]];
        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                Transfer {
                    from: ctx.accounts.collateral_vault.to_account_info(), // WHY: Debit the market vault.
                    to: ctx.accounts.trader_collateral_account.to_account_info(), // WHY: Credit the trader's wallet.
                    authority: ctx.accounts.market.to_account_info(), // WHY: The market PDA owns the vault and must authorize the transfer.
                },
                signer, // WHY: PDA seeds allow the program to sign for the vault authority.
            ),
            collateral_to_trader, // WHY: Send exactly the computed amount net of fees.
        )?;

        Ok(()) // WHY: Return success to commit the state changes.
    }

    // WHY: This instruction resolves the market by calling the oracle program and updating the market state.
    pub fn resolve_market(
        ctx: Context<ResolveMarket>,
        outcome_index: u8, // WHY: The oracle reports which outcome won (0 or 1).
    ) -> Result<()> {
        let market = &mut ctx.accounts.market; // WHY: Mutably borrow to transition state and record the winner.
        // WHY: Only unresolved markets can be resolved; prevents double-resolution.
        require!(market.resolution_state == ResolutionState::Unresolved, MarketError::AlreadyResolved);
        // WHY: Ensure the market has expired before allowing resolution.
        require!(Clock::get()?.unix_timestamp >= market.expiration, MarketError::NotExpired);

        // WHY: Call the oracle program via CPI to verify that the signer is a trusted oracle and the resolution is valid.
        let oracle_program = ctx.accounts.oracle_program.to_account_info(); // WHY: We need the oracle program ID to construct the CPI call.
        let oracle_ix = oracle::instruction::Resolve { // WHY: Build the oracle resolution instruction payload.
            market_key: market.key(), // WHY: Pass the market address so the oracle can log which market is being resolved.
            outcome: outcome_index, // WHY: Pass the winning outcome so the oracle can validate and record it.
        };
        let oracle_accounts = oracle::cpi::accounts::Resolve { // WHY: Define the accounts the oracle instruction expects.
            oracle: ctx.accounts.oracle.to_account_info(), // WHY: The oracle account stores trusted signers and dispute state.
            authority: ctx.accounts.oracle_authority.to_account_info(), // WHY: The oracle authority must sign the resolution.
            system_program: ctx.accounts.system_program.to_account_info(), // WHY: The oracle may need to create accounts during resolution.
        };
        let cpi_ctx = CpiContext::new(oracle_program, oracle_accounts); // WHY: Wrap the program and accounts into a CPI context.
        oracle::cpi::resolve(cpi_ctx, oracle_ix.market_key, oracle_ix.outcome)?; // WHY: Execute the CPI; if the oracle rejects the resolution, this transaction fails atomically.

        // WHY: Update market state only after the oracle CPI succeeds.
        market.resolution_state = ResolutionState::Resolved; // WHY: Transition to Resolved so claim instructions are now allowed.
        market.winning_outcome = outcome_index; // WHY: Record the winner so claim instructions know which shares are valuable.

        Ok(()) // WHY: Return success to commit resolution.
    }

    // WHY: Winning shareholders burn their shares to receive collateral after resolution.
    pub fn claim_winnings(ctx: Context<ClaimWinnings>) -> Result<()> {
        let market = &ctx.accounts.market; // WHY: Immutably borrow because we only read state; no need to update the market after resolution.
        // WHY: Claims are only allowed after resolution.
        require!(market.resolution_state == ResolutionState::Resolved, MarketError::NotResolved);

        // WHY: Determine which outcome the trader is holding by checking the mint of their token account.
        let is_winning = if ctx.accounts.trader_outcome_account.mint == market.yes_mint {
            market.winning_outcome == 0 // WHY: YES is index 0.
        } else if ctx.accounts.trader_outcome_account.mint == market.no_mint {
            market.winning_outcome == 1 // WHY: NO is index 1.
        } else {
            return err!(MarketError::InvalidOutcomeMint); // WHY: Reject claims from unrelated token accounts.
        };
        // WHY: Only winning shares have value; losers receive nothing.
        require!(is_winning, MarketError::NotWinningShare);

        let shares = ctx.accounts.trader_outcome_account.amount; // WHY: Read the trader's balance so we know how much collateral to pay out.
        // WHY: One share pays exactly one unit of collateral because the market was fully collateralized at creation.
        let payout = shares;

        // WHY: Burn the trader's winning shares so the claim cannot be repeated.
        token::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the burn.
                Burn {
                    mint: ctx.accounts.outcome_mint.to_account_info(), // WHY: Burn the specific outcome mint (YES or NO).
                    from: ctx.accounts.trader_outcome_account.to_account_info(), // WHY: Debit the trader's token account.
                    authority: ctx.accounts.trader.to_account_info(), // WHY: The trader must sign to destroy their own tokens.
                },
            ),
            shares, // WHY: Burn the entire balance; partial claims are not supported to keep the logic simple.
        )?;

        // WHY: Transfer the payout collateral from the market vault to the trader.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]];
        let signer = &[&seeds[..]];
        token::transfer(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                Transfer {
                    from: ctx.accounts.collateral_vault.to_account_info(), // WHY: Debit the market vault.
                    to: ctx.accounts.trader_collateral_account.to_account_info(), // WHY: Credit the trader's wallet.
                    authority: ctx.accounts.market.to_account_info(), // WHY: The market PDA owns the vault.
                },
                signer, // WHY: PDA seeds authorize the transfer.
            ),
            payout, // WHY: Pay exactly one collateral per share.
        )?;

        Ok(()) // WHY: Return success to finalize the payout.
    }

    // WHY: Liquidity providers deposit collateral and receive LP tokens representing their share of the AMM pool.
    pub fn provide_liquidity(
        ctx: Context<ProvideLiquidity>,
        collateral_amount: u64, // WHY: The provider specifies how much collateral to deposit.
    ) -> Result<()> {
        let market = &mut ctx.accounts.market; // WHY: Mutably borrow to update reserves and LP supply.
        // WHY: Liquidity can only be added to unresolved markets because once resolved, the pool no longer needs trading liquidity.
        require!(market.resolution_state == ResolutionState::Unresolved, MarketError::MarketNotOpen);

        // WHY: Transfer the provider's collateral into the market vault.
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                Transfer {
                    from: ctx.accounts.provider_collateral_account.to_account_info(), // WHY: Debit the provider's wallet.
                    to: ctx.accounts.collateral_vault.to_account_info(), // WHY: Credit the market vault.
                    authority: ctx.accounts.provider.to_account_info(), // WHY: The provider must sign.
                },
            ),
            collateral_amount, // WHY: Move exactly the specified amount.
        )?;

        // WHY: Calculate LP tokens to mint. If this is the first deposit, LP tokens equal the collateral amount.
        let lp_tokens = if market.total_lp_supply == 0 {
            collateral_amount // WHY: Initial deposit sets the baseline: 1 LP token = 1 collateral unit.
        } else {
            // WHY: Subsequent deposits are proportional to the provider's contribution relative to total pool value.
            // WHY: Pool value = collateral_reserve + yes_reserve + no_reserve (assuming 1 share = 1 collateral in a balanced pool).
            let pool_value = (market.collateral_reserve as u128)
                .checked_add(market.yes_reserve as u128)
                .unwrap()
                .checked_add(market.no_reserve as u128)
                .unwrap();
            (collateral_amount as u128)
                .checked_mul(market.total_lp_supply as u128) // WHY: LP tokens = (deposit * total_lp) / pool_value.
                .unwrap()
                .checked_div(pool_value)
                .unwrap() as u64
        };

        // WHY: Reject tiny deposits that mint zero LP tokens, which would steal value from existing LPs.
        require!(lp_tokens > 0, MarketError::ZeroLpTokens);

        // WHY: Update market reserves and LP supply.
        market.collateral_reserve += collateral_amount; // WHY: The deposited collateral becomes part of the AMM reserve.
        market.total_lp_supply += lp_tokens; // WHY: Increase total LP supply so future deposits calculate proportions correctly.

        // WHY: Mint LP tokens to the provider's wallet.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]];
        let signer = &[&seeds[..]];
        token::mint_to(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the mint.
                MintTo {
                    mint: ctx.accounts.lp_mint.to_account_info(), // WHY: Mint the LP token.
                    to: ctx.accounts.provider_lp_account.to_account_info(), // WHY: Send to the provider's LP token account.
                    authority: ctx.accounts.market.to_account_info(), // WHY: The market PDA is the LP mint authority.
                },
                signer, // WHY: PDA seeds authorize the mint.
            ),
            lp_tokens, // WHY: Mint exactly the computed amount.
        )?;

        Ok(()) // WHY: Return success to commit the liquidity addition.
    }

    // WHY: Liquidity providers burn LP tokens to withdraw their proportional share of the pool.
    pub fn remove_liquidity(
        ctx: Context<RemoveLiquidity>,
        lp_amount: u64, // WHY: The provider specifies how many LP tokens to burn.
    ) -> Result<()> {
        let market = &mut ctx.accounts.market; // WHY: Mutably borrow to update reserves and LP supply.
        // WHY: Liquidity removal is allowed even after resolution so LPs can exit and redeem their mixed assets.

        // WHY: Reject attempts to burn more LP tokens than the provider owns.
        require!(ctx.accounts.provider_lp_account.amount >= lp_amount, MarketError::InsufficientLpTokens);

        // WHY: Calculate the provider's share of each reserve based on their LP proportion.
        let share_ratio = (lp_amount as u128)
            .checked_mul(1_000_000) // WHY: Use a large scalar to preserve precision during integer division.
            .unwrap()
            .checked_div(market.total_lp_supply as u128) // WHY: share_ratio = lp_amount / total_lp_supply (scaled).
            .unwrap();

        let collateral_out = ((market.collateral_reserve as u128)
            .checked_mul(share_ratio)
            .unwrap()
            .checked_div(1_000_000)
            .unwrap()) as u64; // WHY: Unscale to get the actual collateral amount.
        let yes_out = ((market.yes_reserve as u128)
            .checked_mul(share_ratio)
            .unwrap()
            .checked_div(1_000_000)
            .unwrap()) as u64;
        let no_out = ((market.no_reserve as u128)
            .checked_mul(share_ratio)
            .unwrap()
            .checked_div(1_000_000)
            .unwrap()) as u64;

        // WHY: Update reserves atomically so the next instruction sees the reduced pool.
        market.collateral_reserve -= collateral_out;
        market.yes_reserve -= yes_out;
        market.no_reserve -= no_out;
        market.total_lp_supply -= lp_amount; // WHY: Reduce total LP supply so future withdrawals calculate correctly.

        // WHY: Burn the provider's LP tokens because they are cashing out their claim.
        token::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the burn.
                Burn {
                    mint: ctx.accounts.lp_mint.to_account_info(), // WHY: Burn the LP token mint.
                    from: ctx.accounts.provider_lp_account.to_account_info(), // WHY: Debit the provider's LP account.
                    authority: ctx.accounts.provider.to_account_info(), // WHY: The provider must sign to burn their own tokens.
                },
            ),
            lp_amount, // WHY: Burn exactly the amount specified.
        )?;

        // WHY: Transfer the provider's share of collateral from the vault to their wallet.
        let seeds = &[b"market", market.creator.as_ref(), &[market.bump]];
        let signer = &[&seeds[..]];
        if collateral_out > 0 {
            token::transfer(
                CpiContext::new_with_signer(
                    ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                    Transfer {
                        from: ctx.accounts.collateral_vault.to_account_info(), // WHY: Debit the market vault.
                        to: ctx.accounts.provider_collateral_account.to_account_info(), // WHY: Credit the provider's wallet.
                        authority: ctx.accounts.market.to_account_info(), // WHY: Market PDA owns the vault.
                    },
                    signer, // WHY: PDA seeds authorize the transfer.
                ),
                collateral_out, // WHY: Send exactly the computed collateral share.
            )?;
        }

        // WHY: Transfer the provider's share of YES shares from escrow to their wallet.
        if yes_out > 0 {
            token::transfer(
                CpiContext::new_with_signer(
                    ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                    Transfer {
                        from: ctx.accounts.yes_escrow.to_account_info(), // WHY: Debit the YES escrow.
                        to: ctx.accounts.provider_yes_account.to_account_info(), // WHY: Credit the provider's YES wallet.
                        authority: ctx.accounts.market.to_account_info(), // WHY: Market PDA is the escrow authority.
                    },
                    signer, // WHY: PDA seeds authorize the transfer.
                ),
                yes_out, // WHY: Send exactly the computed YES share.
            )?;
        }

        // WHY: Transfer the provider's share of NO shares from escrow to their wallet.
        if no_out > 0 {
            token::transfer(
                CpiContext::new_with_signer(
                    ctx.accounts.token_program.to_account_info(), // WHY: SPL token program executes the transfer.
                    Transfer {
                        from: ctx.accounts.no_escrow.to_account_info(), // WHY: Debit the NO escrow.
                        to: ctx.accounts.provider_no_account.to_account_info(), // WHY: Credit the provider's NO wallet.
                        authority: ctx.accounts.market.to_account_info(), // WHY: Market PDA is the escrow authority.
                    },
                    signer, // WHY: PDA seeds authorize the transfer.
                ),
                no_out, // WHY: Send exactly the computed NO share.
            )?;
        }

        Ok(()) // WHY: Return success to commit the liquidity removal.
    }
}

// WHY: Define the account validation struct for creating a market.
#[derive(Accounts)]
#[instruction(question: String, expiration: i64)] // WHY: Include instruction args so the init seeds can reference them for unique PDA derivation.
pub struct CreateMarket<'info> {
    #[account(mut)] // WHY: The creator must be mutable because they pay for account rent.
    pub creator: Signer<'info>, // WHY: The creator signs and pays; we need a known payer to fund new accounts.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the market account.
        space = 8 + Market::LEN, // WHY: 8 bytes for Anchor discriminator plus the serialized market data.
        seeds = [b"market", creator.key().as_ref()], // WHY: Derive a deterministic PDA from the creator so clients can find the market without an index.
        bump // WHY: Anchor computes and stores the canonical bump so we can re-derive the address later.
    )]
    pub market: Account<'info, Market>, // WHY: The market account holds all global state for this prediction event.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the YES mint.
        seeds = [b"yes_mint", market.key().as_ref()], // WHY: Derive the YES mint from the market so the relationship is deterministic.
        bump,
        mint::decimals = 6, // WHY: Use 6 decimals to match USDC for intuitive pricing (1 share = 1 USDC).
        mint::authority = market, // WHY: The market PDA must be the mint authority so it can mint and burn shares programmatically.
    )]
    pub yes_mint: Account<'info, Mint>, // WHY: This is the SPL token mint for YES outcome shares.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the NO mint.
        seeds = [b"no_mint", market.key().as_ref()], // WHY: Derive the NO mint from the market for deterministic discovery.
        bump,
        mint::decimals = 6,
        mint::authority = market,
    )]
    pub no_mint: Account<'info, Mint>, // WHY: This is the SPL token mint for NO outcome shares.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the LP mint.
        seeds = [b"lp_mint", market.key().as_ref()], // WHY: Derive the LP mint from the market for deterministic discovery.
        bump,
        mint::decimals = 6,
        mint::authority = market,
    )]
    pub lp_mint: Account<'info, Mint>, // WHY: This mint represents ownership in the AMM liquidity pool.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the collateral vault.
        seeds = [b"collateral_vault", market.key().as_ref()], // WHY: Derive the vault from the market so any instruction can verify it.
        bump,
        token::mint = collateral_mint, // WHY: The vault must hold the specified collateral token, not arbitrary tokens.
        token::authority = market, // WHY: The market PDA must control the vault so it can move collateral programmatically.
    )]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: This account holds all collateral backing the shares.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the YES escrow.
        seeds = [b"yes_escrow", market.key().as_ref()], // WHY: Derive the escrow from the market.
        bump,
        token::mint = yes_mint, // WHY: The escrow must hold YES shares.
        token::authority = market, // WHY: The market PDA controls the escrow.
    )]
    pub yes_escrow: Account<'info, TokenAccount>, // WHY: This account holds YES shares owned by the AMM.

    #[account(
        init,
        payer = creator, // WHY: The creator pays rent for the NO escrow.
        seeds = [b"no_escrow", market.key().as_ref()], // WHY: Derive the escrow from the market.
        bump,
        token::mint = no_mint,
        token::authority = market,
    )]
    pub no_escrow: Account<'info, TokenAccount>, // WHY: This account holds NO shares owned by the AMM.

    pub collateral_mint: Account<'info, Mint>, // WHY: Passed so the vault can be validated against the correct mint.

    pub token_program: Program<'info, Token>, // WHY: Required for all SPL token CPI instructions.
    pub system_program: Program<'info, System>, // WHY: Required for account creation (init).
    pub rent: Sysvar<'info, Rent>, // WHY: Required by Anchor when creating accounts to calculate rent exemption.
}

// WHY: Define the account validation struct for buying shares.
#[derive(Accounts)]
pub struct BuyShares<'info> {
    #[account(mut)]
    pub trader: Signer<'info>, // WHY: The trader signs to authorize spending their collateral.

    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Mutably borrowed to update AMM reserves.

    #[account(mut)]
    pub trader_collateral_account: Account<'info, TokenAccount>, // WHY: The trader's USDC account; must be mutable because it is debited.

    #[account(mut)]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: The market vault; must be mutable because it is credited.

    #[account(mut)]
    pub trader_outcome_account: Account<'info, TokenAccount>, // WHY: The trader's YES or NO token account; must be mutable because it is credited.

    #[account(mut)]
    pub yes_escrow: Account<'info, TokenAccount>, // WHY: May be debited if buying YES shares.

    #[account(mut)]
    pub no_escrow: Account<'info, TokenAccount>, // WHY: May be debited if buying NO shares.

    #[account(mut)]
    pub yes_mint: Account<'info, Mint>, // WHY: Referenced to validate the escrow and outcome accounts.

    #[account(mut)]
    pub no_mint: Account<'info, Mint>, // WHY: Referenced to validate the escrow and outcome accounts.

    pub token_program: Program<'info, Token>, // WHY: Required for SPL transfer instructions.
}

// WHY: Define the account validation struct for selling shares.
#[derive(Accounts)]
pub struct SellShares<'info> {
    #[account(mut)]
    pub trader: Signer<'info>, // WHY: The trader signs to authorize burning their shares.

    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Mutably borrowed to update AMM reserves.

    #[account(mut)]
    pub trader_outcome_account: Account<'info, TokenAccount>, // WHY: Debited (burned) during the sale.

    #[account(mut)]
    pub yes_mint: Account<'info, Mint>, // WHY: Referenced for burning YES shares.

    #[account(mut)]
    pub no_mint: Account<'info, Mint>, // WHY: Referenced for burning NO shares.

    #[account(mut)]
    pub trader_collateral_account: Account<'info, TokenAccount>, // WHY: Credited with collateral proceeds.

    #[account(mut)]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: Debited to pay the trader.

    pub token_program: Program<'info, Token>, // WHY: Required for SPL burn and transfer instructions.
}

// WHY: Define the account validation struct for resolving a market.
#[derive(Accounts)]
pub struct ResolveMarket<'info> {
    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Mutably borrowed to transition state and record the winner.

    /// CHECK: We only need the program ID for CPI; Anchor verifies it is executable.
    pub oracle_program: AccountInfo<'info>, // WHY: This is the oracle program we will invoke via CPI.

    /// CHECK: Oracle account is validated by the oracle program during CPI.
    #[account(mut)]
    pub oracle: AccountInfo<'info>, // WHY: The oracle account stores trusted signers and resolution state.

    pub oracle_authority: Signer<'info>, // WHY: The oracle authority must sign to prove the resolution is authorized.

    pub system_program: Program<'info, System>, // WHY: The oracle may create accounts during resolution.
}

// WHY: Define the account validation struct for claiming winnings.
#[derive(Accounts)]
pub struct ClaimWinnings<'info> {
    #[account(mut)]
    pub trader: Signer<'info>, // WHY: The trader signs to authorize burning their shares.

    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Read-only to check resolution state and winning outcome.

    #[account(mut)]
    pub trader_outcome_account: Account<'info, TokenAccount>, // WHY: Debited (burned) during the claim.

    #[account(mut)]
    pub outcome_mint: Account<'info, Mint>, // WHY: The mint of the shares being burned.

    #[account(mut)]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: Debited to pay the trader.

    #[account(mut)]
    pub trader_collateral_account: Account<'info, TokenAccount>, // WHY: Credited with the payout.

    pub token_program: Program<'info, Token>, // WHY: Required for SPL burn and transfer instructions.
}

// WHY: Define the account validation struct for providing liquidity.
#[derive(Accounts)]
pub struct ProvideLiquidity<'info> {
    #[account(mut)]
    pub provider: Signer<'info>, // WHY: The provider signs to authorize depositing their collateral.

    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Mutably borrowed to update reserves and LP supply.

    #[account(mut)]
    pub provider_collateral_account: Account<'info, TokenAccount>, // WHY: Debited for the deposit.

    #[account(mut)]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: Credited with the deposit.

    #[account(mut)]
    pub provider_lp_account: Account<'info, TokenAccount>, // WHY: Credited with newly minted LP tokens.

    #[account(mut)]
    pub lp_mint: Account<'info, Mint>, // WHY: Referenced to mint LP tokens.

    pub token_program: Program<'info, Token>, // WHY: Required for SPL transfer and mint instructions.
}

// WHY: Define the account validation struct for removing liquidity.
#[derive(Accounts)]
pub struct RemoveLiquidity<'info> {
    #[account(mut)]
    pub provider: Signer<'info>, // WHY: The provider signs to authorize burning their LP tokens.

    #[account(mut)]
    pub market: Account<'info, Market>, // WHY: Mutably borrowed to update reserves and LP supply.

    #[account(mut)]
    pub provider_lp_account: Account<'info, TokenAccount>, // WHY: Debited (burned) during removal.

    #[account(mut)]
    pub lp_mint: Account<'info, Mint>, // WHY: Referenced to burn LP tokens.

    #[account(mut)]
    pub provider_collateral_account: Account<'info, TokenAccount>, // WHY: Credited with collateral share.

    #[account(mut)]
    pub collateral_vault: Account<'info, TokenAccount>, // WHY: Debited to pay collateral share.

    #[account(mut)]
    pub provider_yes_account: Account<'info, TokenAccount>, // WHY: Credited with YES share.

    #[account(mut)]
    pub yes_escrow: Account<'info, TokenAccount>, // WHY: Debited to pay YES share.

    #[account(mut)]
    pub provider_no_account: Account<'info, TokenAccount>, // WHY: Credited with NO share.

    #[account(mut)]
    pub no_escrow: Account<'info, TokenAccount>, // WHY: Debited to pay NO share.

    pub token_program: Program<'info, Token>, // WHY: Required for SPL burn and transfer instructions.
}

// WHY: The Market account stores all global state for a prediction market.
#[account]
pub struct Market {
    pub creator: Pubkey, // WHY: Identifies who created the market for admin and refund purposes.
    pub question: String, // WHY: Human-readable description stored on-chain for client display.
    pub collateral_mint: Pubkey, // WHY: Identifies the token that backs all shares.
    pub expiration: i64, // WHY: Unix timestamp after which resolution is allowed.
    pub resolution_state: ResolutionState, // WHY: State machine controlling whether trading, resolution, or claiming is allowed.
    pub winning_outcome: u8, // WHY: Index of the winning outcome after resolution (0 = YES, 1 = NO).
    pub yes_mint: Pubkey, // WHY: Identifies the YES share token.
    pub no_mint: Pubkey, // WHY: Identifies the NO share token.
    pub collateral_vault: Pubkey, // WHY: Identifies the account holding all collateral.
    pub yes_reserve: u64, // WHY: AMM reserve of YES shares used for constant-product pricing.
    pub no_reserve: u64, // WHY: AMM reserve of NO shares used for constant-product pricing.
    pub collateral_reserve: u64, // WHY: AMM reserve of collateral used for constant-product pricing.
    pub lp_mint: Pubkey, // WHY: Identifies the LP token.
    pub total_lp_supply: u64, // WHY: Tracks total LP tokens so withdrawal proportions are correct.
    pub fee_bps: u16, // WHY: Trading fee in basis points; stored per market to allow customization.
    pub bump: u8, // WHY: PDA bump seed for re-deriving the market address.
}

// WHY: Implement a helper to compute the serialized size of the Market account for rent calculation.
impl Market {
    pub const LEN: usize = 32 // creator
        + 4 + 200 // question: 4 bytes length prefix + max 200 chars
        + 32 // collateral_mint
        + 8 // expiration
        + 1 // resolution_state
        + 1 // winning_outcome
        + 32 // yes_mint
        + 32 // no_mint
        + 32 // collateral_vault
        + 8 // yes_reserve
        + 8 // no_reserve
        + 8 // collateral_reserve
        + 32 // lp_mint
        + 8 // total_lp_supply
        + 2 // fee_bps
        + 1; // bump
}

// WHY: Define the resolution state machine to enforce valid lifecycle transitions.
#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum ResolutionState {
    Unresolved, // WHY: Initial state; trading and liquidity provision are allowed.
    Resolving,  // WHY: Optional intermediate state if a dispute period is active (used by oracle program).
    Resolved,   // WHY: Final state; only claims and liquidity removal are allowed.
}

// WHY: Define custom errors so clients can distinguish failure modes without parsing logs.
#[error_code]
pub enum MarketError {
    #[msg("Question too long")]
    QuestionTooLong, // WHY: Prevents account bloat and excessive rent.
    #[msg("Invalid expiration")]
    InvalidExpiration, // WHY: Prevents creating markets that expire in the past.
    #[msg("Market not open")]
    MarketNotOpen, // WHY: Prevents trading on resolved or expired markets.
    #[msg("Already resolved")]
    AlreadyResolved, // WHY: Prevents double-resolution.
    #[msg("Not expired")]
    NotExpired, // WHY: Prevents premature resolution.
    #[msg("Not resolved")]
    NotResolved, // WHY: Prevents claims before resolution.
    #[msg("Invalid outcome mint")]
    InvalidOutcomeMint, // WHY: Prevents claims with unrelated tokens.
    #[msg("Not a winning share")]
    NotWinningShare, // WHY: Prevents redeeming losing shares.
    #[msg("Zero shares output")]
    ZeroShares, // WHY: Prevents useless trades.
    #[msg("Zero collateral output")]
    ZeroCollateral, // WHY: Prevents useless trades.
    #[msg("Zero LP tokens minted")]
    ZeroLpTokens, // WHY: Prevents value dilution from tiny deposits.
    #[msg("Insufficient LP tokens")]
    InsufficientLpTokens, // WHY: Prevents burning more than owned.
}
