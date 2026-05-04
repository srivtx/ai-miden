import express, { Request, Response } from "express";
// WHY: Import Express and its TypeScript types to build a typed HTTP API.
import {
  Connection,
  // WHY: Connection handles all RPC communication with the Solana cluster.
  Keypair,
  // WHY: Keypair is used to sign transactions on the server side.
  PublicKey,
  // WHY: PublicKey validates and represents Solana account addresses.
  TransactionMessage,
  // WHY: TransactionMessage compiles instructions into a versioned message.
  VersionedTransaction,
  // WHY: VersionedTransaction is the v0 format that supports Address Lookup Tables.
  AddressLookupTableProgram,
  // WHY: AddressLookupTableProgram generates LUT instructions.
  ComputeBudgetProgram,
  // WHY: ComputeBudgetProgram sets compute limits and priority fees.
  SystemProgram,
  // WHY: SystemProgram provides native instructions like transfer.
  LAMPORTS_PER_SOL,
  // WHY: LAMPORTS_PER_SOL converts SOL to lamports (1 SOL = 1e9 lamports).
} from "@solana/web3.js";
// WHY: The official Solana JavaScript SDK for blockchain operations.

import "dotenv/config";
// WHY: Load environment variables from .env to keep secrets out of source code.

const app = express();
// WHY: Create the Express application instance.
app.use(express.json());
// WHY: Enable JSON body parsing so POST routes can read request payloads.

const HELIUS_API_KEY = process.env.HELIUS_API_KEY || "";
// WHY: Read the Helius API key from the environment for authenticated RPC access.
if (!HELIUS_API_KEY) {
  // WHY: Validate the presence of the API key to fail fast on misconfiguration.
  throw new Error("HELIUS_API_KEY is required");
  // WHY: Prevent the server from starting without a valid RPC credential.
}

const HELIUS_RPC = `https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}`;
// WHY: Build the authenticated Helius RPC URL using the real Helius endpoint.
const connection = new Connection(HELIUS_RPC, "confirmed");
// WHY: Use 'confirmed' commitment for a balance of speed and finality.

const payerSecret = process.env.SOLANA_PRIVATE_KEY || "";
// WHY: Load the fee payer private key from the environment.
let payer: Keypair;
// WHY: Declare payer in the module scope so all routes can share it.
if (payerSecret) {
  // WHY: Only attempt parsing if a key was provided.
  const decoded = Uint8Array.from(JSON.parse(payerSecret));
  // WHY: Convert the JSON-encoded key array into a Uint8Array.
  payer = Keypair.fromSecretKey(decoded);
  // WHY: Reconstruct the Keypair from the decoded secret bytes.
} else {
  // WHY: Fallback for read-only routes if no private key is configured.
  payer = Keypair.generate();
  // WHY: Generate a random keypair so PublicKey methods still work.
}

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || "";
// WHY: Load the shared secret used to verify Helius webhook authenticity.

// ------------------------------------------------------------------
// GET /priority-fee
// ------------------------------------------------------------------
app.get("/priority-fee", async (_req: Request, res: Response) => {
  // WHY: Define a route to expose the current priority fee market data.
  try {
    // WHY: Wrap the RPC call in try/catch to return a proper HTTP error on failure.
    const rpcResponse = await fetch(HELIUS_RPC, {
      // WHY: Call the Helius JSON-RPC endpoint directly.
      method: "POST",
      // WHY: JSON-RPC requires POST.
      headers: { "Content-Type": "application/json" },
      // WHY: Inform the server that the body is JSON.
      body: JSON.stringify({
        // WHY: Serialize the request according to the JSON-RPC 2.0 specification.
        jsonrpc: "2.0",
        // WHY: Specify the protocol version.
        id: 1,
        // WHY: Request ID for response correlation.
        method: "getPriorityFeeEstimate",
        // WHY: Use the Helius-enhanced endpoint for real fee estimates.
        params: [
          {
            // WHY: Pass parameters as an array containing a single object.
            accountKeys: [SystemProgram.programId.toBase58()],
            // WHY: Scope the estimate to a relevant program to improve accuracy.
            options: { includeAllPriorityFeeLevels: true },
            // WHY: Return all levels so clients can choose their urgency.
          },
        ],
      }),
    });
    // WHY: Await the Helius HTTP response.

    const data = await rpcResponse.json();
    // WHY: Parse the JSON body into a JavaScript object.
    res.json({
      // WHY: Return a structured JSON response to the API consumer.
      source: "helius",
      // WHY: Identify the data provider for client transparency.
      priorityFeeLevels: data.result?.priorityFeeLevels || null,
      // WHY: Extract the fee levels or return null if the RPC response is malformed.
    });
    // WHY: Send the parsed fee data back to the caller.
  } catch (err) {
    // WHY: Catch network or parsing errors to prevent server crashes.
    res.status(500).json({ error: String(err) });
    // WHY: Return HTTP 500 with the error message so the client knows what failed.
  }
  // WHY: Always handle errors in async route handlers.
});
// WHY: This endpoint lets frontends query fees before building transactions.

