import express, { Request, Response } from 'express';

/**
 * Phase 29: Strategy Builder API
 *
 * Allows users to construct, simulate, and compare custom DeFi strategies
 * by composing protocol interfaces permissionlessly. No API keys or
 * authorization required — anyone can build and test strategies.
 *
 * Run: npx ts-node src_web3/phase29/strategy_builder.ts
 */

const app = express(); // Initialize Express for the strategy builder service
app.use(express.json()); // Parse JSON bodies so clients can send custom strategy definitions

const PORT = 3014; // Separate port from the yield aggregator so each service scales independently

// ============================================================================
// TYPES
// ============================================================================
interface ProtocolAction {
    id: string; // Unique action identifier
    protocol: string; // Protocol name
    type: 'lending' | 'staking' | 'amm' | 'borrowing'; // Action category
    action: string; // Specific operation name
    apy: number; // Yield or cost as decimal
    risk: number; // 1-10 risk score
    inputToken: string; // Token required
    outputToken: string; // Token received
    fee: number; // Fee as decimal (e.g., 0.003 = 0.3%)
    lockupDays: number; // Days before funds can be withdrawn
    description: string; // Human-readable explanation
}

interface UserStrategy {
    id: string; // Unique strategy ID
    name: string; // User-defined name
    actions: string[]; // Ordered list of action IDs
    capital: number; // Starting capital in USD
    createdAt: number; // Timestamp
}

interface SimulationResult {
    strategyId: string; // Which strategy was simulated
    finalValue: number; // Portfolio value after all steps
    profit: number; // Absolute profit in USD
    roi: number; // Return on investment as decimal
    apy: number; // Annualized yield
    maxDrawdown: number; // Worst-case single-step loss
    riskScore: number; // Composite risk
    stepResults: StepResult[]; // Detailed per-step breakdown
}

interface StepResult {
    step: number; // Step index
    action: ProtocolAction; // Action details
    inputValue: number; // Value entering this step
    outputValue: number; // Value exiting this step
    feePaid: number; // Fees consumed
    daysLocked: number; // Lockup added
    notes: string; // Human-readable result
}

// ============================================================================
// PROTOCOL ACTION LIBRARY
// ============================================================================
const actionLibrary: ProtocolAction[] = [
    {
        id: 'solend_deposit_usdc',
        protocol: 'Solend',
        type: 'lending',
        action: 'deposit',
        apy: 0.034,
        risk: 3,
        inputToken: 'USDC',
        outputToken: 'cUSDC',
        fee: 0,
        lockupDays: 0,
        description: 'Deposit USDC into Solend lending pool to earn interest',
    },
    {
        id: 'solend_borrow_usdc',
        protocol: 'Solend',
        type: 'borrowing',
        action: 'borrow',
        apy: -0.08, // Negative because borrowing costs money
        risk: 4,
        inputToken: 'cUSDC',
        outputToken: 'USDC',
        fee: 0.001,
        lockupDays: 0,
        description: 'Borrow USDC against cUSDC collateral at 75% LTV',
    },
    {
        id: 'marinade_stake_sol',
        protocol: 'Marinade',
        type: 'staking',
        action: 'stake',
        apy: 0.068,
        risk: 2,
        inputToken: 'SOL',
        outputToken: 'mSOL',
        fee: 0,
        lockupDays: 0,
        description: 'Stake SOL through Marinade to receive liquid mSOL',
    },
    {
        id: 'orca_swap_sol_usdc',
        protocol: 'Orca',
        type: 'amm',
        action: 'swap',
        apy: 0,
        risk: 5,
        inputToken: 'SOL',
        outputToken: 'USDC',
        fee: 0.003,
        lockupDays: 0,
        description: 'Swap SOL for USDC on Orca AMM',
    },
    {
        id: 'orca_swap_usdc_sol',
        protocol: 'Orca',
        type: 'amm',
        action: 'swap',
        apy: 0,
        risk: 5,
        inputToken: 'USDC',
        outputToken: 'SOL',
        fee: 0.003,
        lockupDays: 0,
        description: 'Swap USDC for SOL on Orca AMM',
    },
    {
        id: 'raydium_lp_sol_usdc',
        protocol: 'Raydium',
        type: 'amm',
        action: 'addLiquidity',
        apy: 0.12,
        risk: 5,
        inputToken: 'SOL-USDC',
        outputToken: 'LP-SOL-USDC',
        fee: 0.001,
        lockupDays: 0,
        description: 'Provide SOL-USDC liquidity to Raydium and earn trading fees',
    },
    {
        id: 'tulip_vault_usdc',
        protocol: 'Tulip',
        type: 'lending',
        action: 'vaultDeposit',
        apy: 0.22,
        risk: 7,
        inputToken: 'USDC',
        outputToken: 'tvUSDC',
        fee: 0.001,
        lockupDays: 1,
        description: 'Deposit USDC into Tulip leveraged yield vault',
    },
    {
        id: 'mango_deposit_usdc',
        protocol: 'Mango',
        type: 'lending',
        action: 'deposit',
        apy: 0.041,
        risk: 4,
        inputToken: 'USDC',
        outputToken: 'mUSDC',
        fee: 0,
        lockupDays: 0,
        description: 'Deposit USDC into Mango Markets for lending yield',
    },
];

