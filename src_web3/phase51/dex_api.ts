// WHY: We import express to create the HTTP server that clients will interact with.
import express, { Request, Response } from "express";
// WHY: We import body-parser so JSON payloads in POST requests are automatically parsed into objects.
import bodyParser from "body-parser";
// WHY: We import the Solana web3 library to build transactions and interact with the blockchain.
import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  SystemProgram,
  SYSVAR_RENT_PUBKEY,
  SYSVAR_CLOCK_PUBKEY,
} from "@solana/web3.js";
// WHY: We import SPL Token utilities to handle token account instructions and addresses.
import {
  TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  createAssociatedTokenAccountInstruction,
} from "@solana/spl-token";
// WHY: We import fs to read the deployer's keypair from the local filesystem.
import fs from "fs";
// WHY: We import path to safely construct the path to the keypair file.
import path from "path";

// WHY: We initialize the express application.
const app = express();
// WHY: We apply body-parser middleware so every route can access req.body as JSON.
app.use(bodyParser.json());

// WHY: We define the port the API will listen on, as specified in the project requirements.
const PORT = 3055;

// WHY: We connect to Solana devnet so we can test without spending real SOL.
const connection = new Connection("https://api.devnet.solana.com", "confirmed");

// WHY: We load the deployer's keypair from the default Solana CLI location.
// This keypair pays for transactions and acts as the default signer.
const keypairPath = path.join(
  process.env.HOME || "",
  ".config",
  "solana",
  "id.json"
);
// WHY: If the keypair file is missing, we throw immediately so the operator knows to configure a wallet.
if (!fs.existsSync(keypairPath)) {
  throw new Error(`Keypair not found at ${keypairPath}. Run solana-keygen new.`);
}
const secretKey = Uint8Array.from(JSON.parse(fs.readFileSync(keypairPath, "utf-8")));
const payer = Keypair.fromSecretKey(secretKey);

// WHY: These are the program IDs after deployment. In a real environment, these come from environment variables.
const AMM_POOL_PROGRAM_ID = new PublicKey("AMM1111111111111111111111111111111111111111");
const LIMIT_ORDER_PROGRAM_ID = new PublicKey("LMTORD2222222222222222222222222222222222222");

