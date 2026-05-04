import express from "express"; // Import Express to create an HTTP server that clients use to interact with the DAO.
import { Connection, PublicKey, Transaction, SystemProgram, sendAndConfirmTransaction, Keypair } from "@solana/web3.js"; // Import Solana web3.js classes so the API can construct and submit on-chain transactions.
import * as fs from "fs"; // Import the filesystem module so the API can read local keypair files for signing.
import * as path from "path"; // Import path utilities so keypair file resolution works across operating systems.

const app = express(); // Create the Express application instance that will handle all HTTP routes.
app.use(express.json()); // Enable JSON body parsing so POST routes can read structured request payloads.

const PORT = 3058; // Assign port 3058 so the DAO API does not conflict with other services running on standard ports.
const connection = new Connection("http://127.0.0.1:8899", "confirmed"); // Connect to the local Solana validator so transactions are fast and free during development.

const GOVERNANCE_PROGRAM_ID = new PublicKey("Gov1111111111111111111111111111111111111111"); // Define the governance program address so instructions are routed to the correct on-chain program.
const TREASURY_PROGRAM_ID = new PublicKey("Treas11111111111111111111111111111111111111"); // Define the treasury program address so deposit and withdrawal instructions target the correct program.

function loadKeypair(filePath: string): Keypair { // Define a helper so the API can load signing keys from JSON files securely.
    const secretKey = JSON.parse(fs.readFileSync(filePath, "utf-8")); // Read the secret key array from disk and parse it into a JavaScript array.
    return Keypair.fromSecretKey(new Uint8Array(secretKey)); // Convert the array into a Solana Keypair so it can sign transactions.
}

const payer = loadKeypair(path.join(__dirname, "payer.json")); // Load the default payer keypair so the API has a funded account to submit transactions.

