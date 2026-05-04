import express from 'express'; // WHY: import Express framework to create HTTP server handling Action routes
import cors from 'cors'; // WHY: import CORS middleware to allow cross-origin requests from any blink client
import { Connection, PublicKey, SystemProgram, Transaction, clusterApiUrl } from '@solana/web3.js'; // WHY: import Solana web3 classes to build and serialize on-chain transactions
const app = express(); // WHY: instantiate Express application to define routes and middleware
const PORT = 3071; // WHY: use dedicated port 3071 to avoid conflicts with other Web3 course APIs
app.use(cors({ // WHY: enable CORS for all routes so wallet extensions and interstitial sites can call the API
  origin: '*', // WHY: allow requests from any origin because blinks are embedded across unknown domains
  methods: ['GET', 'POST', 'OPTIONS'], // WHY: permit GET for metadata, POST for transactions, and OPTIONS for preflight checks
  allowedHeaders: ['Content-Type', 'Authorization', 'Content-Encoding', 'Accept-Encoding'], // WHY: expose required headers per Dialect spec for compressed and authenticated requests
})); // WHY: close CORS configuration object
app.use(express.json()); // WHY: parse incoming JSON bodies so POST routes can read the account field
app.get('/actions.json', (req, res) => { // WHY: serve actions.json at domain root per spec so clients discover which paths support Actions
  res.setHeader('Content-Type', 'application/json'); // WHY: declare JSON content type so clients parse the response correctly
  res.json({ // WHY: return the discovery payload that maps web paths to Action API endpoints
    rules: [ // WHY: define rules array that lists all path mappings for blink clients to introspect
      { // WHY: open first rule object
        pathPattern: '/actions/*', // WHY: match any single-segment path under /actions/ to support simple action routes
        apiPath: '/actions/*', // WHY: map matched paths to the same structure under /actions/ for idempotent routing
      }, // WHY: close first rule object
      { // WHY: open second rule object to support nested action paths
        pathPattern: '/actions/**', // WHY: match multi-segment paths under /actions/ for chained or parameterized routes
        apiPath: '/actions/**', // WHY: map nested paths to the same nested API structure preserving all sub-routes
      }, // WHY: close second rule object
    ], // WHY: close rules array
  }); // WHY: close JSON payload
}); // WHY: end GET /actions.json route handler
app.get('/actions/swap', (req, res) => { // WHY: define GET route for swap metadata so clients render the swap blink UI
  res.setHeader('Content-Type', 'application/json'); // WHY: set JSON content type per Actions spec for consistent client parsing
  res.json({ // WHY: return ActionGetResponse payload describing the swap action and available user choices
    type: 'action', // WHY: declare type as action because this endpoint offers interactive linked actions
    icon: 'https://alice.com/swap-icon.png', // WHY: provide absolute icon URL so clients display a recognizable image for the blink
    title: 'Alice Swap', // WHY: set human-readable title identifying the source of the action request
    description: 'Swap SOL for USDC at the best available rate.', // WHY: explain the action so users understand what will happen before clicking
    label: 'Swap', // WHY: set root label text though it will be hidden since linked actions are provided
    links: { // WHY: open links object to declare specific linked actions with individual buttons
      actions: [ // WHY: define array of LinkedAction objects each representing one clickable option
        { // WHY: open first linked action for a fixed quick-swap amount
          label: 'Swap 0.1 SOL', // WHY: provide concise button text telling the user exactly how much they will swap
          href: '/actions/swap?amount=0.1', // WHY: specify endpoint path with hardcoded amount so no extra input is needed
        }, // WHY: close first linked action
        { // WHY: open second linked action for another fixed amount
          label: 'Swap 0.5 SOL', // WHY: offer a larger preset amount to reduce friction for common swap sizes
          href: '/actions/swap?amount=0.5', // WHY: encode the amount in query string so the POST handler reads it directly
        }, // WHY: close second linked action
        { // WHY: open third linked action accepting custom user input
          label: 'Swap', // WHY: label the button with a verb because the amount comes from the input field
          href: '/actions/swap?amount={amount}', // WHY: use template placeholder so the client substitutes the user input before POSTing
          parameters: [ // WHY: declare input fields required to collect the custom swap amount from the user
            { // WHY: open parameter object for the amount input
              name: 'amount', // WHY: name the parameter amount so the client knows which template variable to substitute
              label: 'SOL amount', // WHY: set placeholder text guiding the user to enter a numeric SOL quantity
              type: 'number', // WHY: declare number type for client-side validation and numeric keyboard on mobile
            }, // WHY: close parameter object
          ], // WHY: close parameters array
        }, // WHY: close third linked action
      ], // WHY: close linked actions array
    }, // WHY: close links object
  }); // WHY: close ActionGetResponse payload
}); // WHY: end GET /actions/swap route handler
app.post('/actions/swap', async (req, res) => { // WHY: define POST route to build and return a signable swap transaction
  try { // WHY: wrap transaction building in try/catch to return actionable errors without crashing the server
    const account: string = req.body.account; // WHY: extract the base58-encoded user account from the POST body per spec
    if (!account) { // WHY: validate that the account field exists because POST requests must include a signer's public key
      res.status(400).json({ message: 'Missing account field' }); // WHY: return 400 error if account is absent so the client knows the request was malformed
      return; // WHY: exit the handler early to prevent further execution with invalid input
    } // WHY: close account validation block
    const amountParam = req.query.amount as string || '0.1'; // WHY: read the amount from query string defaulting to 0.1 if not provided
    const connection = new Connection(clusterApiUrl('devnet')); // WHY: connect to devnet so demo transactions do not spend real SOL
    const sender = new PublicKey(account); // WHY: convert the account string to a PublicKey to use as transaction signer and fee payer
    const recipient = sender; // WHY: use sender as recipient for demo safety so devnet transactions do not send funds to an invalid address
    const lamports = Math.round(parseFloat(amountParam) * 1e9); // WHY: convert human SOL to lamports because Solana programs operate in integer lamports
    const transaction = new Transaction(); // WHY: instantiate a new Solana Transaction to hold the swap instruction
    transaction.add( // WHY: append the transfer instruction to the transaction as a simplified stand-in for a swap
      SystemProgram.transfer({ // WHY: use SystemProgram transfer because this demo illustrates transaction structure without complex DEX integration
        fromPubkey: sender, // WHY: set sender as the debit account so the user authorizes the outgoing funds
        toPubkey: recipient, // WHY: set recipient as the credit account receiving the swapped or donated funds
        lamports: lamports, // WHY: specify exact lamport amount derived from user input to ensure correct value transfer
      }), // WHY: close SystemProgram.transfer instruction
    ); // WHY: close transaction.add call
    transaction.feePayer = sender; // WHY: assign fee payer to the user account because the user must cover network fees
    const { blockhash } = await connection.getLatestBlockhash(); // WHY: fetch a recent blockhash so the transaction is valid for the current ledger slot
    transaction.recentBlockhash = blockhash; // WHY: attach the recent blockhash to prevent replay and anchor the transaction in time
    const serialized = transaction.serialize({ requireAllSignatures: false }); // WHY: serialize without all signatures because only the user will sign later in their wallet
    const base64 = Buffer.from(serialized).toString('base64'); // WHY: encode serialized bytes to base64 string as required by the ActionPostResponse spec
    res.setHeader('Content-Type', 'application/json'); // WHY: ensure the response is parsed as JSON by the blink client
    res.json({ // WHY: return ActionPostResponse containing the encoded transaction for the wallet to decode and sign
      transaction: base64, // WHY: include the base64 transaction string as the required payload for client deserialization
      message: `Swap ${amountParam} SOL`, // WHY: provide a human-readable message describing the transaction nature to display in the wallet
    }); // WHY: close ActionPostResponse payload
  } catch (err: any) { // WHY: catch any error during async transaction construction to return a safe error response
    res.status(400).json({ // WHY: return 400 status for client errors such as invalid account or malformed amount
      message: err.message || 'Failed to build swap transaction', // WHY: include the error message so the user knows why the action failed
    }); // WHY: close error response payload
  } // WHY: end catch block
}); // WHY: end POST /actions/swap route handler
app.get('/actions/donate', (req, res) => { // WHY: define GET route for donation metadata so clients render a donate blink card
  res.setHeader('Content-Type', 'application/json'); // WHY: set JSON content type so the client correctly interprets the metadata payload
  res.json({ // WHY: return ActionGetResponse describing the donation action and preset amounts
    type: 'action', // WHY: mark response as action type to indicate interactive donation choices are available
    icon: 'https://alice.com/donate-icon.png', // WHY: supply absolute icon URL for visual identification in unfurled blink cards
    title: 'Support Alice', // WHY: name the beneficiary so users know who receives the donation
    description: 'Donate SOL to fund open source tooling and educational content.', // WHY: explain the cause so donors understand the impact of their contribution
    label: 'Donate', // WHY: set root label though linked actions override it with specific button text
    links: { // WHY: open links to define multiple donation options
      actions: [ // WHY: list linked actions allowing users to pick preset amounts or enter a custom value
        { // WHY: open first preset donation option
          label: 'Donate 0.01 SOL', // WHY: offer a small preset amount lowering the barrier for casual supporters
          href: '/actions/donate?amount=0.01', // WHY: encode the small amount in the href so the POST handler knows the donation size
        }, // WHY: close first preset option
        { // WHY: open second preset donation option
          label: 'Donate 0.1 SOL', // WHY: offer a standard preset amount for users who want to give more significantly
          href: '/actions/donate?amount=0.1', // WHY: pass the standard amount as a query parameter for server-side transaction building
        }, // WHY: close second preset option
        { // WHY: open custom donation option
          label: 'Donate', // WHY: use verb-only label because the amount is collected via the input field
          href: '/actions/donate?amount={amount}', // WHY: template the amount variable so the client injects user input before making the POST request
          parameters: [ // WHY: declare input parameters needed for the custom donation
            { // WHY: open amount parameter definition
              name: 'amount', // WHY: name the parameter to match the template placeholder in the href
              label: 'SOL amount', // WHY: display placeholder text prompting the user to enter a donation quantity
              type: 'number', // WHY: enforce numeric input type for client-side validation and better mobile UX
            }, // WHY: close amount parameter
          ], // WHY: close parameters array
        }, // WHY: close custom donation option
      ], // WHY: close linked actions array
    }, // WHY: close links object
  }); // WHY: close ActionGetResponse payload
}); // WHY: end GET /actions/donate route handler
app.post('/actions/donate', async (req, res) => { // WHY: define POST route to construct and return a signable donation transaction
  try { // WHY: guard against runtime errors during transaction assembly to prevent server crashes
    const account: string = req.body.account; // WHY: read the donor's public key from the POST body per the Actions POST request spec
    if (!account) { // WHY: ensure the account is present because the server cannot build a transaction without a known signer
      res.status(400).json({ message: 'Missing account field' }); // WHY: reject malformed requests with a clear error so the client can prompt the user correctly
      return; // WHY: stop execution here to avoid passing undefined into the PublicKey constructor
    } // WHY: close validation block
    const amountParam = req.query.amount as string || '0.01'; // WHY: retrieve the donation amount from query string defaulting to a small tip if absent
    const connection = new Connection(clusterApiUrl('devnet')); // WHY: target devnet to ensure no real economic loss during demo and testing
    const sender = new PublicKey(account); // WHY: parse the donor account string into a PublicKey for use as signer and fee payer
    const recipient = sender; // WHY: use sender as recipient for demo safety so funds remain under the user's control on devnet
    const lamports = Math.round(parseFloat(amountParam) * 1e9); // WHY: convert decimal SOL to integer lamports as required by the Solana runtime
    const transaction = new Transaction(); // WHY: create a fresh Transaction container to hold the donation instruction
    transaction.add( // WHY: append the transfer instruction representing the donation payment
      SystemProgram.transfer({ // WHY: utilize SystemProgram transfer for a straightforward SOL donation instruction
        fromPubkey: sender, // WHY: designate the donor as the source of funds requiring their signature
        toPubkey: recipient, // WHY: designate the treasury as the destination for the donated lamports
        lamports: lamports, // WHY: set the precise lamport amount equal to the user-specified donation quantity
      }), // WHY: close transfer instruction arguments
    ); // WHY: close add call
    transaction.feePayer = sender; // WHY: require the donor to pay network fees since they are initiating the transaction
    const { blockhash } = await connection.getLatestBlockhash(); // WHY: obtain a fresh blockhash to ensure the transaction is accepted by the current leader
    transaction.recentBlockhash = blockhash; // WHY: bind the transaction to a recent ledger state for replay protection
    const serialized = transaction.serialize({ requireAllSignatures: false }); // WHY: serialize while allowing missing signatures because the donor signs in their wallet
    const base64 = Buffer.from(serialized).toString('base64'); // WHY: encode to base64 per ActionPostResponse so the client can decode and submit
    res.setHeader('Content-Type', 'application/json'); // WHY: mark response as JSON so the wallet parses it correctly
    res.json({ // WHY: return the ActionPostResponse containing the donation transaction
      transaction: base64, // WHY: deliver the base64-encoded transaction as the primary signable payload
      message: `Donate ${amountParam} SOL to Support Alice`, // WHY: display a clear human-readable description inside the wallet confirmation screen
    }); // WHY: close POST response payload
  } catch (err: any) { // WHY: intercept any exception to return a controlled error message to the blink client
    res.status(400).json({ // WHY: use 400 Bad Request to signal client-side input or account issues
      message: err.message || 'Failed to build donation transaction', // WHY: surface the underlying error so developers and users can diagnose failures
    }); // WHY: close error response
  } // WHY: end error handling block
}); // WHY: end POST /actions/donate route handler
app.options('*', (req, res) => { // WHY: handle OPTIONS preflight requests for all routes to satisfy CORS requirements
  res.setHeader('Access-Control-Allow-Origin', '*'); // WHY: echo wildcard origin header so browsers allow subsequent cross-origin GET and POST calls
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,OPTIONS'); // WHY: advertise supported HTTP methods per the Actions CORS specification
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, Content-Encoding, Accept-Encoding'); // WHY: list permitted headers so wallets can send JSON and compression headers
  res.sendStatus(200); // WHY: respond with HTTP 200 to indicate the preflight check passed
}); // WHY: end OPTIONS handler
app.listen(PORT, () => { // WHY: start the Express server and bind to the dedicated port
  console.log(`Blink server running on port ${PORT}`); // WHY: log startup confirmation so the developer knows the Actions API is live and ready for introspection
}); // WHY: end listen callback
