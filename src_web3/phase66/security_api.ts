import express, { Request, Response } from "express"; // WHY: Importing express framework and HTTP request/response types
import bodyParser from "body-parser"; // WHY: Importing middleware to parse JSON request bodies

const app = express(); // WHY: Creating the Express application instance
const PORT = 3074; // WHY: Binding the API to port 3074 as specified in requirements

app.use(bodyParser.json()); // WHY: Enabling JSON body parsing for incoming POST requests

app.get("/vulnerabilities", (req: Request, res: Response) => { // WHY: Defining GET route to list common vulnerability patterns
  const patterns = [ // WHY: Array storing documented vulnerability patterns for Solana/Anchor
    { id: "arbitrary-cpi", name: "Arbitrary CPI", severity: "Critical" }, // WHY: Documenting arbitrary cross-program invocation vulnerability
    { id: "closed-account-reuse", name: "Closed Account Reuse", severity: "High" }, // WHY: Documenting account reuse after improper closure
    { id: "pda-canonicalization", name: "PDA Canonicalization Failure", severity: "High" }, // WHY: Documenting non-canonical program derived address attacks
    { id: "missing-owner-check", name: "Missing Owner Check", severity: "Critical" }, // WHY: Documenting missing account ownership validation
    { id: "signer-auth", name: "Signer Authorization Bypass", severity: "Critical" }, // WHY: Documenting signature verification failures
    { id: "integer-overflow", name: "Integer Overflow", severity: "Medium" }, // WHY: Documenting arithmetic overflow vulnerabilities
    { id: "account-discriminator", name: "Account Discriminator Collision", severity: "High" }, // WHY: Documenting discriminator-related deserialization issues
    { id: "rent-exemption", name: "Rent Exemption Violation", severity: "Medium" }, // WHY: Documenting insufficient rent exemption problems
    { id: "reentrancy", name: "Reentrancy", severity: "High" }, // WHY: Documenting reentrant call vulnerabilities
    { id: "seed-auth", name: "Seed Authority Confusion", severity: "High" }, // WHY: Documenting seed-based authority confusion bugs
  ]; // WHY: Closing vulnerabilities array
  res.json({ patterns }); // WHY: Returning the vulnerability list as a JSON response
}); // WHY: Closing GET /vulnerabilities route handler

app.post("/audit", (req: Request, res: Response) => { // WHY: Defining POST route to accept program source for automated audit
  const { source } = req.body; // WHY: Extracting the source field from the JSON request body
  if (!source || typeof source !== "string") { // WHY: Validating that source is provided and is a string type
    return res.status(400).json({ error: "Source must be a string" }); // WHY: Returning 400 error for invalid input format
  } // WHY: Closing input validation block
  const findings: Array<{ check: string; status: string; detail: string }> = []; // WHY: Initializing array to accumulate audit findings
  if (source.includes("invoke") && !source.includes("program_id")) { // WHY: Heuristic detecting CPI calls without program ID validation
    findings.push({ // WHY: Adding a new finding to the results array
      check: "CPI Validation", // WHY: Labeling the category of the finding
      status: "fail", // WHY: Marking the check as failed
      detail: "CPI call may lack program ID whitelist check", // WHY: Describing the potential arbitrary CPI vulnerability
    }); // WHY: Closing push for CPI finding
  } // WHY: Closing CPI heuristic check
  if (source.includes("close") && !source.includes("CLOSED_ACCOUNT_DISCRIMINATOR")) { // WHY: Heuristic detecting close operations without discriminator invalidation
    findings.push({ // WHY: Adding a new finding to the results array
      check: "Closed Account Handling", // WHY: Labeling the category of the finding
      status: "fail", // WHY: Marking the check as failed
      detail: "Close operation may not prevent account reuse", // WHY: Describing the potential closed account reuse vulnerability
    }); // WHY: Closing push for closed account finding
  } // WHY: Closing closed account heuristic check
  if (source.includes("create_program_address") && !source.includes("find_program_address")) { // WHY: Heuristic detecting non-canonical PDA derivation
    findings.push({ // WHY: Adding a new finding to the results array
      check: "PDA Canonicalization", // WHY: Labeling the category of the finding
      status: "fail", // WHY: Marking the check as failed
      detail: "Using create_program_address without canonical bump validation", // WHY: Describing the potential PDA canonicalization bug
    }); // WHY: Closing push for PDA finding
  } // WHY: Closing PDA heuristic check
  if (findings.length === 0) { // WHY: Checking if any security findings were detected
    findings.push({ // WHY: Adding a default passing result when no issues are found
      check: "General", // WHY: Labeling the general audit status
      status: "pass", // WHY: Marking the overall audit as passed
      detail: "No obvious issues detected by automated heuristics", // WHY: Describing the clean scan result
    }); // WHY: Closing push for general passing result
  } // WHY: Closing empty findings check
  res.json({ findings, sourceLength: source.length }); // WHY: Returning audit results with source length metadata
}); // WHY: Closing POST /audit route handler

app.get("/secure-patterns", (req: Request, res: Response) => { // WHY: Defining GET route to return secure code examples
  const examples = { // WHY: Object containing secure implementations for side-by-side comparison
    arbitraryCpi: { // WHY: Secure arbitrary CPI mitigation example
      pattern: "Whitelist program ID before CPI", // WHY: Describing the secure pattern
      code: "require!(WHITELIST.contains(&target.key()), ErrorCode::NotWhitelisted); invoke(&ix, &accounts)?;", // WHY: Showing validation before invocation
    }, // WHY: Closing arbitrary CPI example
    closedAccount: { // WHY: Secure closed account handling example
      pattern: "Use Anchor close constraint or set CLOSED_ACCOUNT_DISCRIMINATOR", // WHY: Describing the secure pattern
      code: '#[account(close = signer)] or account.discriminator = CLOSED_ACCOUNT_DISCRIMINATOR', // WHY: Showing proper account closure
    }, // WHY: Closing closed account example
    pdaCanonical: { // WHY: Secure PDA canonicalization example
      pattern: "Use find_program_address and validate canonical bump", // WHY: Describing the secure pattern
      code: "let (pda, bump) = Pubkey::find_program_address(seeds, program_id); require_eq!(provided_bump, bump);", // WHY: Showing canonical PDA validation
    }, // WHY: Closing PDA canonicalization example
  }; // WHY: Closing examples object
  res.json({ examples }); // WHY: Returning secure patterns as a JSON response
}); // WHY: Closing GET /secure-patterns route handler

app.listen(PORT, () => { // WHY: Starting the Express server on the specified port
  console.log(`Security API running on port ${PORT}`); // WHY: Logging successful server startup
}); // WHY: Closing server initialization callback
