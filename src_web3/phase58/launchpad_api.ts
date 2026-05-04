import express, { Request, Response } from "express"; // WHY: Import Express to build the HTTP API that simulates token launchpad on-chain operations off-chain.

const app = express(); // WHY: Initialize the Express application instance for the token launchpad service.

app.use(express.json()); // WHY: Enable JSON body parsing so clients can send project details and participation requests.

const PORT = 3062; // WHY: Use port 3062 to avoid conflicts with other Web3 phase APIs running in the project.

interface Tier { // WHY: Define the Tier interface so TypeScript can enforce the shape of every participation tier.
  id: string; // WHY: Unique identifier for referencing a specific tier within a project.
  name: string; // WHY: Human-readable tier name such as "Early Adopters" or "Public" for display purposes.
  price: number; // WHY: Price per token in this tier so the contract can compute how many tokens a user receives.
  maxAllocation: number; // WHY: Maximum amount a single wallet can contribute to this tier to prevent whale dominance.
  tokensReserved: number; // WHY: Number of tokens allocated to this tier so the contract can enforce supply limits.
  whitelist: string[]; // WHY: Array of wallet addresses approved for this tier so only authorized users can participate.
} // WHY: Close the Tier interface block.

interface Project { // WHY: Define the Project interface so TypeScript can enforce the shape of every registered sale.
  id: string; // WHY: Unique identifier for referencing and tracking a specific token sale.
  name: string; // WHY: Human-readable project name so users can distinguish between different token sales.
  tokenMint: string; // WHY: On-chain token mint address that identifies the token being sold.
  totalTokens: number; // WHY: Total supply of tokens offered in the sale so the contract can enforce hard supply limits.
  hardCap: number; // WHY: Maximum fundraising goal that caps total contributions and prevents over-collection.
  softCap: number; // WHY: Minimum viable funding threshold that determines whether the sale succeeds or enables refunds.
  raised: number; // WHY: Current amount of payment tokens collected so the API can report progress toward caps.
  startTime: number; // WHY: Unix timestamp when the sale opens so the contract can reject early contributions.
  endTime: number; // WHY: Unix timestamp when the sale closes so the contract can enforce the deadline.
  status: "upcoming" | "active" | "success" | "failed"; // WHY: Lifecycle state tracking whether the sale is open, finished, or refundable.
  creator: string; // WHY: Wallet address of the project team so funds can be routed correctly upon success.
  tiers: Tier[]; // WHY: Array of tiers so each project can configure multiple pricing levels and whitelist groups.
} // WHY: Close the Project interface block.

interface Participation { // WHY: Define the Participation interface so TypeScript can enforce the shape of every user contribution.
  id: string; // WHY: Unique identifier for referencing a specific contribution record.
  projectId: string; // WHY: Reference to the project this contribution belongs to for lookups and accounting.
  user: string; // WHY: Wallet address of the participant so tokens and refunds can be routed correctly.
  amount: number; // WHY: Amount of payment tokens contributed so the contract can compute allocation and refunds.
  tierId: string; // WHY: Reference to the tier this contribution was made under for price and limit enforcement.
  tokensAllocated: number; // WHY: Number of project tokens this contribution earned based on tier price.
  claimed: boolean; // WHY: Flag indicating whether the user has already claimed their tokens to prevent double claims.
  refunded: boolean; // WHY: Flag indicating whether the user has already received a refund to prevent double refunds.
  timestamp: number; // WHY: Unix timestamp when the contribution occurred for chronological ordering and vesting math.
} // WHY: Close the Participation interface block.

const projects: Map<string, Project> = new Map(); // WHY: In-memory storage for registered projects because this is an educational simulation without a database.

const participations: Map<string, Participation[]> = new Map(); // WHY: In-memory storage for user contributions keyed by project ID so we can aggregate allocations per sale.

let nextProjectId = 1; // WHY: Sequence counter to generate unique project IDs without an external database.

let nextParticipationId = 1; // WHY: Sequence counter to generate unique participation IDs for bookkeeping.

