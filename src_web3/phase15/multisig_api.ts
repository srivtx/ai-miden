// Express API for interacting with the multisig program
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

// Initialize Express application for multisig operations
const app = express();

// Enable JSON body parsing to read request parameters
app.use(express.json());

// Connect to Solana devnet for multisig interactions
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// Program ID of the deployed multisig program (replace after deployment)
const MULTISIG_PROGRAM_ID = new PublicKey(
  "Multisig11111111111111111111111111111111111"
);

// Helper to derive the multisig PDA from a payer public key
function getMultisigPDA(payer: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("multisig"), payer.toBuffer()],
    MULTISIG_PROGRAM_ID
  );
}

// Helper to derive a proposal PDA from a multisig and a proposer
function getProposalPDA(multisig: PublicKey, proposer: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("proposal"), multisig.toBuffer(), proposer.toBuffer()],
    MULTISIG_PROGRAM_ID
  );
}

// Endpoint to create a new multisig config with a signer set and threshold
app.post("/multisig/create", async (req: Request, res: Response) => {
  try {
    // Reconstruct the payer keypair from the request secret
    const payerSecret = Uint8Array.from(req.body.payerSecret);
    const payer = Keypair.fromSecretKey(payerSecret);

    // Parse threshold and signer addresses from the request
    const threshold = req.body.threshold as number;
    const signerAddresses: string[] = req.body.signers;
    const signers = signerAddresses.map((s) => new PublicKey(s));

    // Derive the deterministic multisig PDA for this payer
    const [multisigPda, _bump] = getMultisigPDA(payer.publicKey);

    // Build instruction data: tag 0 for CreateMultisig
    // Layout: [tag: 1 byte] [threshold: 1 byte] [signer_count: 1 byte] [signers: 32 bytes each]
    const signerCount = signers.length;
    const instructionData = Buffer.alloc(3 + signerCount * 32);
    instructionData.writeUInt8(0, 0);
    instructionData.writeUInt8(threshold, 1);
    instructionData.writeUInt8(signerCount, 2);
    for (let i = 0; i < signerCount; i++) {
      instructionData.set(signers[i].toBuffer(), 3 + i * 32);
    }

    // Construct the transaction instruction to create the multisig
    const instruction = new TransactionInstruction({
      keys: [
        // Payer funds and signs the multisig creation
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        // Multisig config PDA stores the signer set and threshold
        { pubkey: multisigPda, isSigner: false, isWritable: true },
        // Rent sysvar provides rent exemption requirements
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // System program creates the multisig config account
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: MULTISIG_PROGRAM_ID,
      data: instructionData,
    });

    // Send the transaction to create the multisig on-chain
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      payer,
    ]);

    // Return the transaction signature and multisig PDA to the client
    res.json({ success: true, signature, multisigPda: multisigPda.toBase58() });
  } catch (error) {
    // Log and report initialization errors
    console.error("Multisig creation failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to create a new proposal for an existing multisig
app.post("/multisig/proposal", async (req: Request, res: Response) => {
  try {
    // Reconstruct the proposer keypair from the request secret
    const proposerSecret = Uint8Array.from(req.body.proposerSecret);
    const proposer = Keypair.fromSecretKey(proposerSecret);

    // Parse the multisig PDA from the request
    const multisigPda = new PublicKey(req.body.multisigPda);

    // Derive the deterministic proposal PDA for this multisig and proposer
    const [proposalPda, _bump] = getProposalPDA(multisigPda, proposer.publicKey);

    // Build instruction data: tag 1 for CreateProposal
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(1, 0);

    // Construct the transaction instruction to create the proposal
    const instruction = new TransactionInstruction({
      keys: [
        // Proposer funds and signs the proposal creation
        { pubkey: proposer.publicKey, isSigner: true, isWritable: true },
        // Proposal PDA will track approvals for this proposal
        { pubkey: proposalPda, isSigner: false, isWritable: true },
        // Multisig config links the proposal to its parent multisig
        { pubkey: multisigPda, isSigner: false, isWritable: false },
        // Rent sysvar provides rent exemption requirements
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        // System program creates the proposal account
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      programId: MULTISIG_PROGRAM_ID,
      data: instructionData,
    });

    // Send the transaction to create the proposal on-chain
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      proposer,
    ]);

    // Return the transaction signature and proposal PDA to the client
    res.json({
      success: true,
      signature,
      proposalPda: proposalPda.toBase58(),
    });
  } catch (error) {
    // Log and report proposal creation errors
    console.error("Proposal creation failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint for a signer to approve a proposal
app.post("/multisig/approve", async (req: Request, res: Response) => {
  try {
    // Reconstruct the signer's keypair from the request secret
    const signerSecret = Uint8Array.from(req.body.signerSecret);
    const signer = Keypair.fromSecretKey(signerSecret);

    // Parse the proposal and multisig PDAs from the request
    const proposalPda = new PublicKey(req.body.proposalPda);
    const multisigPda = new PublicKey(req.body.multisigPda);

    // Build instruction data: tag 2 for Approve
    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(2, 0);

    // Construct the transaction instruction to record the approval
    const instruction = new TransactionInstruction({
      keys: [
        // Signer must sign to prove they approve the proposal
        { pubkey: signer.publicKey, isSigner: true, isWritable: false },
        // Proposal PDA is updated with the new approval
        { pubkey: proposalPda, isSigner: false, isWritable: true },
        // Multisig config provides the signer set for validation
        { pubkey: multisigPda, isSigner: false, isWritable: false },
      ],
      programId: MULTISIG_PROGRAM_ID,
      data: instructionData,
    });

    // Send the transaction to record the approval on-chain
    const transaction = new Transaction().add(instruction);
    const signature = await sendAndConfirmTransaction(connection, transaction, [
      signer,
    ]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Log and report approval errors such as unauthorized signer
    console.error("Approval failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Endpoint to execute a proposal if the threshold is met
app.post("/multisig/execute", async (req: Request, res: Response) => {
  try {
    // Reconstruct the executor keypair from the request secret
    const executorSecret = Uint8Array.from(req.body.executorSecret);
    const executor = Keypair.fromSecretKey(executorSecret);

    // Parse proposal, multisig, mint, and recipient from the request
    const proposalPda = new PublicKey(req.body.proposalPda);
    const multisigPda = new PublicKey(req.body.multisigPda);
    const mint = new PublicKey(req.body.mint);
    const recipient = new PublicKey(req.body.recipient);
    const amount = req.body.amount as number;

    // Derive the multisig treasury ATA that holds the funds
    const treasuryAta = getAssociatedTokenAddressSync(mint, multisigPda, true);

    // Derive the recipient's ATA for the specified mint
    const recipientAta = getAssociatedTokenAddressSync(mint, recipient);

    // Build a transaction that may create the recipient ATA and executes the proposal
    const tx = new Transaction();

    // Check if recipient ATA exists; if not, add creation instruction
    const recipientAtaInfo = await connection.getAccountInfo(recipientAta);
    if (!recipientAtaInfo) {
      tx.add(
        createAssociatedTokenAccountInstruction(
          executor.publicKey, // Payer
          recipientAta,       // ATA to create
          recipient,          // Owner
          mint                // Mint
        )
      );
    }

    // Build instruction data: tag 3 for Execute, followed by 8-byte amount
    const instructionData = Buffer.alloc(9);
    instructionData.writeUInt8(3, 0);
    instructionData.writeBigUInt64LE(BigInt(amount), 1);

    // Add the execute instruction
    tx.add(
      new TransactionInstruction({
        keys: [
          // Executor signs to trigger execution
          { pubkey: executor.publicKey, isSigner: true, isWritable: true },
          // Proposal PDA is checked and marked executed
          { pubkey: proposalPda, isSigner: false, isWritable: true },
          // Multisig config provides threshold for validation
          { pubkey: multisigPda, isSigner: false, isWritable: false },
          // Treasury ATA is the source of the transfer
          { pubkey: treasuryAta, isSigner: false, isWritable: true },
          // Recipient ATA receives the transferred tokens
          { pubkey: recipientAta, isSigner: false, isWritable: true },
          // SPL Token program processes the transfer CPI
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ],
        programId: MULTISIG_PROGRAM_ID,
        data: instructionData,
      })
    );

    // Send and confirm the execution transaction
    const signature = await sendAndConfirmTransaction(connection, tx, [executor]);

    // Return the confirmation to the client
    res.json({ success: true, signature });
  } catch (error) {
    // Report execution errors such as threshold not met or already executed
    console.error("Execution failed:", error);
    res.status(500).json({ success: false, error: String(error) });
  }
});

// Start the Express server on port 3004 for multisig API requests
app.listen(3004, () => {
  console.log("Multisig API listening on port 3004");
});
