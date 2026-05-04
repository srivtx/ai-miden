import * as anchor from "@coral-xyz/anchor";           // WHY: Imports the Anchor TypeScript client library for interacting with Solana programs.
import { Program } from "@coral-xyz/anchor";            // WHY: Imports the Program class which provides typed methods based on the IDL.
import { Counter } from "../target/types/counter";      // WHY: Imports the generated TypeScript types from the IDL for compile-time type safety.
import { expect } from "chai";                          // WHY: Imports the assertion library used to verify test outcomes.

describe("counter", () => {                             // WHY: Groups all counter program tests into a single Mocha test suite.
  const provider = anchor.AnchorProvider.env();         // WHY: Creates a provider from environment variables connecting to the cluster and wallet.
  anchor.setProvider(provider);                         // WHY: Registers the provider as the default so program instances use it automatically.

  const program = anchor.workspace.Counter as Program<Counter>; // WHY: Loads the compiled Counter program from the Anchor workspace with full IDL typing.

  it("Initializes the counter", async () => {           // WHY: Defines a test case that verifies the counter account can be created and initialized.
    const payer = provider.wallet.publicKey;            // WHY: Gets the public key of the test wallet which will pay for account creation and sign transactions.

    const [counterPda] = anchor.web3.PublicKey.findProgramAddressSync( // WHY: Derives the PDA off-chain using the same seeds as the program to know the target address.
      [Buffer.from("counter"), payer.toBuffer()],       // WHY: Uses the static seed and payer buffer to match the seeds array in the Rust program exactly.
      program.programId                                 // WHY: Provides the program ID so the PDA is derived from this specific program's address space.
    );

    await program.methods                                 // WHY: Starts building a transaction by selecting an instruction method from the IDL-typed program.
      .initialize()                                       // WHY: Selects the initialize instruction which requires no arguments beyond the accounts.
      .accounts({                                         // WHY: Begins the accounts object that maps account names to their public keys for the transaction.
        counter: counterPda,                              // WHY: Passes the derived PDA as the counter account so the program can create it at this address.
        payer: payer,                                     // WHY: Passes the payer public key so Anchor knows who funds the account creation and signs.
        systemProgram: anchor.web3.SystemProgram.programId, // WHY: Passes the System Program ID which Anchor needs to create the counter account on-chain.
      })
      .rpc();                                             // WHY: Sends the transaction to the RPC node and waits for confirmation, returning the signature.

    const account = await program.account.counterAccount.fetch(counterPda); // WHY: Fetches the on-chain account data at the PDA to verify initialization succeeded.
    expect(account.count.toNumber()).to.equal(0);         // WHY: Asserts that the count is zero because the initialize handler sets it to zero.
    expect(account.bump).to.exist;                        // WHY: Asserts that the bump seed was stored in the account data for future PDA verification.
  });

  it("Increments the counter", async () => {             // WHY: Defines a test case that verifies the increment instruction increases the count by one.
    const payer = provider.wallet.publicKey;             // WHY: Reuses the same payer so the PDA derivation matches the initialized counter account.

    const [counterPda] = anchor.web3.PublicKey.findProgramAddressSync( // WHY: Re-derives the PDA off-chain to target the existing counter account.
      [Buffer.from("counter"), payer.toBuffer()],        // WHY: Uses identical seeds to the initialize test so the derived address is the same.
      program.programId                                  // WHY: Uses the same program ID to ensure the PDA is in the correct address space.
    );

    await program.methods                                 // WHY: Starts building the increment instruction transaction.
      .increment()                                        // WHY: Selects the increment instruction which takes no arguments.
      .accounts({                                         // WHY: Begins mapping account names to public keys for the increment instruction.
        counter: counterPda,                              // WHY: Targets the existing counter PDA so the program increments the correct account.
        payer: payer,                                     // WHY: Passes the payer as the signer because the Update context requires a signer.
      })
      .rpc();                                             // WHY: Sends the increment transaction and waits for on-chain confirmation.

    const account = await program.account.counterAccount.fetch(counterPda); // WHY: Fetches the updated account data to verify the increment took effect.
    expect(account.count.toNumber()).to.equal(1);         // WHY: Asserts the count is now one because increment added one to the initial value of zero.
  });

  it("Decrements the counter", async () => {             // WHY: Defines a test case that verifies the decrement instruction decreases the count by one.
    const payer = provider.wallet.publicKey;             // WHY: Reuses the same payer to ensure we operate on the same PDA created in the previous test.

    const [counterPda] = anchor.web3.PublicKey.findProgramAddressSync( // WHY: Derives the same PDA again because tests must independently resolve account addresses.
      [Buffer.from("counter"), payer.toBuffer()],        // WHY: Uses the same seed pattern so the address matches the initialized counter account.
      program.programId                                  // WHY: Uses the program ID to derive the address from the correct program.
    );

    await program.methods                                 // WHY: Starts building the decrement instruction transaction.
      .decrement()                                        // WHY: Selects the decrement instruction which takes no arguments.
      .accounts({                                         // WHY: Begins mapping account names to public keys for the decrement instruction.
        counter: counterPda,                              // WHY: Targets the existing counter PDA so the program decrements the correct account.
        payer: payer,                                     // WHY: Passes the payer as the signer because the Update context requires a signer.
      })
      .rpc();                                             // WHY: Sends the decrement transaction and waits for on-chain confirmation.

    const account = await program.account.counterAccount.fetch(counterPda); // WHY: Fetches the updated account data to verify the decrement took effect.
    expect(account.count.toNumber()).to.equal(0);         // WHY: Asserts the count is back to zero because decrement subtracted one from the previous value of one.
  });

  it("Closes the counter", async () => {                 // WHY: Defines a test case that verifies the close instruction destroys the counter account.
    const payer = provider.wallet.publicKey;             // WHY: Reuses the same payer because only the original creator should be able to close their counter.

    const [counterPda] = anchor.web3.PublicKey.findProgramAddressSync( // WHY: Derives the PDA one final time to identify the account to be closed.
      [Buffer.from("counter"), payer.toBuffer()],        // WHY: Uses the same seed pattern to target the correct counter account.
      program.programId                                  // WHY: Uses the program ID for consistent PDA derivation.
    );

    await program.methods                                 // WHY: Starts building the close instruction transaction.
      .close()                                            // WHY: Selects the close instruction which takes no arguments.
      .accounts({                                         // WHY: Begins mapping account names to public keys for the close instruction.
        counter: counterPda,                              // WHY: Targets the counter PDA so the program closes the correct account.
        payer: payer,                                     // WHY: Passes the payer as the signer and rent refund recipient.
      })
      .rpc();                                             // WHY: Sends the close transaction and waits for on-chain confirmation.

    try {                                                 // WHY: Begins a try block because fetching a closed account should throw an error.
      await program.account.counterAccount.fetch(counterPda); // WHY: Attempts to fetch the account data to prove the account no longer exists.
      expect.fail("Account should have been closed");     // WHY: Forces a test failure if the fetch succeeds, because a closed account must not be found.
    } catch (err) {                                       // WHY: Catches the expected error when fetching a non-existent closed account.
      expect(err).to.be.an("error");                      // WHY: Asserts that an error was thrown, confirming the account no longer exists on-chain.
    }
  });
});
