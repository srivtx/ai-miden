import express from "express"; // Import the express framework to build the HTTP server for decentralized identity operations
import cors from "cors"; // Import cors middleware to allow browser clients to interact with this API from different origins
import crypto from "crypto"; // Import the crypto module so challenge strings can be generated securely

const app = express(); // Create the express application instance that will handle DID routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects
app.use(cors()); // Enable CORS so frontend dashboards can query identity status without preflight errors

interface DidDocument { // Define a TypeScript interface for a DID document to ensure type safety across endpoints
    id: string; // Store the DID string so the document can be resolved uniquely
    controller: string; // Store the wallet address or public key that controls this DID so authorization can be checked
    publicKey: string; // Store a hex-encoded public key so verifiers can validate signatures
    serviceEndpoints: string[]; // Store a list of URLs where additional data can be fetched so integrations are discoverable
    createdAt: number; // Record the Unix timestamp of creation so document age can be displayed
} // Close the DidDocument interface definition

interface Credential { // Define a TypeScript interface for a verifiable credential to ensure consistent structure
    id: string; // Store a unique identifier for the credential so it can be referenced during verification
    issuerDid: string; // Store the DID of the issuing party so the verifier knows who attested to the claim
    subjectDid: string; // Store the DID of the subject so the credential is bound to a specific identity
    claim: string; // Store the human-readable claim so the content of the attestation is clear
    issuedAt: number; // Record the Unix timestamp when the credential was created so freshness can be evaluated
    signature: string; // Store a hex-encoded signature so tampering can be detected
} // Close the Credential interface definition

const dids: Map<string, DidDocument> = new Map(); // Initialize a Map to store DID documents because fast lookup by DID string is critical
const credentials: Credential[] = []; // Initialize an in-memory array to store issued credentials because this is a teaching demo without a database
const challenges: Map<string, string> = new Map(); // Initialize a Map to store pending authentication challenges so replay attacks are prevented

let nextCredentialId = 1; // Initialize a simple counter to generate unique credential IDs sequentially

function nowSeconds(): number { // Define a helper to get the current time in seconds because credential timestamps use second-level granularity
    return Math.floor(Date.now() / 1000); // Convert millisecond timestamps to whole seconds for clean display
} // Close the nowSeconds helper

function generateDid(controller: string): string { // Define a helper to create a unique DID string from a controller address
    return `did:miden:${controller}`; // Prefix the controller with a method name so the identifier conforms to DID syntax
} // Close the generateDid helper

