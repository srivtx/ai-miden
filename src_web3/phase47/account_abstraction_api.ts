import express, { Request, Response } from "express"; // Import Express to build the HTTP API for UserOperations, bundlers, smart contract wallets, and paymasters

const app = express(); // Initialize the Express application instance for the account abstraction service

app.use(express.json()); // Enable JSON body parsing so clients can send UserOperations and wallet configuration data

const PORT = 3051; // Use port 3051 to avoid conflicts with other Web3 phase APIs running in the project

interface UserOperation { // Define the UserOperation interface so TypeScript can enforce the shape of every abstracted transaction
  sender: string; // Address of the smart contract wallet that initiates the operation
  nonce: number; // Sequence number preventing replay attacks on the wallet contract
  callData: string; // Encoded function call that the wallet contract will execute
  signature: string; // Cryptographic proof authorizing this operation from the wallet owner
  paymaster: string | null; // Address of a paymaster sponsoring gas, or null if the user pays
  paymasterData: string | null; // Additional validation data required by the paymaster contract
} // Close the block

interface SmartContractWallet { // Define the SmartContractWallet interface to track deployed wallets and their rules
  address: string; // On-chain address of the smart contract wallet
  owner: string; // Primary owner address that controls the wallet
  guardians: string[]; // List of trusted addresses that can assist with social recovery
  dailyLimit: number; // Maximum amount that can be spent in a single day without extra approval
  requiredSigs: number; // Number of signatures required for transactions exceeding the daily limit
  signers: string[]; // List of authorized signer addresses for multi-signature validation
  lastActivity: number; // Unix timestamp of the last successful transaction for recovery timers
} // Close the block

interface Paymaster { // Define the Paymaster interface to track paymaster contracts, deposits, and usage
  address: string; // On-chain address of the paymaster contract
  deposit: number; // Balance of native token deposited in the EntryPoint available for gas sponsorship
  acceptedToken: string | null; // ERC-20 token the paymaster accepts as reimbursement, or null for free sponsorship
  minBalance: number; // Minimum user token balance required to qualify for sponsorship
  fee: number; // Fee charged in acceptedToken units when sponsorship is granted
} // Close the block

const userOpPool: UserOperation[] = []; // In-memory storage for submitted UserOperations because this is an educational simulation without a database

const wallets: Map<string, SmartContractWallet> = new Map(); // In-memory storage for deployed smart contract wallets keyed by wallet address

const paymasters: Map<string, Paymaster> = new Map(); // In-memory storage for registered paymasters keyed by paymaster address

const bundleHistory: { bundleId: number; operations: UserOperation[]; settledAt: number }[] = []; // In-memory storage for bundler-submitted batches so we can trace execution history

let nextBundleId = 1; // Sequence counter to generate unique bundle IDs without an external database

app.get("/health", (_req: Request, res: Response) => { // Health check endpoint so load balancers and operators can verify the service is alive
  res.json({ // Return current system status, pool sizes, and counts for monitoring dashboards
    status: "healthy", // Signal that the API process is running and responsive
    userOpsInPool: userOpPool.length, // Report how many UserOperations are waiting for bundling
    walletCount: wallets.size, // Report how many smart contract wallets have been deployed
    paymasterCount: paymasters.size, // Report how many paymasters are registered
    bundleCount: bundleHistory.length, // Report how many bundles have been settled
  }); // Close the route handler
}); // Close the route handler

app.post("/wallet/deploy", (req: Request, res: Response) => { // Endpoint to deploy a new smart contract wallet with programmable rules
  const { address, owner, guardians, dailyLimit, requiredSigs, signers } = req.body; // Destructure required parameters from the request body

  if (!address || !owner || dailyLimit === undefined || requiredSigs === undefined) { // Validate that all required fields are present to prevent malformed wallet deployments
    return res.status(400).json({ error: "address, owner, dailyLimit, and requiredSigs are required" }); // Return result to the caller
  } // Close the block

  if (Number(requiredSigs) < 1) { // Validate that required signatures is at least one because a wallet must have at least one signer
    return res.status(400).json({ error: "requiredSigs must be at least 1" }); // Return result to the caller
  } // Close the block

  const wallet: SmartContractWallet = { // Build the new SmartContractWallet object with all provided configuration
    address, // Execute the statement
    owner, // Execute the statement
    guardians: guardians || [], // Default to empty array if no guardians are provided
    dailyLimit: Number(dailyLimit), // Set the property value
    requiredSigs: Number(requiredSigs), // Set the property value
    signers: signers || [owner], // Default to owner as sole signer if no explicit signers are provided
    lastActivity: Date.now(), // Initialize activity timestamp to now for recovery logic
  }; // Execute the statement

  wallets.set(wallet.address, wallet); // Store the new wallet in the in-memory map keyed by its address

  res.status(201).json({ success: true, wallet }); // Return the full wallet object so the owner knows the deployment rules have been registered
}); // Close the route handler

