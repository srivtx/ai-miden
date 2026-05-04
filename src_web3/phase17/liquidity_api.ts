import express, { Request, Response } from 'express'; // Import Express to build the REST API server for liquidity operations

/**
 * Phase 17: Liquidity Pool API
 *
 * REST API for liquidity pool operations:
 * POST /pool/create - Create a new pool
 * POST /pool/:id/deposit - Add liquidity
 * POST /pool/:id/withdraw - Remove liquidity
 * GET /pool/:id - Get pool info
 * GET /pool/:id/il-calculator - Calculate impermanent loss
 */

const app = express(); // Instantiate the Express application to handle HTTP requests
app.use(express.json()); // Enable JSON body parsing so request bodies are available as objects

const PORT = 3006; // Use port 3006 to avoid collisions with other phase APIs

// ============================================================================
// TYPES
// ============================================================================

interface LiquidityPool { // Define the TypeScript shape of a liquidity pool for compile-time safety
    id: string; // Unique identifier for the pool
    tokenA: string; // Symbol or mint address of the first token
    tokenB: string; // Symbol or mint address of the second token
    reserveA: number; // Current amount of Token A in the pool
    reserveB: number; // Current amount of Token B in the pool
    totalLpSupply: number; // Total LP tokens issued to track ownership
    providers: Map<string, number>; // Map from provider address to their LP token balance
    fee: number; // Trading fee as a decimal fraction
    priceAtDeposit: number; // Price ratio when the pool was created for IL calculations
}

// ============================================================================
// STORAGE
// ============================================================================

const pools: Map<string, LiquidityPool> = new Map(); // Store pools in memory using a Map for fast lookup by ID

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => { // Define a health check so monitoring tools can verify uptime
    res.json({ status: 'healthy', pools: pools.size }); // Respond with the count of active pools as a liveness metric
}); // Close the health route

/**
 * POST /pool/create
 * Create a new liquidity pool
 */
app.post('/pool/create', (req: Request, res: Response) => { // Define the endpoint to initialize a new pool
    try { // Wrap in try/catch to prevent server crashes from malformed input
        const { tokenA, tokenB, initialA, initialB, creator } = req.body; // Extract initialization parameters from the JSON body

        if (!tokenA || !tokenB || !initialA || !initialB || !creator) { // Validate that all required fields are present
            return res.status(400).json({ error: 'Missing parameters' }); // Return 400 to inform the client of bad input
        } // Close validation block

        const id = `pool_${tokenA.slice(0, 8)}_${tokenB.slice(0, 8)}`; // Generate a readable ID from truncated token names

        if (pools.has(id)) { // Prevent duplicate pools for the same pair to avoid fragmentation
            return res.status(409).json({ error: 'Pool already exists' }); // Return 409 Conflict for duplicate resources
        } // Close duplicate check

        const initialLp = Math.sqrt(initialA * initialB); // Compute initial LP tokens as the geometric mean of starting reserves

        const pool: LiquidityPool = { // Construct the pool object with all fields initialized
            id, // Assign the generated ID
            tokenA, // Store the first token identifier
            tokenB, // Store the second token identifier
            reserveA: initialA, // Set the starting reserve for Token A
            reserveB: initialB, // Set the starting reserve for Token B
            totalLpSupply: initialLp, // Set the initial LP token supply
            providers: new Map([[creator, initialLp]]), // Grant all initial LP tokens to the pool creator
            fee: 0.003, // Set a default 0.3% trading fee
            priceAtDeposit: initialB / initialA, // Record the initial price for impermanent loss baselines
        }; // Close pool object construction

        pools.set(id, pool); // Save the pool into memory so it can be queried and modified later

        res.status(201).json({ // Respond with 201 Created to indicate successful resource creation
            success: true, // Include a status flag for simple client-side checks
            pool: { // Nest pool details under a descriptive key
                id, // Echo back the pool ID
                tokenA, // Echo back the first token
                tokenB, // Echo back the second token
                reserveA: initialA, // Show the starting reserve A
                reserveB: initialB, // Show the starting reserve B
                totalLpSupply: initialLp, // Show the initial LP token supply
                price: initialB / initialA, // Calculate and show the initial spot price
            }, // Close pool detail group
        }); // Close the 201 response
    } catch (error) { // Catch unexpected exceptions such as invalid math operations
        res.status(500).json({ error: `Failed to create pool: ${error}` }); // Return 500 with the error for debugging
    } // Close catch block
}); // Close the create route