// WHY: This helper creates a transaction instruction for the AMM pool initialize instruction.
// It requires the initializer to sign and fund the pool state account.
async function buildInitializePoolInstruction(
  initializer: PublicKey,
  poolState: PublicKey,
  tokenAMint: PublicKey,
  tokenBMint: PublicKey,
  tokenAVault: PublicKey,
  tokenBVault: PublicKey,
  poolAuthority: PublicKey
): Promise<TransactionInstruction> {
  // WHY: We pack the instruction data with tag 0 to match the Rust program's dispatch logic.
  const data = Buffer.from([0]);
  return new TransactionInstruction({
    keys: [
      { pubkey: initializer, isSigner: true, isWritable: true },
      { pubkey: poolState, isSigner: false, isWritable: true },
      { pubkey: tokenAMint, isSigner: false, isWritable: false },
      { pubkey: tokenBMint, isSigner: false, isWritable: false },
      { pubkey: tokenAVault, isSigner: false, isWritable: true },
      { pubkey: tokenBVault, isSigner: false, isWritable: true },
      { pubkey: poolAuthority, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: AMM_POOL_PROGRAM_ID,
    data,
  });
}

// WHY: This route initializes a new AMM pool with two token mints.
app.post("/pool/initialize", async (req: Request, res: Response) => {
  try {
    // WHY: We destructure the request body to get the two token mints the user wants to pair.
    const { tokenAMint, tokenBMint } = req.body;
    // WHY: We validate that both mints were provided so we don't submit an invalid transaction.
    if (!tokenAMint || !tokenBMint) {
      return res.status(400).json({ error: "tokenAMint and tokenBMint are required" });
    }

    const mintA = new PublicKey(tokenAMint);
    const mintB = new PublicKey(tokenBMint);

    // WHY: We generate a new keypair for the pool state account so it has a unique address.
    const poolState = Keypair.generate();
    // WHY: We derive the pool authority PDA deterministically so it matches the Rust program's expectation.
    const [poolAuthority] = PublicKey.findProgramAddressSync(
      [Buffer.from("pool_authority")],
      AMM_POOL_PROGRAM_ID
    );
    // WHY: We get the associated token addresses for the pool vaults so the program can own them.
    const tokenAVault = await getAssociatedTokenAddress(mintA, poolAuthority, true);
    const tokenBVault = await getAssociatedTokenAddress(mintB, poolAuthority, true);

    // WHY: We build the instruction that will create the pool on-chain.
    const ix = await buildInitializePoolInstruction(
      payer.publicKey,
      poolState.publicKey,
      mintA,
      mintB,
      tokenAVault,
      tokenBVault,
      poolAuthority
    );

    // WHY: We create a transaction, add the instruction, and send it with the payer and pool state signers.
    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer, poolState]);

    // WHY: We return the transaction signature and the pool state address so the client can track it.
    return res.json({ signature, poolState: poolState.publicKey.toBase58() });
  } catch (err: any) {
    // WHY: We catch any error and return a 500 so the client knows something went wrong on the server.
    console.error("Initialize pool error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route lets a user deposit liquidity into an existing pool.
app.post("/pool/deposit", async (req: Request, res: Response) => {
  try {
    // WHY: We read the pool state address and the depositor's token accounts from the request.
    const { poolState, depositorAAccount, depositorBAccount } = req.body;
    if (!poolState || !depositorAAccount || !depositorBAccount) {
      return res.status(400).json({ error: "poolState, depositorAAccount, and depositorBAccount are required" });
    }

    const poolStatePubkey = new PublicKey(poolState);
    const poolAuthority = PublicKey.findProgramAddressSync(
      [Buffer.from("pool_authority")],
      AMM_POOL_PROGRAM_ID
    )[0];

    // WHY: We fetch the pool state account to read the mints and vaults.
    const accountInfo = await connection.getAccountInfo(poolStatePubkey);
    if (!accountInfo) {
      return res.status(404).json({ error: "Pool state not found" });
    }
    // WHY: We parse the token mints from the serialized state. In a real implementation, we would use a proper schema.
    // For this example, we assume the vaults are the 64th and 96th bytes (simplified).
    const tokenAVault = new PublicKey(accountInfo.data.slice(64, 96));
    const tokenBVault = new PublicKey(accountInfo.data.slice(96, 128));

    // WHY: We pack the instruction data with tag 1 for deposit_liquidity.
    const data = Buffer.from([1]);
    const ix = new TransactionInstruction({
      keys: [
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        { pubkey: poolStatePubkey, isSigner: false, isWritable: true },
        { pubkey: new PublicKey(depositorAAccount), isSigner: false, isWritable: true },
        { pubkey: new PublicKey(depositorBAccount), isSigner: false, isWritable: true },
        { pubkey: tokenAVault, isSigner: false, isWritable: true },
        { pubkey: tokenBVault, isSigner: false, isWritable: true },
        { pubkey: poolAuthority, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: AMM_POOL_PROGRAM_ID,
      data,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer]);
    return res.json({ signature });
  } catch (err: any) {
    console.error("Deposit error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route executes a swap against the AMM pool.
app.post("/pool/swap", async (req: Request, res: Response) => {
  try {
    // WHY: We read the pool, user accounts, direction, amount, and slippage tolerance.
    const { poolState, sourceAccount, destAccount, amountIn, minAmountOut } = req.body;
    if (!poolState || !sourceAccount || !destAccount || amountIn == null || minAmountOut == null) {
      return res.status(400).json({ error: "Missing required swap parameters" });
    }

    const poolStatePubkey = new PublicKey(poolState);
    const poolAuthority = PublicKey.findProgramAddressSync(
      [Buffer.from("pool_authority")],
      AMM_POOL_PROGRAM_ID
    )[0];

    const accountInfo = await connection.getAccountInfo(poolStatePubkey);
    if (!accountInfo) {
      return res.status(404).json({ error: "Pool state not found" });
    }
    const tokenAVault = new PublicKey(accountInfo.data.slice(64, 96));
    const tokenBVault = new PublicKey(accountInfo.data.slice(96, 128));

    // WHY: We serialize amountIn and minAmountOut as little-endian u64 values and prefix with instruction tag 2.
    const amountInBuf = Buffer.alloc(8);
    amountInBuf.writeBigUInt64LE(BigInt(amountIn));
    const minAmountOutBuf = Buffer.alloc(8);
    minAmountOutBuf.writeBigUInt64LE(BigInt(minAmountOut));
    const data = Buffer.concat([Buffer.from([2]), amountInBuf, minAmountOutBuf]);

    const ix = new TransactionInstruction({
      keys: [
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        { pubkey: poolStatePubkey, isSigner: false, isWritable: true },
        { pubkey: new PublicKey(sourceAccount), isSigner: false, isWritable: true },
        { pubkey: new PublicKey(destAccount), isSigner: false, isWritable: true },
        { pubkey: tokenAVault, isSigner: false, isWritable: true },
        { pubkey: tokenBVault, isSigner: false, isWritable: true },
        { pubkey: poolAuthority, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: AMM_POOL_PROGRAM_ID,
      data,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer]);
    return res.json({ signature });
  } catch (err: any) {
    console.error("Swap error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route lets a user withdraw their liquidity by burning LP shares.
app.post("/pool/withdraw", async (req: Request, res: Response) => {
  try {
    const { poolState, withdrawerAAccount, withdrawerBAccount, shares } = req.body;
    if (!poolState || !withdrawerAAccount || !withdrawerBAccount || shares == null) {
      return res.status(400).json({ error: "Missing required withdraw parameters" });
    }

    const poolStatePubkey = new PublicKey(poolState);
    const poolAuthority = PublicKey.findProgramAddressSync(
      [Buffer.from("pool_authority")],
      AMM_POOL_PROGRAM_ID
    )[0];

    const accountInfo = await connection.getAccountInfo(poolStatePubkey);
    if (!accountInfo) {
      return res.status(404).json({ error: "Pool state not found" });
    }
    const tokenAVault = new PublicKey(accountInfo.data.slice(64, 96));
    const tokenBVault = new PublicKey(accountInfo.data.slice(96, 128));

    // WHY: We serialize shares as little-endian u64 and prefix with instruction tag 3.
    const sharesBuf = Buffer.alloc(8);
    sharesBuf.writeBigUInt64LE(BigInt(shares));
    const data = Buffer.concat([Buffer.from([3]), sharesBuf]);

    const ix = new TransactionInstruction({
      keys: [
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        { pubkey: poolStatePubkey, isSigner: false, isWritable: true },
        { pubkey: new PublicKey(withdrawerAAccount), isSigner: false, isWritable: true },
        { pubkey: new PublicKey(withdrawerBAccount), isSigner: false, isWritable: true },
        { pubkey: tokenAVault, isSigner: false, isWritable: true },
        { pubkey: tokenBVault, isSigner: false, isWritable: true },
        { pubkey: poolAuthority, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: AMM_POOL_PROGRAM_ID,
      data,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer]);
    return res.json({ signature });
  } catch (err: any) {
    console.error("Withdraw error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route places a limit order by creating an order account and escrowing tokens.
app.post("/order/place", async (req: Request, res: Response) => {
  try {
    const { inputMint, outputMint, inputAmount, limitPrice } = req.body;
    if (!inputMint || !outputMint || inputAmount == null || limitPrice == null) {
      return res.status(400).json({ error: "Missing required order parameters" });
    }

    const orderAccount = Keypair.generate();
    const escrowAuthority = PublicKey.findProgramAddressSync(
      [Buffer.from("escrow_authority")],
      LIMIT_ORDER_PROGRAM_ID
    )[0];
    const inputMintPubkey = new PublicKey(inputMint);
    const traderInputTokenAccount = await getAssociatedTokenAddress(inputMintPubkey, payer.publicKey);
    const escrowTokenAccount = await getAssociatedTokenAddress(inputMintPubkey, escrowAuthority, true);

    const inputAmountBuf = Buffer.alloc(8);
    inputAmountBuf.writeBigUInt64LE(BigInt(inputAmount));
    const limitPriceBuf = Buffer.alloc(8);
    limitPriceBuf.writeBigUInt64LE(BigInt(limitPrice));
    const data = Buffer.concat([Buffer.from([0]), inputAmountBuf, limitPriceBuf]);

    const ix = new TransactionInstruction({
      keys: [
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        { pubkey: orderAccount.publicKey, isSigner: true, isWritable: true },
        { pubkey: traderInputTokenAccount, isSigner: false, isWritable: true },
        { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
        { pubkey: escrowAuthority, isSigner: false, isWritable: false },
        { pubkey: inputMintPubkey, isSigner: false, isWritable: false },
        { pubkey: new PublicKey(outputMint), isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
        { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false },
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
      ],
      programId: LIMIT_ORDER_PROGRAM_ID,
      data,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer, orderAccount]);
    return res.json({ signature, orderAccount: orderAccount.publicKey.toBase58() });
  } catch (err: any) {
    console.error("Place order error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route cancels an active order and refunds the escrowed tokens to the owner.
app.post("/order/cancel", async (req: Request, res: Response) => {
  try {
    const { orderAccount } = req.body;
    if (!orderAccount) {
      return res.status(400).json({ error: "orderAccount is required" });
    }

    const orderPubkey = new PublicKey(orderAccount);
    const escrowAuthority = PublicKey.findProgramAddressSync(
      [Buffer.from("escrow_authority")],
      LIMIT_ORDER_PROGRAM_ID
    )[0];

    // WHY: We fetch the order account to determine the input mint for the refund destination.
    const orderInfo = await connection.getAccountInfo(orderPubkey);
    if (!orderInfo) {
      return res.status(404).json({ error: "Order account not found" });
    }
    const inputMint = new PublicKey(orderInfo.data.slice(32, 64));
    const ownerOutputTokenAccount = await getAssociatedTokenAddress(inputMint, payer.publicKey);
    const escrowTokenAccount = await getAssociatedTokenAddress(inputMint, escrowAuthority, true);

    const data = Buffer.from([1]);
    const ix = new TransactionInstruction({
      keys: [
        { pubkey: payer.publicKey, isSigner: true, isWritable: true },
        { pubkey: orderPubkey, isSigner: false, isWritable: true },
        { pubkey: ownerOutputTokenAccount, isSigner: false, isWritable: true },
        { pubkey: escrowTokenAccount, isSigner: false, isWritable: true },
        { pubkey: escrowAuthority, isSigner: false, isWritable: false },
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      ],
      programId: LIMIT_ORDER_PROGRAM_ID,
      data,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(connection, tx, [payer]);
    return res.json({ signature });
  } catch (err: any) {
    console.error("Cancel order error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route returns a simulated view of the order book.
// In a full implementation, this would query an indexer or scan all order accounts.
app.get("/order/book", async (_req: Request, res: Response) => {
  try {
    // WHY: We fetch all accounts owned by the limit order program.
    const accounts = await connection.getProgramAccounts(LIMIT_ORDER_PROGRAM_ID);
    const orders = accounts.map(({ pubkey, account }) => {
      // WHY: We parse the order data. The structure is: owner(32), input_mint(32), output_mint(32), input_amount(8), limit_price(8), is_active(1)...
      const data = account.data;
      return {
        address: pubkey.toBase58(),
        owner: new PublicKey(data.slice(0, 32)).toBase58(),
        inputMint: new PublicKey(data.slice(32, 64)).toBase58(),
        outputMint: new PublicKey(data.slice(64, 96)).toBase58(),
        inputAmount: Number(data.readBigUInt64LE(96)),
        limitPrice: Number(data.readBigUInt64LE(104)),
        isActive: data[112] !== 0,
      };
    });
    return res.json({ orders });
  } catch (err: any) {
    console.error("Get book error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: This route finds the best path for a swap, either direct or multi-hop.
app.post("/route/best-path", async (req: Request, res: Response) => {
  try {
    const { inputMint, outputMint, amountIn } = req.body;
    if (!inputMint || !outputMint || amountIn == null) {
      return res.status(400).json({ error: "inputMint, outputMint, and amountIn are required" });
    }

    // WHY: In a real router, we would query a graph of all pools. Here we simulate a direct pool check.
    // We fetch all program accounts and look for a pool state that matches the requested mint pair.
    const poolAccounts = await connection.getProgramAccounts(AMM_POOL_PROGRAM_ID);
    let bestPath: string[] | null = null;
    let bestOutput = 0;

    for (const { pubkey, account } of poolAccounts) {
      const data = account.data;
      const poolMintA = new PublicKey(data.slice(0, 32)).toBase58();
      const poolMintB = new PublicKey(data.slice(32, 64)).toBase58();
      // WHY: We check if this pool contains the exact pair requested.
      if (
        (poolMintA === inputMint && poolMintB === outputMint) ||
        (poolMintA === outputMint && poolMintB === inputMint)
      ) {
        // WHY: We read the vault balances from the chain to compute the current price.
        const vaultA = new PublicKey(data.slice(64, 96));
        const vaultB = new PublicKey(data.slice(96, 128));
        const vaultAInfo = await connection.getTokenAccountBalance(vaultA);
        const vaultBInfo = await connection.getTokenAccountBalance(vaultB);
        const reserveA = Number(vaultAInfo.value.amount);
        const reserveB = Number(vaultBInfo.value.amount);

        // WHY: We simulate the constant product swap with fees.
        const feeNum = 3;
        const feeDen = 1000;
        const amountInWithFee = (amountIn * feeNum) / feeDen;
        const numerator = reserveA * reserveB;
        const denominator = reserveA + amountInWithFee;
        const amountOut = reserveB - numerator / denominator;

        if (amountOut > bestOutput) {
          bestOutput = amountOut;
          bestPath = [inputMint, outputMint];
        }
      }
    }

    // WHY: If no direct pool is found, we return a suggestion for a multi-hop route.
    if (!bestPath) {
      return res.json({
        path: null,
        output: null,
        suggestion: "No direct pool found. A multi-hop route would be evaluated here.",
      });
    }

    return res.json({ path: bestPath, expectedOutput: bestOutput });
  } catch (err: any) {
    console.error("Route error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// WHY: We start the Express server so it can accept incoming HTTP requests.
app.listen(PORT, () => {
  console.log(`DEX API server listening on port ${PORT}`);
});
