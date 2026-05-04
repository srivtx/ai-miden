import express, { Request, Response } from "express"; // Import Express to build the HTTP API for DePIN node registration, proof-of-location, storage, and reward distribution

const app = express(); // Initialize the Express application instance for the DePIN service

app.use(express.json()); // Enable JSON body parsing so clients can send node metadata, location proofs, and storage parameters

const PORT = 3054; // Use port 3054 to avoid conflicts with other Web3 phase APIs running in the project

interface DePINNode { // Define the DePINNode interface so TypeScript can enforce the shape of every infrastructure node
  id: string; // Unique identifier for referencing and tracking a specific node
  owner: string; // Wallet address or identifier of the node operator
  nodeType: "beacon" | "storage" | "compute"; // Category of service the node provides
  location: { x: number; y: number } | null; // Geographic coordinates for beacon nodes, null for others
  capacityGb: number; // Total storage or compute capacity offered by the node
  usedGb: number; // Currently utilized capacity to track availability
  uptimePercent: number; // Historical uptime metric used for reward calculations
  rewards: number; // Accumulated token earnings from providing services
  status: "active" | "offline"; // Lifecycle state indicating whether the node is currently participating
} // Close the block

interface LocationProof { // Define the LocationProof interface so TypeScript can enforce the shape of every proof-of-location attestation
  id: string; // Unique identifier for the location proof
  deviceId: string; // Identifier of the device claiming the location
  x: number; // Claimed x coordinate
  y: number; // Claimed y coordinate
  timestamp: number; // Unix timestamp when the location was claimed
  witnesses: string[]; // List of beacon node IDs that corroborated the claim
  verified: boolean; // Flag indicating whether the proof passed network verification
} // Close the block

interface StorageDeal { // Define the StorageDeal interface so TypeScript can enforce the shape of every file storage agreement
  id: string; // Unique identifier for the storage deal
  owner: string; // Wallet address of the user storing the file
  sizeGb: number; // Size of the file in gigabytes
  replicas: number; // Number of redundant copies required across nodes
  pricePerMonth: number; // Monthly fee paid by the owner for storage
  nodeAssignments: string[]; // List of node IDs currently storing replicas
  createdAt: number; // Unix timestamp when the deal was created
} // Close the block

const nodes: Map<string, DePINNode> = new Map(); // In-memory storage for DePIN nodes keyed by node ID

const locationProofs: Map<string, LocationProof> = new Map(); // In-memory storage for location proofs keyed by proof ID

const storageDeals: Map<string, StorageDeal> = new Map(); // In-memory storage for storage deals keyed by deal ID

let nextNodeId = 1; // Sequence counter to generate unique node IDs without an external database

let nextProofId = 1; // Sequence counter to generate unique location proof IDs without an external database

let nextDealId = 1; // Sequence counter to generate unique storage deal IDs without an external database

app.get("/health", (_req: Request, res: Response) => { // Health check endpoint so load balancers and operators can verify the service is alive
  const activeNodes = Array.from(nodes.values()).filter((n) => n.status === "active"); // Return current system status, node counts, and aggregate capacity for monitoring dashboards
  const totalCapacity = activeNodes.reduce((sum, n) => sum + n.capacityGb, 0); // Declare and initialize the variable
  const totalUsed = activeNodes.reduce((sum, n) => sum + n.usedGb, 0); // Declare and initialize the variable
  res.json({ // Send the JSON response to the client
    status: "healthy", // Signal that the API process is running and responsive
    totalNodes: nodes.size, // Report how many nodes have been registered
    activeNodes: activeNodes.length, // Report how many nodes are currently online
    totalCapacityGb: totalCapacity, // Report aggregate infrastructure capacity
    totalUsedGb: totalUsed, // Report aggregate utilization
    locationProofs: locationProofs.size, // Report how many location proofs have been generated
    storageDeals: storageDeals.size, // Report how many storage deals are active
  }); // Close the route handler
}); // Close the route handler

