import express from "express"; // WHY: Import Express to build a REST API server that exposes Jupiter operations as HTTP endpoints.
import { Connection, Keypair, VersionedTransaction } from "@solana/web3.js"; // WHY: Import Solana web3 classes to connect to devnet, deserialize transactions, and sign with keypairs.
import bs58 from "bs58"; // WHY: Import base58 decoding so we can load the server signing key from an environment variable.

const app = express(); // WHY: Create an Express application instance to define routes and middleware for the Jupiter API.
app.use(express.json()); // WHY: Enable JSON body parsing middleware so POST endpoints can read JSON payloads from clients.

const PORT = 3068; // WHY: Use port 3068 as specified so the API does not conflict with other phase APIs in the project.
const JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"; // WHY: Define the Jupiter v6 quote endpoint so we can fetch live prices for client requests.
const JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"; // WHY: Define the Jupiter v6 swap endpoint so we can build serialized transactions server-side.
const JUPITER_ROUTE_MAP_API = "https://quote-api.jup.ag/v6/route-map"; // WHY: Define the Jupiter route-map endpoint so we can return available token pairs.
const DEVNET_RPC = "https://api.devnet.solana.com"; // WHY: Use the public devnet RPC so all submissions are on the test network, protecting real funds.
const connection = new Connection(DEVNET_RPC, "confirmed"); // WHY: Create a Connection with confirmed commitment for reliable transaction status polling.

const privateKeyBase58 = process.env.DEVNET_WALLET_PRIVATE_KEY; // WHY: Load the server signing key from the environment so secrets are not committed to source control.
if (!privateKeyBase58) { // WHY: Validate that the signing key is present so the server fails fast on startup with a clear error.
    console.error("DEVNET_WALLET_PRIVATE_KEY environment variable is required"); // WHY: Print an explicit error message so the operator knows exactly which variable to set.
    process.exit(1); // WHY: Exit immediately with a failure code because the API cannot sign transactions without a keypair.
} // WHY: Close the validation block.
const keypair = Keypair.fromSecretKey(bs58.decode(privateKeyBase58)); // WHY: Decode the base58 key and construct a Keypair for signing devnet transactions.

app.get("/quote", async (req, res) => { // WHY: Define the GET /quote route so clients can request Jupiter quotes by passing query parameters.
    const { inputMint, outputMint, amount, slippage } = req.query; // WHY: Extract query parameters from the request URL so we can forward them to Jupiter.
    if (!inputMint || !outputMint || !amount) { // WHY: Validate required fields so we reject malformed requests before calling the Jupiter API.
        res.status(400).json({ error: "inputMint, outputMint, and amount are required" }); // WHY: Return a 400 Bad Request with a clear message so the client knows what is missing.
        return; // WHY: Stop processing this request so we do not proceed with undefined parameters.
    } // WHY: Close the validation block.

    const slippageBps = slippage ? String(slippage) : "50"; // WHY: Default slippage to 50 basis points if the client does not provide a value.
    const quoteUrl = `${JUPITER_QUOTE_API}?inputMint=${inputMint}&outputMint=${outputMint}&amount=${amount}&slippageBps=${slippageBps}`; // WHY: Build the full Jupiter quote URL with the client's parameters.
    try { // WHY: Wrap the external API call in a try block so we can catch network or Jupiter errors gracefully.
        const response = await fetch(quoteUrl); // WHY: Call Jupiter to fetch the live quote and route plan for the requested token pair.
        if (!response.ok) { // WHY: Check the HTTP status so we propagate Jupiter errors to the client accurately.
            const errorText = await response.text(); // WHY: Read the error body so we can include Jupiter's error message in our response.
            res.status(response.status).json({ error: "Jupiter API error", details: errorText }); // WHY: Forward Jupiter's status and error text so the client receives transparent feedback.
            return; // WHY: End the handler so we do not attempt to parse a non-JSON error body as a quote.
        } // WHY: Close the error check.
        const quoteData = await response.json(); // WHY: Parse the JSON quote so we can return it to the client in a structured format.
        res.json(quoteData); // WHY: Send the quote JSON back to the client so their frontend can display price, route, and slippage floor.
    } catch (err: any) { // WHY: Catch exceptions from fetch or JSON parsing so the server does not crash on unexpected errors.
        res.status(500).json({ error: "Failed to fetch quote", message: err.message }); // WHY: Return a 500 with the error message so the client knows the request failed internally.
    } // WHY: Close the catch block.
}); // WHY: Close the /quote route handler.

