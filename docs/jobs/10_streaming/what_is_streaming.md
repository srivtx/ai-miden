## Why it exists (THE PROBLEM)

Normal HTTP: client sends request → server processes → server sends response → connection closes. For code completion: model generates 100 tokens, waits for ALL of them, sends them at once. User sees nothing for 500ms, then a wall of text.

The user experience is terrible. The user typed `def add` and stared at a blank cursor for 500ms. They started typing manually. Then the completion appeared and overwrote what they typed. Frustrating.

**Streaming** sends tokens ONE AT A TIME as they're generated. Token 1 appears after 5ms. Token 2 after 10ms. The user SEES the completion forming. They can hit Escape if it's wrong. Latency feels 50× faster because partial results arrive immediately.

Streaming requires: a persistent connection (WebSocket or SSE), the model yielding tokens one at a time, and the client rendering tokens as they arrive.

## Definition (very simple)

**SSE (Server-Sent Events):** A one-way stream from server to client over HTTP. The server sends `data: {"token": "a"}\n\n` every few milliseconds. The client listens for `event.data`. Simpler than WebSockets (HTTP, no upgrade) but one-way only.

**WebSocket:** A bidirectional persistent connection. Client and server can both send at any time. For code completion: client sends `{"prompt": "def add(a,b):"}` once. Server streams tokens back via WebSocket messages. Client can send `{"cancel": true}` to stop generation.

**Streaming HTTP (chunked transfer):** Standard HTTP with `Transfer-Encoding: chunked`. The server writes chunks (each chunk = one or more tokens). The client reads the response stream incrementally. Used by OpenAI API: `stream=True` gives `data: {"choices": [{"delta": {"content": "a"}}]}\n\n`.

## Practice: Streaming code completion in FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def generate_tokens_stream(model, prompt, max_tokens=80):
    """Generate tokens one at a time and yield them as SSE events."""
    ids = tokenizer.encode(prompt)
    for _ in range(max_tokens):
        # Generate one token
        with torch.no_grad():
            logits = model(ids).logits[:, -1, :]
            probs = torch.softmax(logits / 0.2, dim=-1)
            next_token = torch.multinomial(probs, 1).item()

        ids.append(next_token)
        token_text = tokenizer.decode([next_token])

        # Check for stop
        if next_token == eos_token_id:
            yield f"data: {json.dumps({'done': True})}\n\n"
            break

        # Send token immediately
        yield f"data: {json.dumps({'token': token_text, 'id': next_token})}\n\n"
        await asyncio.sleep(0)  # yield to event loop


@app.post("/complete/stream")
async def complete_stream(req: CompleteRequest):
    """Stream code completion token by token."""
    return StreamingResponse(
        generate_tokens_stream(MODEL, req.prompt, req.n_tokens),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        }
    )
```

**Client-side (JavaScript in our frontend):**
```javascript
async function streamComplete(prompt) {
    const response = await fetch('/complete/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt, n_tokens: 80, temperature: 0.2})
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const outputDiv = document.getElementById('output');

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                if (data.done) return;
                // Append token to output IMMEDIATELY
                outputDiv.textContent += data.token;
            }
        }
    }
}
```

Now: user types `def add(a, b):`, clicks Complete, and SEES `return a` appear after 5ms, then ` + b` after 10ms. Total time: same 500ms. Perceived time: <50ms because the first token appears instantly.

## Key properties

| | Non-streaming | Streaming |
|---|---|---|
| First token visible | After full generation (500ms) | After first token (5-10ms) |
| User can cancel | No (must wait) | Yes (close connection) |
| Perceived latency | 100% of generation time | ~2% of generation time |
| Memory | Full output held until done | One token at a time |
| Time-to-first-byte (TTFB) | Generation time | Network RTT + 1 token |

## Tech comparison: streaming protocols

| Protocol | Best for | Notes |
|---|---|---|
| **SSE** | One-way server→client | Simpler than WS, works through proxies |
| **WebSocket** | Bidirectional (cancel, progress) | More complex, connection upgrade |
| **HTTP chunked** | API compatibility (OpenAI) | Most HTTP clients support streaming |
| **gRPC streaming** | Microservices, typed | Binary protocol, harder to debug |

## Common confusion

1. **"Streaming just sends the same data faster."** No. The completion takes the SAME wall time. But the USER sees tokens 50× earlier because the first token arrives after 5ms, not after the full 500ms generation. Perceived latency is everything for UX.

2. **"Any web framework can stream."** Flask's `Response(generator)` is synchronous and blocks. FastAPI's `StreamingResponse` with `async for` is truly non-blocking. For production streaming: FastAPI or Starlette, not Flask. For Colab: FastAPI works.

3. **"SSE doesn't work through some proxies."** Nginx buffers responses by default. Add `proxy_buffering off;` and `X-Accel-Buffering: no` header. Cloudflare tunnel: SSE works transparently (we proved this with the trycloudflare URLs working).

4. **"The client needs a special library."** No. Standard `fetch()` with `ReadableStream` (JavaScript). Or `EventSource` for SSE (simpler but no POST support, GET only). Python: `httpx.stream()` or `requests.Session().get(stream=True)`.

## Connection to our projects

**cortexcode:** Add the streaming endpoint above. Update `frontend/index.html` to use `fetch()` streaming instead of wait-for-response. The "Try it" panel now shows tokens appearing one by one. User experience: professional (matches GitHub Copilot's UX).

**Implementation plan:** ~30 lines on server side (the `generate_tokens_stream` function). ~30 lines on frontend (the `ReadableStream` reader). Total: 60 lines. Impact: user experience transforms from "is it broken?" to "this feels fast."