app.post("/node/register", (req: Request, res: Response) => { // Endpoint to register a new DePIN node so operators can join the network
  const { owner, nodeType, location, capacityGb } = req.body; // Destructure required parameters from the request body

  if (!owner || !nodeType || capacityGb === undefined) { // Validate that all required fields are present to prevent malformed node registrations
    return res.status(400).json({ error: "owner, nodeType, and capacityGb are required" }); // Return result to the caller
  } // Close the block

  if (nodeType !== "beacon" && nodeType !== "storage" && nodeType !== "compute") { // Validate that nodeType is one of the supported service categories
    return res.status(400).json({ error: "nodeType must be beacon, storage, or compute" }); // Return result to the caller
  } // Close the block

  if (nodeType === "beacon" && (!location || location.x === undefined || location.y === undefined)) { // Validate that beacon nodes include location coordinates because beacons are geographically anchored
    return res.status(400).json({ error: "beacon nodes require location coordinates" }); // Return result to the caller
  } // Close the block

  if (Number(capacityGb) <= 0) { // Validate that capacity is positive because a node must offer some resources to be useful
    return res.status(400).json({ error: "capacityGb must be positive" }); // Return result to the caller
  } // Close the block

  const node: DePINNode = { // Build the new DePINNode object with initial zero utilization and active status
    id: String(nextNodeId++), // Increment global ID counter so every node is unique
    owner, // Execute the statement
    nodeType, // Execute the statement
    location: nodeType === "beacon" ? { x: Number(location.x), y: Number(location.y) } : null, // Set the property value
    capacityGb: Number(capacityGb), // Set the property value
    usedGb: 0, // Initialize used capacity to zero because the node has not accepted any work yet
    uptimePercent: 100, // Initialize uptime to perfect because the node just registered
    rewards: 0, // Initialize rewards to zero because the node has not earned anything yet
    status: "active", // Set status to active so the node immediately appears in network queries
  }; // Execute the statement

  nodes.set(node.id, node); // Store the new node in the in-memory map keyed by its unique ID

  res.status(201).json({ success: true, node }); // Return the full node object so the operator knows their registration succeeded
}); // Close the route handler

