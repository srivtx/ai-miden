import express, { Request, Response } from "express";
// WHY: Express provides the HTTP server framework for routing and middleware.
import { Connection, PublicKey, Keypair, Transaction } from "@solana/web3.js";
// WHY: Solana web3.js is the standard library for constructing transactions and interacting with the Solana JSON-RPC API.
import * as bs58 from "bs58";
// WHY: bs58 is used to decode base58-encoded private keys and transaction signatures, which is Solana's standard encoding.

const app = express();
// WHY: Create the Express application instance that will handle all HTTP requests.
app.use(express.json());
// WHY: JSON body parsing is required because all POST routes accept structured JSON payloads.

const PORT = 3060;
// WHY: Port 3060 is dedicated to the bridge API to avoid conflicts with common ports like 3000 or 8080.

const SOLANA_RPC = process.env.SOLANA_RPC || "http://127.0.0.1:8899";
// WHY: The RPC endpoint connects to the Solana cluster; defaulting to localhost supports local development.
const connection = new Connection(SOLANA_RPC, "confirmed");
// WHY: "confirmed" commitment ensures the API waits for transaction finality before responding, preventing race conditions.

const BRIDGE_PROGRAM_ID = new PublicKey(process.env.BRIDGE_PROGRAM_ID || "Bridge11111111111111111111111111111111111111");
// WHY: The bridge program ID tells the API which on-chain program to invoke for lock, mint, burn, and release.
const GUARDIAN_PROGRAM_ID = new PublicKey(process.env.GUARDIAN_PROGRAM_ID || "Guardian1111111111111111111111111111111111");
// WHY: The guardian program ID is needed for registering guardians and verifying attestations.

const PAYER_KEYPAIR = Keypair.fromSecretKey(
  bs58.decode(process.env.PAYER_PRIVATE_KEY || "1111111111111111111111111111111111111111111111111111111111111111")
);
// WHY: The payer keypair signs and pays for all on-chain transactions submitted by the API.

