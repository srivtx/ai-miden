import express from "express"; // Import the express framework to build the HTTP server
import { Connection, PublicKey } from "@solana/web3.js"; // Import Solana web3 utilities for chain interaction
import { Proposal, VoteRecord } from "./types"; // Import local type definitions for governance structures

const app = express(); // Create the express application instance that will handle all routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects

const connection = new Connection("http://localhost:8899", "confirmed"); // Initialize a connection to the local validator for development
const GOVERNANCE_PROGRAM_ID = new PublicKey("Gov1..."); // Define the on-chain governance program address for deriving accounts

app.post("/proposals", async (req, res) => { // Define the endpoint for clients to submit new governance proposals
    const { proposer, descriptionHash } = req.body; // Destructure the request body to extract proposal parameters
    if (!proposer || !descriptionHash) { // Validate that both required fields were provided by the client
        return res.status(400).json({ error: "Missing proposer or descriptionHash" }); // Return 400 if inputs are incomplete
    } // Close the input validation block
    try { // Start a try block to catch chain errors and send graceful HTTP responses
        const proposalAccount = PublicKey.createWithSeed( // Derive a deterministic account address from the proposer and hash
            new PublicKey(proposer), // Use the proposer's public key as the base for seed generation
            descriptionHash, // Use the description hash as the seed string to make the address unique per proposal
            GOVERNANCE_PROGRAM_ID, // Bind the derived address to the governance program so only it can own it
        ); // Close the createWithSeed call
        const instructionData = Buffer.alloc(33); // Allocate a 33-byte buffer for the instruction discriminator plus hash
        instructionData.writeUInt8(0, 0); // Write instruction discriminator 0 to route to create_proposal on-chain
        Buffer.from(descriptionHash, "hex").copy(instructionData, 1); // Copy the 32-byte hash into the buffer after discriminator
        return res.status(200).json({ // Return success to the client with the derived account address
            proposalAccount: proposalAccount.toBase58(), // Encode the address in base58 for standard Solana display
            instructionData: instructionData.toString("base64"), // Encode the serialized instruction for wallet signing
        }); // Close the success response
    } catch (err) { // Catch any errors thrown during public key derivation or buffer operations
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message for debugging
    } // Close the catch block
}); // Close the POST /proposals route

app.post("/proposals/:address/votes", async (req, res) => { // Define the endpoint for casting votes on a specific proposal
    const proposalAddress = req.params.address; // Extract the proposal account address from the URL path parameter
    const { voter, amount, side } = req.body; // Destructure vote details from the request body
    if (!voter || !amount || side === undefined) { // Validate that all vote fields are present to prevent malformed transactions
        return res.status(400).json({ error: "Missing voter, amount, or side" }); // Return 400 if any field is missing
    } // Close the input validation block
    try { // Start a try block to handle serialization and response errors gracefully
        const instructionData = Buffer.alloc(10); // Allocate 10 bytes for discriminator, side byte, and 8-byte amount
        instructionData.writeUInt8(1, 0); // Write instruction discriminator 1 to route to cast_vote on-chain
        instructionData.writeUInt8(side ? 1 : 0, 1); // Write 1 for yes or 0 for no at the second byte
        instructionData.writeBigUInt64LE(BigInt(amount), 2); // Write the 64-bit vote amount in little-endian at bytes 2-9
        return res.status(200).json({ // Return the serialized transaction data to the client for signing
            proposalAddress, // Echo the proposal address so the client knows which account to include
            voter, // Echo the voter address for client-side verification
            instructionData: instructionData.toString("base64"), // Encode the instruction payload for wallet transmission
        }); // Close the success response
    } catch (err) { // Catch any unexpected errors during buffer operations
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /votes route

app.post("/proposals/:address/execute", async (req, res) => { // Define the endpoint to trigger proposal execution after timelock
    const proposalAddress = req.params.address; // Extract the proposal address from the URL path parameter
    const { executor } = req.body; // Extract the executor's public key from the request body
    if (!executor) { // Validate that the executor field is provided since execution requires a signer
        return res.status(400).json({ error: "Missing executor" }); // Return 400 if the executor is absent
    } // Close the input validation block
    try { // Start a try block to handle any runtime errors during execution preparation
        const instructionData = Buffer.alloc(1); // Allocate 1 byte because execution only needs the discriminator
        instructionData.writeUInt8(2, 0); // Write instruction discriminator 2 to route to execute_proposal on-chain
        return res.status(200).json({ // Return the serialized execution payload to the client
            proposalAddress, // Echo the proposal address for the transaction
            executor, // Echo the executor address so the client includes it as a signer
            instructionData: instructionData.toString("base64"), // Encode the instruction for wallet signing
        }); // Close the success response
    } catch (err) { // Catch any unexpected errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /execute route

app.get("/proposals/:address", async (req, res) => { // Define the endpoint to fetch on-chain proposal state
    const proposalAddress = req.params.address; // Extract the proposal address from the URL path parameter
    try { // Start a try block to handle account fetch failures gracefully
        const accountInfo = await connection.getAccountInfo(new PublicKey(proposalAddress)); // Fetch raw account data from the chain
        if (!accountInfo) { // Check if the account exists to avoid deserialization errors on null data
            return res.status(404).json({ error: "Proposal not found" }); // Return 404 if the account does not exist
        } // Close the existence check
        const proposal = Proposal.deserialize(accountInfo.data); // Deserialize the raw bytes into a typed Proposal object
        return res.status(200).json({ // Return the proposal state to the client
            proposer: proposal.proposer.toBase58(), // Convert the proposer public key to base58 string
            forVotes: proposal.for_votes.toString(), // Convert the yes tally to string to avoid JavaScript number overflow
            againstVotes: proposal.against_votes.toString(), // Convert the no tally to string for safety
            startSlot: proposal.start_slot, // Return the voting start slot for client-side countdowns
            endSlot: proposal.end_slot, // Return the voting end slot for client-side countdowns
            eta: proposal.eta, // Return the earliest execution time so users know the timelock deadline
            executed: proposal.executed, // Return whether the proposal has already been executed
            canceled: proposal.canceled, // Return whether the proposal was canceled
        }); // Close the success response
    } catch (err) { // Catch errors from connection failures or deserialization issues
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the GET /proposals/:address route

app.listen(3000, () => { // Start the HTTP server and bind it to port 3000 for incoming requests
    console.log("Governance API listening on port 3000"); // Log startup so operators know the service is ready
}); // Close the listen callback