app.get("/node/:id", (req: Request, res: Response) => { // Endpoint to fetch a single node by ID so operators can check their status and earnings
  const node = nodes.get(req.params.id); // Look up the node in the registered nodes map using the URL parameter

  if (!node) { // Return 404 if the node does not exist or has not been registered
    return res.status(404).json({ error: "Node not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, node }); // Return the node state so the operator can view capacity, utilization, uptime, and rewards
}); // Close the route handler

app.get("/nodes/active", (_req: Request, res: Response) => { // Endpoint to list all active nodes so users and protocols can discover available infrastructure
  const activeNodes = Array.from(nodes.values()).filter((n) => n.status === "active"); // Filter the nodes map to find only nodes with active status

  res.json({ success: true, count: activeNodes.length, nodes: activeNodes }); // Return the filtered list so frontends can display available capacity and coverage
}); // Close the route handler

app.post("/location/prove", (req: Request, res: Response) => { // Endpoint to submit a proof-of-location claim corroborated by nearby beacon nodes
  const { deviceId, x, y, witnesses } = req.body; // Destructure required parameters from the request body

  if (!deviceId || x === undefined || y === undefined || !Array.isArray(witnesses)) { // Validate that all required fields are present to prevent malformed location proofs
    return res.status(400).json({ error: "deviceId, x, y, and witnesses array are required" }); // Return result to the caller
  } // Close the block

  const validWitnesses: string[] = []; // Verify that every witness node exists and is a beacon because only beacons can attest to location
  for (const witnessId of witnesses) { // Iterate over the collection
    const witness = nodes.get(witnessId); // Declare and initialize the variable
    if (witness && witness.nodeType === "beacon" && witness.status === "active") { // Check the condition before proceeding
      validWitnesses.push(witnessId); // Include only active beacon nodes in the valid witness list
    } // Close the block
  } // Close the block

  if (validWitnesses.length < 2) { // Reject the proof if there are fewer than two valid witnesses because a single witness is insufficient for triangulation
    return res.status(400).json({ error: "At least 2 active beacon witnesses are required" }); // Return result to the caller
  } // Close the block

  let consistencyScore = 0; // Simulate distance consistency check by comparing claimed coordinates to witness coordinates
  for (const witnessId of validWitnesses) { // Iterate over the collection
    const witness = nodes.get(witnessId); // Declare and initialize the variable
    if (witness && witness.location) { // Check the condition before proceeding
      const distance = Math.sqrt(Math.pow(Number(x) - witness.location.x, 2) + Math.pow(Number(y) - witness.location.y, 2)); // Calculate Euclidean distance between claimed location and witness location
      if (distance <= 500) { // Assume a reasonable signal range of 500 meters for beacon coverage
        consistencyScore += 1; // Increment score if the claimed location is within plausible range
      } // Close the block
    } // Close the block
  } // Close the block

  const verified = consistencyScore >= validWitnesses.length / 2; // Determine verification result based on whether most witnesses corroborate the claim

  const proof: LocationProof = { // Build the new LocationProof object to record the attestation
    id: String(nextProofId++), // Increment global ID counter so every proof is unique
    deviceId, // Execute the statement
    x: Number(x), // Set the property value
    y: Number(y), // Set the property value
    timestamp: Date.now(), // Record current time to prevent replay of old proofs
    witnesses: validWitnesses, // Set the property value
    verified, // Execute the statement
  }; // Execute the statement

  locationProofs.set(proof.id, proof); // Store the proof in the in-memory map keyed by its unique ID

  res.status(201).json({ success: true, proof }); // Return the proof so the device knows whether its location claim was accepted
}); // Close the route handler

app.get("/location/:id", (req: Request, res: Response) => { // Endpoint to fetch a single location proof by ID so verifiers can inspect witness details
  const proof = locationProofs.get(req.params.id); // Look up the proof in the generated proofs map using the URL parameter

  if (!proof) { // Return 404 if the proof does not exist or has not been generated
    return res.status(404).json({ error: "Location proof not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, proof }); // Return the proof so the verifier can check coordinates, witnesses, and verification status
}); // Close the route handler

app.post("/storage/deal", (req: Request, res: Response) => { // Endpoint to create a new decentralized storage deal so users can store files across the network
  const { owner, sizeGb, replicas, pricePerMonth } = req.body; // Destructure required parameters from the request body

  if (!owner || sizeGb === undefined || replicas === undefined || pricePerMonth === undefined) { // Validate that all required fields are present to prevent malformed storage deals
    return res.status(400).json({ error: "owner, sizeGb, replicas, and pricePerMonth are required" }); // Return result to the caller
  } // Close the block

  if (Number(replicas) <= 0) { // Validate that requested replicas is positive because zero replicas means no redundancy
    return res.status(400).json({ error: "replicas must be positive" }); // Return result to the caller
  } // Close the block

  if (Number(sizeGb) <= 0) { // Validate that file size is positive because zero or negative files are meaningless
    return res.status(400).json({ error: "sizeGb must be positive" }); // Return result to the caller
  } // Close the block

  const availableNodes = Array.from(nodes.values()).filter( // Find active storage nodes that have enough free capacity to accept a replica
    (n) => n.nodeType === "storage" && n.status === "active" && n.capacityGb - n.usedGb >= Number(sizeGb) // Cast the value to a number
  ); // Close the call

  if (availableNodes.length < Number(replicas)) { // Reject the deal if there are not enough available nodes to satisfy the replica requirement
    return res.status(400).json({ error: `Only ${availableNodes.length} storage nodes available. ${replicas} replicas requested.` }); // Return result to the caller
  } // Close the block

  const selectedNodes = availableNodes.sort(() => Math.random() - 0.5).slice(0, Number(replicas)); // Randomly shuffle available nodes and select the first N to distribute replicas unpredictably

  for (const node of selectedNodes) { // Update selected nodes' used capacity to reflect the new storage obligation
    node.usedGb += Number(sizeGb); // Increase used capacity because the node now stores a replica
  } // Close the block

  const deal: StorageDeal = { // Build the new StorageDeal object to record the agreement
    id: String(nextDealId++), // Increment global ID counter so every deal is unique
    owner, // Execute the statement
    sizeGb: Number(sizeGb), // Set the property value
    replicas: Number(replicas), // Set the property value
    pricePerMonth: Number(pricePerMonth), // Set the property value
    nodeAssignments: selectedNodes.map((n) => n.id), // Record which nodes are responsible for replicas
    createdAt: Date.now(), // Set the property value
  }; // Execute the statement

  storageDeals.set(deal.id, deal); // Store the deal in the in-memory map keyed by its unique ID

  res.status(201).json({ success: true, deal }); // Return the deal details so the owner knows where their file replicas are stored
}); // Close the route handler

app.get("/storage/:id", (req: Request, res: Response) => { // Endpoint to fetch a single storage deal by ID so users can check replica placement
  const deal = storageDeals.get(req.params.id); // Look up the deal in the active deals map using the URL parameter

  if (!deal) { // Return 404 if the deal does not exist or has not been created
    return res.status(404).json({ error: "Storage deal not found" }); // Return result to the caller
  } // Close the block

  res.json({ success: true, deal }); // Return the deal so the user can view size, replicas, price, and node assignments
}); // Close the route handler

app.post("/rewards/distribute", (req: Request, res: Response) => { // Endpoint to distribute rewards to nodes based on uptime and contributed capacity
  const { totalRewards } = req.body; // Destructure the total reward pool from the request body

  if (totalRewards === undefined || Number(totalRewards) <= 0) { // Validate that totalRewards is provided and positive because zero or negative rewards are meaningless
    return res.status(400).json({ error: "totalRewards must be a positive number" }); // Return result to the caller
  } // Close the block

  let totalWeight = 0; // Calculate total weighted contribution across all active nodes to determine reward share proportions
  const activeNodes = Array.from(nodes.values()).filter((n) => n.status === "active"); // Declare and initialize the variable
  for (const node of activeNodes) { // Iterate over the collection
    totalWeight += node.usedGb * (node.uptimePercent / 100); // Weight each node by its used capacity multiplied by its uptime percentage to reward useful and reliable nodes
  } // Close the block

  const allocations: { nodeId: string; owner: string; reward: number }[] = []; // Array to collect per-node reward allocations for the response

  for (const node of activeNodes) { // Iterate over every active node to compute and assign its proportional reward
    const weight = node.usedGb * (node.uptimePercent / 100); // Declare and initialize the variable
    const reward = totalWeight > 0 ? (weight / totalWeight) * Number(totalRewards) : 0; // Avoid division by zero if total weight is zero because all nodes might have zero used capacity
    node.rewards += reward; // Add the computed reward to the node's accumulated balance
    allocations.push({ nodeId: node.id, owner: node.owner, reward }); // Execute the statement
  } // Close the block

  res.json({ success: true, totalRewards: Number(totalRewards), totalWeight, allocations }); // Return the allocation summary so operators can audit how rewards were distributed
}); // Close the route handler

app.post("/node/status", (req: Request, res: Response) => { // Endpoint to update node status so operators can mark nodes offline for maintenance
  const { nodeId, status } = req.body; // Destructure required parameters from the request body

  if (!nodeId || !status) { // Validate that all required fields are present to prevent malformed status updates
    return res.status(400).json({ error: "nodeId and status are required" }); // Return result to the caller
  } // Close the block

  if (status !== "active" && status !== "offline") { // Validate that status is either active or offline because those are the only supported states
    return res.status(400).json({ error: "status must be active or offline" }); // Return result to the caller
  } // Close the block

  const node = nodes.get(nodeId); // Look up the target node to ensure it exists
  if (!node) { // Validate that the required condition is met
    return res.status(404).json({ error: "Node not found" }); // Return result to the caller
  } // Close the block

  node.status = status; // Update the node status to reflect the operator's reported state

  res.json({ success: true, node }); // Return the updated node so the operator knows the status change was recorded
}); // Close the route handler

app.get("/network/stats", (_req: Request, res: Response) => { // Endpoint to retrieve aggregate DePIN network statistics for dashboards
  const activeNodes = Array.from(nodes.values()).filter((n) => n.status === "active"); // Calculate total active nodes across all types to understand network size

  const totalCapacity = activeNodes.reduce((sum, n) => sum + n.capacityGb, 0); // Calculate total network capacity to understand infrastructure scale

  const totalUsed = activeNodes.reduce((sum, n) => sum + n.usedGb, 0); // Calculate total utilized capacity to understand demand

  const totalRewards = Array.from(nodes.values()).reduce((sum, n) => sum + n.rewards, 0); // Calculate total distributed rewards to understand incentive outflows

  res.json({ // Return network stats so dashboards can display growth, utilization, and economics
    totalNodes: nodes.size, // Set the property value
    activeNodes: activeNodes.length, // Set the property value
    totalCapacityGb: totalCapacity, // Set the property value
    totalUsedGb: totalUsed, // Set the property value
    utilizationPercent: totalCapacity > 0 ? (totalUsed / totalCapacity) * 100 : 0, // Set the property value
    totalRewardsDistributed: totalRewards, // Set the property value
    locationProofs: locationProofs.size, // Set the property value
    storageDeals: storageDeals.size, // Set the property value
  }); // Close the route handler
}); // Close the route handler

app.listen(PORT, () => { // Start the Express server on the designated port and log readiness
  console.log(`DePIN API listening on port ${PORT}`); // Log startup so operators know the service is ready
}); // Close the route handler
