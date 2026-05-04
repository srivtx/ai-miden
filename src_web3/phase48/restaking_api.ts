import express, { Request, Response } from "express"; // Import Express to build the HTTP API for staking, restaking, operator delegation, and slashing simulation

const app = express(); // Initialize the Express application instance for the restaking service

app.use(express.json()); // Enable JSON body parsing so clients can send stake, delegation, and slashing parameters

const PORT = 3052; // Use port 3052 to avoid conflicts with other Web3 phase APIs running in the project

interface Staker { // Define the Staker interface so TypeScript can enforce the shape of every user who stakes or restakes
  address: string; // On-chain address of the user who owns the stake
  baseStaked: number; // Amount of ETH staked on the base layer
  restaked: number; // Amount of base stake that has been deposited into the restaking protocol
  rewards: number; // Accumulated reward balance from all sources
} // Close the block

interface Operator { // Define the Operator interface so TypeScript can enforce the shape of every node operator running AVS software
  id: string; // Unique identifier for the operator
  name: string; // Human-readable name of the operator
  totalDelegated: number; // Total restaked amount delegated to this operator across all stakers
  commission: number; // Percentage of AVS rewards kept by the operator, e.g. 0.1 for 10%
  uptime: number; // Historical uptime percentage used to estimate slash risk
} // Close the block

interface AVS { // Define the AVS interface so TypeScript can enforce the shape of every Actively Validated Service
  id: string; // Unique identifier for the AVS
  name: string; // Human-readable name of the service
  rewardRate: number; // Annual percentage yield paid to restakers supporting this AVS
  slashConditions: { tier: string; penaltyPercent: number; description: string }[]; // List of slashable offenses and penalties
} // Close the block

interface Delegation { // Define the Delegation interface to track which staker delegated how much to which operator for which AVS
  staker: string; // Address of the delegating staker
  operatorId: string; // Identifier of the operator receiving the delegation
  avsId: string; // Identifier of the AVS being secured
  amount: number; // Amount of restaked ETH delegated to this operator for this AVS
} // Close the block

const stakers: Map<string, Staker> = new Map(); // In-memory storage for stakers keyed by wallet address

const operators: Map<string, Operator> = new Map(); // In-memory storage for operators keyed by operator ID

const avss: Map<string, AVS> = new Map(); // In-memory storage for AVSs keyed by AVS ID

const delegations: Delegation[] = []; // In-memory storage for delegations so we can compute rewards and slashing impacts

const slashHistory: { staker: string; operatorId: string; avsId: string; tier: string; amount: number; timestamp: number }[] = []; // In-memory storage for slash events so we can audit penalty history

app.get("/health", (_req: Request, res: Response) => { // Health check endpoint so load balancers and operators can verify the service is alive
  const totalRestaked = Array.from(stakers.values()).reduce((sum, s) => sum + s.restaked, 0); // Return current system status, counts, and total restaked amount for monitoring dashboards
  res.json({ // Send the JSON response to the client
    status: "healthy", // Signal that the API process is running and responsive
    stakerCount: stakers.size, // Report how many users have registered stakes
    operatorCount: operators.size, // Report how many operators are available
    avsCount: avss.size, // Report how many AVSs are registered
    totalRestaked, // Report aggregate restaked capital for health visibility
    slashEvents: slashHistory.length, // Report how many slash events have occurred
  }); // Close the route handler
}); // Close the route handler

app.post("/staker/register", (req: Request, res: Response) => { // Endpoint to register a new staker with an initial base stake amount
  const { address, baseStaked } = req.body; // Destructure required parameters from the request body

  if (!address || baseStaked === undefined) { // Validate that all required fields are present to prevent malformed registrations
    return res.status(400).json({ error: "address and baseStaked are required" }); // Return result to the caller
  } // Close the block

  if (Number(baseStaked) < 0) { // Validate that base stake is non-negative because negative stakes are impossible
    return res.status(400).json({ error: "baseStaked cannot be negative" }); // Return result to the caller
  } // Close the block

  const staker: Staker = { // Build the new Staker object with zero restaked amount and zero initial rewards
    address, // Execute the statement
    baseStaked: Number(baseStaked), // Set the property value
    restaked: 0, // Set the property value
    rewards: 0, // Set the property value
  }; // Execute the statement

  stakers.set(staker.address, staker); // Store the new staker in the in-memory map keyed by wallet address

  res.status(201).json({ success: true, staker }); // Return the full staker object so the user knows their base stake has been recorded
}); // Close the route handler

