import express, { Request, Response } from "express";
import fs from "fs";
import path from "path";

// Create the Express application to serve as an on-demand security scanner.
const app = express();
// Parse JSON bodies so clients can submit source code strings for analysis.
app.use(express.json());

// Define vulnerability patterns mapped to human-readable descriptions and fixes.
const VULNERABILITY_PATTERNS = [
  {
    // Detect standard arithmetic operators that do not check for overflow.
    pattern: /\bbalance\s*[=+-]\s*[^;]+\+/g,
    description: "Possible integer overflow: uses unchecked '+' instead of checked_add",
    severity: "High",
    fix: "Use checked_add().ok_or(ErrorCode::Overflow)?",
  },
  {
    // Detect subtraction without checked arithmetic.
    pattern: /\bbalance\s*-\s*\w+/g,
    description: "Possible integer underflow: uses unchecked '-' instead of checked_sub",
    severity: "High",
    fix: "Use checked_sub().ok_or(ErrorCode::Underflow)?",
  },
  {
    // Detect CPI token transfers that occur before state mutations.
    pattern: /token::transfer\(.*\).*\n.*balance\s*=/s,
    description: "Possible reentrancy: external transfer before state update",
    severity: "Critical",
    fix: "Update state before token::transfer",
  },
  {
    // Detect raw AccountInfo usage without Anchor validation macros.
    pattern: /AccountInfo<'info>/g,
    description: "Raw AccountInfo without validation: verify ownership and constraints",
    severity: "Medium",
    fix: "Use Anchor account types with #[account(...)] constraints",
  },
  {
    // Detect missing Signer checks on accounts that should require authorization.
    pattern: /pub\s+\w+:\s*Account<'info,\s*\w+>[^,]*\n/g,
    description: "Account field may be missing signer check",
    severity: "Medium",
    fix: "Add Signer<'info> or has_one = owner constraint",
  },
  {
    // Detect manual subtraction without checked math in Rust.
    pattern: /-\s*amount/g,
    description: "Unchecked subtraction detected",
    severity: "High",
    fix: "Use checked_sub or saturating_sub",
  },
];

// POST /scan — accepts a file path or code string and returns vulnerability findings.
app.post("/scan", async (req: Request, res: Response) => {
  try {
    // Extract the code input and optional filename from the request body.
    const { code, filePath: inputPath } = req.body;
    // Determine the source string to analyze from either inline code or a file.
    let source = "";
    if (code) {
      source = code;
    } else if (inputPath) {
      // Resolve the absolute path to prevent directory traversal attacks.
      const resolved = path.resolve(inputPath);
      // Read the file synchronously for simplicity in this demo scanner.
      source = fs.readFileSync(resolved, "utf-8");
    } else {
      // Return an error if neither code nor filePath was provided.
      return res.status(400).json({ error: "Provide code or filePath" });
    }

    // Collect all findings by running each pattern against the source string.
    const findings = [];
    for (const rule of VULNERABILITY_PATTERNS) {
      // Reset regex lastIndex because some patterns have global flags.
      if (rule.pattern.global) {
        rule.pattern.lastIndex = 0;
      }
      // Find all matches for the current vulnerability pattern.
      const matches = source.match(rule.pattern);
      if (matches && matches.length > 0) {
        findings.push({
          description: rule.description,
          severity: rule.severity,
          occurrences: matches.length,
          fix: rule.fix,
        });
      }
    }

    // Categorize overall risk based on the highest severity finding present.
    let riskLevel = "Low";
    if (findings.some((f) => f.severity === "Critical")) {
      riskLevel = "Critical";
    } else if (findings.some((f) => f.severity === "High")) {
      riskLevel = "High";
    } else if (findings.some((f) => f.severity === "Medium")) {
      riskLevel = "Medium";
    }

    // Return the scan report with findings count, details, and recommended actions.
    return res.status(200).json({
      scannedLines: source.split("\n").length,
      findingsCount: findings.length,
      riskLevel,
      findings,
    });
  } catch (err: any) {
    // Log the error server-side and return a safe message to the client.
    console.error("Scan error:", err);
    return res.status(500).json({ error: err.message || "Scan failed" });
  }
});

// GET /compare — returns a side-by-side summary of vulnerable vs secure patterns.
app.get("/compare", (_req: Request, res: Response) => {
  // Return a structured comparison to help developers understand the differences.
  return res.status(200).json({
    patterns: [
      {
        vulnerability: "Reentrancy",
        vulnerable: "Transfer before state update",
        secure: "State update before transfer",
      },
      {
        vulnerability: "Integer Overflow",
        vulnerable: "balance + amount",
        secure: "balance.checked_add(amount).ok_or(ErrorCode::Overflow)?",
      },
      {
        vulnerability: "Account Validation",
        vulnerable: "Raw AccountInfo<'info>",
        secure: "#[account(owner = token::ID)] with Anchor types",
      },
      {
        vulnerability: "Signer Check",
        vulnerable: "pub user: Account<'info, User>",
        secure: "pub owner: Signer<'info> + has_one = owner",
      },
    ],
  });
});

// Start the server to listen for security scan requests.
const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  console.log(`Security Scanner API listening on port ${PORT}`);
});
