import express, { Request, Response } from 'express';

/**
 * Phase 30: Flash Loan API
 *
 * REST API demonstrating flash loan mechanics:
 * POST /flash/execute - Execute a flash loan
 * GET /flash/rates - Get current flash loan rates
 * GET /flash/history - Get execution history
 *
 * Flash loans: borrow any amount, use it, repay + fee in same transaction
 *
 * Run: npx ts-node src_web3/phase30/flash_loan_api.ts
 */

const app = express(); // Create the Express application for flash loan operations
app.use(express.json()); // Parse JSON bodies so clients can send loan parameters and strategies

const PORT = 3006; // Dedicated port for the flash loan service

// ============================================================================
// TYPES
// ============================================================================
interface FlashLoan {
    id: string; // Unique identifier for tracking and referencing this execution
    token: string; // Which token was borrowed
    amount: number; // Principal borrowed
    fee: number; // Fee paid to the liquidity pool
    profit: number; // Net profit after fees
    strategy: string; // Which strategy was executed
    executedAt: number; // Unix timestamp for history queries
    status: 'success' | 'failed'; // Atomic outcome: either everything worked or nothing happened
}

interface LiquidityPool {
    token: string; // Token symbol for the pool
    available: number; // Current liquid funds available for borrowing
    fee: number; // Fee rate as decimal (0.0009 = 0.09%)
    totalBorrowed: number; // Cumulative amount lent out historically
    totalRepaid: number; // Cumulative amount returned by borrowers
}

// ============================================================================
// STORAGE
// ============================================================================
const history: FlashLoan[] = []; // Log of every flash loan execution for analytics and debugging
const pools: Map<string, LiquidityPool> = new Map(); // Active liquidity pools keyed by token symbol

// Initialize with demo pools so the API works immediately for testing
pools.set('SOL', { token: 'SOL', available: 1000000, fee: 0.0009, totalBorrowed: 0, totalRepaid: 0 }); // 0.09% fee on SOL pool
pools.set('USDC', { token: 'USDC', available: 5000000, fee: 0.0009, totalBorrowed: 0, totalRepaid: 0 }); // Deep USDC liquidity for stablecoin strategies
pools.set('USDT', { token: 'USDT', available: 3000000, fee: 0.0009, totalBorrowed: 0, totalRepaid: 0 }); // USDT pool for cross-stable arbitrage
pools.set('BONK', { token: 'BONK', available: 500000000000, fee: 0.0015, totalBorrowed: 0, totalRepaid: 0 }); // Higher fee on memecoins due to volatility

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Simulate a strategy to calculate expected profit before executing.
 */
function simulateStrategy(strategy: string, amount: number, feeRate: number): { actualProfit: number; netProfit: number; requiredRepayment: number } {
    const fee = amount * feeRate; // Calculate the pool fee based on borrowed amount
    const requiredRepayment = amount + fee; // Borrower must return principal plus fee for the loan to be valid
    let actualProfit = 0; // Default to zero profit for unknown strategies

    switch (strategy) {
        case 'arbitrage':
            actualProfit = amount * 0.001; // 0.1% arbitrage profit: buy low on one DEX, sell high on another
            break;
        case 'liquidation':
            actualProfit = amount * 0.05; // 5% liquidation bonus: repay someone's debt, seize their collateral at a discount
            break;
        case 'collateral_swap':
            actualProfit = amount * 0.002; // 0.2% savings: swap collateral in a lending position to avoid interest or maintain LTV
            break;
        case 'triangular_arbitrage':
            actualProfit = amount * 0.0008; // 0.08% profit: exploit pricing inefficiencies across three trading pairs
            break;
        case 'dex_rebalance':
            actualProfit = amount * 0.0015; // 0.15% profit: rebalance liquidity pools across DEXes for incentives
            break;
        default:
            actualProfit = 0; // Unknown strategies default to zero profit, which will cause failure
    }

    const netProfit = actualProfit - fee; // Net profit is what remains after paying the flash loan fee
    return { actualProfit, netProfit, requiredRepayment };
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => {
    const poolStats = Array.from(pools.values()).map(p => ({
        token: p.token,
        available: p.available,
        utilization: p.totalBorrowed > 0 ? p.totalRepaid / p.totalBorrowed : 1, // Measure pool health
    }));
    res.json({ status: 'healthy', pools: pools.size, totalExecutions: history.length, poolStats });
});

