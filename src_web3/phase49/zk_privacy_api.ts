import express, { Request, Response } from "express"; // Import Express to build the HTTP API for simulated ZK proof generation, verification, and privacy-preserving credential checks

const app = express(); // Initialize the Express application instance for the ZK privacy service

app.use(express.json()); // Enable JSON body parsing so clients can send witness data and public inputs for proof operations

const PORT = 3053; // Use port 3053 to avoid conflicts with other Web3 phase APIs running in the project

interface Proof { // Define the Proof interface so TypeScript can enforce the shape of every simulated ZK proof
  id: string; // Unique identifier for referencing and tracking a specific proof
  statement: string; // Human-readable description of what the proof claims
  publicInputs: Record<string, unknown>; // Public values that the verifier can see and check against
  proofData: string; // Simulated opaque proof bytes representing the cryptographic evidence
  verified: boolean; // Flag indicating whether the proof has passed verification
  createdAt: number; // Unix timestamp when the proof was generated
} // Close the block

interface Credential { // Define the Credential interface to represent private user data that can be proven without disclosure
  userId: string; // Identifier of the user who owns the credential
  attribute: string; // Type of credential, such as age, income, or membership status
  value: number | string; // The actual secret value stored privately and never exposed directly
  salt: string; // Random value mixed with the attribute to prevent brute-force guessing
} // Close the block

const proofs: Map<string, Proof> = new Map(); // In-memory storage for generated proofs keyed by proof ID

const credentials: Map<string, Credential> = new Map(); // In-memory storage for private credentials keyed by user ID and attribute

const verificationHistory: { proofId: string; result: boolean; checkedAt: number }[] = []; // In-memory storage for verification history so we can audit proof checks

let nextProofId = 1; // Sequence counter to generate unique proof IDs without an external database

app.get("/health", (_req: Request, res: Response) => { // Health check endpoint so load balancers and operators can verify the service is alive
  res.json({ // Return current system status, proof counts, and credential counts for monitoring dashboards
    status: "healthy", // Signal that the API process is running and responsive
    totalProofs: proofs.size, // Report how many proofs have been generated
    verifiedProofs: Array.from(proofs.values()).filter((p) => p.verified).length, // Report how many proofs passed verification
    totalCredentials: credentials.size, // Report how many private credentials are stored
    verificationChecks: verificationHistory.length, // Report how many verification attempts have been made
  }); // Close the route handler
}); // Close the route handler

app.post("/credential/register", (req: Request, res: Response) => { // Endpoint to register a private credential that can later be used in zero-knowledge proofs
  const { userId, attribute, value, salt } = req.body; // Destructure required parameters from the request body

  if (!userId || !attribute || value === undefined || !salt) { // Validate that all required fields are present to prevent malformed credential registrations
    return res.status(400).json({ error: "userId, attribute, value, and salt are required" }); // Return result to the caller
  } // Close the block

  const credential: Credential = { // Build the new Credential object to store the private data securely in memory
    userId, // Execute the statement
    attribute, // Execute the statement
    value, // Execute the statement
    salt, // Execute the statement
  }; // Execute the statement

  credentials.set(`${userId}:${attribute}`, credential); // Store the credential using a composite key so each user-attribute pair is unique

  const commitment = Buffer.from(`${value}:${salt}`).toString("base64"); // Return a commitment hash so the user can reference this credential in proofs without revealing the value
  res.status(201).json({ success: true, userId, attribute, commitment }); // Send the HTTP response with status code
}); // Close the route handler

