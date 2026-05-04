import {
// WHY: Begin the import block so the file can use external libraries.
  DriftClient,
// WHY: Import the core Drift SDK client to read market data, user accounts, and submit liquidations.
  Wallet,
// WHY: Import the Wallet class to wrap a Solana keypair and produce transaction signers.
  loadKeypair,
// WHY: Import the helper that parses a base58 private key string into a Solana Keypair object.
  BN,
// WHY: Import BN (BigNumber) because Solana and Drift use 64-bit integers that exceed JavaScript's safe number range.
  User,
// WHY: Import the User class to parse on-chain margin account state and compute liquidation status.
  BulkAccountLoader,
// WHY: Import BulkAccountLoader to batch-fetch multiple user accounts in a single RPC call and reduce latency.
  SpotMarkets,
// WHY: Import SpotMarkets to access devnet spot market metadata such as market index and oracle addresses.
  PerpMarkets,
// WHY: Import PerpMarkets to access devnet perpetual market metadata such as contract specs.
  calculateMarginRatio,
// WHY: Import the margin ratio helper so the bot can compare user collateral against requirements using Drift's exact math.
  MARGIN_PRECISION,
// WHY: Import MARGIN_PRECISION to normalize raw margin ratio integers into human-readable percentages.
  PositionDirection,
// WHY: Import PositionDirection because liquidation instructions require specifying the direction of the position being closed.
} from "@drift-labs/sdk";
// WHY: Pull all Drift utilities from the official SDK to guarantee compatibility with the deployed on-chain program.
import { Connection, Keypair, PublicKey, ComputeBudgetProgram } from "@solana/web3.js";
// WHY: Import Solana web3 classes to create RPC connections, public keys, and priority-fee instructions.
import dotenv from "dotenv";
// WHY: Import dotenv so the bot can read DRIFT_RPC_URL and DRIFT_PRIVATE_KEY from a local .env file.
import path from "path";
// WHY: Import path utilities to resolve the .env file location relative to this script.

dotenv.config({ path: path.resolve(__dirname, "../../.env") });
// WHY: Load environment variables from the project root .env file so secrets are not hardcoded in source.

const RPC_URL = process.env.DRIFT_RPC_URL || "https://api.devnet.solana.com";
// WHY: Use the configured RPC or fall back to the public Solana devnet endpoint so the bot always has a node to query.
const PRIVATE_KEY = process.env.DRIFT_PRIVATE_KEY;
// WHY: Read the bot wallet private key from the environment so the bot can sign and pay for liquidation transactions.
const ENV = process.env.DRIFT_ENV || "devnet";
// WHY: Determine the target environment so the SDK instantiates the correct program ID and market constants.

if (!PRIVATE_KEY) {
// WHY: Validate that a private key was provided because the bot cannot sign transactions without it.
  throw new Error("DRIFT_PRIVATE_KEY is not set in .env");
// WHY: Crash early with a clear message so the operator knows exactly what is missing.
}
// WHY: Close the guard clause after validating the private key.

const connection = new Connection(RPC_URL, "confirmed");
// WHY: Create a persistent Solana RPC connection with 'confirmed' commitment so the bot reads finalized-ish state without waiting for full finality.
const walletKeypair = loadKeypair(PRIVATE_KEY);
// WHY: Parse the base58 key string into a Keypair so it can be used for signing and as the bot identity.
const wallet = new Wallet(walletKeypair);
// WHY: Wrap the keypair in a Wallet instance because the Drift SDK expects this interface for transaction signing.

let driftClient: DriftClient;
// WHY: Declare the driftClient variable in the outer scope so the main loop and liquidation function share one authenticated connection.

