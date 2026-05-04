import express from "express";
// WHY: Import Solana classes to build and send transactions to the lending program.
import {
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  SYSVAR_CLOCK_PUBKEY,
} from "@solana/web3.js";
// WHY: Import fs to read the payer keypair from the local filesystem.
import fs from "fs";

// WHY: Create the Express application to register HTTP routes.
const app = express();
// WHY: Enable JSON body parsing so route handlers can read request payloads.
app.use(express.json());
// WHY: Use port 3056 as specified in the project requirements.
const PORT = 3056;

// WHY: Read the RPC URL from environment or default to a local validator.
const RPC_URL = process.env.RPC_URL || "http://localhost:8899";
// WHY: Create a connection to the Solana cluster with confirmed commitment for reliable reads.
const connection = new Connection(RPC_URL, "confirmed");

// WHY: Load the payer keypair path from environment or use the Solana CLI default.
const PAYER_KEYPAIR_PATH =
  process.env.PAYER_KEYPAIR_PATH || "/Users/zen/.config/solana/id.json";
// WHY: Read the keypair file as a UTF-8 string so it can be parsed as JSON.
const payerSecret = JSON.parse(fs.readFileSync(PAYER_KEYPAIR_PATH, "utf-8"));
// WHY: Convert the JSON array into a Uint8Array and construct a Keypair for signing.
const payer = Keypair.fromSecretKey(Uint8Array.from(payerSecret));

// WHY: Load the lending program ID from environment or use a placeholder.
const LENDING_PROGRAM_ID = new PublicKey(
  process.env.LENDING_PROGRAM_ID ||
    "Lending111111111111111111111111111111111111"
);
// WHY: Define the SPL Token program ID because token transfers require it as an account.
const TOKEN_PROGRAM_ID = new PublicKey(
  "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
);

// WHY: Convert a JavaScript number into an 8-byte little-endian buffer for u64 instruction data.
function u64ToBuffer(value: number): Buffer {
  // WHY: Allocate exactly 8 bytes because Solana BPF expects u64 to occupy 8 bytes.
  const buf = Buffer.alloc(8);
  // WHY: Write as little-endian using BigInt to safely handle values above 2^53.
  buf.writeBigUInt64LE(BigInt(value), 0);
  // WHY: Return the buffer so it can be concatenated into instruction data.
  return buf;
}

// WHY: Build the instruction payload by combining a 1-byte variant tag with an 8-byte amount.
function buildInstruction(variant: number, amount: number): Buffer {
  // WHY: Create the 1-byte tag that matches the Borsh enum variant index in the Rust program.
  const tag = Buffer.from([variant]);
  // WHY: Append the serialized u64 amount after the tag.
  const amountBuf = u64ToBuffer(amount);
  // WHY: Concatenate tag and amount into a single buffer for the instruction data field.
  return Buffer.concat([tag, amountBuf]);
}

// WHY: Helper to read a single unsigned byte from a buffer at a given offset.
function readUInt8(data: Buffer, offset: number): number {
  return data.readUInt8(offset);
}

// WHY: Helper to read a u64 from a buffer in little-endian format.
function readUInt64LE(data: Buffer, offset: number): number {
  return Number(data.readBigUInt64LE(offset));
}

// WHY: Helper to read an i64 from a buffer in little-endian format.
function readInt64LE(data: Buffer, offset: number): number {
  return Number(data.readBigInt64LE(offset));
}

// WHY: Helper to read a u128 from a buffer by combining two little-endian u64 halves.
function readUInt128LE(data: Buffer, offset: number): bigint {
  // WHY: Read the low 64 bits first.
  const low = data.readBigUInt64LE(offset);
  // WHY: Read the high 64 bits from the next 8 bytes.
  const high = data.readBigUInt64LE(offset + 8);
  // WHY: Combine high and low into a single 128-bit integer.
  return (high << BigInt(64)) | low;
}