/**
 * POST /pool/:id/deposit
 * Add liquidity to a pool
 */
app.post('/pool/:id/deposit', (req: Request, res: Response) => { // Define the endpoint for depositing paired tokens
    try { // Wrap in try/catch to handle missing pools or bad math gracefully
        const { id } = req.params; // Read the pool ID from the URL path
        const { provider, amountA, amountB } = req.body; // Read the depositor address and amounts from the body
        const pool = pools.get(id); // Fetch the pool from memory

        if (!pool) { // Reject if the pool ID does not match any existing pool
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
        } // Close existence check

        const lpA = (amountA / pool.reserveA) * pool.totalLpSupply; // Compute LP tokens if only Token A is considered
        const lpB = (amountB / pool.reserveB) * pool.totalLpSupply; // Compute LP tokens if only Token B is considered
        const lpMinted = Math.min(lpA, lpB); // Take the minimum to prevent unfair dilution from imbalanced deposits

        pool.reserveA += amountA; // Increase Token A reserve by the deposited amount
        pool.reserveB += amountB; // Increase Token B reserve by the deposited amount
        pool.totalLpSupply += lpMinted; // Expand the total LP token supply by the newly minted amount

        const existing = pool.providers.get(provider) || 0; // Read the provider's current LP balance or default to zero
        pool.providers.set(provider, existing + lpMinted); // Credit the provider with their new LP tokens

        res.json({ // Respond with 200 OK and the deposit details
            success: true, // Signal success for easy client parsing
            deposit: { // Group deposit data under a clear key
                amountA, // Echo the deposited Token A
                amountB, // Echo the deposited Token B
                lpMinted, // Show exactly how many LP tokens were created
                providerShare: `${((existing + lpMinted) / pool.totalLpSupply * 100).toFixed(2)}%`, // Calculate the provider's new share
            }, // Close deposit group
            pool: { // Show the updated pool state
                id, // Include the pool ID
                reserveA: pool.reserveA, // Show the new reserve A
                reserveB: pool.reserveB, // Show the new reserve B
                totalLpSupply: pool.totalLpSupply, // Show the expanded LP supply
                price: pool.reserveB / pool.reserveA, // Recalculate the spot price after the deposit
            }, // Close pool state group
        }); // Close response
    } catch (error) { // Catch math errors or unexpected input types
        res.status(500).json({ error: `Deposit failed: ${error}` }); // Return 500 with details for debugging
    } // Close catch block
}); // Close the deposit route

/**
 * POST /pool/:id/withdraw
 * Remove liquidity from a pool
 */
app.post('/pool/:id/withdraw', (req: Request, res: Response) => { // Define the endpoint for withdrawing liquidity
    try { // Wrap in try/catch to handle missing pools or invalid amounts
        const { id } = req.params; // Read the pool ID from the URL path
        const { provider, lpAmount } = req.body; // Read the provider address and the LP tokens they want to burn
        const pool = pools.get(id); // Fetch the pool from memory

        if (!pool) { // Reject if the pool does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
        } // Close existence check

        const providerLp = pool.providers.get(provider) || 0; // Read the provider's current LP balance
        if (lpAmount > providerLp) { // Reject if the provider tries to burn more LP than they own
            return res.status(400).json({ error: 'Insufficient LP tokens' }); // Return 400 for invalid withdrawal requests
        } // Close balance check

        const share = lpAmount / pool.totalLpSupply; // Calculate the provider's fractional share of the pool
        const amountAOut = pool.reserveA * share; // Compute Token A withdrawal proportional to the burned LP
        const amountBOut = pool.reserveB * share; // Compute Token B withdrawal proportional to the burned LP

        pool.reserveA -= amountAOut; // Decrease Token A reserve by the withdrawn amount
        pool.reserveB -= amountBOut; // Decrease Token B reserve by the withdrawn amount
        pool.totalLpSupply -= lpAmount; // Shrink the total LP supply by the burned amount

        const newBalance = providerLp - lpAmount; // Calculate the provider's remaining LP balance
        if (newBalance > 0) { // If the provider still has LP tokens left
            pool.providers.set(provider, newBalance); // Update their balance to the new lower amount
        } else { // If the provider burned their entire balance
            pool.providers.delete(provider); // Remove them from the map to keep storage clean
        } // Close balance update branching

        res.json({ // Respond with 200 OK and the withdrawal details
            success: true, // Signal success for client convenience
            withdrawal: { // Group withdrawal data under a clear key
                lpBurned: lpAmount, // Show how many LP tokens were burned
                amountAOut, // Show the Token A received
                amountBOut, // Show the Token B received
            }, // Close withdrawal group
            pool: { // Show the updated pool state
                id, // Include the pool ID
                reserveA: pool.reserveA, // Show the reduced reserve A
                reserveB: pool.reserveB, // Show the reduced reserve B
                totalLpSupply: pool.totalLpSupply, // Show the reduced LP supply
                price: pool.reserveB / pool.reserveA, // Recalculate the spot price after withdrawal
            }, // Close pool state group
        }); // Close response
    } catch (error) { // Catch unexpected math or input errors
        res.status(500).json({ error: `Withdrawal failed: ${error}` }); // Return 500 with details for debugging
    } // Close catch block
}); // Close the withdraw route