// WHY: Seed mock data so the API is runnable standalone and students can test routes immediately without manual setup.
const mockProject: Project = { // WHY: Create a realistic sample project so learners can see the expected data shape.
  id: String(nextProjectId++), // WHY: Increment the global ID counter so the mock project has a unique identifier.
  name: "SolanaCat Token", // WHY: Provide a memorable example project name for demonstration.
  tokenMint: "SCAT111111111111111111111111111111111111111", // WHY: Use a placeholder mint address to simulate an on-chain SPL token mint.
  totalTokens: 1000000, // WHY: Set a realistic total supply so tier math produces sensible allocation numbers.
  hardCap: 500000, // WHY: Set a hard cap that limits total contributions and forces partial refund logic when exceeded.
  softCap: 100000, // WHY: Set a soft cap that determines the minimum success threshold and refund eligibility.
  raised: 0, // WHY: Initialize raised amount to zero because the sale has not started yet in the mock state.
  startTime: Math.floor(Date.now() / 1000), // WHY: Set the sale start time to now so the mock project is immediately active for testing.
  endTime: Math.floor(Date.now() / 1000) + 86400, // WHY: Set the sale end time to 24 hours later so there is a realistic active window.
  status: "active", // WHY: Mark the mock project as active so participation endpoints accept contributions immediately.
  creator: "Creator222222222222222222222222222222222222", // WHY: Use a placeholder creator address to simulate the project team wallet.
  tiers: [ // WHY: Define three tiers to demonstrate tiered pricing, whitelisting, and allocation limits.
    { // WHY: Open the first tier configuration.
      id: "tier-1", // WHY: Assign a stable tier ID so participation requests can reference it.
      name: "Early Adopters", // WHY: Name the tier to reward early community members with the best price.
      price: 0.4, // WHY: Set the lowest price to incentivize early participation and bootstrap momentum.
      maxAllocation: 2000, // WHY: Cap per-user spending to distribute opportunity across many small participants.
      tokensReserved: 250000, // WHY: Reserve a quarter of supply for early adopters to guarantee their allocation pool.
      whitelist: ["UserAAA111111111111111111111111111111111", "UserBBB111111111111111111111111111111111"], // WHY: Pre-populate the whitelist so students can test tier-restricted participation immediately.
    }, // WHY: Close the first tier configuration.
    { // WHY: Open the second tier configuration.
      id: "tier-2", // WHY: Assign a stable tier ID for participation routing.
      name: "Community", // WHY: Name the tier for users who engage with the community but are not earliest adopters.
      price: 0.45, // WHY: Set a slightly higher price to reflect reduced early risk and reward community engagement.
      maxAllocation: 1500, // WHY: Lower the max allocation compared to tier 1 to spread access more broadly.
      tokensReserved: 333333, // WHY: Reserve roughly one-third of supply for the community tier based on example math.
      whitelist: ["UserAAA111111111111111111111111111111111", "UserCCC111111111111111111111111111111111"], // WHY: Include a partially overlapping whitelist to demonstrate tier-specific authorization.
    }, // WHY: Close the second tier configuration.
    { // WHY: Open the third tier configuration.
      id: "tier-3", // WHY: Assign a stable tier ID for public participation.
      name: "Public", // WHY: Name the tier for general access so anyone can join without special status.
      price: 0.5, // WHY: Set the highest price because public buyers have the lowest risk and latest access.
      maxAllocation: 1000, // WHY: Further reduce the max allocation to prioritize broader distribution over whale buys.
      tokensReserved: 416667, // WHY: Reserve the remaining supply for public buyers to complete the 1,000,000 token allocation.
      whitelist: [], // WHY: Leave the whitelist empty to signify open access for any wallet address.
    }, // WHY: Close the third tier configuration.
  ], // WHY: Close the tiers array.
}; // WHY: Close the mock project object.

projects.set(mockProject.id, mockProject); // WHY: Store the mock project in the in-memory map so GET /projects returns data immediately.

participations.set(mockProject.id, []); // WHY: Initialize an empty participation array for the mock project so contribution logic can append safely.

