import express, { Request, Response } from 'express'; // Import Express framework to build the REST API server

/**
 * Phase 18: Staking API
 *
 * REST API for token staking:
 * POST /stake/create - Create staking pool
 * POST /stake/:id/stake - Stake tokens
 * POST /stake/:id/unstake - Unstake tokens
 * POST /stake/:id/claim - Claim rewards
 * GET /stake/:id/info - Get pool info
 * GET /stake/:id/position/:pubkey - Get user position
 */

const app = express(); // Create the Express application instance to handle HTTP routing
app.use(express.json()); // Enable automatic JSON body parsing so req.body contains parsed objects

const PORT = 3005; // Choose port 3005 for the staking API to avoid collisions with other services

// ============================================================================
// TYPES
// ============================================================================

interface StakingPool { // Define the TypeScript shape of a staking pool for type safety
    id: string; // Unique identifier for the pool
    token: string; // Mint address or symbol of the token being staked
    totalStaked: number; // Sum of all tokens currently locked by all stakers
    rewardToken: string; // Mint address or symbol of the token paid as rewards
    rewardRate: number; // Rewards per second per staked token, using a scaling factor for precision
    stakers: Map<string, StakerPosition>; // Map from user pubkey to their staking position
    createdAt: number; // Timestamp when the pool was created for analytics
    totalRewardsDistributed: number; // Cumulative rewards paid out across all claim events
    rewardPoolBalance: number; // Remaining tokens available for future rewards
}

interface StakerPosition { // Define the shape of an individual user's staking position
    pubkey: string; // User's public key for identification
    amount: number; // Number of tokens currently staked
    stakedAt: number; // Timestamp of the last stake, claim, or unstake to calculate elapsed time
    totalClaimed: number; // Lifetime rewards this user has already withdrawn
    pendingRewards: number; // Rewards calculated but not yet claimed, used for display
}

// ============================================================================
// STORAGE
// ============================================================================

const pools: Map<string, StakingPool> = new Map(); // Use an in-memory Map to store pools for this demo API

// ============================================================================
// HELPERS
// ============================================================================

function calculateRewards(position: StakerPosition, rewardRate: number, now: number): number { // Compute rewards earned since the last timing event
    const timeStaked = now - position.stakedAt; // Calculate elapsed seconds since stake or last claim
    return position.amount * rewardRate * timeStaked; // Multiply staked amount by rate and time for total accrued
} // Close the reward calculation helper

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => { // Define a health check route for monitoring and load balancers
    res.json({ status: 'healthy', pools: pools.size }); // Respond with the number of active pools as a liveness metric
}); // Close the health route

/**
 * POST /stake/create
 * Create a staking pool
 */
app.post('/stake/create', (req: Request, res: Response) => { // Define the endpoint to initialize a new staking pool
    try { // Wrap in try/catch to prevent server crashes from malformed input
        const { token, rewardToken, rewardRate, initialRewards } = req.body; // Extract pool parameters from the JSON body

        if (!token || !rewardToken || !rewardRate) { // Validate that all required fields are present
            return res.status(400).json({ error: 'Missing parameters' }); // Return 400 for bad requests
        } // Close validation block

        const id = `stake_${token.slice(0, 8)}_${Date.now()}`; // Generate a unique ID using the token symbol and current timestamp

        const pool: StakingPool = { // Construct the new staking pool object
            id, // Assign the generated ID
            token, // Store the token that users will stake
            totalStaked: 0, // Start with zero staked tokens
            rewardToken, // Store the token used for reward payouts
            rewardRate, // Store the per-second reward rate
            stakers: new Map(), // Initialize an empty map for user positions
            createdAt: Date.now(), // Record the creation timestamp
            totalRewardsDistributed: 0, // Initialize cumulative rewards to zero
            rewardPoolBalance: initialRewards || 0, // Seed the reward treasury if an initial amount was provided
        }; // Close pool object construction

        pools.set(id, pool); // Save the pool into memory so it can be queried and modified

        const apr = rewardRate * 31_536_000 * 100; // Calculate simple APR by annualizing the per-second rate
        const apy = ((1 + rewardRate) ** 31_536_000 - 1) * 100; // Calculate APY assuming continuous compounding

        res.status(201).json({ // Respond with 201 Created to indicate successful resource creation
            success: true, // Include a status flag for easy client parsing
            pool: { // Nest pool details under a descriptive key
                id, // Echo back the pool ID
                stakeToken: token, // Show which token must be staked
                rewardToken, // Show which token is paid as rewards
                rewardRate: `${rewardRate} rewards/sec/token`, // Display the rate in human-readable form
                apr: `${apr.toFixed(2)}%`, // Format the APR to two decimal places
                apy: `${apy.toFixed(2)}%`, // Format the APY to two decimal places
                rewardPoolBalance: pool.rewardPoolBalance, // Show the initial treasury size
            }, // Close pool detail group
        }); // Close the 201 response
    } catch (error) { // Catch unexpected exceptions such as invalid math
        res.status(500).json({ error: `Failed to create pool: ${error}` }); // Return 500 with the error for debugging
    } // Close catch block
}); // Close the create route

