import express from "express"; // Import the express framework to build the HTTP server for cross-chain bridge operations
import cors from "cors"; // Import cors middleware to allow browser clients to interact with this API from different origins

const app = express(); // Create the express application instance that will handle bridge routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects
app.use(cors()); // Enable CORS so frontend dashboards can initiate transfers and check balances without preflight errors

interface BridgeRecord { // Define a TypeScript interface for a cross-chain transfer record to ensure type safety across endpoints
    id: string; // Store a unique identifier for each transfer so clients can track its status
    user: string; // Store the wallet address of the user initiating the transfer so ownership is recorded
    sourceChain: string; // Store the name of the origin chain so the lock location is known
    destinationChain: string; // Store the name of the target chain so the mint location is known
    asset: string; // Store the asset symbol so the transfer denomination is clear
    amount: number; // Store the quantity being transferred so balances can be updated
    status: "locked" | "attested" | "minted" | "burned" | "released"; // Track the transfer lifecycle so clients know the current stage
    attestations: string[]; // Store guardian signatures so the threshold for minting can be verified
} // Close the BridgeRecord interface definition

const records: BridgeRecord[] = []; // Initialize an in-memory array to store transfer records because this is a teaching demo without a database
const bridgeBalances: Map<string, number> = new Map(); // Initialize a Map to track locked collateral per asset so minting is capped
const wrappedSupplies: Map<string, number> = new Map(); // Initialize a Map to track wrapped token supply per asset so burning is validated

let nextRecordId = 1; // Initialize a simple counter to generate unique transfer record IDs sequentially
const GUARDIAN_THRESHOLD = 2; // Define the minimum number of attestations required so security is maintained before minting

function nowSeconds(): number { // Define a helper to get the current time in seconds because timestamps use second-level granularity
    return Math.floor(Date.now() / 1000); // Convert millisecond timestamps to whole seconds for clean display
} // Close the nowSeconds helper

function getBalanceKey(chain: string, asset: string): string { // Define a helper to create a consistent key for balance lookups
    return `${chain}:${asset}`; // Concatenate chain and asset with a delimiter so composite keys are unique
} // Close the getBalanceKey helper

