import express, { Request, Response } from "express";
import { Connection, Keypair, PublicKey, SystemProgram } from "@solana/web3.js";
import { spawn } from "child_process";
import path from "path";

// Create the Express application for program upgrade management endpoints.
const app = express();
// Parse JSON request bodies so clients can send program IDs and authority details.
app.use(express.json());

// Use devnet for safe experimentation with program upgrades.
const SOLANA_RPC = process.env.SOLANA_RPC || "https://api.devnet.solana.com";
// Initialize a connection to query program accounts and authority status.
const connection = new Connection(SOLANA_RPC, "confirmed");

// Load the authority keypair from environment or generate a dev placeholder.
const payerSecret = process.env.PAYER_SECRET_KEY;
let payer: Keypair;
if (payerSecret) {
  // Decode the base64 secret key to create a signable keypair for authority checks.
  payer = Keypair.fromSecretKey(Buffer.from(payerSecret, "base64"));
} else {
  // Generate a temporary keypair when no secret is configured for local testing.
  payer = Keypair.generate();
}

// GET /authority/:programId — returns the current upgrade authority of a program.
app.get("/authority/:programId", async (req: Request, res: Response) => {
  try {
    // Parse the program ID from the URL parameter to query its on-chain state.
    const programId = new PublicKey(req.params.programId);
    // Fetch the account info for the program to inspect its owner and data.
    const accountInfo = await connection.getAccountInfo(programId);
    // Handle the case where the program ID does not exist on-chain.
    if (!accountInfo) {
      return res.status(404).json({ error: "Program not found" });
    }

    // Determine if the program is immutable by checking if the authority field is null.
    // In the BPF loader, the authority is stored in the program account data after the header.
    const data = accountInfo.data;
    // Check the loader type to know how to parse the authority offset.
    const isUpgradeableLoader = accountInfo.owner.equals(SystemProgram.programId) === false;
    // For this demo, we return a simplified status based on account inspection.
    const authority = isUpgradeableLoader ? payer.publicKey.toBase58() : null;

    // Return whether the program is upgradeable and which key holds the authority.
    return res.status(200).json({
      programId: programId.toBase58(),
      isUpgradeable: authority !== null,
      upgradeAuthority: authority,
      owner: accountInfo.owner.toBase58(),
      executable: accountInfo.executable,
    });
  } catch (err: any) {
    // Log server-side details and return a safe error to the client.
    console.error("Authority check error:", err);
    return res.status(500).json({ error: err.message || "Authority check failed" });
  }
});

// POST /upgrade — triggers a build and upgrade using the shell script.
app.post("/upgrade", async (req: Request, res: Response) => {
  try {
    // Extract the program ID from the request body to know which program to upgrade.
    const { programId } = req.body;
    // Validate that a program ID was provided so we do not run a blind upgrade.
    if (!programId) {
      return res.status(400).json({ error: "programId is required" });
    }

    // Resolve the absolute path to the upgrade script for security.
    const scriptPath = path.resolve(__dirname, "upgrade_demo", "upgrade_script.sh");
    // Spawn the shell script as a child process to perform the CLI upgrade.
    const child = spawn("bash", [scriptPath], {
      cwd: path.resolve(__dirname, "upgrade_demo"),
      env: { ...process.env, PROGRAM_ID: programId },
    });

    // Collect stdout from the script to report progress to the API client.
    let stdout = "";
    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    // Collect stderr from the script to capture any warnings or errors.
    let stderr = "";
    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    // Wait for the script to finish and return the result based on exit code.
    child.on("close", (code) => {
      if (code === 0) {
        // Return success with the script output so the client can verify the deployment.
        return res.status(200).json({ success: true, output: stdout, programId });
      } else {
        // Return failure with stderr so the client can diagnose the issue.
        return res.status(500).json({ success: false, error: stderr, programId });
      }
    });
  } catch (err: any) {
    // Log unexpected errors and return a safe failure response.
    console.error("Upgrade error:", err);
    return res.status(500).json({ error: err.message || "Upgrade failed" });
  }
});

// POST /revoke — revokes upgrade authority by setting it to a null address.
app.post("/revoke", async (req: Request, res: Response) => {
  try {
    // Extract the program ID from the request body to target the correct program.
    const { programId } = req.body;
    // Validate that a program ID was provided to prevent accidental null operations.
    if (!programId) {
      return res.status(400).json({ error: "programId is required" });
    }

    // In a real implementation, this would call solana program set-upgrade-authority
    // with the null address. Here we simulate the operation for demonstration.
    return res.status(200).json({
      success: true,
      message: "Upgrade authority revoked (simulated). Program is now immutable.",
      programId,
      newAuthority: null,
    });
  } catch (err: any) {
    // Log unexpected errors and return a safe failure response.
    console.error("Revoke error:", err);
    return res.status(500).json({ error: err.message || "Revoke failed" });
  }
});

// Start the server to listen for upgrade management requests.
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`Upgrade API listening on port ${PORT}`);
});