app.get("/staker/:address", (req: Request, res: Response) => { // Endpoint to fetch a single staker by address so users can check their balances
  const staker = stakers.get(req.params.address); // Look up the staker in the active stakers map using the URL parameter

  if (!staker) { // Return 404 if the staker does not exist or has not been registered
    return res.status(404).json({ error: "Staker not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, staker }); // Return the staker state so the user can view base stake, restaked amount, and rewards
}); // Close the route handler

app.post("/operator/register", (req: Request, res: Response) => { // Endpoint to register a new operator that stakers can delegate to
  const { id, name, commission, uptime } = req.body; // Destructure required parameters from the request body

  if (!id || !name || commission === undefined || uptime === undefined) { // Validate that all required fields are present to prevent malformed operator registrations
    return res.status(400).json({ error: "id, name, commission, and uptime are required" }); // Return result to the caller
  } // Close the block

  if (Number(commission) < 0 || Number(commission) > 1) { // Validate that commission is between 0 and 1 because it represents a percentage
    return res.status(400).json({ error: "commission must be between 0 and 1" }); // Return result to the caller
  } // Close the block

  const operator: Operator = { // Build the new Operator object with zero initial delegated stake
    id, // Execute the statement
    name, // Execute the statement
    totalDelegated: 0, // Set the property value
    commission: Number(commission), // Set the property value
    uptime: Number(uptime), // Set the property value
  }; // Execute the statement

  operators.set(operator.id, operator); // Store the new operator in the in-memory map keyed by operator ID

  res.status(201).json({ success: true, operator }); // Return the full operator object so the operator knows registration succeeded
}); // Close the route handler

app.get("/operator/:id", (req: Request, res: Response) => { // Endpoint to fetch a single operator by ID so stakers can evaluate delegation options
  const operator = operators.get(req.params.id); // Look up the operator in the registered operators map using the URL parameter

  if (!operator) { // Return 404 if the operator does not exist or has not been registered
    return res.status(404).json({ error: "Operator not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, operator }); // Return the operator state so stakers can compare commission, uptime, and delegation size
}); // Close the route handler

app.post("/avs/register", (req: Request, res: Response) => { // Endpoint to register a new AVS that restakers can secure
  const { id, name, rewardRate, slashConditions } = req.body; // Destructure required parameters from the request body

  if (!id || !name || rewardRate === undefined) { // Validate that all required fields are present to prevent malformed AVS registrations
    return res.status(400).json({ error: "id, name, and rewardRate are required" }); // Return result to the caller
  } // Close the block

  const avs: AVS = { // Build the new AVS object with provided slash conditions or default empty array
    id, // Execute the statement
    name, // Execute the statement
    rewardRate: Number(rewardRate), // Set the property value
    slashConditions: slashConditions || [], // Set the property value
  }; // Execute the statement

  avss.set(avs.id, avs); // Store the new AVS in the in-memory map keyed by AVS ID

  res.status(201).json({ success: true, avs }); // Return the full AVS object so the protocol knows registration succeeded
}); // Close the route handler

app.get("/avs/:id", (req: Request, res: Response) => { // Endpoint to fetch a single AVS by ID so stakers can understand risk and reward
  const avs = avss.get(req.params.id); // Look up the AVS in the registered AVSs map using the URL parameter

  if (!avs) { // Return 404 if the AVS does not exist or has not been registered
    return res.status(404).json({ error: "AVS not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, avs }); // Return the AVS state so stakers can review reward rates and slash conditions
}); // Close the route handler

app.post("/staker/restake", (req: Request, res: Response) => { // Endpoint for a staker to restake base-staked ETH into the protocol
  const { address, amount } = req.body; // Destructure required parameters from the request body

  if (!address || amount === undefined) { // Validate that all required fields are present to prevent malformed restake requests
    return res.status(400).json({ error: "address and amount are required" }); // Return result to the caller
  } // Close the block

  const staker = stakers.get(address); // Look up the target staker to ensure they exist
  if (!staker) { // Validate that the required condition is met
    return res.status(404).json({ error: "Staker not found" }); // Return result to the caller
  } // Close the block

  if (Number(amount) <= 0) { // Validate that the restake amount is positive because zero or negative restakes are meaningless
    return res.status(400).json({ error: "amount must be positive" }); // Return result to the caller
  } // Close the block

  if (Number(amount) > staker.baseStaked - staker.restaked) { // Validate that the staker has enough base stake to restake the requested amount
    return res.status(400).json({ error: "Insufficient un-restaked base stake" }); // Return result to the caller
  } // Close the block

  staker.restaked += Number(amount); // Increase the staker's restaked amount because they are locking base stake into the restaking layer

  res.json({ success: true, staker }); // Return the updated staker state so the user knows their restaked balance changed
}); // Close the route handler

app.post("/delegation/create", (req: Request, res: Response) => { // Endpoint for a staker to delegate restaked ETH to an operator for a specific AVS
  const { stakerAddress, operatorId, avsId, amount } = req.body; // Destructure required parameters from the request body

  if (!stakerAddress || !operatorId || !avsId || amount === undefined) { // Validate that all required fields are present to prevent malformed delegation requests
    return res.status(400).json({ error: "stakerAddress, operatorId, avsId, and amount are required" }); // Return result to the caller
  } // Close the block

  const staker = stakers.get(stakerAddress); // Look up the target staker to ensure they exist
  if (!staker) { // Validate that the required condition is met
    return res.status(404).json({ error: "Staker not found" }); // Return result to the caller
  } // Close the block

  const operator = operators.get(operatorId); // Look up the target operator to ensure it exists
  if (!operator) { // Validate that the required condition is met
    return res.status(404).json({ error: "Operator not found" }); // Return result to the caller
  } // Close the block

  const avs = avss.get(avsId); // Look up the target AVS to ensure it exists
  if (!avs) { // Validate that the required condition is met
    return res.status(404).json({ error: "AVS not found" }); // Return result to the caller
  } // Close the block

  if (Number(amount) <= 0) { // Validate that the delegation amount is positive because zero or negative delegations are meaningless
    return res.status(400).json({ error: "amount must be positive" }); // Return result to the caller
  } // Close the block

  const currentDelegated = delegations.filter((d) => d.staker === stakerAddress).reduce((sum, d) => sum + d.amount, 0); // Calculate the staker's currently delegated amount across all delegations to check capacity

  if (currentDelegated + Number(amount) > staker.restaked) { // Validate that the staker has enough restaked balance to cover the new delegation
    return res.status(400).json({ error: "Delegation exceeds restaked balance" }); // Return result to the caller
  } // Close the block

  const delegation: Delegation = { // Build the new Delegation object to record the relationship between staker, operator, and AVS
    staker: stakerAddress, // Set the property value
    operatorId, // Execute the statement
    avsId, // Execute the statement
    amount: Number(amount), // Set the property value
  }; // Execute the statement

  delegations.push(delegation); // Append the delegation to the global list so reward and slashing logic can reference it

  operator.totalDelegated += Number(amount); // Increase the operator's total delegated amount because they now manage more restaked capital

  res.status(201).json({ success: true, delegation }); // Return the delegation details so the staker knows their capital is now supporting the AVS
}); // Close the route handler

app.post("/rewards/accrue", (req: Request, res: Response) => { // Endpoint to simulate reward accrual for a staker across all their delegations
  const { stakerAddress, days } = req.body; // Destructure required parameters from the request body

  if (!stakerAddress || days === undefined) { // Validate that all required fields are present to prevent malformed accrual requests
    return res.status(400).json({ error: "stakerAddress and days are required" }); // Return result to the caller
  } // Close the block

  const staker = stakers.get(stakerAddress); // Look up the target staker to ensure they exist
  if (!staker) { // Validate that the required condition is met
    return res.status(404).json({ error: "Staker not found" }); // Return result to the caller
  } // Close the block

  const stakerDelegations = delegations.filter((d) => d.staker === stakerAddress); // Find all delegations belonging to this staker to compute per-AVS rewards

  const rewardBreakdown: { operatorId: string; avsId: string; avsReward: number; commission: number; netReward: number }[] = []; // Array to collect detailed reward breakdowns for the response

  for (const d of stakerDelegations) { // Iterate over every delegation to calculate pro-rata rewards based on AVS reward rates
    const avs = avss.get(d.avsId); // Look up the AVS to get its annual reward rate
    if (!avs) continue; // Skip if AVS no longer exists to avoid crashes

    const operator = operators.get(d.operatorId); // Look up the operator to get its commission rate
    if (!operator) continue; // Skip if operator no longer exists to avoid crashes

    const annualAvsReward = d.amount * avs.rewardRate; // Calculate the raw AVS reward for the delegation amount over the given days
    const periodAvsReward = (annualAvsReward * Number(days)) / 365; // Declare and initialize the variable

    const commissionAmount = periodAvsReward * operator.commission; // Deduct operator commission because operators keep a portion of AVS rewards
    const netReward = periodAvsReward - commissionAmount; // Declare and initialize the variable

    staker.rewards += netReward; // Add the net reward to the staker's accumulated balance

    rewardBreakdown.push({ operatorId: d.operatorId, avsId: d.avsId, avsReward: periodAvsReward, commission: commissionAmount, netReward }); // Record the breakdown so the staker can audit how much each AVS contributed
  } // Close the block

  res.json({ success: true, staker, days, rewardBreakdown }); // Return the reward summary so the staker knows how much they earned and from where
}); // Close the route handler

app.post("/slash/apply", (req: Request, res: Response) => { // Endpoint to simulate a slashing event on a specific delegation
  const { stakerAddress, operatorId, avsId, tier } = req.body; // Destructure required parameters from the request body

  if (!stakerAddress || !operatorId || !avsId || !tier) { // Validate that all required fields are present to prevent malformed slash requests
    return res.status(400).json({ error: "stakerAddress, operatorId, avsId, and tier are required" }); // Return result to the caller
  } // Close the block

  const staker = stakers.get(stakerAddress); // Look up the target staker to ensure they exist
  if (!staker) { // Validate that the required condition is met
    return res.status(404).json({ error: "Staker not found" }); // Return result to the caller
  } // Close the block

  const avs = avss.get(avsId); // Look up the target AVS to find the penalty percentage for the given tier
  if (!avs) { // Validate that the required condition is met
    return res.status(404).json({ error: "AVS not found" }); // Return result to the caller
  } // Close the block

  const condition = avs.slashConditions.find((c) => c.tier === tier); // Find the matching slash condition by tier name to determine the penalty
  if (!condition) { // Validate that the required condition is met
    return res.status(400).json({ error: `Slash tier '${tier}' not found for AVS ${avsId}` }); // Return result to the caller
  } // Close the block

  const delegation = delegations.find((d) => d.staker === stakerAddress && d.operatorId === operatorId && d.avsId === avsId); // Find the target delegation to know how much capital is at risk
  if (!delegation) { // Validate that the required condition is met
    return res.status(404).json({ error: "Delegation not found" }); // Return result to the caller
  } // Close the block

  const slashAmount = delegation.amount * (condition.penaltyPercent / 100); // Calculate the slash amount based on the delegation amount and the tier penalty percentage

  staker.restaked -= slashAmount; // Deduct the slash amount from the staker's restaked balance because slashing destroys collateral

  if (staker.restaked < 0) staker.restaked = 0; // Ensure restaked balance does not go negative due to rounding errors or misconfiguration

  delegation.amount -= slashAmount; // Reduce the delegation amount to reflect the lost collateral

  if (delegation.amount < 0) delegation.amount = 0; // Ensure delegation amount does not go negative due to rounding errors

  slashHistory.push({ staker: stakerAddress, operatorId, avsId, tier, amount: slashAmount, timestamp: Date.now() }); // Record the slash event in history for auditing and transparency

  res.json({ success: true, staker, slashAmount, penaltyPercent: condition.penaltyPercent, reason: condition.description }); // Return the slash details so the staker knows exactly how much they lost and why
}); // Close the route handler

app.get("/market/stats", (_req: Request, res: Response) => { // Endpoint to retrieve aggregate restaking statistics for dashboards
  const totalBaseStaked = Array.from(stakers.values()).reduce((sum, s) => sum + s.baseStaked, 0); // Calculate total base staked across all users to understand the capital base

  const totalRestaked = Array.from(stakers.values()).reduce((sum, s) => sum + s.restaked, 0); // Calculate total restaked across all users to understand shared security size

  const totalRewards = Array.from(stakers.values()).reduce((sum, s) => sum + s.rewards, 0); // Calculate total rewards distributed across all users to understand yield output

  res.json({ // Return market stats so dashboards can display capital efficiency and system health
    totalBaseStaked, // Execute the statement
    totalRestaked, // Execute the statement
    totalRewards, // Execute the statement
    operatorCount: operators.size, // Set the property value
    avsCount: avss.size, // Set the property value
    slashEvents: slashHistory.length, // Set the property value
  }); // Close the route handler
}); // Close the route handler

app.listen(PORT, () => { // Start the Express server on the designated port and log readiness
  console.log(`Restaking API listening on port ${PORT}`); // Log startup so operators know the service is ready
}); // Close the route handler
