// WHY: Import Solana classes to read on-chain state and submit liquidation transactions.
import {
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  SYSVAR_CLOCK_PUBKEY,
} from "@solana/web3.js";
// WHY: Import fs to read the liquidator keypair from the filesystem.
import fs from "fs";

// WHY: Read the RPC endpoint from environment or default to a local validator.
const RPC_URL = process.env.RPC_URL || "http://localhost:8899";
// WHY: Create a connection with confirmed commitment to ensure state reads are reliable.
const connection = new Connection(RPC_URL, "confirmed");

// WHY: Load the liquidator keypair path from environment or use the Solana CLI default.
const LIQUIDATOR_KEYPAIR_PATH =
  process.env.LIQUIDATOR_KEYPAIR_PATH ||
  "/Users/zen/.config/solana/id.json";
// WHY: Parse the keypair JSON and construct a Keypair for signing transactions.
const liquidatorSecret = JSON.parse(
  fs.readFileSync(LIQUIDATOR_KEYPAIR_PATH, "utf-8")
);
const liquidator = Keypair.fromSecretKey(
  Uint8Array.from(liquidatorSecret)
);

// WHY: Load the lending program ID so the bot knows which accounts to scan.
const LENDING_PROGRAM_ID = new PublicKey(
  process.env.LENDING_PROGRAM_ID ||
    "Lending111111111111111111111111111111111111"
);
// WHY: Define the SPL Token program ID because liquidation involves token transfers.
const TOKEN_PROGRAM_ID = new PublicKey(
  "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
);

// WHY: Load the global market state address from environment variables.
const MARKET_STATE = new PublicKey(
  process.env.MARKET_STATE || ""
);
// WHY: Load the oracle account address so prices can be fetched for health checks.
const ORACLE_ACCOUNT = new PublicKey(
  process.env.ORACLE_ACCOUNT || ""
);
// WHY: Load the protocol borrow token account where repaid tokens are sent.
const PROTOCOL_BORROW_TOKEN_ACCOUNT = new PublicKey(
  process.env.PROTOCOL_BORROW_TOKEN_ACCOUNT || ""
);
// WHY: Load the protocol collateral token account where seized tokens come from.
const PROTOCOL_COLLATERAL_TOKEN_ACCOUNT = new PublicKey(
  process.env.PROTOCOL_COLLATERAL_TOKEN_ACCOUNT || ""
);
// WHY: Load the protocol authority PDA that signs outgoing collateral transfers.
const PROTOCOL_AUTHORITY = new PublicKey(
  process.env.PROTOCOL_AUTHORITY || ""
);
// WHY: Load the liquidator's repay token account so the bot can spend tokens to clear debt.
const LIQUIDATOR_REPAY_TOKEN_ACCOUNT = new PublicKey(
  process.env.LIQUIDATOR_REPAY_TOKEN_ACCOUNT || ""
);
// WHY: Load the liquidator's collateral token account to receive seized collateral.
const LIQUIDATOR_COLLATERAL_TOKEN_ACCOUNT = new PublicKey(
  process.env.LIQUIDATOR_COLLATERAL_TOKEN_ACCOUNT || ""
);

