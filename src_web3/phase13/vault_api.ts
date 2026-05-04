// Express API for interacting with the token vault program
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

// Initialize Express application for vault operations
const app = express();

// Enable JSON body parsing for reading request parameters
app.use(express.json());

// Connect to Solana devnet for vault interactions
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Program ID of the deployed vault program (replace after deployment)
const VAULT_PROGRAM_ID = new PublicKey(
  "Vault111111111111111111111111111111111111111"
);

// Helper to derive the vault state PDA from an authority public key
function getVaultStatePDA(authority: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("vault_state"), authority.toBuffer()],
    VAULT_PROGRAM_ID
  );
}

// Endpoint to initialize a new vault for a user
app.post("/vault/initialize", async (req: Request, res: Response) => {
  try {
    // Reconstruct the payer keypair from the request secret
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Parse the mint that this vault will accept
    const mint = new PublicKey(req.body.mint);

    // Derive the deterministic vault state PDA for this payer
    const [vaultPda, _bump] = getVaultStatePDA(payer.publicKey);

    // Build instruction data: tag 0 for Initialize, followed by 32-byte authority
    const instructionData = Buffer.alloc(33);
    instructionData.writeUInt8(0, 0);
    instructionData.set(payer.publicKey.toBuffer(), 1);

    // Construct the transaction instruction to initialize the vault
    const instruction = new TransactionInstruction({
      keys: [
        // Payer funds and signs the vault creation
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        // Vault state PDA is created and owned by the vault program
        { pubkey: vaultPda, isSigner: false, isWritable: true },
        // Mint account defines the token type for this vault
        { pubkey: mint, isSigner: false, isWritable: false },
        // Rent sysvar provides rent exemption requirements
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // System program creates the vault state account
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: VAULT_PROGRAM_ID,
      data: instructionData,
    });

    // Send the transaction to create the vault on-chain
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the transaction signature and vault PDA to the client
    res.json({ success: true, signature, vaultPda: vaultPda.toBase58() });
  } catch (error) {
    // Log and report initialization errors
    console.error("Vault initialization failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to deposit tokens into an existing vault
app.post("/vault/deposit", async (req: Request, res: Response) => {
  try {
    // Reconstruct the depositor keypair from the request
    const depositorSecret = Uint8Array.from(req.body.depositorSecret);
    const depositor = Keypair.fromSecretKey(depositorSecret);

    // Parse mint and amount from the request
    const mint = new PublicKey(req.body.mint);
    const amount = req.body.amount as number;

    // Derive the vault state PDA using the depositor as authority
    const [vaultPda, _bump] = getVaultStatePDA(depositor.publicKey);

    // Derive the depositor's ATA for the specified mint
    const depositorAta = getAssociatedTokenAddressSync(mint, depositor.publicKey);

    // Derive the vault's ATA that will hold the deposited tokens
    const vaultAta = getAssociatedTokenAddressSync(mint, vaultPda, true);

    // Build a transaction to create the vault ATA if it does not exist
    const tx = new Transaction();

    // Check if the vault ATA exists; if not, add a creation instruction
    const vaultAtaInfo = await connection.getAccountInfo(vaultAta);
    if (!vaultAtaInfo) {
      tx.add(
        createAssociatedTokenAccountInstruction(
          depositor.publicKey, // Payer
          vaultAta,            // ATA to create
          vaultPda,            // Owner of the ATA
          mint                 // Mint
        )
      );
    }

    // Build instruction data: tag 1 for Deposit, followed by 8-byte amount
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(1, 0);
    instructionData.writeBigUInt64LE(BigInt(amount), 1);

    // Add the deposit instruction to the transaction
    tx.add(
      new TransactionInstruction({
        keys: [
          // Depositor signs to move their tokens
          { pubkey: depositor.publicKey, isSigner: true, isWritable: true },
          // Vault state account tracks the deposit total
          { pubkey: vaultPda, isSigner: false, isWritable: true },
          // Depositor's ATA is the source of tokens
          { pubkey: depositorAta, isSigner: false, isWritable: true },
          // Vault's ATA is the destination
          { pubkey: vaultAta, isSigner: false, isWritable: true },
          // SPL Token program processes the transfer
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ],
        programId: VAULT_PROGRAM_ID,
        data: instructionData,
      })
    );

    // Send and confirm the deposit transaction
    const signature = await sendAndConfirmTransaction(connection, tx, [depositor]);

    // Return the confirmation and addresses to the client
    res.json({
      success: true,
      signature,
      vaultPda: vaultPda.toBase58(),
      vaultAta: vaultAta.toBase58(),
    });
  } catch (error) {
    // Handle and report deposit errors
    console.error("Vault deposit failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to withdraw tokens from a vault
app.post("/vault/withdraw", async (req: Request, res: Response) => {
  try {
    // Reconstruct the authority keypair who controls the vault
    const authoritySecret = Uint8Array.from(req.body.authoritySecret);
    const authority = Keypair.fromSecretKey(authoritySecret);

    // Parse mint and withdrawal amount from request
    const mint = new PublicKey(req.body.mint);
    const amount = req.body.amount as number;

    // Derive the vault state PDA from the authority
    const [vaultPda, _bump] = getVaultStatePDA(authority.publicKey);

    // Derive the vault's ATA that holds the tokens
    const vaultAta = getAssociatedTokenAddressSync(mint, vaultPda, true);

    // Derive the recipient's ATA that will receive the withdrawn tokens
    const recipientAta = getAssociatedTokenAddressSync(mint, authority.publicKey);

    // Build instruction data: tag 2 for Withdraw, followed by 8-byte amount
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(2, 0);
    instructionData.writeBigUInt64LE(BigInt(amount), 1);

    // Construct the withdraw instruction
    const instruction = new TransactionInstruction({
      keys: [
        // Authority signs to authorize the withdrawal
        { pubkey: authority.publicKey, isSigner: true, isWritable: true },
        // Vault state account is read and updated
        { pubkey: vaultPda, isSigner: false, isWritable: true },
        // Vault ATA is the source of tokens
        { pubkey: vaultAta, isSigner: false, isWritable: true },
        // Recipient ATA receives the tokens
        { pubkey: recipientAta, isSigner: false, isWritable: true },
        // SPL Token program handles the transfer
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        // Clock sysvar provides the current time for unlock checks
        { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false },
      ],
      programId: VAULT_PROGRAM_ID,
      data: instructionData,
    });

    // Submit the withdrawal transaction
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      authority,
    ]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Report withdrawal errors such as time lock or insufficient balance
    console.error("Vault withdrawal failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to update the vault unlock time
app.post("/vault/set-unlock-time", async (req: Request, res: Response) => {
  try {
    // Reconstruct the authority keypair from the request
    const authoritySecret = Uint8Array.from(req.body.authoritySecret);
    const authority = Keypair.fromSecretKey(authoritySecret);

    // Parse the new unlock timestamp from the request
    const unlockTime = req.body.unlockTime as number;

    // Derive the vault state PDA from the authority
    const [vaultPda, _bump] = getVaultStatePDA(authority.publicKey);

    // Build instruction data: tag 3 for SetUnlockTime, followed by 8-byte i64
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(3, 0);
    instructionData.writeBigInt64LE(BigInt(unlockTime), 1);

    // Construct the instruction to update the unlock time
    const instruction = new TransactionInstruction({
      keys: [
        // Authority signs to authorize the configuration change
        { pubkey: authority.publicKey, isSigner: true, isWritable: false },
        // Vault state account is updated with the new unlock time
        { pubkey: vaultPda, isSigner: false, isWritable: true },
      ],
      programId: VAULT_PROGRAM_ID,
      data: instructionData,
    });

    // Submit the configuration update transaction
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      authority,
    ]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Log and report errors from unauthorized or invalid updates
    console.error("Set unlock time failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Start the Express server on port 3002 for vault API requests
app.listen(3002, () => {
  console.log("Vault API listening on port 3002");
});
