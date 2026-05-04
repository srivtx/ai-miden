import express, { Request, Response } from 'express'; // Import Express framework to build the REST API server

/**
 * Phase 16: AMM (Automated Market Maker) API
 *
 * REST API implementing a constant product AMM (x * y = k):
 * POST /amm/pool/create - Create liquidity pool
 * POST /amm/pool/add-liquidity - Add liquidity
 * POST /amm/pool/remove-liquidity - Remove liquidity
 * POST /amm/swap - Swap tokens
 * GET /amm/pool/:id - Get pool info
 * GET /amm/price - Get token prices
 */

const app = express(); // Create the Express application instance that handles all HTTP routing
app.use(express.json()); // Enable automatic JSON body parsing so req.body contains parsed objects

const PORT = 3004; // Choose port 3004 to avoid conflicts with other phase APIs running locally

// ============================================================================
// TYPES
// ============================================================================

interface LiquidityPool { // Define the shape of a liquidity pool for TypeScript type safety
    id: string; // Unique identifier derived from token pair names
    tokenA: string; // Mint address or symbol for the first token in the pair
    tokenB: string; // Mint address or symbol for the second token in the pair
    reserveA: number; // Current amount of Token A held in the pool
    reserveB: number; // Current amount of Token B held in the pool
    totalLiquidity: number; // Total LP tokens minted to track proportional ownership
    liquidityProviders: Map<string, number>; // Map from provider pubkey to their LP token balance
    fees: number; // Fee percentage as a decimal, e.g. 0.003 means 0.3%
    swapCount: number; // Counter for total swaps executed to measure activity
    volumeA: number; // Cumulative volume of Token A traded for analytics
    volumeB: number; // Cumulative volume of Token B traded for analytics
}

interface SwapResult { // Define the shape of a swap calculation result
    amountIn: number; // How much the trader deposited
    amountOut: number; // How much the trader received after the curve and fees
    priceImpact: number; // Percentage change in price caused by this trade
    fee: number; // Absolute fee amount collected for liquidity providers
}

// ============================================================================
// STORAGE
// ============================================================================

const pools: Map<string, LiquidityPool> = new Map(); // Use an in-memory Map to store pools because this is a demo API without a database

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Constant Product Market Maker formula: x * y = k
 *
 * Given reserves (x, y) and input amount (dx), calculate output (dy):
 * (x + dx) * (y - dy) = x * y
 * dy = y - (x * y) / (x + dx)
 * dy = y * dx / (x + dx)
 */
function calculateSwap( // Implement the swap math so routes can reuse it consistently
    reserveIn: number, // How much of the input token exists in the pool before the trade
    reserveOut: number, // How much of the output token exists in the pool before the trade
    amountIn: number, // How much the trader wants to deposit
    fee: number // The pool fee as a decimal fraction
): SwapResult { // Return a structured result so callers get all relevant data
    const amountInWithFee = amountIn * (1 - fee); // Deduct the fee from the input so providers earn on every trade
    const amountOut = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee); // Apply constant product math to find output
    const priceImpact = (amountIn / reserveIn) * 100; // Estimate slippage as the ratio of trade size to pool depth
    const feeAmount = amountIn * fee; // Compute the exact fee collected to show transparency to the trader

    return { // Return an object with all calculated fields for the route handler
        amountIn, // Echo back the input for clarity in the response
        amountOut, // Include the computed output so the trader knows what to expect
        priceImpact, // Include slippage so the UI can warn about large trades
        fee: feeAmount, // Include the fee so the trader sees the protocol revenue
    }; // Close the return statement
} // Close the helper function

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => { // Define a health check route so load balancers know the server is alive
    res.json({ status: 'healthy', pools: pools.size }); // Respond with the current pool count as a quick sanity metric
}); // Close the health route handler

/**
 * POST /amm/pool/create
 * Create a new liquidity pool
 */
