import express from "express"; // Import the express framework to build the HTTP server for vesting operations
import cors from "cors"; // Import cors middleware to allow browser clients to interact with this API from different origins

const app = express(); // Create the express application instance that will handle vesting routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects
app.use(cors()); // Enable CORS so frontend dashboards can query vesting status without preflight errors

interface VestingGrant { // Define a TypeScript interface for an in-memory vesting record to ensure type safety across endpoints
    id: string; // Store a unique identifier for each grant so clients can reference specific allocations
    grantor: string; // Store the wallet address of the party allocating tokens so revocation rights can be enforced
    beneficiary: string; // Store the wallet address of the party receiving tokens so claims are routed correctly
    totalAmount: number; // Store the total token grant so the contract knows the maximum that can ever vest
    startTime: number; // Store the Unix timestamp when vesting begins so elapsed time can be computed
    durationSeconds: number; // Store the total vesting duration so the linear rate can be calculated
    cliffSeconds: number; // Store the cliff duration so the contract can block claims before the minimum period
    claimed: number; // Track how many tokens have already been claimed so double claims are prevented
    revoked: boolean; // Store whether the grantor has revoked the grant so unvested tokens can be returned
} // Close the VestingGrant interface definition

const grants: VestingGrant[] = []; // Initialize an in-memory array to store vesting grants because this is a teaching demo without a database

let nextId = 1; // Initialize a simple counter to generate unique grant IDs sequentially

function nowSeconds(): number { // Define a helper to get the current time in seconds because vesting calculations use second-level granularity
    return Math.floor(Date.now() / 1000); // Convert millisecond timestamps to whole seconds for deterministic interval math
} // Close the nowSeconds helper

function calculateVestedAmount(grant: VestingGrant, currentTime: number): number { // Define a helper to compute how many tokens are vested at a given timestamp
    if (grant.revoked) { // Check if the grant has been revoked because revoked grants stop vesting immediately
        return grant.claimed; // Return only already claimed tokens because unvested tokens were returned to the grantor
    } // Close the revoked check
    const elapsed = currentTime - grant.startTime; // Calculate how many seconds have passed since vesting started
    if (elapsed <= grant.cliffSeconds) { // Check if the current time is still inside the cliff period so zero tokens are vested
        return 0; // Return zero because the cliff prevents any unlocks before the minimum commitment period
    } // Close the cliff check
    if (elapsed >= grant.durationSeconds) { // Check if the full duration has passed so the entire grant is vested
        return grant.totalAmount; // Return the total amount because all tokens have finished vesting
    } // Close the fully vested check
    const fraction = elapsed / grant.durationSeconds; // Compute the fraction of the total duration that has elapsed for linear interpolation
    return Math.floor(grant.totalAmount * fraction); // Calculate vested tokens proportionally and floor to avoid fractional token issues
} // Close the calculateVestedAmount helper

