# Phase 63 Architecture: Blinks and Actions

## Step 1: Define an action (swap, stake, pay)

Decide what on-chain operation your blink will enable. A swap action might exchange SOL for USDC via Jupiter. A stake action might delegate SOL to a validator. A pay action might transfer tokens to a creator. Defining the action first determines what parameters you need, what instructions the transaction will contain, and what metadata you will show the user. Without a clear scope, your API will return vague labels and confusing transaction previews.

## Step 2: Create action metadata JSON

Host an `actions.json` file at the root of your domain. This file contains a `rules` array that maps website path patterns to Action API paths. For example, `/donate/*` might map to `/api/donate/*`. The file tells blink clients which URLs on your domain support Action introspection. Without it, a client that sees `https://your-site.com/donate` has no way to know that an Action API exists at `/api/donate`, and the blink will not unfurl.

## Step 3: Build blink URL

Construct a URL that encodes your Action endpoint using the `solana-action:` scheme. If you use an interstitial site like `dial.to`, the URL looks like `https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Fyour-site.com%2Fapi%2Fdonate`. URL-encoding prevents query parameter collisions. The blink URL is what users actually share and click. Building it correctly ensures that every client can decode the underlying Action address regardless of where the link is pasted.

## Step 4: Implement action handler API

Build an Express (or equivalent) server with two routes for each action. The GET route returns an `ActionGetResponse` with `type`, `icon`, `title`, `description`, `label`, and optional `links.actions` with parameters. The POST route accepts `{ account: string }`, constructs the Solana transaction, sets the fee payer to the provided account, fetches a recent blockhash, serializes the transaction to base64, and returns it in an `ActionPostResponse`. This step is where the abstract action definition becomes a concrete, signable transaction.

## Step 5: Test blink execution

Use the Blinks Inspector at `blinks.xyz/inspector` or Dialect's `dial.to` interstitial site to test your blink end-to-end. Verify that the GET response renders correctly, that input parameters validate properly, that the POST response returns a deserializable transaction, and that the transaction simulates successfully on devnet. Testing catches CORS misconfigurations, malformed JSON, and missing blockhash updates before real users encounter them.

## Step 6: Register in Dialect registry

Apply for verification at `dial.to/register` so that supported clients will unfurl your blink on platforms like Twitter. Provide your domain, describe your action, and pass the community safety review. Registration is not required for the blink to function, but it is required for automatic unfurling on platforms that use the registry as a trust layer. Without this step, your blink will work on `dial.to` but will appear as a plain URL on registry-dependent platforms.