app.post('/amm/pool/create', (req: Request, res: Response) => { // Define the endpoint to bootstrap a new trading pair
    try { // Wrap in try/catch because parsing and math can throw unexpected errors
        const { tokenA, tokenB, initialA, initialB, creator, fee = 0.003 } = req.body; // Destructure the request body with a default 0.3% fee

        if (!tokenA || !tokenB || !initialA || !initialB || !creator) { // Validate required fields to prevent half-created pools
            return res.status(400).json({ error: 'Missing parameters' }); // Return 400 so the client knows the request was malformed
        } // Close the validation block

        // Sort tokens to ensure consistent pool IDs regardless of parameter order
        const [tA, tB] = tokenA < tokenB ? [tokenA, tokenB] : [tokenB, tokenA]; // Lexicographic sort prevents duplicate pools for the same pair
        const [rA, rB] = tokenA < tokenB ? [initialA, initialB] : [initialB, initialA]; // Align reserves with the sorted token order

        const id = `pool_${tA.slice(0, 8)}_${tB.slice(0, 8)}`; // Generate a human-readable ID from truncated token addresses

        if (pools.has(id)) { // Reject duplicate pools because each pair should have exactly one canonical pool
            return res.status(409).json({ error: 'Pool already exists' }); // Return 409 Conflict to signal a duplicate resource
        } // Close the duplicate check

        const k = rA * rB; // Compute the constant product k that governs all future swaps
        const initialLiquidity = Math.sqrt(k); // Use geometric mean as initial LP tokens to establish a fair baseline

        const pool: LiquidityPool = { // Construct the new pool object with all fields initialized
            id, // Assign the generated ID for later lookups
            tokenA: tA, // Store the canonical first token
            tokenB: tB, // Store the canonical second token
            reserveA: rA, // Store the initial reserve for Token A
            reserveB: rB, // Store the initial reserve for Token B
            totalLiquidity: initialLiquidity, // Set total LP tokens to the geometric mean
            liquidityProviders: new Map([[creator, initialLiquidity]]), // Grant all initial LP tokens to the creator
            fees: fee, // Store the chosen fee tier
            swapCount: 0, // Initialize activity counter to zero
            volumeA: 0, // Initialize Token A volume tracker
            volumeB: 0, // Initialize Token B volume tracker
        }; // Close the pool object construction

        pools.set(id, pool); // Save the pool into our in-memory Map so future requests can access it

        res.status(201).json({ // Respond with 201 Created to signal successful resource creation
            success: true, // Include a boolean flag so clients can check status without parsing HTTP codes
            pool: { // Nest pool data under a descriptive key for consistent response shapes
                id, // Echo back the ID so the client knows where to query next
                tokenA: tA, // Echo back the sorted token A
                tokenB: tB, // Echo back the sorted token B
                reserveA: rA, // Show the starting reserve A
                reserveB: rB, // Show the starting reserve B
                k, // Show the constant product for educational transparency
                price: rB / rA, // Calculate the initial spot price for the trader's reference
                fee: `${fee * 100}%`, // Convert the decimal to a human-readable percentage
                liquidity: initialLiquidity, // Show the total LP token supply at genesis
            }, // Close the pool detail object
            formula: 'x * y = k (Constant Product Market Maker)', // Label the math so learners know which curve is in use
        }); // Close the 201 response
    } catch (error) { // Catch any unexpected exceptions to prevent crashing the server
        res.status(500).json({ error: `Failed to create pool: ${error}` }); // Return 500 with the error message for debugging
    } // Close the catch block
}); // Close the create pool route

/**
 * POST /amm/pool/:id/add-liquidity
 * Add liquidity to a pool
 */
