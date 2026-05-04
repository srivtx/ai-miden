import express from "express";                          // WHY: Imports the Express framework for building the HTTP API server.
import * as anchor from "@coral-xyz/anchor";            // WHY: Imports the Anchor client library to interact with the deployed Solana program.
import { Program, AnchorProvider, web3, BN } from "@coral-xyz/anchor"; // WHY: Imports specific Anchor classes for typed program interaction and Solana primitives.
import { Counter } from "./target/types/counter";       // WHY: Imports the generated IDL types so the client methods are type-safe.
import fs from "fs";                                    // WHY: Imports the filesystem module to read the local Solana keypair for signing transactions.
import path from "path";                                // WHY: Imports the path module to resolve the keypair file location in a cross-platform way.

const app = express();                                  // WHY: Creates a new Express application instance that will handle HTTP requests.
app.use(express.json());                                // WHY: Registers middleware to parse JSON request bodies so routes can read incoming data.

const PROGRAM_ID = new web3.PublicKey("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"); // WHY: Defines the on-chain program ID that the API will interact with.

const keypairPath = path.resolve(process.env.HOME || "", ".config/solana/id.json"); // WHY: Resolves the default Solana keypair path so the API can sign transactions.
const secretKey = Uint8Array.from(JSON.parse(fs.readFileSync(keypairPath, "utf-8"))); // WHY: Reads and parses the keypair file into a byte array for the wallet.
const walletKeypair = web3.Keypair.fromSecretKey(secretKey); // WHY: Creates a Keypair object from the secret key so it can be used as a transaction signer.

const connection = new web3.Connection("https://api.devnet.solana.com", "confirmed"); // WHY: Establishes a connection to Solana devnet with confirmed commitment for reliable reads.

const provider = new AnchorProvider(connection, new anchor.Wallet(walletKeypair), {}); // WHY: Creates an Anchor provider that couples the connection with the signing wallet.
anchor.setProvider(provider);                           // WHY: Sets the provider as the default for all Program instances created in this process.

const idlPath = path.resolve(__dirname, "target/idl/counter.json"); // WHY: Resolves the path to the generated IDL file which describes the program interface.
const idl = JSON.parse(fs.readFileSync(idlPath, "utf-8")); // WHY: Loads and parses the IDL JSON so the Program constructor can generate typed methods.

const program = new Program<Counter>(idl, PROGRAM_ID, provider); // WHY: Creates a typed Program instance that exposes methods matching the IDL instructions.

app.post("/initialize", async (req, res) => {          // WHY: Defines the POST /initialize route that creates a new counter account for a given payer.
  try {                                                 // WHY: Begins error handling so RPC or program errors return HTTP 500 instead of crashing the server.
    const payerPubkey = new web3.PublicKey(req.body.payer); // WHY: Parses the payer address from the request body to derive the PDA and fund creation.

    const [counterPda] = web3.PublicKey.findProgramAddressSync( // WHY: Derives the counter PDA off-chain using the same seeds as the Anchor program.
      [Buffer.from("counter"), payerPubkey.toBuffer()], // WHY: Uses the static seed and payer public key to match the program's PDA derivation exactly.
      PROGRAM_ID                                        // WHY: Uses the program ID so the address is derived from the correct program's address space.
    );

    const tx = await program.methods                    // WHY: Starts building the initialize instruction transaction via the typed Anchor client.
      .initialize()                                     // WHY: Selects the initialize instruction from the IDL which requires no additional arguments.
      .accounts({                                       // WHY: Begins the accounts mapping so Anchor knows which public keys to include in the transaction.
        counter: counterPda,                            // WHY: Provides the derived PDA as the counter account address that the program will create.
        payer: payerPubkey,                             // WHY: Provides the payer address so Anchor knows who funds the rent and signs the creation.
        systemProgram: web3.SystemProgram.programId,    // WHY: Provides the System Program ID which Anchor needs to create the account on-chain.
      })
      .rpc();                                           // WHY: Sends the transaction to devnet, signs it with the provider wallet, and waits for confirmation.

    return res.json({ success: true, signature: tx, counter: counterPda.toBase58() }); // WHY: Returns the transaction signature and counter address so the client can track it.
  } catch (err) {                                       // WHY: Catches any errors from invalid public keys, insufficient funds, or program constraint failures.
    console.error("Initialize error:", err);            // WHY: Logs the error server-side for debugging and monitoring purposes.
    return res.status(500).json({ success: false, error: (err as Error).message }); // WHY: Returns HTTP 500 with the error message so the HTTP client knows the operation failed.
  }
});

