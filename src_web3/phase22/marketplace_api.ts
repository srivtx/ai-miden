import express, { Request, Response } from "express";
import { Connection, Keypair, PublicKey, Transaction } from "@solana/web3.js";
import { AnchorProvider, Program, Wallet, BN } from "@coral-xyz/anchor";
import { getOrCreateAssociatedTokenAccount, getAssociatedTokenAddress } from "@solana/spl-token";

// Create the Express application for marketplace HTTP endpoints.
const app = express();
// Parse JSON bodies so clients can send listing and purchase parameters.
app.use(express.json());

// Use devnet for development to avoid spending real SOL.
const SOLANA_RPC = process.env.SOLANA_RPC || "https://api.devnet.solana.com";
// Establish a connection to the Solana cluster for transaction submission.
const connection = new Connection(SOLANA_RPC, "confirmed");

// Load the payer keypair from environment or generate one for local testing.
const payerSecret = process.env.PAYER_SECRET_KEY;
let payer: Keypair;
if (payerSecret) {
  // Decode the base64 secret key to create a signable keypair.
  payer = Keypair.fromSecretKey(Buffer.from(payerSecret, "base64"));
} else {
  // Generate a temporary keypair when no secret is configured.
  payer = Keypair.generate();
}

// Build an Anchor provider so the program client can sign and send transactions.
const provider = new AnchorProvider(connection, new Wallet(payer), { commitment: "confirmed" });

// POST /list — accepts a mint and price to create a marketplace listing.
app.post("/list", async (req: Request, res: Response) => {
  try {
    // Extract the NFT mint address and desired price from the request body.
    const { mint, price } = req.body;
    // Validate that the mint address is provided so we know which NFT to list.
    if (!mint) {
      return res.status(400).json({ error: "mint is required" });
    }
    // Validate that the price is a positive number to prevent invalid listings.
    if (!price || Number(price) <= 0) {
      return res.status(400).json({ error: "price must be greater than zero" });
    }

    // Convert the string mint address into a Solana PublicKey.
    const mintPubkey = new PublicKey(mint);
    // Derive the seller's associated token account for this specific mint.
    const sellerTokenAccount = await getAssociatedTokenAddress(mintPubkey, payer.publicKey);

    // Simulate returning the transaction data the client would sign and submit.
    // In a real deployment, the API would build the Anchor transaction and return it partially signed.
    return res.status(200).json({
      instruction: "list",
      mint: mintPubkey.toBase58(),
      seller: payer.publicKey.toBase58(),
      sellerTokenAccount: sellerTokenAccount.toBase58(),
      price: Number(price),
      message: "Transaction prepared. Sign and submit via Anchor client."
    });
  } catch (err: any) {
    // Log server-side details and return a safe error message to the caller.
    console.error("List error:", err);
    return res.status(500).json({ error: err.message || "Listing failed" });
  }
});

// POST /buy — accepts a mint to execute a purchase against an active listing.
app.post("/buy", async (req: Request, res: Response) => {
  try {
    // Extract the NFT mint address the buyer wants to purchase.
    const { mint } = req.body;
    // Validate that the mint is provided so we can locate the listing.
    if (!mint) {
      return res.status(400).json({ error: "mint is required" });
    }

    // Convert the string mint address into a Solana PublicKey.
    const mintPubkey = new PublicKey(mint);
    // Derive the buyer's associated token account to receive the NFT.
    const buyerTokenAccount = await getOrCreateAssociatedTokenAccount(
      connection,
      payer,
      mintPubkey,
      payer.publicKey
    );

    // Simulate returning the purchase transaction data for client signing.
    return res.status(200).json({
      instruction: "buy",
      mint: mintPubkey.toBase58(),
      buyer: payer.publicKey.toBase58(),
      buyerTokenAccount: buyerTokenAccount.address.toBase58(),
      message: "Transaction prepared. Sign and submit via Anchor client."
    });
  } catch (err: any) {
    // Log the error for debugging and return a concise failure message.
    console.error("Buy error:", err);
    return res.status(500).json({ error: err.message || "Purchase failed" });
  }
});

// POST /cancel — accepts a mint to withdraw an NFT from an active listing.
app.post("/cancel", async (req: Request, res: Response) => {
  try {
    // Extract the NFT mint address for the listing to cancel.
    const { mint } = req.body;
    // Validate that the mint is provided so we know which listing to cancel.
    if (!mint) {
      return res.status(400).json({ error: "mint is required" });
    }

    // Convert the string mint address into a Solana PublicKey.
    const mintPubkey = new PublicKey(mint);
    // Derive the seller's associated token account to receive the returned NFT.
    const sellerTokenAccount = await getAssociatedTokenAddress(mintPubkey, payer.publicKey);

    // Simulate returning the cancel transaction data for client signing.
    return res.status(200).json({
      instruction: "cancel",
      mint: mintPubkey.toBase58(),
      seller: payer.publicKey.toBase58(),
      sellerTokenAccount: sellerTokenAccount.toBase58(),
      message: "Transaction prepared. Sign and submit via Anchor client."
    });
  } catch (err: any) {
    // Log the error for debugging and return a concise failure message.
    console.error("Cancel error:", err);
    return res.status(500).json({ error: err.message || "Cancel failed" });
  }
});

// Start the Express server to listen for marketplace API requests.
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Marketplace API listening on port ${PORT}`);
});