/**
 * GET /flash/pools
 * Get available flash loan pools
 */
app.get('/flash/pools', (_req: Request, res: Response) => {
    const list = Array.from(pools.values()).map(p => ({
        token: p.token,
        available: p.available,
        fee: `${p.fee * 100}%`, // Human-readable fee percentage
        feeAmount: p.fee,
        totalBorrowed: p.totalBorrowed,
        totalRepaid: p.totalRepaid,
    }));

    res.json({ pools: list });
});

/**
 * POST /flash/pools
 * Add or update a liquidity pool
 */
app.post('/flash/pools', (req: Request, res: Response) => {
    const { token, available, fee } = req.body; // Extract pool parameters from request

    if (!token || available === undefined || fee === undefined) {
        return res.status(400).json({ error: 'token, available, and fee are required' }); // Reject incomplete pool definitions
    }

    const existing = pools.get(token);
    const pool: LiquidityPool = {
        token,
        available,
        fee,
        totalBorrowed: existing ? existing.totalBorrowed : 0, // Preserve historical stats if updating
        totalRepaid: existing ? existing.totalRepaid : 0,
    };

    pools.set(token, pool); // Store or update the pool configuration
    res.status(201).json({ success: true, pool });
});

/**
 * POST /flash/execute
 * Execute a flash loan
 */
app.post('/flash/execute', (req: Request, res: Response) => {
    try {
        const { token, amount, strategy, expectedProfit } = req.body; // Extract loan request parameters

        if (!token || !amount || !strategy) {
            return res.status(400).json({ error: 'Missing parameters: token, amount, and strategy are required' }); // Validate required fields
        }

        const pool = pools.get(token); // Look up the liquidity pool for the requested token
        if (!pool) {
            return res.status(404).json({ error: 'Pool not found' }); // Reject requests for unsupported tokens
        }

        if (amount > pool.available) {
            return res.status(400).json({
                error: 'Insufficient liquidity',
                requested: amount,
                available: pool.available,
            }); // Prevent borrowing more than the pool holds
        }

        const { actualProfit, netProfit, requiredRepayment } = simulateStrategy(strategy, amount, pool.fee); // Run the strategy simulation
        const status: 'success' | 'failed' = netProfit > 0 ? 'success' : 'failed'; // Flash loans only succeed if profitable after fees

        const execution: FlashLoan = {
            id: `flash_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`, // Generate unique execution ID
            token,
            amount,
            fee: amount * pool.fee,
            profit: netProfit,
            strategy,
            executedAt: Date.now(),
            status,
        };

        history.push(execution); // Record the execution for analytics

        if (status === 'success') {
            pool.totalBorrowed += amount; // Track cumulative borrowing for pool statistics
            pool.totalRepaid += requiredRepayment + netProfit; // Simulate repayment with profit
        }

        res.json({
            success: status === 'success',
            execution: {
                id: execution.id,
                token,
                borrowed: amount,
                fee: `${execution.fee} ${token}`,
                feePercent: `${pool.fee * 100}%`,
                repayment: requiredRepayment,
                strategyProfit: actualProfit,
                netProfit,
                status,
            },
            atomic: true, // Emphasize that this entire operation is atomic
            message: status === 'success'
                ? `Flash loan profitable! Net profit: ${netProfit.toFixed(6)} ${token}`
                : `Flash loan unprofitable. Net loss: ${Math.abs(netProfit).toFixed(6)} ${token}. Transaction reverted.`,
        });
    } catch (error) {
        res.status(500).json({ error: `Flash loan failed: ${error}` }); // Catch unexpected errors to prevent server crashes
    }
});

/**
 * GET /flash/history
 * Get flash loan execution history
 */