app.post('/amm/pool/:id/add-liquidity', (req: Request, res: Response) => { // Define the endpoint for depositing paired tokens
    try { // Wrap in try/catch to handle malformed inputs or missing pools gracefully
        const { id } = req.params; // Extract the pool ID from the URL path parameter
        const { provider, amountA, amountB } = req.body; // Destructure the depositor address and amounts from the JSON body
        const pool = pools.get(id); // Look up the pool in memory to ensure it exists

        if (!pool) { // Reject the request if the pool ID does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 to indicate the resource is missing
        } // Close the existence check

        // Calculate LP tokens to mint proportionally to the value added
        // LP tokens = min(amountA / reserveA, amountB / reserveB) * totalLiquidity
        const liquidityA = (amountA / pool.reserveA) * pool.totalLiquidity; // Compute the LP share if only Token A is considered
        const liquidityB = (amountB / pool.reserveB) * pool.totalLiquidity; // Compute the LP share if only Token B is considered
        const liquidityMinted = Math.min(liquidityA, liquidityB); // Take the minimum to prevent dilution from imbalanced deposits

        pool.reserveA += amountA; // Increase the pool's Token A reserve by the deposited amount
        pool.reserveB += amountB; // Increase the pool's Token B reserve by the deposited amount
        pool.totalLiquidity += liquidityMinted; // Expand the total LP token supply by the newly minted amount

        const existing = pool.liquidityProviders.get(provider) || 0; // Read the provider's current balance or default to zero
        pool.liquidityProviders.set(provider, existing + liquidityMinted); // Credit the provider with their new LP tokens

        res.json({ // Respond with 200 OK and the details of the liquidity addition
            success: true, // Signal success explicitly for client convenience
            liquidityAdded: { // Group the deposit details under a clear key
                amountA, // Echo back the deposited Token A amount
                amountB, // Echo back the deposited Token B amount
                lpTokensReceived: liquidityMinted, // Show exactly how many LP tokens were created
                shareOfPool: (liquidityMinted / pool.totalLiquidity) * 100, // Calculate the provider's new percentage ownership
            }, // Close the liquidityAdded group
            pool: { // Show the updated pool state after the deposit
                id, // Include the pool ID for context
                reserveA: pool.reserveA, // Show the new reserve A
                reserveB: pool.reserveB, // Show the new reserve B
                totalLiquidity: pool.totalLiquidity, // Show the expanded LP supply
                price: pool.reserveB / pool.reserveA, // Recalculate the spot price after the reserves changed
            }, // Close the pool state group
        }); // Close the response
    } catch (error) { // Catch unexpected math or parsing errors
        res.status(500).json({ error: `Failed to add liquidity: ${error}` }); // Return 500 with details for debugging
    } // Close the catch block
}); // Close the add-liquidity route

/**
 * POST /amm/swap
 * Swap tokens
 */