// WHY: Seed a mock participation so the API demonstrates allocations and claim/refund state out of the box.
const mockParticipation: Participation = { // WHY: Create a realistic sample participation so learners can see the expected record shape.
  id: String(nextParticipationId++), // WHY: Increment the global participation counter so the mock record has a unique identifier.
  projectId: mockProject.id, // WHY: Link the mock participation to the mock project so lookups resolve correctly.
  user: "UserAAA111111111111111111111111111111111", // WHY: Use a whitelisted address so the mock data is internally consistent with tier rules.
  amount: 2000, // WHY: Contribute the tier maximum to demonstrate allocation boundary behavior.
  tierId: "tier-1", // WHY: Reference the Early Adopters tier to show the lowest-price participation path.
  tokensAllocated: 5000, // WHY: Compute 2000 / 0.4 = 5000 tokens to demonstrate the price-to-allocation formula.
  claimed: false, // WHY: Leave tokens unclaimed so the claim endpoint has meaningful state to transition.
  refunded: false, // WHY: Leave refund unclaimed so the refund endpoint has meaningful state to transition.
  timestamp: Math.floor(Date.now() / 1000), // WHY: Record the current time so vesting or chronological logic can reference it.
}; // WHY: Close the mock participation object.

participations.get(mockProject.id)!.push(mockParticipation); // WHY: Append the mock participation to the project's array so user allocation queries return results.

mockProject.raised += mockParticipation.amount; // WHY: Update the project's raised total to reflect the seeded contribution for accurate cap reporting.

app.get("/health", (_req: Request, res: Response) => { // WHY: Health check endpoint so load balancers and operators can verify the service is alive.
  res.json({ // WHY: Return current system status and counts for monitoring dashboards.
    status: "healthy", // WHY: Signal that the API process is running and responsive.
    projectCount: projects.size, // WHY: Report how many projects are registered so operators can verify data load.
    totalParticipations: Array.from(participations.values()).reduce((sum, arr) => sum + arr.length, 0), // WHY: Sum all participations across every project to show total activity.
  }); // WHY: Close the response payload.
}); // WHY: Close the health check route handler.

app.post("/project/register", (req: Request, res: Response) => { // WHY: Endpoint for project teams to register a new token sale with caps, timeline, and token details.
  const { name, tokenMint, totalTokens, hardCap, softCap, startTime, endTime, creator } = req.body; // WHY: Destructure required parameters from the request body.

  if (!name || !tokenMint || totalTokens === undefined || hardCap === undefined || softCap === undefined || !startTime || !endTime || !creator) { // WHY: Validate that all required fields are present to prevent malformed project registrations.
    return res.status(400).json({ error: "name, tokenMint, totalTokens, hardCap, softCap, startTime, endTime, and creator are required" }); // WHY: Return a clear error so the caller knows which fields are missing.
  } // WHY: Close the validation block.

  if (softCap > hardCap) { // WHY: Reject impossible configurations where the minimum goal exceeds the maximum goal.
    return res.status(400).json({ error: "softCap cannot exceed hardCap" }); // WHY: Return an error so the caller can fix the cap relationship.
  } // WHY: Close the softCap validation block.

  if (endTime <= startTime) { // WHY: Reject sales where the end time is not strictly after the start time.
    return res.status(400).json({ error: "endTime must be greater than startTime" }); // WHY: Return an error so the caller can fix the timeline.
  } // WHY: Close the timeline validation block.

  const project: Project = { // WHY: Build the new Project object with all provided details.
    id: String(nextProjectId++), // WHY: Increment the global ID counter so every project is unique.
    name: String(name), // WHY: Cast to string to ensure type safety regardless of input type.
    tokenMint: String(tokenMint), // WHY: Cast to string to preserve the mint address format.
    totalTokens: Number(totalTokens), // WHY: Cast to number so downstream math operates on numeric values.
    hardCap: Number(hardCap), // WHY: Cast to number so cap comparisons work correctly.
    softCap: Number(softCap), // WHY: Cast to number so soft cap checks work correctly.
    raised: 0, // WHY: Initialize raised amount to zero because no contributions exist at registration time.
    startTime: Number(startTime), // WHY: Cast to number so time comparisons work correctly.
    endTime: Number(endTime), // WHY: Cast to number so time comparisons work correctly.
    status: Number(startTime) > Math.floor(Date.now() / 1000) ? "upcoming" : "active", // WHY: Derive initial status from the current time so projects scheduled for the future are labeled correctly.
    creator: String(creator), // WHY: Cast to string to preserve the wallet address format.
    tiers: [], // WHY: Initialize tiers as empty because tiers are configured in a separate step after registration.
  }; // WHY: Close the project object.

  projects.set(project.id, project); // WHY: Store the new project in the in-memory map keyed by its unique ID.

  participations.set(project.id, []); // WHY: Initialize an empty participation array for the new project so contribution logic can append safely.

  res.status(201).json({ success: true, project }); // WHY: Return the full project object so the caller knows their registration has been accepted.
}); // WHY: Close the project registration route handler.