app.post("/proposal", async (req, res) => { // Register the POST /proposal route so clients can create new governance proposals.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { title, description, endSlot, quorum, passThreshold } = req.body; // Destructure the request body so required fields are extracted.
        if (!title || !description || !endSlot || !quorum || !passThreshold) { // Validate that all required fields are present so malformed requests are rejected early.
            return res.status(400).json({ error: "Missing required proposal fields" }); // Return 400 so the client knows the request was incomplete.
        }
        const proposalKeypair = Keypair.generate(); // Generate a new keypair so the proposal has a unique on-chain address.
        const instruction = { // Build the raw instruction object so the transaction targets the governance program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: payer.publicKey, isSigner: true, isWritable: false }, // Mark the payer as a signer because they pay for account creation.
                { pubkey: proposalKeypair.publicKey, isSigner: true, isWritable: true }, // Mark the proposal account as writable because it will store the new state.
            ],
            programId: GOVERNANCE_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the governance program.
            data: Buffer.from([0, ...Buffer.from(title), ...Buffer.from(description), ...new Uint8Array(new BigUint64Array([BigInt(endSlot)]).buffer), ...new Uint8Array(new BigUint64Array([BigInt(quorum)]).buffer), ...new Uint8Array(new BigUint64Array([BigInt(passThreshold)]).buffer)]), // Serialize the instruction data so the program can deserialize it into a CreateProposal variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [payer, proposalKeypair]); // Submit the transaction to the local validator and wait for confirmation so the client knows the proposal exists.
        return res.json({ proposalId: proposalKeypair.publicKey.toBase58(), status: "created" }); // Return the proposal address so the client can reference it later.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/vote", async (req, res) => { // Register the POST /vote route so clients can cast weighted ballots.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { proposalId, voteFor, voterSecretKey } = req.body; // Destructure the request body so vote parameters are extracted.
        if (!proposalId || voteFor === undefined) { // Validate that proposalId and voteFor are present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing proposalId or voteFor" }); // Return 400 so the client knows the request was incomplete.
        }
        const voter = voterSecretKey ? Keypair.fromSecretKey(new Uint8Array(voterSecretKey)) : payer; // Use the provided voter key or fall back to the payer so the API supports both authenticated and demo voting.
        const proposalPubkey = new PublicKey(proposalId); // Convert the string proposalId into a PublicKey so the instruction can reference the account.
        const voteRecordKeypair = Keypair.generate(); // Generate a new keypair so the vote record has a unique on-chain address and cannot be overwritten.
        const instruction = { // Build the raw instruction object so the transaction targets the governance program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: voter.publicKey, isSigner: true, isWritable: false }, // Mark the voter as a signer because they must authorize their own ballot.
                { pubkey: proposalPubkey, isSigner: false, isWritable: true }, // Mark the proposal as writable because its vote tally will be updated.
                { pubkey: voteRecordKeypair.publicKey, isSigner: true, isWritable: true }, // Mark the vote record as writable because it will store the ballot.
                { pubkey: voter.publicKey, isSigner: false, isWritable: false }, // Include the voter again as a non-signer so the program can read their token balance.
            ],
            programId: GOVERNANCE_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the governance program.
            data: Buffer.from([1, ...new Uint8Array(new BigUint64Array([BigInt(proposalId)]).buffer), voteFor ? 1 : 0]), // Serialize the instruction data so the program can deserialize it into a Vote variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [voter, voteRecordKeypair]); // Submit the transaction to the local validator and wait for confirmation so the vote is recorded.
        return res.json({ voteRecord: voteRecordKeypair.publicKey.toBase58(), voteFor }); // Return the vote record address so the client can prove participation.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/delegate", async (req, res) => { // Register the POST /delegate route so token holders can assign voting power.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { delegateTo, ownerSecretKey } = req.body; // Destructure the request body so delegation parameters are extracted.
        if (!delegateTo) { // Validate that the delegate address is present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing delegateTo address" }); // Return 400 so the client knows the request was incomplete.
        }
        const owner = ownerSecretKey ? Keypair.fromSecretKey(new Uint8Array(ownerSecretKey)) : payer; // Use the provided owner key or fall back to the payer so the API supports both authenticated and demo delegation.
        const delegatePubkey = new PublicKey(delegateTo); // Convert the string address into a PublicKey so the instruction can reference the delegate account.
        const recordKeypair = Keypair.generate(); // Generate a new keypair so the delegation record has a unique on-chain address.
        const instruction = { // Build the raw instruction object so the transaction targets the governance program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: owner.publicKey, isSigner: true, isWritable: false }, // Mark the owner as a signer because only the owner can delegate their power.
                { pubkey: recordKeypair.publicKey, isSigner: true, isWritable: true }, // Mark the record as writable because it will store the delegation state.
                { pubkey: owner.publicKey, isSigner: false, isWritable: false }, // Include the owner again so the program can read their token balance.
            ],
            programId: GOVERNANCE_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the governance program.
            data: Buffer.from([2, ...delegatePubkey.toBytes()]), // Serialize the instruction data so the program can deserialize it into a Delegate variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [owner, recordKeypair]); // Submit the transaction to the local validator and wait for confirmation so the delegation is recorded.
        return res.json({ delegateRecord: recordKeypair.publicKey.toBase58(), delegateTo }); // Return the record address so the client can reference it later.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/undelegate", async (req, res) => { // Register the POST /undelegate route so token holders can reclaim voting power.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { recordId, ownerSecretKey } = req.body; // Destructure the request body so undelegation parameters are extracted.
        if (!recordId) { // Validate that the record ID is present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing recordId" }); // Return 400 so the client knows the request was incomplete.
        }
        const owner = ownerSecretKey ? Keypair.fromSecretKey(new Uint8Array(ownerSecretKey)) : payer; // Use the provided owner key or fall back to the payer so the API supports both authenticated and demo undelegation.
        const recordPubkey = new PublicKey(recordId); // Convert the string recordId into a PublicKey so the instruction can reference the account.
        const instruction = { // Build the raw instruction object so the transaction targets the governance program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: owner.publicKey, isSigner: true, isWritable: false }, // Mark the owner as a signer because only the owner can revoke delegation.
                { pubkey: recordPubkey, isSigner: false, isWritable: true }, // Mark the record as writable because its delegation state will be cleared.
            ],
            programId: GOVERNANCE_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the governance program.
            data: Buffer.from([3]), // Serialize the instruction data so the program can deserialize it into an Undelegate variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [owner]); // Submit the transaction to the local validator and wait for confirmation so the undelegation is recorded.
        return res.json({ recordId, status: "undelegated" }); // Return confirmation so the client knows the delegation is revoked.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.get("/proposals", async (_req, res) => { // Register the GET /proposals route so clients can list all governance proposals.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const accounts = await connection.getProgramAccounts(GOVERNANCE_PROGRAM_ID); // Query the local validator for all accounts owned by the governance program so the client sees every proposal.
        const proposals = accounts.map(({ pubkey, account }) => ({ // Map over the results so each entry is formatted for JSON consumption.
            address: pubkey.toBase58(), // Convert the public key to a base58 string so clients can reference proposals by readable IDs.
            data: account.data.toString("base64"), // Encode the raw account data as base64 so clients can deserialize it if needed.
        }));
        return res.json({ proposals }); // Return the array so the client can render a proposal list.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.get("/proposal/:id", async (req, res) => { // Register the GET /proposal/:id route so clients can fetch a single proposal.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { id } = req.params; // Extract the route parameter so we know which proposal to look up.
        const pubkey = new PublicKey(id); // Convert the string ID into a PublicKey so the RPC can fetch the account.
        const account = await connection.getAccountInfo(pubkey); // Query the local validator for the account so we can return its state.
        if (!account) { // Check if the account exists so we can return a proper 404 instead of null data.
            return res.status(404).json({ error: "Proposal not found" }); // Return 404 so the client knows the ID is invalid.
        }
        return res.json({ address: id, data: account.data.toString("base64"), owner: account.owner.toBase58() }); // Return the account data so the client can inspect the proposal.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/execute", async (req, res) => { // Register the POST /execute route so clients can trigger proposal execution after the timelock.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { proposalId } = req.body; // Destructure the request body so the proposal identifier is extracted.
        if (!proposalId) { // Validate that the proposal ID is present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing proposalId" }); // Return 400 so the client knows the request was incomplete.
        }
        const proposalPubkey = new PublicKey(proposalId); // Convert the string ID into a PublicKey so the instruction can reference the account.
        const instruction = { // Build the raw instruction object so the transaction targets the governance program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: payer.publicKey, isSigner: true, isWritable: false }, // Mark the payer as a signer because they must authorize the execution transaction.
                { pubkey: proposalPubkey, isSigner: false, isWritable: true }, // Mark the proposal as writable because its status will change to Executed.
            ],
            programId: GOVERNANCE_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the governance program.
            data: Buffer.from([5, ...new Uint8Array(new BigUint64Array([BigInt(proposalId)]).buffer)]), // Serialize the instruction data so the program can deserialize it into an ExecuteProposal variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [payer]); // Submit the transaction to the local validator and wait for confirmation so the proposal is finalized.
        return res.json({ proposalId, status: "executed" }); // Return confirmation so the client knows the proposal is complete.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/treasury/deposit", async (req, res) => { // Register the POST /treasury/deposit route so clients can fund the DAO treasury.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { amount, depositorSecretKey } = req.body; // Destructure the request body so deposit parameters are extracted.
        if (!amount) { // Validate that the amount is present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing amount" }); // Return 400 so the client knows the request was incomplete.
        }
        const depositor = depositorSecretKey ? Keypair.fromSecretKey(new Uint8Array(depositorSecretKey)) : payer; // Use the provided depositor key or fall back to the payer so the API supports both authenticated and demo deposits.
        const vaultKeypair = Keypair.generate(); // Generate a new keypair so the vault account is unique and program-derived in production.
        const instruction = { // Build the raw instruction object so the transaction targets the treasury program.
            keys: [ // Define the accounts that the instruction requires so the runtime can validate them.
                { pubkey: depositor.publicKey, isSigner: true, isWritable: true }, // Mark the depositor as writable because their balance will decrease.
                { pubkey: vaultKeypair.publicKey, isSigner: true, isWritable: true }, // Mark the vault as writable because its balance will increase.
            ],
            programId: TREASURY_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the treasury program.
            data: Buffer.from([0, ...new Uint8Array(new BigUint64Array([BigInt(amount)]).buffer)]), // Serialize the instruction data so the program can deserialize it into a Deposit variant.
        };
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [depositor, vaultKeypair]); // Submit the transaction to the local validator and wait for confirmation so the deposit is recorded.
        return res.json({ vault: vaultKeypair.publicKey.toBase58(), amount, status: "deposited" }); // Return the vault address so the client can reference it later.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.post("/treasury/withdraw", async (req, res) => { // Register the POST /treasury/withdraw route so approved proposals can release funds.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { amount, vaultId, recipient, signers } = req.body; // Destructure the request body so withdrawal parameters are extracted.
        if (!amount || !vaultId || !recipient) { // Validate that required fields are present so incomplete requests are rejected.
            return res.status(400).json({ error: "Missing amount, vaultId, or recipient" }); // Return 400 so the client knows the request was incomplete.
        }
        const vaultPubkey = new PublicKey(vaultId); // Convert the string vaultId into a PublicKey so the instruction can reference the vault.
        const recipientPubkey = new PublicKey(recipient); // Convert the string recipient into a PublicKey so the instruction can route funds.
        const keys = [ // Initialize the accounts array so we can append dynamic signers later.
            { pubkey: GOVERNANCE_PROGRAM_ID, isSigner: false, isWritable: false }, // Include the governance program so the treasury can verify the caller.
            { pubkey: payer.publicKey, isSigner: false, isWritable: false }, // Include the config reference so the treasury can read spending limits.
            { pubkey: vaultPubkey, isSigner: false, isWritable: true }, // Mark the vault as writable because its balance will decrease.
            { pubkey: recipientPubkey, isSigner: false, isWritable: true }, // Mark the recipient as writable because their balance will increase.
            { pubkey: payer.publicKey, isSigner: false, isWritable: true }, // Include a record account placeholder so the treasury can prevent replays.
        ];
        if (signers && Array.isArray(signers)) { // Check if additional multi-sig signers were provided so the threshold can be met.
            for (const s of signers) { // Iterate over each signer so they can be added to the instruction.
                keys.push({ pubkey: new PublicKey(s), isSigner: true, isWritable: false }); // Add each signer with isSigner true so the runtime validates their signatures.
            }
        }
        const instruction = { // Build the raw instruction object so the transaction targets the treasury program.
            keys, // Pass the assembled accounts array so the program receives all required addresses.
            programId: TREASURY_PROGRAM_ID, // Set the program ID so the runtime routes the instruction to the treasury program.
            data: Buffer.from([1, ...new Uint8Array(new BigUint64Array([BigInt(amount)]).buffer)]), // Serialize the instruction data so the program can deserialize it into a Withdraw variant.
        };
        const signerKeypairs = signers ? signers.map((s: string) => loadKeypair(path.join(__dirname, `${s}.json`))) : [payer]; // Load keypair files for each signer so the transaction can include valid signatures.
        const transaction = new Transaction().add(instruction); // Wrap the instruction in a transaction so it can be signed and submitted.
        await sendAndConfirmTransaction(connection, transaction, [payer, ...signerKeypairs]); // Submit the transaction to the local validator and wait for confirmation so the withdrawal is recorded.
        return res.json({ vaultId, amount, recipient, status: "withdrawn" }); // Return confirmation so the client knows the funds were released.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.get("/treasury/balance", async (req, res) => { // Register the GET /treasury/balance route so clients can inspect treasury holdings.
    try { // Wrap in try/catch so runtime errors return HTTP 500 instead of crashing the server.
        const { vaultId } = req.query; // Extract the query parameter so we know which vault to inspect.
        if (!vaultId || typeof vaultId !== "string") { // Validate that vaultId is a string so the PublicKey constructor does not throw.
            return res.status(400).json({ error: "Missing vaultId query parameter" }); // Return 400 so the client knows the request was incomplete.
        }
        const pubkey = new PublicKey(vaultId); // Convert the string vaultId into a PublicKey so the RPC can fetch the balance.
        const balance = await connection.getBalance(pubkey); // Query the local validator for the lamport balance so the client sees the treasury amount.
        return res.json({ vaultId, balance }); // Return the balance so the client can display treasury health.
    } catch (error: any) { // Catch any thrown error so the server remains stable.
        return res.status(500).json({ error: error.message }); // Return 500 with the error message so the client can debug the failure.
    }
});

app.listen(PORT, () => { // Start the Express server so it begins accepting HTTP requests.
    console.log(`DAO API listening on port ${PORT}`); // Log the startup message so the operator knows the service is ready.
});
