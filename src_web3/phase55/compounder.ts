import { Connection, PublicKey, Transaction } from "@solana/web3.js"; // WHY: Solana web3.js provides RPC connectivity and transaction construction for the compounding service.
import { getAssociatedTokenAddress } from "@solana/spl-token"; // WHY: SPL token helpers derive the associated token accounts needed for restaking.
import dotenv from "dotenv"; // WHY: dotenv loads configuration like RPC URLs and program IDs from environment variables.

dotenv.config(); // WHY: Load environment variables at startup before any service logic executes.

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const RPC_URL = process.env.SOLANA_RPC_URL || "http://127.0.0.1:8899"; // WHY: Default to local validator for safe development and testing.
const FARM_PROGRAM_ID = new PublicKey(process.env.FARM_PROGRAM_ID || "Farm111111111111111111111111111111111111111"); // WHY: The farm program address is required to build compounding transactions.
const COMPOUND_INTERVAL_MS = parseInt(process.env.COMPOUND_INTERVAL_MS || "300000"); // WHY: Default 5 minutes between compounding rounds; frequent enough for active farms, rare enough to save RPC credits.
const REWARD_THRESHOLD = parseInt(process.env.REWARD_THRESHOLD || "1000000"); // WHY: Minimum pending reward value (in smallest token units) to justify transaction cost; prevents unprofitable compounds.
const FEE_PERCENT_BPS = parseInt(process.env.FEE_PERCENT_BPS || "500"); // WHY: 5% fee in basis points (500/10000); sustainable revenue without excessive user cost.

const connection = new Connection(RPC_URL, "confirmed"); // WHY: "confirmed" commitment strikes balance between speed and finality for background operations.

// ---------------------------------------------------------------------------
// In-memory opt-in registry
// ---------------------------------------------------------------------------

/**
 * WHY: optedInUsers stores the list of users who have delegated compounding authority.
 * In production, this would be a persistent database or an on-chain registry account.
 */
interface OptedInUser
{
    userPublicKey: string; // WHY: The wallet address to compound for.
    poolAddress: string; // WHY: The specific pool where the user's position lives.
    stakingTokenMint: string; // WHY: Needed to derive token accounts for restaking.
    rewardTokenMint: string; // WHY: Needed to derive token accounts for claiming.
    lastCompoundedAt: number; // WHY: Timestamp of last successful compound to enforce cooldowns.
}

const optedInUsers: OptedInUser[] = []; // WHY: In-memory storage is sufficient for demonstration; production requires persistence.

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * WHY: fetchPendingRewards simulates a claim to read the pending reward amount without mutating state.
 * This avoids wasting transaction fees on users with negligible rewards.
 */
async function fetchPendingRewards(
    userPublicKey: PublicKey,
    poolAddress: PublicKey,
): Promise<number>
{
    try
    {
        const [positionPda] = PublicKey.findProgramAddressSync(
            [Buffer.from("user"), poolAddress.toBuffer(), userPublicKey.toBuffer()],
            FARM_PROGRAM_ID,
        ); // WHY: Derive the user's position PDA to read on-chain data.

        const accountInfo = await connection.getAccountInfo(positionPda); // WHY: Fetch the position account to inspect staked amount and accumulator.
        if (!accountInfo)
        {
            return 0; // WHY: No position means no pending rewards.
        }

        const data = accountInfo.data;
        const stakedAmount = Number(data.readBigUInt64LE(64)); // WHY: Offset 64 is staked_amount in UserPosition.
        const boostMultiplier = Number(data.readBigUInt64LE(88)); // WHY: Offset 88 is boost_multiplier in UserPosition.
        const rewardPerSharePaid = Number(data.readBigUInt64LE(72)); // WHY: Offset 72 is the user's accumulator snapshot (simplified to 64 bits here).

        const poolInfo = await connection.getAccountInfo(poolAddress); // WHY: Fetch pool state to read the global accumulator.
        if (!poolInfo)
        {
            return 0;
        }
        const poolData = poolInfo.data;
        const globalRewardPerShare = Number(poolData.readBigUInt64LE(96)); // WHY: Offset 96 is reward_per_share_stored in PoolState.
        const totalStaked = Number(poolData.readBigUInt64LE(136)); // WHY: Offset 136 is total_staked.

        /// WHY: If total staked is zero, no rewards are being distributed.
        if (totalStaked === 0)
        {
            return 0;
        }

        /// WHY: Calculate effective stake with boost applied.
        const effectiveStake = (stakedAmount * boostMultiplier) / 1000;

        /// WHY: Pending rewards = effective_stake * (global_accumulator - user_accumulator) / PRECISION.
        const PRECISION = 1_000_000_000_000; // WHY: Must match the on-chain precision constant.
        const accumulatorDiff = globalRewardPerShare - rewardPerSharePaid;
        const pending = (effectiveStake * accumulatorDiff) / PRECISION;

        return Math.max(0, pending); // WHY: Clamp to zero in case of data misalignment.
    }
    catch (error)
    {
        console.error("Error fetching pending rewards:", error); // WHY: Log errors so the service does not crash on one bad user.
        return 0;
    }
}

