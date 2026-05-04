import express, { Request, Response } from "express";
import { Connection, Keypair, PublicKey } from "@solana/web3.js";
import { AnchorProvider, Program, Wallet } from "@coral-xyz/anchor";
import { createMint, getOrCreateAssociatedTokenAccount, mintTo } from "@solana/spl-token";

// Create the Express application to handle HTTP mint requests.
const app = express();
// Parse JSON bodies so clients can send metadata parameters in POST requests.
app.use(express.json());

// Use devnet for testing to avoid spending real SOL during development.
const SOLANA_RPC = process.env.SOLANA_RPC || "https://api.devnet.solana.com";
// Initialize a connection to the Solana cluster for sending transactions.
const connection = new Connection(SOLANA_RPC, "confirmed");

// Load the payer keypair from environment or generate a temporary one for dev.
const payerSecret = process.env.PAYER_SECRET_KEY;
let payer: Keypair;
if (payerSecret) {
  // Parse the secret key from base64 so we can sign transactions.
  payer = Keypair.fromSecretKey(Buffer.from(payerSecret, "base64"));
} else {
  // Generate a new keypair for local development when no secret is provided.
  payer = Keypair.generate();
}

// Build an Anchor provider using the payer wallet and connection.
const provider = new AnchorProvider(connection, new Wallet(payer), { commitment: "confirmed" });

// POST /mint — accepts name, symbol, and uri to create a new NFT.
app.post("/mint", async (req: Request, res: Response) => {
  try {
    // Destructure the request body to extract user-provided metadata fields.
    const { name, symbol, uri } = req.body;
    // Validate that the name is present because NFTs require a display name.
    if (!name || typeof name !== "string") {
      return res.status(400).json({ error: "name is required and must be a string" });
    }
    // Validate that the URI is present so wallets can fetch off-chain metadata.
    if (!uri || typeof uri !== "string") {
      return res.status(400).json({ error: "uri is required and must be a string" });
    }

    // Create a new mint with zero decimals because NFTs are indivisible tokens.
    const mint = await createMint(
      connection,         // Connection to the Solana network.
      payer,              // Fee payer for the transaction.
      payer.publicKey,    // Mint authority that can create tokens.
      payer.publicKey,    // Freeze authority to disable minting later.
      0                   // Decimals set to zero for non-fungible behavior.
    );

    // Derive or create an associated token account for the payer to receive the NFT.
    const tokenAccount = await getOrCreateAssociatedTokenAccount(
      connection,
      payer,
      mint,
      payer.publicKey
    );

    // Mint exactly one token to the token account, establishing unique ownership.
    await mintTo(
      connection,
      payer,
      mint,
      tokenAccount.address,
      payer.publicKey,
      1 // Amount must be 1 to enforce NFT scarcity.
    );

    // Return the mint and token account addresses so the client can verify ownership.
    return res.status(200).json({
      mint: mint.toBase58(),
      tokenAccount: tokenAccount.address.toBase58(),
      owner: payer.publicKey.toBase58(),
      metadata: { name, symbol, uri }
    });
  } catch (err: any) {
    // Log the error server-side for debugging and return a safe message to the client.
    console.error("Mint error:", err);
    return res.status(500).json({ error: err.message || "Minting failed" });
  }
});

// GET /nft/:mint — fetches the token account and balance for a given mint.
app.get("/nft/:mint", async (req: Request, res: Response) => {
  try {
    // Parse the mint address from the URL parameter to look up the NFT.
    const mint = new PublicKey(req.params.mint);
    // Derive the associated token account for the payer and this mint.
    const tokenAccount = await getOrCreateAssociatedTokenAccount(
      connection,
      payer,
      mint,
      payer.publicKey
    );
    // Return the balance and account info to verify ownership on-chain.
    return res.status(200).json({
      mint: mint.toBase58(),
      tokenAccount: tokenAccount.address.toBase58(),
      amount: tokenAccount.amount.toString()
    });
  } catch (err: any) {
    // Handle invalid public keys or network errors gracefully.
    console.error("Fetch error:", err);
    return res.status(500).json({ error: err.message || "Fetch failed" });
  }
});

// Start the server on port 3000 to listen for incoming mint and query requests.
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`NFT API listening on port ${PORT}`);
});