app.get('/flash/history', (_req: Request, res: Response) => {
    const successful = history.filter(h => h.status === 'success'); // Separate successes for profit calculations
    const failed = history.filter(h => h.status === 'failed'); // Separate failures for failure rate analysis
    const totalProfit = successful.reduce((sum, h) => sum + h.profit, 0); // Sum only successful profits
    const totalFees = history.reduce((sum, h) => sum + h.fee, 0); // Sum all fees paid across all attempts

    res.json({
        summary: {
            total: history.length,
            successful: successful.length,
            failed: failed.length,
            successRate: history.length > 0 ? `${((successful.length / history.length) * 100).toFixed(1)}%` : '0%', // Calculate success percentage
            totalProfit: parseFloat(totalProfit.toFixed(6)),
            totalFees: parseFloat(totalFees.toFixed(6)),
            netProfit: parseFloat((totalProfit - totalFees).toFixed(6)), // True net after all fees
        },
        history: history.map(h => ({
            id: h.id,
            token: h.token,
            amount: h.amount,
            fee: h.fee,
            profit: h.profit,
            strategy: h.strategy,
            status: h.status,
            executedAt: new Date(h.executedAt).toISOString(), // Convert timestamp to human-readable format
        })),
    });
});

/**
 * GET /flash/calculator
 * Calculate flash loan profitability
 */
app.get('/flash/calculator', (req: Request, res: Response) => {
    const { token, amount, expectedReturn, strategy } = req.query;
    const pool = pools.get(token as string);

    if (!pool) {
        return res.status(404).json({ error: 'Pool not found' });
    }

    const borrowAmount = parseFloat(amount as string) || 0; // Parse borrow amount from query
    const fee = borrowAmount * pool.fee; // Calculate fee based on pool rate
    const profit = parseFloat(expectedReturn as string) || 0; // Parse expected profit from query
    const net = profit - fee; // Determine if the strategy is viable after fees
    const roi = borrowAmount > 0 ? (net / borrowAmount) * 100 : 0; // Calculate return on borrowed capital

    const { actualProfit } = simulateStrategy(strategy as string || 'arbitrage', borrowAmount, pool.fee); // Show what the built-in simulator predicts

    res.json({
        calculation: {
            token,
            borrowAmount,
            fee: `${fee.toFixed(6)} ${token}`,
            feePercent: `${pool.fee * 100}%`,
            expectedProfit: profit,
            simulatedProfit: actualProfit,
            netProfit: net,
            profitable: net > 0,
            roi: `${roi.toFixed(4)}%`,
        },
        message: net > 0
            ? 'Strategy is profitable after flash loan fees'
            : 'Strategy is NOT profitable after flash loan fees',
    });
});

/**
 * GET /flash/strategies
 * List supported strategies
 */
app.get('/flash/strategies', (_req: Request, res: Response) => {
    const strategies = [
        { id: 'arbitrage', name: 'Cross-DEX Arbitrage', description: 'Buy low on one DEX, sell high on another', typicalProfit: '0.1%' },
        { id: 'liquidation', name: 'Liquidation Bonus', description: 'Repay undercollateralized debt, seize collateral', typicalProfit: '5%' },
        { id: 'collateral_swap', name: 'Collateral Swap', description: 'Swap collateral in lending position without closing', typicalProfit: '0.2%' },
        { id: 'triangular_arbitrage', name: 'Triangular Arbitrage', description: 'Exploit pricing across three trading pairs', typicalProfit: '0.08%' },
        { id: 'dex_rebalance', name: 'DEX Rebalance', description: 'Rebalance liquidity pools for incentives', typicalProfit: '0.15%' },
    ];

    res.json({ strategies });
});

app.listen(PORT, () => {
    console.log(`=== Phase 30: Flash Loan API ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /flash/pools         - Available pools`);
    console.log(`  POST /flash/pools         - Add/update pool`);
    console.log(`  POST /flash/execute       - Execute flash loan`);
    console.log(`  GET  /flash/history       - Execution history`);
    console.log(`  GET  /flash/calculator    - Profit calculator`);
    console.log(`  GET  /flash/strategies    - Supported strategies`);
    console.log(`\nFlash Loan Rules:`);
    console.log(`  1. Borrow any amount`);
    console.log(`  2. Use it in the same transaction`);
    console.log(`  3. Repay principal + fee`);
    console.log(`  4. If any step fails, entire transaction reverts`);
    console.log(`  5. No collateral required!`);
});