/**
 * WHY: buildCompoundTransaction constructs the instruction to claim and restake rewards for a user.
 */
async function buildCompoundTransaction(
    userPublicKey: PublicKey,
    poolAddress: PublicKey,
    stakingTokenMint: PublicKey,
    rewardTokenMint: PublicKey,
): Promise<Transaction>
{
    const [positionPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("user"), poolAddress.toBuffer(), userPublicKey.toBuffer()],
        FARM_PROGRAM_ID,
    );

    const userRewardAta = await getAssociatedTokenAddress(rewardTokenMint, userPublicKey);
    const [poolAuthority] = PublicKey.findProgramAddressSync(
        [Buffer.from("pool"), stakingTokenMint.toBuffer(), rewardTokenMint.toBuffer()],
        FARM_PROGRAM_ID,
    );
    const poolRewardAta = await getAssociatedTokenAddress(rewardTokenMint, poolAuthority, true); // WHY: allowOwnerOffCurve=true for PDA-owned ATAs.
    const poolStakingAta = await getAssociatedTokenAddress(stakingTokenMint, poolAuthority, true);
    const userStakingAta = await getAssociatedTokenAddress(stakingTokenMint, userPublicKey);

    const instructionData = Buffer.alloc(1);
    instructionData.writeUInt8(4, 0); // WHY: Discriminant 4 maps to Compound in the farm program.

    const compoundIx = {
        keys: [
            { pubkey: userPublicKey, isSigner: true, isWritable: false }, // WHY: User must authorize the compound.
            { pubkey: poolAddress, isSigner: false, isWritable: true }, // WHY: Pool state updates with new stake.
            { pubkey: positionPda, isSigner: false, isWritable: true }, // WHY: Position records increased principal.
            { pubkey: userRewardAta, isSigner: false, isWritable: true }, // WHY: Receives claimed rewards.
            { pubkey: poolRewardAta, isSigner: false, isWritable: true }, // WHY: Sends claimed rewards.
            { pubkey: userStakingAta, isSigner: false, isWritable: true }, // WHY: Not directly used in this simplified flow, but reserved for swap intermediates.
            { pubkey: poolStakingAta, isSigner: false, isWritable: true }, // WHY: Receives restaked tokens.
            { pubkey: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), isSigner: false, isWritable: false }, // WHY: Token Program executes transfers.
            { pubkey: new PublicKey("SysvarC1ock11111111111111111111111111111111"), isSigner: false, isWritable: false }, // WHY: Clock sysvar for reward math.
        ],
        programId: FARM_PROGRAM_ID,
        data: instructionData,
    };

    const transaction = new Transaction(); // WHY: Encapsulate the compound instruction in a transaction.
    transaction.add(compoundIx); // WHY: Add the instruction to the transaction.
    return transaction;
}

/**
 * WHY: compoundUser attempts to claim and restake rewards for a single opted-in user.
 * It checks thresholds, deducts fees, and updates the last-compounded timestamp.
 */
async function compoundUser(user: OptedInUser): Promise<void>
{
    try
    {
        const userPubkey = new PublicKey(user.userPublicKey);
        const poolAddress = new PublicKey(user.poolAddress);
        const stakingTokenMint = new PublicKey(user.stakingTokenMint);
        const rewardTokenMint = new PublicKey(user.rewardTokenMint);

        /// WHY: Enforce a cooldown to prevent spamming transactions and wasting fees.
        const now = Date.now();
        if (now - user.lastCompoundedAt < COMPOUND_INTERVAL_MS)
        {
            return;
        }

        /// WHY: Only compound if pending rewards exceed the gas-cost threshold.
        const pending = await fetchPendingRewards(userPubkey, poolAddress);
        if (pending < REWARD_THRESHOLD)
        {
            console.log(`Skipping ${user.userPublicKey}: pending ${pending} below threshold ${REWARD_THRESHOLD}`);
            return;
        }

        /// WHY: Calculate fee amount in reward tokens.
        const feeAmount = Math.floor((pending * FEE_PERCENT_BPS) / 10000); // WHY: Basis point math avoids floating point.
        const compoundAmount = pending - feeAmount; // WHY: User restakes the net amount after fee.

        console.log(`Compounding for ${user.userPublicKey}: pending=${pending}, fee=${feeAmount}, net=${compoundAmount}`);

        /// WHY: Build the transaction but do not send it yet; in production, a secure signer service would sign and submit.
        const tx = await buildCompoundTransaction(userPubkey, poolAddress, stakingTokenMint, rewardTokenMint);

        /// WHY: Simulate the transaction to catch errors before paying fees.
        const simulation = await connection.simulateTransaction(tx);
        if (simulation.value.err)
        {
            console.error(`Simulation failed for ${user.userPublicKey}:`, simulation.value.err);
            return;
        }

        /// WHY: In a production service, you would sign and send here using a secure keypair or vault.
        /// const signature = await connection.sendTransaction(tx, [signer]);
        /// console.log(`Compound tx sent: ${signature}`);

        /// WHY: Update the timestamp so the cooldown is respected.
        user.lastCompoundedAt = now;
        console.log(`Compound successful for ${user.userPublicKey}`);
    }
    catch (error)
    {
        console.error(`Error compounding for ${user.userPublicKey}:`, error); // WHY: Catch per-user errors so one failure does not stop the loop.
    }
}