/**
 * POST /stake/:id/stake
 * Stake tokens
 */
app.post('/stake/:id/stake', (req: Request, res: Response) => { // Define the endpoint for locking tokens into a pool
    try { // Wrap in try/catch to handle missing pools or bad input
        const { id } = req.params; // Read the pool ID from the URL path
        const { pubkey, amount } = req.body; // Read the user's public key and stake amount from the body
        const pool = pools.get(id); // Fetch the pool from memory

        if (!pool) { // Reject if the pool does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
        } // Close existence check

        let position = pool.stakers.get(pubkey); // Try to find the user's existing position

        if (position) { // If the user already has a position in this pool
            const rewards = calculateRewards(position, pool.rewardRate, Date.now()); // Calculate rewards accrued since last update
            position.pendingRewards += rewards; // Add newly earned rewards to the pending balance
            position.amount += amount; // Increase the staked amount by the new deposit
            position.stakedAt = Date.now(); // Reset the timer to now because the staked amount changed
        } else { // If this is the user's first time staking in this pool
            position = { // Create a new position object
                pubkey, // Store the user's public key
                amount, // Set the initial staked amount
                stakedAt: Date.now(), // Record the current timestamp as the start time
                totalClaimed: 0, // Initialize lifetime claimed to zero
                pendingRewards: 0, // Initialize pending rewards to zero
            }; // Close the new position object
            pool.stakers.set(pubkey, position); // Save the new position into the pool's map
        } // Close the existing versus new position branching

        pool.totalStaked += amount; // Increase the global staked total by the new deposit

        res.json({ // Respond with 200 OK and the updated position details
            success: true, // Signal success for client convenience
            position: { // Group position data under a clear key
                pubkey: pubkey.slice(0, 8) + '...', // Truncate the address for privacy
                staked: position.amount, // Show the total staked amount
                pendingRewards: position.pendingRewards, // Show rewards waiting to be claimed
                shareOfPool: `${((position.amount / pool.totalStaked) * 100).toFixed(4)}%`, // Calculate the user's percentage ownership
            }, // Close position group
            pool: { // Show the updated pool state
                id, // Include the pool ID
                totalStaked: pool.totalStaked, // Show the new global staked total
                stakers: pool.stakers.size, // Show how many unique users are staking
            }, // Close pool state group
        }); // Close response
    } catch (error) { // Catch unexpected math or input errors
        res.status(500).json({ error: `Staking failed: ${error}` }); // Return 500 with details for debugging
    } // Close catch block
}); // Close the stake route

/**
 * POST /stake/:id/claim
 * Claim rewards
 */
