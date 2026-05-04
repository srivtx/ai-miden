import express, { Request, Response } from "express";
// WHY: Import Express and its type definitions to build a typed REST API that exposes Drift protocol data.
import {
// WHY: Begin importing Drift SDK classes so the API can query on-chain state using official program bindings.
  DriftClient,
// WHY: Import DriftClient to connect to the Drift program and fetch user accounts, markets, and oracle prices.
  Wallet,
// WHY: Import Wallet to wrap a keypair and satisfy the SDK's signer interface even though read-only calls do not always need signing.
  loadKeypair,
// WHY: Import the keypair loader so the API can initialize a wallet from an environment variable for authenticated driftClient creation.
  User,
// WHY: Import User to parse individual margin accounts and compute per-user position details.
  SpotMarkets,
// WHY: Import SpotMarkets to return devnet spot market metadata such as market indices and oracle addresses.
  PerpMarkets,
// WHY: Import PerpMarkets to return devnet perpetual market metadata such as contract specs and funding rates.
  calculateMarginRatio,
// WHY: Import the margin ratio calculator so the API can report liquidation risk using Drift's exact on-chain math.
  MARGIN_PRECISION,
// WHY: Import MARGIN_PRECISION to convert raw margin ratio integers into human-readable percentages in API responses.
} from "@drift-labs/sdk";
// WHY: Pull utilities from the official Drift SDK to guarantee that API responses match the live on-chain program behavior.
import { Connection, PublicKey } from "@solana/web3.js";
// WHY: Import Solana web3 classes to create an RPC connection and parse public key strings from URL parameters.
import dotenv from "dotenv";
// WHY: Import dotenv so the API can read DRIFT_RPC_URL and wallet configuration from a .env file instead of hardcoding values.
import path from "path";
// WHY: Import path utilities to resolve the .env file location relative to this script's directory.

dotenv.config({ path: path.resolve(__dirname, "../../.env") });
// WHY: Load environment variables from the project root .env file so secrets and RPC URLs are configurable per deployment.

const RPC_URL = process.env.DRIFT_RPC_URL || "https://api.devnet.solana.com";
// WHY: Use the configured RPC URL or default to public devnet so the API can start even if the operator has not customized .env.
const PRIVATE_KEY = process.env.DRIFT_PRIVATE_KEY;
// WHY: Read the wallet private key from the environment because the DriftClient constructor requires a wallet even for read-heavy operations.
const ENV = process.env.DRIFT_ENV || "devnet";
// WHY: Determine the target cluster so the SDK loads the correct program IDs, market constants, and oracle mappings.

const connection = new Connection(RPC_URL, "confirmed");
// WHY: Create a persistent Solana RPC connection with 'confirmed' commitment so API endpoints return stable, finalized-ish data.
let driftClient: DriftClient;
// WHY: Declare driftClient in the outer scope so all route handlers share one cached, authenticated connection instead of reconnecting per request.

async function initializeDrift(): Promise<void> {
// WHY: Define an async initializer because SDK setup requires asynchronous RPC calls and program account fetching.
  const walletKeypair = PRIVATE_KEY ? loadKeypair(PRIVATE_KEY) : new PublicKey("11111111111111111111111111111111");
// WHY: Load the wallet if a key is provided, otherwise use a dummy public key because some DriftClient methods tolerate a read-only wallet.
  const wallet = new Wallet(walletKeypair as any);
// WHY: Wrap the keypair in a Wallet instance because the DriftClient constructor strictly expects a Wallet-compatible object.
  driftClient = new DriftClient({
// WHY: Construct the DriftClient with explicit configuration so it targets devnet and reuses the shared RPC connection.
    connection,
// WHY: Pass the shared RPC connection so all API routes query the same node and benefit from connection pooling.
    wallet,
// WHY: Attach the wallet so the client can sign transactions if any route later needs to submit instructions.
    env: ENV as "devnet" | "mainnet-beta",
// WHY: Cast the environment string to the SDK's expected union type so TypeScript compiles without type errors.
    accountSubscription: {
// WHY: Configure how the client subscribes to on-chain accounts so market and user data stays fresh between requests.
      type: "polling",
// WHY: Use polling because it is more compatible with stateless API processes and avoids long-lived WebSocket issues.
      frequency: 1000,
// WHY: Poll every 1000 ms to balance freshness against RPC rate limits in a shared API process.
    },
  });
// WHY: Close the DriftClient constructor options.
  await driftClient.subscribe();
// WHY: Activate the client's internal subscriptions so it begins caching oracle prices, market configs, and user accounts.
  console.log("Drift API initialized on", ENV);
// WHY: Log the initialization so the operator knows the backend is ready to handle HTTP requests.
}
// WHY: Close the initialization function.