// ============================================================================
// USER STRATEGY STORAGE
// ============================================================================
const userStrategies: Map<string, UserStrategy> = new Map(); // Store strategies by ID for retrieval and simulation

// ============================================================================
// SIMULATION ENGINE
// ============================================================================

/**
 * Simulate a strategy by executing each action sequentially against the library.
 */
function simulateStrategy(strategy: UserStrategy): SimulationResult {
    let currentValue = strategy.capital; // Start with the user's initial capital
    let totalFees = 0; // Accumulate fees across all steps
    let maxLockup = 0; // Track the longest lockup period
    let maxRisk = 0; // Track the highest risk encountered
    let maxDrawdown = 0; // Track the worst single-step loss
    const stepResults: StepResult[] = [];

    for (let i = 0; i < strategy.actions.length; i++) {
        const actionId = strategy.actions[i]; // Get the action ID for this step
        const action = actionLibrary.find(a => a.id === actionId); // Resolve the action from the library

        if (!action) {
            stepResults.push({
                step: i + 1,
                action: {} as ProtocolAction,
                inputValue: currentValue,
                outputValue: currentValue,
                feePaid: 0,
                daysLocked: 0,
                notes: `Unknown action: ${actionId}`, // Flag invalid actions without crashing
            });
            continue;
        }

        const fee = currentValue * action.fee; // Calculate fee based on current portfolio value
        const netInput = currentValue - fee; // Deduct fee before applying yield
        const yieldAmount = netInput * action.apy; // Calculate yield or borrowing cost
        const outputValue = netInput + yieldAmount; // Apply the action's financial effect
        const stepDrawdown = currentValue - outputValue; // Calculate value change for this step

        totalFees += fee;
        currentValue = outputValue;
        maxRisk = Math.max(maxRisk, action.risk);
        maxLockup = Math.max(maxLockup, action.lockupDays);
        if (stepDrawdown > maxDrawdown) {
            maxDrawdown = stepDrawdown; // Update worst single-step loss
        }

        stepResults.push({
            step: i + 1,
            action,
            inputValue: parseFloat(currentValue.toFixed(6)),
            outputValue: parseFloat(outputValue.toFixed(6)),
            feePaid: parseFloat(fee.toFixed(6)),
            daysLocked: action.lockupDays,
            notes: `${action.protocol} ${action.action}: ${netInput.toFixed(4)} -> ${outputValue.toFixed(4)} ${action.outputToken}`,
        });
    }

    const profit = currentValue - strategy.capital; // Absolute profit in USD
    const roi = profit / strategy.capital; // Return on investment ratio
    const apy = roi; // Simplified: treat the simulation period as one year

    return {
        strategyId: strategy.id,
        finalValue: parseFloat(currentValue.toFixed(4)),
        profit: parseFloat(profit.toFixed(4)),
        roi: parseFloat(roi.toFixed(6)),
        apy: parseFloat(apy.toFixed(6)),
        maxDrawdown: parseFloat(maxDrawdown.toFixed(4)),
        riskScore: maxRisk,
        stepResults,
    };
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        actions: actionLibrary.length,
        strategies: userStrategies.size,
    });
});

/**
 * GET /actions
 * List all available protocol actions
 */
