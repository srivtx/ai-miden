import express, { Request, Response } from 'express'; // Import Express framework to build the REST API server

/**
 * Phase 20: Time-Locked Vault API
 *
 * REST API for time-locked token releases and vesting schedules:
 * POST /timelock/create - Create a time lock vault
 * POST /timelock/:id/lock - Deposit tokens
 * POST /timelock/:id/unlock - Withdraw after unlock time
 * POST /timelock/:id/cancel - Guardian cancels before unlock
 * POST /timelock/:id/claim-vested - Claim according to schedule
 * GET /timelock/:id - Get vault info
 */

const app = express(); // Create the Express application instance to handle HTTP routing
app.use(express.json()); // Enable automatic JSON body parsing so req.body contains parsed objects

const PORT = 3008; // Choose port 3008 to avoid conflicts with other phase APIs running locally

// ============================================================================
// TYPES
// ============================================================================

interface TimeLockVault { // Define the TypeScript shape of a time-locked vault
    id: string; // Unique identifier for the vault
    owner: string; // Public key of the user who owns the locked tokens
    guardian: string; // Public key authorized to cancel the lock before expiration
    amount: number; // Total tokens currently deposited in the vault
    unlockTime: number; // Unix timestamp after which full unlock is permitted
    vestingStart: number; // Unix timestamp when linear vesting begins
    vestingDuration: number; // Total seconds over which tokens vest linearly
    claimed: number; // Tokens already withdrawn through vesting or unlock
    createdAt: number; // Timestamp when the vault was created
}

// ============================================================================
// STORAGE
// ============================================================================

const vaults: Map<string, TimeLockVault> = new Map(); // Store vaults in memory using a Map for fast lookup by ID

// ============================================================================
// HELPERS
// ============================================================================

function calculateVested(vault: TimeLockVault, now: number): number { // Compute how many tokens have vested by the current time
    if (now < vault.vestingStart) { // If the current time is before the vesting start
        return 0; // Return zero because nothing has vested yet
    } // Close the pre-vesting guard
    const elapsed = now - vault.vestingStart; // Calculate seconds since vesting began
    const duration = vault.vestingDuration; // Read the total vesting duration
    if (duration === 0) { // Avoid division by zero if no duration was set
        return vault.amount; // Return the full amount if there is no schedule
    } // Close the zero-duration guard
    const ratio = Math.min(elapsed / duration, 1); // Cap the ratio at one because vesting cannot exceed one hundred percent
    return vault.amount * ratio; // Multiply total amount by the vested fraction
} // Close the vested calculation helper

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => { // Define a health check route for monitoring
    res.json({ status: 'healthy', vaults: vaults.size }); // Respond with the count of active vaults
}); // Close the health route

/**
 * POST /timelock/create
 * Create a time lock vault
 */
app.post('/timelock/create', (req: Request, res: Response) => { // Define the endpoint to initialize a new vault
    try { // Wrap in try/catch to handle malformed input gracefully
        const { owner, guardian, unlockTime, vestingStart, vestingDuration } = req.body; // Extract vault parameters

        if (!owner || !guardian || !unlockTime) { // Validate that all required fields are present
            return res.status(400).json({ error: 'Missing parameters' }); // Return 400 for incomplete requests
        } // Close validation

        const id = `vault_${owner.slice(0, 8)}_${Date.now()}`; // Generate a unique ID from the owner and timestamp

        if (vaults.has(id)) { // Prevent duplicate vault IDs
            return res.status(409).json({ error: 'Vault already exists' }); // Return 409 for duplicates
        } // Close duplicate check

        const vault: TimeLockVault = { // Construct the vault object
            id, // Assign the generated ID
            owner, // Store the vault owner
            guardian, // Store the authorized guardian
            amount: 0, // Start with zero deposited tokens
            unlockTime, // Store the absolute unlock timestamp
            vestingStart: vestingStart || unlockTime, // Default vesting start to unlock time if not provided
            vestingDuration: vestingDuration || 0, // Default vesting duration to zero if not provided
            claimed: 0, // Initialize claimed tokens to zero
            createdAt: Date.now(), // Record the creation timestamp
        }; // Close vault construction

        vaults.set(id, vault); // Save the vault into memory

        res.status(201).json({ // Respond with 201 Created
            success: true, // Signal success explicitly
            vault: { // Nest vault details under a clear key
                id, // Echo back the ID
                owner: owner.slice(0, 8) + '...', // Truncate owner address for privacy
                guardian: guardian.slice(0, 8) + '...', // Truncate guardian address for privacy
                unlockTime: new Date(unlockTime * 1000).toISOString(), // Format unlock time as a readable ISO string
                vestingStart: new Date(vault.vestingStart * 1000).toISOString(), // Format vesting start as a readable string
                vestingDuration: vault.vestingDuration, // Show the vesting duration in seconds
            }, // Close vault detail group
        }); // Close response
    } catch (error) { // Catch unexpected exceptions
        res.status(500).json({ error: `Failed to create vault: ${error}` }); // Return 500 for debugging
    } // Close catch
}); // Close the create route