app.post("/project/tiers", (req: Request, res: Response) => { // WHY: Endpoint for project teams to configure participation tiers after registering a project.
  const { projectId, tiers } = req.body; // WHY: Destructure required parameters from the request body.

  if (!projectId || !Array.isArray(tiers) || tiers.length === 0) { // WHY: Validate that a project ID and a non-empty tiers array are provided.
    return res.status(400).json({ error: "projectId and a non-empty tiers array are required" }); // WHY: Return a clear error so the caller knows what is missing.
  } // WHY: Close the validation block.

  const project = projects.get(projectId); // WHY: Look up the target project to ensure it exists before modifying its tiers.

  if (!project) { // WHY: Return 404 if the project does not exist because you cannot configure tiers for a missing sale.
    return res.status(404).json({ error: "Project not found" }); // WHY: Return an error so the caller knows the project ID is invalid.
  } // WHY: Close the not-found block.

  if (project.status !== "upcoming" && project.status !== "active") { // WHY: Reject tier changes for finished or failed projects because sale rules must be immutable after conclusion.
    return res.status(400).json({ error: "Cannot modify tiers for a project that is not upcoming or active" }); // WHY: Return an error so the caller knows the project lifecycle state prohibits changes.
  } // WHY: Close the status validation block.

  const reservedTotal = tiers.reduce((sum: number, t: any) => sum + (Number(t.tokensReserved) || 0), 0); // WHY: Sum all tier token reservations to verify they do not exceed the project's total supply.

  if (reservedTotal > project.totalTokens) { // WHY: Reject tier configurations that promise more tokens than the project has available.
    return res.status(400).json({ error: `Tier tokens reserved (${reservedTotal}) exceed project totalTokens (${project.totalTokens})` }); // WHY: Return an error so the caller can adjust tier allocations.
  } // WHY: Close the supply validation block.

  const validatedTiers: Tier[] = tiers.map((t: any, idx: number) => ({ // WHY: Map over the incoming tiers to sanitize and assign stable IDs.
    id: t.id || `tier-${idx + 1}`, // WHY: Use a provided ID or generate a sequential default so every tier has a referenceable key.
    name: String(t.name), // WHY: Cast to string to ensure type safety.
    price: Number(t.price), // WHY: Cast to number so price math works correctly.
    maxAllocation: Number(t.maxAllocation), // WHY: Cast to number so allocation limit checks work correctly.
    tokensReserved: Number(t.tokensReserved), // WHY: Cast to number so supply tracking works correctly.
    whitelist: Array.isArray(t.whitelist) ? t.whitelist.map(String) : [], // WHY: Normalize whitelist to an array of strings so tier authorization checks do not crash.
  })); // WHY: Close the tier mapping.

  project.tiers = validatedTiers; // WHY: Overwrite the project's tiers with the validated configuration.

  res.status(200).json({ success: true, project }); // WHY: Return the updated project so the caller can confirm tier configuration.
}); // WHY: Close the tier configuration route handler.