app.get('/actions', (req: Request, res: Response) => {
    const { type, token } = req.query; // Optional filters for action type and token
    let list = actionLibrary;

    if (type) {
        list = list.filter(a => a.type === type); // Filter by category
    }

    if (token) {
        list = list.filter(a => a.inputToken === token || a.outputToken === token); // Filter by token involvement
    }

    res.json({ count: list.length, actions: list });
});

/**
 * GET /actions/:id
 * Get a single action
 */
app.get('/actions/:id', (req: Request, res: Response) => {
    const action = actionLibrary.find(a => a.id === req.params.id); // Lookup by action ID
    if (!action) {
        return res.status(404).json({ error: 'Action not found' });
    }
    res.json({ action });
});

/**
 * POST /strategies
 * Create a custom strategy
 */
app.post('/strategies', (req: Request, res: Response) => {
    const { name, actions, capital } = req.body; // Extract strategy definition from request

    if (!name || !Array.isArray(actions) || actions.length === 0) {
        return res.status(400).json({ error: 'name and actions array are required' }); // Validate required fields
    }

    const id = `strat_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`; // Generate unique strategy ID
    const strategy: UserStrategy = {
        id,
        name,
        actions,
        capital: capital || 1000, // Default to $1000 if not specified
        createdAt: Date.now(),
    };

    userStrategies.set(id, strategy); // Persist the strategy for later simulation and retrieval
    res.status(201).json({ success: true, strategy });
});

/**
 * GET /strategies/:id
 * Get a saved strategy
 */
app.get('/strategies/:id', (req: Request, res: Response) => {
    const strategy = userStrategies.get(req.params.id); // Lookup by strategy ID
    if (!strategy) {
        return res.status(404).json({ error: 'Strategy not found' });
    }
    res.json({ strategy });
});

/**
 * POST /strategies/:id/simulate
 * Simulate a saved strategy
 */
app.post('/strategies/:id/simulate', (req: Request, res: Response) => {
    const strategy = userStrategies.get(req.params.id);
    if (!strategy) {
        return res.status(404).json({ error: 'Strategy not found' });
    }

    const result = simulateStrategy(strategy); // Run the simulation engine
    res.json({ result });
});

/**
 * POST /simulate/quick
 * Quick simulation without saving
 */
app.post('/simulate/quick', (req: Request, res: Response) => {
    const { name, actions, capital } = req.body; // Accept a temporary strategy for immediate simulation

    if (!Array.isArray(actions) || actions.length === 0) {
        return res.status(400).json({ error: 'actions array is required' });
    }

    const tempStrategy: UserStrategy = {
        id: `temp_${Date.now()}`,
        name: name || 'Quick Simulation',
        actions,
        capital: capital || 1000,
        createdAt: Date.now(),
    };

    const result = simulateStrategy(tempStrategy); // Run simulation without persisting
    res.json({ result });
});

/**
 * POST /compare
 * Compare multiple strategies side by side
 */
app.post('/compare', (req: Request, res: Response) => {
    const { strategies: strategyIds } = req.body; // Array of strategy IDs to compare

    if (!Array.isArray(strategyIds) || strategyIds.length < 2) {
        return res.status(400).json({ error: 'Provide at least 2 strategy IDs to compare' }); // Comparison needs multiple items
    }

    const results = strategyIds.map((id: string) => {
        const strategy = userStrategies.get(id);
        if (!strategy) {
            return { id, error: 'Strategy not found' }; // Gracefully handle missing strategies
        }
        return {
            id,
            name: strategy.name,
            ...simulateStrategy(strategy), // Expand simulation results inline
        };
    });

    res.json({ comparison: results });
});

app.listen(PORT, () => {
    console.log(`=== Phase 29: Strategy Builder API ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /actions              - List available protocol actions`);
    console.log(`  GET  /actions/:id          - Get action details`);
    console.log(`  POST /strategies           - Create a custom strategy`);
    console.log(`  GET  /strategies/:id       - Get saved strategy`);
    console.log(`  POST /strategies/:id/simulate - Simulate saved strategy`);
    console.log(`  POST /simulate/quick       - Quick simulation without saving`);
    console.log(`  POST /compare              - Compare multiple strategies`);
    console.log(`\nPermissionless: No API key required to build and test strategies`);
});