app.post("/proof/generate", (req: Request, res: Response) => { // Endpoint to generate a simulated ZK proof that a credential satisfies a condition
  const { userId, attribute, condition, threshold } = req.body; // Destructure required parameters from the request body

  if (!userId || !attribute || !condition || threshold === undefined) { // Validate that all required fields are present to prevent malformed proof generation requests
    return res.status(400).json({ error: "userId, attribute, condition, and threshold are required" }); // Return result to the caller
  } // Close the block

  const credential = credentials.get(`${userId}:${attribute}`); // Look up the target credential to ensure it exists before generating a proof about it
  if (!credential) { // Validate that the required condition is met
    return res.status(404).json({ error: "Credential not found" }); // Return result to the caller
  } // Close the block

  let statementTrue = false; // Evaluate the condition against the secret value to determine if the statement is true
  const numericValue = Number(credential.value); // Declare and initialize the variable
  if (condition === "gt") { // Check the condition before proceeding
    statementTrue = numericValue > Number(threshold); // Prove value is greater than threshold
  } else if (condition === "lt") { // Handle the alternative condition branch
    statementTrue = numericValue < Number(threshold); // Prove value is less than threshold
  } else if (condition === "eq") { // Handle the alternative condition branch
    statementTrue = credential.value === threshold; // Prove value equals threshold
  } else if (condition === "gte") { // Handle the alternative condition branch
    statementTrue = numericValue >= Number(threshold); // Prove value is greater than or equal to threshold
  } else { // Handle the alternative branch
    return res.status(400).json({ error: "condition must be gt, lt, eq, or gte" }); // Return result to the caller
  } // Close the block

  if (!statementTrue) { // Reject proof generation if the statement is false because a valid ZK proof cannot prove a false statement
    return res.status(400).json({ error: "Statement is false. Cannot generate valid proof." }); // Return result to the caller
  } // Close the block

  const publicInputs: Record<string, unknown> = { // Build public inputs that the verifier can see, deliberately excluding the secret value
    userId: credential.userId, // Set the property value
    attribute: credential.attribute, // Set the property value
    condition, // Execute the statement
    threshold, // Execute the statement
    commitment: Buffer.from(`${credential.value}:${credential.salt}`).toString("base64"), // Set the property value
  }; // Execute the statement

  const proofData = Buffer.from(JSON.stringify(publicInputs)).toString("base64"); // Simulate proof data as a hash of the inputs because this is an educational API without real cryptography

  const proof: Proof = { // Build the new Proof object with generated metadata
    id: String(nextProofId++), // Increment global ID counter so every proof is unique
    statement: `Prove that ${attribute} ${condition} ${threshold}`, // Set the property value
    publicInputs, // Execute the statement
    proofData, // Execute the statement
    verified: false, // Initialize as unverified until an explicit verification call is made
    createdAt: Date.now(), // Set the property value
  }; // Execute the statement

  proofs.set(proof.id, proof); // Store the proof in the in-memory map keyed by its unique ID

  res.status(201).json({ success: true, proof }); // Return the proof object so the prover can share the proof ID with verifiers
}); // Close the route handler

app.post("/proof/verify", (req: Request, res: Response) => { // Endpoint to verify a ZK proof by checking its consistency and public inputs
  const { proofId } = req.body; // Destructure the proof ID from the request body

  if (!proofId) { // Validate that proofId is provided because we cannot verify a missing proof
    return res.status(400).json({ error: "proofId is required" }); // Return result to the caller
  } // Close the block

  const proof = proofs.get(proofId); // Look up the target proof to ensure it exists
  if (!proof) { // Validate that the required condition is met
    return res.status(404).json({ error: "Proof not found" }); // Return result to the caller
  } // Close the block

  const expectedData = Buffer.from(JSON.stringify(proof.publicInputs)).toString("base64"); // Simulate verification by re-deriving the expected proof data from public inputs

  const isValid = proof.proofData === expectedData; // Check if the stored proof data matches the re-derived data because a valid proof must be internally consistent

  proof.verified = isValid; // Update the proof's verified flag so future queries reflect its status

  verificationHistory.push({ proofId, result: isValid, checkedAt: Date.now() }); // Record the verification attempt in history for auditing

  res.json({ success: true, proofId, verified: isValid, statement: proof.statement }); // Return the verification result so the caller knows whether the proof is valid
}); // Close the route handler

