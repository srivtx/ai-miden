import express from "express"; // Import the express framework to build the HTTP server
import bodyParser from "body-parser"; // Import body-parser to parse JSON request bodies

const app = express(); // Create the express application instance
app.use(bodyParser.json()); // Attach middleware to parse incoming JSON request bodies

interface SoulboundToken { // Define the shape of a soulbound token record for type safety
    id: string; // Store a unique identifier so each token can be referenced individually
    issuer: string; // Store the address of the entity that minted and attests to this credential
    recipient: string; // Store the address that permanently owns this non-transferable token
    metadata: string; // Store a human-readable description or URI of what this token represents
    revoked: boolean; // Store whether the issuer has revoked this token due to fraud or error
}

let tokens: SoulboundToken[] = []; // Initialize an in-memory array to hold all issued soulbound tokens
let issuers: Set<string> = new Set(); // Initialize a set to track addresses authorized to mint new soulbound tokens

function isSoulbound(tokenId: string): boolean { // Determine whether a given token is non-transferable
    const token = tokens.find((t) => t.id === tokenId); // Search the array for a token matching the provided ID
    if (!token) { // Check if the token was found
        return false; // Return false because a nonexistent token has no transfer restrictions
    } // Close the not-found branch
    return true; // Return true because all tokens in this system are soulbound by design
} // Close the soulbound check helper

app.post("/issuer/register", (req, res) => { // Define endpoint to register a new authorized issuer
    const { address } = req.body; // Extract the issuer address from the request body
    if (!address) { // Validate that the address is provided
        return res.status(400).json({ error: "Address is required" }); // Return 400 if the address is missing
    } // Close the validation block
    issuers.add(address); // Add the address to the authorized issuer set
    return res.status(200).json({ // Return the registration confirmation to the client
        message: "Issuer registered", // Confirm that the address can now mint soulbound tokens
        address, // Echo the registered address
    }); // Close the success response
}); // Close the POST /issuer/register route

app.post("/token/mint", (req, res) => { // Define endpoint to mint a new soulbound token
    const { issuer, recipient, metadata } = req.body; // Extract minting parameters from the request body
    if (!issuer || !recipient || !metadata) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing issuer, recipient, or metadata" }); // Return 400 if input is incomplete
    } // Close the validation block
    if (!issuers.has(issuer)) { // Check if the sender is an authorized issuer
        return res.status(403).json({ error: "Unauthorized issuer" }); // Return 403 to prevent unauthorized minting
    } // Close the issuer authorization block
    const token: SoulboundToken = { // Build the soulbound token object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the token
        issuer, // Assign the issuer address from the request
        recipient, // Assign the recipient address from the request
        metadata, // Assign the metadata from the request
        revoked: false, // Mark the token as active at minting
    }; // Close the token object
    tokens.push(token); // Add the new token to the global in-memory array
    return res.status(201).json({ // Return the created token to the client
        message: "Soulbound token minted", // Confirm that the token was issued successfully
        token, // Include the full token details for client reference
    }); // Close the success response
}); // Close the POST /token/mint route

app.post("/token/transfer", (req, res) => { // Define endpoint to attempt a token transfer
    const { tokenId, from, to } = req.body; // Extract transfer parameters from the request body
    if (!tokenId || !from || !to) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing tokenId, from, or to" }); // Return 400 if input is incomplete
    } // Close the validation block
    if (isSoulbound(tokenId)) { // Check if the requested token is soulbound and therefore non-transferable
        return res.status(403).json({ // Return 403 to enforce the non-transferability rule
            error: "Transfer rejected: token is soulbound and non-transferable", // Explain why the transfer was blocked
            tokenId, // Echo the token ID for reference
        }); // Close the rejection response
    } // Close the soulbound check block
    return res.status(200).json({ // Return a hypothetical success if the token were transferable
        message: "Transfer would succeed if token were transferable", // Clarify that this path is not used for SBTs
        tokenId, // Echo the token ID
        from, // Echo the sender address
        to, // Echo the recipient address
    }); // Close the success response
}); // Close the POST /token/transfer route

