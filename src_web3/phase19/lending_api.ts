import express, { Request, Response } from 'express'; // Import Express framework to build the REST API server

/**
 * Phase 19: Lending Protocol API
 *
 * REST API for collateralized lending:
 * POST /lend/market/create - Create lending market
 * POST /lend/deposit - Deposit collateral
 * POST /lend/borrow - Borrow against collateral
 * POST /lend/repay - Repay loan
 * POST /lend/liquidate - Liquidate unhealthy position
 * GET /lend/position/:pubkey - Get user position
 */

const app = express(); // Create the Express application instance to handle HTTP routing
app.use(express.json()); // Enable automatic JSON body parsing so req.body contains parsed objects

const PORT = 3007; // Choose port 3007 to avoid conflicts with other phase APIs running locally

// ============================================================================
// TYPES
// ============================================================================

interface LendingMarket { // Define the TypeScript shape of a lending market
    id: string; // Unique identifier for the market
    collateralToken: string; // Symbol or mint address of the accepted collateral
    borrowToken: string; // Symbol or mint address of the token being lent
    ltvRatio: number; // Maximum loan-to-value ratio as a percentage
    liquidationThreshold: number; // Collateral ratio percentage below which liquidation is allowed
    totalCollateral: number; // Sum of all collateral deposited across users
    totalDebt: number; // Sum of all debt borrowed across users
    collateralPrice: number; // Current dollar price of one unit of collateral
}

interface UserPosition { // Define the TypeScript shape of a borrower's position
    pubkey: string; // User's public key
    collateral: number; // Amount of collateral tokens deposited
    debt: number; // Amount of borrowed tokens currently owed
    collateralValue: number; // Cached dollar value of the deposited collateral
    healthFactor: number; // Computed safety ratio; below 1 means liquidatable
}

// ============================================================================
// STORAGE
// ============================================================================

const markets: Map<string, LendingMarket> = new Map(); // Store lending markets in memory using a Map
const positions: Map<string, UserPosition> = new Map(); // Store user positions in memory using a Map keyed by "marketId:pubkey"

// ============================================================================
// HELPERS
// ============================================================================

function getPositionKey(marketId: string, pubkey: string): string { // Generate a composite key to uniquely identify a position
    return `${marketId}:${pubkey}`; // Concatenate market and user to avoid collisions across markets
} // Close the helper

function calculateHealthFactor(collateralValue: number, debt: number, liquidationThreshold: number): number { // Compute the standardized health factor
    if (debt === 0) { // Avoid division by zero for debt-free positions
        return Number.MAX_VALUE; // Return infinity because a debt-free position is perfectly safe
    } // Close the zero-debt guard
    return (collateralValue * (liquidationThreshold / 100)) / debt; // Apply the threshold to collateral value and divide by debt
} // Close the health factor helper

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => { // Define a health check route for monitoring
    res.json({ status: 'healthy', markets: markets.size }); // Respond with the count of active markets
}); // Close the health route

/**
 * POST /lend/market/create
 * Create a lending market
 */
app.post('/lend/market/create', (req: Request, res: Response) => { // Define the endpoint to initialize a lending market
    try { // Wrap in try/catch to handle malformed input gracefully
        const { collateralToken, borrowToken, ltvRatio, liquidationThreshold, collateralPrice } = req.body; // Extract market parameters

        if (!collateralToken || !borrowToken || !ltvRatio || !liquidationThreshold) { // Validate required fields
            return res.status(400).json({ error: 'Missing parameters' }); // Return 400 for incomplete requests
        } // Close validation

        const id = `lend_${collateralToken.slice(0, 8)}_${borrowToken.slice(0, 8)}`; // Generate a readable market ID

        if (markets.has(id)) { // Prevent duplicate markets for the same pair
            return res.status(409).json({ error: 'Market already exists' }); // Return 409 for duplicate resources
        } // Close duplicate check

        const market: LendingMarket = { // Construct the market object
            id, // Assign the generated ID
            collateralToken, // Store the accepted collateral token
            borrowToken, // Store the borrowable token
            ltvRatio, // Store the maximum LTV percentage
            liquidationThreshold, // Store the liquidation trigger percentage
            totalCollateral: 0, // Initialize global collateral to zero
            totalDebt: 0, // Initialize global debt to zero
            collateralPrice: collateralPrice || 2000, // Default collateral price to 2000 if not provided
        }; // Close market construction

        markets.set(id, market); // Save the market into memory

        res.status(201).json({ // Respond with 201 Created
            success: true, // Signal success explicitly
            market: { // Nest market details under a clear key
                id, // Echo back the ID
                collateralToken, // Show the collateral token
                borrowToken, // Show the borrow token
                ltvRatio: `${ltvRatio}%`, // Format LTV as a percentage
                liquidationThreshold: `${liquidationThreshold}%`, // Format threshold as a percentage
                collateralPrice: market.collateralPrice, // Show the current collateral price
            }, // Close market detail group
        }); // Close response
    } catch (error) { // Catch unexpected exceptions
        res.status(500).json({ error: `Failed to create market: ${error}` }); // Return 500 for debugging
    } // Close catch
}); // Close the create market route

