import express from "express"; // Import the express framework to build the HTTP server for subscription operations
import cors from "cors"; // Import cors middleware to allow cross-origin requests from frontend clients

const app = express(); // Create the express application instance that will handle subscription routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects
app.use(cors()); // Enable CORS so browser-based dashboards can interact with this API without preflight errors

interface Subscription { // Define a TypeScript interface for an in-memory subscription record to ensure type safety
    id: string; // Store a unique identifier for each subscription so clients can reference specific agreements
    payer: string; // Store the wallet address of the party depositing funds so access control can be enforced
    payee: string; // Store the wallet address of the party receiving funds so claims are routed correctly
    amountPerInterval: number; // Store the fixed amount released each billing cycle so the contract knows the claim size
    intervalSeconds: number; // Store the duration between claims so the server can calculate eligibility
    totalDeposited: number; // Store the initial deposit so the server knows the maximum funds available
    totalClaimed: number; // Track cumulative funds released so the server can prevent over-claims
    lastClaimTime: number; // Record the Unix timestamp of the most recent claim so intervals can be measured
    createdAt: number; // Record the Unix timestamp when the subscription was created for audit and display
    active: boolean; // Store whether the subscription is still live so cancelled agreements reject new claims
} // Close the Subscription interface definition

const subscriptions: Subscription[] = []; // Initialize an in-memory array to store subscriptions because this is a teaching demo without a database

let nextId = 1; // Initialize a simple counter to generate unique subscription IDs sequentially

function nowSeconds(): number { // Define a helper to get the current time in seconds because subscriptions use second-level granularity
    return Math.floor(Date.now() / 1000); // Convert millisecond timestamps to whole seconds for cleaner interval math
} // Close the nowSeconds helper

app.post("/subscribe", (req, res) => { // Define an endpoint to create a new subscription agreement between a payer and payee
    const { payer, payee, amountPerInterval, intervalSeconds, totalDeposited } = req.body; // Destructure request fields so validation can be performed
    if (!payer || !payee || !amountPerInterval || !intervalSeconds || !totalDeposited) { // Validate that every required field is present so incomplete subscriptions are rejected
        return res.status(400).json({ error: "Missing required fields: payer, payee, amountPerInterval, intervalSeconds, totalDeposited" }); // Return 400 with a descriptive message so the client knows what is wrong
    } // Close the required field validation block
    if (amountPerInterval <= 0 || intervalSeconds <= 0 || totalDeposited <= 0) { // Validate that numeric inputs are positive because negative or zero values break the payment logic
        return res.status(400).json({ error: "amountPerInterval, intervalSeconds, and totalDeposited must be positive" }); // Return 400 so the client cannot create malformed subscriptions
    } // Close the positive value validation block
    if (amountPerInterval > totalDeposited) { // Validate that a single interval does not exceed the deposit so at least one claim is possible
        return res.status(400).json({ error: "amountPerInterval cannot exceed totalDeposited" }); // Return 400 because such a subscription would immediately exhaust and confuse users
    } // Close the interval cap validation block
    const subscription: Subscription = { // Construct a new subscription object with all fields initialized
        id: String(nextId++), // Assign the next sequential ID and increment the counter so future subscriptions get unique identifiers
        payer, // Store the payer from the request so the server knows who funded the subscription
        payee, // Store the payee from the request so the server knows who is entitled to claim
        amountPerInterval, // Store the periodic claim amount so the contract releases the correct quantity each cycle
        intervalSeconds, // Store the time between claims so eligibility windows can be computed
        totalDeposited, // Store the initial escrow amount so the server knows the upper bound of total claims
        totalClaimed: 0, // Initialize claimed amount to zero because no funds have been released yet
        lastClaimTime: nowSeconds(), // Set the last claim time to now so the first interval starts immediately
        createdAt: nowSeconds(), // Record the creation timestamp so dashboards can show subscription age
        active: true, // Mark the subscription as active so claims and cancellations behave correctly
    }; // Close the subscription object creation
    subscriptions.push(subscription); // Append the new subscription to the in-memory array so it can be queried later
    return res.status(201).json({ // Return a 201 Created response so the client knows the resource was successfully created
        success: true, // Include a success flag so programmatic clients can check status without parsing the body deeply
        subscription, // Return the full subscription object so the client receives the generated ID and timestamps
    }); // Close the success response
}); // Close the POST /subscribe route

