import express from "express"; // Import the express framework to build the HTTP server
import bodyParser from "body-parser"; // Import body-parser to parse JSON request bodies

const app = express(); // Create the express application instance
app.use(bodyParser.json()); // Attach middleware to parse incoming JSON request bodies

interface Position { // Define the shape of a perpetual position for type safety
    id: string; // Store a unique identifier so each position can be tracked individually
    trader: string; // Store the trader address to associate the position with an owner
    side: "long" | "short"; // Store whether the position bets on price increase or decrease
    entryPrice: number; // Store the price at which the position was opened for PnL calculation
    size: number; // Store the quantity of the asset controlled by the position
    leverage: number; // Store the leverage multiplier to compute margin and liquidation price
    margin: number; // Store the collateral deposited by the trader to secure the position
    liquidationPrice: number; // Store the price threshold where the position is force-closed
}

let positions: Position[] = []; // Initialize an in-memory array to hold all open positions
let markPrice = 2000; // Initialize the simulated mark price to a realistic starting value
let indexPrice = 2000; // Initialize the simulated spot index price equal to mark at genesis
let fundingIntervalHours = 8; // Define how often funding payments are applied in hours
let fundingRate = 0.0005; // Set a default funding rate of 0.05% per interval for simulation

function calculateLiquidationPrice(entry: number, leverage: number, side: "long" | "short"): number { // Compute the price where margin is exhausted
    const maintenanceMargin = 0.05; // Require 5% maintenance margin to avoid immediate liquidation
    if (side === "long") { // Check if the position direction is upward
        return entry * (1 - 1 / leverage + maintenanceMargin / leverage); // Derive liquidation price below entry for longs
    } else { // Handle the short case where price rising causes losses
        return entry * (1 + 1 / leverage - maintenanceMargin / leverage); // Derive liquidation price above entry for shorts
    } // Close the side branch
} // Close the liquidation price helper

function applyFunding(): void { // Deduct or credit funding payments to all open positions
    const premium = (markPrice - indexPrice) / indexPrice; // Compute the percentage premium of mark over index
    fundingRate = premium * 0.1; // Scale the premium by 10% to derive a realistic funding rate
    for (const pos of positions) { // Iterate over every open position to adjust margin
        const notional = pos.size * markPrice; // Compute the current dollar value of the position
        const payment = notional * fundingRate; // Compute the funding payment based on notional size and rate
        if (pos.side === "long") { // Check if the position is long because longs pay when premium is positive
            pos.margin -= payment; // Deduct the funding payment from the long's margin
        } else { // Handle the short side which receives funding when mark is above index
            pos.margin += payment; // Credit the funding payment to the short's margin
        } // Close the side branch
    } // Close the position loop
} // Close the funding application function

function checkLiquidations(): string[] { // Identify and close positions that have breached their liquidation threshold
    const liquidated: string[] = []; // Initialize an array to collect IDs of liquidated positions
    positions = positions.filter((pos) => { // Filter positions to remove those that have been liquidated
        const shouldLiquidate = pos.side === "long" ? markPrice <= pos.liquidationPrice : markPrice >= pos.liquidationPrice; // Determine if the current price triggers liquidation based on side
        if (shouldLiquidate) { // Check if this position has crossed its liquidation boundary
            liquidated.push(pos.id); // Record the position ID so the API can report what was closed
            return false; // Exclude this position from the surviving array
        } // Close the liquidation trigger branch
        return true; // Keep this position open because it still has sufficient margin
    }); // Close the filter operation
    return liquidated; // Return the list of liquidated IDs for the response
} // Close the liquidation check function

