import express from "express"; // Import the express framework to build the HTTP server
import { Connection, PublicKey } from "@solana/web3.js"; // Import Solana utilities for blockchain interaction
import crypto from "crypto"; // Import Node.js crypto module for hashing leaf data

const app = express(); // Create the express application instance
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies

const connection = new Connection("http://localhost:8899", "confirmed"); // Initialize connection to the local validator
const COMPRESSION_PROGRAM_ID = new PublicKey("Comp..."); // Define the compression program address

app.post("/tree/proof", async (req, res) => { // Define endpoint to generate a Merkle proof for a given leaf
    const { leaf, siblings } = req.body; // Destructure the leaf hash and sibling path from the request body
    if (!leaf || !siblings || !Array.isArray(siblings)) { // Validate that leaf and siblings array are provided
        return res.status(400).json({ error: "Missing leaf or siblings array" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to handle hashing errors gracefully
        let current = Buffer.from(leaf, "hex"); // Convert the hex leaf string into a buffer for hashing
        for (const sibling of siblings) { // Iterate over each sibling in the proof path
            const siblingBuf = Buffer.from(sibling, "hex"); // Convert the sibling hex string to a buffer
            const combined = current.compare(siblingBuf) < 0 // Enforce consistent lexicographic ordering
                ? Buffer.concat([current, siblingBuf]) // Concatenate current before sibling if smaller
                : Buffer.concat([siblingBuf, current]); // Otherwise concatenate sibling before current
            current = crypto.createHash("sha256").update(combined).digest(); // Compute SHA-256 parent hash
        } // Close the sibling iteration loop
        return res.status(200).json({ // Return the computed proof root to the client
            leaf, // Echo the leaf hash for verification
            siblingsCount: siblings.length, // Include the proof depth for client reference
            computedRoot: current.toString("hex"), // Return the root as a hex string for comparison
        }); // Close the success response
    } catch (err) { // Catch buffer parsing or hashing errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /tree/proof route

app.post("/tree/leaf", async (req, res) => { // Define endpoint to compute a leaf hash from NFT metadata
    const { owner, assetId, metadata } = req.body; // Destructure NFT parameters from the request body
    if (!owner || !assetId || !metadata) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing owner, assetId, or metadata" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to handle hashing errors
        const ownerBuf = new PublicKey(owner).toBuffer(); // Convert the owner string to a 32-byte public key buffer
        const assetBuf = Buffer.from(assetId, "hex"); // Convert the asset identifier hex string to a buffer
        const metaHash = crypto.createHash("sha256").update(JSON.stringify(metadata)).digest(); // Hash the metadata
        const leafInput = Buffer.concat([ownerBuf, assetBuf, metaHash]); // Concatenate all fields into one buffer
        const leafHash = crypto.createHash("sha256").update(leafInput).digest(); // Compute the final leaf hash
        return res.status(200).json({ // Return the leaf hash and components to the client
            owner, // Echo the owner address
            assetId, // Echo the asset identifier
            metadataHash: metaHash.toString("hex"), // Return the metadata hash for independent verification
            leafHash: leafHash.toString("hex"), // Return the computed leaf hash for tree insertion
        }); // Close the success response
    } catch (err) { // Catch public key parsing or hashing errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /tree/leaf route

app.post("/tree/mint", async (req, res) => { // Define endpoint to build a compressed NFT mint transaction
    const { tree, leaf, proof } = req.body; // Destructure mint parameters from the request body
    if (!tree || !leaf || !proof) { // Validate that tree address, leaf, and proof are provided
        return res.status(400).json({ error: "Missing tree, leaf, or proof" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to handle serialization errors
        const leafBuf = Buffer.from(leaf, "hex"); // Convert the leaf hex string to a buffer
        const proofBuf = Buffer.concat(proof.map((s: string) => Buffer.from(s, "hex"))); // Concatenate all proof siblings
        const instructionData = Buffer.alloc(1 + leafBuf.length + proofBuf.length); // Allocate payload with exact size
        instructionData.writeUInt8(0, 0); // Write instruction discriminator 0 for verify_proof
        leafBuf.copy(instructionData, 1); // Copy the leaf hash into the payload after the discriminator
        proofBuf.copy(instructionData, 1 + leafBuf.length); // Copy the proof path after the leaf hash
        return res.status(200).json({ // Return the serialized instruction to the client
            tree, // Echo the tree account address
            instructionData: instructionData.toString("base64"), // Encode the payload for wallet signing
            instructionSize: instructionData.length, // Include the byte size for debugging
        }); // Close the success response
    } catch (err) { // Catch buffer or encoding errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the POST /tree/mint route

app.get("/tree/:address", async (req, res) => { // Define endpoint to fetch the current state of a Merkle tree
    const treeAddress = req.params.address; // Extract the tree account address from the URL path parameter
    try { // Start a try block to handle account fetch errors
        const accountInfo = await connection.getAccountInfo(new PublicKey(treeAddress)); // Fetch on-chain tree data
        if (!accountInfo) { // Check if the tree account exists
            return res.status(404).json({ error: "Tree not found" }); // Return 404 if the account is missing
        } // Close the existence check
        return res.status(200).json({ // Return the raw account data length for basic inspection
            address: treeAddress, // Echo the requested address
            dataLength: accountInfo.data.length, // Report the account size to estimate rent costs
            owner: accountInfo.owner.toBase58(), // Return the program owner for verification
        }); // Close the success response
    } catch (err) { // Catch connection or public key errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the GET /tree/:address route

app.listen(3003, () => { // Start the HTTP server on port 3003
    console.log("Compression API listening on port 3003"); // Log startup so operators know the service is ready
}); // Close the listen callback