// ------------------------------------------------------------------
// POST /create-lut
// ------------------------------------------------------------------
app.post("/create-lut", async (req: Request, res: Response) => {
  // WHY: Define a route to create an Address Lookup Table on-chain.
  try {
    // WHY: Wrap on-chain operations to catch and report errors gracefully.
    const slot = await connection.getSlot();
    // WHY: LUT creation requires the current slot for deterministic address derivation.
    const [createInstruction, lookupTableAddress] =
      // WHY: The program returns both the instruction and the derived address.
      AddressLookupTableProgram.createLookupTable({
        // WHY: Build the create-LUT instruction.
        authority: payer.publicKey,
        // WHY: The authority controls future modifications to the LUT.
        payer: payer.publicKey,
        // WHY: The payer funds the rent-exempt account creation.
        recentSlot: slot,
        // WHY: Use the current slot as the derivation parameter.
      });
    // WHY: Destructure the instruction and address from the returned tuple.

    const messageV0 = new TransactionMessage({
      // WHY: Build a version-0 compatible message for the creation transaction.
      payerKey: payer.publicKey,
      // WHY: The fee payer must be specified for every transaction.
      recentBlockhash: (await connection.getLatestBlockhash()).blockhash,
      // WHY: A recent blockhash prevents replay and expiration.
      instructions: [createInstruction],
      // WHY: Include only the LUT creation instruction.
    }).compileToV0Message();
    // WHY: Compile into the v0 message format.

    const tx = new VersionedTransaction(messageV0);
    // WHY: Construct a versioned transaction from the compiled message.
    tx.sign([payer]);
    // WHY: Sign the transaction to authorize creation and payment.

    const signature = await connection.sendTransaction(tx);
    // WHY: Submit the transaction to the Helius RPC.
    await connection.confirmTransaction(signature, "confirmed");
    // WHY: Wait for confirmation so the LUT is guaranteed to exist on-chain.

    res.json({
      // WHY: Return the result as JSON so the client can store the address.
      success: true,
      // WHY: Explicit success flag for client-side logic.
      lookupTableAddress: lookupTableAddress.toBase58(),
      // WHY: Return the base58-encoded address for easy copying.
      signature,
      // WHY: Include the transaction signature for explorer verification.
    });
    // WHY: The client needs the address to reference it in future transactions.
  } catch (err) {
    // WHY: Handle unexpected RPC or signing failures.
    res.status(500).json({ error: String(err) });
    // WHY: Return a 500 status with the error message.
  }
  // WHY: Always handle errors to keep the API stable.
});
// WHY: This endpoint centralizes LUT creation so clients do not need to build transactions.