const app = express();
// WHY: Create the Express application instance so routes and middleware can be registered.
app.use(express.json());
// WHY: Enable JSON body parsing so POST endpoints like /liquidate can read request payloads containing target user addresses.

app.get("/positions", async (_req: Request, res: Response) => {
// WHY: Define GET /positions so external clients can retrieve a snapshot of all tracked user margin accounts and their positions.
  try {
// WHY: Open a try block so unexpected RPC errors return a 500 rather than crashing the API process.
    const userAccounts = await driftClient.getUserAccountsForAuthority(new PublicKey("11111111111111111111111111111111"));
// WHY: Query the Drift program for user accounts; in production this queries an indexer, but this demonstrates the SDK pattern.
    const positions = userAccounts.map((ua) => {
// WHY: Map over each raw user account to transform on-chain data into a clean JSON shape for API consumers.
      const marginRatio = calculateMarginRatio(ua.account);
// WHY: Compute the margin ratio using Drift's canonical helper so the API risk metrics match the on-chain program exactly.
      return {
// WHY: Return a plain object for each user so the JSON response is predictable and easy for frontends to parse.
        userPublicKey: ua.publicKey.toBase58(),
// WHY: Include the base58 public key so callers can uniquely identify and link to each margin account.
        authority: ua.account.authority.toBase58(),
// WHY: Include the wallet authority so callers know which wallet controls this sub-account.
        subAccountId: ua.account.subAccountId,
// WHY: Include the sub-account ID because Drift users can have up to 20 isolated sub-accounts.
        marginRatio: marginRatio.toNumber() / MARGIN_PRECISION.toNumber(),
// WHY: Normalize the raw BN margin ratio by the protocol precision so the response shows a standard decimal like 1.15.
        perpPositions: ua.account.perpPositions.map((p) => ({
// WHY: Map each perpetual position to a simplified object so the response does not leak unnecessary raw BN internals.
          marketIndex: p.marketIndex,
// WHY: Include the market index so callers know which perp market this position belongs to.
          baseAssetAmount: p.baseAssetAmount.toString(),
// WHY: Convert the position size to a string because JSON cannot safely represent 64-bit integers as native numbers.
          quoteAssetAmount: p.quoteAssetAmount.toString(),
// WHY: Convert the quote entry value to a string for the same BN safety reason.
          lastCumulativeFundingRate: p.lastCumulativeFundingRate.toString(),
// WHY: Include the last funding rate so callers can compute unrealized funding payments if desired.
        })),
// WHY: Close the perp position mapper.
        spotPositions: ua.account.spotPositions.map((s) => ({
// WHY: Map each spot position to a simplified object so the response includes collateral deposits and borrows.
          marketIndex: s.marketIndex,
// WHY: Include the spot market index so callers know which token this balance represents.
          balance: s.balance.toString(),
// WHY: Convert the token balance to a string to preserve precision for large or fractional amounts.
          openAsks: s.openAsks.toString(),
// WHY: Include open asks so the response reflects pending spot sell orders that affect available collateral.
          openBids: s.openBids.toString(),
// WHY: Include open bids so the response reflects pending spot buy orders that affect available collateral.
        })),
// WHY: Close the spot position mapper.
      };
// WHY: Close the returned user object.
    });
// WHY: Close the userAccounts map.
    res.json({ count: positions.length, positions });
// WHY: Respond with a JSON envelope containing the count and array so pagination clients know the result set size.
  } catch (err) {
// WHY: Catch errors so the API returns a controlled error response instead of crashing.
    console.error("GET /positions error:", err);
// WHY: Log the server-side error details so operators can diagnose RPC or SDK issues.
    res.status(500).json({ error: "Failed to fetch positions" });
// WHY: Return a 500 status and a generic message so API consumers know the backend encountered an issue.
  }
// WHY: Close the catch block.
});
// WHY: Close the GET /positions route handler.