app.post("/swap", async (req, res) => { // WHY: Define the POST /swap route so clients can submit a quote response and have the server build and submit the transaction.
    const { quoteResponse } = req.body; // WHY: Extract the quoteResponse from the JSON body because Jupiter's swap endpoint requires the full quote object.
    if (!quoteResponse) { // WHY: Ensure the client provided a quote so we do not call Jupiter with an invalid payload.
        res.status(400).json({ error: "quoteResponse is required in the request body" }); // WHY: Return 400 with guidance so the client knows what to include.
        return; // WHY: Abort the handler because the swap cannot proceed without a valid quote.
    } // WHY: Close the validation block.

    const swapBody = { // WHY: Construct the request body for Jupiter's swap endpoint with the necessary fields.
        quoteResponse: quoteResponse, // WHY: Pass the client's quote response to Jupiter so it reconstructs the identical route as a transaction.
        userPublicKey: keypair.publicKey.toBase58(), // WHY: Use the server's keypair public key as the fee payer and token account owner for this devnet demo.
        wrapAndUnwrapSol: true, // WHY: Enable automatic SOL wrapping because Jupiter route instructions expect wrapped SOL (wSOL) for swaps.
        prioritizationFeeLamports: 10000, // WHY: Add 10000 lamports as a priority fee so the transaction is prioritized during devnet congestion.
    }; // WHY: Close the swapBody object.

    try { // WHY: Wrap the swap API call and submission in try/catch to handle Jupiter errors and network failures gracefully.
        const response = await fetch(JUPITER_SWAP_API, { // WHY: POST to Jupiter to receive a serialized transaction built from the provided quote.
            method: "POST", // WHY: Use POST because we are creating a transaction resource by submitting the quote and public key.
            headers: { "Content-Type": "application/json" }, // WHY: Inform Jupiter that the request body is JSON so it parses the payload correctly.
            body: JSON.stringify(swapBody), // WHY: Serialize the swapBody to a JSON string for transmission over HTTP.
        }); // WHY: Close the fetch options object.

        if (!response.ok) { // WHY: Validate the response so we do not attempt to submit a failed or missing transaction.
            const errorText = await response.text(); // WHY: Capture Jupiter's error text to provide detailed feedback to the client.
            res.status(response.status).json({ error: "Jupiter swap API error", details: errorText }); // WHY: Forward the exact error to the client for transparency and debugging.
            return; // WHY: Stop processing so we do not try to deserialize an error response as a transaction.
        } // WHY: Close the error check.

        const swapData = await response.json(); // WHY: Parse the JSON to extract the base64-encoded swapTransaction string.
        const swapTransactionBase64 = swapData.swapTransaction; // WHY: Access the swapTransaction field because it contains the serialized transaction bytes.
        if (!swapTransactionBase64) { // WHY: Guard against unexpected Jupiter payloads that might omit the transaction field.
            res.status(500).json({ error: "swapTransaction missing from Jupiter response" }); // WHY: Return a clear server error so the client knows the swap could not be built.
            return; // WHY: Abort because there is no transaction to sign and submit.
        } // WHY: Close the guard block.

        const transactionBuffer = Buffer.from(swapTransactionBase64, "base64"); // WHY: Decode the base64 string into raw bytes so we can deserialize it into a Solana transaction.
        const transaction = VersionedTransaction.deserialize(transactionBuffer); // WHY: Deserialize into a VersionedTransaction because Jupiter returns modern transactions that may use lookup tables.

        transaction.sign([keypair]); // WHY: Sign the transaction with the server's keypair to authorize execution and pay fees on devnet.
        const signature = await connection.sendTransaction(transaction); // WHY: Submit the signed transaction to the Solana network via the devnet RPC endpoint.
        await connection.confirmTransaction(signature, "confirmed"); // WHY: Wait for confirmed status so we know the swap executed successfully and will not be rolled back.

        res.json({ // WHY: Return a JSON response to the client with the transaction result.
            success: true, // WHY: Indicate success so the client knows the swap completed.
            signature: signature, // WHY: Include the transaction signature so the client can verify the swap on a block explorer.
            explorer: `https://explorer.solana.com/tx/${signature}?cluster=devnet`, // WHY: Provide a direct devnet explorer link so the client can inspect the transaction details.
        }); // WHY: Close the response JSON object.
    } catch (err: any) { // WHY: Catch any exceptions from fetch, deserialization, signing, or submission to prevent server crashes.
        res.status(500).json({ error: "Swap failed", message: err.message }); // WHY: Return a 500 with the error message so the client knows why the swap did not complete.
    } // WHY: Close the catch block.
}); // WHY: Close the /swap route handler.

app.get("/routes", async (_req, res) => { // WHY: Define GET /routes so clients can discover which token pairs have available liquidity through Jupiter.
    try { // WHY: Wrap the external API call to handle network errors without crashing the server.
        const response = await fetch(JUPITER_ROUTE_MAP_API); // WHY: Call Jupiter's route-map endpoint to retrieve the graph of supported input-to-output mint pairs.
        if (!response.ok) { // WHY: Check the HTTP status so we propagate any Jupiter service errors to the client.
            const errorText = await response.text(); // WHY: Read the error response to provide meaningful feedback.
            res.status(response.status).json({ error: "Jupiter route-map API error", details: errorText }); // WHY: Forward the error transparently to the client.
            return; // WHY: Stop processing because we cannot return route data if the upstream request failed.
        } // WHY: Close the error check.
        const routeMap = await response.json(); // WHY: Parse the route-map JSON so we can return it to the client.
        res.json({ // WHY: Send a structured JSON response containing the route map and helpful metadata.
            description: "Route map of supported token pairs on Jupiter v6", // WHY: Add a description so clients understand what the data represents.
            routeMap: routeMap, // WHY: Include the raw route map so clients can inspect supported pairs.
            note: "Keys are input mints; values are arrays of output mints with available routes.", // WHY: Explain the data structure so developers know how to parse the map.
        }); // WHY: Close the response JSON object.
    } catch (err: any) { // WHY: Catch exceptions from fetch or JSON parsing so the server remains stable.
        res.status(500).json({ error: "Failed to fetch route map", message: err.message }); // WHY: Return a 500 with details so the client knows the request failed internally.
    } // WHY: Close the catch block.
}); // WHY: Close the /routes route handler.

app.listen(PORT, () => { // WHY: Start the Express server so it begins accepting HTTP requests on the specified port.
    console.log(`Jupiter API listening on port ${PORT}`); // WHY: Log the listening port so the operator knows the server is ready and where to send requests.
    console.log(`Signer wallet: ${keypair.publicKey.toBase58()}`); // WHY: Display the signer wallet address so the operator knows which account will pay fees and receive tokens.
}); // WHY: Close the listen callback.
