import * as anchor from "@coral-xyz/anchor"; // WHY: The Anchor library provides typed program interaction, IDL parsing, and transaction building.
import { Connection, Keypair, PublicKey, clusterApiUrl } from "@solana/web3.js"; // WHY: These Solana web3.js types are needed for raw connection and keypair operations that Anchor wraps.
import { Program, AnchorProvider, Wallet, BN } from "@coral-xyz/anchor"; // WHY: Program wraps the IDL, AnchorProvider bundles connection and wallet, and BN handles u64 values from Rust.
import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token"; // WHY: The SPL Token library provides helpers for token account operations and mint queries.
import * as express from "express"; // WHY: Express provides the HTTP server framework for the REST API.
import * as bodyParser from "body-parser"; // WHY: Body-parser parses JSON request bodies so route handlers can read parameters.
import * as fs from "fs"; // WHY: The filesystem module reads the IDL JSON and wallet keypair files.
import * as path from "path"; // WHY: Path utilities ensure cross-platform file resolution.

// WHY: The governance program ID must match the deployed program address on-chain.
const GOVERNANCE_PROGRAM_ID = new PublicKey("Gov111111111111111111111111111111111111111"); // WHY: PublicKey validates the base58 string and provides typed equality checks.
// WHY: The treasury program ID must match the deployed treasury program address.
const TREASURY_PROGRAM_ID = new PublicKey("Tre222222222222222222222222222222222222222"); // WHY: PublicKey ensures the address is well-formed.

// WHY: The API port is 3063 to match the project specification and avoid conflicts with other local services.
const PORT = 3063; // WHY: Hardcoding the port ensures the client knows where to connect.

// WHY: The app variable creates the Express application instance.
const app = express(); // WHY: Express is the industry standard for Node.js HTTP APIs.

// WHY: Middleware to parse JSON bodies must be registered before route handlers.
app.use(bodyParser.json()); // WHY: Without this, req.body is undefined for JSON POST requests.

// WHY: This helper function creates an Anchor provider and program instance for each request.
function getPrograms(walletPath: string) { // WHY: Encapsulating setup in a function allows different wallets per request in a multi-tenant API.
    const connection = new Connection(clusterApiUrl("devnet"), "confirmed"); // WHY: Devnet is the public test network for integration testing without real funds.
    const keypair = Keypair.fromSecretKey( // WHY: Keypair.fromSecretKey reconstructs a signing key from the wallet file bytes.
        Buffer.from(JSON.parse(fs.readFileSync(walletPath, "utf-8"))) // WHY: fs.readFileSync reads the wallet JSON, and JSON.parse converts it to an array.
    );
    const wallet = new Wallet(keypair); // WHY: Anchor Wallet wraps the Keypair to provide a consistent interface.
    const provider = new AnchorProvider(connection, wallet, AnchorProvider.defaultOptions()); // WHY: The provider bundles the connection, wallet, and default commitment level.
    anchor.setProvider(provider); // WHY: setProvider makes the provider available globally for Anchor operations.

    const governanceIdl = JSON.parse( // WHY: The IDL is the interface contract between on-chain and off-chain code.
        fs.readFileSync( // WHY: fs.readFileSync loads the IDL from the Anchor build output.
            path.join(__dirname, "governance", "target", "idl", "governance.json"), // WHY: __dirname ensures the path is relative to the script location.
            "utf-8" // WHY: The IDL is encoded as UTF-8 JSON.
        )
    );
    const treasuryIdl = JSON.parse( // WHY: The treasury program has its own IDL describing its instructions and accounts.
        fs.readFileSync(
            path.join(__dirname, "governance", "target", "idl", "treasury.json"),
            "utf-8"
        )
    );

    const governanceProgram = new Program(governanceIdl, provider); // WHY: The Program class uses the IDL to generate typed methods for every instruction.
    const treasuryProgram = new Program(treasuryIdl, provider); // WHY: A separate Program instance is created for the treasury IDL.

    return { connection, wallet, provider, governanceProgram, treasuryProgram }; // WHY: Returning all objects allows the caller to access whichever layer it needs.
}