app.post("/grant", (req, res) => { // Define an endpoint to create a new token vesting grant from a grantor to a beneficiary
    const { grantor, beneficiary, totalAmount, durationSeconds, cliffSeconds } = req.body; // Destructure request fields so validation can be performed
    if (!grantor || !beneficiary || !totalAmount || !durationSeconds) { // Validate that every required field is present so incomplete grants are rejected
        return res.status(400).json({ error: "Missing required fields: grantor, beneficiary, totalAmount, durationSeconds" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    if (totalAmount <= 0 || durationSeconds <= 0) { // Validate that numeric inputs are positive because negative or zero values break vesting logic
        return res.status(400).json({ error: "totalAmount and durationSeconds must be positive" }); // Return 400 so the client cannot create malformed grants
    } // Close the positive value validation block
    if (cliffSeconds && cliffSeconds >= durationSeconds) { // Validate that the cliff is shorter than the total duration so some linear vesting can occur
        return res.status(400).json({ error: "cliffSeconds must be less than durationSeconds" }); // Return 400 because a cliff equal to duration leaves no vesting period
    } // Close the cliff duration validation block
    const grant: VestingGrant = { // Construct a new vesting grant object with all fields initialized
        id: String(nextId++), // Assign the next sequential ID and increment the counter so future grants get unique identifiers
        grantor, // Store the grantor from the request so the server knows who can revoke the grant
        beneficiary, // Store the beneficiary from the request so the server knows who is entitled to claim
        totalAmount, // Store the total token amount so the contract knows the upper bound of vesting
        startTime: nowSeconds(), // Record the current timestamp as the vesting start so elapsed time calculations have a baseline
        durationSeconds, // Store the total duration so the linear rate and end date can be computed
        cliffSeconds: cliffSeconds || 0, // Store the cliff duration defaulting to zero so immediate vesting is supported
        claimed: 0, // Initialize claimed amount to zero because no tokens have been released yet
        revoked: false, // Mark the grant as active so claims and revocations behave correctly
    }; // Close the grant object creation
    grants.push(grant); // Append the new grant to the in-memory array so it can be queried and claimed later
    return res.status(201).json({ // Return a 201 Created response so the client knows the resource was successfully created
        success: true, // Include a success flag so programmatic clients can check status without deep body parsing
        grant, // Return the full grant object so the client receives the generated ID and timestamps
    }); // Close the success response
}); // Close the POST /grant route

app.post("/claim", (req, res) => { // Define an endpoint to let a beneficiary claim tokens that have vested since the last claim
    const { grantId, claimer } = req.body; // Destructure the claim parameters so the server knows which grant and who is claiming
    if (!grantId || !claimer) { // Validate that both fields are provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing grantId or claimer" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const grant = grants.find((g) => g.id === grantId); // Search the in-memory array for the requested grant so claims target the correct allocation
    if (!grant) { // Check if the grant exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Grant not found" }); // Return 404 so the client knows the ID is invalid
    } // Close the existence check
    if (grant.revoked) { // Check if the grant has been revoked because revoked allocations should not allow new claims
        return res.status(400).json({ error: "Grant has been revoked" }); // Return 400 so the client knows the agreement is terminated
    } // Close the revoked check
    if (grant.beneficiary !== claimer) { // Verify that the claimer matches the stored beneficiary so unauthorized wallets cannot drain the grant
        return res.status(403).json({ error: "Only the beneficiary can claim" }); // Return 403 so attackers learn that access is denied
    } // Close the beneficiary authorization block
    const currentTime = nowSeconds(); // Capture the current time so vested calculations use a consistent timestamp
    const vested = calculateVestedAmount(grant, currentTime); // Compute the total tokens vested up to now so the claim amount can be determined
    const claimable = vested - grant.claimed; // Subtract already claimed tokens so only new unlocks are transferred
    if (claimable <= 0) { // Check if there is anything new to claim so empty claims return a clear message
        return res.status(400).json({ error: "No tokens available to claim" }); // Return 400 so the client knows vesting has not progressed
    } // Close the empty claim check
    grant.claimed += claimable; // Increase the claimed total so future claims reflect the updated state
    return res.status(200).json({ // Return the claim result so the beneficiary knows how much was transferred
        success: true, // Confirm the operation succeeded so clients can update their UI state
        claimed: claimable, // Report the exact amount claimed so accounting records stay accurate
        totalClaimed: grant.claimed, // Report the lifetime claimed amount so the beneficiary tracks their progress
        grant, // Return the updated grant so the client sees the new totals
    }); // Close the success response
}); // Close the POST /claim route

app.post("/revoke", (req, res) => { // Define an endpoint to let a grantor revoke unvested tokens and return them
    const { grantId, requester } = req.body; // Destructure revocation parameters so the server knows which grant and who requested it
    if (!grantId || !requester) { // Validate that both fields are present so the server can perform authorization checks
        return res.status(400).json({ error: "Missing grantId or requester" }); // Return 400 so the client sends complete input
    } // Close the input validation block
    const grant = grants.find((g) => g.id === grantId); // Locate the grant in memory so revocation targets the correct record
    if (!grant) { // Ensure the grant exists so the server does not modify undefined state
        return res.status(404).json({ error: "Grant not found" }); // Return 404 so the client knows the ID is invalid
    } // Close the existence check
    if (grant.grantor !== requester) { // Verify that the requester is the grantor so unauthorized wallets cannot cancel others' allocations
        return res.status(403).json({ error: "Only the grantor can revoke" }); // Return 403 so unauthorized actors know they are rejected
    } // Close the authorization check
    if (grant.revoked) { // Prevent double revocation because an already revoked grant has no unvested tokens to return
        return res.status(400).json({ error: "Grant already revoked" }); // Return 400 so the client knows the agreement is already ended
    } // Close the revoked check
    const currentTime = nowSeconds(); // Capture the current time so vested calculations determine how much must stay with the beneficiary
    const vested = calculateVestedAmount(grant, currentTime); // Compute the tokens the beneficiary has earned so they are protected from revocation
    const returned = grant.totalAmount - vested; // Compute the unvested remainder so the exact return amount can be reported
    grant.revoked = true; // Mark the grant as revoked so future claims are blocked and unvested tokens are conceptually returned
    return res.status(200).json({ // Return the revocation result so both parties know the final state
        success: true, // Indicate that the revocation was processed so clients can update their UI
        returned, // Report the returned unvested amount so the grantor knows what was recovered
        beneficiaryKeeps: vested, // Report the vested amount that remains with the beneficiary so fairness is transparent
        grant, // Return the updated grant so the client sees the revoked flag
    }); // Close the success response
}); // Close the POST /revoke route

app.get("/grants", (req, res) => { // Define an endpoint to list all grants for dashboard or audit purposes
    return res.status(200).json({ // Return the full list so clients can browse allocations
        count: grants.length, // Include the total count so summary widgets can display it
        grants, // Return the array of grant objects so the client receives complete data
    }); // Close the success response
}); // Close the GET /grants route

app.get("/grants/:id", (req, res) => { // Define an endpoint to fetch a single grant by its unique ID
    const id = req.params.id; // Extract the ID from the URL path so the server can look up the specific record
    const grant = grants.find((g) => g.id === id); // Search the array for the matching ID so the correct grant is returned
    if (!grant) { // Check if the grant exists so the server returns a proper error instead of null
        return res.status(404).json({ error: "Grant not found" }); // Return 404 so the client knows the ID does not exist
    } // Close the existence check
    const currentVested = calculateVestedAmount(grant, nowSeconds()); // Compute the current vested amount so the client sees real-time progress
    return res.status(200).json({ // Return the found grant with live calculations so the client can display its details
        grant, // Include the full grant object so the client sees all fields
        currentVested, // Include the real-time vested amount so the beneficiary knows how much is unlocked
        currentClaimable: currentVested - grant.claimed, // Include the difference so the client knows the exact claimable balance
    }); // Close the success response
}); // Close the GET /grants/:id route

app.listen(3041, () => { // Start the HTTP server on port 3041 because this phase owns that port to avoid conflicts with other APIs
    console.log("Vesting API listening on port 3041"); // Log startup so operators know the service is ready to accept connections
}); // Close the listen callback
