import express from "express"; // Import the express framework to build the HTTP server
import { Connection, PublicKey } from "@solana/web3.js"; // Import Solana utilities for blockchain interaction

const app = express(); // Create the express application instance
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies

const connection = new Connection("http://localhost:8899", "confirmed"); // Initialize connection to the local validator
const PYTH_PROGRAM_ID = new PublicKey("Pyth..."); // Define the Pyth oracle program address for account lookup

app.get("/price/:asset", async (req, res) => { // Define endpoint to fetch the current price for a given asset
    const asset = req.params.asset; // Extract the asset identifier from the URL path parameter
    try { // Start a try block to handle chain fetch errors gracefully
        const priceAccountPubkey = new PublicKey(asset); // Convert the asset string to a valid Solana public key
        const accountInfo = await connection.getAccountInfo(priceAccountPubkey); // Fetch the on-chain account data
        if (!accountInfo) { // Check if the price account exists to avoid null pointer errors
            return res.status(404).json({ error: "Price account not found" }); // Return 404 if the account is missing
        } // Close the existence check
        const data = accountInfo.data; // Extract the raw buffer from the account info object
        const price = data.readBigInt64LE(0); // Read the first 8 bytes as the current price in little-endian format
        const confidence = data.readBigInt64LE(8); // Read bytes 8 through 15 as the confidence interval
        const publishSlot = data.readBigInt64LE(16); // Read bytes 16 through 23 as the slot of last update
        const expo = data.readInt32LE(24); // Read bytes 24 through 27 as the price exponent
        const currentSlot = BigInt(await connection.getSlot()); // Fetch the current slot to calculate staleness
        const slotDiff = currentSlot - publishSlot; // Compute the difference between now and the last update
        if (slotDiff > BigInt(100)) { // Reject prices that are older than 100 slots for safety
            return res.status(400).json({ // Return an error response if the price is stale
                error: "Stale price", // Inform the client that the data is too old
                slotDiff: slotDiff.toString(), // Include the staleness magnitude for debugging
            }); // Close the stale response
        } // Close the staleness check
        const adjustedPrice = Number(price) * Math.pow(10, expo); // Convert the raw integer price to a human-readable float
        return res.status(200).json({ // Return the validated price data to the client
            asset: asset, // Echo the requested asset for client verification
            price: adjustedPrice, // Return the decimal-adjusted price for human readability
            confidence: Number(confidence) * Math.pow(10, expo), // Adjust confidence to match the price scale
            publishSlot: publishSlot.toString(), // Return the publish slot as a string to avoid overflow
            currentSlot: currentSlot.toString(), // Return the current slot as a string for comparison
            expo, // Include the exponent so clients can recompute the raw value if needed
        }); // Close the success response
    } catch (err) { // Catch any errors from connection failures or buffer overflows
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the GET /price/:asset route

app.post("/price/validate", async (req, res) => { // Define endpoint to validate a price update before on-chain consumption
    const { price, confidence, expo, maxConfidenceRatio } = req.body; // Destructure validation parameters from request body
    if (price === undefined || confidence === undefined || expo === undefined) { // Check that required fields are present
        return res.status(400).json({ error: "Missing price, confidence, or expo" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to handle math errors safely
        const priceFloat = Number(price) * Math.pow(10, expo); // Convert the raw price to a float using the exponent
        const confidenceFloat = Number(confidence) * Math.pow(10, expo); // Convert confidence to a float using the exponent
        const ratio = confidenceFloat / Math.abs(priceFloat); // Compute the confidence as a ratio of the price
        const isValid = ratio <= (maxConfidenceRatio || 0.10); // Validate against the default 10% threshold if none provided
        return res.status(200).json({ // Return the validation result to the client
            price: priceFloat, // Include the human-readable price for reference
            confidence: confidenceFloat, // Include the human-readable confidence for reference
            ratio, // Include the computed ratio for transparency
            isValid, // Return true if the confidence is within acceptable bounds
            maxConfidenceRatio: maxConfidenceRatio || 0.10, // Echo the threshold used for the check
        }); // Close the success response
    } catch (err) { // Catch division by zero or parsing errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /price/validate route

app.get("/health", async (req, res) => { // Define a health check endpoint for load balancers and monitoring
    try { // Start a try block to detect RPC connectivity issues
        const slot = await connection.getSlot(); // Fetch the current slot to verify the RPC is responsive
        return res.status(200).json({ // Return the health status
            status: "ok", // Report that the service is operational
            currentSlot: slot, // Include the current slot to prove chain connectivity
        }); // Close the success response
    } catch (err) { // Catch RPC failures or network timeouts
        return res.status(503).json({ // Return 503 service unavailable if the chain is unreachable
            status: "error", // Report that the service is degraded
            message: (err as Error).message, // Include the specific error for operator diagnostics
        }); // Close the error response
    } // Close the catch block
}); // Close the GET /health route

app.listen(3001, () => { // Start the HTTP server on port 3001
    console.log("Price Feed API listening on port 3001"); // Log startup so operators know the service is ready
}); // Close the listen callback