app.post("/lock", async (req: Request, res: Response) => {
  // WHY: POST /lock is the entry point for users to deposit original tokens into the bridge vault.
  const { userPublicKey, amount, targetRecipient } = req.body;
  // WHY: Destructure the request body to extract the lock parameters.
  if (!userPublicKey || !amount || !targetRecipient) {
    // WHY: Validating inputs prevents submitting malformed transactions that would waste gas and fail on-chain.
    return res.status(400).json({ error: "Missing required fields: userPublicKey, amount, targetRecipient" });
  }
  try {
    // WHY: Wrapping in try/catch ensures database or network errors return a 500 instead of crashing the process.
    const userPubkey = new PublicKey(userPublicKey);
    // WHY: Converting the string to a PublicKey validates the base58 encoding and prevents invalid addresses.
    const targetPubkey = new PublicKey(targetRecipient);
    // WHY: The target recipient must be a valid Solana address for wrapped token minting.
    const transaction = new Transaction();
    // WHY: A new Transaction holds all instructions for this atomic operation.
    // WHY: In production, the API would construct the Lock instruction with the bridge program and add it here.
    // For this educational API, we return a simulated success with the transaction structure.
    const txHash = "simulated_lock_tx_" + Date.now();
    // WHY: Generating a simulated transaction hash allows frontend integration before the program is fully deployed.
    res.json({ success: true, txHash, user: userPubkey.toBase58(), amount, targetRecipient: targetPubkey.toBase58() });
    // WHY: Returning structured JSON allows the client to track the lock by txHash and poll for mint status.
  } catch (error: any) {
    // WHY: Catching errors prevents server crashes and allows meaningful error messages to reach the client.
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /lock to the Express application.

app.post("/mint", async (req: Request, res: Response) => {
  // WHY: POST /mint triggers the creation of wrapped tokens after lock verification by guardians.
  const { recipient, amount, nonce, signatures, guardianIndices } = req.body;
  // WHY: Minting requires proof in the form of guardian signatures to prevent unauthorized inflation.
  if (!recipient || !amount || nonce === undefined || !signatures || !guardianIndices) {
    // WHY: Incomplete proofs must be rejected because the on-chain program would fail anyway.
    return res.status(400).json({ error: "Missing required fields" });
  }
  try {
    const recipientPubkey = new PublicKey(recipient);
    // WHY: Validate the recipient address before constructing the transaction.
    const transaction = new Transaction();
    // WHY: The transaction will contain the MintWrapped instruction.
    // WHY: The API would add the instruction with the bridge program, accounts, and proof data.
    const txHash = "simulated_mint_tx_" + Date.now();
    // WHY: Simulation allows integration testing without requiring a live guardian network.
    res.json({ success: true, txHash, recipient: recipientPubkey.toBase58(), amount, nonce });
    // WHY: The client uses txHash to track when wrapped tokens arrive in the recipient wallet.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /mint to the Express application.

app.post("/burn", async (req: Request, res: Response) => {
  // WHY: POST /burn initiates the reverse bridge by destroying wrapped tokens on Solana.
  const { userPublicKey, amount, sourceRecipient } = req.body;
  // WHY: The user must specify the source chain address where original tokens should be released.
  if (!userPublicKey || !amount || !sourceRecipient) {
    // WHY: Missing fields would cause the burn transaction to be invalid.
    return res.status(400).json({ error: "Missing required fields" });
  }
  try {
    const userPubkey = new PublicKey(userPublicKey);
    // WHY: Validate the user's Solana address.
    const transaction = new Transaction();
    // WHY: A new transaction will hold the BurnWrapped instruction.
    const txHash = "simulated_burn_tx_" + Date.now();
    // WHY: Simulation supports testing of the full round-trip flow.
    res.json({ success: true, txHash, user: userPubkey.toBase58(), amount, sourceRecipient });
    // WHY: Returning the txHash lets the user monitor the subsequent release on the source chain.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /burn to the Express application.

app.post("/release", async (req: Request, res: Response) => {
  // WHY: POST /release returns original tokens from the vault after a burn event is verified by guardians.
  const { recipient, amount, nonce, signatures, guardianIndices } = req.body;
  // WHY: Release requires the same threshold proof as minting to prevent unauthorized vault drainage.
  if (!recipient || !amount || nonce === undefined || !signatures || !guardianIndices) {
    // WHY: Without a full proof, the on-chain program would reject the release.
    return res.status(400).json({ error: "Missing required fields" });
  }
  try {
    const recipientPubkey = new PublicKey(recipient);
    // WHY: Validate the destination address for the released tokens.
    const transaction = new Transaction();
    // WHY: The transaction will contain the Release instruction.
    const txHash = "simulated_release_tx_" + Date.now();
    // WHY: Simulation allows testing without a full cross-chain setup.
    res.json({ success: true, txHash, recipient: recipientPubkey.toBase58(), amount, nonce });
    // WHY: The client can track the return of original tokens using the returned txHash.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /release to the Express application.

app.post("/guardian/register", async (req: Request, res: Response) => {
  // WHY: POST /guardian/register adds a new guardian to the on-chain registry with an initial stake.
  const { guardianPublicKey, stake } = req.body;
  // WHY: The guardian's public key and stake amount are required to create the on-chain record.
  if (!guardianPublicKey || stake === undefined) {
    // WHY: Rejecting incomplete data prevents invalid guardian entries.
    return res.status(400).json({ error: "Missing required fields" });
  }
  try {
    const guardianPubkey = new PublicKey(guardianPublicKey);
    // WHY: Validate the public key format before submitting to the program.
    const transaction = new Transaction();
    // WHY: The transaction will invoke the guardian program's RegisterGuardian instruction.
    const txHash = "simulated_register_tx_" + Date.now();
    // WHY: Simulation allows governance interfaces to be built before mainnet deployment.
    res.json({ success: true, txHash, guardian: guardianPubkey.toBase58(), stake });
    // WHY: Returning the transaction hash confirms the registration request was received and processed.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /guardian/register to the Express application.

app.post("/guardian/attest", async (req: Request, res: Response) => {
  // WHY: POST /guardian/attest records a guardian's off-chain signature on-chain for transparency.
  const { guardianPublicKey, eventHash } = req.body;
  // WHY: The guardian public key identifies the signer, and the eventHash identifies the attested event.
  if (!guardianPublicKey || !eventHash) {
    // WHY: Both fields are required to construct a valid attestation log entry.
    return res.status(400).json({ error: "Missing required fields" });
  }
  try {
    const guardianPubkey = new PublicKey(guardianPublicKey);
    // WHY: Validate the guardian address.
    const transaction = new Transaction();
    // WHY: The transaction will invoke the guardian program's AttestEvent instruction.
    const txHash = "simulated_attest_tx_" + Date.now();
    // WHY: Simulation supports testing of the attestation aggregation pipeline.
    res.json({ success: true, txHash, guardian: guardianPubkey.toBase58(), eventHash });
    // WHY: The returned hash allows relayers to include this attestation in a threshold proof.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds POST /guardian/attest to the Express application.

app.get("/guardian/list", async (req: Request, res: Response) => {
  // WHY: GET /guardian/list returns the current active guardian set so users and relayers know who can attest.
  try {
    // WHY: In production, this would fetch the GuardianRegistry account and deserialize the guardian vector.
    const guardians = [
      // WHY: Returning mock data allows the frontend to render the guardian list before mainnet launch.
      { pubkey: "Guardian1111111111111111111111111111111111", stake: 1000000, active: true, slashCount: 0 },
      { pubkey: "Guardian2222222222222222222222222222222222", stake: 2000000, active: true, slashCount: 0 },
      { pubkey: "Guardian3333333333333333333333333333333333", stake: 1500000, active: true, slashCount: 0 },
    ];
    // WHY: A hardcoded list is sufficient for educational testing; production uses on-chain deserialization.
    res.json({ success: true, guardians, threshold: 3 });
    // WHY: Including the threshold helps clients understand how many signatures are required for a valid proof.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds GET /guardian/list to the Express application.

app.get("/bridge/status/:tx", async (req: Request, res: Response) => {
  // WHY: GET /bridge/status/:tx allows clients to poll the state of a specific bridge transaction.
  const { tx } = req.params;
  // WHY: The tx parameter is the source chain transaction hash or the bridge nonce.
  if (!tx) {
    // WHY: A missing parameter would make the lookup impossible.
    return res.status(400).json({ error: "Missing transaction identifier" });
  }
  try {
    // WHY: In production, this would query a database or indexer for the lock/mint/burn/release state.
    const status = "pending";
    // WHY: "pending" is the default state before a relayer delivers the proof to the target chain.
    res.json({ success: true, tx, status, details: "Waiting for guardian threshold and relay" });
    // WHY: Returning a status and detail message keeps the user informed during the multi-step bridging process.
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});
// WHY: The route handler closes and binds GET /bridge/status/:tx to the Express application.

app.listen(PORT, () => {
  // WHY: The listen callback confirms the server is ready to accept connections.
  console.log(`Bridge API listening on port ${PORT}`);
  // WHY: Logging the port aids debugging and confirms successful startup.
});
// WHY: The listen call binds to the port and begins accepting connections.