app.post("/lock", (req, res) => { // Define an endpoint to lock native assets on the source chain and initiate a cross-chain transfer
    const { user, sourceChain, destinationChain, asset, amount } = req.body; // Destructure request fields so validation can be performed
    if (!user || !sourceChain || !destinationChain || !asset || !amount) { // Validate that every required field is present so incomplete transfers are rejected
        return res.status(400).json({ error: "Missing required fields: user, sourceChain, destinationChain, asset, amount" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    if (amount <= 0) { // Validate that the amount is positive because negative or zero transfers are meaningless
        return res.status(400).json({ error: "amount must be positive" }); // Return 400 so the client cannot create malformed transfers
    } // Close the positive amount validation block
    const balanceKey = getBalanceKey(sourceChain, asset); // Compute the key so the bridge balance for this asset can be updated
    const currentBalance = bridgeBalances.get(balanceKey) || 0; // Retrieve the current locked amount defaulting to zero if none exists
    bridgeBalances.set(balanceKey, currentBalance + amount); // Increase the locked balance so the bridge tracks total collateral
    const record: BridgeRecord = { // Construct a new transfer record with all fields initialized
        id: String(nextRecordId++), // Assign the next sequential ID and increment the counter so future transfers get unique identifiers
        user, // Store the user address so the transfer is linked to the correct owner
        sourceChain, // Store the origin chain so the lock location is documented
        destinationChain, // Store the target chain so the mint destination is documented
        asset, // Store the asset symbol so the transfer denomination is clear
        amount, // Store the quantity so balance updates can be traced
        status: "locked", // Set the initial status to locked so the lifecycle starts at the deposit stage
        attestations: [], // Initialize an empty attestation list so guardians can add signatures later
    }; // Close the transfer record creation
    records.push(record); // Append the record to the in-memory array so it can be queried and updated later
    return res.status(201).json({ // Return a 201 Created response so the client knows the lock was recorded
        success: true, // Include a success flag so programmatic clients can check status without deep body parsing
        record, // Return the full record so the client receives the generated ID and status
    }); // Close the success response
}); // Close the POST /lock route

app.post("/attest", (req, res) => { // Define an endpoint for guardians to submit signatures attesting to a locked transfer
    const { recordId, guardianId, signature } = req.body; // Destructure request fields so validation can be performed
    if (!recordId || !guardianId || !signature) { // Validate that every required field is present so incomplete attestations are rejected
        return res.status(400).json({ error: "Missing required fields: recordId, guardianId, signature" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    const record = records.find((r) => r.id === recordId); // Locate the transfer record so the attestation is linked to the correct transfer
    if (!record) { // Ensure the record exists so attestations do not target deleted or invalid transfers
        return res.status(404).json({ error: "Record not found" }); // Return 404 so the client knows the record ID is invalid
    } // Close the record existence check
    if (record.status !== "locked") { // Check if the record is still awaiting attestation because only locked transfers can be attested
        return res.status(400).json({ error: `Record is already ${record.status}` }); // Return 400 so the client knows the lifecycle has moved on
    } // Close the status check
    if (record.attestations.includes(guardianId)) { // Prevent duplicate attestations from the same guardian so signature counts remain honest
        return res.status(409).json({ error: "Guardian already attested" }); // Return 409 so the client knows this guardian has already signed
    } // Close the duplicate attestation check
    record.attestations.push(guardianId); // Add the guardian to the attestation list so the signature count increases
    if (record.attestations.length >= GUARDIAN_THRESHOLD) { // Check if the threshold has been reached so the transfer can advance
        record.status = "attested"; // Update the status to attested so minting endpoints know the transfer is approved
    } // Close the threshold advancement block
    return res.status(200).json({ // Return the attestation result so the guardian knows their signature was recorded
        success: true, // Confirm the operation succeeded so clients can update their UI state
        record, // Return the updated record so the client sees the new attestation count and status
    }); // Close the success response
}); // Close the POST /attest route

app.post("/mint", (req, res) => { // Define an endpoint to mint wrapped tokens on the destination chain after sufficient attestations
    const { recordId } = req.body; // Destructure the record ID so the server can locate the specific transfer
    if (!recordId) { // Validate that the record ID is provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing recordId" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const record = records.find((r) => r.id === recordId); // Locate the transfer record so minting targets the correct transfer
    if (!record) { // Ensure the record exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Record not found" }); // Return 404 so the client knows the record ID is invalid
    } // Close the record existence check
    if (record.status !== "attested") { // Require attested status so minting cannot occur before guardian approval
        return res.status(400).json({ error: `Record must be attested before minting. Current status: ${record.status}` }); // Return 400 with context
    } // Close the status validation block
    const wrappedKey = getBalanceKey(record.destinationChain, record.asset); // Compute the key so the wrapped supply can be updated
    const currentSupply = wrappedSupplies.get(wrappedKey) || 0; // Retrieve the current wrapped supply defaulting to zero if none exists
    wrappedSupplies.set(wrappedKey, currentSupply + record.amount); // Increase the wrapped supply so the total tracks minted tokens
    record.status = "minted"; // Update the status to minted so the lifecycle reflects that wrapped tokens have been issued
    return res.status(200).json({ // Return the mint result so the user knows wrapped tokens were created
        success: true, // Confirm the operation succeeded so clients can update their UI state
        record, // Return the updated record so the client sees the new status
        wrappedSupply: wrappedSupplies.get(wrappedKey), // Report the total wrapped supply so transparency is maintained
    }); // Close the success response
}); // Close the POST /mint route

app.post("/burn", (req, res) => { // Define an endpoint to burn wrapped tokens on the destination chain and initiate a return transfer
    const { recordId } = req.body; // Destructure the record ID so the server can locate the specific transfer
    if (!recordId) { // Validate that the record ID is provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing recordId" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const record = records.find((r) => r.id === recordId); // Locate the transfer record so burning targets the correct transfer
    if (!record) { // Ensure the record exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Record not found" }); // Return 404 so the client knows the record ID is invalid
    } // Close the record existence check
    if (record.status !== "minted") { // Require minted status so burning cannot occur before wrapped tokens were created
        return res.status(400).json({ error: `Record must be minted before burning. Current status: ${record.status}` }); // Return 400 with context
    } // Close the status validation block
    const wrappedKey = getBalanceKey(record.destinationChain, record.asset); // Compute the key so the wrapped supply can be reduced
    const currentSupply = wrappedSupplies.get(wrappedKey) || 0; // Retrieve the current wrapped supply defaulting to zero if none exists
    if (currentSupply < record.amount) { // Validate that enough wrapped supply exists so the burn does not create negative balances
        return res.status(400).json({ error: "Insufficient wrapped supply to burn" }); // Return 400 so the client knows the bridge is under-collateralized
    } // Close the supply check
    wrappedSupplies.set(wrappedKey, currentSupply - record.amount); // Decrease the wrapped supply so the total reflects destroyed tokens
    record.status = "burned"; // Update the status to burned so the lifecycle reflects that wrapped tokens have been destroyed
    return res.status(200).json({ // Return the burn result so the user knows wrapped tokens were destroyed
        success: true, // Confirm the operation succeeded so clients can update their UI state
        record, // Return the updated record so the client sees the new status
        wrappedSupply: wrappedSupplies.get(wrappedKey), // Report the remaining wrapped supply so transparency is maintained
    }); // Close the success response
}); // Close the POST /burn route

app.post("/release", (req, res) => { // Define an endpoint to release native assets on the source chain after wrapped tokens are burned
    const { recordId } = req.body; // Destructure the record ID so the server can locate the specific transfer
    if (!recordId) { // Validate that the record ID is provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing recordId" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const record = records.find((r) => r.id === recordId); // Locate the transfer record so release targets the correct transfer
    if (!record) { // Ensure the record exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Record not found" }); // Return 404 so the client knows the record ID is invalid
    } // Close the record existence check
    if (record.status !== "burned") { // Require burned status so release cannot occur before wrapped tokens were destroyed
        return res.status(400).json({ error: `Record must be burned before releasing. Current status: ${record.status}` }); // Return 400 with context
    } // Close the status validation block
    const balanceKey = getBalanceKey(record.sourceChain, record.asset); // Compute the key so the locked balance can be reduced
    const currentBalance = bridgeBalances.get(balanceKey) || 0; // Retrieve the current locked balance defaulting to zero if none exists
    if (currentBalance < record.amount) { // Validate that enough collateral exists so the release does not create negative balances
        return res.status(400).json({ error: "Insufficient locked balance to release" }); // Return 400 so the client knows the bridge is insolvent
    } // Close the balance check
    bridgeBalances.set(balanceKey, currentBalance - record.amount); // Decrease the locked balance so the bridge no longer holds the released collateral
    record.status = "released"; // Update the status to released so the lifecycle reflects that native assets have been returned
    return res.status(200).json({ // Return the release result so the user knows native assets were unlocked
        success: true, // Confirm the operation succeeded so clients can update their UI state
        record, // Return the updated record so the client sees the final status
        lockedBalance: bridgeBalances.get(balanceKey), // Report the remaining locked balance so transparency is maintained
    }); // Close the success response
}); // Close the POST /release route

app.get("/records", (req, res) => { // Define an endpoint to list all bridge transfer records for audit and tracking
    return res.status(200).json({ // Return the full list so clients can browse transfers
        count: records.length, // Include the total count so summary widgets can display it
        records, // Return the array of transfer records so the client receives complete data
    }); // Close the success response
}); // Close the GET /records route

app.get("/balances", (req, res) => { // Define an endpoint to inspect bridge balances and wrapped supplies
    const balances = Object.fromEntries(bridgeBalances); // Convert the Map to a plain object so JSON serialization works correctly
    const supplies = Object.fromEntries(wrappedSupplies); // Convert the Map to a plain object so JSON serialization works correctly
    return res.status(200).json({ // Return the current state so clients can verify collateralization
        lockedBalances: balances, // Include the locked collateral so users can audit backing
        wrappedSupplies: supplies, // Include the wrapped supplies so users can check for mismatches
    }); // Close the success response
}); // Close the GET /balances route

app.listen(3044, () => { // Start the HTTP server on port 3044 because this phase owns that port to avoid conflicts with other APIs
    console.log("Bridge API listening on port 3044"); // Log startup so operators know the service is ready to accept connections
}); // Close the listen callback
