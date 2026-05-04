import express from "express"; // Express provides the HTTP server framework for handling REST requests.
import { Connection, PublicKey, Keypair, Transaction, SystemProgram, SYSVAR_CLOCK_PUBKEY, SYSVAR_RENT_PUBKEY } from "@solana/web3.js"; // Solana web3.js enables RPC communication and transaction building.
import { Token, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from "@solana/spl-token"; // SPL token helpers create token instructions and derive ATAs.
import bs58 from "bs58"; // bs58 decodes base58-encoded secret keys into Keypair objects.

// Create the Express application instance.
const app = express();
// Define the port the API listens on as specified in the requirements.
const PORT = 3057;
// Load the marketplace program ID from environment variables to avoid hardcoding secrets.
const MARKETPLACE_PROGRAM_ID = new PublicKey(process.env.MARKETPLACE_PROGRAM_ID || "Marketplace111111111111111111111111111111111");
// Load the escrow program ID from environment variables for CPI references.
const ESCROW_PROGRAM_ID = new PublicKey(process.env.ESCROW_PROGRAM_ID || "Escrow11111111111111111111111111111111111111");
// Initialize a connection to the Solana devnet RPC endpoint for testing.
const connection = new Connection(process.env.SOLANA_RPC || "https://api.devnet.solana.com", "confirmed");
// Load the server keypair from a base58-encoded secret key for signing administrative transactions.
const serverKeypair = Keypair.fromSecretKey(bs58.decode(process.env.SERVER_PRIVATE_KEY || Keypair.generate().secretKey.toString()));

// Middleware to parse JSON request bodies so routes can read posted data.
app.use(express.json());

// POST /list creates a fixed-price listing by building a transaction that invokes the marketplace program.
app.post("/list", async (req, res) => {
  try {
    // Extract sellerPublicKey, nftMint, price, and sellerTokenAccount from the request body.
    const { sellerPublicKey, nftMint, price, sellerTokenAccount } = req.body;
    // Convert the seller's public key string into a PublicKey object for on-chain use.
    const seller = new PublicKey(sellerPublicKey);
    // Convert the NFT mint address string into a PublicKey object.
    const mint = new PublicKey(nftMint);
    // Convert the seller's token account string into a PublicKey object.
    const sellerAta = new PublicKey(sellerTokenAccount);
    // Derive the listing PDA from the seller, mint, and program ID so the client does not need to compute it.
    const [listingPda] = PublicKey.findProgramAddressSync([Buffer.from("listing"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    // Derive the escrow PDA from the listing PDA and program ID.
    const [escrowPda] = PublicKey.findProgramAddressSync([Buffer.from("escrow"), listingPda.toBuffer()], MARKETPLACE_PROGRAM_ID);
    // Derive the escrow associated token account so the NFT can be transferred into custody.
    const escrowAta = await Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, escrowPda, true);
    // Build a transaction to invoke the marketplace program's List instruction.
    const transaction = new Transaction().add({
      keys: [
        { pubkey: seller, isSigner: true, isWritable: true }, // seller pays for account creation and signs.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only for validation.
        { pubkey: sellerAta, isSigner: false, isWritable: true }, // seller's ATA loses the NFT.
        { pubkey: listingPda, isSigner: false, isWritable: true }, // listing PDA is created.
        { pubkey: escrowPda, isSigner: false, isWritable: true }, // escrow PDA is referenced.
        { pubkey: escrowAta, isSigner: false, isWritable: true }, // escrow ATA receives the NFT.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program handles transfers.
        { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // ATA program creates token accounts.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program creates accounts.
        { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false }, // Rent sysvar calculates exemption.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([0, ...Buffer.from(new BigUint64Array([BigInt(price)]).buffer)]), // instruction index 0 = List, followed by price.
    });
    // Set a recent blockhash so the transaction is valid and cannot be replayed.
    transaction.feePayer = seller;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    // Return the serialized transaction to the client for the seller to sign with their wallet.
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    // Catch any errors and return a 500 response with the error message so the client knows what failed.
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /delist cancels a fixed-price listing and returns the NFT to the seller.
app.post("/delist", async (req, res) => {
  try {
    const { sellerPublicKey, nftMint, sellerTokenAccount } = req.body;
    const seller = new PublicKey(sellerPublicKey);
    const mint = new PublicKey(nftMint);
    const sellerAta = new PublicKey(sellerTokenAccount);
    const [listingPda] = PublicKey.findProgramAddressSync([Buffer.from("listing"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const [escrowPda] = PublicKey.findProgramAddressSync([Buffer.from("escrow"), listingPda.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const escrowAta = await Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, escrowPda, true);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: seller, isSigner: true, isWritable: true }, // seller signs and receives rent refund.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: listingPda, isSigner: false, isWritable: true }, // listing PDA is closed.
        { pubkey: escrowPda, isSigner: false, isWritable: true }, // escrow PDA is referenced.
        { pubkey: escrowAta, isSigner: false, isWritable: true }, // escrow ATA loses the NFT.
        { pubkey: sellerAta, isSigner: false, isWritable: true }, // seller's ATA receives the NFT.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program handles transfer.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program closes accounts.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([1]), // instruction index 1 = Delist.
    });
    transaction.feePayer = seller;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /buy purchases a fixed-price listing and triggers royalty distribution.
app.post("/buy", async (req, res) => {
  try {
    const { buyerPublicKey, sellerPublicKey, nftMint, buyerTokenAccount, metadataAccount } = req.body;
    const buyer = new PublicKey(buyerPublicKey);
    const seller = new PublicKey(sellerPublicKey);
    const mint = new PublicKey(nftMint);
    const buyerAta = new PublicKey(buyerTokenAccount);
    const [listingPda] = PublicKey.findProgramAddressSync([Buffer.from("listing"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const [escrowPda] = PublicKey.findProgramAddressSync([Buffer.from("escrow"), listingPda.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const escrowAta = await Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, escrowPda, true);
    const meta = new PublicKey(metadataAccount);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: buyer, isSigner: true, isWritable: true }, // buyer signs and pays.
        { pubkey: seller, isSigner: false, isWritable: true }, // seller receives payment.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: listingPda, isSigner: false, isWritable: true }, // listing PDA is updated.
        { pubkey: escrowPda, isSigner: false, isWritable: true }, // escrow PDA releases NFT.
        { pubkey: escrowAta, isSigner: false, isWritable: true }, // escrow ATA sends NFT.
        { pubkey: buyerAta, isSigner: false, isWritable: true }, // buyer's ATA receives NFT.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program for SOL transfers.
        { pubkey: meta, isSigner: false, isWritable: false }, // metadata account provides royalty info.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([2]), // instruction index 2 = Buy.
    });
    transaction.feePayer = buyer;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /offer allows a buyer to lock lamports as an offer on an NFT.
app.post("/offer", async (req, res) => {
  try {
    const { buyerPublicKey, nftMint, price, expiry } = req.body;
    const buyer = new PublicKey(buyerPublicKey);
    const mint = new PublicKey(nftMint);
    const [offerPda] = PublicKey.findProgramAddressSync([Buffer.from("offer"), buyer.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: buyer, isSigner: true, isWritable: true }, // buyer signs and funds the offer.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: offerPda, isSigner: false, isWritable: true }, // offer PDA is created with escrowed lamports.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program creates accounts.
        { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false }, // Rent sysvar.
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false }, // Clock sysvar validates expiry.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([3, ...Buffer.from(new BigUint64Array([BigInt(price)]).buffer), ...Buffer.from(new BigInt64Array([BigInt(expiry)]).buffer)]), // instruction 3 = PlaceOffer.
    });
    transaction.feePayer = buyer;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /cancel-offer refunds the buyer and closes the offer account.
app.post("/cancel-offer", async (req, res) => {
  try {
    const { buyerPublicKey, nftMint } = req.body;
    const buyer = new PublicKey(buyerPublicKey);
    const mint = new PublicKey(nftMint);
    const [offerPda] = PublicKey.findProgramAddressSync([Buffer.from("offer"), buyer.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: buyer, isSigner: true, isWritable: true }, // buyer signs and receives lamports.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: offerPda, isSigner: false, isWritable: true }, // offer PDA is closed.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program for lamport transfers.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([4]), // instruction index 4 = CancelOffer.
    });
    transaction.feePayer = buyer;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /accept-offer lets the NFT owner accept a buyer's offer and transfer the NFT.
app.post("/accept-offer", async (req, res) => {
  try {
    const { sellerPublicKey, buyerPublicKey, nftMint, sellerTokenAccount, buyerTokenAccount } = req.body;
    const seller = new PublicKey(sellerPublicKey);
    const buyer = new PublicKey(buyerPublicKey);
    const mint = new PublicKey(nftMint);
    const sellerAta = new PublicKey(sellerTokenAccount);
    const buyerAta = new PublicKey(buyerTokenAccount);
    const [offerPda] = PublicKey.findProgramAddressSync([Buffer.from("offer"), buyer.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: seller, isSigner: true, isWritable: true }, // seller signs and receives payment.
        { pubkey: buyer, isSigner: false, isWritable: true }, // buyer receives NFT.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: offerPda, isSigner: false, isWritable: true }, // offer PDA releases lamports.
        { pubkey: sellerAta, isSigner: false, isWritable: true }, // seller's ATA loses NFT.
        { pubkey: buyerAta, isSigner: false, isWritable: true }, // buyer's ATA receives NFT.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program.
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false }, // Clock validates expiry.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([5]), // instruction index 5 = AcceptOffer.
    });
    transaction.feePayer = seller;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /auction/create initializes a new English or Dutch auction.
app.post("/auction/create", async (req, res) => {
  try {
    const { sellerPublicKey, nftMint, reservePrice, minIncrement, endTime, startPrice, isDutch, sellerTokenAccount } = req.body;
    const seller = new PublicKey(sellerPublicKey);
    const mint = new PublicKey(nftMint);
    const sellerAta = new PublicKey(sellerTokenAccount);
    const [auctionPda] = PublicKey.findProgramAddressSync([Buffer.from("auction"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const [escrowPda] = PublicKey.findProgramAddressSync([Buffer.from("escrow"), auctionPda.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const escrowAta = await Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, escrowPda, true);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: seller, isSigner: true, isWritable: true }, // seller signs and provides NFT.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: sellerAta, isSigner: false, isWritable: true }, // seller's ATA sends NFT.
        { pubkey: auctionPda, isSigner: false, isWritable: true }, // auction PDA is created.
        { pubkey: escrowPda, isSigner: false, isWritable: true }, // escrow PDA is referenced.
        { pubkey: escrowAta, isSigner: false, isWritable: true }, // escrow ATA receives NFT.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program.
        { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // ATA program.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program.
        { pubkey: SYSVAR_RENT_PUBKEY, isSigner: false, isWritable: false }, // Rent sysvar.
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false }, // Clock validates end time.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([6, ...Buffer.from(new BigUint64Array([BigInt(reservePrice)]).buffer), ...Buffer.from(new BigUint64Array([BigInt(minIncrement)]).buffer), ...Buffer.from(new BigInt64Array([BigInt(endTime)]).buffer), ...Buffer.from(new BigUint64Array([BigInt(startPrice)]).buffer), isDutch ? 1 : 0]), // instruction 6 = CreateAuction.
    });
    transaction.feePayer = seller;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /auction/bid places a bid in an English auction.
app.post("/auction/bid", async (req, res) => {
  try {
    const { bidderPublicKey, sellerPublicKey, nftMint, amount } = req.body;
    const bidder = new PublicKey(bidderPublicKey);
    const seller = new PublicKey(sellerPublicKey);
    const mint = new PublicKey(nftMint);
    const [auctionPda] = PublicKey.findProgramAddressSync([Buffer.from("auction"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const [bidPda] = PublicKey.findProgramAddressSync([Buffer.from("bid"), auctionPda.toBuffer(), bidder.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: bidder, isSigner: true, isWritable: true }, // bidder signs and funds bid.
        { pubkey: auctionPda, isSigner: false, isWritable: true }, // auction PDA updates highest bid.
        { pubkey: bidPda, isSigner: false, isWritable: true }, // bid PDA is created.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program.
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false }, // Clock checks auction status.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([7, ...Buffer.from(new BigUint64Array([BigInt(amount)]).buffer)]), // instruction 7 = PlaceBid.
    });
    transaction.feePayer = bidder;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// POST /auction/settle finalizes an auction and distributes the NFT and payment.
app.post("/auction/settle", async (req, res) => {
  try {
    const { callerPublicKey, sellerPublicKey, winnerPublicKey, nftMint, winnerTokenAccount, bidPda } = req.body;
    const caller = new PublicKey(callerPublicKey);
    const seller = new PublicKey(sellerPublicKey);
    const winner = new PublicKey(winnerPublicKey);
    const mint = new PublicKey(nftMint);
    const winnerAta = new PublicKey(winnerTokenAccount);
    const [auctionPda] = PublicKey.findProgramAddressSync([Buffer.from("auction"), seller.toBuffer(), mint.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const [escrowPda] = PublicKey.findProgramAddressSync([Buffer.from("escrow"), auctionPda.toBuffer()], MARKETPLACE_PROGRAM_ID);
    const escrowAta = await Token.getAssociatedTokenAddress(ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID, mint, escrowPda, true);
    const bid = new PublicKey(bidPda);
    const transaction = new Transaction().add({
      keys: [
        { pubkey: caller, isSigner: true, isWritable: false }, // caller triggers settlement.
        { pubkey: seller, isSigner: false, isWritable: true }, // seller receives payment.
        { pubkey: winner, isSigner: false, isWritable: true }, // winner receives NFT.
        { pubkey: mint, isSigner: false, isWritable: false }, // mint is read-only.
        { pubkey: auctionPda, isSigner: false, isWritable: true }, // auction PDA is updated.
        { pubkey: escrowPda, isSigner: false, isWritable: true }, // escrow PDA releases NFT.
        { pubkey: escrowAta, isSigner: false, isWritable: true }, // escrow ATA sends NFT.
        { pubkey: winnerAta, isSigner: false, isWritable: true }, // winner's ATA receives NFT.
        { pubkey: bid, isSigner: false, isWritable: true }, // bid PDA releases lamports.
        { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // SPL token program.
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // System program.
        { pubkey: SYSVAR_CLOCK_PUBKEY, isSigner: false, isWritable: false }, // Clock verifies auction end.
      ],
      programId: MARKETPLACE_PROGRAM_ID,
      data: Buffer.from([8]), // instruction index 8 = SettleAuction.
    });
    transaction.feePayer = caller;
    transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
    res.json({ success: true, transaction: transaction.serialize({ requireAllSignatures: false }).toString("base64") });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// GET /listings returns all active fixed-price listings by querying program accounts.
app.get("/listings", async (_req, res) => {
  try {
    // Fetch all accounts owned by the marketplace program that match the listing prefix.
    const accounts = await connection.getProgramAccounts(MARKETPLACE_PROGRAM_ID, {
      filters: [{ dataSize: 106 }], // 106 bytes approximates the Listing struct size.
    ]});
    // Map raw accounts to a friendly response format with public keys and deserialized prices.
    const listings = accounts.map(({ pubkey, account }) => {
      // In a real implementation, deserialize the account data to extract seller, mint, and price.
      return { address: pubkey.toBase58(), data: account.data.toString("base64") };
    });
    res.json({ success: true, listings });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// GET /auctions returns all active auctions by querying program accounts.
app.get("/auctions", async (_req, res) => {
  try {
    const accounts = await connection.getProgramAccounts(MARKETPLACE_PROGRAM_ID, {
      filters: [{ dataSize: 154 }], // 154 bytes approximates the Auction struct size.
    ]});
    const auctions = accounts.map(({ pubkey, account }) => {
      return { address: pubkey.toBase58(), data: account.data.toString("base64") };
    });
    res.json({ success: true, auctions });
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message });
  }
});

// Start the Express server and listen on the configured port.
app.listen(PORT, () => {
  console.log(`Marketplace API listening on port ${PORT}`);
});
