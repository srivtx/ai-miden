import express, { Request, Response } from "express"; // WHY: Express is the standard Node.js web framework for building REST APIs.
import { Connection, Keypair, PublicKey, Transaction } from "@solana/web3.js"; // WHY: Solana web3.js provides the primitives to build, sign, and send transactions to the Solana network.
import { Program, AnchorProvider, web3, BN } from "@coral-xyz/anchor"; // WHY: Anchor client simplifies interaction with Anchor programs by handling account resolution, IDL parsing, and transaction building.
import { Token, TOKEN_PROGRAM_ID } from "@solana/spl-token"; // WHY: SPL Token library provides helpers to create token accounts and mints from the API layer.
import * as fs from "fs"; // WHY: We need the filesystem module to read the Anchor IDL and wallet keypair files.
import * as path from "path"; // WHY: Path utilities ensure cross-platform file resolution when loading IDLs and keypairs.

// WHY: Initialize the Express application so we can register routes and middleware.
const app = express();
// WHY: Parse JSON request bodies so POST routes can read parameters like market IDs and amounts.
app.use(express.json());

// WHY: Configure the Solana connection; use "http://127.0.0.1:8899" for localnet or "https://api.devnet.solana.com" for Devnet.
const connection = new Connection("http://127.0.0.1:8899", "confirmed");

// WHY: Load the deployer wallet keypair from a local file so the API has a payer for transactions.
const walletKeypair = Keypair.fromSecretKey(
  Uint8Array.from(JSON.parse(fs.readFileSync(path.join(__dirname, "wallet.json"), "utf-8"))) // WHY: Read and parse the JSON array of secret key bytes.
);

// WHY: Create an Anchor wallet wrapper so the Provider can sign transactions.
const wallet = new web3.Keypair(); // WHY: Dummy placeholder; in production use AnchorWallet or WalletAdapter. We override signing below.
// WHY: Build an Anchor provider that links the connection, wallet, and confirmation commitment.
const provider = new AnchorProvider(connection, wallet as any, { commitment: "confirmed" });

// WHY: Set the provider as the global default so Program instances can use it without explicit injection.
anchor.setProvider(provider);

// WHY: Load the market program IDL so the client knows the account layouts and instruction discriminators.
const marketIdl = JSON.parse(fs.readFileSync(path.join(__dirname, "../market/target/idl/prediction_market.json"), "utf-8"));
// WHY: Load the oracle program IDL for the same reason as the market IDL.
const oracleIdl = JSON.parse(fs.readFileSync(path.join(__dirname, "../oracle/target/idl/oracle_resolution.json"), "utf-8"));

// WHY: Define the market program public key; this must match the deployed program ID.
const MARKET_PROGRAM_ID = new PublicKey("MarketProgram11111111111111111111111111111111");
// WHY: Define the oracle program public key; this must match the deployed program ID.
const ORACLE_PROGRAM_ID = new PublicKey("OracleProgram1111111111111111111111111111111");

// WHY: Instantiate an Anchor Program client for the market program so we can call instructions.
const marketProgram = new Program(marketIdl, MARKET_PROGRAM_ID, provider);
// WHY: Instantiate an Anchor Program client for the oracle program so we can call resolution instructions.
const oracleProgram = new Program(oracleIdl, ORACLE_PROGRAM_ID, provider);

// WHY: In-memory cache of market metadata so GET /markets can respond quickly without querying every account on-chain.
const marketCache: Map<string, any> = new Map();