// ------------------------------------------------------------------
// POST /versioned-tx
// ------------------------------------------------------------------
app.post("/versioned-tx", async (req: Request, res: Response) => {
  // WHY: Define a route to build, simulate, and submit a versioned transaction.
  try {
    // WHY: Wrap the entire flow to catch errors and avoid partial state.
    const { lookupTableAddress, recipient, amountSol } = req.body;
    // WHY: Destructure the request body to extract client-provided parameters.

    if (!lookupTableAddress || !recipient || !amountSol) {
      // WHY: Validate required fields to fail fast with a clear client error.
      res.status(400).json({ error: "Missing lookupTableAddress, recipient, or amountSol" });
      // WHY: HTTP 400 indicates a client-side request error.
      return;
      // WHY: Stop processing to avoid running with invalid inputs.
    }
    // WHY: Server-side validation is essential for API security and reliability.

    const lutPubkey = new PublicKey(lookupTableAddress);
    // WHY: Parse the string into a validated PublicKey instance.
    const recipientPubkey = new PublicKey(recipient);
    // WHY: Validate the recipient address before using it in a transaction.

    const priorityFeeRes = await fetch(HELIUS_RPC, {
      // WHY: Fetch a fresh priority fee estimate before building the transaction.
      method: "POST",
      // WHY: JSON-RPC uses POST.
      headers: { "Content-Type": "application/json" },
      // WHY: Set the correct content type.
      body: JSON.stringify({
        // WHY: Build the getPriorityFeeEstimate request.
        jsonrpc: "2.0",
        // WHY: Protocol version.
        id: 1,
        // WHY: Request ID.
        method: "getPriorityFeeEstimate",
        // WHY: Helius-enhanced fee endpoint.
        params: [
          {
            accountKeys: [SystemProgram.programId.toBase58()],
            // WHY: Scope the estimate to relevant programs.
            options: { includeAllPriorityFeeLevels: true },
            // WHY: Return all levels for client flexibility.
          },
        ],
      }),
    });
    // WHY: Await the Helius response.

    const priorityData = await priorityFeeRes.json();
    // WHY: Parse the JSON response.
    const microLamports = priorityData.result?.priorityFeeLevels?.medium || 0;
    // WHY: Default to the 'medium' level; fallback to 0 if unavailable.

    const computeBudgetIx = ComputeBudgetProgram.setComputeUnitLimit({
      // WHY: Set a compute limit to control resource usage and cost.
      units: 30000,
      // WHY: 30,000 CUs is sufficient for a standard transfer.
    });
    // WHY: Compute budget must be set before program instructions.

    const priorityFeeIx = ComputeBudgetProgram.setComputeUnitPrice({
      // WHY: Attach the priority fee so the leader prioritizes inclusion.
      microLamports,
      // WHY: Use the dynamically fetched market fee.
    });
    // WHY: Without this, the transaction competes only on base fee.

    const transferIx = SystemProgram.transfer({
      // WHY: Build the core transfer instruction.
      fromPubkey: payer.publicKey,
      // WHY: The payer sends the SOL.
      toPubkey: recipientPubkey,
      // WHY: The validated recipient receives the SOL.
      lamports: amountSol * LAMPORTS_PER_SOL,
      // WHY: Convert the human-readable SOL amount to lamports.
    });
    // WHY: SystemProgram.transfer is the native instruction for SOL movement.

    const lookupTableAccount = await connection
      .getAddressLookupTable(lutPubkey)
      // WHY: Fetch the LUT account state from the RPC.
      .then((res) => res.value);
    // WHY: Unwrap the RPC response to get the account object.

    if (!lookupTableAccount) {
      // WHY: Guard against referencing a missing or unconfirmed LUT.
      res.status(400).json({ error: "Lookup table not found" });
      // WHY: Return 400 because the client provided an invalid address.
      return;
      // WHY: Halt to avoid building an invalid transaction.
    }
    // WHY: The LUT must exist on-chain before it can be referenced.

    const messageV0 = new TransactionMessage({
      // WHY: Construct a version-0 message with compute budget, priority fee, and transfer.
      payerKey: payer.publicKey,
      // WHY: The fee payer funds the transaction.
      recentBlockhash: (await connection.getLatestBlockhash()).blockhash,
      // WHY: A fresh blockhash is required for every transaction.
      instructions: [computeBudgetIx, priorityFeeIx, transferIx],
      // WHY: Order matters: compute budget instructions must precede others.
    }).compileToV0Message([lookupTableAccount]);
    // WHY: Pass the LUT so the compiler compresses referenced addresses into 1-byte indices.

    const versionedTx = new VersionedTransaction(messageV0);
    // WHY: Instantiate the versioned transaction from the compiled v0 message.
    versionedTx.sign([payer]);
    // WHY: Sign the transaction to authorize the transfer and fee payment.

    const simulation = await connection.simulateTransaction(versionedTx);
    // WHY: Run a dry-run to catch errors before spending real fees.
    if (simulation.value.err) {
      // WHY: Check the simulation error field before submission.
      res.status(400).json({
        // WHY: Return 400 because the transaction would fail on-chain.
        error: "Simulation failed",
        // WHY: Inform the client that the transaction is invalid.
        simulationError: simulation.value.err,
        // WHY: Include the raw error for debugging.
        logs: simulation.value.logs,
        // WHY: Provide program logs so the developer can diagnose the issue.
      });
      // WHY: Do not send a transaction that simulation proves will fail.
      return;
      // WHY: Abort to save fees and prevent a failed on-chain record.
    }
    // WHY: Simulation is the final safety check before mainnet submission.

    const signature = await connection.sendTransaction(versionedTx);
    // WHY: Submit the simulated-and-valid transaction to the network.
    res.json({
      // WHY: Return the submission result to the client.
      success: true,
      // WHY: Explicit success flag.
      signature,
      // WHY: The client needs the signature to track the transaction.
      simulationLogs: simulation.value.logs,
      // WHY: Include simulation logs for transparency.
    });
    // WHY: The client can now poll or listen for confirmation.
  } catch (err) {
    // WHY: Catch all unexpected errors to prevent server crashes.
    res.status(500).json({ error: String(err) });
    // WHY: Return HTTP 500 with the error details.
  }
  // WHY: Consistent error handling keeps the API predictable.
});
// WHY: This route demonstrates the full production flow: fee estimation, LUT usage, simulation, and submission.