/**
 * POST /timelock/:id/lock
 * Deposit tokens into the vault
 */
app.post('/timelock/:id/lock', (req: Request, res: Response) => { // Define the endpoint for depositing tokens
    try { // Wrap in try/catch
        const { id } = req.params; // Read the vault ID from the URL path
        const { owner, amount } = req.body; // Read the owner and deposit amount from the body
        const vault = vaults.get(id); // Fetch the vault from memory

        if (!vault) { // Reject if the vault does not exist
            return res.status(404).json({ error: 'Vault not found' }); // Return 404
        } // Close existence check

        if (vault.owner !== owner) { // Reject if the caller is not the vault owner
            return res.status(403).json({ error: 'Only vault owner can lock tokens' }); // Return 403 for unauthorized access
        } // Close ownership check

        vault.amount += amount; // Increase the locked amount by the deposit

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            lock: { // Group lock details
                amount, // Echo the deposited amount
                totalLocked: vault.amount, // Show the new total locked balance
            }, // Close lock group
            vault: { // Show updated vault
                id, // Include the vault ID
                amount: vault.amount, // Show the updated amount
            }, // Close vault group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Lock failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the lock route

/**
 * POST /timelock/:id/unlock
 * Withdraw tokens after unlock time
 */
app.post('/timelock/:id/unlock', (req: Request, res: Response) => { // Define the endpoint for full withdrawal after expiration
    try { // Wrap in try/catch
        const { id } = req.params; // Read the vault ID from the URL
        const { owner } = req.body; // Read the owner from the body
        const vault = vaults.get(id); // Fetch the vault
        const now = Math.floor(Date.now() / 1000); // Get the current Unix timestamp in seconds

        if (!vault) { // Reject if the vault does not exist
            return res.status(404).json({ error: 'Vault not found' }); // Return 404
        } // Close existence check

        if (vault.owner !== owner) { // Reject if the caller is not the owner
            return res.status(403).json({ error: 'Only vault owner can unlock tokens' }); // Return 403
        } // Close ownership check

        if (now < vault.unlockTime) { // Reject if the unlock time has not yet been reached
            return res.status(400).json({ // Return 400 with details
                error: 'Unlock time not reached', // Explain the failure
                now: new Date(now * 1000).toISOString(), // Show current time
                unlockTime: new Date(vault.unlockTime * 1000).toISOString(), // Show unlock time
                secondsRemaining: vault.unlockTime - now, // Show how many seconds are left
            }); // Close error response
        } // Close time check

        const withdrawAmount = vault.amount - vault.claimed; // Calculate the remaining unclaimed tokens
        vault.claimed = vault.amount; // Mark all tokens as claimed because this is a full unlock

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            unlock: { // Group unlock details
                amount: withdrawAmount, // Show how many tokens were withdrawn
                unlockedAt: new Date(now * 1000).toISOString(), // Show the unlock timestamp
            }, // Close unlock group
            vault: { // Show updated vault
                id, // Include the vault ID
                claimed: vault.claimed, // Show the updated claimed amount
                remaining: vault.amount - vault.claimed, // Show the remaining balance
            }, // Close vault group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Unlock failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the unlock route

/**
 * POST /timelock/:id/cancel
 * Guardian cancels the lock before unlock time
 */
app.post('/timelock/:id/cancel', (req: Request, res: Response) => { // Define the endpoint for guardian cancellation
    try { // Wrap in try/catch
        const { id } = req.params; // Read the vault ID from the URL
        const { guardian } = req.body; // Read the guardian from the body
        const vault = vaults.get(id); // Fetch the vault
        const now = Math.floor(Date.now() / 1000); // Get the current Unix timestamp

        if (!vault) { // Reject if the vault does not exist
            return res.status(404).json({ error: 'Vault not found' }); // Return 404
        } // Close existence check

        if (vault.guardian !== guardian) { // Reject if the caller is not the authorized guardian
            return res.status(403).json({ error: 'Only guardian can cancel lock' }); // Return 403
        } // Close guardian check

        if (now >= vault.unlockTime) { // Reject if the lock has already expired
            return res.status(400).json({ error: 'Lock already expired, cannot cancel' }); // Return 400
        } // Close expiration check

        const returnAmount = vault.amount - vault.claimed; // Calculate the remaining tokens to return
        vault.claimed = vault.amount; // Mark all tokens as returned to prevent double withdrawal

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            cancel: { // Group cancellation details
                returnedAmount: returnAmount, // Show how many tokens are being returned
                cancelledAt: new Date(now * 1000).toISOString(), // Show the cancellation timestamp
            }, // Close cancel group
            vault: { // Show updated vault
                id, // Include the vault ID
                claimed: vault.claimed, // Show the updated claimed amount
                status: 'cancelled', // Label the vault as cancelled for UI clarity
            }, // Close vault group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Cancel failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the cancel route

/**
 * POST /timelock/:id/claim-vested
 * Claim tokens according to the vesting schedule
 */
app.post('/timelock/:id/claim-vested', (req: Request, res: Response) => { // Define the endpoint for vesting claims
    try { // Wrap in try/catch
        const { id } = req.params; // Read the vault ID from the URL
        const { owner } = req.body; // Read the owner from the body
        const vault = vaults.get(id); // Fetch the vault
        const now = Math.floor(Date.now() / 1000); // Get the current Unix timestamp

        if (!vault) { // Reject if the vault does not exist
            return res.status(404).json({ error: 'Vault not found' }); // Return 404
        } // Close existence check

        if (vault.owner !== owner) { // Reject if the caller is not the owner
            return res.status(403).json({ error: 'Only vault owner can claim vested tokens' }); // Return 403
        } // Close ownership check

        if (now < vault.vestingStart) { // Reject if vesting has not yet started
            return res.status(400).json({ // Return 400 with details
                error: 'Vesting has not started', // Explain the failure
                now: new Date(now * 1000).toISOString(), // Show current time
                vestingStart: new Date(vault.vestingStart * 1000).toISOString(), // Show vesting start
            }); // Close error response
        } // Close pre-vesting check

        const totalVested = calculateVested(vault, now); // Compute the total vested amount based on elapsed time
        const claimable = totalVested - vault.claimed; // Calculate how many tokens are newly available

        if (claimable <= 0) { // Reject if there are no new tokens to claim
            return res.status(400).json({ error: 'No vested tokens available to claim' }); // Return 400
        } // Close zero-claimable check

        vault.claimed += claimable; // Increase the lifetime claimed counter

        res.json({ // Respond with 200 OK
            success: true, // Signal success
            claim: { // Group claim details
                amount: claimable, // Show how many tokens were claimed
                totalVested, // Show the cumulative vested amount
                remainingLocked: vault.amount - totalVested, // Show how many tokens are still locked
            }, // Close claim group
            vault: { // Show updated vault
                id, // Include the vault ID
                claimed: vault.claimed, // Show the updated claimed amount
                vestingProgress: `${((totalVested / vault.amount) * 100).toFixed(2)}%`, // Format vesting progress as a percentage
            }, // Close vault group
        }); // Close response
    } catch (error) { // Catch unexpected errors
        res.status(500).json({ error: `Claim failed: ${error}` }); // Return 500
    } // Close catch
}); // Close the claim-vested route

/**
 * GET /timelock/:id
 * Get vault info
 */
app.get('/timelock/:id', (req: Request, res: Response) => { // Define the endpoint to read vault state
    const vault = vaults.get(req.params.id); // Fetch the vault by ID
    if (!vault) { // Reject if the vault does not exist
        return res.status(404).json({ error: 'Vault not found' }); // Return 404
    } // Close existence check

    const now = Math.floor(Date.now() / 1000); // Get the current Unix timestamp
    const totalVested = calculateVested(vault, now); // Compute the current vested amount
    const claimable = totalVested - vault.claimed; // Calculate tokens available for immediate claim
    const isUnlocked = now >= vault.unlockTime; // Determine if the full unlock time has passed

    res.json({ // Respond with the full vault state
        vault: { // Nest data under a descriptive key
            id: vault.id, // Show the vault ID
            owner: vault.owner.slice(0, 8) + '...', // Truncate owner address
            guardian: vault.guardian.slice(0, 8) + '...', // Truncate guardian address
            amount: vault.amount, // Show total deposited tokens
            unlockTime: new Date(vault.unlockTime * 1000).toISOString(), // Format unlock time
            isUnlocked, // Show whether full unlock is available
            vestingStart: new Date(vault.vestingStart * 1000).toISOString(), // Format vesting start
            vestingDuration: vault.vestingDuration, // Show vesting duration in seconds
            totalVested, // Show cumulative vested amount
            claimed: vault.claimed, // Show lifetime claimed amount
            claimable, // Show currently available tokens
            remainingLocked: vault.amount - totalVested, // Show tokens still subject to the schedule
            vestingProgress: vault.amount > 0 ? `${((totalVested / vault.amount) * 100).toFixed(2)}%` : '0%', // Format progress
        }, // Close vault group
    }); // Close response
}); // Close the vault info route

app.listen(PORT, () => { // Start the Express server on the chosen port
    console.log(`=== Phase 20: Time-Locked Vault API ===`); // Print a header identifying this API
    console.log(`Server running on http://localhost:${PORT}`); // Print the URL for easy testing
    console.log(`\nEndpoints:`); // Print a section header
    console.log(`  POST /timelock/create           - Create vault`); // Document the create endpoint
    console.log(`  POST /timelock/:id/lock         - Deposit tokens`); // Document the lock endpoint
    console.log(`  POST /timelock/:id/unlock       - Withdraw after unlock`); // Document the unlock endpoint
    console.log(`  POST /timelock/:id/cancel       - Guardian cancel`); // Document the cancel endpoint
    console.log(`  POST /timelock/:id/claim-vested - Claim vested tokens`); // Document the claim endpoint
    console.log(`  GET  /timelock/:id              - Vault info`); // Document the info endpoint
}); // Close the listen callback