app.post("/token/revoke", (req, res) => { // Define endpoint to revoke an existing soulbound token
    const { tokenId, issuer } = req.body; // Extract revocation parameters from the request body
    if (!tokenId || !issuer) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing tokenId or issuer" }); // Return 400 if input is incomplete
    } // Close the validation block
    const token = tokens.find((t) => t.id === tokenId); // Search the array for a token matching the provided ID
    if (!token) { // Check if the token was found
        return res.status(404).json({ error: "Token not found" }); // Return 404 if the token ID does not exist
    } // Close the not-found branch
    if (token.issuer !== issuer) { // Check if the requesting address is the original issuer
        return res.status(403).json({ error: "Only the original issuer can revoke this token" }); // Return 403 to enforce issuer authority
    } // Close the issuer match block
    token.revoked = true; // Mark the token as revoked to invalidate its credential status
    return res.status(200).json({ // Return the revocation confirmation to the client
        message: "Token revoked", // Confirm that the token was successfully revoked
        token, // Include the updated token details
    }); // Close the success response
}); // Close the POST /token/revoke route

app.get("/wallet/:address/tokens", (req, res) => { // Define endpoint to fetch all tokens owned by a specific wallet
    const address = req.params.address; // Extract the wallet address from the URL parameter
    const walletTokens = tokens.filter((t) => t.recipient === address && !t.revoked); // Filter for active tokens bound to this address
    return res.status(200).json({ // Return the wallet's token holdings to the client
        address, // Echo the wallet address
        tokenCount: walletTokens.length, // Return the count of active soulbound tokens
        tokens: walletTokens, // Return the array of active token records
    }); // Close the success response
}); // Close the GET /wallet/:address/tokens route

app.get("/wallet/:address/reputation", (req, res) => { // Define endpoint to compute a composite reputation score
    const address = req.params.address; // Extract the wallet address from the URL parameter
    const walletTokens = tokens.filter((t) => t.recipient === address && !t.revoked); // Filter for active tokens bound to this address
    let score = 0; // Initialize the reputation score to zero
    for (const token of walletTokens) { // Iterate over each token to accumulate reputation points
        if (token.metadata.toLowerCase().includes("governance")) { // Check if the token represents governance participation
            score += 20; // Add 20 points for governance credentials because they signal long-term commitment
        } else if (token.metadata.toLowerCase().includes("security")) { // Check if the token represents a security contribution
            score += 25; // Add 25 points for security credentials because they indicate technical expertise
        } else if (token.metadata.toLowerCase().includes("early")) { // Check if the token represents early participation
            score += 15; // Add 15 points for early contribution because it signals founder-level alignment
        } else { // Handle generic tokens that do not match specific categories
            score += 5; // Add 5 points for any other verified credential to encourage broad participation
        } // Close the category branch
    } // Close the token loop
    return res.status(200).json({ // Return the computed reputation data to the client
        address, // Echo the wallet address
        reputationScore: score, // Return the total computed reputation score
        tokenCount: walletTokens.length, // Return the number of active credentials
        tokens: walletTokens.map((t) => ({ id: t.id, metadata: t.metadata })), // Return a summary of each credential
    }); // Close the success response
}); // Close the GET /wallet/:address/reputation route

app.get("/token/:id/verify", (req, res) => { // Define endpoint to verify whether a specific token is valid and active
    const token = tokens.find((t) => t.id === req.params.id); // Search the array for a token matching the URL ID
    if (!token) { // Check if the token was found
        return res.status(404).json({ error: "Token not found" }); // Return 404 if the token ID does not exist
    } // Close the not-found branch
    return res.status(200).json({ // Return the verification result to the client
        tokenId: token.id, // Echo the token ID
        valid: !token.revoked, // Report true if the token is active and false if it was revoked
        issuer: token.issuer, // Include the issuer for trust evaluation
        recipient: token.recipient, // Include the bound recipient address
        metadata: token.metadata, // Include the credential description
    }); // Close the success response
}); // Close the GET /token/:id/verify route

app.listen(3049, () => { // Start the HTTP server on port 3049
    console.log("SBT API listening on port 3049"); // Log startup so operators know the service is ready
}); // Close the listen callback