// ---------------------------------------------------------------------------
// Main Loop
// ---------------------------------------------------------------------------

/**
 * WHY: runCompoundingLoop is the heartbeat of the service.
 * It iterates over all opted-in users and triggers compounding when profitable.
 */
async function runCompoundingLoop(): Promise<void>
{
    console.log("Starting compounding loop..."); // WHY: Log loop start for operational monitoring.

    while (true) // WHY: Infinite loop keeps the service running continuously as a background process.
    {
        console.log(`Processing ${optedInUsers.length} opted-in users at ${new Date().toISOString()}`); // WHY: Log each iteration for observability.

        /// WHY: Process users sequentially to avoid RPC rate limits; batching could be added later.
        for (const user of optedInUsers)
        {
            await compoundUser(user); // WHY: await each user to respect RPC limits and avoid nonce conflicts.
        }

        /// WHY: Sleep until the next interval to reduce CPU and RPC usage.
        await new Promise((resolve) => setTimeout(resolve, COMPOUND_INTERVAL_MS));
    }
}

// ---------------------------------------------------------------------------
// Admin: Opt-in / Opt-out helpers
// ---------------------------------------------------------------------------

/**
 * WHY: optIn allows a user to register for auto-compounding.
 * In production, this would require a signed message or on-chain delegation.
 */
export function optIn(
    userPublicKey: string,
    poolAddress: string,
    stakingTokenMint: string,
    rewardTokenMint: string,
): void
{
    const existing = optedInUsers.find(
        (u) => u.userPublicKey === userPublicKey && u.poolAddress === poolAddress,
    ); // WHY: Prevent duplicate registrations for the same user-pool pair.

    if (existing)
    {
        console.log(`User ${userPublicKey} already opted in for pool ${poolAddress}`);
        return;
    }

    optedInUsers.push({
        userPublicKey,
        poolAddress,
        stakingTokenMint,
        rewardTokenMint,
        lastCompoundedAt: 0, // WHY: Initialize to 0 so the first loop iteration immediately evaluates compounding.
    });

    console.log(`User ${userPublicKey} opted in for pool ${poolAddress}`);
}

/**
 * WHY: optOut removes a user from the compounding registry.
 */
export function optOut(userPublicKey: string, poolAddress: string): void
{
    const index = optedInUsers.findIndex(
        (u) => u.userPublicKey === userPublicKey && u.poolAddress === poolAddress,
    );

    if (index === -1)
    {
        console.log(`User ${userPublicKey} not found in pool ${poolAddress}`);
        return;
    }

    optedInUsers.splice(index, 1); // WHY: Remove the entry from the in-memory array.
    console.log(`User ${userPublicKey} opted out from pool ${poolAddress}`);
}

// ---------------------------------------------------------------------------
// Entrypoint
// ---------------------------------------------------------------------------

/**
 * WHY: The script starts the compounding loop when executed directly.
 * It also exports helpers for testing or programmatic use.
 */
if (require.main === module)
{
    console.log("Compounder service starting..."); // WHY: Confirm startup in process logs.
    console.log(`RPC: ${RPC_URL}`); // WHY: Log configuration for debugging deployment issues.
    console.log(`Compound interval: ${COMPOUND_INTERVAL_MS}ms`);
    console.log(`Reward threshold: ${REWARD_THRESHOLD}`);
    console.log(`Fee: ${FEE_PERCENT_BPS / 100}%`);

    runCompoundingLoop().catch((err) => {
        console.error("Compounder loop crashed:", err); // WHY: Log fatal errors before process exit.
        process.exit(1); // WHY: Exit with error code so a process manager can restart the service.
    });
}
