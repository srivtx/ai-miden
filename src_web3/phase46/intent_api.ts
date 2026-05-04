import express, { Request, Response } from "express"; // Import Express to build the HTTP API for intent submission, solver competition, and batch settlement

const app = express(); // Initialize the Express application instance for the intent-based architecture service

app.use(express.json()); // Enable JSON body parsing so clients can send intent constraints and solver proposals

const PORT = 3050; // Use port 3050 to avoid conflicts with other Web3 phase APIs running in the project

interface Intent { // Define the Intent interface so TypeScript can enforce the shape of every user request
  id: string; // Unique identifier for referencing and tracking a specific intent
  user: string; // Wallet address or identifier of the user who submitted the intent
  inputToken: string; // Token the user wants to spend or lock
  inputAmount: number; // Quantity of the input token offered by the user
  outputToken: string; // Token the user wants to receive
  minOutput: number; // Minimum acceptable output amount that protects the user from bad fills
  deadline: number; // Unix timestamp after which the intent expires and cannot be filled
  status: "open" | "filled" | "expired"; // Lifecycle state tracking whether the intent is still available
} // Close the block

interface SolverProposal { // Define the SolverProposal interface so TypeScript can enforce the shape of every solver bid
  intentId: string; // Reference to the intent this proposal aims to fill
  solver: string; // Identifier of the solver submitting the proposal
  outputAmount: number; // Total output tokens the solver promises to deliver
  route: string; // Human-readable description of the execution path chosen by the solver
  timestamp: number; // Unix timestamp when the proposal was submitted for ordering and expiry checks
} // Close the block

interface BatchWindow { // Define the BatchWindow interface to configure how long intents are collected before settlement
  start: number; // Unix timestamp when the current batch window opened
  durationMs: number; // Length of the batch window in milliseconds
} // Close the block

const intents: Map<string, Intent> = new Map(); // In-memory storage for open intents because this is an educational simulation without a database

const proposals: Map<string, SolverProposal[]> = new Map(); // In-memory storage for solver proposals so we can rank them during batch settlement

const batchHistory: { batchId: number; settledAt: number; intentIds: string[] }[] = []; // In-memory storage for batch history so we can audit past settlements

const batchWindow: BatchWindow = { start: Date.now(), durationMs: 60000 }; // Current batch configuration with a 60-second window to simulate frequent auctions

let nextIntentId = 1; // Sequence counter to generate unique intent IDs without an external database

let nextBatchId = 1; // Sequence counter to generate unique batch IDs for historical tracking

app.get("/health", (_req: Request, res: Response) => { // Health check endpoint so load balancers and operators can verify the service is alive
  res.json({ // Return current system status, batch timing, and counts for monitoring dashboards
    status: "healthy", // Signal that the API process is running and responsive
    openIntents: intents.size, // Report how many intents are currently active
    batchStart: batchWindow.start, // Include batch start time for diagnostics
    batchDurationMs: batchWindow.durationMs, // Include batch duration for diagnostics
    totalBatchesSettled: batchHistory.length, // Report how many batches have been processed
  }); // Close the route handler
}); // Close the route handler

