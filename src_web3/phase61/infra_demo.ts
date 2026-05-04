import {
  // WHY: Import all required classes from the official Solana web3.js library.
  Connection,
  // WHY: Connection manages RPC communication with the Solana cluster.
  Keypair,
  // WHY: Keypair generates and holds public/private keys for signing.
  PublicKey,
  // WHY: PublicKey represents on-chain account addresses in a type-safe way.
  TransactionMessage,
  // WHY: TransactionMessage compiles instructions into a versioned message format.
  VersionedTransaction,
  // WHY: VersionedTransaction is the v0 format that supports Address Lookup Tables.
  AddressLookupTableProgram,
  // WHY: AddressLookupTableProgram provides instructions to create and extend LUTs.
  ComputeBudgetProgram,
  // WHY: ComputeBudgetProgram sets compute unit limits and priority fees.
  SystemProgram,
  // WHY: SystemProgram provides basic Solana instructions like transfer and createAccount.
  LAMPORTS_PER_SOL,
  // WHY: LAMPORTS_PER_SOL is the conversion constant (1 SOL = 1e9 lamports).
} from "@solana/web3.js";
// WHY: The @solana/web3.js package is the canonical Solana JavaScript SDK.

import "dotenv/config";
// WHY: dotenv loads environment variables from .env so secrets are not hardcoded.

const HELIUS_API_KEY = process.env.HELIUS_API_KEY || "";
// WHY: Read the Helius API key from environment variables for security.
if (!HELIUS_API_KEY) {
  // WHY: Validate that the key exists to fail fast with a clear error.
  throw new Error("HELIUS_API_KEY is required in .env");
  // WHY: Throwing here prevents the script from running with an invalid RPC URL.
}

const HELIUS_RPC = `https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}`;
// WHY: Construct the authenticated Helius RPC endpoint using the real Helius domain.
const connection = new Connection(HELIUS_RPC, "confirmed");
// WHY: Create a Connection with 'confirmed' commitment for balanced speed and finality.

const payerSecret = process.env.SOLANA_PRIVATE_KEY || "";
// WHY: Read the fee payer private key from environment variables.
let payer: Keypair;
// WHY: Declare payer in outer scope so it is accessible across async functions.
if (payerSecret) {
  // WHY: Only parse the key if it was provided to avoid crashing on empty string.
  const decoded = Uint8Array.from(JSON.parse(payerSecret));
  // WHY: Convert the JSON-encoded secret key array into a Uint8Array.
  payer = Keypair.fromSecretKey(decoded);
  // WHY: Reconstruct the Keypair from the secret key bytes.
} else {
  // WHY: Fallback to a random Keypair for read-only demo operations.
  payer = Keypair.generate();
  // WHY: Generate a new random keypair when no private key is configured.
}

async function getPriorityFeeEstimate(): Promise<number> {
  // WHY: Define an async function to fetch a dynamic priority fee from Helius.
  const response = await fetch(HELIUS_RPC, {
    // WHY: Use fetch to call the Helius JSON-RPC HTTP endpoint.
    method: "POST",
    // WHY: JSON-RPC requires POST to submit request bodies.
    headers: { "Content-Type": "application/json" },
    // WHY: Set Content-Type so the server correctly parses the JSON body.
    body: JSON.stringify({
      // WHY: Serialize the JSON-RPC request payload.
      jsonrpc: "2.0",
      // WHY: Specify the JSON-RPC protocol version expected by Solana nodes.
      id: 1,
      // WHY: Provide a request ID to match the response (required by spec).
      method: "getPriorityFeeEstimate",
      // WHY: Call the Helius-enhanced endpoint for fee market data.
      params: [
        {
          // WHY: params is an array containing a single configuration object.
          accountKeys: [SystemProgram.programId.toBase58()],
          // WHY: Pass a relevant program ID to scope the fee estimate to actual transaction patterns.
          options: { includeAllPriorityFeeLevels: true },
          // WHY: Request all fee levels so we can choose the appropriate urgency.
        },
      ],
    }),
  });
  // WHY: Await the HTTP response from Helius.

  const data = await response.json();
  // WHY: Parse the JSON body into a JavaScript object.
  console.log("Priority fee response:", JSON.stringify(data, null, 2));
  // WHY: Log the raw response for transparency and debugging.

  const medium = data.result?.priorityFeeLevels?.medium || 0;
  // WHY: Extract the 'medium' fee level as a balanced default; fallback to 0 if absent.
  return medium;
  // WHY: Return the numeric micro-lamport value to the caller.
}

