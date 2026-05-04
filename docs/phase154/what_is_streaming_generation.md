## What Is Streaming Generation?

**The Problem:**
A language model takes 10 seconds to generate a 200-token response. During that time, the user stares at a loading spinner, unsure if the system is working. How do you show partial results as they are generated, so the user sees text appear word-by-word?

**Definition:**
**Streaming generation** is the process of generating tokens one at a time and sending each token to the client immediately, rather than waiting for the full response to be complete. It creates the illusion of the model "thinking out loud."

**Real-life analogy:**
Streaming generation is like a court stenographer typing in real-time. As the witness speaks, the stenographer types each word and it appears on screens around the courtroom. The audience reads along as the testimony unfolds. Without streaming, the stenographer would wait until the witness finished speaking, then hand out a typed transcript 10 minutes later. Streaming makes the experience feel interactive and immediate.

**Tiny numeric example:**
Without streaming:
- Request at t=0
- Model generates for 10 seconds
- Full response delivered at t=10

With streaming:
- Request at t=0
- First token delivered at t=0.05
- 10th token delivered at t=0.5
- 100th token delivered at t=5.0
- Full response complete at t=10
The user starts reading immediately and perceives the system as 10x faster.

**Common confusion:**
- **"Streaming makes generation faster."** No. The total time is the same. Streaming reduces perceived latency by showing partial results early.
- **"Streaming is just chunked HTTP responses."** Server-Sent Events (SSE) is the standard for streaming. Each token is a separate event. Chunked transfer encoding is a lower-level mechanism.
- **"You cannot batch streaming requests."** You can. vLLM's continuous batching interleaves streaming requests so that each client receives tokens as they are generated, while the GPU processes multiple requests in parallel.
- **"Streaming complicates error handling."** It does. If an error occurs mid-stream, you must send an error event and close the connection gracefully. This requires careful exception handling.
- **"All clients support streaming."** Most modern clients do, but some older HTTP clients buffer the entire response. You should always support both streaming and non-streaming modes.

**Where it appears in our code:**
`src/phase154/phase154_inference_api.py` — The `generate_text_stream()` function yields tokens one at a time. The `/v1/completions` endpoint returns a `StreamingResponse` with SSE format when `stream=true`.
