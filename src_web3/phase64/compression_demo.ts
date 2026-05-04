import { createRpc } from "@lightprotocol/stateless.js"; // WHY: Import the Light Protocol RPC factory to connect to the compressed-state indexer and ZK prover service.
import { CompressedTokenProgram } from "@lightprotocol/compressed-token"; // WHY: Import the compressed-token SDK to create mints, mint tokens, and execute ZK-verified transfers.
import { Keypair, PublicKey } from "@solana/web3.js"; // WHY: Import Solana web3.js for keypair generation and public key types used across Light Protocol instructions.
const RPC_ENDPOINT = process.env.RPC_ENDPOINT || "https://devnet.helius-rpc.com/?api-key=YOUR_API_KEY"; // WHY: Read the RPC endpoint from environment variables so the demo can target devnet, mainnet, or a custom Light Protocol node without code changes.
const rpc = createRpc(RPC_ENDPOINT); // WHY: Create the Light Protocol RPC connection which routes compressed-state queries, validity proofs, and transaction submissions to the correct cluster.
const payer = Keypair.generate(); // WHY: Generate a payer keypair for demonstration purposes; in production this secret key must be loaded from a secure vault or environment variable.
const recipient = Keypair.generate(); // WHY: Generate a recipient keypair so the demo can show minting compressed tokens to a fresh address with no prior on-chain state.
async function runCompressionDemo() { // WHY: Define the main async function so we can use await for asynchronous on-chain operations like mint creation and proof generation.
  console.log("Starting ZK Compression demo, RPC:", RPC_ENDPOINT); // WHY: Log the target endpoint so operators can confirm the demo is running against the expected Solana cluster.
  const createMintResult = await CompressedTokenProgram.createMint( // WHY: Step 1 — Create a compressed token mint so there is a Merkle tree-backed token type to issue and transfer.
    rpc, // WHY: Pass the RPC so the SDK can read the current fee payer balance and submit the Merkle tree initialization transaction.
    payer, // WHY: The payer signs and pays the small network fee for creating the Merkle tree account that stores compressed mint metadata.
    payer.publicKey, // WHY: The payer is the mint authority so it can authorize the creation of new compressed tokens later.
    9 // WHY: Use 9 decimals to match the standard SPL token convention where 1 token equals 1 billion base units.
  ); // WHY: Close the createMint call so the SDK can return the mint public key and transaction signature.
  const mint = createMintResult.mint; // WHY: Destructure the mint public key from the result so subsequent instructions can reference the same compressed token type.
  console.log("Compressed mint created:", mint.toBase58()); // WHY: Log the mint address so developers can inspect the compressed token mint on a Solana explorer.
  console.log("Mint tx signature:", createMintResult.transactionSignature); // WHY: Log the transaction signature so the exact on-chain creation event can be traced and debugged if necessary.
  const mintAmount = 1_000_000_000n; // WHY: Represent 1 token in base units using BigInt to match the u64 on-chain integer format and avoid precision loss.
  const mintSig = await CompressedTokenProgram.mintTo( // WHY: Step 2 — Mint compressed tokens to the recipient so their balance is stored as a leaf in the Merkle tree rather than a standard account.
    rpc, // WHY: The RPC provides the current Merkle tree state and relays the append instruction to the on-chain Light Protocol program.
    payer, // WHY: The payer funds the transaction fee and signs the instruction that increases the token supply.
    mint, // WHY: Specify the compressed mint so the new leaf is correctly tagged with the token type and decimal metadata.
    recipient.publicKey, // WHY: Embed the recipient's public key in the leaf so only their private key can authorize future spends of this balance.
    payer.publicKey, // WHY: The mint authority must explicitly sign to prove it is authorized to inflate this compressed token supply.
    mintAmount // WHY: The integer amount becomes the balance field of the newly created compressed token leaf in the Merkle tree.
  ); // WHY: Close the mintTo call so the SDK can return the transaction signature for verification.
  console.log("Minted to", recipient.publicKey.toBase58(), "tx:", mintSig); // WHY: Log the mint transaction signature so operators can verify the compressed tokens were successfully appended on-chain.
  const compressedAccounts = await rpc.getCompressedTokenAccountsByOwner(recipient.publicKey); // WHY: Step 3 — Read compressed balances from the Light Protocol indexer to verify the mint was recorded without creating an SPL token account.
  console.log("Recipient compressed accounts:", compressedAccounts); // WHY: Log the returned compressed accounts to demonstrate that balance data is reconstructed off-chain by the indexer from Merkle tree updates.
  const transferAmount = 500_000_000n; // WHY: Transfer half a token to demonstrate that partial spending is supported from a compressed leaf balance.
  const newRecipient = Keypair.generate(); // WHY: Generate a fresh recipient to prove compressed tokens can be sent to any valid Solana address.
  const leafHashes = compressedAccounts.items.map((item: any) => item.hash); // WHY: Map the recipient's compressed account items to their leaf hashes because the prover needs hashes to build a Merkle inclusion proof.
  const proof = await rpc.getValidityProof(leafHashes); // WHY: Request a validity proof from the Light Protocol RPC that proves the sender's leaf exists in the current Merkle tree root.
  const transferSig = await CompressedTokenProgram.transfer( // WHY: Step 4 — Transfer compressed tokens by generating a ZK proof that the sender owns a valid leaf without revealing all leaf data.
    rpc, // WHY: The RPC relays the ZK proof and current Merkle tree context to the on-chain Light Protocol verifier program.
    payer, // WHY: The payer signs the transaction and pays the network fee for the proof verification and root update.
    mint, // WHY: The mint address identifies which compressed token standard and Merkle tree to use for the spend logic.
    transferAmount, // WHY: The exact base-unit quantity to move from the sender's leaf to a new leaf owned by the recipient.
    newRecipient.publicKey, // WHY: The destination public key is written into the new leaf so only they can spend it in the future.
    proof // WHY: The ZK proof convinces the on-chain verifier that the spendable leaf exists without reading every leaf on Solana.
  ); // WHY: Close the transfer call so the SDK can return the transaction signature for the ZK-verified spend.
  console.log("Transferred compressed tokens, tx:", transferSig); // WHY: Log the transfer signature so developers can trace the ZK-verified transaction on a Solana explorer.
  const senderAccounts = await rpc.getCompressedTokenAccountsByOwner(recipient.publicKey); // WHY: Step 5 — Read final compressed balances to demonstrate that both sender and recipient now hold valid leaves after the transfer.
  const receiverAccounts = await rpc.getCompressedTokenAccountsByOwner(newRecipient.publicKey); // WHY: Query the new recipient's compressed balances to prove the Merkle tree was updated correctly and the recipient received the transfer.
  console.log("Sender remaining balance:", senderAccounts); // WHY: Log the sender's remaining compressed balance to verify that change was returned correctly after the partial spend.
  console.log("Receiver new balance:", receiverAccounts); // WHY: Log the receiver's compressed balance to confirm the ZK transfer preserved token conservation and created the expected leaf.
} // WHY: Close the main async function so the demo logic is encapsulated and can be invoked cleanly.
runCompressionDemo().catch((err) => { // WHY: Invoke the demo function and catch any errors so the process exits cleanly if the RPC is unreachable or proof generation fails.
  console.error("Compression demo failed:", err); // WHY: Log the error to stderr so operators can diagnose network, proof, or configuration issues.
  process.exit(1); // WHY: Exit with a non-zero code so automated CI pipelines recognize the demo did not complete successfully.
}); // WHY: Close the catch handler so unhandled promise rejections are captured and logged.
