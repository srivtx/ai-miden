import express, { Request, Response } from 'express';

/**
 * Phase 30: Arbitrage Bot Simulator
 *
 * Simulates arbitrage strategies across multiple DEXes with:
 * - Real-time price monitoring
 * - Opportunity detection and profitability calculation
 * - Flash loan integration
 * - MEV analysis and sandwich attack simulation
 *
 * Run: npx ts-node src_web3/phase30/arbitrage_bot.ts
 */

const app = express(); // Initialize Express to serve arbitrage simulation endpoints
app.use(express.json()); // Parse JSON bodies for strategy configuration requests

const PORT = 3015; // Dedicated port for the arbitrage bot service

// ============================================================================
// TYPES
// ============================================================================
interface DEXPrice {
    dex: string; // Exchange name
    tokenPair: string; // Trading pair symbol
    bid: number; // Price at which the DEX buys the base token
    ask: number; // Price at which the DEX sells the base token
    liquidity: number; // Available liquidity in USD
    lastUpdated: number; // Timestamp of last price update
}

interface ArbitrageOpportunity {
    id: string; // Unique opportunity identifier
    tokenPair: string; // Which pair shows the discrepancy
    buyDex: string; // Where to buy low
    sellDex: string; // Where to sell high
    buyPrice: number; // Lower price
    sellPrice: number; // Higher price
    spread: number; // Absolute price difference
    spreadPercent: number; // Percentage spread
    maxTradeSize: number; // Limited by the lower liquidity side
    estimatedProfit: number; // Profit after flash loan fee
    flashLoanFee: number; // Cost of borrowing capital
    netProfit: number; // Final profit
    timestamp: number; // When the opportunity was detected
}

interface MEVAnalysis {
    targetTx: string; // Transaction being analyzed for MEV extraction
    mevType: 'sandwich' | 'frontrun' | 'backrun' | 'arbitrage'; // Category of MEV opportunity
    estimatedProfit: number; // How much value could be extracted
    risk: number; // 1-10 risk score
    bundle: string[]; // Ordered transaction signatures for the MEV bundle
    protection: string[]; // Recommendations to protect against this MEV
}

// ============================================================================
// MOCK DEX PRICES
// ============================================================================
const dexPrices: DEXPrice[] = [
    { dex: 'Raydium', tokenPair: 'SOL/USDC', bid: 21.95, ask: 22.05, liquidity: 5000000, lastUpdated: Date.now() },
    { dex: 'Orca', tokenPair: 'SOL/USDC', bid: 22.00, ask: 22.10, liquidity: 3000000, lastUpdated: Date.now() },
    { dex: 'Jupiter', tokenPair: 'SOL/USDC', bid: 21.98, ask: 22.08, liquidity: 8000000, lastUpdated: Date.now() },
    { dex: 'Raydium', tokenPair: 'BONK/USDC', bid: 0.0000098, ask: 0.0000102, liquidity: 500000, lastUpdated: Date.now() },
    { dex: 'Orca', tokenPair: 'BONK/USDC', bid: 0.0000100, ask: 0.0000105, liquidity: 300000, lastUpdated: Date.now() },
    { dex: 'Raydium', tokenPair: 'USDC/USDT', bid: 0.999, ask: 1.001, liquidity: 10000000, lastUpdated: Date.now() },
    { dex: 'Orca', tokenPair: 'USDC/USDT', bid: 0.998, ask: 1.002, liquidity: 8000000, lastUpdated: Date.now() },
];

// ============================================================================
// ARBITRAGE DETECTION ENGINE
// ============================================================================

/**
 * Scan all DEX prices to find profitable arbitrage opportunities.
 */
