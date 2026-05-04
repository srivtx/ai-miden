import express from "express"; // Import the express framework to build the HTTP server
import bodyParser from "body-parser"; // Import body-parser to parse JSON request bodies

const app = express(); // Create the express application instance
app.use(bodyParser.json()); // Attach middleware to parse incoming JSON request bodies

interface TokenizedAsset { // Define the shape of a tokenized asset record for type safety
    id: string; // Store a unique identifier so each asset can be tracked individually
    name: string; // Store the human-readable name of the asset for display purposes
    totalSupply: number; // Store the maximum number of tokens representing fractional ownership
    pricePerToken: number; // Store the issuance price used for valuation and accounting
    yieldRate: number; // Store the annual percentage yield distributed to token holders
    whitelistRequired: boolean; // Store whether transfers are restricted to verified addresses
}

interface Holder { // Define the shape of a token holder record for type safety
    address: string; // Store the blockchain address that owns a balance of tokens
    balance: number; // Store the quantity of tokens currently held at this address
    whitelisted: boolean; // Store whether this address has passed KYC and accreditation checks
}

let assets: TokenizedAsset[] = []; // Initialize an in-memory array to hold all tokenized asset definitions
let holders: Record<string, Holder> = {}; // Initialize an in-memory map to track balances and whitelist status by address
const whitelistRegistry: Set<string> = new Set(); // Initialize a set to store addresses that have passed compliance verification
const MAX_HOLDING_PERCENT = 0.1; // Define a 10% maximum holding limit to prevent ownership concentration

app.post("/asset/create", (req, res) => { // Define endpoint to create a new tokenized asset
    const { name, totalSupply, pricePerToken, yieldRate, whitelistRequired } = req.body; // Extract asset parameters from the request body
    if (!name || !totalSupply || !pricePerToken || yieldRate === undefined || whitelistRequired === undefined) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing required asset fields" }); // Return 400 if input is incomplete
    } // Close the validation block
    const asset: TokenizedAsset = { // Build the asset object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the asset
        name, // Assign the asset name from the request
        totalSupply, // Assign the total supply from the request
        pricePerToken, // Assign the price per token from the request
        yieldRate, // Assign the yield rate from the request
        whitelistRequired, // Assign the whitelist requirement flag from the request
    }; // Close the asset object
    assets.push(asset); // Add the new asset to the global in-memory array
    return res.status(201).json({ // Return the created asset to the client
        message: "Tokenized asset created", // Confirm that the asset was created successfully
        asset, // Include the full asset details for client reference
    }); // Close the success response
}); // Close the POST /asset/create route

app.post("/compliance/whitelist", (req, res) => { // Define endpoint to add an address to the compliance whitelist
    const { address } = req.body; // Extract the address from the request body
    if (!address) { // Validate that the address is provided
        return res.status(400).json({ error: "Address is required" }); // Return 400 if the address is missing
    } // Close the validation block
    whitelistRegistry.add(address); // Add the address to the whitelist set
    if (!holders[address]) { // Check if this address already has a holder record
        holders[address] = { address, balance: 0, whitelisted: true }; // Create a new holder record with zero balance and whitelisted status
    } else { // Handle the case where the holder record already exists
        holders[address].whitelisted = true; // Update the existing record to reflect whitelisted status
    } // Close the holder existence branch
    return res.status(200).json({ // Return the whitelist confirmation to the client
        message: "Address whitelisted", // Confirm that the address passed compliance
        address, // Echo the whitelisted address
    }); // Close the success response
}); // Close the POST /compliance/whitelist route

app.post("/asset/mint", (req, res) => { // Define endpoint to mint tokens to a specific holder
    const { assetId, address, amount } = req.body; // Extract minting parameters from the request body
    if (!assetId || !address || !amount) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing assetId, address, or amount" }); // Return 400 if input is incomplete
    } // Close the validation block
    const asset = assets.find((a) => a.id === assetId); // Search the array for an asset matching the provided ID
    if (!asset) { // Check if the asset was found
        return res.status(404).json({ error: "Asset not found" }); // Return 404 if the asset ID does not exist
    } // Close the not-found branch
    if (asset.whitelistRequired && !whitelistRegistry.has(address)) { // Check if the recipient is whitelisted when required
        return res.status(403).json({ error: "Address not whitelisted for this asset" }); // Return 403 to enforce compliance
    } // Close the whitelist enforcement block
    if (!holders[address]) { // Check if this address already has a holder record
        holders[address] = { address, balance: 0, whitelisted: whitelistRegistry.has(address) }; // Create a new holder record
    } // Close the holder initialization block
    const projectedBalance = holders[address].balance + amount; // Compute the balance after this mint to check concentration limits
    if (projectedBalance > asset.totalSupply * MAX_HOLDING_PERCENT) { // Check if the mint would violate the maximum holding limit
        return res.status(400).json({ error: "Mint would exceed maximum holding limit" }); // Return 400 to enforce anti-concentration rules
    } // Close the holding limit block
    holders[address].balance += amount; // Increase the holder's balance by the minted amount
    return res.status(200).json({ // Return the mint confirmation to the client
        message: "Tokens minted", // Confirm that the mint was successful
        assetId, // Echo the asset ID for reference
        address, // Echo the recipient address
        newBalance: holders[address].balance, // Return the updated balance
    }); // Close the success response
}); // Close the POST /asset/mint route