// WHY: This route creates a new governance proposal.
app.post("/proposal", async (req, res) => { // WHY: POST is used for creation because it is not idempotent and has side effects.
    try { // WHY: try/catch prevents server crashes and allows sending meaningful error responses to the client.
        const { walletPath, description, quorum, deadline } = req.body; // WHY: Destructuring extracts the required parameters from the JSON body.
        if (!walletPath || !description || quorum === undefined || !deadline) { // WHY: Input validation prevents undefined behavior and wasted transactions.
            res.status(400).json({ error: "Missing required fields: walletPath, description, quorum, deadline" }); // WHY: 400 Bad Request tells the client the input was malformed.
            return; // WHY: Early return prevents further execution with invalid input.
        }

        const { governanceProgram } = getPrograms(walletPath); // WHY: The program instance is created per request so different wallets can be used.

        const [configPda] = PublicKey.findProgramAddressSync( // WHY: findProgramAddressSync derives the config PDA from the fixed seed.
            [Buffer.from("config")], // WHY: The seed must match the on-chain seeds exactly.
            GOVERNANCE_PROGRAM_ID // WHY: The program ID is part of the PDA derivation.
        );

        const tx = await governanceProgram.methods // WHY: methods exposes all instructions defined in the IDL.
            .createProposal(description, new BN(deadline)) // WHY: BN wraps the deadline because Rust i64 does not map directly to JavaScript number.
            .accounts({ // WHY: accounts maps instruction accounts by name as defined in the IDL.
                creator: governanceProgram.provider.publicKey, // WHY: The provider's public key is the signer paying for the proposal.
                config: configPda, // WHY: The config PDA is read to get the proposal counter.
                proposal: null, // WHY: Anchor automatically derives the proposal PDA from seeds when using init; passing null triggers auto-derivation.
                systemProgram: anchor.web3.SystemProgram.programId, // WHY: The system program ID is a well-known constant required for account creation.
            })
            .rpc(); // WHY: rpc builds, signs, and sends the transaction, then waits for confirmation.

        res.json({ success: true, signature: tx }); // WHY: Returning the transaction signature allows the client to verify the result on-chain.
    } catch (err) { // WHY: Catching errors allows the API to respond gracefully instead of crashing.
        console.error("Error creating proposal:", err); // WHY: Logging the error helps with server-side debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 tells the client the error was server-side.
    }
});