// WHY: Deserialize raw account data into a MarketState object matching the Rust layout.
function deserializeMarketState(data: Buffer): any {
  // WHY: Start reading from byte offset 0.
  let o = 0;
  // WHY: Read the initialization flag as a boolean.
  const isInitialized = readUInt8(data, o) === 1;
  o += 1;
  // WHY: Read total deposits as u64.
  const totalDeposits = readUInt64LE(data, o);
  o += 8;
  // WHY: Read total borrows as u64.
  const totalBorrows = readUInt64LE(data, o);
  o += 8;
  // WHY: Read collateral factor as u64.
  const collateralFactor = readUInt64LE(data, o);
  o += 8;
  // WHY: Read liquidation bonus as u64.
  const liquidationBonus = readUInt64LE(data, o);
  o += 8;
  // WHY: Read close factor as u64.
  const closeFactor = readUInt64LE(data, o);
  o += 8;
  // WHY: Read base rate as u64.
  const baseRate = readUInt64LE(data, o);
  o += 8;
  // WHY: Read slope1 as u64.
  const slope1 = readUInt64LE(data, o);
  o += 8;
  // WHY: Read slope2 as u64.
  const slope2 = readUInt64LE(data, o);
  o += 8;
  // WHY: Read optimal utilization as u64.
  const optimalUtilization = readUInt64LE(data, o);
  o += 8;
  // WHY: Read reserve factor as u64.
  const reserveFactor = readUInt64LE(data, o);
  o += 8;
  // WHY: Read borrow index as u128.
  const borrowIndex = readUInt128LE(data, o);
  o += 16;
  // WHY: Read last update time as i64.
  const lastUpdateTime = readInt64LE(data, o);
  o += 8;
  // WHY: Return an object with named fields so route handlers can access metrics easily.
  return {
    isInitialized,
    totalDeposits,
    totalBorrows,
    collateralFactor,
    liquidationBonus,
    closeFactor,
    baseRate,
    slope1,
    slope2,
    optimalUtilization,
    reserveFactor,
    borrowIndex,
    lastUpdateTime,
  };
}

// WHY: Deserialize raw account data into a UserPosition object matching the Rust layout.
function deserializeUserPosition(data: Buffer): any {
  let o = 0;
  const isInitialized = readUInt8(data, o) === 1;
  o += 1;
  const collateralDeposited = readUInt64LE(data, o);
  o += 8;
  const borrowPrincipal = readUInt64LE(data, o);
  o += 8;
  const borrowIndexSnapshot = readUInt128LE(data, o);
  o += 16;
  return {
    isInitialized,
    collateralDeposited,
    borrowPrincipal,
    borrowIndexSnapshot,
  };
}

// WHY: Deserialize raw account data into an OracleState object matching the Rust layout.
function deserializeOracleState(data: Buffer): any {
  let o = 0;
  const isInitialized = readUInt8(data, o) === 1;
  o += 1;
  // WHY: Read the 32-byte authority public key.
  const authority = new PublicKey(data.slice(o, o + 32));
  o += 32;
  const price = readUInt64LE(data, o);
  o += 8;
  const decimals = readUInt8(data, o);
  o += 1;
  return { isInitialized, authority, price, decimals };
}

// WHY: Compute the user's current debt by scaling principal with the global borrow index.
function getCurrentBorrowBalance(user: any, market: any): bigint {
  // WHY: Return zero immediately if the user has never borrowed.
  if (user.borrowPrincipal === 0) return BigInt(0);
  // WHY: Scale the principal by the ratio of current index to snapshot index.
  return (
    BigInt(user.borrowPrincipal) * market.borrowIndex
  ) / user.borrowIndexSnapshot;
}

// WHY: Compute pool utilization as total borrows divided by total deposits in basis points.
function getUtilization(market: any): number {
  // WHY: Avoid division by zero when the pool has no collateral yet.
  if (market.totalDeposits === 0) return 0;
  // WHY: Multiply by BASIS_POINTS first so the result stays in integer basis points.
  return Math.floor(
    (market.totalBorrows * 10000) / market.totalDeposits
  );
}