app.post("/participate", (req: Request, res: Response) => { // WHY: Endpoint for users to contribute payment tokens to an active sale.
  const { projectId, user, amount, tierId } = req.body; // WHY: Destructure required parameters from the request body.

  if (!projectId || !user || amount === undefined || !tierId) { // WHY: Validate that all required fields are present to prevent malformed contributions.
    return res.status(400).json({ error: "projectId, user, amount, and tierId are required" }); // WHY: Return a clear error so the caller knows which fields are missing.
  } // WHY: Close the validation block.

  const project = projects.get(projectId); // WHY: Look up the target project to ensure it exists and is active.

  if (!project) { // WHY: Return 404 if the project does not exist because you cannot participate in a missing sale.
    return res.status(404).json({ error: "Project not found" }); // WHY: Return an error so the caller knows the project ID is invalid.
  } // WHY: Close the not-found block.

  if (project.status !== "active") { // WHY: Reject contributions for projects that are not currently active to enforce the sale timeline.
    return res.status(400).json({ error: "Project is not active" }); // WHY: Return an error so the caller knows the sale is closed or not yet open.
  } // WHY: Close the status validation block.

  const now = Math.floor(Date.now() / 1000); // WHY: Capture the current Unix timestamp to validate the sale window.

  if (now < project.startTime || now > project.endTime) { // WHY: Reject contributions outside the declared sale window even if the status has not been updated yet.
    return res.status(400).json({ error: "Sale is not open at this time" }); // WHY: Return an error so the caller knows the timeline restriction.
  } // WHY: Close the time validation block.

  const tier = project.tiers.find((t) => t.id === tierId); // WHY: Find the requested tier so the contract can enforce pricing and whitelist rules.

  if (!tier) { // WHY: Return 404 if the tier does not exist because pricing and limits are undefined.
    return res.status(404).json({ error: "Tier not found" }); // WHY: Return an error so the caller knows the tier ID is invalid.
  } // WHY: Close the tier not-found block.

  if (tier.whitelist.length > 0 && !tier.whitelist.includes(user)) { // WHY: Reject users who are not on the tier whitelist when a whitelist is configured.
    return res.status(403).json({ error: "User is not whitelisted for this tier" }); // WHY: Return an error so the caller knows they need tier authorization.
  } // WHY: Close the whitelist validation block.

  const numericAmount = Number(amount); // WHY: Cast to number so all subsequent math is numeric.

  if (numericAmount <= 0) { // WHY: Reject non-positive contributions because zero or negative payments are meaningless.
    return res.status(400).json({ error: "amount must be positive" }); // WHY: Return an error so the caller knows the amount is invalid.
  } // WHY: Close the amount validation block.

  if (numericAmount > tier.maxAllocation) { // WHY: Reject contributions that exceed the per-user allocation limit for this tier.
    return res.status(400).json({ error: `amount exceeds tier maxAllocation of ${tier.maxAllocation}` }); // WHY: Return an error so the caller knows the tier limit.
  } // WHY: Close the max allocation validation block.

  const projectParts = participations.get(project.id) || []; // WHY: Retrieve existing participations for this project to enforce cumulative limits.

  const userTierTotal = projectParts // WHY: Calculate the user's prior contributions in this tier so we can enforce the cumulative maxAllocation.
    .filter((p) => p.user === user && p.tierId === tierId && !p.refunded) // WHY: Only count non-refunded contributions for this user in this tier.
    .reduce((sum, p) => sum + p.amount, 0); // WHY: Sum the amounts to compute the total prior spend.

  if (userTierTotal + numericAmount > tier.maxAllocation) { // WHY: Reject contributions that would push the user over the tier's cumulative maxAllocation.
    return res.status(400).json({ error: `Cumulative amount would exceed tier maxAllocation of ${tier.maxAllocation}` }); // WHY: Return an error so the caller knows their cumulative limit.
  } // WHY: Close the cumulative limit validation block.

  if (project.raised + numericAmount > project.hardCap) { // WHY: Reject contributions that would push the project over its hard cap.
    return res.status(400).json({ error: `Contribution would exceed hard cap of ${project.hardCap}` }); // WHY: Return an error so the caller knows the sale is nearly sold out.
  } // WHY: Close the hard cap validation block.

  const tokensAllocated = Math.floor(numericAmount / tier.price); // WHY: Compute the token allocation by dividing contribution amount by tier price, flooring to whole tokens.

  const participation: Participation = { // WHY: Build the new Participation record with all computed and provided fields.
    id: String(nextParticipationId++), // WHY: Increment the global ID counter so every participation record is unique.
    projectId: project.id, // WHY: Link the participation to the project for lookups and accounting.
    user: String(user), // WHY: Cast to string to preserve the wallet address format.
    amount: numericAmount, // WHY: Store the numeric amount for refund and reporting calculations.
    tierId: String(tierId), // WHY: Cast to string to preserve the tier reference.
    tokensAllocated, // WHY: Store the computed token amount so claim logic knows the entitlement.
    claimed: false, // WHY: Initialize claimed to false because the user has not yet claimed their tokens.
    refunded: false, // WHY: Initialize refunded to false because the user has not requested a refund.
    timestamp: now, // WHY: Record the contribution time for chronological ordering and vesting calculations.
  }; // WHY: Close the participation object.

  projectParts.push(participation); // WHY: Append the new participation to the project's array so future lookups include it.

  participations.set(project.id, projectParts); // WHY: Store the updated participation array back in the in-memory map.

  project.raised += numericAmount; // WHY: Increment the project's raised total so cap progress is accurate.

  if (project.raised >= project.hardCap) { // WHY: Automatically mark the project as successful when the hard cap is reached.
    project.status = "success"; // WHY: Transition status to success so no further contributions are accepted.
  } // WHY: Close the hard cap success block.

  res.status(201).json({ success: true, participation, projectRaised: project.raised }); // WHY: Return the participation record and updated raised total so the caller knows their contribution was accepted.
}); // WHY: Close the participation route handler.

