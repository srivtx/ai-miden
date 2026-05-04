import express from "express"; // Import the express framework to build the HTTP server
import { exec } from "child_process"; // Import child_process to run shell commands from the Node.js process
import { promisify } from "util"; // Import promisify to convert callback-based exec into a promise-based function
import { Connection, PublicKey } from "@solana/web3.js"; // Import Solana utilities for blockchain interaction

const app = express(); // Create the express application instance
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies

const execAsync = promisify(exec); // Create an async version of exec to use with await in route handlers
const connection = new Connection("https://api.devnet.solana.com", "confirmed"); // Initialize connection to devnet RPC

interface DeploymentRecord { // Define a TypeScript interface for in-memory deployment tracking
    programName: string; // Store the human-readable name of the deployed program
    programId: string; // Store the on-chain program address in base58 format
    environment: string; // Store the cluster where the program is deployed
    buildHash: string; // Store the SHA-256 hash of the compiled binary for verification reference
    deployedAt: string; // Store the ISO timestamp of when the deployment occurred
    verified: boolean; // Flag whether the build has been cryptographically verified against on-chain data
} // Close the DeploymentRecord interface

const deployments: DeploymentRecord[] = []; // Initialize an in-memory array to track deployment history

app.post("/deploy", async (req, res) => { // Define endpoint to trigger a deployment pipeline run
    const { programName, environment } = req.body; // Destructure deployment parameters from the request body
    if (!programName || !environment) { // Validate that both program name and target environment are provided
        return res.status(400).json({ error: "Missing programName or environment" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to catch pipeline execution errors
        const { stdout, stderr } = await execAsync( // Execute the deployment pipeline script asynchronously
            `bash src_web3/phase35/deploy_pipeline.sh ${programName} ${environment}` // Build the shell command with user inputs
        ); // Close the execAsync call
        const buildHashMatch = stdout.match(/Build hash: ([a-f0-9]{64})/); // Use regex to extract the build hash from script output
        const buildHash = buildHashMatch ? buildHashMatch[1] : "unknown"; // Use the matched hash or default to unknown
        const deployment: DeploymentRecord = { // Create a new deployment record for tracking
            programName, // Store the program name from the request
            programId: "Pending", // Initialize program id as pending because the script may not return it directly
            environment, // Store the target environment from the request
            buildHash, // Store the extracted build hash for later verification
            deployedAt: new Date().toISOString(), // Record the current timestamp in ISO format
            verified: false, // Mark as unverified until an explicit verification step is run
        }; // Close the deployment record creation
        deployments.push(deployment); // Append the record to the in-memory history
        return res.status(200).json({ // Return the deployment result to the client
            success: true, // Indicate that the pipeline completed without throwing
            output: stdout, // Include the full standard output for operator inspection
            errors: stderr || null, // Include standard error if present, otherwise null
            deployment, // Return the structured deployment record
        }); // Close the success response
    } catch (err) { // Catch pipeline failures, timeouts, or script errors
        return res.status(500).json({ // Return 500 to signal a server-side pipeline failure
            success: false, // Indicate that the deployment did not complete successfully
            error: (err as Error).message, // Include the error message for debugging
        }); // Close the error response
    } // Close the catch block
}); // Close the POST /deploy route

app.post("/verify", async (req, res) => { // Define endpoint to run a verified build check against on-chain data
    const { programId, buildPath, cluster } = req.body; // Destructure verification parameters from the request body
    if (!programId) { // Validate that the program id is provided since verification requires an on-chain target
        return res.status(400).json({ error: "Missing programId" }); // Return 400 for incomplete input
    } // Close the input validation block
    try { // Start a try block to catch verification script errors
        const { stdout, stderr } = await execAsync( // Execute the verification script asynchronously
            `bash src_web3/phase35/verify_build.sh ${programId} ${buildPath || "target/verifiable/"} ${cluster || "mainnet"}` // Build command
        ); // Close the execAsync call
        const passed = stdout.includes("VERIFICATION PASSED"); // Determine success by scanning the script output for the pass string
        const record = deployments.find((d) => d.programId === programId); // Search for an existing deployment record
        if (record) { // If a matching deployment record exists
            record.verified = passed; // Update the verified flag based on the script result
        } // Close the record update block
        return res.status(200).json({ // Return the verification result to the client
            passed, // Report true if the hash matched, false otherwise
            output: stdout, // Include the full script output for transparency
            errors: stderr || null, // Include standard error if present
        }); // Close the success response
    } catch (err) { // Catch verification failures or script errors
        return res.status(500).json({ // Return 500 to signal a verification execution failure
            passed: false, // Report failure because the script could not complete
            error: (err as Error).message, // Include the error message for debugging
        }); // Close the error response
    } // Close the catch block
}); // Close the POST /verify route

app.get("/deployments", async (req, res) => { // Define endpoint to list all tracked deployments
    return res.status(200).json({ // Return the deployment history
        count: deployments.length, // Include the total number of tracked deployments
        deployments, // Return the full array of deployment records
    }); // Close the success response
}); // Close the GET /deployments route

app.get("/deployments/:programName", async (req, res) => { // Define endpoint to fetch deployments for a specific program
    const programName = req.params.programName; // Extract the program name from the URL path parameter
    const filtered = deployments.filter((d) => d.programName === programName); // Filter the history by program name
    return res.status(200).json({ // Return the filtered results
        programName, // Echo the requested program name
        count: filtered.length, // Include how many deployments match the name
        deployments: filtered, // Return the matching deployment records
    }); // Close the success response
}); // Close the GET /deployments/:programName route

app.get("/account/:address", async (req, res) => { // Define endpoint to inspect an on-chain account
    const address = req.params.address; // Extract the account address from the URL path parameter
    try { // Start a try block to handle chain fetch errors
        const accountInfo = await connection.getAccountInfo(new PublicKey(address)); // Fetch raw account data
        if (!accountInfo) { // Check if the account exists
            return res.status(404).json({ error: "Account not found" }); // Return 404 if the address is empty
        } // Close the existence check
        return res.status(200).json({ // Return the account metadata
            address, // Echo the requested address
            executable: accountInfo.executable, // Report whether the account contains a program
            owner: accountInfo.owner.toBase58(), // Return the program owner in base58
            lamports: accountInfo.lamports, // Return the SOL balance in lamports
            dataLength: accountInfo.data.length, // Report the data size for rent estimation
        }); // Close the success response
    } catch (err) { // Catch connection or public key errors
        return res.status(500).json({ error: (err as Error).message }); // Return 500 with the error message
    } // Close the catch block
}); // Close the GET /account/:address route

app.listen(3004, () => { // Start the HTTP server on port 3004
    console.log("Deployment API listening on port 3004"); // Log startup so operators know the service is ready
}); // Close the listen callback