function findArbitrageOpportunities(): ArbitrageOpportunity[] {
    const opportunities: ArbitrageOpportunity[] = []; // Collect all detected opportunities
    const flashLoanFeeRate = 0.0009; // 0.09% flash loan fee from the flash loan API

    // Group prices by token pair so we can compare DEXes for the same pair
    const pairMap = new Map<string, DEXPrice[]>();
    for (const price of dexPrices) {
        const list = pairMap.get(price.tokenPair) || []; // Get existing list or create empty
        list.push(price);
        pairMap.set(price.tokenPair, list); // Update the map with the new entry
    }

    for (const [tokenPair, prices] of pairMap.entries()) {
        for (let i = 0; i < prices.length; i++) {
            for (let j = 0; j < prices.length; j++) {
                if (i === j) continue; // Skip comparing a DEX with itself

                const buyDex = prices[i]; // DEX where we would buy
                const sellDex = prices[j]; // DEX where we would sell

                // Arbitrage exists if we can buy low and sell high
                if (sellDex.bid > buyDex.ask) {
                    const spread = sellDex.bid - buyDex.ask; // Absolute price difference
                    const spreadPercent = (spread / buyDex.ask) * 100; // Percentage difference
                    const maxTradeSize = Math.min(buyDex.liquidity, sellDex.liquidity) * 0.1; // Use 10% of min liquidity to avoid slippage
                    const grossProfit = maxTradeSize * (spreadPercent / 100); // Profit before fees
                    const flashLoanFee = maxTradeSize * flashLoanFeeRate; // Cost to borrow capital
                    const netProfit = grossProfit - flashLoanFee; // True profit after all costs

                    if (netProfit > 0) {
                        opportunities.push({
                            id: `arb_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`, // Unique ID for tracking
                            tokenPair,
                            buyDex: buyDex.dex,
                            sellDex: sellDex.dex,
                            buyPrice: buyDex.ask,
                            sellPrice: sellDex.bid,
                            spread: parseFloat(spread.toFixed(6)),
                            spreadPercent: parseFloat(spreadPercent.toFixed(4)),
                            maxTradeSize: parseFloat(maxTradeSize.toFixed(2)),
                            estimatedProfit: parseFloat(grossProfit.toFixed(4)),
                            flashLoanFee: parseFloat(flashLoanFee.toFixed(4)),
                            netProfit: parseFloat(netProfit.toFixed(4)),
                            timestamp: Date.now(),
                        });
                    }
                }
            }
        }
    }

    return opportunities.sort((a, b) => b.netProfit - a.netProfit); // Sort by profit so the best opportunities appear first
}

// ============================================================================
// MEV ANALYSIS ENGINE
// ============================================================================

/**
 * Analyze a target transaction for MEV extraction opportunities.
 */
function analyzeMEV(targetTx: string, tokenPair: string, tradeSize: number): MEVAnalysis {
    const prices = dexPrices.filter(p => p.tokenPair === tokenPair); // Get relevant DEX prices for the pair
    const buyPrice = Math.min(...prices.map(p => p.ask)); // Best available ask price
    const sellPrice = Math.max(...prices.map(p => p.bid)); // Best available bid price

    const priceImpact = tradeSize / (prices[0]?.liquidity || 1); // Estimate how much the trade moves the price
    const sandwichProfit = tradeSize * priceImpact * 0.5; // Searchers capture about half the price impact

    const analysis: MEVAnalysis = {
        targetTx,
        mevType: 'sandwich', // Default to sandwich as it is the most common harmful MEV
        estimatedProfit: parseFloat(sandwichProfit.toFixed(4)),
        risk: priceImpact > 0.01 ? 8 : 4, // Higher risk for trades that move the price more than 1%
        bundle: [
            `searcher_buy_${tokenPair}`, // Step 1: Searcher buys to push price up
            targetTx, // Step 2: Victim's transaction executes at worse price
            `searcher_sell_${tokenPair}`, // Step 3: Searcher sells at the inflated price
        ],
        protection: [
            'Use slippage tolerance of 0.5% or less', // Tight slippage prevents execution at bad prices
            'Route through MEV-protecting RPC endpoints', // Services like Jito or Flashbots protect transaction ordering
            'Split large trades into smaller chunks', // Smaller trades have less price impact and attract less MEV
            'Use private mempool submission', // Hide the transaction from public mempools until it is included
        ],
    };

    return analysis;
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        dexes: new Set(dexPrices.map(p => p.dex)).size, // Count unique DEXes being monitored
        pairs: new Set(dexPrices.map(p => p.tokenPair)).size, // Count unique trading pairs
    });
});

/**
 * GET /prices
 * Current prices across all DEXes
 */
app.get('/prices', (req: Request, res: Response) => {
    const { pair } = req.query; // Optional filter for a specific trading pair
    let prices = dexPrices;

    if (pair) {
        prices = prices.filter(p => p.tokenPair === pair); // Filter if pair parameter is provided
    }

    res.json({ count: prices.length, prices });
});

/**
 * GET /opportunities
 * Find current arbitrage opportunities
 */
app.get('/opportunities', (_req: Request, res: Response) => {
    const opportunities = findArbitrageOpportunities(); // Run the detection engine
    res.json({
        count: opportunities.length,
        bestOpportunity: opportunities.length > 0 ? opportunities[0] : null, // Surface the top opportunity for quick decisions
        opportunities: opportunities.slice(0, 10), // Limit to top 10 to keep response size manageable
    });
});

/**
 * POST /execute
 * Simulate executing an arbitrage trade with flash loan
 */
