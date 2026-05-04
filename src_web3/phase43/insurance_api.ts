import express from "express"; // Import the express framework to build the HTTP server
import bodyParser from "body-parser"; // Import body-parser to parse JSON request bodies

const app = express(); // Create the express application instance
app.use(bodyParser.json()); // Attach middleware to parse incoming JSON request bodies

interface Policy { // Define the shape of an insurance policy for type safety
    id: string; // Store a unique identifier so each policy can be referenced individually
    policyholder: string; // Store the address of the insured party who pays premiums and receives payouts
    coverageAmount: number; // Store the maximum payout the policy guarantees for a verified claim
    premium: number; // Store the upfront or periodic cost paid by the policyholder
    riskType: string; // Store the category of covered event for underwriting and routing
    active: boolean; // Store whether the policy is currently in force or has expired
}

interface Claim { // Define the shape of an insurance claim for type safety
    id: string; // Store a unique identifier so each claim can be tracked individually
    policyId: string; // Store the reference to the policy against which the claim is filed
    amount: number; // Store the requested payout amount for the claim
    status: "pending" | "verified" | "rejected" | "paid"; // Store the current state in the verification lifecycle
    evidence: string; // Store a description or hash of the evidence supporting the claim
    challengeDeadline: number; // Store the timestamp after which the challenge window closes
}

let poolBalance = 1000000; // Initialize the premium pool with $1,000,000 to ensure solvency at genesis
let policies: Policy[] = []; // Initialize an in-memory array to hold all active policies
let claims: Claim[] = []; // Initialize an in-memory array to hold all filed claims
let oracleThreshold = 50000; // Define the minimum loss threshold in dollars that an oracle must confirm for a claim

app.post("/pool/deposit", (req, res) => { // Define endpoint to deposit capital into the premium pool
    const { amount, provider } = req.body; // Extract deposit parameters from the request body
    if (!amount || amount <= 0 || !provider) { // Validate that the amount is positive and the provider is specified
        return res.status(400).json({ error: "Valid amount and provider required" }); // Return 400 if input is invalid
    } // Close the validation block
    poolBalance += amount; // Increase the pool balance by the deposited amount
    return res.status(200).json({ // Return the updated pool state to the client
        message: "Capital deposited", // Confirm that the deposit was accepted
        provider, // Echo the provider address for reference
        amount, // Echo the deposited amount
        newPoolBalance: poolBalance, // Return the updated total pool balance
    }); // Close the success response
}); // Close the POST /pool/deposit route

app.post("/policy/purchase", (req, res) => { // Define endpoint to purchase a new insurance policy
    const { policyholder, coverageAmount, premium, riskType } = req.body; // Extract policy parameters from the request body
    if (!policyholder || !coverageAmount || !premium || !riskType) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing required policy fields" }); // Return 400 if input is incomplete
    } // Close the validation block
    if (coverageAmount > poolBalance * 0.1) { // Enforce a maximum coverage limit of 10% of pool to prevent concentration risk
        return res.status(400).json({ error: "Coverage exceeds 10% of pool balance" }); // Return 400 if the policy would overextend the pool
    } // Close the coverage limit block
    const policy: Policy = { // Build the policy object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the policy
        policyholder, // Assign the policyholder address from the request
        coverageAmount, // Assign the coverage amount from the request
        premium, // Assign the premium from the request
        riskType, // Assign the risk type from the request
        active: true, // Mark the policy as active at creation
    }; // Close the policy object
    policies.push(policy); // Add the new policy to the global in-memory array
    poolBalance += premium; // Add the premium payment to the pool balance immediately
    return res.status(201).json({ // Return the created policy to the client
        message: "Policy purchased", // Confirm that the policy was created successfully
        policy, // Include the full policy details for client reference
        newPoolBalance: poolBalance, // Return the updated pool balance after premium collection
    }); // Close the success response
}); // Close the POST /policy/purchase route

