import { Connection, Keypair, VersionedTransaction } from "@solana/web3.js"; // WHY: Import Solana web3 classes to connect to devnet, manage keypairs, and handle versioned transactions returned by Jupiter.
import bs58 from "bs58"; // WHY: Import base58 decoding so we can load the wallet private key from a base58 environment variable string.

async function main() { // WHY: Define an async main function because all network calls to Jupiter and Solana are asynchronous.
    const JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"; // WHY: Store the Jupiter v6 quote endpoint URL so we can fetch live swap pricing.
    const JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"; // WHY: Store the Jupiter v6 swap endpoint URL so we can build a serialized transaction from a quote.
    const DEVNET_RPC = "https://api.devnet.solana.com"; // WHY: Use the public Solana devnet RPC endpoint for testing so no real funds are at risk.
    const connection = new Connection(DEVNET_RPC, "confirmed"); // WHY: Create a Connection with confirmed commitment for reliable transaction status and finality.

    const privateKeyBase58 = process.env.DEVNET_WALLET_PRIVATE_KEY; // WHY: Load the test wallet private key from an environment variable to avoid hardcoding secrets in source code.
    if (!privateKeyBase58) { // WHY: Validate that the environment variable exists so the script fails fast with a clear error instead of crashing later.
        throw new Error("DEVNET_WALLET_PRIVATE_KEY environment variable is required"); // WHY: Throw a descriptive error so the operator knows exactly which variable to set.
    } // WHY: Close the validation block.

    const keypair = Keypair.fromSecretKey(bs58.decode(privateKeyBase58)); // WHY: Decode the base58 key and construct a Keypair that can sign transactions on behalf of the user.
    console.log("Wallet public key:", keypair.publicKey.toBase58()); // WHY: Log the wallet address so the operator can verify they are using the correct test account.

    const inputMint = "So11111111111111111111111111111111111111112"; // WHY: Use the wrapped SOL mint address as the input token because SOL is the native currency and most commonly swapped.
    const outputMint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"; // WHY: Use the USDC mint address as the output token because it is the most liquid stablecoin on Solana.
    const amount = 100000000; // WHY: Specify 100000000 lamports which equals 0.1 SOL, a small test amount that limits financial exposure on devnet.
    const slippageBps = 50; // WHY: Set 50 basis points (0.5%) slippage tolerance to balance execution certainty against price movement risk.

    console.log("Fetching quote from Jupiter..."); // WHY: Log the operation so the operator knows the script is actively calling the Jupiter API.
    const quoteUrl = `${JUPITER_QUOTE_API}?inputMint=${inputMint}&outputMint=${outputMint}&amount=${amount}&slippageBps=${slippageBps}`; // WHY: Build the full quote URL with query parameters so Jupiter knows which swap to price.
    const quoteResponse = await fetch(quoteUrl); // WHY: Send the HTTP GET request to Jupiter to retrieve the live quote and optimal route plan.
    if (!quoteResponse.ok) { // WHY: Check the HTTP status so we handle API failures gracefully instead of parsing invalid JSON.
        throw new Error(`Jupiter quote API error: ${quoteResponse.status} ${quoteResponse.statusText}`); // WHY: Throw a descriptive error including the status code for debugging.
    } // WHY: Close the error check block.

    const quoteData = await quoteResponse.json(); // WHY: Parse the JSON response body into a JavaScript object so we can access quote fields programmatically.
    console.log("Quote received:"); // WHY: Log a header before printing the quote so the output is readable and scannable.
    console.log(JSON.stringify(quoteData, null, 2)); // WHY: Pretty-print the quote object so the operator can inspect route, price impact, and slippage floor.

    console.log("Building swap transaction..."); // WHY: Inform the operator that the script is converting the quote into a signable Solana transaction.
    const swapBody = { // WHY: Construct the request body object because the Jupiter swap endpoint requires specific fields in the POST payload.
        quoteResponse: quoteData, // WHY: Pass the entire quote response back to Jupiter so it reconstructs the identical route as an on-chain transaction.
        userPublicKey: keypair.publicKey.toBase58(), // WHY: Provide the user's public key so Jupiter derives the correct associated token accounts and sets the fee payer.
        wrapAndUnwrapSol: true, // WHY: Enable automatic SOL wrapping because Jupiter route instructions expect wrapped SOL (wSOL) for token swaps.
        prioritizationFeeLamports: 10000, // WHY: Add 10000 lamports as a priority fee so the transaction is prioritized by validators during devnet congestion.
    }; // WHY: Close the swapBody object.

    const swapResponse = await fetch(JUPITER_SWAP_API, { // WHY: Send the HTTP POST request to Jupiter to receive a serialized transaction built from the provided quote.
        method: "POST", // WHY: Use POST because we are submitting structured data to create a transaction resource.
        headers: { "Content-Type": "application/json" }, // WHY: Set the Content-Type header so Jupiter knows the request body is JSON.
        body: JSON.stringify(swapBody), // WHY: Serialize the swapBody object to a JSON string for transmission over HTTP.
    }); // WHY: Close the fetch options object.

    if (!swapResponse.ok) { // WHY: Validate the swap API response so we do not attempt to submit a failed or missing transaction.
        throw new Error(`Jupiter swap API error: ${swapResponse.status} ${swapResponse.statusText}`); // WHY: Surface the exact HTTP error so debugging is straightforward.
    } // WHY: Close the error check block.

    const swapData = await swapResponse.json(); // WHY: Parse the swap JSON response to extract the base64-encoded swapTransaction string.
    const swapTransactionBase64 = swapData.swapTransaction; // WHY: Access the swapTransaction field because it contains the serialized transaction bytes encoded as base64.
    if (!swapTransactionBase64) { // WHY: Guard against unexpected Jupiter payloads that might omit the transaction field.
        throw new Error("swapTransaction not found in Jupiter response"); // WHY: Throw a specific error that pinpoints the missing field for debugging.
    } // WHY: Close the guard block.

    const transactionBuffer = Buffer.from(swapTransactionBase64, "base64"); // WHY: Decode the base64 string into a raw byte buffer so we can deserialize it into a Solana transaction object.
    const transaction = VersionedTransaction.deserialize(transactionBuffer); // WHY: Deserialize into a VersionedTransaction because Jupiter returns modern transactions that may use address lookup tables.

    console.log("Signing transaction..."); // WHY: Log the signing step so the operator knows the private key is about to authorize the transaction.
    transaction.sign([keypair]); // WHY: Sign the transaction with the user's keypair to authorize the swap and pay network fees.

    console.log("Submitting to devnet..."); // WHY: Inform the operator that the signed transaction is being broadcast to the Solana network.
    const signature = await connection.sendTransaction(transaction); // WHY: Submit the signed transaction to the RPC which forwards it to the current leader for block inclusion.
    console.log("Transaction submitted:", signature); // WHY: Print the transaction signature so the operator can look it up on a block explorer.

    console.log("Confirming transaction..."); // WHY: Let the operator know the script is waiting for on-chain confirmation.
    await connection.confirmTransaction(signature, "confirmed"); // WHY: Wait for confirmed status so we know the swap executed successfully and is highly unlikely to roll back.
    console.log("Transaction confirmed:", signature); // WHY: Print confirmation so the operator knows the swap completed on-chain.
} // WHY: Close the main function.

main().catch((err) => { // WHY: Call main and attach a catch handler so unhandled promise rejections do not crash the process silently.
    console.error("Swap failed:", err); // WHY: Print the full error to stderr so the operator sees what went wrong.
    process.exit(1); // WHY: Exit with a non-zero code so calling scripts and CI systems know the operation failed.
}); // WHY: Close the catch handler.
