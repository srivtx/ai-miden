import fetch from "node-fetch";
// WHY: node-fetch is used to query guardian APIs and the bridge API for events and signatures.
import * as bs58 from "bs58";
// WHY: bs58 decodes the relayer's private key from environment variables (reserved for direct submission).

const SOURCE_RPC = process.env.SOURCE_RPC || "http://localhost:8545";
// WHY: The source chain RPC endpoint is where the relayer monitors for lock events.
const BRIDGE_API = process.env.BRIDGE_API || "http://localhost:3060";
// WHY: The bridge API provides an HTTP interface for querying status and submitting proofs.

const RELAYER_KEYPAIR = {
  publicKey: bs58.decode(process.env.RELAYER_PUBLIC_KEY || "11111111111111111111111111111111"),
  secretKey: bs58.decode(process.env.RELAYER_PRIVATE_KEY || "1111111111111111111111111111111111111111111111111111111111111111"),
};
// WHY: The relayer identity is used to authenticate requests if the bridge API requires signed headers.

const GUARDIAN_ENDPOINTS = [
  // WHY: A list of guardian HTTP endpoints allows the relayer to query multiple nodes for signatures.
  "http://localhost:4001",
  "http://localhost:4002",
  "http://localhost:4003",
  "http://localhost:4004",
  "http://localhost:4005",
];

const THRESHOLD = 3;
// WHY: The relayer must collect at least 3 signatures before submitting a proof to the target chain.

interface LockEvent {
  // WHY: A typed interface prevents errors when parsing event data from the source chain.
  user: string;
  amount: number;
  targetRecipient: string;
  nonce: number;
  txHash: string;
}

async function fetchPendingEvents(): Promise<LockEvent[]> {
  // WHY: The relayer must continuously poll for new lock events that have not yet been relayed.
  try {
    const response = await fetch(`${BRIDGE_API}/bridge/status/pending`);
    // WHY: Calling the bridge API abstracts the source chain indexing logic from the relayer.
    if (!response.ok) {
      // WHY: Checking response.ok ensures we do not parse error pages as valid JSON.
      return [];
    }
    const data = await response.json() as { events: LockEvent[] };
    // WHY: Casting the response to the expected shape catches schema mismatches early.
    return data.events || [];
    // WHY: Defaulting to an empty array prevents undefined errors if the API returns no events field.
  } catch (error) {
    // WHY: Catching network errors prevents the relayer from crashing if the API is temporarily unreachable.
    console.error("Failed to fetch pending events:", error);
    return [];
  }
}

async function collectSignatures(eventHash: string): Promise<{ signatures: string[], indices: number[] }> {
  // WHY: The relayer queries each guardian independently to collect threshold signatures.
  const signatures: string[] = [];
  // WHY: An array holds the raw signature strings returned by guardian APIs.
  const indices: number[] = [];
  // WHY: An array holds the guardian indices corresponding to each signature for on-chain verification.
  for (let i = 0; i < GUARDIAN_ENDPOINTS.length; i++) {
    // WHY: Iterating over all endpoints maximizes the chance of reaching the threshold.
    const endpoint = GUARDIAN_ENDPOINTS[i];
    // WHY: Select the current guardian endpoint.
    try {
      const response = await fetch(`${endpoint}/attest?eventHash=${eventHash}`);
      // WHY: The query parameter identifies which event the guardian should sign.
      if (!response.ok) {
        // WHY: Skipping non-ok responses prevents including invalid or missing signatures.
        continue;
      }
      const data = await response.json() as { signature: string };
      // WHY: Parse the JSON response to extract the base64 or hex signature.
      if (data.signature) {
        // WHY: Only push valid signatures; empty strings would fail on-chain verification.
        signatures.push(data.signature);
        indices.push(i);
        // WHY: The index tells the on-chain program which guardian public key to verify against.
      }
      if (signatures.length >= THRESHOLD) {
        // WHY: Early exit saves bandwidth and time once the threshold is reached.
        break;
      }
    } catch (error) {
      // WHY: Individual guardian failures must not crash the relayer; we log and continue.
      console.error(`Guardian ${i} at ${endpoint} failed:`, error);
    }
  }
  return { signatures, indices };
  // WHY: Returning both arrays allows the caller to construct the complete mint instruction.
}

async function submitMintProof(event: LockEvent, signatures: string[], indices: number[]): Promise<string | null> {
  // WHY: Submitting the proof is the critical action that moves the bridge state forward on the target chain.
  try {
    const response = await fetch(`${BRIDGE_API}/mint`, {
      // WHY: The bridge API handles the Solana transaction construction and submission.
      method: "POST",
      // WHY: POST is required because we are creating a new mint transaction.
      headers: { "Content-Type": "application/json" },
      // WHY: JSON content type ensures the server parses the body correctly.
      body: JSON.stringify({
        // WHY: Serializing the proof data into JSON allows the API to deserialize and construct the instruction.
        recipient: event.targetRecipient,
        amount: event.amount,
        nonce: event.nonce,
        signatures,
        guardianIndices: indices,
      }),
    });
    if (!response.ok) {
      // WHY: A failed response means the proof was rejected; the relayer should retry later.
      console.error("Mint submission failed:", await response.text());
      return null;
    }
    const data = await response.json() as { txHash: string };
    // WHY: Extracting the txHash confirms the transaction was submitted and accepted.
    return data.txHash;
  } catch (error) {
    // WHY: Catching submission errors prevents the relayer loop from terminating.
    console.error("Error submitting mint proof:", error);
    return null;
  }
}

async function runRelayerLoop() {
  // WHY: The main loop ensures continuous monitoring and relaying without manual intervention.
  console.log("Relayer started");
  // WHY: Logging startup confirms the process is alive.
  while (true) {
    // WHY: An infinite loop is standard for daemon services that must run 24/7.
    try {
      const events = await fetchPendingEvents();
      // WHY: Fetch the current batch of unprocessed lock events.
      for (const event of events) {
        // WHY: Process each event sequentially to avoid nonce conflicts and double-mints.
        console.log(`Processing event nonce ${event.nonce} for ${event.amount} tokens`);
        // WHY: Logging each event aids debugging and provides an audit trail.
        const eventHash = `${event.user}:${event.amount}:${event.nonce}`;
        // WHY: Constructing a deterministic hash string identifies the event for guardians.
        const { signatures, indices } = await collectSignatures(eventHash);
        // WHY: Collect threshold signatures before attempting to submit.
        if (signatures.length < THRESHOLD) {
          // WHY: If the threshold is not met, we cannot mint; skip and retry next iteration.
          console.warn(`Threshold not met for nonce ${event.nonce}`);
          continue;
        }
        const txHash = await submitMintProof(event, signatures, indices);
        // WHY: Submit the aggregated proof to the target chain.
        if (txHash) {
          // WHY: Only mark as processed if the submission returned a valid transaction hash.
          console.log(`Minted for nonce ${event.nonce} in tx ${txHash}`);
          // WHY: Logging the successful txHash allows operators to monitor progress.
        }
      }
    } catch (error) {
      // WHY: Catching errors in the outer loop prevents the relayer from dying on unexpected failures.
      console.error("Relayer loop error:", error);
    }
    await new Promise((resolve) => setTimeout(resolve, 5000));
    // WHY: A 5-second sleep prevents CPU spinning and reduces RPC load.
  }
}
// WHY: Closing the runRelayerLoop function declaration.

runRelayerLoop();
// WHY: Starting the loop immediately makes this file a standalone executable service.
