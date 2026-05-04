import express from "express"; // WHY: Web framework for HTTP API
import { Connection, PublicKey, Keypair, Transaction, SystemProgram } from "@solana/web3.js"; // WHY: Core Solana client libraries
import { AnchorProvider, Program, web3, BN } from "@coral-xyz/anchor"; // WHY: Anchor client for interacting with on-chain programs
import fetch from "node-fetch"; // WHY: HTTP client for Jupiter API calls

const app = express(); // WHY: Create Express application instance
app.use(express.json()); // WHY: Parse JSON request bodies

const PORT = 3066; // WHY: Dedicated port for this service to avoid conflicts
const RPC_URL = process.env.SOLANA_RPC || "https://api.devnet.solana.com"; // WHY: Devnet for safe testing; mainnet for production
const JUPITER_API = "https://quote-api.jup.ag/v6"; // WHY: Jupiter v6 API endpoint for swap quotes

// WHY: Load deployed program IDs from environment or use devnet placeholders
const LAUNCHPAD_PROGRAM_ID = new PublicKey(
    process.env.LAUNCHPAD_PROGRAM_ID || "LchPad111111111111111111111111111111111111"
);
const VESTING_PROGRAM_ID = new PublicKey(
    process.env.VESTING_PROGRAM_ID || "Vest222222222222222222222222222222222222222"
);

// WHY: Initialize Solana connection with commitment level for reliable reads
const connection = new Connection(RPC_URL, "confirmed"); // WHY: "confirmed" balances speed and finality

// WHY: Load wallet from filesystem or generate ephemeral keypair for testing
let wallet: Keypair; // WHY: Variable to hold signing keypair
try {
    const secretKey = JSON.parse(require("fs").readFileSync(process.env.WALLET_PATH || "./keypair.json", "utf-8")); // WHY: Load existing keypair
    wallet = Keypair.fromSecretKey(new Uint8Array(secretKey)); // WHY: Reconstruct keypair from secret key
} catch {
    wallet = Keypair.generate(); // WHY: Fallback to generated keypair if file missing
    console.warn("WARNING: Using ephemeral keypair. Fund it with devnet SOL."); // WHY: Alert user to fund the wallet
}

// WHY: Create Anchor provider that links connection + wallet for program interaction
const provider = new AnchorProvider(connection, { publicKey: wallet.publicKey, signTransaction: async (tx) => { tx.partialSign(wallet); return tx; }, signAllTransactions: async (txs) => txs.map(tx => { tx.partialSign(wallet); return tx; }) }, { commitment: "confirmed" });
// WHY: AnchorProvider bundles connection and wallet for automatic transaction signing

// WHY: Load Anchor IDL for launchpad program (in production, fetched from chain)
const launchpadIdl = require("./launchpad_idl.json"); // WHY: IDL defines program interface for client
const launchpadProgram = new Program(launchpadIdl, LAUNCHPAD_PROGRAM_ID, provider); // WHY: Typed program instance

// WHY: Load Anchor IDL for vesting program
const vestingIdl = require("./vesting_idl.json"); // WHY: IDL defines vesting program interface
const vestingProgram = new Program(vestingIdl, VESTING_PROGRAM_ID, provider); // WHY: Typed program instance

// WHY: In-memory store for project metadata (off-chain index, not source of truth)
const projects = new Map<string, any>(); // WHY: Cache for quick lookups; on-chain state is authoritative

/**
 * POST /project/register
 * Register a new token sale project on-chain.
 */