app.get("/wallet/:address", (req: Request, res: Response) => { // Endpoint to fetch a single smart contract wallet by address so users can check configuration
  const wallet = wallets.get(req.params.address); // Look up the wallet in the active wallets map using the URL parameter

  if (!wallet) { // Return 404 if the wallet does not exist or has not been deployed
    return res.status(404).json({ error: "Wallet not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, wallet }); // Return the wallet state so the user can view signers, limits, and guardians
}); // Close the route handler

app.post("/userop/submit", (req: Request, res: Response) => { // Endpoint to submit a UserOperation to the mempool for later bundling
  const { sender, nonce, callData, signature, paymaster, paymasterData } = req.body; // Destructure required parameters from the request body

  if (!sender || nonce === undefined || !callData || !signature) { // Validate that all required fields are present to prevent malformed operations
    return res.status(400).json({ error: "sender, nonce, callData, and signature are required" }); // Return result to the caller
  } // Close the block

  const wallet = wallets.get(sender); // Look up the sender wallet to ensure it exists before accepting the operation
  if (!wallet) { // Validate that the required condition is met
    return res.status(404).json({ error: "Sender wallet not found" }); // Return result to the caller
  } // Close the block

  const userOp: UserOperation = { // Build the new UserOperation object with all provided fields
    sender, // Execute the statement
    nonce: Number(nonce), // Set the property value
    callData, // Execute the statement
    signature, // Execute the statement
    paymaster: paymaster || null, // Allow null to indicate user-paid gas
    paymasterData: paymasterData || null, // Set the property value
  }; // Execute the statement

  userOpPool.push(userOp); // Push the operation into the pool so bundlers can collect it for the next bundle

  wallet.lastActivity = Date.now(); // Update the wallet's last activity timestamp because a new operation indicates owner activity

  res.status(201).json({ success: true, userOp, poolPosition: userOpPool.length }); // Return confirmation so the user knows their operation is pending bundling
}); // Close the route handler

app.get("/userop/pool", (_req: Request, res: Response) => { // Endpoint to list all UserOperations currently in the mempool so bundlers can plan batches
  res.json({ success: true, count: userOpPool.length, operations: userOpPool }); // Return the entire pool so bundler nodes can inspect pending operations
}); // Close the route handler

app.post("/bundler/submit", (_req: Request, res: Response) => { // Endpoint to simulate a bundler packaging UserOperations into a bundle and submitting to the EntryPoint
  if (userOpPool.length === 0) { // If the pool is empty, reject the bundle submission because there is nothing to execute
    return res.status(400).json({ error: "UserOperation pool is empty" }); // Return result to the caller
  } // Close the block

  const bundleOps = userOpPool.slice(); // Copy all current pool operations into a bundle so we can clear the pool afterward

  userOpPool.length = 0; // Clear the pool because these operations are now claimed by the bundler

  bundleHistory.push({ bundleId: nextBundleId++, operations: bundleOps, settledAt: Date.now() }); // Record the bundle in history so operators can trace execution order

  res.json({ success: true, bundleId: nextBundleId - 1, operationCount: bundleOps.length, operations: bundleOps }); // Return the bundle details so the bundler knows which operations were included
}); // Close the route handler

app.post("/paymaster/register", (req: Request, res: Response) => { // Endpoint to register a new paymaster that can sponsor gas for qualifying UserOperations
  const { address, deposit, acceptedToken, minBalance, fee } = req.body; // Destructure required parameters from the request body

  if (!address || deposit === undefined || minBalance === undefined || fee === undefined) { // Validate that all required fields are present to prevent malformed paymaster registration
    return res.status(400).json({ error: "address, deposit, minBalance, and fee are required" }); // Return result to the caller
  } // Close the block

  const paymaster: Paymaster = { // Build the new Paymaster object with all provided configuration
    address, // Execute the statement
    deposit: Number(deposit), // Set the property value
    acceptedToken: acceptedToken || null, // Allow null for unconditional or free sponsorship
    minBalance: Number(minBalance), // Set the property value
    fee: Number(fee), // Set the property value
  }; // Execute the statement

  paymasters.set(paymaster.address, paymaster); // Store the new paymaster in the in-memory map keyed by its address

  res.status(201).json({ success: true, paymaster }); // Return the full paymaster object so the operator knows registration succeeded
}); // Close the route handler

app.get("/paymaster/:address", (req: Request, res: Response) => { // Endpoint to fetch a single paymaster by address so operators can check deposit balances
  const paymaster = paymasters.get(req.params.address); // Look up the paymaster in the registered paymasters map using the URL parameter

  if (!paymaster) { // Return 404 if the paymaster does not exist or has not been registered
    return res.status(404).json({ error: "Paymaster not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, paymaster }); // Return the paymaster state so operators can monitor deposits and fee settings
}); // Close the route handler

app.post("/paymaster/validate", (req: Request, res: Response) => { // Endpoint to simulate paymaster validation for a UserOperation
  const { paymasterAddress, sender, userTokenBalance } = req.body; // Destructure required parameters from the request body

  if (!paymasterAddress || !sender || userTokenBalance === undefined) { // Validate that all required fields are present to prevent malformed validation requests
    return res.status(400).json({ error: "paymasterAddress, sender, and userTokenBalance are required" }); // Return result to the caller
  } // Close the block

  const paymaster = paymasters.get(paymasterAddress); // Look up the target paymaster to ensure it exists
  if (!paymaster) { // Validate that the required condition is met
    return res.status(404).json({ error: "Paymaster not found" }); // Return result to the caller
  } // Close the block

  if (paymaster.deposit <= 0) { // Check if the paymaster has enough deposit to sponsor gas because a dry paymaster cannot fulfill its promise
    return res.json({ valid: false, reason: "Paymaster deposit is empty" }); // Return result to the caller
  } // Close the block

  if (Number(userTokenBalance) < paymaster.minBalance) { // Check if the user's token balance meets the minimum required by the paymaster
    return res.json({ valid: false, reason: "User token balance below paymaster minimum" }); // Return result to the caller
  } // Close the block

  res.json({ valid: true, fee: paymaster.fee, acceptedToken: paymaster.acceptedToken }); // If all checks pass, the paymaster will sponsor this operation
}); // Close the route handler

app.post("/wallet/recover", (req: Request, res: Response) => { // Endpoint to simulate social recovery by guardian vote
  const { walletAddress, guardianVotes, newOwner } = req.body; // Destructure required parameters from the request body

  if (!walletAddress || !guardianVotes || !newOwner) { // Validate that all required fields are present to prevent malformed recovery requests
    return res.status(400).json({ error: "walletAddress, guardianVotes, and newOwner are required" }); // Return result to the caller
  } // Close the block

  const wallet = wallets.get(walletAddress); // Look up the target wallet to ensure it exists
  if (!wallet) { // Validate that the required condition is met
    return res.status(404).json({ error: "Wallet not found" }); // Return result to the caller
  } // Close the block

  const validVotes = guardianVotes.filter((g: string) => wallet.guardians.includes(g)); // Count how many submitted votes match actual guardians because only real guardians count

  if (validVotes.length < 2) { // Require at least two guardian votes to approve recovery because a single guardian should not control the wallet
    return res.status(400).json({ error: `Only ${validVotes.length} valid guardian votes. At least 2 required.` }); // Return result to the caller
  } // Close the block

  const daysInactive = (Date.now() - wallet.lastActivity) / (1000 * 60 * 60 * 24); // Check if the wallet has been inactive long enough to allow recovery, simulating a time-lock rule
  if (daysInactive < 30) { // Check the condition before proceeding
    return res.status(400).json({ error: `Wallet was active ${daysInactive.toFixed(1)} days ago. Recovery allowed after 30 days of inactivity.` }); // Return result to the caller
  } // Close the block

  wallet.owner = newOwner; // Update the wallet owner to the new address because recovery was approved

  wallet.signers = [newOwner]; // Reset signers to the new owner because old keys may be compromised

  wallet.lastActivity = Date.now(); // Update last activity to now because recovery counts as a wallet interaction

  res.json({ success: true, wallet, validVotes: validVotes.length }); // Return confirmation so guardians and the new owner know recovery succeeded
}); // Close the route handler

app.get("/stats", (_req: Request, res: Response) => { // Endpoint to retrieve aggregate account abstraction statistics for dashboards
  res.json({ // Return summary stats so dashboards can display adoption and system health
    walletsDeployed: wallets.size, // Set the property value
    paymastersRegistered: paymasters.size, // Set the property value
    userOpsPending: userOpPool.length, // Set the property value
    bundlesSettled: bundleHistory.length, // Set the property value
  }); // Close the route handler
}); // Close the route handler

app.listen(PORT, () => { // Start the Express server on the designated port and log readiness
  console.log(`Account Abstraction API listening on port ${PORT}`); // Log startup so operators know the service is ready
}); // Close the route handler
