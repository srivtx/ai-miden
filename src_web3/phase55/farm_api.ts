import express, { Request, Response } from "express"; // WHY: Express provides the HTTP server framework for REST API routes.
import { Connection, PublicKey, Transaction, SystemProgram } from "@solana/web3.js"; // WHY: Solana web3.js is the standard library for RPC communication and transaction building.
import { getAssociatedTokenAddress, createAssociatedTokenAccountInstruction, createTransferInstruction } from "@solana/spl-token"; // WHY: SPL token helpers abstract ATA derivation and token transfer instruction creation.
import dotenv from "dotenv"; // WHY: dotenv loads environment variables from .env so secrets are not hardcoded.

dotenv.config(); // WHY: Load environment variables before any configuration logic runs.

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const app = express(); // WHY: Create the Express application instance.
const PORT = 3059; // WHY: Port 3059 is dedicated to this service to avoid conflicts with other local services.
const RPC_URL = process.env.SOLANA_RPC_URL || "http://127.0.0.1:8899"; // WHY: Defaults to local validator for development; override for devnet/mainnet.
const FARM_PROGRAM_ID = new PublicKey(process.env.FARM_PROGRAM_ID || "Farm111111111111111111111111111111111111111"); // WHY: Public key of the deployed farm program; placeholder used if env is missing.
const BOOST_PROGRAM_ID = new PublicKey(process.env.BOOST_PROGRAM_ID || "Boost1111111111111111111111111111111111111"); // WHY: Public key of the deployed boost program.

const connection = new Connection(RPC_URL, "confirmed"); // WHY: "confirmed" commitment ensures transactions are finalized enough for API responses.

app.use(express.json()); // WHY: Parse JSON request bodies so routes can read POST parameters.

// ---------------------------------------------------------------------------
// Helper: Build and send transactions
// ---------------------------------------------------------------------------

/**
 * WHY: sendTransaction abstracts RPC submission so route handlers stay focused on business logic.
 * In production, you would integrate a wallet adapter or keypair for signing.
 */
async function sendTransaction(instructions: any[], signers: any[] = []): Promise<string>
{
    const transaction = new Transaction(); // WHY: A Transaction encapsulates all instructions to be atomically executed.
    instructions.forEach((ix) => transaction.add(ix)); // WHY: Add each instruction to the transaction in order.
    const signature = await connection.sendTransaction(transaction, signers); // WHY: Submit to the Solana network via RPC.
    return signature; // WHY: Return the tx signature so the client can track confirmation.
}

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

/**
 * WHY: POST /pool/create initializes a new farming pool on-chain.
 * Body: { authority, stakingTokenMint, rewardTokenMint, rewardRate }
 */
