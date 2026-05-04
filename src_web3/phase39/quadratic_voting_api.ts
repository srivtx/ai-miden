import express from "express"; // Import the express framework to build the HTTP server for quadratic voting operations
import cors from "cors"; // Import cors middleware to allow browser clients to interact with this API from different origins

const app = express(); // Create the express application instance that will handle quadratic voting routes
app.use(express.json()); // Attach middleware to parse incoming JSON request bodies into JavaScript objects
app.use(cors()); // Enable CORS so frontend dashboards can submit votes and view results without preflight errors

interface Proposal { // Define a TypeScript interface for an election proposal to ensure type safety across endpoints
    id: string; // Store a unique identifier for each proposal so votes can be attributed correctly
    title: string; // Store a human-readable title so voters know what they are voting on
    description: string; // Store a description so voters understand the proposal context
    totalVotes: number; // Track the cumulative votes cast for this proposal so results can be tallied
} // Close the Proposal interface definition

interface Voter { // Define a TypeScript interface for a registered voter to ensure type safety across endpoints
    address: string; // Store the wallet address so each voter is uniquely identified
    voiceCredits: number; // Store the remaining budget so overspending is prevented
    votesCast: Map<string, number>; // Track votes per proposal so duplicate voting and double counting are prevented
} // Close the Voter interface definition

const proposals: Proposal[] = []; // Initialize an in-memory array to store proposals because this is a teaching demo without a database
const voters: Map<string, Voter> = new Map(); // Initialize a Map to store registered voters because fast lookup by address is critical
const VOICE_CREDIT_BUDGET = 25; // Define a constant budget so every voter receives equal initial influence

let nextProposalId = 1; // Initialize a simple counter to generate unique proposal IDs sequentially

function nowSeconds(): number { // Define a helper to get the current time in seconds because timestamps use second-level granularity
    return Math.floor(Date.now() / 1000); // Convert millisecond timestamps to whole seconds for clean display
} // Close the nowSeconds helper

app.post("/proposals", (req, res) => { // Define an endpoint to create a new proposal for the election
    const { title, description } = req.body; // Destructure request fields so validation can be performed
    if (!title) { // Validate that the title is present because a proposal without a title is meaningless to voters
        return res.status(400).json({ error: "Missing required field: title" }); // Return 400 so the client knows what is missing
    } // Close the title validation block
    const proposal: Proposal = { // Construct a new proposal object with all fields initialized
        id: String(nextProposalId++), // Assign the next sequential ID and increment the counter so future proposals get unique identifiers
        title, // Store the title from the request so the proposal is identifiable
        description: description || "", // Store the description defaulting to an empty string so optional details are supported
        totalVotes: 0, // Initialize the vote count to zero because no votes have been cast yet
    }; // Close the proposal object creation
    proposals.push(proposal); // Append the new proposal to the in-memory array so it appears in election results
    return res.status(201).json({ // Return a 201 Created response so the client knows the proposal was successfully created
        success: true, // Include a success flag so programmatic clients can check status without deep body parsing
        proposal, // Return the full proposal so the client receives the generated ID
    }); // Close the success response
}); // Close the POST /proposals route

app.post("/register", (req, res) => { // Define an endpoint to register a voter and assign them a voice credit budget
    const { address } = req.body; // Destructure the address so the server can identify the voter
    if (!address) { // Validate that the address is provided so the server does not create anonymous voters
        return res.status(400).json({ error: "Missing required field: address" }); // Return 400 so the client sends complete input
    } // Close the address validation block
    if (voters.has(address)) { // Check if the address is already registered so duplicate budgets are not issued
        return res.status(409).json({ error: "Voter already registered" }); // Return 409 so the client knows the address is already in the system
    } // Close the duplicate check
    const voter: Voter = { // Construct a new voter object with all fields initialized
        address, // Store the address so the voter is uniquely identified
        voiceCredits: VOICE_CREDIT_BUDGET, // Assign the fixed budget so every voter starts with equal influence
        votesCast: new Map(), // Initialize an empty Map so votes per proposal are tracked individually
    }; // Close the voter object creation
    voters.set(address, voter); // Insert the voter into the Map so they can vote and be queried later
    return res.status(201).json({ // Return a 201 Created response so the client knows registration succeeded
        success: true, // Include a success flag so programmatic clients can check status
        voter: { // Return a sanitized voter object so the client sees the budget and address
            address: voter.address, // Include the address so the response is self-contained
            voiceCredits: voter.voiceCredits, // Include the budget so the voter knows their spending power
        }, // Close the sanitized voter object
    }); // Close the success response
}); // Close the POST /register route

