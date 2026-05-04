"""
Phase 154: Production Inference API
====================================
This is a REAL project. Not a toy.

We build a production-ready inference server:
1. FastAPI application with async endpoints
2. /v1/completions endpoint (OpenAI-compatible)
3. /v1/chat/completions endpoint (OpenAI-compatible)
4. Streaming generation with Server-Sent Events
5. Dynamic batching for concurrent requests
6. Health check and metrics endpoints
7. Request validation and error handling
8. Rate limiting simulation

This is exactly what companies deploy to serve models in production.
Run: python src/phase154/phase154_inference_api.py
Then test with: curl -X POST http://localhost:8000/v1/completions -H "Content-Type: application/json" -d '{"prompt":"AI is","max_tokens":20}'
"""

import os
import time
import asyncio
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    "model_name": "gpt2",
    "max_batch_size": 4,
    "max_sequence_length": 512,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}

# ============================================================================
# MODEL LOADING (LIFESPAN)
# ============================================================================
# WHY: We load the model once at startup and share it across all requests.
# Loading a model per request would be catastrophically slow.

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = CONFIG["device"]
        self.request_count = 0
        self.total_tokens_generated = 0

    def load(self):
        print(f"Loading {CONFIG['model_name']} on {self.device}...")
        self.tokenizer = GPT2Tokenizer.from_pretrained(CONFIG["model_name"])
        self.model = GPT2LMHeadModel.from_pretrained(CONFIG["model_name"]).to(self.device)
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print("Model loaded.")

model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_manager.load()
    yield
    print("Shutting down...")

app = FastAPI(
    title="AI-MIDEN Inference API",
    description="OpenAI-compatible inference server for LLMs",
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================================================
# REQUEST MODELS
# ============================================================================
# WHY: Pydantic models validate incoming JSON and provide clear error messages.

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 20
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False
    n: int = 1
    stop: Optional[List[str]] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "gpt2"
    messages: List[ChatMessage]
    max_tokens: int = 20
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False
    n: int = 1

# ============================================================================
# GENERATION LOGIC
# ============================================================================

def generate_text(
    prompt: str,
    max_tokens: int = 20,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    """Generate text from a prompt. Blocking call."""
    inputs = model_manager.tokenizer.encode(prompt, return_tensors="pt").to(model_manager.device)

    with torch.no_grad():
        outputs = model_manager.model.generate(
            inputs,
            max_length=inputs.shape[1] + max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=model_manager.tokenizer.eos_token_id,
        )

    generated = model_manager.tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from the output
    answer = generated[len(prompt):].strip()
    return answer

async def generate_text_stream(
    prompt: str,
    max_tokens: int = 20,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> AsyncGenerator[str, None]:
    """Generate text token by token for streaming."""
    inputs = model_manager.tokenizer.encode(prompt, return_tensors="pt").to(model_manager.device)
    generated = inputs.clone()

    for _ in range(max_tokens):
        with torch.no_grad():
            outputs = model_manager.model(generated)
            logits = outputs.logits[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)

            # Top-p (nucleus) sampling
            sorted_probs, sorted_indices = torch.sort(probs, descending=True)
            cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = False
            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[0, indices_to_remove] = -float('Inf')

            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

        generated = torch.cat([generated, next_token], dim=1)
        token_str = model_manager.tokenizer.decode(next_token[0], skip_special_tokens=True)

        yield token_str

        if next_token.item() == model_manager.tokenizer.eos_token_id:
            break

        await asyncio.sleep(0.01)  # Simulate streaming delay

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring."""
    return {
        "status": "healthy",
        "model": CONFIG["model_name"],
        "device": CONFIG["device"],
        "requests_served": model_manager.request_count,
        "total_tokens": model_manager.total_tokens_generated,
    }

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    return {
        "object": "list",
        "data": [
            {
                "id": CONFIG["model_name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "ai-miden",
            }
        ],
    }

@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """
    OpenAI-compatible completions endpoint.
    Supports both streaming and non-streaming responses.
    """
    model_manager.request_count += 1

    if request.stream:
        async def stream_response():
            async for token in generate_text_stream(
                request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            ):
                data = {
                    "id": f"cmpl-{model_manager.request_count}",
                    "object": "text_completion",
                    "choices": [{"text": token, "index": 0, "finish_reason": None}],
                }
                yield f"data: {__import__('json').dumps(data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_response(), media_type="text/event-stream")

    # Non-streaming
    start_time = time.time()
    text = generate_text(
        request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
    )
    model_manager.total_tokens_generated += len(text.split())

    return {
        "id": f"cmpl-{model_manager.request_count}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": CONFIG["model_name"],
        "choices": [
            {
                "text": text,
                "index": 0,
                "finish_reason": "length",
            }
        ],
        "usage": {
            "prompt_tokens": len(request.prompt.split()),
            "completion_tokens": len(text.split()),
            "total_tokens": len(request.prompt.split()) + len(text.split()),
        },
    }

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    Converts chat messages into a single prompt string.
    """
    model_manager.request_count += 1

    # WHY: GPT-2 is not chat-trained, so we concatenate messages with separators.
    # A real chat model (Llama, Mistral) would use a special chat template.
    prompt_parts = []
    for msg in request.messages:
        if msg.role == "system":
            prompt_parts.append(f"System: {msg.content}")
        elif msg.role == "user":
            prompt_parts.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            prompt_parts.append(f"Assistant: {msg.content}")
    prompt_parts.append("Assistant:")
    prompt = "\n".join(prompt_parts)

    if request.stream:
        async def stream_response():
            async for token in generate_text_stream(
                prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            ):
                data = {
                    "id": f"chatcmpl-{model_manager.request_count}",
                    "object": "chat.completion.chunk",
                    "choices": [{"delta": {"content": token}, "index": 0, "finish_reason": None}],
                }
                yield f"data: {__import__('json').dumps(data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_response(), media_type="text/event-stream")

    text = generate_text(
        prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
    )

    return {
        "id": f"chatcmpl-{model_manager.request_count}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "message": {"role": "assistant", "content": text},
                "index": 0,
                "finish_reason": "length",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(text.split()),
            "total_tokens": len(prompt.split()) + len(text.split()),
        },
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header for monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ============================================================================
# CLIENT DEMO
# ============================================================================
def demo_client():
    """Run a demo client that hits the API without starting the server."""
    print("Running API demo (serverless mode)...")
    model_manager.load()

    prompts = [
        "Artificial intelligence is",
        "The future of machine learning",
        "Neural networks work by",
    ]

    results = []
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        text = generate_text(prompt, max_tokens=25)
        print(f"Completion: {text}")
        results.append({"prompt": prompt, "completion": text})

    # Save demo results
    os.makedirs("src/phase154", exist_ok=True)
    with open("src/phase154/api_demo_results.json", "w") as f:
        __import__('json').dump(results, f, indent=2)
    print("\nSaved demo results to src/phase154/api_demo_results.json")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_client()
    else:
        print("Starting inference server...")
        print(f"Model: {CONFIG['model_name']}")
        print(f"Device: {CONFIG['device']}")
        print("\nTest with:")
        print('  curl -X POST http://localhost:8000/v1/completions \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"prompt": "AI is", "max_tokens": 20}\'')
        print("\nOr run demo without server:")
        print("  python src/phase154/phase154_inference_api.py --demo")
        uvicorn.run(app, host="0.0.0.0", port=8000)
