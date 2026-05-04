import express, { Request, Response } from 'express';

/**
 * Phase 29: Yield Aggregator API
 *
 * Express API that composes multiple DeFi protocols (staking, lending, AMM)
 * to calculate combined yields, compare strategies, and simulate multi-step
 * investment flows without requiring separate transactions for each step.
 *
 * Run: npx ts-node src_web3/phase29/yield_aggregator.ts
 */

const app = express(); // Initialize Express to serve yield calculation endpoints
app.use(express.json()); // Parse JSON bodies so clients can send strategy parameters

const PORT = 3013; // Dedicated port for the yield aggregator service

// ============================================================================
// TYPES
// ============================================================================
interface Protocol {
    id: string; // Unique protocol identifier for routing and display
    name: string; // Human-readable name
    type: 'lending' | 'staking' | 'amm' | 'vault'; // Category for filtering and composition logic
    apy: number; // Annual percentage yield as a decimal (0.05 = 5%)
    tvl: number; // Total value locked in USD for liquidity assessment
    riskScore: number; // 1-10 scale where 10 is highest risk
    token: string; // Primary token accepted by the protocol
}

interface LendingInterface {
    deposit: (amount: number, token: string) => { receiptTokens: number; apy: number }; // Simulate deposit and return yield-bearing receipt tokens
    withdraw: (receiptTokens: number, token: string) => { principal: number; yield: number }; // Simulate withdrawal with accrued interest
    getCollateralFactor: (token: string) => number; // Loan-to-value ratio for borrowing against deposits
}

interface StakingInterface {
    stake: (amount: number, token: string) => { stakedAmount: number; rewardsPerDay: number }; // Simulate staking and daily reward accrual
    unstake: (amount: number) => { principal: number; rewards: number }; // Simulate unstaking with accumulated rewards
    lockupPeriod: number; // Days before unstaking is allowed
}

interface AMMInterface {
    swap: (amountIn: number, tokenIn: string, tokenOut: string) => { amountOut: number; fee: number }; // Simulate token swap with slippage and fees
    getPrice: (tokenIn: string, tokenOut: string) => number; // Current exchange rate between two tokens
    getLiquidity: (pair: string) => number; // Total liquidity in the trading pair
}

interface YieldStrategy {
    id: string; // Unique strategy identifier
    name: string; // Display name
    steps: StrategyStep[]; // Ordered list of protocol interactions
    totalApy: number; // Combined annual yield
    totalRisk: number; // Aggregate risk score
    minInvestment: number; // Minimum capital required
    tokens: string[]; // Tokens involved
}

interface StrategyStep {
    protocolId: string; // Which protocol to interact with
    action: string; // deposit, stake, swap, borrow, etc.
    amount: number; // Capital allocated to this step
    token: string; // Token used in this step
    expectedOutput: number; // Projected result of this step
}

// ============================================================================
// MOCK PROTOCOLS
// ============================================================================
const protocols: Protocol[] = [
    { id: 'solend', name: 'Solend', type: 'lending', apy: 0.034, tvl: 450000000, riskScore: 3, token: 'USDC' },
    { id: 'mango', name: 'Mango Markets', type: 'lending', apy: 0.041, tvl: 120000000, riskScore: 4, token: 'USDC' },
    { id: 'marinade', name: 'Marinade', type: 'staking', apy: 0.068, tvl: 800000000, riskScore: 2, token: 'SOL' },
    { id: 'lido', name: 'Lido', type: 'staking', apy: 0.055, tvl: 600000000, riskScore: 2, token: 'SOL' },
    { id: 'raydium', name: 'Raydium', type: 'amm', apy: 0.12, tvl: 200000000, riskScore: 5, token: 'SOL-USDC' },
    { id: 'orca', name: 'Orca', type: 'amm', apy: 0.15, tvl: 180000000, riskScore: 5, token: 'SOL-USDC' },
    { id: 'tulip', name: 'Tulip Vault', type: 'vault', apy: 0.22, tvl: 50000000, riskScore: 7, token: 'USDC' },
];

// ============================================================================
// PROTOCOL IMPLEMENTATIONS
// ============================================================================

const lendingImpl: LendingInterface = {
    deposit: (amount: number, _token: string) => ({
        receiptTokens: amount, // 1:1 for simplicity; real protocols use exchange rates
        apy: 0.04, // 4% base lending APY
    }),
    withdraw: (receiptTokens: number, _token: string) => ({
        principal: receiptTokens,
        yield: receiptTokens * 0.04, // Accrued interest over one year
    }),
    getCollateralFactor: (_token: string) => 0.75, // 75% loan-to-value ratio
};