// WHY: This route casts a token-weighted vote on a proposal.
app.post("/vote", async (req, res) => { // WHY: POST is used because voting changes on-chain state.
    try {
        const { walletPath, proposalId, voteFor, tokenAccount } = req.body; // WHY: Destructuring extracts vote parameters.
        if (!walletPath || proposalId === undefined || voteFor === undefined || !tokenAccount) { // WHY: Validation prevents missing parameter errors.
            res.status(400).json({ error: "Missing required fields: walletPath, proposalId, voteFor, tokenAccount" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution with invalid input.
        }

        const { governanceProgram, provider } = getPrograms(walletPath); // WHY: Each request may use a different voter wallet.

        const [configPda] = PublicKey.findProgramAddressSync( // WHY: Deriving the config PDA ensures we read the correct governance parameters.
            [Buffer.from("config")],
            GOVERNANCE_PROGRAM_ID
        );

        const proposalPda = PublicKey.findProgramAddressSync( // WHY: Deriving the proposal PDA from its ID ensures we target the correct proposal.
            [Buffer.from("proposal"), new BN(proposalId).toArrayLike(Buffer, "le", 8)], // WHY: The seed must match the on-chain serialization: little-endian u64.
            GOVERNANCE_PROGRAM_ID
        )[0];

        const voterTokenAccount = new PublicKey(tokenAccount); // WHY: Converting the string to PublicKey validates the base58 format.
        const voterRecordPda = PublicKey.findProgramAddressSync( // WHY: Deriving the voter record PDA prevents double voting.
            [
                Buffer.from("vote"),
                proposalPda.toBuffer(),
                provider.publicKey.toBuffer(),
            ],
            GOVERNANCE_PROGRAM_ID
        )[0];

        const tx = await governanceProgram.methods
            .castVote(voteFor) // WHY: voteFor is a boolean matching the Rust bool type.
            .accounts({
                voter: provider.publicKey, // WHY: The voter is the signer.
                proposal: proposalPda, // WHY: The proposal PDA is the account being updated.
                config: configPda, // WHY: The config provides the governance mint for validation.
                voterTokenAccount: voterTokenAccount, // WHY: The token account provides the voting weight.
                voterRecord: voterRecordPda, // WHY: The voter record prevents double voting.
                systemProgram: anchor.web3.SystemProgram.programId, // WHY: Required for init_if_needed.
            })
            .rpc(); // WHY: rpc sends and confirms the transaction.

        res.json({ success: true, signature: tx }); // WHY: The signature proves the vote was recorded on-chain.
    } catch (err) {
        console.error("Error casting vote:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This route delegates voting power to another address.
app.post("/delegate", async (req, res) => { // WHY: POST is used because delegation creates on-chain state.
    try {
        const { walletPath, delegatee } = req.body; // WHY: Destructuring extracts delegation parameters.
        if (!walletPath || !delegatee) { // WHY: Validation prevents missing fields.
            res.status(400).json({ error: "Missing required fields: walletPath, delegatee" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution.
        }

        const { governanceProgram, provider } = getPrograms(walletPath); // WHY: Each request may use a different delegator wallet.

        const delegationRecordPda = PublicKey.findProgramAddressSync( // WHY: Deriving the delegation PDA ensures a unique record per delegator.
            [
                Buffer.from("delegation"),
                provider.publicKey.toBuffer(),
            ],
            GOVERNANCE_PROGRAM_ID
        )[0];

        const tx = await governanceProgram.methods
            .delegateVote(new PublicKey(delegatee)) // WHY: The delegatee is converted to PublicKey for type safety.
            .accounts({
                delegator: provider.publicKey, // WHY: The delegator is the signer.
                delegationRecord: delegationRecordPda, // WHY: The record stores the delegation.
                systemProgram: anchor.web3.SystemProgram.programId, // WHY: Required for account creation.
            })
            .rpc(); // WHY: rpc sends and confirms the transaction.

        res.json({ success: true, signature: tx }); // WHY: The signature proves the delegation was recorded.
    } catch (err) {
        console.error("Error delegating vote:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This route executes a proposal after the deadline and timelock.
app.post("/execute", async (req, res) => { // WHY: POST is used because execution changes on-chain state.
    try {
        const { walletPath, proposalId } = req.body; // WHY: Destructuring extracts execution parameters.
        if (!walletPath || proposalId === undefined) { // WHY: Validation prevents missing fields.
            res.status(400).json({ error: "Missing required fields: walletPath, proposalId" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution.
        }

        const { governanceProgram } = getPrograms(walletPath); // WHY: Each request may use a different executor wallet.

        const [configPda] = PublicKey.findProgramAddressSync( // WHY: Deriving the config PDA provides the timelock delay.
            [Buffer.from("config")],
            GOVERNANCE_PROGRAM_ID
        );

        const proposalPda = PublicKey.findProgramAddressSync( // WHY: Deriving the proposal PDA ensures we target the correct proposal.
            [Buffer.from("proposal"), new BN(proposalId).toArrayLike(Buffer, "le", 8)],
            GOVERNANCE_PROGRAM_ID
        )[0];

        const tx = await governanceProgram.methods
            .executeProposal() // WHY: executeProposal takes no parameters because all state is read from accounts.
            .accounts({
                proposal: proposalPda, // WHY: The proposal is the account being executed.
                config: configPda, // WHY: The config provides the timelock delay.
            })
            .rpc(); // WHY: rpc sends and confirms the transaction.

        res.json({ success: true, signature: tx }); // WHY: The signature proves execution occurred.
    } catch (err) {
        console.error("Error executing proposal:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This route lists all proposals by fetching them from the chain.
app.get("/proposals", async (req, res) => { // WHY: GET is used because listing is a read-only operation.
    try {
        const { walletPath } = req.query as { walletPath: string }; // WHY: Query parameters are used for GET requests.
        if (!walletPath) { // WHY: Validation prevents missing fields.
            res.status(400).json({ error: "Missing required query parameter: walletPath" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution.
        }

        const { governanceProgram } = getPrograms(walletPath); // WHY: The program instance is needed to fetch typed accounts.

        const proposals = await governanceProgram.account.proposal.all(); // WHY: The all() method fetches every proposal account by its discriminator.

        res.json({ success: true, proposals }); // WHY: Returning the full account data allows the client to render proposal details.
    } catch (err) {
        console.error("Error fetching proposals:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This route fetches a single proposal by its PDA.
app.get("/proposal/:id", async (req, res) => { // WHY: The route parameter :id identifies the proposal to fetch.
    try {
        const { walletPath } = req.query as { walletPath: string }; // WHY: The wallet path is a query parameter because GET bodies are discouraged.
        const proposalId = parseInt(req.params.id, 10); // WHY: parseInt converts the string parameter to an integer.
        if (!walletPath || isNaN(proposalId)) { // WHY: Validation prevents invalid lookups.
            res.status(400).json({ error: "Missing or invalid parameters" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution.
        }

        const { governanceProgram } = getPrograms(walletPath); // WHY: The program instance is needed to fetch typed accounts.

        const proposalPda = PublicKey.findProgramAddressSync( // WHY: Deriving the PDA from the ID ensures we fetch the correct account.
            [Buffer.from("proposal"), new BN(proposalId).toArrayLike(Buffer, "le", 8)],
            GOVERNANCE_PROGRAM_ID
        )[0];

        const proposal = await governanceProgram.account.proposal.fetch(proposalPda); // WHY: fetch deserializes the account data using the IDL.

        if (!proposal) { // WHY: Checking for null handles the case where the account does not exist.
            res.status(404).json({ error: "Proposal not found" }); // WHY: 404 tells the client the resource does not exist.
            return; // WHY: Early return stops execution.
        }

        res.json({ success: true, proposal }); // WHY: Returning the typed account data allows the client to render proposal details.
    } catch (err) {
        console.error("Error fetching proposal:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This route returns the treasury vault token balance.
app.get("/treasury/balance", async (req, res) => { // WHY: GET is used because balance checks are read-only.
    try {
        const { walletPath, treasuryAddress } = req.query as { walletPath: string; treasuryAddress: string }; // WHY: Query parameters are used for GET requests.
        if (!walletPath || !treasuryAddress) { // WHY: Validation prevents missing fields.
            res.status(400).json({ error: "Missing required query parameters: walletPath, treasuryAddress" }); // WHY: 400 indicates client error.
            return; // WHY: Early return stops execution.
        }

        const { connection } = getPrograms(walletPath); // WHY: The connection is sufficient for balance queries without program methods.
        const treasuryPda = new PublicKey(treasuryAddress); // WHY: Converting to PublicKey validates the address format.

        const vaultPda = PublicKey.findProgramAddressSync( // WHY: Deriving the vault PDA from the treasury key ensures we read the correct account.
            [Buffer.from("vault"), treasuryPda.toBuffer()],
            TREASURY_PROGRAM_ID
        )[0];

        const accountInfo = await connection.getTokenAccountBalance(vaultPda); // WHY: getTokenAccountBalance returns the SPL token balance, not lamports.

        if (!accountInfo || !accountInfo.value) { // WHY: Checking for null handles the case where the vault does not exist.
            res.status(404).json({ error: "Treasury vault not found" }); // WHY: 404 tells the client the vault has not been initialized.
            return; // WHY: Early return stops execution.
        }

        res.json({ // WHY: Returning structured data allows the client to parse the balance easily.
            success: true,
            treasury: treasuryAddress,
            vault: vaultPda.toBase58(),
            balance: accountInfo.value.amount,
            decimals: accountInfo.value.decimals,
        });
    } catch (err) {
        console.error("Error fetching treasury balance:", err); // WHY: Logging aids debugging.
        res.status(500).json({ error: err.message || "Internal server error" }); // WHY: 500 indicates server-side failure.
    }
});

// WHY: This starts the Express server and listens for incoming HTTP requests.
app.listen(PORT, () => { // WHY: listen binds the server to the specified port.
    console.log(`DAO API listening on port ${PORT}`); // WHY: Logging the startup message confirms the server is running.
    console.log(`Governance program: ${GOVERNANCE_PROGRAM_ID.toBase58()}`); // WHY: Logging the program ID helps verify the correct deployment.
    console.log(`Treasury program: ${TREASURY_PROGRAM_ID.toBase58()}`); // WHY: Logging the program ID helps verify the correct deployment.
}); // WHY: The callback runs after the server starts successfully.