app.post("/claim", (req: Request, res: Response) => { // WHY: Endpoint for participants to claim their purchased tokens after a successful sale.
  const { projectId, user } = req.body; // WHY: Destructure required parameters from the request body.

  if (!projectId || !user) { // WHY: Validate that both projectId and user are provided to locate the correct participation records.
    return res.status(400).json({ error: "projectId and user are required" }); // WHY: Return a clear error so the caller knows which fields are missing.
  } // WHY: Close the validation block.

  const project = projects.get(projectId); // WHY: Look up the target project to ensure it exists.

  if (!project) { // WHY: Return 404 if the project does not exist because you cannot claim from a missing sale.
    return res.status(404).json({ error: "Project not found" }); // WHY: Return an error so the caller knows the project ID is invalid.
  } // WHY: Close the not-found block.

  if (project.status !== "success") { // WHY: Reject claims for projects that have not reached success status because tokens are only released on success.
    return res.status(400).json({ error: "Tokens can only be claimed for successful sales" }); // WHY: Return an error so the caller knows the sale outcome.
  } // WHY: Close the status validation block.

  const projectParts = participations.get(project.id) || []; // WHY: Retrieve all participations for this project to find the user's records.

  const userParts = projectParts.filter((p) => p.user === user && !p.claimed && !p.refunded); // WHY: Select only unclaimed and non-refunded records for this user so we do not double-claim.

  if (userParts.length === 0) { // WHY: Return 404 if there are no eligible records because the user has nothing to claim.
    return res.status(404).json({ error: "No unclaimed allocations found for this user" }); // WHY: Return an error so the caller knows their claim status.
  } // WHY: Close the empty allocations block.

  let totalClaimed = 0; // WHY: Initialize a running total so we can report how many tokens were claimed in this request.

  for (const p of userParts) { // WHY: Iterate over every eligible participation record to mark them as claimed.
    p.claimed = true; // WHY: Set claimed to true so future requests cannot claim the same tokens again.
    totalClaimed += p.tokensAllocated; // WHY: Accumulate the token amount for the response summary.
  } // WHY: Close the participation loop.

  res.json({ success: true, totalClaimed, claimedParts: userParts.length }); // WHY: Return the total tokens claimed and count of records updated so the caller knows the outcome.
}); // WHY: Close the claim route handler.