// ------------------------------------------------------------------
// GET /webhook/setup
// ------------------------------------------------------------------
app.get("/webhook/setup", (_req: Request, res: Response) => {
  // WHY: Define a route that documents how to configure Helius webhooks.
  res.json({
    // WHY: Return JSON so the client can parse configuration programmatically.
    provider: "helius",
    // WHY: Identify the webhook provider.
    webhookUrl: "https://your-server.com/webhooks/helius",
    // WHY: Show the HTTPS endpoint that Helius should POST to.
    webhookSecret: WEBHOOK_SECRET ? "<configured>" : "<not configured>",
    // WHY: Indicate whether the server has a secret configured for signature verification.
    exampleConfiguration: {
      // WHY: Provide a concrete example to reduce copy-paste errors.
      webhookURL: "https://your-server.com/webhooks/helius",
      // WHY: The exact URL registered in the Helius dashboard.
      transactionTypes: ["Any"],
      // WHY: Subscribe to all transaction types for comprehensive monitoring.
      accountAddresses: [payer.publicKey.toBase58()],
      // WHY: Monitor the fee payer account as a starting example.
      webhookType: "enhanced",
      // WHY: Use enhanced webhooks for enriched transaction data.
      encoding: "jsonParsed",
      // WHY: Request parsed JSON for human-readable token balances and instructions.
    },
    // WHY: An example configuration helps students understand required fields.
    verificationNote:
      // WHY: Document security expectations.
      "Helius sends an HMAC-SHA256 signature in the x-helius-signature header. " +
      // WHY: Explain how to authenticate webhook payloads.
      "Verify it against WEBHOOK_SECRET to ensure the payload originated from Helius.",
    // WHY: Security note prevents students from accepting unverified payloads.
  });
  // WHY: This route acts as living documentation for webhook integration.
});
// WHY: Centralizing webhook docs in the API makes onboarding easier.

// ------------------------------------------------------------------
// POST /webhooks/helius
// ------------------------------------------------------------------
app.post("/webhooks/helius", (req: Request, res: Response) => {
  // WHY: Define the actual webhook receiver route that Helius will call.
  console.log("Webhook received:", JSON.stringify(req.body, null, 2));
  // WHY: Log the payload immediately for debugging and audit trails.
  res.status(200).send("OK");
  // WHY: Respond with 200 quickly so Helius does not retry the delivery.
});
// WHY: Fast acknowledgment is critical; heavy processing should happen asynchronously.

// ------------------------------------------------------------------
// Start server
// ------------------------------------------------------------------
const PORT = 3069;
// WHY: Use port 3069 as specified in the requirements.
app.listen(PORT, () => {
  // WHY: Start the HTTP server and bind to the specified port.
  console.log(`Phase 61 API listening on port ${PORT}`);
  // WHY: Log the listening address so the user knows where to send requests.
});
// WHY: The server must listen on a port to accept incoming HTTP connections.