/**
 * POST /lend/deposit
 * Deposit collateral
 */
app.post('/lend/deposit', (req: Request, res: Response) => { // Define the endpoint for locking collateral
    try { // Wrap in try/catch
        const { marketId, pubkey, amount, collateralPrice } = req.body; // Extract deposit parameters
        const market = markets.get(marketId); // Fetch the market from memory

        if (!market) { // Reject if the market does not exist
            return res.status(404).json({ error: 'Market not found' }); // Return 404
        } // Close existence check

        const key = getPositionKey(marketId, pubkey); // Generate the composite key for this position
        let position = positions.get(key); // Try to find an existing position

        if (!position) { // If this is the user's first interaction with this market
            position = { // Create a new position
                pubkey, // Store the user's public key
                collateral: 0, // Start with zero collateral
                debt: 0, // Start with zero debt
                collateralValue: 0, // Start with zero collateral value
                healthFactor: Number.MAX_VALUE, // Start with infinite health factor because there is no debt
            }; // Close new position object
        } // Close initialization block

        position.collateral += amount; // Increase the collateral balance by the deposit
        const addedValue = amount * (collateralPrice || market.collateralPrice); // Compute the dollar value of the new deposit
        position.collateralValue += addedValue; // Increase the cached collateral value
        position.healthFactor = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Recalculate health factor
        positions.set(key, position); // Save the updated position

        market.totalCollateral += amount; // Increase the global collateral tracker
        if (collateralPrice) { // If a new price was provided in the request
            market.collateralPrice = collateralPrice; // Update the market's cached collateral price
        } // Close price update block

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            deposit: { // Group deposit details
                amount, // Echo the deposited amount
                collateralValue: position.collateralValue, // Show the total collateral value
            }, // Close deposit group
            position: { // Show the updated position
                collateral: position.collateral, // Show total collateral
                debt: position.debt, // Show current debt
                healthFactor: position.healthFactor.toFixed(4), // Format health factor for readability
            }, // Close position group
            market: { // Show updated market totals
                totalCollateral: market.totalCollateral, // Show global collateral
                collateralPrice: market.collateralPrice, // Show current price
            }, // Close market group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Deposit failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the deposit route

/**
 * POST /lend/borrow
 * Borrow against collateral
 */
app.post('/lend/borrow', (req: Request, res: Response) => { // Define the endpoint for taking out a loan
    try { // Wrap in try/catch
        const { marketId, pubkey, amount } = req.body; // Extract borrow parameters
        const market = markets.get(marketId); // Fetch the market

        if (!market) { // Reject if the market does not exist
            return res.status(404).json({ error: 'Market not found' }); // Return 404
        } // Close existence check

        const key = getPositionKey(marketId, pubkey); // Generate the composite key
        const position = positions.get(key); // Fetch the user's position

        if (!position) { // Reject if the user has not deposited collateral
            return res.status(400).json({ error: 'No collateral deposited' }); // Return 400
        } // Close collateral check

        const maxBorrow = position.collateralValue * (market.ltvRatio / 100); // Calculate maximum borrow based on LTV
        if (position.debt + amount > maxBorrow) { // Reject if the request exceeds the LTV limit
            return res.status(400).json({ // Return 400 with detailed error
                error: 'Borrow exceeds LTV limit', // Explain the failure
                maxBorrow, // Show the maximum allowed borrow
                requestedDebt: position.debt + amount, // Show what the debt would become
            }); // Close error response
        } // Close LTV check

        position.debt += amount; // Increase the user's debt by the borrowed amount
        position.healthFactor = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Recalculate health factor
        positions.set(key, position); // Save the updated position
        market.totalDebt += amount; // Increase global debt

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            borrow: { // Group borrow details
                amount, // Echo the borrowed amount
                totalDebt: position.debt, // Show the new total debt
                maxBorrow, // Show the maximum allowed for reference
            }, // Close borrow group
            position: { // Show updated position
                collateral: position.collateral, // Show collateral
                collateralValue: position.collateralValue, // Show collateral value
                debt: position.debt, // Show debt
                healthFactor: position.healthFactor.toFixed(4), // Format health factor
            }, // Close position group
            market: { // Show updated market
                totalDebt: market.totalDebt, // Show global debt
            }, // Close market group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Borrow failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the borrow route

/**
 * POST /lend/repay
 * Repay borrowed tokens
 */
app.post('/lend/repay', (req: Request, res: Response) => { // Define the endpoint for returning borrowed funds
    try { // Wrap in try/catch
        const { marketId, pubkey, amount } = req.body; // Extract repayment parameters
        const market = markets.get(marketId); // Fetch the market

        if (!market) { // Reject if the market does not exist
            return res.status(404).json({ error: 'Market not found' }); // Return 404
        } // Close existence check

        const key = getPositionKey(marketId, pubkey); // Generate the composite key
        const position = positions.get(key); // Fetch the user's position

        if (!position) { // Reject if the user has no position
            return res.status(404).json({ error: 'No position found' }); // Return 404
        } // Close position check

        if (amount > position.debt) { // Reject if the repayment exceeds the total debt
            return res.status(400).json({ error: 'Repay amount exceeds debt' }); // Return 400
        } // Close overpayment check

        position.debt -= amount; // Decrease the debt by the repaid amount
        position.healthFactor = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Recalculate health factor
        positions.set(key, position); // Save the updated position
        market.totalDebt -= amount; // Decrease global debt

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            repay: { // Group repayment details
                amount, // Echo the repaid amount
                remainingDebt: position.debt, // Show the remaining balance
            }, // Close repay group
            position: { // Show updated position
                collateral: position.collateral, // Show collateral
                debt: position.debt, // Show debt
                healthFactor: position.healthFactor.toFixed(4), // Format health factor
            }, // Close position group
            market: { // Show updated market
                totalDebt: market.totalDebt, // Show global debt
            }, // Close market group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Repay failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the repay route

/**
 * POST /lend/liquidate
 * Liquidate an unhealthy position
 */
app.post('/lend/liquidate', (req: Request, res: Response) => { // Define the endpoint for executing liquidations
    try { // Wrap in try/catch
        const { marketId, borrowerPubkey, repayAmount, liquidatorPubkey } = req.body; // Extract liquidation parameters
        const market = markets.get(marketId); // Fetch the market

        if (!market) { // Reject if the market does not exist
            return res.status(404).json({ error: 'Market not found' }); // Return 404
        } // Close existence check

        const key = getPositionKey(marketId, borrowerPubkey); // Generate the key for the borrower's position
        const position = positions.get(key); // Fetch the borrower's position

        if (!position) { // Reject if the borrower has no position
            return res.status(404).json({ error: 'Borrower position not found' }); // Return 404
        } // Close position check

        const hf = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Calculate current health factor
        if (hf >= 1) { // Reject if the position is still healthy
            return res.status(400).json({ // Return 400 with details
                error: 'Position is healthy, cannot liquidate', // Explain the failure
                healthFactor: hf.toFixed(4), // Show the health factor
            }); // Close error response
        } // Close health check

        if (repayAmount > position.debt) { // Reject if the liquidator tries to repay more than the debt
            return res.status(400).json({ error: 'Repay amount exceeds borrower debt' }); // Return 400
        } // Close repay amount check

        const collateralToSeize = repayAmount * 1.05; // Calculate seized collateral with a 5% liquidation bonus
        if (collateralToSeize > position.collateral) { // Reject if seizure exceeds available collateral
            return res.status(400).json({ error: 'Insufficient collateral to seize' }); // Return 400
        } // Close collateral check

        position.debt -= repayAmount; // Reduce the borrower's debt by the repaid amount
        position.collateral -= collateralToSeize; // Reduce the borrower's collateral by the seized amount
        position.collateralValue = position.collateral * market.collateralPrice; // Recalculate collateral value after seizure
        position.healthFactor = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Recalculate health factor
        positions.set(key, position); // Save the updated position
        market.totalDebt -= repayAmount; // Decrease global debt
        market.totalCollateral -= collateralToSeize; // Decrease global collateral

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            liquidation: { // Group liquidation details
                borrower: borrowerPubkey.slice(0, 8) + '...', // Truncate borrower address for privacy
                liquidator: liquidatorPubkey.slice(0, 8) + '...', // Truncate liquidator address
                repayAmount, // Show the debt repaid
                collateralToSeize, // Show the collateral seized
                liquidatorProfit: collateralToSeize - repayAmount, // Calculate the liquidator's profit
                newHealthFactor: position.healthFactor.toFixed(4), // Show the updated health factor
            }, // Close liquidation group
            market: { // Show updated market
                totalDebt: market.totalDebt, // Show global debt
                totalCollateral: market.totalCollateral, // Show global collateral
            }, // Close market group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Liquidation failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the liquidate route

/**
 * GET /lend/position/:marketId/:pubkey
 * Get user position
 */
app.get('/lend/position/:marketId/:pubkey', (req: Request, res: Response) => { // Define the endpoint to read a user's position
    const market = markets.get(req.params.marketId); // Fetch the market by ID
    if (!market) { // Reject if the market does not exist
        return res.status(404).json({ error: 'Market not found' }); // Return 404
    } // Close existence check

    const key = getPositionKey(req.params.marketId, req.params.pubkey); // Generate the composite key
    const position = positions.get(key); // Fetch the position
    if (!position) { // Reject if no position exists
        return res.status(404).json({ error: 'No position found' }); // Return 404
    } // Close position check

    const maxBorrow = position.collateralValue * (market.ltvRatio / 100); // Calculate maximum borrow for reference
    const hf = calculateHealthFactor(position.collateralValue, position.debt, market.liquidationThreshold); // Recalculate health factor

    res.json({ // Respond with the full position
        position: { // Nest data under a descriptive key
            pubkey: req.params.pubkey.slice(0, 8) + '...', // Truncate address for privacy
            collateral: position.collateral, // Show collateral amount
            collateralValue: position.collateralValue, // Show collateral dollar value
            debt: position.debt, // Show debt amount
            maxBorrow, // Show borrowing capacity
            healthFactor: hf.toFixed(4), // Format health factor
            status: hf >= 1 ? 'healthy' : 'liquidatable', // Label the position status for UI convenience
        }, // Close position group
        market: { // Include market context
            id: market.id, // Show market ID
            collateralPrice: market.collateralPrice, // Show current collateral price
            liquidationThreshold: market.liquidationThreshold, // Show threshold for reference
        }, // Close market group
    }); // Close response
}); // Close the position route

app.listen(PORT, () => { // Start the Express server on the chosen port
    console.log(`=== Phase 19: Lending Protocol API ===`); // Print a header identifying this API
    console.log(`Server running on http://localhost:${PORT}`); // Print the URL for easy testing
    console.log(`\nEndpoints:`); // Print a section header
    console.log(`  POST /lend/market/create   - Create market`); // Document the create endpoint
    console.log(`  POST /lend/deposit         - Deposit collateral`); // Document the deposit endpoint
    console.log(`  POST /lend/borrow          - Borrow tokens`); // Document the borrow endpoint
    console.log(`  POST /lend/repay           - Repay loan`); // Document the repay endpoint
    console.log(`  POST /lend/liquidate       - Liquidate position`); // Document the liquidate endpoint
    console.log(`  GET  /lend/position/:m/:pk - User position`); // Document the position endpoint
}); // Close the listen callback