app.post("/asset/transfer", (req, res) => { // Define endpoint to transfer tokens between holders
    const { assetId, from, to, amount } = req.body; // Extract transfer parameters from the request body
    if (!assetId || !from || !to || !amount) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing transfer fields" }); // Return 400 if input is incomplete
    } // Close the validation block
    const asset = assets.find((a) => a.id === assetId); // Search the array for an asset matching the provided ID
    if (!asset) { // Check if the asset was found
        return res.status(404).json({ error: "Asset not found" }); // Return 404 if the asset ID does not exist
    } // Close the not-found branch
    if (!holders[from] || holders[from].balance < amount) { // Check if the sender has sufficient balance
        return res.status(400).json({ error: "Insufficient balance" }); // Return 400 if the sender cannot cover the transfer
    } // Close the balance check block
    if (asset.whitelistRequired && !whitelistRegistry.has(to)) { // Check if the recipient is whitelisted when required
        return res.status(403).json({ error: "Recipient not whitelisted" }); // Return 403 to enforce compliance
    } // Close the recipient whitelist block
    if (!holders[to]) { // Check if the recipient already has a holder record
        holders[to] = { address: to, balance: 0, whitelisted: whitelistRegistry.has(to) }; // Create a new holder record
    } // Close the recipient initialization block
    const projectedToBalance = holders[to].balance + amount; // Compute the recipient's balance after transfer
    if (projectedToBalance > asset.totalSupply * MAX_HOLDING_PERCENT) { // Check if the transfer would violate the maximum holding limit
        return res.status(400).json({ error: "Transfer would exceed recipient maximum holding limit" }); // Return 400 to enforce limits
    } // Close the recipient holding limit block
    holders[from].balance -= amount; // Deduct the transfer amount from the sender's balance
    holders[to].balance += amount; // Credit the transfer amount to the recipient's balance
    return res.status(200).json({ // Return the transfer confirmation to the client
        message: "Transfer successful", // Confirm that the transfer was executed
        assetId, // Echo the asset ID for reference
        from, // Echo the sender address
        to, // Echo the recipient address
        amount, // Echo the transferred amount
        fromBalance: holders[from].balance, // Return the sender's updated balance
        toBalance: holders[to].balance, // Return the recipient's updated balance
    }); // Close the success response
}); // Close the POST /asset/transfer route

app.post("/asset/distribute-yield", (req, res) => { // Define endpoint to distribute yield to all token holders
    const { assetId } = req.body; // Extract the asset ID from the request body
    if (!assetId) { // Validate that the asset ID is provided
        return res.status(400).json({ error: "Asset ID is required" }); // Return 400 if the asset ID is missing
    } // Close the validation block
    const asset = assets.find((a) => a.id === assetId); // Search the array for an asset matching the provided ID
    if (!asset) { // Check if the asset was found
        return res.status(404).json({ error: "Asset not found" }); // Return 404 if the asset ID does not exist
    } // Close the not-found branch
    const distributions: { address: string; amount: number }[] = []; // Initialize an array to record each distribution for the response
    for (const holder of Object.values(holders)) { // Iterate over all holders to compute and credit yield
        if (holder.balance > 0) { // Check if the holder owns any tokens eligible for yield
            const yieldAmount = holder.balance * asset.pricePerToken * (asset.yieldRate / 100); // Compute annual yield in dollar terms
            distributions.push({ address: holder.address, amount: yieldAmount }); // Record the distribution for reporting
        } // Close the positive balance check
    } // Close the holder loop
    return res.status(200).json({ // Return the distribution summary to the client
        message: "Yield distributed", // Confirm that the yield calculation was performed
        assetId, // Echo the asset ID for reference
        distributions, // Include the list of all computed distributions
    }); // Close the success response
}); // Close the POST /asset/distribute-yield route

app.get("/asset/:id/holders", (req, res) => { // Define endpoint to fetch all holders of a specific asset
    const asset = assets.find((a) => a.id === req.params.id); // Search the array for an asset matching the URL ID
    if (!asset) { // Check if the asset was found
        return res.status(404).json({ error: "Asset not found" }); // Return 404 if the asset ID does not exist
    } // Close the not-found branch
    const assetHolders = Object.values(holders).filter((h) => h.balance > 0); // Filter to include only addresses with a positive balance
    return res.status(200).json({ // Return the holder list to the client
        assetId: req.params.id, // Echo the asset ID
        totalHolders: assetHolders.length, // Return the count of active holders
        holders: assetHolders, // Return the array of holder records
    }); // Close the success response
}); // Close the GET /asset/:id/holders route

app.listen(3048, () => { // Start the HTTP server on port 3048
    console.log("RWA API listening on port 3048"); // Log startup so operators know the service is ready
}); // Close the listen callback
