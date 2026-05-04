import express from "express"; // WHY: Import the Express framework to build the REST API server.
import { Connection, Keypair, PublicKey, Transaction, sendAndConfirmTransaction } from "@solana/web3.js"; // WHY: Import Solana web3 utilities including Transaction and sendAndConfirmTransaction for manual instruction assembly.
import { createMint, getAccount, createTransferInstruction, TOKEN_2022_PROGRAM_ID } from "@solana/spl-token"; // WHY: Import Token-2022 functions, the transfer instruction builder, and the real program ID.
import { createInitializeMetadataInstruction } from "@solana/spl-token-metadata"; // WHY: Import the metadata instruction helper for Token-2022.
const app = express(); // WHY: Create an Express application instance to register routes and middleware.
app.use(express.json()); // WHY: Enable JSON body parsing so POST requests can read incoming parameters.
const connection = new Connection("http://localhost:8899", "confirmed"); // WHY: Connect to the local validator with confirmed commitment for reliable reads.
const payer = Keypair.generate(); // WHY: Generate a payer keypair that will fund all blockchain transactions in this demo.
app.post("/mint/create", async (req, res) => { // WHY: Register a route to create a new Token-2022 mint on-chain.
    const decimals = req.body.decimals || 9; // WHY: Read decimals from the request body, defaulting to 9 for standard token behavior.
    const mint = await createMint( // WHY: Call the spl-token helper to create a new Token-2022 mint account.
        connection, // WHY: Pass the RPC connection so the helper can send the transaction.
        payer, // WHY: Pass the payer to fund the mint account creation lamports.
        payer.publicKey, // WHY: Set the payer as the mint authority who can later mint tokens.
        null, // WHY: Pass null for freeze authority because this demo does not freeze accounts.
        decimals, // WHY: Pass the chosen decimals so token amounts are represented correctly.
        undefined, // WHY: Pass undefined for optional keypair so the helper generates a random mint address.
        undefined, // WHY: Pass undefined for confirm options to use the default confirmation strategy.
        TOKEN_2022_PROGRAM_ID // WHY: Specify the real Token-2022 program ID instead of legacy SPL Token.
    ); // WHY: Close the createMint call.
    res.json({ mint: mint.toBase58() }); // WHY: Return the new mint address in JSON so the client can reference it.
}); // WHY: Close the /mint/create route handler.
app.post("/mint/metadata", async (req, res) => { // WHY: Register a route to attach metadata to an existing Token-2022 mint.
    const { mint, name, symbol, uri } = req.body; // WHY: Destructure metadata fields from the JSON body for cleaner variable access.
    const mintPubkey = new PublicKey(mint); // WHY: Convert the mint string into a PublicKey for on-chain instructions.
    const metadataIx = createInitializeMetadataInstruction({ // WHY: Build the metadata initialization instruction for the Token-2022 mint.
        mint: mintPubkey, // WHY: Target the mint that will receive the metadata pointer extension.
        metadata: mintPubkey, // WHY: Use the mint itself as the metadata account address for simplicity in this demo.
        mintAuthority: payer.publicKey, // WHY: Set the payer as the authority allowed to update metadata.
        name, // WHY: Pass the token name from the request body.
        symbol, // WHY: Pass the token symbol from the request body.
        uri // WHY: Pass the off-chain URI from the request body.
    }); // WHY: Close the metadata instruction builder.
    res.json({ mint, name, symbol, uri, instruction: metadataIx }); // WHY: Return the submitted metadata and instruction to confirm the endpoint logic.
}); // WHY: Close the /mint/metadata route handler.
app.post("/transfer", async (req, res) => { // WHY: Register a route to transfer Token-2022 tokens between accounts.
    const { from, to, amount, mint } = req.body; // WHY: Extract transfer parameters from the request body to know sender, receiver, quantity, and token type.
    const fromPubkey = new PublicKey(from); // WHY: Convert the sender string into a PublicKey for on-chain validation.
    const toPubkey = new PublicKey(to); // WHY: Convert the recipient string into a PublicKey for on-chain validation.
    const transaction = new Transaction().add( // WHY: Create a new transaction to hold the transfer instruction.
        createTransferInstruction( // WHY: Build the Token-2022 transfer instruction manually so the program ID can be specified.
            fromPubkey, // WHY: Pass the sender token account as the source of the transfer.
            toPubkey, // WHY: Pass the recipient token account as the destination of the transfer.
            payer.publicKey, // WHY: Pass the payer as the owner to authorize the transfer.
            amount, // WHY: Pass the raw token amount to move from source to destination.
            [], // WHY: Pass an empty array for multi-signers because the payer is a single signer.
            TOKEN_2022_PROGRAM_ID // WHY: Explicitly target the real Token-2022 program for the transfer.
        ) // WHY: Close the createTransferInstruction call.
    ); // WHY: Close the transaction builder.
    const signature = await sendAndConfirmTransaction(connection, transaction, [payer]); // WHY: Send and confirm the transaction so the transfer is finalized on-chain.
    res.json({ signature, mint }); // WHY: Return the transaction signature and mint so clients can track the transfer on-chain.
}); // WHY: Close the /transfer route handler.
app.get("/account/:address", async (req, res) => { // WHY: Register a route to read a token account balance and details.
    const address = new PublicKey(req.params.address); // WHY: Parse the URL parameter into a PublicKey for on-chain queries.
    const accountInfo = await getAccount( // WHY: Fetch the parsed token account information from the Token-2022 program.
        connection, // WHY: Use the RPC connection to read the account state.
        address, // WHY: Query the specific account requested by the client.
        undefined, // WHY: Pass undefined for commitment to use the connection default.
        TOKEN_2022_PROGRAM_ID // WHY: Explicitly query the Token-2022 program so the correct account parser is used.
    ); // WHY: Close the getAccount call.
    res.json({ // WHY: Return a JSON object with the account details.
        address: address.toBase58(), // WHY: Echo the queried address for client verification.
        mint: accountInfo.mint.toBase58(), // WHY: Include the mint address to identify which token this account holds.
        owner: accountInfo.owner.toBase58(), // WHY: Include the owner address to show who controls the account.
        amount: accountInfo.amount.toString() // WHY: Convert the balance to string to avoid JSON number precision loss for large integers.
    }); // WHY: Close the JSON response object.
}); // WHY: Close the /account/:address route handler.
app.listen(3070, () => { // WHY: Start the HTTP server on port 3070 as required for this phase.
    console.log("Token-2022 API on port 3070"); // WHY: Log a startup message so the operator knows the server is ready.
}); // WHY: Close the listen callback.