app.post('/stake/:id/claim', (req: Request, res: Response) => { // Define the endpoint for withdrawing accrued rewards
    try { // Wrap in try/catch to handle missing pools or positions
        const { id } = req.params; // Read the pool ID from the URL path
        const { pubkey } = req.body; // Read the user's public key from the body
        const pool = pools.get(id); // Fetch the pool from memory

        if (!pool) { // Reject if the pool does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
        } // Close existence check

        const position = pool.stakers.get(pubkey); // Look up the user's position
        if (!position) { // Reject if the user has never staked in this pool
            return res.status(404).json({ error: 'No position found' }); // Return 404 for missing positions
        } // Close position check

        const newRewards = calculateRewards(position, pool.rewardRate, Date.now()); // Calculate rewards earned since the last timing event
        const totalClaimable = position.pendingRewards + newRewards; // Sum previously pending and newly earned rewards

        if (totalClaimable > pool.rewardPoolBalance) { // Ensure the treasury can cover the full claim
            return res.status(400).json({ error: 'Insufficient reward pool balance' }); // Return 400 if the pool is depleted
        } // Close treasury check

        position.totalClaimed += totalClaimable; // Increase the lifetime claimed counter
        position.pendingRewards = 0; // Clear the pending rewards because they are now paid out
        position.stakedAt = Date.now(); // Reset the timer to now for future reward calculations
        pool.totalRewardsDistributed += totalClaimable; // Increase the global cumulative rewards counter
        pool.rewardPoolBalance -= totalClaimable; // Decrease the treasury by the claimed amount

        res.json({ // Respond with 200 OK and the claim details
            success: true, // Signal success for client convenience
            claim: { // Group claim data under a clear key
                amount: totalClaimable, // Show the total tokens claimed in this transaction
                token: pool.rewardToken, // Identify which reward token was paid
                newRewards, // Show how much of the claim came from newly earned rewards
                accumulated: position.pendingRewards, // Show the remaining pending balance after clearing
            }, // Close claim group
            position: { // Show the updated position
                staked: position.amount, // Show the unchanged staked principal
                totalClaimed: position.totalClaimed, // Show the updated lifetime claimed amount
            }, // Close position group
        }); // Close response
    } catch (error) { // Catch unexpected exceptions
        res.status(500).json({ error: `Claim failed: ${error}` }); // Return 500 with details for debugging
    } // Close catch block
}); // Close the claim route

/**
 * POST /stake/:id/unstake
 * Unstake tokens
 */
app.post('/stake/:id/unstake', (req: Request, res: Response) => { // Define the endpoint for unlocking staked tokens
    try { // Wrap in try/catch to handle missing pools, positions, or over-withdrawals
        const { id } = req.params; // Read the pool ID from the URL path
        const { pubkey, amount } = req.body; // Read the user's public key and withdrawal amount from the body
        const pool = pools.get(id); // Fetch the pool from memory

        if (!pool) { // Reject if the pool does not exist
            return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
        } // Close existence check

        const position = pool.stakers.get(pubkey); // Look up the user's position
        if (!position) { // Reject if the user has no stake in this pool
            return res.status(404).json({ error: 'No position found' }); // Return 404 for missing positions
        } // Close position check

        if (amount > position.amount) { // Reject if the user tries to unstake more than they have locked
            return res.status(400).json({ error: 'Insufficient staked amount' }); // Return 400 for invalid withdrawal requests
        } // Close balance check

        // Auto-claim rewards before unstaking so the user does not forfeit accrued earnings
        const rewards = calculateRewards(position, pool.rewardRate, Date.now()); // Calculate rewards earned since last update
        position.pendingRewards += rewards; // Add newly earned rewards to the pending balance
        position.stakedAt = Date.now(); // Reset the timer to now

        const claimable = position.pendingRewards; // Store the total claimable amount
        if (claimable > 0 && claimable <= pool.rewardPoolBalance) { // If there are claimable rewards and the treasury can cover them
            position.totalClaimed += claimable; // Increase lifetime claimed
            pool.totalRewardsDistributed += claimable; // Increase global cumulative rewards
            pool.rewardPoolBalance -= claimable; // Decrease the treasury
            position.pendingRewards = 0; // Clear pending rewards after payout
            msg!("Auto-claimed {} rewards on unstake", claimable); // Log the auto-claim for transparency
        } // Close auto-claim block

        position.amount -= amount; // Reduce the staked amount by the withdrawal
        pool.totalStaked -= amount; // Reduce the global staked total by the withdrawal

        if (position.amount === 0) { // If the user has fully exited their position
            pool.stakers.delete(pubkey); // Remove them from the map to keep storage clean
        } // Close zero-balance cleanup

        res.json({ // Respond with 200 OK and the unstake details
            success: true, // Signal success for client convenience
            unstake: { // Group unstake data under a clear key
                amount, // Show how many tokens were unlocked
                rewardsClaimed: claimable, // Show any rewards that were auto-claimed
            }, // Close unstake group
            position: position.amount > 0 ? { // If the user still has a remaining position
                staked: position.amount, // Show the remaining staked amount
                pendingRewards: position.pendingRewards, // Show any remaining pending rewards
            } : null, // Otherwise return null to indicate full exit
            pool: { // Show the updated pool state
                totalStaked: pool.totalStaked, // Show the reduced global staked total
                stakers: pool.stakers.size, // Show the updated count of unique stakers
                rewardPoolBalance: pool.rewardPoolBalance, // Show the remaining treasury
            }, // Close pool state group
        }); // Close response
    } catch (error) { // Catch unexpected exceptions
        res.status(500).json({ error: `Unstake failed: ${error}` }); // Return 500 with details for debugging
    } // Close catch block
}); // Close the unstake route