app.post("/vote", (req, res) => { // Define an endpoint to cast votes on a proposal using quadratic cost rules
    const { address, proposalId, votes } = req.body; // Destructure request fields so validation can be performed
    if (!address || !proposalId || votes === undefined) { // Validate that every required field is present so incomplete votes are rejected
        return res.status(400).json({ error: "Missing required fields: address, proposalId, votes" }); // Return 400 with a descriptive message
    } // Close the required field validation block
    const voter = voters.get(address); // Retrieve the voter so the server can check their budget and past votes
    if (!voter) { // Ensure the voter is registered so only enrolled participants can influence the election
        return res.status(404).json({ error: "Voter not registered" }); // Return 404 so the client knows to register first
    } // Close the voter existence check
    const proposal = proposals.find((p) => p.id === proposalId); // Locate the proposal so votes are attributed to the correct initiative
    if (!proposal) { // Ensure the proposal exists so votes do not target deleted or invalid options
        return res.status(404).json({ error: "Proposal not found" }); // Return 404 so the client knows the proposal ID is invalid
    } // Close the proposal existence check
    if (votes < 0) { // Validate that the vote count is non-negative because negative votes are not supported in this implementation
        return res.status(400).json({ error: "votes must be non-negative" }); // Return 400 so the client cannot submit invalid input
    } // Close the non-negative validation block
    const previousVotes = voter.votesCast.get(proposalId) || 0; // Retrieve any prior votes on this proposal so cumulative cost can be computed
    const newTotalVotes = previousVotes + votes; // Compute the new cumulative votes so the quadratic cost reflects the updated total
    const previousCost = previousVotes * previousVotes; // Calculate the credits already spent on this proposal so the incremental cost can be derived
    const newCost = newTotalVotes * newTotalVotes; // Calculate the credits that would be spent after this vote so the total commitment is known
    const incrementalCost = newCost - previousCost; // Compute the additional credits required so the voter only pays for the marginal increase
    if (incrementalCost > voter.voiceCredits) { // Check if the voter has sufficient remaining budget so overspending is prevented
        return res.status(400).json({ // Return 400 so the client knows the vote is too expensive
            error: "Insufficient voice credits", // Explain why the vote was rejected so the voter understands the constraint
            required: incrementalCost, // Report the needed credits so the voter knows the exact shortfall
            available: voter.voiceCredits, // Report the remaining budget so the voter can adjust their strategy
        }); // Close the insufficient credits response
    } // Close the budget check
    voter.voiceCredits -= incrementalCost; // Deduct the incremental cost so the voter's budget reflects the new expenditure
    voter.votesCast.set(proposalId, newTotalVotes); // Update the voter's cumulative votes on this proposal so future costs are calculated correctly
    proposal.totalVotes += votes; // Increase the proposal's total vote count so election results stay current
    return res.status(200).json({ // Return the vote result so the voter knows their vote was recorded
        success: true, // Confirm the operation succeeded so clients can update their UI state
        votesCast: votes, // Report how many new votes were added so the voter sees their exact contribution
        totalVotesOnProposal: proposal.totalVotes, // Report the updated proposal total so the voter sees the aggregate impact
        remainingCredits: voter.voiceCredits, // Report the remaining budget so the voter can plan future votes
    }); // Close the success response
}); // Close the POST /vote route

app.get("/results", (req, res) => { // Define an endpoint to tally and display the current election results
    const sorted = [...proposals].sort((a, b) => b.totalVotes - a.totalVotes); // Sort proposals by total votes descending so the leader appears first
    return res.status(200).json({ // Return the sorted results so clients can display rankings
        count: proposals.length, // Include the total number of proposals so summary widgets can display it
        proposals: sorted, // Return the sorted array so the client sees the current standings
    }); // Close the success response
}); // Close the GET /results route

app.get("/voters/:address", (req, res) => { // Define an endpoint to inspect a voter's budget and vote history
    const address = req.params.address; // Extract the address from the URL path so the server can look up the specific voter
    const voter = voters.get(address); // Retrieve the voter so their data can be returned
    if (!voter) { // Check if the voter exists so the server returns a proper error instead of null
        return res.status(404).json({ error: "Voter not found" }); // Return 404 so the client knows the address is unregistered
    } // Close the existence check
    return res.status(200).json({ // Return the voter's state so the client can display their budget and votes
        address: voter.address, // Include the address so the response is self-contained
        remainingCredits: voter.voiceCredits, // Include the remaining budget so the voter knows their spending power
        votesCast: Object.fromEntries(voter.votesCast), // Convert the Map to a plain object so JSON serialization works correctly
    }); // Close the success response
}); // Close the GET /voters/:address route

app.listen(3043, () => { // Start the HTTP server on port 3043 because this phase owns that port to avoid conflicts with other APIs
    console.log("Quadratic Voting API listening on port 3043"); // Log startup so operators know the service is ready to accept connections
}); // Close the listen callback
