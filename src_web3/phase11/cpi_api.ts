// Express API that demonstrates constructing and sending CPI-based transactions
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

// Initialize Express application for serving CPI demo endpoints
const app = express();

// Parse JSON bodies so we can read instruction parameters from requests
app.use(express.json());

// Connection to the Solana devnet cluster for testing
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Program ID of the deployed CPI demo program (replace with actual deployment)
const CPI_PROGRAM_ID = new PublicKey(
  "CpiDemo111111111111111111111111111111111111"
);

// Endpoint to execute a simple CPI transfer instruction
app.post("/cpi/simple-transfer", async (req: Request, res: Response) => {
  try {
    // Extract the payer secret key from request so we can sign transactions
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Extract the recipient public key and transfer amount from request body
    const recipient = new PublicKey(req.body.recipient);
    const amount = req.body.amount as number;

    // Build instruction data: first byte 0 selects SimpleCpiTransfer variant
    // Next 8 bytes encode the amount as a little-endian u64
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(0, 0); // Variant tag 0
    instructionData.writeBigUInt64LE(BigInt(amount), 1); // Amount as u64

    // Construct the transaction instruction targeting our CPI demo program
    const instruction = new TransactionInstruction({
      keys: [
        // Wallet account is a signer and writable because it pays and authorizes
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        // System program is not a signer but is needed for the CPI transfer
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // Recipient account is writable because it receives lamports
        { pubkey: recipient, isSigner: false, isWritable: true },
      ],
      programId: CPI_PROGRAM_ID, // Must match the deployed program address
      data: instructionData,     // Serialized instruction parameters
    });

    // Create a new transaction and add the CPI instruction to it
    const transaction = new Transaction().add(instruction);

    // Send and confirm the transaction using the payer's signature
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the transaction signature so the client can track it on-chain
    res.json({ success: true, signature });
  } catch (error) {
    // Log the error and return a 500 response with details
    console.error("Simple CPI transfer failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to execute a signed CPI transfer where the program signs for a PDA
app.post("/cpi/signed-transfer", async (req: Request, res: Response) => {
  try {
    // Reconstruct the payer keypair from the secret key in the request
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Derive the PDA that the program will sign for using the same seeds as on-chain
    const seeds = [Buffer.from("escrow"), Buffer.from("demo")];
    const [pda] = PublicKey.findProgramAddressSync(seeds, CPI_PROGRAM_ID);

    // Extract recipient and amount from the request body
    const recipient = new PublicKey(req.body.recipient);
    const amount = req.body.amount as number;

    // Build instruction data: first byte 1 selects SignedCpiTransfer variant
    // Next 8 bytes encode the amount as a little-endian u64
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(1, 0); // Variant tag 1
    instructionData.writeBigUInt64LE(BigInt(amount), 1); // Amount as u64

    // Construct the instruction with the PDA as the source account
    const instruction = new TransactionInstruction({
      keys: [
        // PDA is the source of lamports and must be writable
        { pubkey: pda, isSigner: false, isWritable: true },
        // Recipient receives lamports and must be writable
        { pubkey: recipient, isSigner: false, isWritable: true },
        // System program is required for the transfer CPI inside the program
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: CPI_PROGRAM_ID, // Target the CPI demo program
      data: instructionData,     // Serialized parameters
    });

    // Assemble the transaction containing the signed CPI instruction
    const transaction = new Transaction().add(instruction);

    // Submit the transaction to the cluster and wait for confirmation
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the confirmed transaction signature to the caller
    res.json({ success: true, signature, pda: pda.toBase58() });
  } catch (error) {
    // Handle and report any errors during transaction processing
    console.error("Signed CPI transfer failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Start the Express server on port 3000 to accept CPI demo requests
app.listen(3000, () => {
  console.log("CPI API listening on port 3000");
});