app.post("/intent/submit", (req: Request, res: Response) => { // Endpoint to submit a new intent with constraints that solvers must satisfy
  const { user, inputToken, inputAmount, outputToken, minOutput, deadline } = req.body; // Destructure required parameters from the request body

  if (!user || !inputToken || inputAmount === undefined || !outputToken || minOutput === undefined || !deadline) { // Validate that all required fields are present to prevent malformed intents
    return res.status(400).json({ error: "user, inputToken, inputAmount, outputToken, minOutput, and deadline are required" }); // Return result to the caller
  } // Close the block

  if (minOutput <= 0) { // Validate that the minimum output is positive because a zero or negative minimum is meaningless
    return res.status(400).json({ error: "minOutput must be positive" }); // Return result to the caller
  } // Close the block

  if (inputAmount <= 0) { // Validate that the input amount is positive because you cannot swap zero or negative tokens
    return res.status(400).json({ error: "inputAmount must be positive" }); // Return result to the caller
  } // Close the block

  const intent: Intent = { // Build the new Intent object with all provided constraints
    id: String(nextIntentId++), // Increment global ID counter so every intent is unique
    user, // Execute the statement
    inputToken, // Execute the statement
    inputAmount: Number(inputAmount), // Set the property value
    outputToken, // Execute the statement
    minOutput: Number(minOutput), // Set the property value
    deadline: Number(deadline), // Set the property value
    status: "open", // Set lifecycle state to open so solvers can propose fills
  }; // Execute the statement

  intents.set(intent.id, intent); // Store the new intent in the in-memory map keyed by its unique ID

  proposals.set(intent.id, []); // Initialize an empty proposal array for this intent so solvers can later append bids

  res.status(201).json({ success: true, intent }); // Return the full intent object so the user knows their request has been registered
}); // Close the route handler