async function createLookupTable(): Promise<PublicKey> {
  // WHY: Define an async function to create an on-chain Address Lookup Table.
  const slot = await connection.getSlot();
  // WHY: Fetch the current slot because LUT creation requires a recent slot parameter.
  const [createInstruction, lookupTableAddress] =
    // WHY: The create method returns both the instruction and the derived address.
    AddressLookupTableProgram.createLookupTable({
      // WHY: Call the program method to build the create-LUT instruction.
      authority: payer.publicKey,
      // WHY: The authority is the only account that can later extend or close this LUT.
      payer: payer.publicKey,
      // WHY: The payer funds the rent-exempt balance for the new LUT account.
      recentSlot: slot,
      // WHY: Use the current slot to derive the LUT address deterministically.
    });
  // WHY: Destructure the returned tuple into the instruction and the address.

  const messageV0 = new TransactionMessage({
    // WHY: Use TransactionMessage to build a version-0 compatible message.
    payerKey: payer.publicKey,
    // WHY: Set the fee payer for this transaction.
    recentBlockhash: (await connection.getLatestBlockhash()).blockhash,
    // WHY: Fetch a recent blockhash to prevent replay and expiration.
    instructions: [createInstruction],
    // WHY: Include only the LUT creation instruction in this transaction.
  }).compileToV0Message();
  // WHY: Compile the message into the v0 format even though no LUTs are referenced yet.

  const tx = new VersionedTransaction(messageV0);
  // WHY: Create a versioned transaction from the compiled v0 message.
  tx.sign([payer]);
  // WHY: Sign the transaction with the payer so it is valid for submission.

  const sig = await connection.sendTransaction(tx);
  // WHY: Submit the signed transaction to the Helius RPC for confirmation.
  console.log("LUT created. Signature:", sig);
  // WHY: Log the signature so the transaction can be inspected on a block explorer.
  console.log("LUT Address:", lookupTableAddress.toBase58());
  // WHY: Print the derived LUT address; it must be saved for future transactions.

  await connection.confirmTransaction(sig, "confirmed");
  // WHY: Wait for confirmation before returning so the LUT exists on-chain.
  return lookupTableAddress;
  // WHY: Return the address so subsequent code can reference it.
}

async function extendLookupTable(
  // WHY: Define a function to add addresses into an existing LUT.
  lookupTableAddress: PublicKey,
  // WHY: Accept the target LUT address as a parameter.
  addresses: PublicKey[]
  // WHY: Accept the list of addresses to compress.
): Promise<void> {
  // WHY: Return nothing; the side effect is the on-chain extension.
  const extendInstruction = AddressLookupTableProgram.extendLookupTable({
    // WHY: Build the instruction that appends addresses to the LUT.
    payer: payer.publicKey,
    // WHY: The payer covers the additional rent for the new address entries.
    authority: payer.publicKey,
    // WHY: Only the authority can modify the LUT contents.
    lookupTable: lookupTableAddress,
    // WHY: Specify which LUT account to extend.
    addresses,
    // WHY: Pass the array of public keys to store inside the LUT.
  });
  // WHY: The instruction is ready to be included in a transaction.

  const messageV0 = new TransactionMessage({
    // WHY: Build a version-0 message for the extend transaction.
    payerKey: payer.publicKey,
    // WHY: The payer funds the transaction fee and rent.
    recentBlockhash: (await connection.getLatestBlockhash()).blockhash,
    // WHY: Use a fresh blockhash to ensure the transaction is accepted.
    instructions: [extendInstruction],
    // WHY: The transaction contains only the extend instruction.
  }).compileToV0Message();
  // WHY: Compile to v0 so it is consistent with the rest of the phase.

  const tx = new VersionedTransaction(messageV0);
  // WHY: Construct a VersionedTransaction from the compiled message.
  tx.sign([payer]);
  // WHY: Sign with the payer/authority to authorize the LUT modification.

  const sig = await connection.sendTransaction(tx);
  // WHY: Send the transaction via the Helius RPC.
  console.log("LUT extended. Signature:", sig);
  // WHY: Log the signature for verification and debugging.
  await connection.confirmTransaction(sig, "confirmed");
  // WHY: Wait for on-chain confirmation so the addresses are usable.
}