// WHY: POST /market/create creates a new prediction market with YES/NO outcomes, collateral vault, and AMM pool.
app.post("/market/create", async (req: Request, res: Response) => {
  try {
    const { question, expiration } = req.body; // WHY: Destructure the request body to extract market parameters.
    // WHY: Validate that the question is a non-empty string to prevent creating meaningless markets.
    if (!question || typeof question !== "string") {
      return res.status(400).json({ error: "Question is required and must be a string" }); // WHY: Return 400 so the client knows the request was malformed.
    }
    // WHY: Validate that expiration is a future timestamp so the market is not instantly resolvable.
    if (!expiration || typeof expiration !== "number") {
      return res.status(400).json({ error: "Expiration is required and must be a number" });
    }

    // WHY: Derive the market PDA so the client and server agree on the market address before sending the transaction.
    const [marketPda, marketBump] = PublicKey.findProgramAddressSync(
      [Buffer.from("market"), walletKeypair.publicKey.toBuffer()], // WHY: Seeds must match the on-chain seeds ["market", creator_pubkey].
      MARKET_PROGRAM_ID
    );

    // WHY: Derive the YES mint PDA deterministically from the market address.
    const [yesMint] = PublicKey.findProgramAddressSync(
      [Buffer.from("yes_mint"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );
    // WHY: Derive the NO mint PDA deterministically from the market address.
    const [noMint] = PublicKey.findProgramAddressSync(
      [Buffer.from("no_mint"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );
    // WHY: Derive the LP mint PDA deterministically from the market address.
    const [lpMint] = PublicKey.findProgramAddressSync(
      [Buffer.from("lp_mint"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );
    // WHY: Derive the collateral vault PDA deterministically from the market address.
    const [collateralVault] = PublicKey.findProgramAddressSync(
      [Buffer.from("collateral_vault"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );
    // WHY: Derive the YES escrow PDA deterministically from the market address.
    const [yesEscrow] = PublicKey.findProgramAddressSync(
      [Buffer.from("yes_escrow"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );
    // WHY: Derive the NO escrow PDA deterministically from the market address.
    const [noEscrow] = PublicKey.findProgramAddressSync(
      [Buffer.from("no_escrow"), marketPda.toBuffer()],
      MARKET_PROGRAM_ID
    );

    // WHY: Build and send the create_market transaction using the Anchor client.
    const tx = await marketProgram.methods
      .create_market(question, new BN(expiration)) // WHY: BN handles large integers safely for on-chain u64/i64 fields.
      .accounts({
        creator: walletKeypair.publicKey,
        market: marketPda,
        yesMint,
        noMint,
        lpMint,
        collateralVault,
        yesEscrow,
        noEscrow,
        collateralMint: new PublicKey("So11111111111111111111111111111111111111112"), // WHY: Example collateral mint (wrapped SOL); replace with USDC in production.
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: web3.SystemProgram.programId,
        rent: web3.SYSVAR_RENT_PUBKEY,
      })
      .signers([walletKeypair]) // WHY: The creator must sign to pay for account creation.
      .rpc(); // WHY: .rpc() sends the transaction, waits for confirmation, and returns the signature.

    // WHY: Cache the market metadata so GET /markets can return it without an on-chain lookup.
    marketCache.set(marketPda.toBase58(), {
      address: marketPda.toBase58(),
      question,
      expiration,
      creator: walletKeypair.publicKey.toBase58(),
      yesMint: yesMint.toBase58(),
      noMint: noMint.toBase58(),
      tx,
    });

    // WHY: Return 201 Created with the market address so the client can reference it in future requests.
    return res.status(201).json({ market: marketPda.toBase58(), tx });
  } catch (err: any) {
    // WHY: Log the full error server-side for debugging, but send a sanitized message to the client.
    console.error("create market error:", err);
    return res.status(500).json({ error: err.message || "Failed to create market" });
  }
});

// WHY: POST /market/buy allows a trader to buy YES or NO shares from the AMM.
app.post("/market/buy", async (req: Request, res: Response) => {
  try {
    const { marketId, outcomeIndex, collateralAmount, traderPublicKey } = req.body; // WHY: Extract parameters from the request.
    // WHY: Validate required fields so the transaction does not fail on-chain due to missing data.
    if (!marketId || outcomeIndex === undefined || !collateralAmount) {
      return res.status(400).json({ error: "marketId, outcomeIndex, and collateralAmount are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert the string market ID to a PublicKey for Anchor.
    // WHY: Derive the trader's collateral token account address; in production this should be fetched from the token registry or created if missing.
    const traderCollateralAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    // WHY: Derive the trader's outcome token account address; simplified here.
    const traderOutcomeAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account for the specific mint.

    const tx = await marketProgram.methods
      .buy_shares(outcomeIndex, new BN(collateralAmount)) // WHY: BN handles u64 amounts safely.
      .accounts({
        trader: walletKeypair.publicKey,
        market: marketPubkey,
        traderCollateralAccount,
        collateralVault: PublicKey.findProgramAddressSync([Buffer.from("collateral_vault"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        traderOutcomeAccount,
        yesEscrow: PublicKey.findProgramAddressSync([Buffer.from("yes_escrow"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        noEscrow: PublicKey.findProgramAddressSync([Buffer.from("no_escrow"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        yesMint: PublicKey.findProgramAddressSync([Buffer.from("yes_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        noMint: PublicKey.findProgramAddressSync([Buffer.from("no_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([walletKeypair])
      .rpc();

    // WHY: Return the transaction signature so the client can track the trade on a block explorer.
    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("buy shares error:", err);
    return res.status(500).json({ error: err.message || "Failed to buy shares" });
  }
});

// WHY: POST /market/sell allows a trader to sell YES or NO shares back to the AMM for collateral.
app.post("/market/sell", async (req: Request, res: Response) => {
  try {
    const { marketId, outcomeIndex, sharesAmount, traderPublicKey } = req.body; // WHY: Extract parameters.
    if (!marketId || outcomeIndex === undefined || !sharesAmount) {
      return res.status(400).json({ error: "marketId, outcomeIndex, and sharesAmount are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert string to PublicKey.
    const traderOutcomeAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const traderCollateralAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account.

    const tx = await marketProgram.methods
      .sell_shares(outcomeIndex, new BN(sharesAmount)) // WHY: BN handles u64 amounts safely.
      .accounts({
        trader: walletKeypair.publicKey,
        market: marketPubkey,
        traderOutcomeAccount,
        yesMint: PublicKey.findProgramAddressSync([Buffer.from("yes_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        noMint: PublicKey.findProgramAddressSync([Buffer.from("no_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        traderCollateralAccount,
        collateralVault: PublicKey.findProgramAddressSync([Buffer.from("collateral_vault"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([walletKeypair])
      .rpc();

    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("sell shares error:", err);
    return res.status(500).json({ error: err.message || "Failed to sell shares" });
  }
});

// WHY: POST /market/resolve submits an oracle resolution to settle the market.
app.post("/market/resolve", async (req: Request, res: Response) => {
  try {
    const { marketId, outcomeIndex, oracleAuthorityPublicKey } = req.body; // WHY: Extract parameters.
    if (!marketId || outcomeIndex === undefined) {
      return res.status(400).json({ error: "marketId and outcomeIndex are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert string to PublicKey.
    const oracleAuthority = new PublicKey(oracleAuthorityPublicKey); // WHY: The trusted oracle must sign; we pass its pubkey for account validation.

    const tx = await marketProgram.methods
      .resolve_market(outcomeIndex) // WHY: Pass the winning outcome index to the market program.
      .accounts({
        market: marketPubkey,
        oracleProgram: ORACLE_PROGRAM_ID,
        oracle: PublicKey.findProgramAddressSync([Buffer.from("oracle_state")], ORACLE_PROGRAM_ID)[0],
        oracleAuthority,
        systemProgram: web3.SystemProgram.programId,
      })
      .signers([walletKeypair]) // WHY: In production the oracle authority would sign; here we use the deployer for demonstration.
      .rpc();

    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("resolve market error:", err);
    return res.status(500).json({ error: err.message || "Failed to resolve market" });
  }
});

// WHY: POST /market/claim allows a winning shareholder to redeem their shares for collateral.
app.post("/market/claim", async (req: Request, res: Response) => {
  try {
    const { marketId, outcomeMint, traderPublicKey } = req.body; // WHY: Extract parameters.
    if (!marketId || !outcomeMint) {
      return res.status(400).json({ error: "marketId and outcomeMint are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert string to PublicKey.
    const outcomeMintPubkey = new PublicKey(outcomeMint); // WHY: The mint of the shares being claimed (YES or NO).
    const traderOutcomeAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const traderCollateralAccount = new PublicKey(traderPublicKey); // WHY: Simplified; real implementation would derive the associated token account.

    const tx = await marketProgram.methods
      .claim_winnings() // WHY: No arguments needed because the instruction reads shares from the trader's token account.
      .accounts({
        trader: walletKeypair.publicKey,
        market: marketPubkey,
        traderOutcomeAccount,
        outcomeMint: outcomeMintPubkey,
        collateralVault: PublicKey.findProgramAddressSync([Buffer.from("collateral_vault"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        traderCollateralAccount,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([walletKeypair])
      .rpc();

    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("claim winnings error:", err);
    return res.status(500).json({ error: err.message || "Failed to claim winnings" });
  }
});

// WHY: POST /liquidity/add allows a user to deposit collateral into the AMM pool and receive LP tokens.
app.post("/liquidity/add", async (req: Request, res: Response) => {
  try {
    const { marketId, collateralAmount, providerPublicKey } = req.body; // WHY: Extract parameters.
    if (!marketId || !collateralAmount) {
      return res.status(400).json({ error: "marketId and collateralAmount are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert string to PublicKey.
    const providerCollateralAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const providerLpAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account for LP tokens.

    const tx = await marketProgram.methods
      .provide_liquidity(new BN(collateralAmount)) // WHY: BN handles u64 amounts safely.
      .accounts({
        provider: walletKeypair.publicKey,
        market: marketPubkey,
        providerCollateralAccount,
        collateralVault: PublicKey.findProgramAddressSync([Buffer.from("collateral_vault"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        providerLpAccount,
        lpMint: PublicKey.findProgramAddressSync([Buffer.from("lp_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([walletKeypair])
      .rpc();

    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("add liquidity error:", err);
    return res.status(500).json({ error: err.message || "Failed to add liquidity" });
  }
});

// WHY: POST /liquidity/remove allows a liquidity provider to burn LP tokens and withdraw their share of the pool.
app.post("/liquidity/remove", async (req: Request, res: Response) => {
  try {
    const { marketId, lpAmount, providerPublicKey } = req.body; // WHY: Extract parameters.
    if (!marketId || !lpAmount) {
      return res.status(400).json({ error: "marketId and lpAmount are required" });
    }

    const marketPubkey = new PublicKey(marketId); // WHY: Convert string to PublicKey.
    const providerLpAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const providerCollateralAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const providerYesAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account.
    const providerNoAccount = new PublicKey(providerPublicKey); // WHY: Simplified; real implementation would derive the associated token account.

    const tx = await marketProgram.methods
      .remove_liquidity(new BN(lpAmount)) // WHY: BN handles u64 amounts safely.
      .accounts({
        provider: walletKeypair.publicKey,
        market: marketPubkey,
        providerLpAccount,
        lpMint: PublicKey.findProgramAddressSync([Buffer.from("lp_mint"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        providerCollateralAccount,
        collateralVault: PublicKey.findProgramAddressSync([Buffer.from("collateral_vault"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        providerYesAccount,
        yesEscrow: PublicKey.findProgramAddressSync([Buffer.from("yes_escrow"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        providerNoAccount,
        noEscrow: PublicKey.findProgramAddressSync([Buffer.from("no_escrow"), marketPubkey.toBuffer()], MARKET_PROGRAM_ID)[0],
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .signers([walletKeypair])
      .rpc();

    return res.status(200).json({ tx });
  } catch (err: any) {
    console.error("remove liquidity error:", err);
    return res.status(500).json({ error: err.message || "Failed to remove liquidity" });
  }
});

// WHY: GET /markets returns a list of all cached markets so clients can browse available prediction events.
app.get("/markets", (_req: Request, res: Response) => {
  // WHY: Convert the Map values to an array for JSON serialization.
  const markets = Array.from(marketCache.values());
  return res.status(200).json({ markets });
});

// WHY: GET /market/:id returns the details of a specific market by its on-chain address.
app.get("/market/:id", async (req: Request, res: Response) => {
  try {
    const { id } = req.params; // WHY: Extract the market address from the URL path.
    const marketPubkey = new PublicKey(id); // WHY: Convert string to PublicKey.

    // WHY: Fetch the market account directly from the blockchain so the client sees the latest on-chain state.
    const marketAccount = await marketProgram.account.market.fetch(marketPubkey); // WHY: Anchor's fetch method deserializes the account data using the IDL.

    // WHY: Return the full market account data, including reserves, resolution state, and mints.
    return res.status(200).json({ market: marketAccount });
  } catch (err: any) {
    console.error("fetch market error:", err);
    return res.status(500).json({ error: err.message || "Failed to fetch market" });
  }
});

// WHY: Start the Express server on port 3061 so it does not conflict with common ports like 3000 or 8080.
const PORT = 3061;
app.listen(PORT, () => {
  console.log(`Market API listening on port ${PORT}`); // WHY: Log startup so the operator knows the service is running.
});