const stakingImpl: StakingInterface = {
    stake: (amount: number, _token: string) => ({
        stakedAmount: amount,
        rewardsPerDay: (amount * 0.06) / 365, // 6% APY distributed daily
    }),
    unstake: (amount: number) => ({
        principal: amount,
        rewards: amount * 0.06, // One year of rewards
    }),
    lockupPeriod: 2, // 2-day lockup for unstaking
};

const ammImpl: AMMInterface = {
    swap: (amountIn: number, _tokenIn: string, _tokenOut: string) => ({
        amountOut: amountIn * 0.997, // 0.3% swap fee deducted
        fee: amountIn * 0.003,
    }),
    getPrice: (_tokenIn: string, _tokenOut: string) => 22.5, // Mock SOL/USDC price
    getLiquidity: (_pair: string) => 50000000, // $50M mock liquidity
};

// ============================================================================
// STRATEGY ENGINE
// ============================================================================

/**
 * Calculate combined APY for a multi-step strategy.
 */
function calculateStrategyYield(steps: StrategyStep[]): { totalApy: number; totalRisk: number } {
    let compoundedValue = 1; // Start with 1 unit of capital for percentage math
    let maxRisk = 0; // Track the highest risk in the chain since risk is not averaged

    for (const step of steps) {
        const protocol = protocols.find(p => p.id === step.protocolId); // Look up protocol metadata
        if (!protocol) continue;

        const stepYield = 1 + protocol.apy; // Convert APY to multiplier (e.g., 5% -> 1.05)
        compoundedValue *= stepYield; // Compound yields across steps
        maxRisk = Math.max(maxRisk, protocol.riskScore); // Risk is determined by the weakest link
    }

    const totalApy = compoundedValue - 1; // Convert multiplier back to percentage
    return { totalApy, totalRisk: maxRisk };
}

// ============================================================================
// PRE-BUILT STRATEGIES
// ============================================================================
const strategies: YieldStrategy[] = [
    {
        id: 'conservative_lend',
        name: 'Conservative Lending',
        steps: [
            { protocolId: 'solend', action: 'deposit', amount: 100, token: 'USDC', expectedOutput: 104 },
        ],
        totalApy: 0.034,
        totalRisk: 3,
        minInvestment: 10,
        tokens: ['USDC'],
    },
    {
        id: 'sol_stake',
        name: 'SOL Staking',
        steps: [
            { protocolId: 'marinade', action: 'stake', amount: 100, token: 'SOL', expectedOutput: 106.8 },
        ],
        totalApy: 0.068,
        totalRisk: 2,
        minInvestment: 1,
        tokens: ['SOL'],
    },
    {
        id: 'yield_loop',
        name: 'Leveraged Yield Loop',
        steps: [
            { protocolId: 'solend', action: 'deposit', amount: 100, token: 'USDC', expectedOutput: 100 },
            { protocolId: 'solend', action: 'borrow', amount: 75, token: 'USDC', expectedOutput: 75 },
            { protocolId: 'tulip', action: 'deposit', amount: 175, token: 'USDC', expectedOutput: 213 },
        ],
        totalApy: 0.28,
        totalRisk: 7,
        minInvestment: 100,
        tokens: ['USDC'],
    },
    {
        id: 'lp_farm',
        name: 'Liquidity Provider Farm',
        steps: [
            { protocolId: 'orca', action: 'swap', amount: 50, token: 'SOL', expectedOutput: 1125 },
            { protocolId: 'orca', action: 'addLiquidity', amount: 2250, token: 'SOL-USDC', expectedOutput: 2000 },
        ],
        totalApy: 0.15,
        totalRisk: 5,
        minInvestment: 100,
        tokens: ['SOL', 'USDC'],
    },
];

// Recalculate totals for consistency
for (const s of strategies) {
    const calc = calculateStrategyYield(s.steps); // Ensure stored totals match the calculation engine
    s.totalApy = calc.totalApy;
    s.totalRisk = calc.totalRisk;
}

// ============================================================================
// ROUTES
// ============================================================================

app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        protocols: protocols.length,
        strategies: strategies.length,
    });
});

/**
 * GET /protocols
 * List available protocols
 */