async function initializeDrift(): Promise<void> {
// WHY: Define an async initialization function because SDK setup requires asynchronous RPC calls and account fetching.
  const bulkAccountLoader = new BulkAccountLoader(connection, "confirmed", 1000);
// WHY: Instantiate a bulk loader with a 1000 ms polling interval to batch-fetch user accounts efficiently without spamming the RPC.
  driftClient = new DriftClient({
// WHY: Construct the DriftClient with explicit configuration to ensure it targets devnet and uses the bot wallet.
    connection,
// WHY: Pass the shared RPC connection so the client sends all requests through the same authenticated node.
    wallet,
// WHY: Attach the wallet so the client can automatically sign transactions when the bot calls liquidation methods.
    env: ENV as "devnet" | "mainnet-beta",
// WHY: Cast the environment string to the SDK's expected union type so TypeScript allows the value.
    accountSubscription: {
// WHY: Configure how the client subscribes to on-chain account changes to keep position data fresh.
      type: "polling",
// WHY: Use polling rather than WebSocket because polling is more stable on public RPCs and easier to debug.
      accountLoader: bulkAccountLoader,
// WHY: Wire the bulk loader into the subscription so account updates are fetched in batches rather than one by one.
    },
  });
// WHY: Close the DriftClient constructor options.
  await driftClient.subscribe();
// WHY: Activate the client's internal subscriptions so it begins caching market, oracle, and user account data.
  console.log("Drift client initialized on", ENV);
// WHY: Log the successful connection so the operator sees the bot is ready and targeting the correct cluster.
}
// WHY: Close the initialization function.

async function getAllUserPositions(): Promise<User[]> {
// WHY: Define a helper that returns all monitored User objects so the main loop can evaluate every account for liquidation.
  const users: User[] = [];
// WHY: Initialize an empty array to collect User instances because the SDK does not expose a single "get all users" method.
  const programUserAccounts = await driftClient.getUserAccountsForAuthority(new PublicKey("11111111111111111111111111111111"));
// WHY: Query the program for user accounts; this line demonstrates the SDK pattern, though in production the bot scans all accounts via program-derived addresses or a custom indexer.
  for (const account of programUserAccounts) {
// WHY: Iterate over every returned account to wrap each in a User object for margin math.
    const user = new User({
// WHY: Instantiate a User wrapper around raw account data so the SDK can compute liquidation prices and margin ratios.
      driftClient,
// WHY: Pass the driftClient so the User instance can fetch current oracle prices and market state.
      userAccountPublicKey: account.publicKey,
// WHY: Provide the on-chain public key of the user's margin account so the User class knows which account to parse.
      accountSubscription: {
// WHY: Configure per-user subscription settings so the bot tracks each account independently.
        type: "polling",
// WHY: Use polling for consistency with the main client subscription model.
        accountLoader: driftClient.accountSubscriber as BulkAccountLoader,
// WHY: Reuse the client's bulk loader to batch user account updates and reduce RPC load.
      },
    });
// WHY: Close the User constructor options.
    await user.subscribe();
// WHY: Start listening to updates for this specific user account so margin ratio calculations use fresh data.
    users.push(user);
// WHY: Add the subscribed User to the array so the main loop can evaluate it.
  }
// WHY: End the loop after processing all fetched accounts.
  return users;
// WHY: Return the populated array so the caller receives every user ready for margin analysis.
}
// WHY: Close the helper function.

function isUnderwater(user: User): boolean {
// WHY: Define a predicate that evaluates whether a single user is liquidatable so the bot can filter accounts quickly.
  const marginRatio = calculateMarginRatio(user.getUserAccount());
// WHY: Compute the user's margin ratio using Drift's canonical helper to ensure the bot uses the exact same math as the on-chain program.
  const maintenanceRequirement = user.getUserAccount().marginMode;
// WHY: Read the account's margin mode to understand which maintenance threshold applies.
  const ratioNum = marginRatio.toNumber() / MARGIN_PRECISION.toNumber();
// WHY: Normalize the raw BN ratio by the protocol precision constant so the value becomes a standard decimal like 1.05 or 0.98.
  const isLiquidatable = ratioNum < 1.0;
// WHY: Compare the normalized ratio to 1.0 because Drift defines liquidation eligibility when collateral no longer covers maintenance requirements.
  return isLiquidatable;
// WHY: Return the boolean result so the caller knows whether to proceed with liquidation for this user.
}
// WHY: Close the predicate function.

