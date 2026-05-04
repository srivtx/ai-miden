// Express API that exposes SPL Token operations via HTTP endpoints
import express, { Request, Response } from "express";
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  SystemProgram,
} from "@solana/web3.js";
import {
  ASSOCIATED_TOKEN_PROGRAM_ID,
  TOKEN_PROGRAM_ID,
  createAssociatedTokenAccountInstruction,
  createMintToInstruction,
  createTransferInstruction,
  getAssociatedTokenAddressSync,
  getMint,
  getAccount,
} from "@solana/spl-token";

// Initialize Express application for token management endpoints
const app = express();

// Enable JSON body parsing so clients can send parameters in requests
app.use(express.json());

// Establish a connection to Solana devnet for all token operations
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Program ID of the deployed SPL token demo program (replace after deploy)
const TOKEN_PROGRAM_DEMO_ID = new PublicKey(
  "TokenDemo1111111111111111111111111111111111"
);

// Endpoint to create a new SPL token Mint
app.post("/token/create-mint", async (req: Request, res: Response) => {
  try {
    // Reconstruct the payer keypair from the secret key bytes in the request
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Generate a new keypair for the Mint account; it must be uninitialized
    const mintKeypair = Keypair.generate();

    // Build instruction data with variant tag 0 for CreateMint
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(0, 0);

    // Construct the transaction instruction targeting our demo program
    const instruction = new TransactionInstruction({
      keys: [
        // Payer funds the account creation and signs
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        // Mint account is created and initialized
        { pubkey: mintKeypair.publicKey, isSigner: true, isWritable: true },
        // Rent sysvar provides rent exemption requirements
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // SPL Token program processes the mint initialization
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: TOKEN_PROGRAM_DEMO_ID,
      data: instructionData,
    });

    // Send the transaction with both payer and mint keypair signatures
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
      mintKeypair,
    ]);

    // Return the transaction signature and the new mint address to the client
    res.json({
      success: true,
      signature,
      mintAddress: mintKeypair.publicKey.toBase58(),
    });
  } catch (error) {
    // Report any errors encountered during mint creation
    console.error("Create mint failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to create an Associated Token Account for a wallet and mint
app.post("/token/create-ata", async (req: Request, res: Response) => {
  try {
    // Reconstruct payer keypair to fund potential account creation
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Parse wallet and mint addresses from the request body
    const wallet = new PublicKey(req.body.wallet);
    const mint = new PublicKey(req.body.mint);

    // Derive the deterministic ATA address so we know where tokens will go
    const ata = getAssociatedTokenAddressSync(mint, wallet);

    // Build the ATA creation instruction using the SPL helper
    const instruction = createAssociatedTokenAccountInstruction(
      payer.publicKey, // Payer funds the account
      ata,             // Address of the ATA to create
      wallet,          // Owner of the ATA
      mint             // Mint associated with this ATA
    );

    // Submit the transaction to create the ATA
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the ATA address and confirmation signature
    res.json({ success: true, signature, ata: ata.toBase58() });
  } catch (error) {
    // Handle and report errors during ATA creation
    console.error("Create ATA failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to mint tokens into a destination token account
app.post("/token/mint", async (req: Request, res: Response) => {
  try {
    // Reconstruct the mint authority keypair from the request
    const authoritySecret = Uint8Array.from(req.body.authoritySecret);
    const authority = Keypair.fromSecretKey(authoritySecret);

    // Parse the target mint and destination token account from the request
    const mint = new PublicKey(req.body.mint);
    const destination = new PublicKey(req.body.destination);
    const amount = BigInt(req.body.amount);

    // Build a MintTo instruction using the SPL Token helper
    const instruction = createMintToInstruction(
      mint,              // Mint whose supply increases
      destination,       // Token account receiving the new tokens
      authority.publicKey, // Mint authority must sign
      amount             // Number of tokens to mint
    );

    // Submit the minting transaction with the authority signature
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      authority,
    ]);

    // Confirm the mint operation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Log and return any minting errors
    console.error("Mint tokens failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to query the balance of a token account
app.get("/token/balance", async (req: Request, res: Response) => {
  try {
    // Parse the token account address from query parameters
    const tokenAccount = new PublicKey(req.query.account as string);

    // Fetch the on-chain token account info using SPL helper
    const accountInfo = await getAccount(connection, tokenAccount);

    // Fetch the mint info to convert raw balance to human-readable units
    const mintInfo = await getMint(connection, accountInfo.mint);

    // Return the raw balance, mint address, owner, and decimal-adjusted amount
    res.json({
      success: true,
      address: tokenAccount.toBase58(),
      mint: accountInfo.mint.toBase58(),
      owner: accountInfo.owner.toBase58(),
      balance: accountInfo.amount.toString(),
      decimals: mintInfo.decimals,
    });
  } catch (error) {
    // Report errors when the account does not exist or is invalid
    console.error("Get balance failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to transfer SPL tokens between token accounts
app.post("/token/transfer", async (req: Request, res: Response) => {
  try {
    // Reconstruct the source owner keypair who authorizes the transfer
    const senderSecret = Uint8Array.from(req.body.senderSecret);
    const sender = Keypair.fromSecretKey(senderSecret);

    // Parse source, destination, mint, and amount from the request
    const source = new PublicKey(req.body.source);
    const destination = new PublicKey(req.body.destination);
    const mint = new PublicKey(req.body.mint);
    const amount = BigInt(req.body.amount);

    // Build a Transfer instruction using the SPL Token helper
    const instruction = createTransferInstruction(
      source,              // Source token account
      destination,         // Destination token account
      sender.publicKey,    // Owner of the source account
      amount               // Amount to transfer in base units
    );

    // Submit the transfer transaction signed by the sender
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      sender,
    ]);

    // Return the confirmed signature to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Handle and report transfer errors such as insufficient balance
    console.error("Transfer failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Start the Express server on port 3001 for token API requests
app.listen(3001, () => {
  console.log("Token API listening on port 3001");
});