app.post("/refund", (req: Request, res: Response) => { // WHY: Endpoint for participants to reclaim their contributions if the sale failed to meet its soft cap.
  const { projectId, user } = req.body; // WHY: Destructure required parameters from the request body.

  if (!projectId || !user) { // WHY: Validate that both projectId and user are provided to locate the correct participation records.
    return res.status(400).json({ error: "projectId and user are required" }); // WHY: Return a clear error so the caller knows which fields are missing.
  } // WHY: Close the validation block.

  const project = projects.get(projectId); // WHY: Look up the target project to ensure it exists.

  if (!project) { // WHY: Return 404 if the project does not exist because you cannot refund from a missing sale.
    return res.status(404).json({ error: "Project not found" }); // WHY: Return an error so the caller knows the project ID is invalid.
  } // WHY: Close the not-found block.

  const now = Math.floor(Date.now() / 1000); // WHY: Capture the current Unix timestamp to evaluate sale deadline and outcome.

  const saleEnded = now > project.endTime || project.status === "success" || project.status === "failed"; // WHY: Determine whether the sale period is over or the outcome has already been decided.

  if (!saleEnded) { // WHY: Reject refunds while the sale is still open because participants must wait for the conclusion.
    return res.status(400).json({ error: "Sale is still active; refunds are only available after the sale ends" }); // WHY: Return an error so the caller knows to wait.
  } // WHY: Close the active sale block.

  const softCapMet = project.raised >= project.softCap; // WHY: Compute whether the minimum funding goal was achieved to determine refund eligibility.

  if (softCapMet && project.status !== "failed") { // WHY: Reject refunds for successful sales because funds are transferred to the project team and tokens are distributed.
    return res.status(400).json({ error: "Soft cap was met; refunds are not available for successful sales" }); // WHY: Return an error so the caller knows the sale succeeded.
  } // WHY: Close the soft cap validation block.

  if (project.status === "active" || project.status === "upcoming") { // WHY: Automatically transition the project status to failed if the deadline passed without meeting the soft cap.
    project.status = "failed"; // WHY: Update status so the API consistently reports the correct outcome and prevents further participation.
  } // WHY: Close the auto-fail block.

  const projectParts = participations.get(project.id) || []; // WHY: Retrieve all participations for this project to find the user's records.

  const userParts = projectParts.filter((p) => p.user === user && !p.refunded && !p.claimed); // WHY: Select only unrefunded and unclaimed records for this user so we do not double-refund.

  if (userParts.length === 0) { // WHY: Return 404 if there are no eligible records because the user has nothing to refund.
    return res.status(404).json({ error: "No refundable allocations found for this user" }); // WHY: Return an error so the caller knows their refund status.
  } // WHY: Close the empty allocations block.

  let totalRefunded = 0; // WHY: Initialize a running total so we can report how much was refunded in this request.

  for (const p of userParts) { // WHY: Iterate over every eligible participation record to mark them as refunded.
    p.refunded = true; // WHY: Set refunded to true so future requests cannot refund the same contribution again.
    totalRefunded += p.amount; // WHY: Accumulate the payment amount for the response summary.
  } // WHY: Close the participation loop.

  project.raised -= totalRefunded; // WHY: Decrease the project's raised total by the refunded amount so accounting remains accurate.

  res.json({ success: true, totalRefunded, refundedParts: userParts.length }); // WHY: Return the total amount refunded and count of records updated so the caller knows the outcome.
}); // WHY: Close the refund route handler.

app.get("/projects", (_req: Request, res: Response) => { // WHY: Endpoint to list all registered projects so users can discover available token sales.
  const allProjects = Array.from(projects.values()); // WHY: Convert the projects map values to an array so the response is a JSON list.

  res.json({ success: true, count: allProjects.length, projects: allProjects }); // WHY: Return the full project list with a count so frontends can render discovery pages.
}); // WHY: Close the projects list route handler.

