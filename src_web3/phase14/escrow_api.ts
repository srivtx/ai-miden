// Express API for interacting with the escrow program
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
  TOKEN_PROGRAM_ID,
  getAssociatedTokenAddressSync,
  createAssociatedTokenAccountInstruction,
} from "@solana/spl-token";

// Initialize Express application for escrow operations
const app = express();

// Enable JSON body parsing to read request parameters
app.use(express.json());

// Connect to Solana devnet for escrow interactions
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Program ID of the deployed escrow program (replace after deployment)
const ESCROW_PROGRAM_ID = new PublicKey(
  "Escrow11111111111111111111111111111111111111"
);

// Helper to derive the escrow PDA from party A and party B public keys
function getEscrowPDA(partyA: PublicKey, partyB: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("escrow"), partyA.toBuffer(), partyB.toBuffer()],
    ESCROW_PROGRAM_ID
  );
}

// Endpoint to initialize a new escrow between two parties
app.post("/escrow/initialize", async (req: Request, res: Response) => {
  try {
    // Reconstruct the payer keypair from the request secret
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Parse party addresses, mints, amounts, and expiry from the request
    const partyA = new PublicKey(req.body.partyA);
    const partyB = new PublicKey(req.body.partyB);
    const mintA = new PublicKey(req.body.mintA);
    const mintB = new PublicKey(req.body.mintB);
    const amountA = req.body.amountA as number;
    const amountB = req.body.amountB as number;
    const expiry = req.body.expiry as number;

    // Derive the deterministic escrow PDA for these two parties
    const [escrowPda, _bump] = getEscrowPDA(partyA, partyB);

    // Build instruction data: tag 0 for Initialize, then 8+8+8 bytes
    const instructionData = Buffer.alloc(25);
    instructionData.writeUInt8(0, 0);
    instructionData.writeBigUInt64LE(BigInt(amountA), 1);
    instructionData.writeBigUInt64LE(BigInt(amountB), 9);
    instructionData.writeBigInt64LE(BigInt(expiry), 17);

    // Construct the transaction instruction to initialize the escrow
    const instruction = new TransactionInstruction({
      keys: [
        // Payer funds and signs the escrow creation
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        // Escrow state PDA will store the trade terms
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        // Party A is recorded as the first counterparty
        { pubkey: partyA, isSigner: false, isWritable: false },
        // Party B is recorded as the second counterparty
        { pubkey: partyB, isSigner: false, isWritable: false },
        // Mint A defines the token type for party A's deposit
        { pubkey: mintA, isSigner: false, isWritable: false },
        // Mint B defines the token type for party B's deposit
        { pubkey: mintB, isSigner: false, isWritable: false },
        // Rent sysvar provides rent exemption requirements
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // System program creates the escrow state account
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: ESCROW_PROGRAM_ID,
      data: instructionData,
    });

    // Send the transaction to create the escrow on-chain
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the transaction signature and escrow PDA to the client
    res.json({ success: true, signature, escrowPda: escrowPda.toBase58() });
  } catch (error) {
    // Log and report initialization errors
    console.error("Escrow initialization failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint for party A to deposit tokens into the escrow
app.post("/escrow/deposit-a", async (req: Request, res: Response) => {
  try {
    // Reconstruct party A's keypair from the request secret
    const partyASecret = Uint8Array.from(req.body.partyASecret);
    const partyA = Keypair.fromSecretKey(partyASecret);

    // Parse party B address and mint from the request
    const partyB = new PublicKey(req.body.partyB);
    const mintA = new PublicKey(req.body.mintA);

    // Derive the escrow PDA using party A and party B
    const [escrowPda, _bump] = getEscrowPDA(partyA.publicKey, partyB);

    // Derive party A's ATA for token A
    const partyAAta = getAssociatedTokenAddressSync(mintA, partyA.publicKey);

    // Derive the escrow's ATA for token A, owned by the escrow PDA
    const escrowAtaA = getAssociatedTokenAddressSync(mintA, escrowPda, true);

    // Build a transaction that creates the escrow ATA if needed and deposits
    const tx = new Transaction();

    // Check if escrow ATA exists; if not, add creation instruction
    const escrowAtaInfo = await connection.getAccountInfo(escrowAtaA);
    if (!escrowAtaInfo) {
      tx.add(
        createAssociatedTokenAccountInstruction(
          partyA.publicKey, // Payer
          escrowAtaA,       // ATA to create
          escrowPda,        // Owner
          mintA             // Mint
        )
      );
    }

    // Build instruction data: tag 1 for DepositA
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(1, 0);

    // Add the deposit instruction
    tx.add(
      new TransactionInstruction({
        keys: [
          // Party A signs to move their tokens
          { pubkey: partyA.publicKey, isSigner: true, isWritable: true },
          // Escrow state is updated with the deposit
          { pubkey: escrowPda, isSigner: false, isWritable: true },
          // Party A's ATA is the source of the deposit
          { pubkey: partyAAta, isSigner: false, isWritable: true },
          // Escrow's ATA receives the deposited tokens
          { pubkey: escrowAtaA, isSigner: false, isWritable: true },
          // SPL Token program processes the transfer
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ],
        programId: ESCROW_PROGRAM_ID,
        data: instructionData,
      })
    );

    // Send and confirm the deposit transaction
    const signature = await sendAndConfirmTransaction(connection, tx, [partyA]);

    // Return confirmation and addresses to the client
    res.json({
      success: true,
      signature,
      escrowPda: escrowPda.toBase58(),
      escrowAtaA: escrowAtaA.toBase58(),
    });
  } catch (error) {
    // Handle and report deposit errors
    console.error("Escrow deposit A failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint for party B to deposit tokens into the escrow
app.post("/escrow/deposit-b", async (req: Request, res: Response) => {
  try {
    // Reconstruct party B's keypair from the request secret
    const partyBSecret = Uint8Array.from(req.body.partyBSecret);
    const partyB = Keypair.fromSecretKey(partyBSecret);

    // Parse party A address and mint from the request
    const partyA = new PublicKey(req.body.partyA);
    const mintB = new PublicKey(req.body.mintB);

    // Derive the escrow PDA using party A and party B
    const [escrowPda, _bump] = getEscrowPDA(partyA, partyB.publicKey);

    // Derive party B's ATA for token B
    const partyBAta = getAssociatedTokenAddressSync(mintB, partyB.publicKey);

    // Derive the escrow's ATA for token B, owned by the escrow PDA
    const escrowAtaB = getAssociatedTokenAddressSync(mintB, escrowPda, true);

    // Build a transaction that creates the escrow ATA if needed and deposits
    const tx = new Transaction();

    // Check if escrow ATA exists; if not, add creation instruction
    const escrowAtaInfo = await connection.getAccountInfo(escrowAtaB);
    if (!escrowAtaInfo) {
      tx.add(
        createAssociatedTokenAccountInstruction(
          partyB.publicKey, // Payer
          escrowAtaB,       // ATA to create
          escrowPda,        // Owner
          mintB             // Mint
        )
      );
    }

    // Build instruction data: tag 2 for DepositB
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(2, 0);

    // Add the deposit instruction
    tx.add(
      new TransactionInstruction({
        keys: [
          // Party B signs to move their tokens
          { pubkey: partyB.publicKey, isSigner: true, isWritable: true },
          // Escrow state is updated with the deposit
          { pubkey: escrowPda, isSigner: false, isWritable: true },
          // Party B's ATA is the source of the deposit
          { pubkey: partyBAta, isSigner: false, isWritable: true },
          // Escrow's ATA receives the deposited tokens
          { pubkey: escrowAtaB, isSigner: false, isWritable: true },
          // SPL Token program processes the transfer
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ],
        programId: ESCROW_PROGRAM_ID,
        data: instructionData,
      })
    );

    // Send and confirm the deposit transaction
    const signature = await sendAndConfirmTransaction(connection, tx, [partyB]);

    // Return confirmation and addresses to the client
    res.json({
      success: true,
      signature,
      escrowPda: escrowPda.toBase58(),
      escrowAtaB: escrowAtaB.toBase58(),
    });
  } catch (error) {
    // Handle and report deposit errors
    console.error("Escrow deposit B failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to release tokens to both parties after both have deposited
app.post("/escrow/release", async (req: Request, res: Response) => {
  try {
    // Reconstruct the signer's keypair from the request secret
    const signerSecret = Uint8Array.from(req.body.signerSecret);
    const signer = Keypair.fromSecretKey(signerSecret);

    // Parse party addresses and mints from the request
    const partyA = new PublicKey(req.body.partyA);
    const partyB = new PublicKey(req.body.partyB);
    const mintA = new PublicKey(req.body.mintA);
    const mintB = new PublicKey(req.body.mintB);

    // Derive the escrow PDA
    const [escrowPda, _bump] = getEscrowPDA(partyA, partyB);

    // Derive token accounts for both parties and the escrow
    const escrowAtaA = getAssociatedTokenAddressSync(mintA, escrowPda, true);
    const escrowAtaB = getAssociatedTokenAddressSync(mintB, escrowPda, true);
    const partyAAta = getAssociatedTokenAddressSync(mintB, partyA);
    const partyBAta = getAssociatedTokenAddressSync(mintA, partyB);

    // Build instruction data: tag 3 for Release
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(3, 0);

    // Construct the release instruction
    const instruction = new TransactionInstruction({
      keys: [
        // Signer authorizes the release instruction
        { pubkey: signer.publicKey, isSigner: true, isWritable: true },
        // Escrow state is updated to closed
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        // Escrow ATA A is the source for party B's receipt
        { pubkey: escrowAtaA, isSigner: false, isWritable: true },
        // Escrow ATA B is the source for party A's receipt
        { pubkey: escrowAtaB, isSigner: false, isWritable: true },
        // Party A receives token B
        { pubkey: partyAAta, isSigner: false, isWritable: true },
        // Party B receives token A
        { pubkey: partyBAta, isSigner: false, isWritable: true },
        // SPL Token program processes both transfers
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: ESCROW_PROGRAM_ID,
      data: instructionData,
    });

    // Submit the release transaction
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      signer,
    ]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Report release errors such as missing deposits
    console.error("Escrow release failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to cancel the escrow and return funds after expiry
app.post("/escrow/cancel", async (req: Request, res: Response) => {
  try {
    // Reconstruct the signer's keypair from the request secret
    const signerSecret = Uint8Array.from(req.body.signerSecret);
    const signer = Keypair.fromSecretKey(signerSecret);

    // Parse party addresses and mints from the request
    const partyA = new PublicKey(req.body.partyA);
    const partyB = new PublicKey(req.body.partyB);
    const mintA = new PublicKey(req.body.mintA);
    const mintB = new PublicKey(req.body.mintB);

    // Derive the escrow PDA
    const [escrowPda, _bump] = getEscrowPDA(partyA, partyB);

    // Derive token accounts for returns
    const escrowAtaA = getAssociatedTokenAddressSync(mintA, escrowPda, true);
    const escrowAtaB = getAssociatedTokenAddressSync(mintB, escrowPda, true);
    const partyAAta = getAssociatedTokenAddressSync(mintA, partyA);
    const partyBAta = getAssociatedTokenAddressSync(mintB, partyB);

    // Build instruction data: tag 4 for Cancel
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(4, 0);

    // Construct the cancel instruction
    const instruction = new TransactionInstruction({
      keys: [
        // Signer authorizes the cancellation
        { pubkey: signer.publicKey, isSigner: true, isWritable: true },
        // Escrow state is updated to closed
        { pubkey: escrowPda, isSigner: false, isWritable: true },
        // Escrow ATA A returns tokens to party A
        { pubkey: escrowAtaA, isSigner: false, isWritable: true },
        // Escrow ATA B returns tokens to party B
        { pubkey: escrowAtaB, isSigner: false, isWritable: true },
        // Party A receives returned token A
        { pubkey: partyAAta, isSigner: false, isWritable: true },
        // Party B receives returned token B
        { pubkey: partyBAta, isSigner: false, isWritable: true },
        // SPL Token program processes returns
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        // Clock sysvar enforces the expiry time
        { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false },
      ],
      programId: ESCROW_PROGRAM_ID,
      data: instructionData,
    });

    // Submit the cancellation transaction
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      signer,
    ]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Report cancellation errors such as early cancellation attempt
    console.error("Escrow cancel failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Start the Express server on port 3003 for escrow API requests
app.listen(3003, () => {
  console.log("Escrow API listening on port 3003");
});