// WHY: Convert a number into an 8-byte little-endian buffer for instruction data.
function u64ToBuffer(value: number): Buffer {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

// WHY: Build instruction data by prefixing a variant tag to an 8-byte amount.
function buildInstruction(variant: number, amount: number): Buffer {
  const tag = Buffer.from([variant]);
  const amountBuf = u64ToBuffer(amount);
  return Buffer.concat([tag, amountBuf]);
}

// WHY: Read a single unsigned byte from a buffer at the specified offset.
function readUInt8(data: Buffer, offset: number): number {
  return data.readUInt8(offset);
}

// WHY: Read a u64 in little-endian from the buffer.
function readUInt64LE(data: Buffer, offset: number): number {
  return Number(data.readBigUInt64LE(offset));
}

// WHY: Read an i64 in little-endian from the buffer.
function readInt64LE(data: Buffer, offset: number): number {
  return Number(data.readBigInt64LE(offset));
}

// WHY: Read a u128 by combining two consecutive little-endian u64 values.
function readUInt128LE(data: Buffer, offset: number): bigint {
  const low = data.readBigUInt64LE(offset);
  const high = data.readBigUInt64LE(offset + 8);
  return (high << BigInt(64)) | low;
}

// WHY: Deserialize raw account data into a MarketState object to compute rates.
function deserializeMarketState(data: Buffer): any {
  let o = 0;
  const isInitialized = readUInt8(data, o) === 1;
  o += 1;
  const totalDeposits = readUInt64LE(data, o);
  o += 8;
  const totalBorrows = readUInt64LE(data, o);
  o += 8;
  const collateralFactor = readUInt64LE(data, o);
  o += 8;
  const liquidationBonus = readUInt64LE(data, o);
  o += 8;
  const closeFactor = readUInt64LE(data, o);
  o += 8;
  const baseRate = readUInt64LE(data, o);
  o += 8;
  const slope1 = readUInt64LE(data, o);
  o += 8;
  const slope2 = readUInt64LE(data, o);
  o += 8;
  const optimalUtilization = readUInt64LE(data, o);
  o += 8;
  const reserveFactor = readUInt64LE(data, o);
  o += 8;
  const borrowIndex = readUInt128LE(data, o);
  o += 16;
  const lastUpdateTime = readInt64LE(data, o);
  o += 8;
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

// WHY: Deserialize raw account data into a UserPosition object to evaluate risk.
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

// WHY: Deserialize raw account data into an OracleState object to read the price.
function deserializeOracleState(data: Buffer): any {
  let o = 0;
  const isInitialized = readUInt8(data, o) === 1;
  o += 1;
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
  if (user.borrowPrincipal === 0) return BigInt(0);
  return (
    BigInt(user.borrowPrincipal) * market.borrowIndex
  ) / user.borrowIndexSnapshot;
}

// WHY: Compute the health factor using the same formula as the on-chain program.
function getHealthFactor(user: any, market: any, oracle: any): number {
  const collateralValue =
    BigInt(user.collateralDeposited) * BigInt(oracle.price);
  let collateralValueAdj = collateralValue;
  if (oracle.decimals > 0) {
    collateralValueAdj =
      collateralValue / BigInt(Math.pow(10, oracle.decimals));
  }
  const weightedCollateral =
    (collateralValueAdj * BigInt(market.collateralFactor)) /
    BigInt(10000);
  const borrowBalance = getCurrentBorrowBalance(user, market);
  if (borrowBalance === BigInt(0)) return Number.MAX_SAFE_INTEGER;
  return Number(
    (weightedCollateral * BigInt(10000)) / borrowBalance
  );
}

// WHY: checkAndLiquidate scans all positions, finds underwater ones, and sends liquidation transactions.
async function checkAndLiquidate() {
  // WHY: Fetch the market state so the bot has the latest rate parameters and close factor.
  const marketInfo = await connection.getAccountInfo(
    MARKET_STATE,
    "confirmed"
  );
  // WHY: Abort if the market is missing to avoid computing against stale defaults.
  if (!marketInfo) {
    console.log("Market state not found");
    return;
  }
  // WHY: Deserialize the market account buffer into a typed object.
  const market = deserializeMarketState(marketInfo.data);

  // WHY: Fetch the oracle state so collateral can be accurately priced.
  const oracleInfo = await connection.getAccountInfo(
    ORACLE_ACCOUNT,
    "confirmed"
  );
  if (!oracleInfo) {
    console.log("Oracle not found");
    return;
  }
  const oracle = deserializeOracleState(oracleInfo.data);

  // WHY: Query all program accounts with the exact UserPosition data size to find every borrower.
  const accounts = await connection.getProgramAccounts(LENDING_PROGRAM_ID, {
    filters: [{ dataSize: 33 }],
  });

  // WHY: Iterate over every discovered account to evaluate its health.
  for (const { pubkey, account } of accounts) {
    // WHY: Deserialize the account data into a user position.
    const user = deserializeUserPosition(account.data);
    // WHY: Skip uninitialized accounts and positions with no debt.
    if (!user.isInitialized || user.borrowPrincipal === 0) {
      continue;
    }
    // WHY: Compute the health factor to determine if liquidation is allowed.
    const hf = getHealthFactor(user, market, oracle);
    // WHY: A health factor below 10000 means the position is underwater.
    if (hf < 10000) {
      // WHY: Compute the current debt so the bot knows how much to repay.
      const currentDebt = getCurrentBorrowBalance(user, market);
      // WHY: Cap the repay amount by the close factor to respect protocol rules.
      const repayAmount = Number(
        (currentDebt * BigInt(market.closeFactor)) / BigInt(10000)
      );
      // WHY: Build a Liquidate instruction that matches the Rust account list.
      const ix = new TransactionInstruction({
        keys: [
          // WHY: Market state is writable because total borrows and deposits change.
          { pubkey: MARKET_STATE, isSigner: false, isWritable: true },
          // WHY: Borrower position is writable because debt and collateral are reduced.
          { pubkey: pubkey, isSigner: false, isWritable: true },
          // WHY: The liquidator must sign to authorize spending their repay tokens.
          { pubkey: liquidator.publicKey, isSigner: true, isWritable: false },
          // WHY: Oracle is read-only because the program only needs the price.
          { pubkey: ORACLE_ACCOUNT, isSigner: false, isWritable: false },
          // WHY: Liquidator repay account loses tokens to repay the debt.
          {
            pubkey: LIQUIDATOR_REPAY_TOKEN_ACCOUNT,
            isSigner: false,
            isWritable: true,
          },
          // WHY: Protocol borrow account receives the repaid tokens.
          {
            pubkey: PROTOCOL_BORROW_TOKEN_ACCOUNT,
            isSigner: false,
            isWritable: true,
          },
          // WHY: Protocol collateral account loses tokens that are seized.
          {
            pubkey: PROTOCOL_COLLATERAL_TOKEN_ACCOUNT,
            isSigner: false,
            isWritable: true,
          },
          // WHY: Liquidator collateral account receives the seized collateral plus bonus.
          {
            pubkey: LIQUIDATOR_COLLATERAL_TOKEN_ACCOUNT,
            isSigner: false,
            isWritable: true,
          },
          // WHY: Protocol authority signs the collateral transfer via CPI.
          { pubkey: PROTOCOL_AUTHORITY, isSigner: false, isWritable: false },
          // WHY: SPL Token program is required for both token transfers.
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
          // WHY: Clock sysvar is required for interest accrual inside the program.
          { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false },
        ],
        programId: LENDING_PROGRAM_ID,
        // WHY: Variant 5 corresponds to the Liquidate instruction in the Rust enum.
        data: buildInstruction(5, repayAmount),
      });
      // WHY: Wrap the instruction in a Transaction so it can be signed and sent.
      const tx = new Transaction().add(ix);
      try {
        // WHY: Send and confirm the liquidation transaction.
        const sig = await sendAndConfirmTransaction(
          connection,
          tx,
          [liquidator],
          { commitment: "confirmed" }
        );
        // WHY: Log success so operators can monitor bot activity.
        console.log(
          `Liquidated ${pubkey.toBase58()} with repay ${repayAmount}, tx: ${sig}`
        );
      } catch (e) {
        // WHY: Log errors without crashing so the bot continues scanning other positions.
        console.error(
          `Failed to liquidate ${pubkey.toBase58()}:`,
          e
        );
      }
    }
  }
}

// WHY: run loops forever so the bot continuously monitors positions.
async function run() {
  // WHY: Use an infinite loop because liquidations can happen at any time.
  while (true) {
    // WHY: Check all positions for liquidation opportunities.
    await checkAndLiquidate();
    // WHY: Wait 5 seconds between scans to avoid RPC rate limits.
    await new Promise((r) => setTimeout(r, 5000));
  }
}

// WHY: Start the bot immediately when the script is executed.
run();
