import express from "express"; // Import the express framework to build the HTTP server
import bodyParser from "body-parser"; // Import body-parser to parse JSON request bodies

const app = express(); // Create the express application instance
app.use(bodyParser.json()); // Attach middleware to parse incoming JSON request bodies

interface OptionContract { // Define the shape of an option contract for type safety
    id: string; // Store a unique identifier so each contract can be referenced individually
    writer: string; // Store the address of the seller who receives the premium and assumes obligation
    holder: string; // Store the address of the buyer who pays the premium and holds the right
    side: "call" | "put"; // Store whether the contract is a call or a put for payoff routing
    strike: number; // Store the agreed transaction price if the option is exercised
    premium: number; // Store the upfront cost paid by the holder to the writer
    expiration: number; // Store the expiration timestamp in milliseconds since epoch
    size: number; // Store the quantity of the underlying asset covered by the contract
    exercised: boolean; // Store whether the option has already been exercised to prevent double execution
}

let options: OptionContract[] = []; // Initialize an in-memory array to hold all created option contracts
let currentUnderlyingPrice = 2000; // Initialize the simulated underlying price to a realistic starting value

function calculatePremium(strike: number, timeToExpiryDays: number, volatility: number, side: "call" | "put"): number { // Estimate a fair premium using a simplified pricing model
    const intrinsic = side === "call" // Determine whether to compute call or put intrinsic value
        ? Math.max(0, currentUnderlyingPrice - strike) // Compute call intrinsic as current price minus strike floored at zero
        : Math.max(0, strike - currentUnderlyingPrice); // Compute put intrinsic as strike minus current price floored at zero
    const timeValue = currentUnderlyingPrice * volatility * Math.sqrt(timeToExpiryDays / 365); // Estimate time value from volatility and time remaining
    return intrinsic + timeValue; // Return total premium as the sum of intrinsic and time value
} // Close the premium calculation helper

function calculatePayoff(contract: OptionContract): number { // Compute the gross payoff if the option is exercised now
    if (contract.side === "call") { // Check if the contract is a call
        return Math.max(0, currentUnderlyingPrice - contract.strike) * contract.size; // Compute call payoff per unit times size
    } else { // Handle the put case
        return Math.max(0, contract.strike - currentUnderlyingPrice) * contract.size; // Compute put payoff per unit times size
    } // Close the side branch
} // Close the payoff helper

app.post("/option/create", (req, res) => { // Define endpoint to create a new option contract
    const { writer, holder, side, strike, timeToExpiryDays, volatility, size } = req.body; // Extract contract parameters from the request body
    if (!writer || !holder || !side || !strike || timeToExpiryDays === undefined || volatility === undefined || !size) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing required fields for option creation" }); // Return 400 if input is incomplete
    } // Close the validation block
    if (side !== "call" && side !== "put") { // Validate that the side is either call or put
        return res.status(400).json({ error: "Side must be 'call' or 'put'" }); // Return 400 if side is invalid
    } // Close the side validation block
    const premium = calculatePremium(strike, timeToExpiryDays, volatility, side); // Compute the premium using the simplified model
    const expiration = Date.now() + timeToExpiryDays * 24 * 60 * 60 * 1000; // Compute the expiration timestamp from days provided
    const contract: OptionContract = { // Build the option contract object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the contract
        writer, // Assign the writer address from the request
        holder, // Assign the holder address from the request
        side, // Assign the side from the request
        strike, // Assign the strike price from the request
        premium, // Assign the computed premium
        expiration, // Assign the computed expiration timestamp
        size, // Assign the contract size from the request
        exercised: false, // Mark the contract as unexercised at creation
    }; // Close the contract object
    options.push(contract); // Add the new contract to the global in-memory array
    return res.status(201).json({ // Return the created contract to the client
        message: "Option contract created", // Confirm that the contract was created successfully
        contract, // Include the full contract details for client reference
    }); // Close the success response
}); // Close the POST /option/create route

