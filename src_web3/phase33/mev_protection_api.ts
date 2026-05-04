import express from "express"; // Import the express framework to build the HTTP server
import { Connection, PublicKey } from "@solana/web3.js"; // Import Solana utilities for blockchain interaction

const app = express(); // Create the express application instance
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies

const connection = new Connection("http://localhost:8899", "confirmed"); // Initialize connection to the local validator
const POOL_PROGRAM_ID = new PublicKey("Swap..."); // Define the swap program address for deriving pool accounts

app.post("/swap/simulate", async (req, res) => { // Define endpoint to simulate a swap and compute slippage bounds
    const { amountIn, tokenAReserve, tokenBReserve, feeNumerator, feeDenominator } = req.body; // Extract pool params
    if (!amountIn || !tokenAReserve || !tokenBReserve) { // Validate that required simulation inputs are present
        return res.status(400).json({ error: "Missing amountIn or reserves" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to handle math errors gracefully
        const amtIn = BigInt(amountIn); // Convert the input amount to BigInt for precision
        const reserveA = BigInt(tokenAReserve); // Convert token A reserve to BigInt for precision
        const reserveB = BigInt(tokenBReserve); // Convert token B reserve to BigInt for precision
        const num = BigInt(feeNumerator || 3); // Default to a 0.3% fee if no numerator is provided
        const den = BigInt(feeDenominator || 1000); // Default to denominator 1000 to match the 0.3% fee
        const amountInWithFee = (amtIn * num) / den; // Calculate the fee portion of the input amount
        const amountInAfterFee = amtIn - amountInWithFee; // Subtract the fee to get the tradable amount
        const numerator = amountInAfterFee * reserveB; // Compute the constant product numerator
        const denominator = reserveA + amountInAfterFee; // Compute the constant product denominator
        const amountOut = numerator / denominator; // Calculate the expected output using constant product math
        const priceBefore = Number(reserveB) / Number(reserveA); // Calculate the pre-swap price for reference
        const priceAfter = Number(reserveB - amountOut) / Number(reserveA + amountInAfterFee); // Calculate post-swap price
        const slippage = ((priceAfter - priceBefore) / priceBefore) * 100; // Compute the percentage price impact
        const minOut01 = (amountOut * BigInt(999)) / BigInt(1000); // Compute 0.1% slippage tolerance minimum
        const minOut05 = (amountOut * BigInt(995)) / BigInt(1000); // Compute 0.5% slippage tolerance minimum
        const minOut10 = (amountOut * BigInt(990)) / BigInt(1000); // Compute 1.0% slippage tolerance minimum
        return res.status(200).json({ // Return the simulation results to the client
            amountIn: amtIn.toString(), // Return the input amount as a string
            expectedAmountOut: amountOut.toString(), // Return the expected output as a string
            priceBefore: priceBefore.toFixed(6), // Return the pre-swap price with six decimals
            priceAfter: priceAfter.toFixed(6), // Return the post-swap price with six decimals
            priceImpactPercent: slippage.toFixed(4), // Return the price impact with four decimals
            minAmountOut01Percent: minOut01.toString(), // Return the 0.1% slippage minimum
            minAmountOut05Percent: minOut05.toString(), // Return the 0.5% slippage minimum
            minAmountOut10Percent: minOut10.toString(), // Return the 1.0% slippage minimum
        }); // Close the success response
    } catch (err) { // Catch division by zero or BigInt parsing errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /swap/simulate route

app.post("/swap/build", async (req, res) => { // Define endpoint to build a protected swap transaction payload
    const { user, amountIn, minimumAmountOut, deadlineSlot } = req.body; // Extract swap parameters from request body
    if (!user || !amountIn || minimumAmountOut === undefined || !deadlineSlot) { // Validate all required fields
        return res.status(400).json({ error: "Missing user, amountIn, minimumAmountOut, or deadlineSlot" }); // Return 400
    } // Close the input validation block
    try { // Start a try block to handle buffer and serialization errors
        const instructionData = Buffer.alloc(25); // Allocate 25 bytes for discriminator, amountIn, minOut, and deadline
        instructionData.writeUInt8(0, 0); // Write instruction discriminator 0 to route to the swap instruction
        instructionData.writeBigUInt64LE(BigInt(amountIn), 1); // Write the 8-byte input amount at bytes 1-8
        instructionData.writeBigUInt64LE(BigInt(minimumAmountOut), 9); // Write the 8-byte minimum output at bytes 9-16
        instructionData.writeBigUInt64LE(BigInt(deadlineSlot), 17); // Write the 8-byte deadline at bytes 17-24
        const currentSlot = await connection.getSlot(); // Fetch the current slot to warn if the deadline is too tight
        return res.status(200).json({ // Return the constructed transaction data to the client
            user, // Echo the user address for client-side verification
            currentSlot, // Include the current slot so the client knows how much time remains
            deadlineSlot, // Echo the deadline so the client can display it
            instructionData: instructionData.toString("base64"), // Encode the instruction payload for wallet transmission
            warning: currentSlot + 10 > deadlineSlot // Warn if the deadline is within 10 slots of the current time
                ? "Deadline is very close; transaction may expire before confirmation" // Set warning text if tight
                : undefined, // Leave warning undefined if the deadline is safe
        }); // Close the success response
    } catch (err) { // Catch RPC failures or buffer errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /swap/build route

app.get("/health", async (req, res) => { // Define a health check endpoint for monitoring and load balancers
    try { // Start a try block to detect RPC connectivity issues
        const slot = await connection.getSlot(); // Fetch the current slot to verify the RPC is responsive
        return res.status(200).json({ status: "ok", currentSlot: slot }); // Return health status with current slot
    } catch (err) { // Catch RPC failures or network timeouts
        return res.status(503).json({ status: "error", message: (err as Error).message }); // Return 503 if degraded
    } // Close the catch block
}); // Close the GET /health route

app.listen(3002, () => { // Start the HTTP server on port 3002
    console.log("MEV Protection API listening on port 3002"); // Log startup so operators know the service is ready
}); // Close the listen callback