// WHY: Implement the piecewise linear interest rate model to match on-chain logic.
function getBorrowRate(utilization: number, market: any): number {
  // WHY: Use slope1 below the optimal kink for slow rate growth.
  if (utilization <= market.optimalUtilization) {
    return (
      market.baseRate +
      Math.floor((utilization * market.slope1) / market.optimalUtilization)
    );
  }
  // WHY: Use slope2 above the kink for aggressive rate growth during high utilization.
  const extra1 = market.slope1;
  const extra2 = Math.floor(
    ((utilization - market.optimalUtilization) * market.slope2) /
      (10000 - market.optimalUtilization)
  );
  return market.baseRate + extra1 + extra2;
}

// WHY: Compute the health factor exactly as the on-chain program does.
function getHealthFactor(user: any, market: any, oracle: any): number {
  // WHY: Multiply collateral amount by price to get dollar-denominated value.
  const collateralValue =
    BigInt(user.collateralDeposited) * BigInt(oracle.price);
  // WHY: Adjust for oracle decimals so the value is in base units.
  let collateralValueAdj = collateralValue;
  if (oracle.decimals > 0) {
    collateralValueAdj =
      collateralValue / BigInt(Math.pow(10, oracle.decimals));
  }
  // WHY: Apply the collateral factor to find effective borrowing power.
  const weightedCollateral =
    (collateralValueAdj * BigInt(market.collateralFactor)) /
    BigInt(10000);
  // WHY: Load current debt including accrued interest.
  const borrowBalance = getCurrentBorrowBalance(user, market);
  // WHY: Return infinity when there is no debt so the position is always safe.
  if (borrowBalance === BigInt(0)) return Number.MAX_SAFE_INTEGER;
  // WHY: Divide weighted collateral by debt and scale by BASIS_POINTS.
  return Number(
    (weightedCollateral * BigInt(10000)) / borrowBalance
  );
}

// WHY: POST /deposit lets a user lock collateral tokens into the lending pool.
app.post("/deposit", async (req, res) => {
  // WHY: Destructure the request body to extract all account addresses and the deposit amount.
  const {
    amount,
    marketState,
    userPosition,
    userCollateralTokenAccount,
    protocolCollateralTokenAccount,
  } = req.body;
  // WHY: Build a TransactionInstruction that matches the Rust Deposit handler account list.
  const ix = new TransactionInstruction({
    keys: [
      // WHY: Market state is writable because total deposits will increase.
      { pubkey: new PublicKey(marketState), isSigner: false, isWritable: true },
      // WHY: User position is writable because collateral deposited will increase.
      { pubkey: new PublicKey(userPosition), isSigner: false, isWritable: true },
      // WHY: The user must sign to authorize the token transfer.
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
      // WHY: The user's token account is writable because tokens leave it.
      { pubkey: new PublicKey(userCollateralTokenAccount), isSigner: false, isWritable: true },
      // WHY: The protocol token account is writable because tokens enter it.
      { pubkey: new PublicKey(protocolCollateralTokenAccount), isSigner: false, isWritable: true },
      // WHY: SPL Token program is required to execute the token transfer.
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      // WHY: Clock sysvar is required so the program can read the current timestamp.
      { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: LENDING_PROGRAM_ID,
    // WHY: Variant 1 corresponds to the Deposit instruction in the Rust enum.
    data: buildInstruction(1, amount),
  });
  // WHY: Wrap the instruction in a Transaction so it can be signed and sent.
  const tx = new Transaction().add(ix);
  // WHY: Send and confirm the transaction using the payer keypair.
  const sig = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });
  // WHY: Return the transaction signature so the caller can track it on-chain.
  res.json({ success: true, signature: sig });
});