app.post("/project/register", async (req, res) => {
    try {
        const { tokenMint, hardCap, softCap, saleStart, saleEnd } = req.body; // WHY: Destructure request parameters
        if (!tokenMint || !hardCap || !softCap) { // WHY: Validate required fields
            return res.status(400).json({ error: "Missing required fields" }); // WHY: Reject incomplete requests
        }

        const tokenMintPubkey = new PublicKey(tokenMint); // WHY: Convert string to PublicKey
        const adminPubkey = wallet.publicKey; // WHY: Admin is the wallet owner

        // WHY: Derive project PDA using same seeds as on-chain program
        const [projectPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("project"), adminPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Deterministic PDA derivation matching Anchor seeds

        // WHY: Build and send Anchor transaction for register_project
        const tx = await launchpadProgram.methods
            .registerProject(tokenMintPubkey, new BN(hardCap), new BN(softCap), new BN(saleStart), new BN(saleEnd))
            .accounts({
                project: projectPda,
                admin: adminPubkey,
                systemProgram: SystemProgram.programId,
            })
            .rpc(); // WHY: .rpc() signs, sends, and confirms the transaction

        // WHY: Cache off-chain metadata for quick retrieval
        projects.set(projectPda.toBase58(), {
            admin: adminPubkey.toBase58(),
            tokenMint,
            hardCap,
            softCap,
            saleStart,
            saleEnd,
            tx,
        });

        res.json({ success: true, project: projectPda.toBase58(), tx }); // WHY: Return project address and tx signature
    } catch (err: any) {
        console.error("Register error:", err); // WHY: Log for debugging
        res.status(500).json({ error: err.message }); // WHY: Return error to client
    }
});

/**
 * POST /project/tiers
 * Define a whitelist tier for a project.
 */
app.post("/project/tiers", async (req, res) => {
    try {
        const { project, tierId, price, allocation, whitelistMint } = req.body; // WHY: Destructure tier parameters
        const projectPubkey = new PublicKey(project); // WHY: Convert to PublicKey
        const adminPubkey = wallet.publicKey; // WHY: Admin signs

        // WHY: Derive tier PDA
        const [tierPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("tier"), projectPubkey.toBuffer(), Buffer.from([tierId])],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Match on-chain seed derivation

        const whitelistPubkey = whitelistMint ? new PublicKey(whitelistMint) : null; // WHY: Optional whitelist mint

        const tx = await launchpadProgram.methods
            .setTier(tierId, new BN(price), new BN(allocation), whitelistPubkey)
            .accounts({
                project: projectPubkey,
                tier: tierPda,
                admin: adminPubkey,
                systemProgram: SystemProgram.programId,
            })
            .rpc(); // WHY: Send transaction

        res.json({ success: true, tier: tierPda.toBase58(), tx }); // WHY: Return tier address
    } catch (err: any) {
        console.error("Set tier error:", err); // WHY: Log for debugging
        res.status(500).json({ error: err.message }); // WHY: Return error
    }
});

/**
 * POST /participate
 * Participate in a token sale. If payment is not SOL/USDC, use Jupiter to swap first.
 */
app.post("/participate", async (req, res) => {
    try {
        const { project, tier, amount, paymentMint } = req.body; // WHY: Destructure participation parameters
        const projectPubkey = new PublicKey(project); // WHY: Convert to PublicKey
        const tierPubkey = new PublicKey(tier); // WHY: Convert to PublicKey
        const userPubkey = wallet.publicKey; // WHY: User is the wallet owner

        // WHY: Fetch tier info to calculate cost
        const tierAccount = await launchpadProgram.account.tier.fetch(tierPubkey); // WHY: Read on-chain tier state
        const cost = tierAccount.price.mul(new BN(amount)); // WHY: Calculate total cost

        let txs: string[] = []; // WHY: Collect transaction signatures

        // WHY: If payment mint is not the project's accepted token, use Jupiter to swap
        if (paymentMint && paymentMint !== tierAccount.project.toBase58()) {
            // WHY: Call Jupiter API to get swap quote
            const quoteRes = await fetch(
                `${JUPITER_API}/quote?inputMint=${paymentMint}&outputMint=So11111111111111111111111111111111111111112&amount=${cost.toString()}&slippageBps=50`
            ); // WHY: Get quote from Jupiter with 0.5% slippage
            if (!quoteRes.ok) throw new Error("Jupiter quote failed"); // WHY: Handle API failure
            const quote = await quoteRes.json(); // WHY: Parse quote response

            // WHY: Build swap transaction via Jupiter
            const swapRes = await fetch(`${JUPITER_API}/swap`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    quoteResponse: quote,
                    userPublicKey: userPubkey.toBase58(),
                    wrapAndUnwrapSol: true,
                }),
            }); // WHY: Request swap transaction from Jupiter
            if (!swapRes.ok) throw new Error("Jupiter swap failed"); // WHY: Handle API failure
            const swapData = await swapRes.json(); // WHY: Parse swap response
            txs.push(swapData.txid); // WHY: Record swap tx signature
        }

        // WHY: Derive participation PDA
        const [participationPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("participation"), projectPubkey.toBuffer(), userPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Match on-chain seed derivation

        // WHY: Derive project vault PDA
        const [projectVault] = PublicKey.findProgramAddressSync(
            [Buffer.from("vault"), projectPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Match on-chain vault seeds

        // WHY: Build and send participation transaction
        const tx = await launchpadProgram.methods
            .participate(new BN(amount))
            .accounts({
                project: projectPubkey,
                tier: tierPubkey,
                participation: participationPda,
                user: userPubkey,
                userPaymentAccount: userPubkey, // WHY: Simplified; real impl would use user's token account
                projectVault: projectVault,
                whitelistTokenAccount: userPubkey, // WHY: Simplified; real impl would use whitelist token account
                tokenProgram: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                systemProgram: SystemProgram.programId,
            })
            .rpc(); // WHY: Send transaction
        txs.push(tx); // WHY: Record participation tx

        res.json({ success: true, participation: participationPda.toBase58(), txs }); // WHY: Return results
    } catch (err: any) {
        console.error("Participate error:", err); // WHY: Log for debugging
        res.status(500).json({ error: err.message }); // WHY: Return error
    }
});

/**
 * POST /claim
 * Claim purchased tokens after successful sale.
 */
app.post("/claim", async (req, res) => {
    try {
        const { project } = req.body; // WHY: Need project address to derive accounts
        const projectPubkey = new PublicKey(project); // WHY: Convert to PublicKey
        const userPubkey = wallet.publicKey; // WHY: Claimer signs

        const [participationPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("participation"), projectPubkey.toBuffer(), userPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Derive participation PDA

        const [projectVaultAuthority] = PublicKey.findProgramAddressSync(
            [Buffer.from("vault"), projectPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Derive vault authority PDA

        const tx = await launchpadProgram.methods
            .claim()
            .accounts({
                project: projectPubkey,
                participation: participationPda,
                user: userPubkey,
                projectTokenVault: projectVaultAuthority, // WHY: Simplified; real impl would use separate token vault
                userTokenAccount: userPubkey, // WHY: Simplified; real impl would use user's token account
                projectVaultAuthority: projectVaultAuthority,
                tokenProgram: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            })
            .rpc(); // WHY: Send transaction

        res.json({ success: true, tx }); // WHY: Return tx signature
    } catch (err: any) {
        console.error("Claim error:", err); // WHY: Log for debugging
        res.status(500).json({ error: err.message }); // WHY: Return error
    }
});

/**
 * POST /refund
 * Refund if soft cap not met.
 */
app.post("/refund", async (req, res) => {
    try {
        const { project } = req.body; // WHY: Need project address
        const projectPubkey = new PublicKey(project); // WHY: Convert to PublicKey
        const userPubkey = wallet.publicKey; // WHY: Refund recipient signs

        const [participationPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("participation"), projectPubkey.toBuffer(), userPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Derive participation PDA

        const [projectVaultAuthority] = PublicKey.findProgramAddressSync(
            [Buffer.from("vault"), projectPubkey.toBuffer()],
            LAUNCHPAD_PROGRAM_ID
        ); // WHY: Derive vault authority PDA

        const tx = await launchpadProgram.methods
            .refund()
            .accounts({
                project: projectPubkey,
                participation: participationPda,
                user: userPubkey,
                projectVault: projectVaultAuthority,
                userPaymentAccount: userPubkey, // WHY: Simplified; real impl would use user's payment token account
                projectVaultAuthority: projectVaultAuthority,
                tokenProgram: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            })
            .rpc(); // WHY: Send transaction

        res.json({ success: true, tx }); // WHY: Return tx signature
    } catch (err: any) {
        console.error("Refund error:", err); // WHY: Log for debugging
        res.status(500).json({ error: err.message }); // WHY: Return error
    }
});

/**
 * GET /projects
 * List all registered projects (from off-chain cache).
 */
app.get("/projects", (req, res) => {
    const list = Array.from(projects.entries()).map(([id, data]) => ({ id, ...data })); // WHY: Convert Map to array for JSON
    res.json({ projects: list }); // WHY: Return project list
});

/**
 * GET /project/:id
 * Get project details by ID.
 */
app.get("/project/:id", (req, res) => {
    const project = projects.get(req.params.id); // WHY: Lookup by project ID
    if (!project) return res.status(404).json({ error: "Project not found" }); // WHY: Handle missing project
    res.json({ project }); // WHY: Return project data
});

// WHY: Start Express server
app.listen(PORT, () => {
    console.log(`Phase 58v2 Launchpad API running on port ${PORT}`); // WHY: Log startup for debugging
    console.log(`Wallet: ${wallet.publicKey.toBase58()}`); // WHY: Display wallet address for funding
    console.log(`RPC: ${RPC_URL}`); // WHY: Display connected RPC endpoint
});