app.get("/position/:user", async (req: Request, res: Response) => {
// WHY: Define GET /position/:user so callers can query a single margin account by its public key instead of downloading all accounts.
  try {
// WHY: Open a try block to handle invalid public keys or missing accounts gracefully.
    const userPubKey = new PublicKey(req.params.user);
// WHY: Parse the URL parameter into a PublicKey so the SDK can fetch the specific on-chain account.
    const userAccount = await driftClient.getUserAccount(userPubKey);
// WHY: Fetch the single user account directly from the RPC to minimize data transfer and latency.
    if (!userAccount) {
// WHY: Check for a null result because the requested public key may not correspond to an existing Drift user.
      res.status(404).json({ error: "User not found" });
// WHY: Return 404 so REST clients can distinguish between a missing resource and a server error.
      return;
// WHY: Exit the handler early so the code below does not attempt to read properties of a null object.
    }
// WHY: Close the null check.
    const marginRatio = calculateMarginRatio(userAccount);
// WHY: Compute the margin ratio for this single user so the response includes a real-time risk metric.
    res.json({
// WHY: Begin the JSON response payload for the single user query.
      userPublicKey: userPubKey.toBase58(),
// WHY: Echo the requested public key back so the response is self-describing and easy to correlate.
      authority: userAccount.authority.toBase58(),
// WHY: Include the authority so callers know which wallet owns this margin account.
      subAccountId: userAccount.subAccountId,
// WHY: Include the sub-account ID because a single wallet can control multiple isolated sub-accounts.
      marginRatio: marginRatio.toNumber() / MARGIN_PRECISION.toNumber(),
// WHY: Normalize the raw margin ratio to a decimal so the response is human-readable.
      perpPositions: userAccount.perpPositions.map((p) => ({
// WHY: Map perpetual positions to a simplified shape so the JSON response is clean and frontend-friendly.
        marketIndex: p.marketIndex,
// WHY: Include the market index to identify which perp market each position belongs to.
        baseAssetAmount: p.baseAssetAmount.toString(),
// WHY: Serialize the position size as a string to prevent JavaScript number precision loss.
        quoteAssetAmount: p.quoteAssetAmount.toString(),
// WHY: Serialize the quote value as a string for the same precision safety.
        lastCumulativeFundingRate: p.lastCumulativeFundingRate.toString(),
// WHY: Include the funding rate so callers can compute funding payments if needed.
      })),
// WHY: Close the perp position mapper.
      spotPositions: userAccount.spotPositions.map((s) => ({
// WHY: Map spot positions to a simplified shape so the response includes collateral and borrow details.
        marketIndex: s.marketIndex,
// WHY: Include the spot market index so callers know which token this balance represents.
        balance: s.balance.toString(),
// WHY: Serialize the balance as a string to preserve precision across the JSON boundary.
        openAsks: s.openAsks.toString(),
// WHY: Include open asks so the response reflects pending orders that lock collateral.
        openBids: s.openBids.toString(),
// WHY: Include open bids so the response reflects pending orders that lock collateral.
      })),
// WHY: Close the spot position mapper.
    });
// WHY: Close the JSON response object.
  } catch (err) {
// WHY: Catch parsing errors (invalid pubkey) or RPC failures so the API does not crash.
    console.error("GET /position/:user error:", err);
// WHY: Log the error server-side so operators can trace issues with specific user lookups.
    res.status(500).json({ error: "Failed to fetch user position" });
// WHY: Return 500 so the client knows the lookup failed due to a backend problem.
  }
// WHY: Close the catch block.
});
// WHY: Close the GET /position/:user route handler.