app.get("/intent/:id", (req: Request, res: Response) => { // Endpoint to fetch a single intent by ID so users can check their current status
  const intent = intents.get(req.params.id); // Look up the intent in the active intents map using the URL parameter

  if (!intent) { // Return 404 if the intent does not exist or has already been removed
    return res.status(404).json({ error: "Intent not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, intent }); // Return the intent state so the user can view constraints and fill status
}); // Close the route handler

app.get("/intents/open", (_req: Request, res: Response) => { // Endpoint to list all open intents so solvers can discover opportunities
  const openIntents = Array.from(intents.values()).filter((i) => i.status === "open"); // Filter the intents map to find only intents with open status

  res.json({ success: true, count: openIntents.length, intents: openIntents }); // Return the filtered list so solvers and frontends can display available intents
}); // Close the route handler

app.post("/solver/propose", (req: Request, res: Response) => { // Endpoint for solvers to submit a proposal to fill a specific intent
  const { intentId, solver, outputAmount, route } = req.body; // Destructure required parameters from the request body

  if (!intentId || !solver || outputAmount === undefined || !route) { // Validate that all required fields are present to prevent malformed proposals
    return res.status(400).json({ error: "intentId, solver, outputAmount, and route are required" }); // Return result to the caller
  } // Close the block

  const intent = intents.get(intentId); // Look up the target intent to ensure it exists and is still open

  if (!intent) { // Return 404 if the intent does not exist because you cannot propose to a missing intent
    return res.status(404).json({ error: "Intent not found" }); // Return result to the caller
  } // Close the block

  if (intent.status !== "open") { // Reject proposals for intents that are already filled or expired to keep state consistent
    return res.status(400).json({ error: "Intent is not open for proposals" }); // Return result to the caller
  } // Close the block

  if (Number(outputAmount) < intent.minOutput) { // Reject proposals that fail to meet the minimum output because the user explicitly set a floor
    return res.status(400).json({ error: `Proposal output ${outputAmount} is below intent minimum ${intent.minOutput}` }); // Return result to the caller
  } // Close the block

  const proposal: SolverProposal = { // Build the new SolverProposal object with all provided details
    intentId, // Execute the statement
    solver, // Execute the statement
    outputAmount: Number(outputAmount), // Set the property value
    route, // Execute the statement
    timestamp: Date.now(), // Record submission time so batch auctions can filter stale proposals
  }; // Execute the statement

  const existing = proposals.get(intentId) || []; // Append the proposal to the intent's proposal list so it competes in the next batch settlement
  existing.push(proposal); // Append the item to the array
  proposals.set(intentId, existing); // Store the object in the in-memory map

  res.status(201).json({ success: true, proposal }); // Return confirmation so the solver knows their bid has been registered
}); // Close the route handler

app.get("/intent/:id/proposals", (req: Request, res: Response) => { // Endpoint to view all proposals for a specific intent so users can compare solver bids
  const intentProposals = proposals.get(req.params.id) || []; // Look up the proposals array for the given intent ID

  res.json({ success: true, count: intentProposals.length, proposals: intentProposals }); // Return the proposals so users can inspect the competitive landscape before settlement
}); // Close the route handler

app.post("/batch/settle", (_req: Request, res: Response) => { // Endpoint to run a batch auction and settle all open intents with the best available proposals
  const settlements: { intentId: string; winner: string | null; outputAmount: number; route: string }[] = []; // Array to collect settlement results for every intent processed in this batch

  for (const intent of intents.values()) { // Iterate over all intents to evaluate and settle the open ones
    if (intent.status !== "open") continue; // Skip intents that are not open because only open intents participate in the batch

    if (Date.now() > intent.deadline) { // Check if the intent has expired by comparing its deadline to the current time
      intent.status = "expired"; // Mark the intent as expired so it no longer accepts proposals
      settlements.push({ intentId: intent.id, winner: null, outputAmount: 0, route: "expired" }); // Execute the statement
      continue; // Skip to the next iteration
    } // Close the block

    const intentProposals = proposals.get(intent.id) || []; // Retrieve all proposals for this intent to find the best one

    if (intentProposals.length === 0) { // If there are no proposals, the intent remains open for the next batch
      settlements.push({ intentId: intent.id, winner: null, outputAmount: 0, route: "no proposals" }); // Execute the statement
      continue; // Skip to the next iteration
    } // Close the block

    const ranked = intentProposals.sort((a, b) => b.outputAmount - a.outputAmount); // Rank proposals by output amount descending because higher output is better for the user

    const winner = ranked[0]; // Select the top proposal as the winner because it offers the best outcome

    intent.status = "filled"; // Update the intent status to filled so it will not be settled again

    settlements.push({ intentId: intent.id, winner: winner.solver, outputAmount: winner.outputAmount, route: winner.route }); // Record the settlement details for auditing and user notification
  } // Close the block

  batchHistory.push({ batchId: nextBatchId++, settledAt: Date.now(), intentIds: settlements.map((s) => s.intentId) }); // Record this batch settlement in history so operators can review past performance

  batchWindow.start = Date.now(); // Reset the batch window start time to begin collecting the next batch immediately

  res.json({ success: true, settledCount: settlements.length, settlements }); // Return a summary of the batch settlement so operators can audit the auction results
}); // Close the route handler

app.get("/market/stats", (_req: Request, res: Response) => { // Endpoint to retrieve aggregate solver statistics so operators can evaluate market competitiveness
  const openCount = Array.from(intents.values()).filter((i) => i.status === "open").length; // Calculate total open intents to understand current demand

  const filledCount = Array.from(intents.values()).filter((i) => i.status === "filled").length; // Calculate total filled intents to understand historical success rate

  const expiredCount = Array.from(intents.values()).filter((i) => i.status === "expired").length; // Calculate total expired intents to understand how often demand goes unsatisfied

  res.json({ // Return market stats so dashboards can display demand, success, and solver activity
    openIntents: openCount, // Set the property value
    filledIntents: filledCount, // Set the property value
    expiredIntents: expiredCount, // Set the property value
    totalProposals: Array.from(proposals.values()).reduce((sum, arr) => sum + arr.length, 0), // Sum all proposals across every intent
    totalBatchesSettled: batchHistory.length, // Set the property value
    batchWindowStart: batchWindow.start, // Set the property value
    batchWindowDurationMs: batchWindow.durationMs, // Set the property value
  }); // Close the route handler
}); // Close the route handler

app.get("/batch/history", (_req: Request, res: Response) => { // Endpoint to retrieve batch history so operators can audit past settlements
  res.json({ success: true, count: batchHistory.length, history: batchHistory }); // Return the full batch history array so analytics tools can review auction trends
}); // Close the route handler

app.listen(PORT, () => { // Start the Express server on the designated port and log readiness
  console.log(`Intent-Based Architecture API listening on port ${PORT}`); // Log startup so operators know the service is ready
}); // Close the route handler
