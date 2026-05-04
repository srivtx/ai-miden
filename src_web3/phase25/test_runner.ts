import express, { Request, Response } from "express";
import { spawn } from "child_process";
import path from "path";

// Create the Express application to act as a test runner and reporting server.
const app = express();
// Parse JSON bodies so clients can request specific test suites or filter modes.
app.use(express.json());

// Define the root directory where Rust test files are located.
const TEST_ROOT = path.resolve(__dirname);

// POST /run — triggers cargo test and returns structured results.
app.post("/run", async (req: Request, res: Response) => {
  try {
    // Extract optional test filter from the request body to run specific tests.
    const { filter } = req.body;
    // Build the cargo test command arguments array.
    const args = ["test"];
    // If a filter is provided, append it to run only matching tests.
    if (filter) {
      args.push(filter);
    }
    // Add JSON output format so we can parse results programmatically.
    args.push("--", "--nocapture");

    // Spawn cargo test in the phase25 directory to execute the escrow test suite.
    const child = spawn("cargo", args, {
      cwd: TEST_ROOT,
      env: { ...process.env, RUST_BACKTRACE: "1" },
    });

    // Accumulate stdout lines to capture test output and pass/fail counts.
    let stdout = "";
    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    // Accumulate stderr lines to capture compilation errors or warnings.
    let stderr = "";
    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    // Wait for the cargo test process to exit and report results.
    child.on("close", (code) => {
      // Count passing tests by searching for the standard Rust "test result: ok" pattern.
      const passed = (stdout.match(/test result: ok/g) || []).length;
      // Count failing tests by searching for the standard Rust "test result: FAILED" pattern.
      const failed = (stdout.match(/test result: FAILED/g) || []).length;
      // Extract individual test names from output lines for detailed reporting.
      const testLines = stdout.split("\n").filter((line) => line.trim().startsWith("test "));

      // Build the response object with summary and raw output.
      const result = {
        success: code === 0,
        exitCode: code,
        summary: {
          passed,
          failed,
          total: passed + failed,
        },
        tests: testLines.map((line) => {
          // Parse each line to determine if the individual test passed or failed.
          const status = line.includes("... ok") ? "passed" : line.includes("... FAILED") ? "failed" : "unknown";
          // Extract the test name by removing the prefix and suffix.
          const name = line.replace("test ", "").replace(" ... ok", "").replace(" ... FAILED", "").trim();
          return { name, status };
        }),
        stdout,
        stderr,
      };

      // Return HTTP 200 if tests passed, or 500 if there were failures.
      return res.status(code === 0 ? 200 : 500).json(result);
    });
  } catch (err: any) {
    // Log server-side errors and return a safe failure message to the client.
    console.error("Test run error:", err);
    return res.status(500).json({ error: err.message || "Test run failed" });
  }
});

// GET /report — returns a human-readable summary of the last test run.
app.get("/report", (_req: Request, res: Response) => {
  // Return instructions on how to generate a report since we do not persist state.
  return res.status(200).json({
    message: "Use POST /run to execute tests and generate a report.",
    endpoints: {
      runAll: "POST /run",
      runUnit: "POST /run with body { filter: 'unit_tests' }",
      runIntegration: "POST /run with body { filter: 'integration_tests' }",
      runFuzz: "POST /run with body { filter: 'fuzzing_tests' }",
    },
    tips: [
      "Unit tests verify individual functions in isolation.",
      "Integration tests verify multi-instruction workflows.",
      "Fuzzing tests verify stability under random inputs.",
    ],
  });
});

// POST /fuzz — triggers a longer fuzzing run with many iterations.
app.post("/fuzz", async (req: Request, res: Response) => {
  try {
    // Extract optional iteration count from the request body.
    const { iterations = 10000 } = req.body;
    // Build the cargo test command to run only fuzzing tests with extended iterations.
    const args = ["test", "fuzzing_tests", "--", "--nocapture"];

    // Set an environment variable to inform the Rust tests how many iterations to run.
    const child = spawn("cargo", args, {
      cwd: TEST_ROOT,
      env: { ...process.env, FUZZ_ITERATIONS: String(iterations) },
    });

    // Collect stdout to parse fuzzing results and any crashes.
    let stdout = "";
    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    // Collect stderr to capture Rust panics or assertion failures.
    let stderr = "";
    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    // Wait for the fuzzing run to complete and report findings.
    child.on("close", (code) => {
      return res.status(code === 0 ? 200 : 500).json({
        success: code === 0,
        iterations,
        stdout,
        stderr,
        message: code === 0 ? "Fuzzing completed without crashes." : "Fuzzing found crashes or failures.",
      });
    });
  } catch (err: any) {
    // Log errors and return a concise failure message.
    console.error("Fuzz run error:", err);
    return res.status(500).json({ error: err.message || "Fuzz run failed" });
  }
});

// Start the server to listen for test runner requests.
const PORT = process.env.PORT || 3004;
app.listen(PORT, () => {
  console.log(`Test Runner API listening on port ${PORT}`);
});