app.post("/liquidate", async (req: Request, res: Response) => {
// WHY: Define POST /liquidate so authorized callers or the keeper bot can trigger a liquidation transaction via HTTP.
  try {
// WHY: Open a try block because transaction submission can fail due to racing keepers, stale oracle data, or invalid accounts.
    const { userPubKey, marketIndex, maxBaseAssetAmount } = req.body;
// WHY: Destructure the request body to extract the target user, market, and liquidation size.
    if (!userPubKey || marketIndex === undefined || !maxBaseAssetAmount) {
// WHY: Validate that all required fields are present so the bot does not build an incomplete transaction.
      res.status(400).json({ error: "Missing required fields: userPubKey, marketIndex, maxBaseAssetAmount" });
// WHY: Return 400 to tell the client the request was malformed and which fields are required.
      return;
// WHY: Exit early so the code below does not attempt to use undefined values.
    }
// WHY: Close the validation check.
    const userPublicKey = new PublicKey(userPubKey);
// WHY: Parse the user public key string into a PublicKey object so the Drift instruction references the correct on-chain account.
    const marketIdx = Number(marketIndex);
// WHY: Coerce the market index to a Number because it may arrive as a string in JSON and the SDK expects a numeric index.
    const maxBase = new BN(maxBaseAssetAmount);
// WHY: Wrap the max base amount in a BN because Drift program instructions expect 64-bit integer encodings for token amounts.
    const txSig = await driftClient.liquidatePerp(
// WHY: Call the SDK's liquidatePerp method to build, sign, and send the liquidation transaction.
      userPublicKey,
// WHY: Pass the target user's margin account so the Drift program knows which account to evaluate and liquidate.
      marketIdx,
// WHY: Pass the perp market index so the instruction targets the specific position causing the margin deficiency.
      maxBase,
// WHY: Pass the maximum base asset amount so the instruction respects the caller's desired liquidation size cap.
      undefined,
// WHY: Pass undefined for the optional limit price to accept the current oracle price and minimize transaction build time.
      undefined
// WHY: Pass undefined for the optional referrer info because this bot does not route through a referral account.
    );
// WHY: Close the liquidatePerp call.
    res.json({ success: true, signature: txSig });
// WHY: Respond with the transaction signature so the caller can verify the liquidation on a Solana block explorer.
  } catch (err) {
// WHY: Catch submission errors so the API returns a controlled response instead of crashing the process.
    console.error("POST /liquidate error:", err);
// WHY: Log the server-side error so operators can diagnose why a liquidation transaction failed.
    res.status(500).json({ error: "Liquidation transaction failed", details: String(err) });
// WHY: Return 500 and stringify the error so the client receives actionable feedback about the failure reason.
  }
// WHY: Close the catch block.
});
// WHY: Close the POST /liquidate route handler.