app.post("/increment", async (req, res) => {            // WHY: Defines the POST /increment route that increases an existing counter by one.
  try {                                                 // WHY: Begins error handling to catch invalid accounts or authorization failures.
    const payerPubkey = new web3.PublicKey(req.body.payer); // WHY: Parses the payer address from the request body to identify which counter to increment.

    const [counterPda] = web3.PublicKey.findProgramAddressSync( // WHY: Re-derives the PDA to ensure we target the correct counter account for this payer.
      [Buffer.from("counter"), payerPubkey.toBuffer()], // WHY: Uses identical seeds to the initialize route so the PDA matches the created account.
      PROGRAM_ID                                        // WHY: Uses the same program ID for consistent address derivation.
    );

    const tx = await program.methods                    // WHY: Starts building the increment instruction transaction.
      .increment()                                      // WHY: Selects the increment instruction which takes no arguments.
      .accounts({                                       // WHY: Begins mapping the accounts required by the Update context in the program.
        counter: counterPda,                            // WHY: Targets the existing counter PDA so the program increments the right account.
        payer: payerPubkey,                             // WHY: Provides the payer as the signer because the Update context requires a signer.
      })
      .rpc();                                           // WHY: Sends the increment transaction to devnet and waits for confirmation.

    return res.json({ success: true, signature: tx });  // WHY: Returns the transaction signature so the client can confirm the increment on-chain.
  } catch (err) {                                       // WHY: Catches errors such as missing accounts, wrong signer, or constraint violations.
    console.error("Increment error:", err);             // WHY: Logs the error for server-side debugging.
    return res.status(500).json({ success: false, error: (err as Error).message }); // WHY: Returns HTTP 500 to indicate the increment operation failed.
  }
});

app.post("/decrement", async (req, res) => {            // WHY: Defines the POST /decrement route that decreases an existing counter by one.
  try {                                                 // WHY: Begins error handling to catch underflow or authorization errors.
    const payerPubkey = new web3.PublicKey(req.body.payer); // WHY: Parses the payer address from the request body to identify which counter to decrement.

    const [counterPda] = web3.PublicKey.findProgramAddressSync( // WHY: Re-derives the PDA to target the correct counter account.
      [Buffer.from("counter"), payerPubkey.toBuffer()], // WHY: Uses the same seeds as initialization and increment to find the matching account.
      PROGRAM_ID                                        // WHY: Uses the program ID for deterministic PDA derivation.
    );

    const tx = await program.methods                    // WHY: Starts building the decrement instruction transaction.
      .decrement()                                      // WHY: Selects the decrement instruction which takes no arguments.
      .accounts({                                       // WHY: Begins mapping the accounts required by the Update context.
        counter: counterPda,                            // WHY: Targets the existing counter PDA so the program decrements the correct account.
        payer: payerPubkey,                             // WHY: Provides the payer as the signer because the Update context requires a signer.
      })
      .rpc();                                           // WHY: Sends the decrement transaction to devnet and waits for confirmation.

    return res.json({ success: true, signature: tx });  // WHY: Returns the transaction signature so the client can verify the operation on-chain.
  } catch (err) {                                       // WHY: Catches errors such as missing accounts, wrong signer, or constraint violations.
    console.error("Decrement error:", err);             // WHY: Logs the error for server-side debugging.
    return res.status(500).json({ success: false, error: (err as Error).message }); // WHY: Returns HTTP 500 to indicate the decrement operation failed.
  }
});

app.get("/count/:address", async (req, res) => {        // WHY: Defines the GET /count/:address route that reads the current count without signing a transaction.
  try {                                                 // WHY: Begins error handling for invalid addresses or missing accounts.
    const counterPubkey = new web3.PublicKey(req.params.address); // WHY: Parses the counter PDA address from the URL path parameter.

    const account = await program.account.counterAccount.fetch(counterPubkey); // WHY: Fetches the on-chain account data using Anchor's typed account fetch method.

    return res.json({                                   // WHY: Returns the account state as JSON so HTTP clients can read the counter value.
      success: true,                                    // WHY: Indicates the fetch succeeded so the client knows the data is valid.
      count: account.count.toNumber(),                  // WHY: Converts the BN count to a plain JavaScript number for JSON serialization.
      bump: account.bump,                               // WHY: Includes the bump seed so the client can verify the PDA if needed.
    });
  } catch (err) {                                       // WHY: Catches errors when the account does not exist or the address is invalid.
    console.error("Fetch error:", err);                 // WHY: Logs the error server-side for debugging.
    return res.status(404).json({ success: false, error: (err as Error).message }); // WHY: Returns HTTP 404 because a missing account is a resource-not-found scenario.
  }
});

const PORT = 3067;                                      // WHY: Defines the TCP port that the Express server will listen on for incoming HTTP requests.
app.listen(PORT, () => {                                // WHY: Starts the HTTP server and binds it to the specified port.
  console.log(`Counter API listening on port ${PORT}`); // WHY: Logs the startup message so the operator knows the server is ready to accept requests.
});