app.post("/position/open", (req, res) => { // Define endpoint to create a new leveraged perpetual position
    const { trader, side, entryPrice, size, leverage } = req.body; // Extract position parameters from the request body
    if (!trader || !side || !entryPrice || !size || !leverage) { // Validate that all required fields are present
        return res.status(400).json({ error: "Missing required fields: trader, side, entryPrice, size, leverage" }); // Return 400 if input is incomplete
    } // Close the validation block
    if (leverage < 1 || leverage > 50) { // Enforce a leverage cap to prevent impossibly risky positions
        return res.status(400).json({ error: "Leverage must be between 1x and 50x" }); // Return 400 if leverage is out of bounds
    } // Close the leverage validation block
    const margin = (size * entryPrice) / leverage; // Compute the collateral required based on notional size and leverage
    const liquidationPrice = calculateLiquidationPrice(entryPrice, leverage, side); // Derive the automatic closure price
    const position: Position = { // Build the position object to store in memory
        id: Math.random().toString(36).substring(2, 10), // Generate a random alphanumeric ID for the position
        trader, // Assign the trader address from the request
        side, // Assign the side from the request
        entryPrice, // Assign the entry price from the request
        size, // Assign the size from the request
        leverage, // Assign the leverage from the request
        margin, // Assign the computed margin
        liquidationPrice, // Assign the computed liquidation price
    }; // Close the position object
    positions.push(position); // Add the new position to the global in-memory array
    return res.status(201).json({ // Return the created position to the client
        message: "Position opened", // Confirm that the position was created successfully
        position, // Include the full position details for client reference
    }); // Close the success response
}); // Close the POST /position/open route

app.post("/market/tick", (req, res) => { // Define endpoint to simulate a new mark price and process consequences
    const { newMarkPrice, newIndexPrice } = req.body; // Extract the simulated prices from the request body
    if (newMarkPrice === undefined || newIndexPrice === undefined) { // Validate that both prices are provided
        return res.status(400).json({ error: "Missing newMarkPrice or newIndexPrice" }); // Return 400 if prices are missing
    } // Close the validation block
    markPrice = newMarkPrice; // Update the global mark price to the new simulated value
    indexPrice = newIndexPrice; // Update the global index price to the new simulated value
    applyFunding(); // Recompute and apply funding payments based on the new premium
    const liquidated = checkLiquidations(); // Evaluate all positions and liquidate those underwater
    return res.status(200).json({ // Return the market tick result to the client
        markPrice, // Echo the new mark price
        indexPrice, // Echo the new index price
        fundingRate, // Include the computed funding rate after the tick
        liquidated, // List the IDs of positions that were closed by liquidation
        openPositions: positions.length, // Report how many positions remain open
    }); // Close the success response
}); // Close the POST /market/tick route

app.get("/position/:id", (req, res) => { // Define endpoint to fetch details of a specific position
    const position = positions.find((p) => p.id === req.params.id); // Search the array for a position matching the URL ID
    if (!position) { // Check if the position was found
        return res.status(404).json({ error: "Position not found" }); // Return 404 if the ID does not exist
    } // Close the not-found branch
    const notional = position.size * markPrice; // Compute the current notional value using the latest mark price
    const pnl = position.side === "long" // Determine whether to compute long or short PnL
        ? notional - position.size * position.entryPrice // Compute profit for longs as current value minus entry cost
        : position.size * position.entryPrice - notional; // Compute profit for shorts as entry proceeds minus current cost
    return res.status(200).json({ // Return the enriched position details
        position, // Include the base position data
        currentMarkPrice: markPrice, // Include the latest mark price for context
        notional, // Include the current dollar value of the position
        unrealizedPnl: pnl, // Include the floating profit or loss before closure
        unrealizedPnlPercent: (pnl / position.margin) * 100, // Express PnL as a percentage of the initial margin
    }); // Close the success response
}); // Close the GET /position/:id route

app.get("/market/status", (req, res) => { // Define endpoint to inspect the current simulated market state
    return res.status(200).json({ // Return the global market variables
        markPrice, // Return the current mark price
        indexPrice, // Return the current index price
        fundingRate, // Return the active funding rate
        fundingIntervalHours, // Return the funding interval for client scheduling
        openInterestLong: positions.filter((p) => p.side === "long").reduce((sum, p) => sum + p.size * markPrice, 0), // Sum notional of all longs
        openInterestShort: positions.filter((p) => p.side === "short").reduce((sum, p) => sum + p.size * markPrice, 0), // Sum notional of all shorts
    }); // Close the success response
}); // Close the GET /market/status route

app.listen(3045, () => { // Start the HTTP server on port 3045
    console.log("Perpetual API listening on port 3045"); // Log startup so operators know the service is ready
}); // Close the listen callback
