import { Connection, Keypair, PublicKey } from "@solana/web3.js"; // WHY: Import Solana web3 for RPC polling and transaction building.
import { AnchorProvider, Program, Wallet, BN } from "@coral-xyz/anchor"; // WHY: Import Anchor to interact with the bridge program.
import { getAssociatedTokenAddressSync, TOKEN_PROGRAM_ID } from "@solana/spl-token"; // WHY: Import SPL helpers to derive token accounts.
import nacl from "tweetnacl"; // WHY: Import tweetnacl for real Ed25519 signing by guardian keys.
import { createHash } from "crypto"; // WHY: Import Node crypto to compute SHA-256 digests that match on-chain verification.
import fs from "fs"; // WHY: Import filesystem to load program IDLs and wallet files.
import path from "path"; // WHY: Import path for cross-platform file resolution.

const RPC_URL = process.env.SOLANA_RPC || "http://127.0.0.1:8899"; // WHY: Allow cluster override for devnet or mainnet-beta.
const connection = new Connection(RPC_URL, "confirmed"); // WHY: Connect with confirmed commitment so we observe finalized events.

const walletPath = process.env.WALLET || path.join(process.env.HOME || "", ".config/solana/id.json"); // WHY: Resolve the relayer wallet path.
const keypair = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(walletPath, "utf8")))); // WHY: Load the relayer keypair to sign and pay for transactions.
const wallet = new Wallet(keypair); // WHY: Wrap in Anchor Wallet.
const provider = new AnchorProvider(connection, wallet, { commitment: "confirmed" }); // WHY: Create provider for program interactions.

const bridgeIdlPath = path.join(__dirname, "bridge", "target", "idl", "bridge.json"); // WHY: Resolve bridge IDL.
const bridgeIdl = JSON.parse(fs.readFileSync(bridgeIdlPath, "utf8")); // WHY: Parse bridge IDL.
const bridgeProgramId = new PublicKey(bridgeIdl.address); // WHY: Extract program ID.
const bridgeProgram = new Program(bridgeIdl, bridgeProgramId, provider); // WHY: Create typed bridge program instance.

const guardianIdlPath = path.join(__dirname, "bridge", "target", "idl", "guardian.json"); // WHY: Resolve guardian IDL.
const guardianIdl = JSON.parse(fs.readFileSync(guardianIdlPath, "utf8")); // WHY: Parse guardian IDL.
const guardianProgramId = new PublicKey(guardianIdl.address); // WHY: Extract program ID.
const guardianProgram = new Program(guardianIdl, guardianProgramId, provider); // WHY: Create typed guardian program instance.

const GUARDIAN_SECRETS = (process.env.GUARDIAN_SECRETS || "").split(",").filter(Boolean); // WHY: Load guardian Ed25519 secret seeds from environment and ignore empty strings.
const guardianKeypairs = GUARDIAN_SECRETS.map((s) => nacl.sign.keyPair.fromSeed(Uint8Array.from(Buffer.from(s, "hex")))); // WHY: Convert each 32-byte hex seed into a tweetnacl keypair containing secret and public keys.

const getBridgeStatePDA = () => PublicKey.findProgramAddressSync([Buffer.from("bridge_state")], bridgeProgramId)[0]; // WHY: Derive bridge state PDA.
const getGuardianRegistryPDA = () => PublicKey.findProgramAddressSync([Buffer.from("guardian_registry")], guardianProgramId)[0]; // WHY: Derive guardian registry PDA.

const POLL_INTERVAL_MS = 5000; // WHY: Poll every 5 seconds to detect new lock events without overwhelming the RPC node.
let lastProcessedNonce = -1; // WHY: Track the highest nonce processed so each lock event is handled exactly once.