async function buildAndSimulateVersionedTx(
  // WHY: Define a function that builds a v0 transaction using a LUT.
  lookupTableAddress: PublicKey
  // WHY: Pass the LUT address so the transaction can reference compressed accounts.
): Promise<void> {
  // WHY: No return value needed; the function logs simulation results.
  const priorityFee = await getPriorityFeeEstimate();
  // WHY: Fetch the current market-driven priority fee before building the transaction.
  const computeBudgetIx = ComputeBudgetProgram.setComputeUnitLimit({
    // WHY: Set an explicit compute unit limit to control cost and resource allocation.
    units: 30000,
    // WHY: 30,000 CUs is sufficient for a simple transfer or token instruction.
  });
  // WHY: Compute budget instructions must precede program instructions.

  const priorityFeeIx = ComputeBudgetProgram.setComputeUnitPrice({
    // WHY: Attach the priority fee so the transaction is prioritized by the leader.
    microLamports: priorityFee,
    // WHY: Use the dynamically estimated fee in micro-lamports per compute unit.
  });
  // WHY: Without this instruction, the transaction pays only the base fee.

  const transferIx = SystemProgram.transfer({
    // WHY: Create a simple SOL transfer as the core business logic instruction.
    fromPubkey: payer.publicKey,
    // WHY: The payer is the sender of the SOL.
    toPubkey: new PublicKey("11111111111111111111111111111111"),
    // WHY: Use the system program ID as a dummy recipient for demo purposes.
    lamports: 0.001 * LAMPORTS_PER_SOL,
    // WHY: Transfer a small, safe amount of SOL (0.001) for the demonstration.
  });
  // WHY: SystemProgram.transfer is a reliable instruction for basic testing.

  const lookupTableAccount = await connection
    .getAddressLookupTable(lookupTableAddress)
    // WHY: Fetch the on-chain LUT account state to resolve stored addresses.
    .then((res) => res.value);
  // WHY: Extract the actual account object from the RPC response wrapper.

  if (!lookupTableAccount) {
    // WHY: Guard against using a missing or unconfirmed LUT.
    throw new Error("Lookup table account not found");
    // WHY: Fail fast rather than submitting a transaction with invalid references.
  }
  // WHY: The lookup table must exist on-chain before it can be referenced.

  const messageV0 = new TransactionMessage({
    // WHY: Build the transaction message with v0 compatibility.
    payerKey: payer.publicKey,
    // WHY: The fee payer signs and funds the transaction.
    recentBlockhash: (await connection.getLatestBlockhash()).blockhash,
    // WHY: A recent blockhash is required for every transaction to prevent replay.
    instructions: [computeBudgetIx, priorityFeeIx, transferIx],
    // WHY: Order matters: compute budget instructions must come first.
  }).compileToV0Message([lookupTableAccount]);
  // WHY: Pass the LUT account so the compiler can replace addresses with 1-byte indices.

  const versionedTx = new VersionedTransaction(messageV0);
  // WHY: Instantiate the versioned transaction from the compiled v0 message.
  versionedTx.sign([payer]);
  // WHY: Sign the transaction to prove authorization from the fee payer.

  console.log("Transaction serialized size:", versionedTx.serialize().length, "bytes");
  // WHY: Log the byte size to demonstrate the space savings achieved by the LUT.

  const simulation = await connection.simulateTransaction(versionedTx);
  // WHY: Run a dry-run execution on the RPC node to catch errors before spending fees.
  console.log("Simulation result:", JSON.stringify(simulation.value, null, 2));
  // WHY: Print the full simulation output including logs and error fields.

  if (simulation.value.err) {
    // WHY: Inspect the error field to decide whether to proceed with submission.
    console.error("Simulation failed. Do not send transaction.");
    // WHY: Warn the user that the transaction would fail on-chain.
    return;
    // WHY: Abort to avoid wasting SOL on a failed transaction.
  }
  // WHY: Sending a transaction that failed simulation is a preventable cost.

  console.log("Simulation succeeded. Ready to send.");
  // WHY: Confirm success so the user knows the next step is safe.
}

async function main() {
  // WHY: The main entry point orchestrates the demo steps sequentially.
  console.log("Payer:", payer.publicKey.toBase58());
  // WHY: Display the fee payer address for record keeping.

  const lutAddress = await createLookupTable();
  // WHY: Step 1: Create the LUT on-chain.
  await extendLookupTable(lutAddress, [
    // WHY: Step 2: Populate the LUT with addresses that will be referenced later.
    SystemProgram.programId,
    // WHY: Store the system program ID as a demo address.
    new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
    // WHY: Store the SPL Token program ID as another common reference.
  ]);
  // WHY: Extend must happen after creation and before the LUT is referenced.

  await buildAndSimulateVersionedTx(lutAddress);
  // WHY: Step 3: Build a versioned transaction, attach priority fees, and simulate.
}

main().catch((err) => {
  // WHY: Catch top-level errors to prevent unhandled promise rejections.
  console.error("Demo failed:", err);
  // WHY: Print the error so the user can diagnose the failure.
  process.exit(1);
  // WHY: Exit with a non-zero code so CI or scripts detect failure.
});
// WHY: Invoke main and attach a global error handler.
