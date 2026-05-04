import express, { Request, Response } from "express"; // WHY: Import Express to build the HTTP server that exposes compressed token operations via REST endpoints.
import { createRpc } from "@lightprotocol/stateless.js"; // WHY: Import the Light Protocol RPC factory to connect to the compressed-state indexer and ZK prover service.
import { CompressedTokenProgram } from "@lightprotocol/compressed-token"; // WHY: Import the compressed-token SDK to create mints, mint tokens, and execute ZK-verified transfers programmatically.
import { Keypair, PublicKey } from "@solana/web3.js"; // WHY: Import Solana web3.js for keypair reconstruction from secret keys and public key validation.
const app = express(); // WHY: Instantiate the Express application so we can register routes that handle compressed token minting, transfer, and balance queries.
app.use(express.json()); // WHY: Enable JSON body parsing middleware so POST requests can carry structured parameters like recipient addresses and amounts.
const RPC_ENDPOINT = process.env.RPC_ENDPOINT || "https://devnet.helius-rpc.com/?api-key=YOUR_API_KEY"; // WHY: Read the RPC endpoint from environment variables so the API can target devnet, mainnet, or a custom Light Protocol node without code changes.
const rpc = createRpc(RPC_ENDPOINT); // WHY: Create the Light Protocol RPC client which handles compressed account indexing, validity proof generation, and transaction relay.
const payerSecretKey = Uint8Array.from(JSON.parse(process.env.PAYER_SECRET_KEY || "[]")); // WHY: Read the payer secret key from the environment as a JSON array of bytes so the server can sign compressed token transactions.
const payer = Keypair.fromSecretKey(payerSecretKey); // WHY: Reconstruct the payer Keypair from the secret key bytes so it can be used as signer and mint authority in Light Protocol instructions.
const MINT_PUBKEY = new PublicKey(process.env.COMPRESSED_MINT || "So11111111111111111111111111111111111111112"); // WHY: Parse the compressed token mint address from the environment so all API routes reference the same Merkle tree-backed token type.
app.post("/mint/compressed", async (req: Request, res: Response) => { // WHY: Define POST /mint/compressed so clients can create new compressed tokens and assign them to a recipient without standard SPL token accounts.
  try { // WHY: Wrap the handler in try/catch so RPC failures or invalid inputs return structured HTTP errors instead of crashing the server.
    const { recipientAddress, amount } = req.body; // WHY: Extract recipientAddress and amount from the request body so the caller controls who receives tokens and how many.
    const recipient = new PublicKey(recipientAddress); // WHY: Validate the recipient address by constructing a PublicKey so malformed base58 strings fail early with a clear error message.
    const mintAmount = BigInt(amount); // WHY: Parse the amount as BigInt because on-chain compressed token amounts use integer base units with no floating point representation.
    const signature = await CompressedTokenProgram.mintTo( // WHY: Call the Light Protocol SDK to mint compressed tokens directly into a Merkle tree leaf owned by the recipient.
      rpc, // WHY: Pass the RPC so the SDK can read the current Merkle root and submit the append instruction to the on-chain program.
      payer, // WHY: The payer signs the transaction and pays the small network fee for adding a compressed token leaf to the tree.
      MINT_PUBKEY, // WHY: Specify the compressed mint so the leaf is tagged with the correct token type and decimal metadata.
      recipient, // WHY: Embed the recipient's public key in the leaf as the owner, enabling them to spend it later with a ZK proof.
      payer.publicKey, // WHY: The mint authority must sign to prove it is authorized to inflate the compressed token supply.
      mintAmount // WHY: The integer amount in base units becomes the balance field of the newly created compressed token leaf.
    ); // WHY: Close the mintTo call so the SDK returns the transaction signature for the newly created leaf.
    return res.status(200).json({ success: true, signature, recipient: recipient.toBase58(), amount: amount.toString() }); // WHY: Return HTTP 200 with the transaction signature so the client can confirm the mint succeeded on a Solana explorer.
  } catch (err: any) { // WHY: Catch any thrown errors from invalid addresses, RPC failures, or insufficient balance so the server remains stable.
    console.error("Mint error:", err); // WHY: Log the full error server-side for debugging while returning only the message to the client to avoid information leakage.
    return res.status(400).json({ success: false, error: err.message || "Mint failed" }); // WHY: Return HTTP 400 because mint failures are usually caused by malformed addresses or insufficient payer balance.
  } // WHY: Close the catch block so the try/catch scope ends and the route handler is complete.
}); // WHY: Close the POST /mint/compressed route registration so Express knows the handler is fully defined.
app.post("/transfer/compressed", async (req: Request, res: Response) => { // WHY: Define POST /transfer/compressed so clients can move compressed tokens between owners using a ZK proof of leaf ownership.
  try { // WHY: Use try/catch to handle invalid pubkeys, insufficient compressed balance, or proof generation failures gracefully.
    const { senderAddress, recipientAddress, amount } = req.body; // WHY: Destructure senderAddress, recipientAddress, and amount from the body so the API knows which leaves to spend and where to route value.
    const sender = new PublicKey(senderAddress); // WHY: Validate the sender address by constructing a PublicKey to catch malformed inputs before querying compressed state.
    const recipient = new PublicKey(recipientAddress); // WHY: Validate the recipient address by constructing a PublicKey to ensure the destination is valid before creating the new leaf.
    const transferAmount = BigInt(amount); // WHY: Parse the transfer amount as BigInt to match the u64 on-chain representation and avoid JavaScript floating point precision errors.
    const senderAccounts = await rpc.getCompressedTokenAccountsByOwner(sender); // WHY: Query the Light Protocol indexer for the sender's compressed token accounts so we know which leaves are available to spend.
    const leafHashes = senderAccounts.items.map((item: any) => item.hash); // WHY: Map the sender's compressed account items to their leaf hashes because the ZK prover needs hashes to build a Merkle inclusion proof.
    const proof = await rpc.getValidityProof(leafHashes); // WHY: Request a validity proof from the Light Protocol RPC that proves the sender's leaves exist in the current Merkle tree root.
    const signature = await CompressedTokenProgram.transfer( // WHY: Call the SDK transfer method which creates a ZK-verified transaction consuming old leaves and appending new recipient leaves.
      rpc, // WHY: The RPC relays the proof and current Merkle tree context to the on-chain Light Protocol verifier program.
      payer, // WHY: The payer funds transaction fees; in production the sender would sign or a relayer would submit on their behalf.
      MINT_PUBKEY, // WHY: The mint determines which compressed token standard and Merkle tree to target for the spend logic.
      transferAmount, // WHY: The exact base-unit quantity to move from the sender's leaf to a new leaf owned by the recipient.
      recipient, // WHY: The recipient public key is written into the new leaf so only their private key can authorize future spends.
      proof // WHY: The ZK proof demonstrates the sender owns valid leaves without revealing the full leaf contents on-chain.
    ); // WHY: Close the transfer call so the SDK returns the transaction signature for the ZK-verified spend.
    return res.status(200).json({ success: true, signature, sender: sender.toBase58(), recipient: recipient.toBase58(), amount: amount.toString() }); // WHY: Return HTTP 200 with the signature so the client can verify the ZK transfer succeeded on-chain.
  } catch (err: any) { // WHY: Catch any thrown errors from invalid addresses, insufficient balance, or proof failures so the server remains stable.
    console.error("Transfer error:", err); // WHY: Log the error for operators while returning a safe message to prevent leaking sensitive server or RPC internals.
    return res.status(400).json({ success: false, error: err.message || "Transfer failed" }); // WHY: Return HTTP 400 because transfer failures are typically due to bad inputs or insufficient compressed balance.
  } // WHY: Close the catch block so the try/catch scope ends and the route handler is complete.
}); // WHY: Close the POST /transfer/compressed route registration so Express knows the handler is fully defined.
app.get("/balance/:address", async (req: Request, res: Response) => { // WHY: Define GET /balance/:address so clients can read compressed token balances from the Light Protocol indexer instead of standard SPL accounts.
  try { // WHY: Use try/catch so malformed addresses or indexer downtime result in a controlled HTTP error response.
    const { address } = req.params; // WHY: Extract the address route parameter so we can query the specific user's compressed token holdings.
    const owner = new PublicKey(address); // WHY: Validate and convert the address string to a PublicKey to catch invalid base58 inputs immediately.
    const accounts = await rpc.getCompressedTokenAccountsByOwner(owner); // WHY: Query the Light Protocol RPC indexer for all compressed token leaves owned by this public key.
    const totalBalance = accounts.items.reduce((sum: bigint, item: any) => sum + BigInt(item.parsed.amount), 0n); // WHY: Sum the balances of all returned compressed token items to compute the total spendable amount across multiple leaves.
    return res.status(200).json({ success: true, address: owner.toBase58(), totalBalance: totalBalance.toString(), accounts: accounts.items }); // WHY: Return HTTP 200 with the total balance and individual account details so clients can display holdings accurately.
  } catch (err: any) { // WHY: Catch any thrown errors from invalid addresses or indexer failures so the server remains stable.
    console.error("Balance error:", err); // WHY: Log indexer errors server-side so operators can diagnose RPC issues without exposing internal stack traces.
    return res.status(400).json({ success: false, error: err.message || "Balance lookup failed" }); // WHY: Return HTTP 400 because balance lookup failures are typically caused by malformed addresses.
  } // WHY: Close the catch block so the try/catch scope ends and the route handler is complete.
}); // WHY: Close the GET /balance/:address route registration so Express knows the handler is fully defined.
const PORT = 3072; // WHY: Use port 3072 to avoid conflicts with other Web3 course APIs that run on adjacent ports in the 3000-3020 range.
app.listen(PORT, () => { // WHY: Start the Express server so external clients can begin submitting compressed token mint, transfer, and balance requests.
  console.log(`Compressed Token API listening on port ${PORT}, RPC: ${RPC_ENDPOINT}`); // WHY: Log the startup message so operators know the API is ready and which RPC endpoint is active.
}); // WHY: Close the listen callback so the server initialization is complete.