app.post("/claim", (req, res) => { // Define an endpoint to let a payee claim funds that have become eligible since the last claim
    const { subscriptionId, claimer } = req.body; // Destructure the claim parameters so the server knows which subscription and who is claiming
    if (!subscriptionId || !claimer) { // Validate that both fields are provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing subscriptionId or claimer" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const sub = subscriptions.find((s) => s.id === subscriptionId); // Search the in-memory array for the requested subscription so claims target the correct agreement
    if (!sub) { // Check if the subscription exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Subscription not found" }); // Return 404 so the client knows the ID is invalid
    } // Close the existence check
    if (!sub.active) { // Check if the subscription is still active because cancelled agreements should not allow new claims
        return res.status(400).json({ error: "Subscription is inactive" }); // Return 400 so the client knows the agreement has ended
    } // Close the active check
    if (sub.payee !== claimer) { // Verify that the claimer matches the stored payee so unauthorized wallets cannot drain the escrow
        return res.status(403).json({ error: "Only the designated payee can claim" }); // Return 403 so attackers learn that access is denied
    } // Close the payee authorization block
    const elapsed = nowSeconds() - sub.lastClaimTime; // Calculate how many seconds have passed since the last claim so interval math can be applied
    const intervalsDue = Math.floor(elapsed / sub.intervalSeconds); // Compute how many full billing cycles have elapsed so the claim amount is deterministic
    if (intervalsDue < 1) { // Require at least one full interval so claims cannot happen continuously within a single cycle
        return res.status(400).json({ error: "No full interval has elapsed since last claim" }); // Return 400 so the client waits for the next cycle
    } // Close the interval eligibility check
    const claimAmount = intervalsDue * sub.amountPerInterval; // Compute the total tokens that became eligible across all due intervals
    const remaining = sub.totalDeposited - sub.totalClaimed; // Compute how much unclaimed balance remains so the server caps the payout
    const actualClaim = Math.min(claimAmount, remaining); // Cap the claim at the remaining balance so the escrow never goes negative
    if (actualClaim <= 0) { // Check if there is anything left to claim so empty escrows return a clear message
        return res.status(400).json({ error: "Subscription fully claimed" }); // Return 400 so the client knows the funds are exhausted
    } // Close the empty escrow check
    sub.totalClaimed += actualClaim; // Increase the claimed total so future claims reflect the updated state
    sub.lastClaimTime += intervalsDue * sub.intervalSeconds; // Advance the last claim time by whole intervals so partial intervals carry over
    if (sub.totalClaimed >= sub.totalDeposited) { // Check if the escrow is fully exhausted so the subscription can be auto-finalized
        sub.active = false; // Mark the subscription inactive because there are no more funds to release
    } // Close the auto-finalization block
    return res.status(200).json({ // Return the claim result so the payee knows how much was transferred
        success: true, // Confirm the operation succeeded so clients can update their UI state
        claimed: actualClaim, // Report the exact amount claimed so accounting records stay accurate
        subscription: sub, // Return the updated subscription so the client sees the new totals and timestamps
    }); // Close the success response
}); // Close the POST /claim route

app.post("/cancel", (req, res) => { // Define an endpoint to let either party cancel the subscription and return unclaimed funds
    const { subscriptionId, requester } = req.body; // Destructure cancellation parameters so the server knows which agreement and who requested it
    if (!subscriptionId || !requester) { // Validate that both fields are present so the server can perform authorization checks
        return res.status(400).json({ error: "Missing subscriptionId or requester" }); // Return 400 so the client sends complete input
    } // Close the input validation block
    const sub = subscriptions.find((s) => s.id === subscriptionId); // Locate the subscription in memory so cancellation targets the correct record
    if (!sub) { // Ensure the subscription exists so the server does not modify undefined state
        return res.status(404).json({ error: "Subscription not found" }); // Return 404 so the client knows the ID is invalid
    } // Close the existence check
    if (!sub.active) { // Prevent double cancellation because an already inactive subscription has no unclaimed funds to return
        return res.status(400).json({ error: "Subscription already inactive" }); // Return 400 so the client knows the agreement is already ended
    } // Close the active check
    if (sub.payer !== requester && sub.payee !== requester) { // Verify that the requester is a party to the agreement so random wallets cannot cancel others' subscriptions
        return res.status(403).json({ error: "Only the payer or payee can cancel" }); // Return 403 so unauthorized actors know they are rejected
    } // Close the authorization check
    const refund = sub.totalDeposited - sub.totalClaimed; // Compute how much remains unclaimed so the exact refund amount can be reported
    sub.active = false; // Mark the subscription inactive so future claims are rejected
    return res.status(200).json({ // Return the cancellation result so both parties know the final state
        success: true, // Indicate that the cancellation was processed so clients can update their UI
        refund, // Report the refunded amount so the payer knows what was returned
        totalClaimed: sub.totalClaimed, // Report the lifetime claimed amount so the payee knows what they earned
        subscription: sub, // Return the updated subscription so the client sees the inactive flag
    }); // Close the success response
}); // Close the POST /cancel route

app.get("/subscriptions", (req, res) => { // Define an endpoint to list all subscriptions for dashboard or audit purposes
    return res.status(200).json({ // Return the full list so clients can browse agreements
        count: subscriptions.length, // Include the total count so pagination or summary widgets can display it
        subscriptions, // Return the array of subscription objects so the client receives complete data
    }); // Close the success response
}); // Close the GET /subscriptions route

app.get("/subscriptions/:id", (req, res) => { // Define an endpoint to fetch a single subscription by its unique ID
    const id = req.params.id; // Extract the ID from the URL path so the server can look up the specific record
    const sub = subscriptions.find((s) => s.id === id); // Search the array for the matching ID so the correct subscription is returned
    if (!sub) { // Check if the subscription exists so the server returns a proper error instead of null
        return res.status(404).json({ error: "Subscription not found" }); // Return 404 so the client knows the ID does not exist
    } // Close the existence check
    return res.status(200).json({ // Return the found subscription so the client can display its details
        subscription: sub, // Include the full subscription object so the client sees all fields
    }); // Close the success response
}); // Close the GET /subscriptions/:id route

app.listen(3040, () => { // Start the HTTP server on port 3040 because this phase owns that port to avoid conflicts with other APIs
    console.log("Subscription API listening on port 3040"); // Log startup so operators know the service is ready to accept connections
}); // Close the listen callback