app.post("/claim/file", (req, res) => { // Define endpoint to file a new insurance claim
    const { policyId, amount, evidence } = req.body; // Extract claim parameters from the request body
    if (!policyId || !amount || !evidence) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing required claim fields" }); // Return 400 if input is incomplete
    } // Close the validation block
    const policy = policies.find((p) => p.id === policyId); // Search the array for a policy matching the provided ID
    if (!policy) { // Check if the policy was found
        return res.status(404).json({ error: "Policy not found" }); // Return 404 if the policy ID does not exist
    } // Close the not-found branch
    if (!policy.active) { // Check if the policy is still active
        return res.status(400).json({ error: "Policy is not active" }); // Return 400 because expired policies cannot file claims
    } // Close the inactive policy branch
    if (amount > policy.coverageAmount) { // Check if the claimed amount exceeds the policy limit
        return res.status(400).json({ error: "Claim amount exceeds coverage limit" }); // Return 400 to enforce policy terms
    } // Close the coverage limit branch
    const claim: Claim = { // Build the claim object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the claim
        policyId, // Assign the policy ID from the request
        amount, // Assign the claim amount from the request
        status: "pending", // Mark the claim as pending until verification is complete
        evidence, // Assign the evidence from the request
        challengeDeadline: Date.now() + 48 * 60 * 60 * 1000, // Set the challenge window to 48 hours from now
    }; // Close the claim object
    claims.push(claim); // Add the new claim to the global in-memory array
    return res.status(201).json({ // Return the filed claim to the client
        message: "Claim filed", // Confirm that the claim was filed successfully
        claim, // Include the full claim details for client reference
    }); // Close the success response
}); // Close the POST /claim/file route

app.post("/claim/verify/:id", (req, res) => { // Define endpoint to verify a pending claim
    const claim = claims.find((c) => c.id === req.params.id); // Search the array for a claim matching the URL ID
    if (!claim) { // Check if the claim was found
        return res.status(404).json({ error: "Claim not found" }); // Return 404 if the claim ID does not exist
    } // Close the not-found branch
    if (claim.status !== "pending") { // Check if the claim is still awaiting verification
        return res.status(400).json({ error: "Claim is not pending verification" }); // Return 400 if the claim was already processed
    } // Close the status check branch
    const { oracleConfirmedLoss } = req.body; // Extract the oracle confirmation flag from the request body
    if (!oracleConfirmedLoss || oracleConfirmedLoss < oracleThreshold) { // Validate that the oracle confirmed a loss above the threshold
        claim.status = "rejected"; // Reject the claim because the event did not meet the minimum severity
        return res.status(200).json({ // Return the rejection to the client
            message: "Claim rejected: oracle threshold not met", // Explain why the claim was rejected
            claim, // Include the updated claim details
        }); // Close the rejection response
    } // Close the oracle validation block
    if (Date.now() < claim.challengeDeadline) { // Check if the challenge window is still open
        claim.status = "verified"; // Advance the claim to verified status after oracle confirmation
        return res.status(200).json({ // Return the intermediate verification to the client
            message: "Claim verified, awaiting challenge window", // Inform the client that the challenge period must pass
            claim, // Include the updated claim details
        }); // Close the intermediate response
    } // Close the challenge window check
    claim.status = "paid"; // Mark the claim as paid because verification passed and the challenge window expired
    poolBalance -= claim.amount; // Deduct the claim amount from the pool balance
    return res.status(200).json({ // Return the payout confirmation to the client
        message: "Claim paid", // Confirm that the claim was settled
        claim, // Include the updated claim details
        newPoolBalance: poolBalance, // Return the updated pool balance after payout
    }); // Close the payout response
}); // Close the POST /claim/verify/:id route

app.get("/pool/status", (req, res) => { // Define endpoint to inspect the current premium pool state
    const totalCoverage = policies.reduce((sum, p) => sum + p.coverageAmount, 0); // Sum the coverage amounts of all active policies
    return res.status(200).json({ // Return the pool status and metrics
        poolBalance, // Return the current pool balance
        totalPolicies: policies.length, // Return the count of active policies
        totalCoverage, // Return the aggregate coverage exposure
        capitalRatio: poolBalance / totalCoverage, // Compute the ratio of pool capital to total coverage
    }); // Close the success response
}); // Close the GET /pool/status route

app.get("/claim/:id", (req, res) => { // Define endpoint to fetch details of a specific claim
    const claim = claims.find((c) => c.id === req.params.id); // Search the array for a claim matching the URL ID
    if (!claim) { // Check if the claim was found
        return res.status(404).json({ error: "Claim not found" }); // Return 404 if the claim ID does not exist
    } // Close the not-found branch
    return res.status(200).json({ claim }); // Return the claim details to the client
}); // Close the GET /claim/:id route

app.listen(3047, () => { // Start the HTTP server on port 3047
    console.log("Insurance API listening on port 3047"); // Log startup so operators know the service is ready
}); // Close the listen callback