function calculateKeeperProfit(user: User, marketIndex: number): number {
// WHY: Define a profit estimator so the bot only spends gas on liquidations that exceed transaction costs.
  const position = user.getPerpPosition(marketIndex);
// WHY: Fetch the specific perp position for the given market so the profit math targets the exact notional at risk.
  if (!position) return 0;
// WHY: Return zero profit if the user has no position in this market to prevent the bot from attempting invalid liquidations.
  const notional = Math.abs(position.baseAssetAmount.toNumber());
// WHY: Convert the position size to a JavaScript number and take the absolute value because profit depends on notional magnitude, not direction.
  const oraclePrice = driftClient.getOracleDataForPerpMarket(marketIndex).price.toNumber();
// WHY: Read the current oracle price for the market so the notional value reflects real-time market conditions.
  const notionalUsd = (notional * oraclePrice) / 1e9;
// WHY: Scale the raw notional by the oracle price and adjust for Drift's base-asset precision so the result is in USD terms.
  const liquidationFeeRate = 0.025;
// WHY: Hardcode the 2.5% liquidation fee because this is the Drift devnet parameter; production bots read it from on-chain market configs.
  const estimatedReward = notionalUsd * liquidationFeeRate;
// WHY: Multiply notional by the fee rate to estimate the gross reward the keeper receives if the liquidation succeeds.
  const txCostUsd = 0.001;
// WHY: Estimate Solana transaction cost in USD to ensure the bot only acts when reward exceeds gas; this is conservative for devnet.
  const netProfit = estimatedReward - txCostUsd;
// WHY: Subtract transaction cost from gross reward to yield the keeper's actual expected profit.
  return netProfit;
// WHY: Return the net profit so the main loop can filter by profitability threshold.
}
// WHY: Close the profit calculator.

async function submitLiquidation(
// WHY: Define the liquidation submission function because this is the core action the keeper performs.
  userAccountPublicKey: PublicKey,
// WHY: Accept the target user's margin account public key so the transaction knows which account to liquidate.
  marketIndex: number,
// WHY: Accept the market index so the instruction targets the specific perp market where the user is underwater.
  maxBaseAssetAmount: BN
// WHY: Accept a BN cap on how much of the position to liquidate so the bot can partial-liquidate if desired.
): Promise<string> {
// WHY: Return a Promise of the transaction signature so the caller can track the liquidation on a block explorer.
  const priorityFeeIx = ComputeBudgetProgram.setComputeUnitPrice({
// WHY: Build a priority fee instruction so the bot's transaction outbids competing keepers during congestion.
    microLamports: 10000,
// WHY: Set 10,000 micro-lamports as a moderate priority fee; production bots dynamically adjust this based on mempool competition.
  });
// WHY: Close the priority fee instruction builder.
  const txSig = await driftClient.liquidatePerp(
// WHY: Call the SDK's liquidatePerp method to construct and send the liquidation transaction through the Drift program.
    userAccountPublicKey,
// WHY: Pass the target account so the program instruction validates that this user is actually underwater.
    marketIndex,
// WHY: Pass the market index so the program knows which perp market to liquidate within the user's account.
    maxBaseAssetAmount,
// WHY: Pass the maximum base asset amount so the program respects the bot's desired liquidation size.
    undefined,
// WHY: Pass undefined for the optional limit price because the bot accepts the current oracle price for speed.
    [priorityFeeIx]
// WHY: Append the priority fee instruction to the transaction so validators prioritize inclusion.
  );
// WHY: Close the liquidatePerp call.
  return txSig;
// WHY: Return the transaction signature so the caller can log it or verify it on an explorer.
}
// WHY: Close the liquidation submission function.