app.post('/execute', (req: Request, res: Response) => {
    const { tokenPair, buyDex, sellDex, amount, useFlashLoan } = req.body; // Extract trade parameters

    if (!tokenPair || !buyDex || !sellDex || !amount) {
        return res.status(400).json({ error: 'tokenPair, buyDex, sellDex, and amount are required' }); // Validate required fields
    }

    const buyPrice = dexPrices.find(p => p.dex === buyDex && p.tokenPair === tokenPair)?.ask; // Find the buy price
    const sellPrice = dexPrices.find(p => p.dex === sellDex && p.tokenPair === tokenPair)?.bid; // Find the sell price

    if (!buyPrice || !sellPrice) {
        return res.status(404).json({ error: 'Price data not found for specified DEXes' }); // Reject if DEX or pair is unknown
    }

    const flashLoanFeeRate = useFlashLoan ? 0.0009 : 0; // Only apply flash loan fee if explicitly requested
    const grossProfit = amount * ((sellPrice - buyPrice) / buyPrice); // Calculate profit from price spread
    const flashLoanFee = amount * flashLoanFeeRate; // Calculate borrowing cost
    const netProfit = grossProfit - flashLoanFee; // True profit after fees

    const execution = {
        tokenPair,
        buyDex,
        sellDex,
        amount,
        buyPrice,
        sellPrice,
        grossProfit: parseFloat(grossProfit.toFixed(6)),
        flashLoanFee: parseFloat(flashLoanFee.toFixed(6)),
        netProfit: parseFloat(netProfit.toFixed(6)),
        profitable: netProfit > 0,
        useFlashLoan: !!useFlashLoan,
        timestamp: new Date().toISOString(),
    };

    res.json({ success: netProfit > 0, execution }); // Return execution details with profitability flag
});

/**
 * POST /mev/analyze
 * Analyze a transaction for MEV exposure
 */
app.post('/mev/analyze', (req: Request, res: Response) => {
    const { targetTx, tokenPair, tradeSize } = req.body; // Extract transaction to analyze

    if (!targetTx || !tokenPair || !tradeSize) {
        return res.status(400).json({ error: 'targetTx, tokenPair, and tradeSize are required' }); // Validate inputs
    }

    const analysis = analyzeMEV(targetTx, tokenPair, parseFloat(tradeSize)); // Run MEV analysis
    res.json({ analysis });
});

/**
 * GET /mev/protection
 * Get MEV protection recommendations
 */
app.get('/mev/protection', (_req: Request, res: Response) => {
    res.json({
        recommendations: [
            { strategy: 'Slippage Tolerance', description: 'Set maximum slippage to 0.5% to prevent execution at bad prices', effectiveness: 'High' },
            { strategy: 'MEV RPC', description: 'Use RPC endpoints that submit transactions through MEV-protecting relays', effectiveness: 'Very High' },
            { strategy: 'Trade Splitting', description: 'Break large orders into smaller pieces to reduce price impact', effectiveness: 'Medium' },
            { strategy: 'Private Mempool', description: 'Submit transactions privately so searchers cannot see them in advance', effectiveness: 'Very High' },
            { strategy: 'Time Delay', description: 'Avoid trading during high-volatility periods when MEV activity spikes', effectiveness: 'Low' },
        ],
    });
});

/**
 * GET /stats
 * Arbitrage bot statistics
 */
app.get('/stats', (_req: Request, res: Response) => {
    const opportunities = findArbitrageOpportunities(); // Re-run detection for current stats
    const avgSpread = opportunities.length > 0
        ? opportunities.reduce((sum, o) => sum + o.spreadPercent, 0) / opportunities.length
        : 0; // Calculate average spread across all opportunities

    res.json({
        totalOpportunities: opportunities.length,
        avgSpreadPercent: parseFloat(avgSpread.toFixed(4)),
        bestPair: opportunities.length > 0 ? opportunities[0].tokenPair : null, // Which pair currently has the best opportunity
        totalDexes: new Set(dexPrices.map(p => p.dex)).size,
        totalPairs: new Set(dexPrices.map(p => p.tokenPair)).size,
    });
});

app.listen(PORT, () => {
    console.log(`=== Phase 30: Arbitrage Bot Simulator ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /prices              - Current DEX prices`);
    console.log(`  GET  /opportunities       - Find arbitrage opportunities`);
    console.log(`  POST /execute             - Simulate arbitrage execution`);
    console.log(`  POST /mev/analyze         - Analyze MEV exposure`);
    console.log(`  GET  /mev/protection      - MEV protection strategies`);
    console.log(`  GET  /stats               - Bot statistics`);
    console.log(`\nMonitored DEXes: Raydium, Orca, Jupiter`);
    console.log(`Monitored Pairs: SOL/USDC, BONK/USDC, USDC/USDT`);
});