app.get('/protocols', (req: Request, res: Response) => {
    const { type } = req.query; // Optional filter by protocol type
    let list = protocols;
    if (type) {
        list = protocols.filter(p => p.type === type); // Filter if a type parameter was provided
    }
    res.json({ count: list.length, protocols: list });
});

/**
 * GET /protocols/:id
 * Get a single protocol
 */
app.get('/protocols/:id', (req: Request, res: Response) => {
    const protocol = protocols.find(p => p.id === req.params.id); // Lookup by protocol ID
    if (!protocol) {
        return res.status(404).json({ error: 'Protocol not found' });
    }
    res.json({ protocol });
});

/**
 * GET /strategies
 * List pre-built strategies
 */
app.get('/strategies', (req: Request, res: Response) => {
    const { maxRisk, token } = req.query; // Optional filters for risk tolerance and token preference
    let list = strategies;

    if (maxRisk) {
        list = list.filter(s => s.totalRisk <= parseInt(maxRisk as string, 10)); // Filter by maximum acceptable risk
    }

    if (token) {
        list = list.filter(s => s.tokens.includes(token as string)); // Only show strategies using the requested token
    }

    res.json({ count: list.length, strategies: list });
});

/**
 * GET /strategies/:id
 * Get a single strategy
 */
app.get('/strategies/:id', (req: Request, res: Response) => {
    const strategy = strategies.find(s => s.id === req.params.id);
    if (!strategy) {
        return res.status(404).json({ error: 'Strategy not found' });
    }
    res.json({ strategy });
});

/**
 * POST /simulate
 * Simulate a custom strategy
 */
app.post('/simulate', (req: Request, res: Response) => {
    const { steps, initialCapital } = req.body; // Extract the proposed steps and starting capital

    if (!Array.isArray(steps) || steps.length === 0) {
        return res.status(400).json({ error: 'steps array is required' }); // Reject empty strategies
    }

    const calc = calculateStrategyYield(steps); // Run the yield calculation engine
    const projectedValue = (initialCapital || 100) * (1 + calc.totalApy); // Project final value based on initial capital

    res.json({
        initialCapital: initialCapital || 100,
        projectedValue: parseFloat(projectedValue.toFixed(4)), // Round to 4 decimals for readability
        totalApy: `${(calc.totalApy * 100).toFixed(2)}%`, // Convert to percentage string
        totalRisk: calc.totalRisk,
        steps: steps.map((s: StrategyStep, i: number) => ({
            step: i + 1, // Number steps for human readability
            ...s,
        })),
    });
});

/**
 * POST /compose
 * Compose a transaction plan for a strategy
 */
app.post('/compose', (req: Request, res: Response) => {
    const { strategyId, capital } = req.body; // Which strategy to execute and with how much capital
    const strategy = strategies.find(s => s.id === strategyId);

    if (!strategy) {
        return res.status(404).json({ error: 'Strategy not found' });
    }

    if (capital < strategy.minInvestment) {
        return res.status(400).json({ error: `Minimum investment is ${strategy.minInvestment}` }); // Enforce capital requirements
    }

    const plan = strategy.steps.map((step, i) => {
        const protocol = protocols.find(p => p.id === step.protocolId); // Resolve protocol metadata for each step
        const scaledAmount = (step.amount / 100) * capital; // Scale the step amount proportionally to the actual capital
        return {
            step: i + 1,
            protocol: protocol?.name || step.protocolId,
            action: step.action,
            inputAmount: parseFloat(scaledAmount.toFixed(6)),
            inputToken: step.token,
            notes: `Call ${step.action} on ${protocol?.name} with ${scaledAmount.toFixed(4)} ${step.token}`, // Human-readable description
        };
    });

    res.json({
        strategy: strategy.name,
        capital,
        expectedApy: `${(strategy.totalApy * 100).toFixed(2)}%`,
        riskScore: strategy.totalRisk,
        steps: plan,
        atomic: true, // Indicate that all steps execute in one transaction on Solana
    });
});

app.listen(PORT, () => {
    console.log(`=== Phase 29: Yield Aggregator API ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /protocols              - List available protocols`);
    console.log(`  GET  /protocols/:id          - Get protocol details`);
    console.log(`  GET  /strategies             - List yield strategies`);
    console.log(`  GET  /strategies/:id         - Get strategy details`);
    console.log(`  POST /simulate               - Simulate custom strategy yield`);
    console.log(`  POST /compose                - Build transaction plan for strategy`);
    console.log(`\nComposability: All strategies execute atomically on Solana`);
});