app.post("/did/create", (req, res) => { // Define an endpoint to register a new DID and its associated document
    const { controller, publicKey, serviceEndpoints } = req.body; // Destructure request fields so validation can be performed
    if (!controller || !publicKey) { // Validate that required fields are present so incomplete documents are rejected
        return res.status(400).json({ error: "Missing required fields: controller, publicKey" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    const did = generateDid(controller); // Generate the DID string so it is deterministic and resolvable
    if (dids.has(did)) { // Check if the DID already exists so duplicate registrations are rejected
        return res.status(409).json({ error: "DID already exists" }); // Return 409 so the client knows the controller is already registered
    } // Close the duplicate check
    const doc: DidDocument = { // Construct a new DID document with all fields initialized
        id: did, // Store the generated DID so the document is self-identifying
        controller, // Store the controller so ownership can be verified later
        publicKey, // Store the public key so signatures from this identity can be validated
        serviceEndpoints: serviceEndpoints || [], // Store service endpoints defaulting to an empty array so optional integrations are supported
        createdAt: nowSeconds(), // Record the current timestamp so the document has a creation date
    }; // Close the DID document creation
    dids.set(did, doc); // Insert the document into the Map so it can be resolved by its DID string
    return res.status(201).json({ // Return a 201 Created response so the client knows the DID was successfully registered
        success: true, // Include a success flag so programmatic clients can check status without deep body parsing
        did, // Return the DID string so the client can reference it in future calls
        document: doc, // Return the full document so the client sees the stored data
    }); // Close the success response
}); // Close the POST /did/create route

app.get("/did/resolve/:did", (req, res) => { // Define an endpoint to resolve a DID to its stored document
    const did = req.params.did; // Extract the DID from the URL path so the server can look up the specific document
    const doc = dids.get(did); // Search the Map for the matching DID so the correct document is returned
    if (!doc) { // Check if the document exists so the server returns a proper error instead of null
        return res.status(404).json({ error: "DID not found" }); // Return 404 so the client knows the DID is unregistered
    } // Close the existence check
    return res.status(200).json({ // Return the found document so the client can read public keys and service endpoints
        did, // Echo the requested DID so the response is self-contained
        document: doc, // Include the full DID document so the client receives all stored fields
    }); // Close the success response
}); // Close the GET /did/resolve/:did route

app.post("/did/authenticate", (req, res) => { // Define an endpoint to issue a challenge for proving DID ownership
    const { did } = req.body; // Destructure the DID from the request so the server can generate a targeted challenge
    if (!did) { // Validate that the DID is provided so the server does not create challenges for undefined identifiers
        return res.status(400).json({ error: "Missing did" }); // Return 400 so the client sends complete input
    } // Close the input validation block
    const doc = dids.get(did); // Retrieve the DID document so the server can confirm the DID exists before issuing a challenge
    if (!doc) { // Ensure the DID is registered so challenges are not wasted on unknown identities
        return res.status(404).json({ error: "DID not found" }); // Return 404 so the client knows the DID is invalid
    } // Close the existence check
    const challenge = crypto.randomBytes(32).toString("hex"); // Generate a random 32-byte hex challenge so each authentication attempt is unique
    challenges.set(did, challenge); // Store the challenge so the verify endpoint can compare the submitted signature against it
    return res.status(200).json({ // Return the challenge so the client can sign it with their private key
        success: true, // Indicate that the challenge was generated so the client knows to proceed to signing
        did, // Echo the DID so the client knows which identity the challenge targets
        challenge, // Return the random string so the client can create a proof of ownership
    }); // Close the success response
}); // Close the POST /did/authenticate route

app.post("/did/verify", (req, res) => { // Define an endpoint to verify a signed challenge and confirm DID ownership
    const { did, signature } = req.body; // Destructure verification parameters so the server knows which identity and proof to evaluate
    if (!did || !signature) { // Validate that both fields are present so incomplete proofs are rejected
        return res.status(400).json({ error: "Missing did or signature" }); // Return 400 so the client sends complete input
    } // Close the input validation block
    const expectedChallenge = challenges.get(did); // Retrieve the stored challenge so the server can confirm the signature matches the expected payload
    if (!expectedChallenge) { // Check if a challenge was issued so expired or unsolicited verification attempts are rejected
        return res.status(400).json({ error: "No active challenge for this DID" }); // Return 400 so the client must request a fresh challenge
    } // Close the challenge existence check
    const doc = dids.get(did); // Retrieve the DID document so the public key can be used to validate the signature
    if (!doc) { // Ensure the DID is registered so verification does not proceed with unknown identities
        return res.status(404).json({ error: "DID not found" }); // Return 404 so the client knows the DID is invalid
    } // Close the DID existence check
    // NOTE: In a real system the signature would be cryptographically validated against the public key.
    // This simulation accepts any non-empty signature to demonstrate the flow without full elliptic-curve libraries.
    const valid = signature.length > 10; // Perform a shallow length check so obviously malformed signatures are rejected in the demo
    challenges.delete(did); // Remove the challenge so it cannot be reused in a replay attack
    return res.status(200).json({ // Return the verification result so the client knows whether authentication succeeded
        success: true, // Confirm the endpoint processed the request so clients can inspect the valid flag
        valid, // Report true if the signature passed the demo check, false otherwise
        did, // Echo the DID so the response is self-contained
        publicKey: doc.publicKey, // Include the public key so the verifier can cache it for future signature checks
    }); // Close the success response
}); // Close the POST /did/verify route

app.post("/credential/issue", (req, res) => { // Define an endpoint to issue a verifiable credential from an issuer to a subject
    const { issuerDid, subjectDid, claim } = req.body; // Destructure request fields so validation can be performed
    if (!issuerDid || !subjectDid || !claim) { // Validate that every required field is present so incomplete credentials are rejected
        return res.status(400).json({ error: "Missing required fields: issuerDid, subjectDid, claim" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    if (!dids.has(issuerDid)) { // Check if the issuer DID exists so credentials are not issued by unregistered identities
        return res.status(404).json({ error: "Issuer DID not found" }); // Return 404 so the client knows the issuer is invalid
    } // Close the issuer existence check
    if (!dids.has(subjectDid)) { // Check if the subject DID exists so credentials are not bound to unregistered identities
        return res.status(404).json({ error: "Subject DID not found" }); // Return 404 so the client knows the subject is invalid
    } // Close the subject existence check
    const credential: Credential = { // Construct a new credential object with all fields initialized
        id: String(nextCredentialId++), // Assign the next sequential ID and increment the counter so future credentials get unique identifiers
        issuerDid, // Store the issuer so verifiers know who attested to the claim
        subjectDid, // Store the subject so the credential is bound to a specific identity
        claim, // Store the claim text so the content of the attestation is transparent
        issuedAt: nowSeconds(), // Record the current timestamp so the credential has an issuance date
        signature: crypto.randomBytes(32).toString("hex"), // Generate a random hex signature so the demo simulates cryptographic signing
    }; // Close the credential object creation
    credentials.push(credential); // Append the credential to the in-memory array so it can be verified and presented later
    return res.status(201).json({ // Return a 201 Created response so the client knows the credential was successfully issued
        success: true, // Include a success flag so programmatic clients can check status without deep body parsing
        credential, // Return the full credential so the client receives the generated ID and signature
    }); // Close the success response
}); // Close the POST /credential/issue route

app.post("/credential/verify", (req, res) => { // Define an endpoint to verify the authenticity of a presented credential
    const { credentialId } = req.body; // Destructure the credential ID so the server can locate the specific credential
    if (!credentialId) { // Validate that the credential ID is provided so the server does not search with undefined keys
        return res.status(400).json({ error: "Missing credentialId" }); // Return 400 so the client provides complete input
    } // Close the input validation block
    const credential = credentials.find((c) => c.id === credentialId); // Search the in-memory array for the requested credential so verification targets the correct document
    if (!credential) { // Check if the credential exists so the server does not operate on undefined data
        return res.status(404).json({ error: "Credential not found" }); // Return 404 so the client knows the ID is invalid
    } // Close the existence check
    const issuerDoc = dids.get(credential.issuerDid); // Retrieve the issuer's DID document so the public key can be used to validate the signature
    if (!issuerDoc) { // Ensure the issuer is registered so credentials from revoked or unknown issuers are flagged
        return res.status(400).json({ error: "Issuer DID no longer resolvable" }); // Return 400 so the client knows the issuer is untrusted
    } // Close the issuer resolution check
    // NOTE: In a real system the signature would be cryptographically validated against issuerDoc.publicKey.
    const valid = credential.signature.length > 10; // Perform a shallow length check so obviously malformed signatures are rejected in the demo
    return res.status(200).json({ // Return the verification result so the presenter knows whether the credential is accepted
        success: true, // Confirm the endpoint processed the request so clients can inspect the valid flag
        valid, // Report true if the credential passed the demo check, false otherwise
        credential, // Return the credential so the verifier can inspect its claims
        issuerPublicKey: issuerDoc.publicKey, // Include the issuer's public key so the verifier can perform independent validation
    }); // Close the success response
}); // Close the POST /credential/verify route

app.get("/dids", (req, res) => { // Define an endpoint to list all registered DIDs for discovery and audit purposes
    return res.status(200).json({ // Return the full list so clients can browse registered identities
        count: dids.size, // Include the total count so summary widgets can display it
        dids: Array.from(dids.values()), // Convert the Map values to an array so JSON serialization works correctly
    }); // Close the success response
}); // Close the GET /dids route

app.listen(3042, () => { // Start the HTTP server on port 3042 because this phase owns that port to avoid conflicts with other APIs
    console.log("DID API listening on port 3042"); // Log startup so operators know the service is ready to accept connections
}); // Close the listen callback