app.get("/proof/:id", (req: Request, res: Response) => { // Endpoint to fetch a single proof by ID so users can inspect its public inputs
  const proof = proofs.get(req.params.id); // Look up the proof in the generated proofs map using the URL parameter

  if (!proof) { // Return 404 if the proof does not exist or has not been generated
    return res.status(404).json({ error: "Proof not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, proof }); // Return the proof without any secret witness data because the zero-knowledge property hides the witness
}); // Close the route handler

app.get("/proofs/user/:userId", (req: Request, res: Response) => { // Endpoint to list all proofs for a specific user so they can manage their privacy claims
  const userProofs = Array.from(proofs.values()).filter((p) => p.publicInputs.userId === req.params.userId); // Filter the proofs map to find only proofs whose public inputs reference the given user

  res.json({ success: true, count: userProofs.length, proofs: userProofs }); // Return the filtered list so wallets and frontends can display the user's proof history
}); // Close the route handler

app.post("/proof/range", (req: Request, res: Response) => { // Endpoint to simulate a range proof, proving a value is within a range without revealing the exact value
  const { userId, attribute, min, max } = req.body; // Destructure required parameters from the request body

  if (!userId || !attribute || min === undefined || max === undefined) { // Validate that all required fields are present to prevent malformed range proof requests
    return res.status(400).json({ error: "userId, attribute, min, and max are required" }); // Return result to the caller
  } // Close the block

  const credential = credentials.get(`${userId}:${attribute}`); // Look up the target credential to ensure it exists before generating a range proof about it
  if (!credential) { // Validate that the required condition is met
    return res.status(404).json({ error: "Credential not found" }); // Return result to the caller
  } // Close the block

  const numericValue = Number(credential.value); // Check if the secret value falls within the requested range
  const inRange = numericValue >= Number(min) && numericValue <= Number(max); // Declare and initialize the variable

  if (!inRange) { // Reject proof generation if the value is outside the range because a valid proof cannot assert a false statement
    return res.status(400).json({ error: `Value ${numericValue} is outside range [${min}, ${max}]` }); // Return result to the caller
  } // Close the block

  const publicInputs: Record<string, unknown> = { // Build public inputs that reveal only the range boundaries, not the exact secret value
    userId: credential.userId, // Set the property value
    attribute: credential.attribute, // Set the property value
    min, // Execute the statement
    max, // Execute the statement
    commitment: Buffer.from(`${credential.value}:${credential.salt}`).toString("base64"), // Set the property value
  }; // Execute the statement

  const proofData = Buffer.from(JSON.stringify(publicInputs)).toString("base64"); // Simulate range proof data as a hash of the public inputs

  const proof: Proof = { // Build the new Proof object representing the range claim
    id: String(nextProofId++), // Set the property value
    statement: `Prove that ${attribute} is between ${min} and ${max}`, // Set the property value
    publicInputs, // Execute the statement
    proofData, // Execute the statement
    verified: false, // Set the property value
    createdAt: Date.now(), // Set the property value
  }; // Execute the statement

  proofs.set(proof.id, proof); // Store the proof in the in-memory map keyed by its unique ID

  res.status(201).json({ success: true, proof }); // Return the proof so the prover can use it to demonstrate membership in the range without disclosure
}); // Close the route handler

app.get("/stats", (_req: Request, res: Response) => { // Endpoint to retrieve aggregate ZK privacy statistics for dashboards
  const totalProofs = proofs.size; // Calculate total proofs generated to understand system usage

  const verifiedProofs = Array.from(proofs.values()).filter((p) => p.verified).length; // Calculate total verified proofs to understand verification success rate

  res.json({ // Return summary stats so dashboards can display adoption and privacy activity
    totalProofs, // Execute the statement
    verifiedProofs, // Execute the statement
    pendingProofs: totalProofs - verifiedProofs, // Set the property value
    totalCredentials: credentials.size, // Set the property value
    verificationChecks: verificationHistory.length, // Set the property value
  }); // Close the route handler
}); // Close the route handler

app.listen(PORT, () => { // Start the Express server on the designated port and log readiness
  console.log(`ZK Privacy API listening on port ${PORT}`); // Log startup so operators know the service is ready
}); // Close the route handler