app.post("/option/exercise/:id", (req, res) => { // Define endpoint to exercise an existing option contract
    const contract = options.find((o) => o.id === req.params.id); // Search the array for a contract matching the URL ID
    if (!contract) { // Check if the contract was found
        return res.status(404).json({ error: "Option contract not found" }); // Return 404 if the ID does not exist
    } // Close the not-found branch
    if (contract.exercised) { // Check if the contract has already been exercised
        return res.status(400).json({ error: "Option already exercised" }); // Return 400 to prevent double exercise
    } // Close the already-exercised branch
    if (Date.now() > contract.expiration) { // Check if the current time is past the expiration date
        return res.status(400).json({ error: "Option has expired" }); // Return 400 because expired options cannot be exercised
    } // Close the expiration check
    const payoff = calculatePayoff(contract); // Compute the gross payoff based on the current underlying price
    const netPayoff = payoff - contract.premium; // Compute the net profit after subtracting the premium paid
    contract.exercised = true; // Mark the contract as exercised to prevent future duplicate execution
    return res.status(200).json({ // Return the exercise result to the client
        message: "Option exercised", // Confirm that exercise was successful
        contractId: contract.id, // Echo the contract ID for reference
        side: contract.side, // Include the side for clarity
        strike: contract.strike, // Include the strike price
        currentPrice: currentUnderlyingPrice, // Include the price used for settlement
        payoff, // Include the gross payoff before premium
        netPayoff, // Include the net profit or loss after premium
    }); // Close the success response
}); // Close the POST /option/exercise/:id route

app.post("/market/set-price", (req, res) => { // Define endpoint to update the simulated underlying price
    const { price } = req.body; // Extract the new price from the request body
    if (price === undefined || price <= 0) { // Validate that the price is a positive number
        return res.status(400).json({ error: "Price must be a positive number" }); // Return 400 if price is invalid
    } // Close the validation block
    currentUnderlyingPrice = price; // Update the global underlying price to the new simulated value
    return res.status(200).json({ // Return the updated price to the client
        message: "Underlying price updated", // Confirm the update
        currentUnderlyingPrice, // Echo the new price
    }); // Close the success response
}); // Close the POST /market/set-price route

app.get("/option/:id", (req, res) => { // Define endpoint to fetch details of a specific option contract
    const contract = options.find((o) => o.id === req.params.id); // Search the array for a contract matching the URL ID
    if (!contract) { // Check if the contract was found
        return res.status(404).json({ error: "Option contract not found" }); // Return 404 if the ID does not exist
    } // Close the not-found branch
    const payoff = calculatePayoff(contract); // Compute the current gross payoff using the latest underlying price
    const intrinsicValue = contract.side === "call" // Determine which intrinsic formula to use
        ? Math.max(0, currentUnderlyingPrice - contract.strike) // Compute call intrinsic value
        : Math.max(0, contract.strike - currentUnderlyingPrice); // Compute put intrinsic value
    const timeValue = contract.premium - intrinsicValue; // Derive time value as the portion of premium not explained by intrinsic value
    return res.status(200).json({ // Return the enriched contract details
        contract, // Include the base contract data
        currentUnderlyingPrice, // Include the latest underlying price for context
        currentPayoff: payoff, // Include the current gross payoff
        intrinsicValue, // Include the intrinsic component of value
        timeValue: Math.max(0, timeValue), // Include the time value floored at zero to avoid negative display errors
        isExpired: Date.now() > contract.expiration, // Indicate whether the contract has passed its expiration
    }); // Close the success response
}); // Close the GET /option/:id route

app.get("/market/implied-vol", (req, res) => { // Define endpoint to estimate implied volatility from an observed premium
    const { premium, strike, timeToExpiryDays, side } = req.query; // Extract parameters from the query string
    if (!premium || !strike || !timeToExpiryDays || !side) { // Validate that all required query parameters are present
        return res.status(400).json({ error: "Missing query parameters: premium, strike, timeToExpiryDays, side" }); // Return 400 if incomplete
    } // Close the validation block
    const p = Number(premium); // Convert the premium query parameter to a number
    const s = Number(strike); // Convert the strike query parameter to a number
    const t = Number(timeToExpiryDays); // Convert the time query parameter to a number
    const intrinsic = side === "call" // Determine which intrinsic formula to use
        ? Math.max(0, currentUnderlyingPrice - s) // Compute call intrinsic value from current price
        : Math.max(0, s - currentUnderlyingPrice); // Compute put intrinsic value from current price
    const timeValue = Math.max(0, p - intrinsic); // Compute time value as premium minus intrinsic floored at zero
    const impliedVol = timeValue / (currentUnderlyingPrice * Math.sqrt(t / 365)); // Estimate implied volatility by inverting the time value formula
    return res.status(200).json({ // Return the estimated implied volatility
        currentUnderlyingPrice, // Include the price used in the calculation
        premium: p, // Echo the input premium
        strike: s, // Echo the input strike
        timeToExpiryDays: t, // Echo the input time
        side, // Echo the input side
        intrinsicValue: intrinsic, // Include the computed intrinsic value
        timeValue, // Include the computed time value
        impliedVolatility: impliedVol, // Return the estimated implied volatility
    }); // Close the success response
}); // Close the GET /market/implied-vol route

app.listen(3046, () => { // Start the HTTP server on port 3046
    console.log("Options API listening on port 3046"); // Log startup so operators know the service is ready
}); // Close the listen callback