app.get("/markets", async (_req: Request, res: Response) => {
// WHY: Define GET /markets so callers can retrieve current market metadata and oracle prices without parsing on-chain accounts themselves.
  try {
// WHY: Open a try block because RPC failures can occur when fetching market state.
    const perpMarketConfigs = PerpMarkets[ENV === "mainnet-beta" ? "mainnet-beta" : "devnet"];
// WHY: Select the correct market config array based on the environment so the API returns mainnet or devnet metadata accordingly.
    const spotMarketConfigs = SpotMarkets[ENV === "mainnet-beta" ? "mainnet-beta" : "devnet"];
// WHY: Select the correct spot market config array for the same environment-aware reason.
    const perpMarkets = perpMarketConfigs.map((m) => {
// WHY: Map each perp market config to an enriched object that includes live oracle data from the driftClient cache.
      const marketAccount = driftClient.getPerpMarketAccount(m.marketIndex);
// WHY: Fetch the on-chain perp market account from the client's cache so the response includes current funding rates and open interest.
      return {
// WHY: Return a plain object for each perp market so the JSON shape is predictable.
        marketIndex: m.marketIndex,
// WHY: Include the market index so callers can reference this market in other API calls.
        symbol: m.symbol,
// WHY: Include the human-readable symbol like "SOL-PERP" so frontends can display familiar names.
        baseAssetSymbol: m.baseAssetSymbol,
// WHY: Include the base asset symbol so callers know which underlying token this perpetual contract tracks.
        oracle: m.oracle.toBase58(),
// WHY: Include the oracle public key so advanced callers can verify price sources independently.
        markPrice: marketAccount ? marketAccount.amm.historicalOracleData.lastOraclePriceTwap.toString() : null,
// WHY: Include the latest mark price as a string so the response shows current market valuation without precision loss.
        fundingRate: marketAccount ? marketAccount.amm.lastFundingRate.toString() : null,
// WHY: Include the last funding rate so callers can see the cost of carry for holding positions.
        openInterest: marketAccount ? marketAccount.amm.baseAssetAmountLong.add(marketAccount.amm.baseAssetAmountShort).toString() : null,
// WHY: Compute total open interest by adding longs and shorts so the response reflects market size and liquidity.
      };
// WHY: Close the returned market object.
    });
// WHY: Close the perp market mapper.
    const spotMarkets = spotMarketConfigs.map((m) => {
// WHY: Map each spot market config to an enriched object that includes live data from the driftClient cache.
      const marketAccount = driftClient.getSpotMarketAccount(m.marketIndex);
// WHY: Fetch the on-chain spot market account so the response includes current deposit and borrow utilization.
      return {
// WHY: Return a plain object for each spot market so the JSON shape is predictable.
        marketIndex: m.marketIndex,
// WHY: Include the market index so callers can reference this spot market in deposit and withdrawal operations.
        symbol: m.symbol,
// WHY: Include the human-readable symbol like "USDC" so frontends can display familiar token names.
        mint: m.mint.toBase58(),
// WHY: Include the token mint address so callers can verify the SPL token contract and fetch metadata.
        oracle: m.oracle.toBase58(),
// WHY: Include the oracle public key so callers can cross-check price feeds.
        depositBalance: marketAccount ? marketAccount.depositBalance.toString() : null,
// WHY: Include total deposits so the response shows pool depth and available liquidity.
        borrowBalance: marketAccount ? marketAccount.borrowBalance.toString() : null,
// WHY: Include total borrows so callers can compute utilization rate and interest rate curves.
      };
// WHY: Close the returned spot market object.
    });
// WHY: Close the spot market mapper.
    res.json({ perpMarkets, spotMarkets });
// WHY: Respond with both market arrays in one JSON envelope so callers receive a complete market overview.
  } catch (err) {
// WHY: Catch errors so an RPC failure returns a controlled response rather than crashing the API.
    console.error("GET /markets error:", err);
// WHY: Log the server-side error so operators can diagnose market data fetching issues.
    res.status(500).json({ error: "Failed to fetch markets" });
// WHY: Return 500 so the client knows the market query failed on the backend.
  }
// WHY: Close the catch block.
});
// WHY: Close the GET /markets route handler.

const PORT = 3073;
// WHY: Define the listening port as 3073 because the prompt specifies this port for the Phase 65 API.
app.listen(PORT, async () => {
// WHY: Start the Express server asynchronously so the DriftClient can initialize before accepting HTTP requests.
  await initializeDrift();
// WHY: Ensure the DriftClient is fully subscribed before the first request arrives so all routes return live data.
  console.log(`Drift API listening on http://localhost:${PORT}`);
// WHY: Log the bound address so the operator knows where to send requests and can verify startup success.
});
// WHY: Close the listen callback and start the server.