// WHY: POST /borrow lets a user withdraw loan tokens against their deposited collateral.
app.post("/borrow", async (req, res) => {
  const {
    amount,
    marketState,
    userPosition,
    oracleAccount,
    protocolBorrowTokenAccount,
    userBorrowTokenAccount,
    protocolAuthority,
  } = req.body;
  const ix = new TransactionInstruction({
    keys: [
      { pubkey: new PublicKey(marketState), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(userPosition), isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
      // WHY: Oracle is read-only because the program only needs the current price.
      { pubkey: new PublicKey(oracleAccount), isSigner: false, isWritable: false },
      // WHY: Protocol borrow account loses tokens when the user withdraws.
      { pubkey: new PublicKey(protocolBorrowTokenAccount), isSigner: false, isWritable: true },
      // WHY: User borrow account receives the withdrawn loan tokens.
      { pubkey: new PublicKey(userBorrowTokenAccount), isSigner: false, isWritable: true },
      // WHY: Protocol authority signs the transfer via CPI because it owns the protocol token account.
      { pubkey: new PublicKey(protocolAuthority), isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: LENDING_PROGRAM_ID,
    // WHY: Variant 2 corresponds to the Borrow instruction in the Rust enum.
    data: buildInstruction(2, amount),
  });
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });
  res.json({ success: true, signature: sig });
});

// WHY: POST /repay lets a user return loan tokens and reduce their debt.
app.post("/repay", async (req, res) => {
  const {
    amount,
    marketState,
    userPosition,
    userBorrowTokenAccount,
    protocolBorrowTokenAccount,
  } = req.body;
  const ix = new TransactionInstruction({
    keys: [
      { pubkey: new PublicKey(marketState), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(userPosition), isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
      // WHY: User borrow account loses tokens when repaying.
      { pubkey: new PublicKey(userBorrowTokenAccount), isSigner: false, isWritable: true },
      // WHY: Protocol borrow account receives the repaid tokens.
      { pubkey: new PublicKey(protocolBorrowTokenAccount), isSigner: false, isWritable: true },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: LENDING_PROGRAM_ID,
    // WHY: Variant 3 corresponds to the Repay instruction in the Rust enum.
    data: buildInstruction(3, amount),
  });
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });
  res.json({ success: true, signature: sig });
});

// WHY: POST /withdraw lets a user reclaim collateral if their health factor stays above 1.
app.post("/withdraw", async (req, res) => {
  const {
    amount,
    marketState,
    userPosition,
    oracleAccount,
    protocolCollateralTokenAccount,
    userCollateralTokenAccount,
    protocolAuthority,
  } = req.body;
  const ix = new TransactionInstruction({
    keys: [
      { pubkey: new PublicKey(marketState), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(userPosition), isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
      { pubkey: new PublicKey(oracleAccount), isSigner: false, isWritable: false },
      // WHY: Protocol collateral account loses tokens when returning collateral.
      { pubkey: new PublicKey(protocolCollateralTokenAccount), isSigner: false, isWritable: true },
      // WHY: User collateral account receives the withdrawn tokens.
      { pubkey: new PublicKey(userCollateralTokenAccount), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(protocolAuthority), isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: LENDING_PROGRAM_ID,
    // WHY: Variant 4 corresponds to the Withdraw instruction in the Rust enum.
    data: buildInstruction(4, amount),
  });
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });
  res.json({ success: true, signature: sig });
});

// WHY: POST /liquidate lets a third party repay bad debt and seize collateral at a discount.
app.post("/liquidate", async (req, res) => {
  const {
    repayAmount,
    marketState,
    borrowerPosition,
    oracleAccount,
    liquidatorRepayTokenAccount,
    protocolBorrowTokenAccount,
    protocolCollateralTokenAccount,
    liquidatorCollateralTokenAccount,
    protocolAuthority,
  } = req.body;
  const ix = new TransactionInstruction({
    keys: [
      { pubkey: new PublicKey(marketState), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(borrowerPosition), isSigner: false, isWritable: true },
      // WHY: The liquidator must sign to authorize spending their own repay tokens.
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
      { pubkey: new PublicKey(oracleAccount), isSigner: false, isWritable: false },
      { pubkey: new PublicKey(liquidatorRepayTokenAccount), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(protocolBorrowTokenAccount), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(protocolCollateralTokenAccount), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(liquidatorCollateralTokenAccount), isSigner: false, isWritable: true },
      { pubkey: new PublicKey(protocolAuthority), isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
    ],
    programId: LENDING_PROGRAM_ID,
    // WHY: Variant 5 corresponds to the Liquidate instruction in the Rust enum.
    data: buildInstruction(5, repayAmount),
  });
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });
  res.json({ success: true, signature: sig });
});

// WHY: GET /health-factor/:userPosition computes the current health factor off-chain.
app.get("/health-factor/:userPosition", async (req, res) => {
  // WHY: Extract the user position pubkey from the URL path parameter.
  const userPositionPubkey = new PublicKey(req.params.userPosition);
  // WHY: Read the market state and oracle addresses from query parameters.
  const marketStateParam = req.query.marketState as string;
  const oracleAccountParam = req.query.oracleAccount as string;
  // WHY: Validate that required query parameters are present.
  if (!marketStateParam || !oracleAccountParam) {
    // WHY: Return 400 so the caller knows which parameters are missing.
    return res.status(400).json({ error: "Missing marketState or oracleAccount query param" });
  }
  // WHY: Parse the query strings into PublicKey objects.
  const marketStatePubkey = new PublicKey(marketStateParam);
  const oraclePubkey = new PublicKey(oracleAccountParam);
  // WHY: Fetch all three accounts in a single RPC call to reduce latency.
  const [marketInfo, userInfo, oracleInfo] =
    await connection.getMultipleAccountsInfo(
      [marketStatePubkey, userPositionPubkey, oraclePubkey],
      "confirmed"
    );
  // WHY: Return 404 if any account is missing so the caller does not compute on stale data.
  if (!marketInfo || !userInfo || !oracleInfo) {
    return res.status(404).json({ error: "One or more accounts not found" });
  }
  // WHY: Deserialize raw buffers into typed objects using the known on-chain layout.
  const market = deserializeMarketState(marketInfo.data);
  const user = deserializeUserPosition(userInfo.data);
  const oracle = deserializeOracleState(oracleInfo.data);
  // WHY: Compute the health factor using the same formula as the Rust program.
  const hf = getHealthFactor(user, market, oracle);
  // WHY: Also compute the current debt so the response includes both metrics.
  const currentDebt = getCurrentBorrowBalance(user, market);
  // WHY: Return a JSON object with both raw and human-readable health factor values.
  res.json({
    healthFactor: hf,
    healthFactorFormatted: (hf / 10000).toFixed(4),
    currentDebt: currentDebt.toString(),
    collateralDeposited: user.collateralDeposited,
  });
});

// WHY: GET /market-stats returns global pool metrics including utilization and rates.
app.get("/market-stats", async (req, res) => {
  // WHY: Read the market state address from a query parameter.
  const marketStateParam = req.query.marketState as string;
  if (!marketStateParam) {
    return res.status(400).json({ error: "Missing marketState query param" });
  }
  // WHY: Fetch the on-chain market state account.
  const info = await connection.getAccountInfo(
    new PublicKey(marketStateParam),
    "confirmed"
  );
  // WHY: Return 404 if the market has not been created yet.
  if (!info) {
    return res.status(404).json({ error: "Market state not found" });
  }
  // WHY: Deserialize the account buffer into a typed market object.
  const market = deserializeMarketState(info.data);
  // WHY: Compute utilization from total borrows and deposits.
  const utilization = getUtilization(market);
  // WHY: Compute the borrow rate from the interest rate model.
  const borrowRate = getBorrowRate(utilization, market);
  // WHY: Compute the supply rate by taking the lender share of total interest.
  const supplyRate = Math.floor(
    (borrowRate * utilization * (10000 - market.reserveFactor)) / 100000000
  );
  // WHY: Return all metrics in a single JSON response for dashboards and monitoring.
  res.json({
    totalDeposits: market.totalDeposits,
    totalBorrows: market.totalBorrows,
    utilization,
    utilizationFormatted: (utilization / 100).toFixed(2) + "%",
    borrowRate,
    borrowRateFormatted: (borrowRate / 100).toFixed(2) + "%",
    supplyRate,
    supplyRateFormatted: (supplyRate / 100).toFixed(2) + "%",
    collateralFactor: market.collateralFactor,
    liquidationBonus: market.liquidationBonus,
    closeFactor: market.closeFactor,
    optimalUtilization: market.optimalUtilization,
    reserveFactor: market.reserveFactor,
    borrowIndex: market.borrowIndex.toString(),
    lastUpdateTime: market.lastUpdateTime,
  });
});

// WHY: Start the HTTP server so clients can interact with the lending protocol.
app.listen(PORT, () => {
  console.log(`Lending API listening on port ${PORT}`);
});