app.post('/amm/swap', (req: Request, res: Response) => { // Define the endpoint for executing a token swap
    try { // Wrap in try/catch to handle invalid inputs or missing pools
        const { poolId, fromToken, amountIn, trader } = req.body; // Destructure swap parameters from the JSON body
        const pool = pools.get(poolId); // Look up the target pool by ID

        if (!pool) { // Reject if the pool does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 to signal a bad pool reference
        } // Close the existence check

        let reserveIn: number; // Declare a variable to hold the input token reserve
        let reserveOut: number; // Declare a variable to hold the output token reserve
        let tokenOut: string; // Declare a variable to identify which token the trader receives

        if (fromToken === pool.tokenA) { // Check if the trader is selling Token A
            reserveIn = pool.reserveA; // Set the input reserve to Token A's balance
            reserveOut = pool.reserveB; // Set the output reserve to Token B's balance
            tokenOut = pool.tokenB; // Identify Token B as the token the trader will receive
        } else if (fromToken === pool.tokenB) { // Check if the trader is selling Token B
            reserveIn = pool.reserveB; // Set the input reserve to Token B's balance
            reserveOut = pool.reserveA; // Set the output reserve to Token A's balance
            tokenOut = pool.tokenA; // Identify Token A as the token the trader will receive
        } else { // Reject if the fromToken does not match either pool token
            return res.status(400).json({ error: 'Invalid fromToken' }); // Return 400 for an invalid parameter
        } // Close the token direction branching

        const swap = calculateSwap(reserveIn, reserveOut, amountIn, pool.fees); // Run the constant product math to get the trade result

        // Update reserves based on the direction of the trade
        if (fromToken === pool.tokenA) { // If the trader sold Token A
            pool.reserveA += amountIn; // Increase Token A reserve by the input amount
            pool.reserveB -= swap.amountOut; // Decrease Token B reserve by the output amount
            pool.volumeA += amountIn; // Accumulate Token A volume for analytics
        } else { // If the trader sold Token B
            pool.reserveB += amountIn; // Increase Token B reserve by the input amount
            pool.reserveA -= swap.amountOut; // Decrease Token A reserve by the output amount
            pool.volumeB += amountIn; // Accumulate Token B volume for analytics
        } // Close the reserve update branching
        pool.swapCount++; // Increment the swap counter to track pool activity

        res.json({ // Respond with 200 OK and the full trade report
            success: true, // Signal success for easy client parsing
            swap: { // Group trade-specific details under a clear key
                from: fromToken, // Identify the token the trader sold
                to: tokenOut, // Identify the token the trader bought
                amountIn: swap.amountIn, // Echo the deposited amount
                amountOut: swap.amountOut, // Show the computed output after fees and curve
                price: swap.amountOut / swap.amountIn, // Calculate the effective average price for this trade
                priceImpact: `${swap.priceImpact.toFixed(4)}%`, // Format slippage to four decimals for readability
                fee: swap.fee, // Show the absolute fee paid to liquidity providers
                slippage: `${swap.priceImpact.toFixed(4)}%`, // Duplicate slippage with a familiar label for UI compatibility
            }, // Close the swap detail group
            pool: { // Show the updated pool state after the swap
                id: poolId, // Include the pool ID for reference
                newReserveA: pool.reserveA, // Show the post-trade reserve A
                newReserveB: pool.reserveB, // Show the post-trade reserve B
                newPrice: pool.reserveB / pool.reserveA, // Show the new spot price after the ratio shift
                k: pool.reserveA * pool.reserveB, // Verify that k remains constant for educational purposes
                swapCount: pool.swapCount, // Show how many trades have occurred in total
            }, // Close the pool state group
        }); // Close the response
    } catch (error) { // Catch math errors, missing fields, or other exceptions
        res.status(500).json({ error: `Swap failed: ${error}` }); // Return 500 with the error message for debugging
    } // Close the catch block
}); // Close the swap route

/**
 * GET /amm/pool/:id
 * Get pool information
 */
app.get('/amm/pool/:id', (req: Request, res: Response) => { // Define the endpoint to read current pool state
    const pool = pools.get(req.params.id); // Look up the pool by the ID provided in the URL
    if (!pool) { // Reject if no pool matches the requested ID
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
    } // Close the existence check

    res.json({ // Respond with the full pool state
        pool: { // Nest data under a descriptive key for consistency
            id: pool.id, // Include the pool identifier
            tokenA: pool.tokenA, // Show the first token mint
            tokenB: pool.tokenB, // Show the second token mint
            reserveA: pool.reserveA, // Show the current Token A reserve
            reserveB: pool.reserveB, // Show the current Token B reserve
            price: pool.reserveB / pool.reserveA, // Compute the current spot price
            k: pool.reserveA * pool.reserveB, // Show the constant product for verification
            totalLiquidity: pool.totalLiquidity, // Show the total LP token supply
            fee: `${pool.fees * 100}%`, // Convert the fee decimal to a percentage string
            swapCount: pool.swapCount, // Show total number of executed swaps
            volumeA: pool.volumeA, // Show cumulative Token A volume
            volumeB: pool.volumeB, // Show cumulative Token B volume
            liquidityProviders: Array.from(pool.liquidityProviders.entries()).map(([addr, amount]) => ({ // Convert the Map to an array for JSON serialization
                address: addr.slice(0, 8) + '...', // Truncate addresses for privacy and brevity
                lpTokens: amount, // Show the raw LP token balance
                share: `${((amount / pool.totalLiquidity) * 100).toFixed(2)}%`, // Calculate and format the percentage ownership
            })), // Close the providers mapping
        }, // Close the pool detail object
    }); // Close the response
}); // Close the pool info route