async function processLockEvent(nonce: number) { // WHY: Define the handler that constructs guardian signatures and submits the mint proof.
  try { // WHY: Catch errors so one failed event does not crash the relayer loop.
    const bridgeState = getBridgeStatePDA(); // WHY: Derive bridge state.
    const lockRecordSeed = new BN(nonce).toArrayLike(Buffer, "le", 8); // WHY: Convert nonce to seed bytes.
    const lockRecord = PublicKey.findProgramAddressSync([Buffer.from("lock_record"), lockRecordSeed], bridgeProgramId)[0]; // WHY: Derive lock record address.
    const lockData = await bridgeProgram.account.lockRecord.fetch(lockRecord); // WHY: Fetch lock details to build the message.
    if (lockData.isReleased) { // WHY: Skip if the lock was already processed and minted.
      console.log(`Lock ${nonce} already minted, skipping`); // WHY: Log skip for observability.
      return; // WHY: Exit early to avoid redundant work.
    } // WHY: End already-minted check.
    const wrappedMint = await bridgeProgram.account.bridgeState.fetch(bridgeState).then((s: any) => s.wrappedMint); // WHY: Fetch wrapped mint from state.
    const recipientWrappedAccount = getAssociatedTokenAddressSync(wrappedMint, lockData.user); // WHY: Derive user's wrapped token account.
    const message = Buffer.concat([lockData.user.toBuffer(), new BN(lockData.amount.toString()).toArrayLike(Buffer, "le", 8), lockRecordSeed]); // WHY: Reconstruct the exact message that the program verifies: user + amount + nonce.
    const messageHash = createHash("sha256").update(message).digest(); // WHY: Compute SHA-256 digest for Ed25519 signing.
    const signatures: Uint8Array[] = []; // WHY: Initialize array to hold valid Ed25519 signatures.
    const guardianIndices: number[] = []; // WHY: Initialize array to map signatures to registry indices.
    const registry = await guardianProgram.account.guardianRegistry.fetch(getGuardianRegistryPDA()); // WHY: Fetch the guardian registry to find matching indices.
    for (let i = 0; i < registry.guardians.length; i++) { // WHY: Iterate over registered guardians to produce signatures.
      const g = registry.guardians[i]; // WHY: Access guardian metadata.
      if (!g.isActive) continue; // WHY: Skip inactive or slashed guardians.
      const gPubkeyHex = Buffer.from(g.ed25519Pubkey).toString("hex"); // WHY: Convert the guardian's stored Ed25519 pubkey to hex for comparison.
      const kp = guardianKeypairs.find((k) => Buffer.from(k.publicKey).toString("hex") === gPubkeyHex); // WHY: Locate the local keypair that matches this guardian's registered Ed25519 pubkey.
      if (!kp) continue; // WHY: Skip guardians whose keys are not loaded in this relayer instance.
      const sig = nacl.sign.detached(messageHash, kp.secretKey); // WHY: Generate a real Ed25519 signature over the SHA-256 message hash using the guardian's secret key.
      signatures.push(sig); // WHY: Store the signature for the transaction.
      guardianIndices.push(i); // WHY: Store the registry index so the program knows which pubkey to verify against.
    } // WHY: End guardian loop.
    if (signatures.length === 0) { // WHY: Abort if no guardian keys are available to sign.
      console.log(`No guardian keys available for lock ${nonce}`); // WHY: Log the failure for operator alerts.
      return; // WHY: Exit early; the relayer will retry on the next poll cycle if keys become available.
    } // WHY: End empty signature check.
    const guardianRegistry = getGuardianRegistryPDA(); // WHY: Derive guardian registry account.
    const tx = await bridgeProgram.methods // WHY: Build the verify_and_mint_wrapped instruction.
      .verifyAndMintWrapped(Array.from(messageHash), signatures, guardianIndices) // WHY: Pass the real signatures and indices to the on-chain verifier.
      .accounts({ // WHY: Map required accounts.
        bridgeState, // WHY: State for threshold validation.
        lockRecord, // WHY: Record to prevent double mint.
        wrappedMint, // WHY: Mint to inflate.
        recipientWrappedAccount, // WHY: User's wrapped account.
        guardianRegistry, // WHY: Registry for signature pubkey lookups.
        tokenProgram: TOKEN_PROGRAM_ID, // WHY: SPL Token program for mint CPI.
      }) // WHY: Close accounts mapping.
      .transaction(); // WHY: Build transaction object.
    tx.feePayer = wallet.publicKey; // WHY: Relayer pays fees.
    tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash; // WHY: Fresh blockhash.
    tx.partialSign(wallet.payer); // WHY: Relayer signs to submit.
    const sig = await connection.sendRawTransaction(tx.serialize()); // WHY: Submit mint proof to the cluster.
    await connection.confirmTransaction(sig, "confirmed"); // WHY: Wait for confirmation.
    console.log(`Minted wrapped tokens for lock ${nonce}, tx: ${sig}`); // WHY: Log success for observability and audit trails.
  } catch (err) { // WHY: Catch and log errors without stopping the polling loop.
    console.error(`Failed to process lock ${nonce}:`, err); // WHY: Print the error so operators can diagnose guardian key mismatches or RPC issues.
  } // WHY: Close catch block.
} // WHY: Close processLockEvent function scope.

async function poll() { // WHY: Define the polling loop that detects new lock events.
  try { // WHY: Catch RPC errors during polling so the loop continues.
    const bridgeState = getBridgeStatePDA(); // WHY: Derive bridge state.
    const state = await bridgeProgram.account.bridgeState.fetch(bridgeState); // WHY: Fetch the current on-chain nonce.
    const currentNonce = state.nonce.toNumber(); // WHY: Convert BN nonce to JS number for comparison.
    while (lastProcessedNonce + 1 < currentNonce) { // WHY: Process every nonce between the last handled and the current chain state.
      lastProcessedNonce += 1; // WHY: Advance the cursor to the next unprocessed lock.
      await processLockEvent(lastProcessedNonce); // WHY: Handle the lock event asynchronously.
    } // WHY: End catch-up loop.
  } catch (err) { // WHY: Catch polling errors such as RPC downtime.
    console.error("Poll error:", err); // WHY: Log the error for monitoring.
  } // WHY: Close catch block.
  setTimeout(poll, POLL_INTERVAL_MS); // WHY: Schedule the next poll after the interval.
} // WHY: Close poll function scope.

console.log("Relayer starting..."); // WHY: Indicate service startup in logs.
poll(); // WHY: Start the first poll immediately; subsequent polls are scheduled recursively.