async function runKeeperLoop(): Promise<void> {
// WHY: Define the main daemon loop because the bot must continuously monitor and act without human intervention.
  await initializeDrift();
// WHY: Ensure the DriftClient is fully subscribed before scanning accounts so margin calculations use live market data.
  const users = await getAllUserPositions();
// WHY: Fetch the initial user list so the loop has accounts to evaluate; production bots refresh this list periodically.
  console.log(`Monitoring ${users.length} user accounts for liquidation...`);
// WHY: Log the count so the operator knows the bot has loaded accounts and is entering the monitoring phase.

  while (true) {
// WHY: Use an infinite loop because keeper bots run 24/7 until manually stopped.
    for (const user of users) {
// WHY: Iterate over every subscribed user account so no underwater position is missed.
      if (isUnderwater(user)) {
// WHY: Check liquidation eligibility first to avoid wasting gas on healthy accounts.
        const userAccount = user.getUserAccount();
// WHY: Read the raw user account data to extract the public key and open positions.
        const userPubKey = user.userAccountPublicKey;
// WHY: Capture the public key because the liquidation transaction requires it as an argument.
        const perpPositions = userAccount.perpPositions;
// WHY: Access the perp positions array to find which specific market is underwater.
        for (let i = 0; i < perpPositions.length; i++) {
// WHY: Loop through each perp position index because a user can hold multiple markets and any one can trigger liquidation.
          const pos = perpPositions[i];
// WHY: Retrieve the position at this index to inspect its market and size.
          if (!pos.baseAssetAmount.isZero()) {
// WHY: Skip empty positions because liquidating a zero-size position wastes gas and fails on-chain.
            const profit = calculateKeeperProfit(user, pos.marketIndex);
// WHY: Estimate profit for this specific position so the bot only acts on economically viable liquidations.
            if (profit > 0.5) {
// WHY: Require at least $0.50 expected profit to filter out tiny liquidations where gas dominates reward.
              console.log(`Liquidating user ${userPubKey.toBase58()} on market ${pos.marketIndex}, expected profit $${profit.toFixed(2)}`);
// WHY: Log the decision so the operator can audit which accounts were targeted and why.
              try {
// WHY: Open a try block because liquidation transactions can fail due to racing keepers or stale oracle data.
                const txSig = await submitLiquidation(
// WHY: Attempt to submit the liquidation transaction now that the account is underwater and profit is positive.
                  userPubKey,
// WHY: Pass the target user's public key so the Drift program identifies the correct margin account.
                  pos.marketIndex,
// WHY: Pass the specific market index so the instruction liquidates the correct perp position.
                  pos.baseAssetAmount.abs()
// WHY: Pass the absolute position size as the max liquidation amount so the bot attempts to close the entire position.
                );
// WHY: Close the submitLiquidation call.
                console.log(`Liquidation succeeded: ${txSig}`);
// WHY: Log the success and signature so the operator can verify the transaction on the Solana explorer.
              } catch (err) {
// WHY: Catch errors so the bot does not crash when another keeper wins the race or the RPC rejects the transaction.
                console.error(`Liquidation failed for ${userPubKey.toBase58()}:`, err);
// WHY: Log the failure and error details so the operator can diagnose whether the issue is gas, race conditions, or bad math.
              }
// WHY: Close the catch block.
            }
// WHY: End the profit threshold check.
          }
// WHY: End the non-zero position check.
        }
// WHY: End the perp position loop.
      }
// WHY: End the underwater check.
    }
// WHY: End the user iteration loop.
    await new Promise((resolve) => setTimeout(resolve, 400));
// WHY: Pause for 400 ms before the next scan to approximate one Solana slot and avoid RPC rate limits.
  }
// WHY: End the infinite while loop; the bot runs until the process is killed.
}
// WHY: Close the keeper loop function.

runKeeperLoop().catch((err) => {
// WHY: Attach a top-level error handler so unexpected initialization failures are logged instead of silently crashing.
  console.error("Keeper bot crashed:", err);
// WHY: Print the fatal error so the operator knows why the process exited.
  process.exit(1);
// WHY: Exit with a non-zero code so process managers like systemd or Docker know the bot failed and should restart.
});
// WHY: Close the error handler and immediately invoke the keeper loop.