/**
 * GET /amm/pools
 * List all pools
 */
app.get('/amm/pools', (_req: Request, res: Response) => { // Define the endpoint to list every pool in memory
    const list = Array.from(pools.values()).map(p => ({ // Convert the Map values to an array and transform each pool
        id: p.id, // Include the pool ID
        pair: `${p.tokenA.slice(0, 8)}... / ${p.tokenB.slice(0, 8)}...`, // Create a readable pair label from truncated addresses
        reserveA: p.reserveA, // Include the current reserve A for overview
        reserveB: p.reserveB, // Include the current reserve B for overview
        price: p.reserveB / p.reserveA, // Include the current price for quick reference
        liquidity: p.totalLiquidity, // Include total LP tokens as a depth proxy
        swaps: p.swapCount, // Include activity count for ranking
    })); // Close the mapping

    res.json({ count: list.length, pools: list }); // Return the total count and the array of pool summaries
}); // Close the list pools route

/**
 * GET /amm/price
 * Get prices for a token pair
 */
app.get('/amm/price', (req: Request, res: Response) => { // Define the endpoint to query the spot price of a pool
    const { poolId } = req.query; // Extract the pool ID from the query string
    const pool = pools.get(poolId as string); // Look up the pool, casting the query param to string

    if (!pool) { // Reject if the pool ID is missing or invalid
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for unknown pools
    } // Close the existence check

    // Calculate prices in both directions because traders may need either rate
    const priceAtoB = pool.reserveB / pool.reserveA; // Compute how many B you get per A
    const priceBtoA = pool.reserveA / pool.reserveB; // Compute how many A you get per B

    res.json({ // Respond with the price data
        pool: pool.id, // Identify which pool the prices belong to
        tokenA: pool.tokenA, // Include Token A for clarity
        tokenB: pool.tokenB, // Include Token B for clarity
        prices: { // Group the directional prices under a single key
            [`${pool.tokenA.slice(0, 8)}... -> ${pool.tokenB.slice(0, 8)}...`]: priceAtoB, // Label the A-to-B direction
            [`${pool.tokenB.slice(0, 8)}... -> ${pool.tokenA.slice(0, 8)}...`]: priceBtoA, // Label the B-to-A direction
        }, // Close the prices group
        formula: 'price = reserveOut / reserveIn', // Document the formula for educational purposes
    }); // Close the response
}); // Close the price route

app.listen(PORT, () => { // Start the Express server and bind it to the chosen port
    console.log(`=== Phase 16: AMM API ===`); // Print a header so the user knows which API started
    console.log(`Server running on http://localhost:${PORT}`); // Print the URL for easy copy-paste into clients
    console.log(`\nEndpoints:`); // Print a section header for the endpoint list
    console.log(`  POST /amm/pool/create        - Create pool`); // Document the create endpoint
    console.log(`  POST /amm/pool/:id/add-liq   - Add liquidity`); // Document the add liquidity endpoint
    console.log(`  POST /amm/swap               - Swap tokens`); // Document the swap endpoint
    console.log(`  GET  /amm/pool/:id           - Pool info`); // Document the pool info endpoint
    console.log(`  GET  /amm/pools              - List pools`); // Document the list pools endpoint
    console.log(`  GET  /amm/price              - Get price`); // Document the price endpoint
    console.log(`\nFormula: x * y = k`); // Print the core formula for reference
    console.log(`  x = reserve of token A`); // Define x for learners
    console.log(`  y = reserve of token B`); // Define y for learners
    console.log(`  k = constant product`); // Define k for learners
}); // Close the listen callback