/**
 * GET /pool/:id
 * Get pool information
 */
app.get('/pool/:id', (req: Request, res: Response) => { // Define the endpoint to read pool state
    const pool = pools.get(req.params.id); // Look up the pool by the ID in the URL
    if (!pool) { // Reject if no pool matches the ID
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
    } // Close existence check

    res.json({ // Respond with the full pool state
        pool: { // Nest data under a descriptive key
            id: pool.id, // Include the pool identifier
            tokenA: pool.tokenA, // Show the first token
            tokenB: pool.tokenB, // Show the second token
            reserveA: pool.reserveA, // Show the current reserve A
            reserveB: pool.reserveB, // Show the current reserve B
            totalLpSupply: pool.totalLpSupply, // Show the total LP token supply
            price: pool.reserveB / pool.reserveA, // Calculate the current spot price
            providers: Array.from(pool.providers.entries()).map(([addr, amt]) => ({ // Convert the Map to an array for JSON
                address: addr.slice(0, 8) + '...', // Truncate addresses for privacy
                lpTokens: amt, // Show the raw LP balance
                share: `${((amt / pool.totalLpSupply) * 100).toFixed(2)}%`, // Calculate percentage ownership
            })), // Close providers mapping
        }, // Close pool detail object
    }); // Close response
}); // Close the pool info route

/**
 * GET /pool/:id/il-calculator
 * Calculate impermanent loss for current price vs deposit price
 */
app.get('/pool/:id/il-calculator', (req: Request, res: Response) => { // Define the endpoint to compute impermanent loss
    const pool = pools.get(req.params.id); // Look up the pool by ID
    if (!pool) { // Reject if the pool does not exist
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
    } // Close existence check

    const currentPrice = pool.reserveB / pool.reserveA; // Calculate the current spot price from reserves
    const priceRatio = currentPrice / pool.priceAtDeposit; // Compute how much the price has changed since deposit

    const sqrtRatio = Math.sqrt(priceRatio); // Compute the square root because the AMM formula uses geometric relationships
    const impermanentLoss = (2 * sqrtRatio / (1 + priceRatio)) - 1; // Apply the standard IL formula for constant product pools

    res.json({ // Respond with the IL analysis
        pool: pool.id, // Identify which pool was analyzed
        priceAtDeposit: pool.priceAtDeposit, // Show the baseline price for reference
        currentPrice, // Show the current price for comparison
        priceRatio, // Show the raw multiplier of price change
        impermanentLoss: `${(impermanentLoss * 100).toFixed(2)}%`, // Format IL as a percentage with two decimals
        note: 'IL is relative to holding the original tokens. Fees may offset this loss.', // Add an educational disclaimer
    }); // Close response
}); // Close the IL calculator route

app.listen(PORT, () => { // Start the Express server on the chosen port
    console.log(`=== Phase 17: Liquidity Pool API ===`); // Print a header identifying this API
    console.log(`Server running on http://localhost:${PORT}`); // Print the accessible URL for easy testing
    console.log(`\nEndpoints:`); // Print a section header
    console.log(`  POST /pool/create            - Create pool`); // Document the create endpoint
    console.log(`  POST /pool/:id/deposit       - Add liquidity`); // Document the deposit endpoint
    console.log(`  POST /pool/:id/withdraw      - Remove liquidity`); // Document the withdraw endpoint
    console.log(`  GET  /pool/:id               - Pool info`); // Document the info endpoint
    console.log(`  GET  /pool/:id/il-calculator - Impermanent loss calc`); // Document the IL calculator endpoint
}); // Close the listen callback