/**
 * GET /stake/:id/position/:pubkey
 * Get user position
 */
app.get('/stake/:id/position/:pubkey', (req: Request, res: Response) => { // Define the endpoint to read a specific user's stake
    const pool = pools.get(req.params.id); // Look up the pool by ID from the URL
    if (!pool) { // Reject if the pool does not exist
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
    } // Close existence check

    const position = pool.stakers.get(req.params.pubkey); // Look up the user's position by public key
    if (!position) { // Reject if the user has never staked
        return res.status(404).json({ error: 'No position found' }); // Return 404 for missing positions
    } // Close position check

    const currentRewards = calculateRewards(position, pool.rewardRate, Date.now()); // Calculate rewards earned since the last timing event
    const totalPending = position.pendingRewards + currentRewards; // Sum pending and newly earned for the total available

    res.json({ // Respond with the full position details
        position: { // Nest data under a descriptive key
            pubkey: req.params.pubkey.slice(0, 8) + '...', // Truncate the address for privacy
            staked: position.amount, // Show the staked principal
            pendingRewards: totalPending, // Show the total claimable rewards
            totalClaimed: position.totalClaimed, // Show lifetime rewards already withdrawn
            stakedAt: new Date(position.stakedAt).toISOString(), // Format the last timing event as a readable ISO string
            shareOfPool: `${((position.amount / pool.totalStaked) * 100).toFixed(4)}%`, // Calculate the user's ownership percentage
        }, // Close position group
        pool: { // Include a snapshot of the pool for context
            id: pool.id, // Show the pool ID
            totalStaked: pool.totalStaked, // Show the global staked total
            rewardRate: pool.rewardRate, // Show the current reward rate
            rewardPoolBalance: pool.rewardPoolBalance, // Show the remaining treasury
        }, // Close pool snapshot group
    }); // Close response
}); // Close the position route

/**
 * GET /stake/:id/info
 * Get pool info
 */
app.get('/stake/:id/info', (req: Request, res: Response) => { // Define the endpoint to read pool metadata
    const pool = pools.get(req.params.id); // Look up the pool by ID from the URL
    if (!pool) { // Reject if the pool does not exist
        return res.status(404).json({ error: 'Pool not found' }); // Return 404 for missing resources
    } // Close existence check

    const apr = pool.rewardRate * 31_536_000 * 100; // Calculate simple APR by annualizing the per-second rate
    const apy = ((1 + pool.rewardRate) ** 31_536_000 - 1) * 100; // Calculate APY assuming continuous compounding

    res.json({ // Respond with the full pool information
        pool: { // Nest data under a descriptive key
            id: pool.id, // Show the pool identifier
            token: pool.token, // Show the staked token
            rewardToken: pool.rewardToken, // Show the reward token
            totalStaked: pool.totalStaked, // Show the global staked total
            rewardRate: pool.rewardRate, // Show the per-second reward rate
            apr: `${apr.toFixed(2)}%`, // Format the APR for readability
            apy: `${apy.toFixed(2)}%`, // Format the APY for readability
            stakers: pool.stakers.size, // Show the count of unique participants
            totalRewardsDistributed: pool.totalRewardsDistributed, // Show cumulative payouts
            rewardPoolBalance: pool.rewardPoolBalance, // Show the remaining treasury
            createdAt: new Date(pool.createdAt).toISOString(), // Format the creation time as a readable string
        }, // Close pool group
    }); // Close response
}); // Close the info route

app.listen(PORT, () => { // Start the Express server and bind to the chosen port
    console.log(`=== Phase 18: Staking API ===`); // Print a header identifying this phase API
    console.log(`Server running on http://localhost:${PORT}`); // Print the URL for easy copy-paste into clients
    console.log(`\nEndpoints:`); // Print a section header for the endpoint list
    console.log(`  POST /stake/create            - Create pool`); // Document the create endpoint
    console.log(`  POST /stake/:id/stake         - Stake tokens`); // Document the stake endpoint
    console.log(`  POST /stake/:id/claim         - Claim rewards`); // Document the claim endpoint
    console.log(`  POST /stake/:id/unstake       - Unstake tokens`); // Document the unstake endpoint
    console.log(`  GET  /stake/:id/position/:pk  - User position`); // Document the position endpoint
    console.log(`  GET  /stake/:id/info          - Pool info`); // Document the info endpoint
}); // Close the listen callback