app.get("/project/:id", (req: Request, res: Response) => { // WHY: Endpoint to fetch a single project by ID so users can view sale details and tier configuration.
  const project = projects.get(req.params.id); // WHY: Look up the project in the active projects map using the URL parameter.

  if (!project) { // WHY: Return 404 if the project does not exist because the ID may be mistyped or the sale removed.
    return res.status(404).json({ error: "Project not found" }); // WHY: Return an error so the caller knows the project ID is invalid.
  } // WHY: Close the not-found block.

  const projectParts = participations.get(project.id) || []; // WHY: Retrieve all participations for this project so the response can include aggregate stats.

  const participantCount = new Set(projectParts.map((p) => p.user)).size; // WHY: Count unique participant addresses so the response shows how many distinct users have joined.

  res.json({ // WHY: Return the project details enriched with participation statistics so callers get a complete snapshot.
    success: true, // WHY: Signal that the lookup succeeded.
    project, // WHY: Include the full project object with tiers and caps.
    participantCount, // WHY: Include the unique participant count for social proof and analytics.
    totalParticipations: projectParts.length, // WHY: Include the total number of contribution records for auditability.
  }); // WHY: Close the response payload.
}); // WHY: Close the single project route handler.

app.get("/user/:address/allocations", (req: Request, res: Response) => { // WHY: Endpoint to list all allocations for a specific wallet address across every project.
  const address = req.params.address; // WHY: Capture the wallet address from the URL parameter so we can filter participation records.

  if (!address) { // WHY: Validate that the address parameter is present to prevent empty lookups.
    return res.status(400).json({ error: "address is required" }); // WHY: Return an error so the caller knows the parameter is missing.
  } // WHY: Close the validation block.

  const userAllocations: { projectId: string; projectName: string; tierId: string; amount: number; tokensAllocated: number; claimed: boolean; refunded: boolean }[] = []; // WHY: Initialize an array to collect every allocation for this user across all projects.

  for (const [projectId, parts] of participations.entries()) { // WHY: Iterate over every project's participation array to find records belonging to this user.
    const project = projects.get(projectId); // WHY: Look up the project metadata so the response can include the human-readable project name.

    if (!project) continue; // WHY: Skip orphaned participation records if the associated project is missing.

    for (const p of parts) { // WHY: Iterate over every participation record in this project to check ownership.
      if (p.user === address) { // WHY: Only include records where the participant matches the requested address.
        userAllocations.push({ // WHY: Push a slim allocation object so the response does not leak internal IDs unnecessarily.
          projectId: project.id, // WHY: Include the project ID so the caller can link allocations to project details.
          projectName: project.name, // WHY: Include the project name for human-readable display in wallets and dashboards.
          tierId: p.tierId, // WHY: Include the tier ID so the caller knows which pricing level applied.
          amount: p.amount, // WHY: Include the contribution amount for accounting and tax reporting.
          tokensAllocated: p.tokensAllocated, // WHY: Include the token entitlement so the user knows their claimable balance.
          claimed: p.claimed, // WHY: Include the claimed flag so the user knows which allocations have been withdrawn.
          refunded: p.refunded, // WHY: Include the refunded flag so the user knows which allocations were returned.
        }); // WHY: Close the allocation push.
      } // WHY: Close the address match block.
    } // WHY: Close the participation loop.
  } // WHY: Close the project loop.

  res.json({ // WHY: Return the aggregated allocations so wallets and portfolio trackers can display the user's launchpad history.
    success: true, // WHY: Signal that the lookup succeeded.
    address, // WHY: Echo the requested address so the caller can verify the query target.
    count: userAllocations.length, // WHY: Report how many allocations exist so UIs can show summary stats.
    allocations: userAllocations, // WHY: Include the full list so the caller can render detailed tables.
  }); // WHY: Close the response payload.
}); // WHY: Close the user allocations route handler.

app.listen(PORT, () => { // WHY: Start the Express server on the designated port and log readiness.
  console.log(`Token Launchpad API listening on port ${PORT}`); // WHY: Log startup so operators know the service is ready.
}); // WHY: Close the listen callback.