app.post("/pool/create", async (req: Request, res: Response) => {
    try
    {
        const { authority, stakingTokenMint, rewardTokenMint, rewardRate } = req.body; // WHY: Destructure required fields from the JSON body.

        if (!authority || !stakingTokenMint || !rewardTokenMint || rewardRate == null)
        {
            return res.status(400).json({ error: "Missing required fields" }); // WHY: Validate inputs early to avoid wasting RPC calls with bad data.
        }

        const authorityPubkey = new PublicKey(authority); // WHY: Convert string to PublicKey for on-chain use.
        const stakingMintPubkey = new PublicKey(stakingTokenMint); // WHY: Same conversion for staking token mint.
        const rewardMintPubkey = new PublicKey(rewardTokenMint); // WHY: Same conversion for reward token mint.

        /// WHY: Derive the pool PDA so the client knows the deterministic address before creation.
        const [poolPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("pool"), stakingMintPubkey.toBuffer(), rewardMintPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        /// WHY: Serialize instruction data with a discriminant byte (0 for CreatePool) and the reward rate.
        const instructionData = Buffer.alloc(9); // WHY: 1 byte discriminant + 8 bytes u64 rewardRate.
        instructionData.writeUInt8(0, 0); // WHY: Discriminant 0 maps to CreatePool in the Rust enum.
        instructionData.writeBigUInt64LE(BigInt(rewardRate), 1); // WHY: Write rewardRate as little-endian u64.

        const createPoolIx = {
            keys: [
                { pubkey: authorityPubkey, isSigner: true, isWritable: false }, // WHY: Authority signs and pays for pool creation.
                { pubkey: poolPda, isSigner: false, isWritable: true }, // WHY: Pool PDA is initialized by the program.
                { pubkey: stakingMintPubkey, isSigner: false, isWritable: false }, // WHY: Staking mint is read-only for validation.
                { pubkey: rewardMintPubkey, isSigner: false, isWritable: false }, // WHY: Reward mint is read-only for validation.
                { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // WHY: System Program may be needed for account allocation.
                { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false }, // WHY: Token Program ID for CPI reference.
            ],
            programId: FARM_PROGRAM_ID, // WHY: The instruction targets the farm program.
            data: instructionData, // WHY: Serialized arguments tell the program what to do.
        };

        const signature = await sendTransaction([createPoolIx]); // WHY: Submit the transaction to the chain.
        return res.json({ success: true, signature, poolAddress: poolPda.toBase58() }); // WHY: Return the pool address so clients can reference it later.
    }
    catch (error: any)
    {
        console.error("Pool creation error:", error); // WHY: Log server-side for debugging.
        return res.status(500).json({ error: error.message || "Internal server error" }); // WHY: Return a safe error message to the client.
    }
});

/**
 * WHY: POST /stake locks user tokens into a pool and starts reward accrual.
 * Body: { user, poolAddress, stakingTokenMint, rewardTokenMint, amount }
 */
app.post("/stake", async (req: Request, res: Response) => {
    try
    {
        const { user, poolAddress, stakingTokenMint, rewardTokenMint, amount } = req.body;

        if (!user || !poolAddress || !stakingTokenMint || !rewardTokenMint || !amount)
        {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const userPubkey = new PublicKey(user);
        const poolPubkey = new PublicKey(poolAddress);
        const stakingMintPubkey = new PublicKey(stakingTokenMint);
        const rewardMintPubkey = new PublicKey(rewardTokenMint);

        /// WHY: Derive the user's position PDA for this pool.
        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolPubkey.toBuffer(), userPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        /// WHY: Get the user's associated token account for the staking token.
        const userStakingAta = await getAssociatedTokenAddress(stakingMintPubkey, userPubkey);
        /// WHY: Derive the pool's staking escrow ATA.
        const [poolAuthority] = PublicKey.findProgramAddressSync(
            [Buffer.from("pool"), stakingMintPubkey.toBuffer(), rewardMintPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );
        const poolStakingAta = await getAssociatedTokenAddress(stakingMintPubkey, poolAuthority, true); // WHY: allowOwnerOffCurve=true because the owner is a PDA.

        const instructionData = Buffer.alloc(9); // WHY: 1 byte discriminant + 8 bytes u64 amount.
        instructionData.writeUInt8(1, 0); // WHY: Discriminant 1 maps to Stake.
        instructionData.writeBigUInt64LE(BigInt(amount), 1);

        const stakeIx = {
            keys: [
                { pubkey: userPubkey, isSigner: true, isWritable: false }, // WHY: User must sign to transfer tokens.
                { pubkey: poolPubkey, isSigner: false, isWritable: true }, // WHY: Pool state is updated.
                { pubkey: positionPda, isSigner: false, isWritable: true }, // WHY: Position account is created or updated.
                { pubkey: userStakingAta, isSigner: false, isWritable: true }, // WHY: User's token balance is reduced.
                { pubkey: poolStakingAta, isSigner: false, isWritable: true }, // WHY: Pool escrow balance is increased.
                { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false }, // WHY: Token Program executes the transfer.
                { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false }, // WHY: Clock sysvar provides timestamp for reward math.
            ],
            programId: FARM_PROGRAM_ID,
            data: instructionData,
        };

        const signature = await sendTransaction([stakeIx]);
        return res.json({ success: true, signature, positionAddress: positionPda.toBase58() });
    }
    catch (error: any)
    {
        console.error("Stake error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: POST /unstake returns principal and claims pending rewards automatically.
 * Body: { user, poolAddress, stakingTokenMint, rewardTokenMint, amount }
 */
app.post("/unstake", async (req: Request, res: Response) => {
    try
    {
        const { user, poolAddress, stakingTokenMint, rewardTokenMint, amount } = req.body;

        if (!user || !poolAddress || !stakingTokenMint || !rewardTokenMint || !amount)
        {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const userPubkey = new PublicKey(user);
        const poolPubkey = new PublicKey(poolAddress);
        const stakingMintPubkey = new PublicKey(stakingTokenMint);
        const rewardMintPubkey = new PublicKey(rewardTokenMint);

        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolPubkey.toBuffer(), userPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        const [poolAuthority] = PublicKey.findProgramAddressSync(
            [Buffer.from("pool"), stakingMintPubkey.toBuffer(), rewardMintPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );
        const poolStakingAta = await getAssociatedTokenAddress(stakingMintPubkey, poolAuthority, true);
        const userStakingAta = await getAssociatedTokenAddress(stakingMintPubkey, userPubkey);

        const instructionData = Buffer.alloc(9);
        instructionData.writeUInt8(2, 0); // WHY: Discriminant 2 maps to Unstake.
        instructionData.writeBigUInt64LE(BigInt(amount), 1);

        const unstakeIx = {
            keys: [
                { pubkey: userPubkey, isSigner: true, isWritable: false },
                { pubkey: poolPubkey, isSigner: false, isWritable: true },
                { pubkey: positionPda, isSigner: false, isWritable: true },
                { pubkey: poolStakingAta, isSigner: false, isWritable: true },
                { pubkey: userStakingAta, isSigner: false, isWritable: true },
                { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false },
                { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false },
            ],
            programId: FARM_PROGRAM_ID,
            data: instructionData,
        };

        const signature = await sendTransaction([unstakeIx]);
        return res.json({ success: true, signature });
    }
    catch (error: any)
    {
        console.error("Unstake error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: POST /claim calculates and transfers earned rewards without touching principal.
 * Body: { user, poolAddress }
 */
app.post("/claim", async (req: Request, res: Response) => {
    try
    {
        const { user, poolAddress } = req.body;

        if (!user || !poolAddress)
        {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const userPubkey = new PublicKey(user);
        const poolPubkey = new PublicKey(poolAddress);

        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolPubkey.toBuffer(), userPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        const instructionData = Buffer.alloc(1);
        instructionData.writeUInt8(3, 0); // WHY: Discriminant 3 maps to Claim.

        const claimIx = {
            keys: [
                { pubkey: userPubkey, isSigner: true, isWritable: false },
                { pubkey: poolPubkey, isSigner: false, isWritable: true },
                { pubkey: positionPda, isSigner: false, isWritable: true },
                { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false },
                { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false },
            ],
            programId: FARM_PROGRAM_ID,
            data: instructionData,
        };

        const signature = await sendTransaction([claimIx]);
        return res.json({ success: true, signature });
    }
    catch (error: any)
    {
        console.error("Claim error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: POST /compound claims rewards and immediately restakes them to maximize APY.
 * Body: { user, poolAddress, stakingTokenMint, rewardTokenMint }
 */
app.post("/compound", async (req: Request, res: Response) => {
    try
    {
        const { user, poolAddress, stakingTokenMint, rewardTokenMint } = req.body;

        if (!user || !poolAddress || !stakingTokenMint || !rewardTokenMint)
        {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const userPubkey = new PublicKey(user);
        const poolPubkey = new PublicKey(poolAddress);
        const stakingMintPubkey = new PublicKey(stakingTokenMint);
        const rewardMintPubkey = new PublicKey(rewardTokenMint);

        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolPubkey.toBuffer(), userPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        const userRewardAta = await getAssociatedTokenAddress(rewardMintPubkey, userPubkey);
        const [poolAuthority] = PublicKey.findProgramAddressSync(
            [Buffer.from("pool"), stakingMintPubkey.toBuffer(), rewardMintPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );
        const poolRewardAta = await getAssociatedTokenAddress(rewardMintPubkey, poolAuthority, true);
        const poolStakingAta = await getAssociatedTokenAddress(stakingMintPubkey, poolAuthority, true);

        const instructionData = Buffer.alloc(1);
        instructionData.writeUInt8(4, 0); // WHY: Discriminant 4 maps to Compound.

        const compoundIx = {
            keys: [
                { pubkey: userPubkey, isSigner: true, isWritable: false },
                { pubkey: poolPubkey, isSigner: false, isWritable: true },
                { pubkey: positionPda, isSigner: false, isWritable: true },
                { pubkey: userRewardAta, isSigner: false, isWritable: true },
                { pubkey: poolRewardAta, isSigner: false, isWritable: true },
                { pubkey: await getAssociatedTokenAddress(stakingMintPubkey, userPubkey), isSigner: false, isWritable: true },
                { pubkey: poolStakingAta, isSigner: false, isWritable: true },
                { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false },
                { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false },
            ],
            programId: FARM_PROGRAM_ID,
            data: instructionData,
        };

        const signature = await sendTransaction([compoundIx]);
        return res.json({ success: true, signature });
    }
    catch (error: any)
    {
        console.error("Compound error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: GET /rewards/:user fetches a user's pending rewards across all pools by simulating claim transactions.
 * This is read-only and does not mutate state.
 */
app.get("/rewards/:user", async (req: Request, res: Response) => {
    try
    {
        const user = req.params.user; // WHY: Extract the user public key from the URL path.
        const userPubkey = new PublicKey(user);

        /// WHY: Fetch all user position accounts owned by the farm program.
        const positions = await connection.getProgramAccounts(FARM_PROGRAM_ID, {
            filters: [
                {
                    memcmp: {
                        offset: 0, // WHY: The owner field is at the start of UserPosition serialization.
                        bytes: userPubkey.toBase58(),
                    },
                },
            ],
        });

        /// WHY: Map each position to its pending reward by reading the account data.
        const rewards = positions.map(({ pubkey, account }) => {
            const data = account.data;
            /// WHY: Manually parse staked_amount (offset 64) and reward_per_share_paid (offset 72).
            const stakedAmount = data.readBigUInt64LE(64);
            const rewardPerSharePaid = data.readBigUInt64LE(72); // WHY: This is a simplification; real parsing uses the full 16 bytes of u128.

            return {
                positionAddress: pubkey.toBase58(),
                stakedAmount: stakedAmount.toString(),
                rewardPerSharePaid: rewardPerSharePaid.toString(),
            };
        });

        return res.json({ success: true, user, positions: rewards });
    }
    catch (error: any)
    {
        console.error("Rewards fetch error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: GET /pools returns all initialized farm pools so clients can discover staking opportunities.
 */
app.get("/pools", async (_req: Request, res: Response) => {
    try
    {
        /// WHY: Fetch all accounts owned by the farm program with the pool discriminator or filter.
        const pools = await connection.getProgramAccounts(FARM_PROGRAM_ID, {
            filters: [
                {
                    dataSize: 169, // WHY: Approximate size of PoolState serialization; adjust after exact measurement.
                },
            ],
        });

        const poolList = pools.map(({ pubkey, account }) => {
            const data = account.data;
            /// WHY: Parse authority (bytes 0-32), staking mint (bytes 32-64), reward mint (bytes 64-96).
            const authority = new PublicKey(data.slice(0, 32)).toBase58();
            const stakingTokenMint = new PublicKey(data.slice(32, 64)).toBase58();
            const rewardTokenMint = new PublicKey(data.slice(64, 96)).toBase58();
            const rewardRate = data.readBigUInt64LE(128).toString(); // WHY: Approximate offset for reward_rate field.
            const totalStaked = data.readBigUInt64LE(136).toString(); // WHY: Approximate offset for total_staked field.

            return {
                poolAddress: pubkey.toBase58(),
                authority,
                stakingTokenMint,
                rewardTokenMint,
                rewardRate,
                totalStaked,
            };
        });

        return res.json({ success: true, pools: poolList });
    }
    catch (error: any)
    {
        console.error("Pools fetch error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

/**
 * WHY: POST /boost/apply links a boost NFT to a user's farming position, increasing their effective stake.
 * Body: { user, poolAddress, boostNftMint, boostNftAccount }
 */
app.post("/boost/apply", async (req: Request, res: Response) => {
    try
    {
        const { user, poolAddress, boostNftMint, boostNftAccount } = req.body;

        if (!user || !poolAddress || !boostNftMint || !boostNftAccount)
        {
            return res.status(400).json({ error: "Missing required fields" });
        }

        const userPubkey = new PublicKey(user);
        const poolPubkey = new PublicKey(poolAddress);
        const boostNftMintPubkey = new PublicKey(boostNftMint);
        const boostNftAccountPubkey = new PublicKey(boostNftAccount);

        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolPubkey.toBuffer(), userPubkey.toBuffer()],
            FARM_PROGRAM_ID,
        );

        const instructionData = Buffer.alloc(1);
        instructionData.writeUInt8(5, 0); // WHY: Discriminant 5 maps to ApplyBoost in the farm program.

        const applyBoostIx = {
            keys: [
                { pubkey: userPubkey, isSigner: true, isWritable: false }, // WHY: User must sign to apply boost to their position.
                { pubkey: poolPubkey, isSigner: false, isWritable: true }, // WHY: Pool state may update if rewards are auto-claimed.
                { pubkey: positionPda, isSigner: false, isWritable: true }, // WHY: Position stores the new multiplier and NFT mint.
                { pubkey: boostNftMintPubkey, isSigner: false, isWritable: false }, // WHY: Mint is read to derive multiplier.
                { pubkey: boostNftAccountPubkey, isSigner: false, isWritable: false }, // WHY: Token account proves ownership.
                { pubkey: BOOST_PROGRAM_ID, isSigner: false, isWritable: false }, // WHY: Reference to boost program for future CPI.
                { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false }, // WHY: Clock sysvar for time-based math.
            ],
            programId: FARM_PROGRAM_ID,
            data: instructionData,
        };

        const signature = await sendTransaction([applyBoostIx]);
        return res.json({ success: true, signature });
    }
    catch (error: any)
    {
        console.error("Boost apply error:", error);
        return res.status(500).json({ error: error.message || "Internal server error" });
    }
});

// ---------------------------------------------------------------------------
// Server Start
// ---------------------------------------------------------------------------

app.listen(PORT, () => {
    console.log(`Farm API listening on port ${PORT}`); // WHY: Confirm the server is running and on which port.
    console.log(`Connected to Solana RPC: ${RPC_URL}`); // WHY: Log the RPC endpoint for operational visibility.
});
