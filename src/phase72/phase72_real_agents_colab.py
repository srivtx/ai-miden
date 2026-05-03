# phase72_real_agents_colab.py
# Phase 72: Real Agents with Tool Use — Colab Real-Workflow Script
# ============================================================================
# WHY THIS FILE EXISTS
# --------------------
# The local NumPy demo shows the *mechanics* of ReAct. This file shows how
# those mechanics map to an actual LLM inference loop. We use a MOCK model
# so you can run it without a GPU, but every comment marked [REAL MODEL]
# tells you exactly what to change when you plug in Llama, Mistral, or
# another open-source function-calling model.
# ============================================================================

import json
import os
import sys

# ---------------------------------------------------------------------------
# 1. TOOL DEFINITIONS (schemas + implementations)
# ---------------------------------------------------------------------------
# WHY schemas?  The LLM does not know your Python code. It only knows the
# JSON schema you pass in the system prompt.  A well-written schema is the
# contract between the model and your code.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a simple arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression, e.g. '128 * 456'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for a factual query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "weather",
            "description": "Get current weather for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'Tokyo'"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

def calculator(expression: str):
    """Execute calculator safely."""
    # WHY eval inside a restricted dict?  We only want math, no file system.
    allowed = {"__builtins__": {}}
    try:
        result = eval(expression, allowed)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def web_search(query: str):
    """Mock web search. In production this would call SerpAPI, DuckDuckGo, etc."""
    mock_db = {
        "capital of france": "Paris",
        "population of tokyo": "37.4 million",
        "gdp of usa": "23.32 trillion USD"
    }
    return mock_db.get(query.lower(), f"No results found for '{query}'")

def weather(location: str):
    """Mock weather API. In production this would call OpenWeatherMap."""
    mock_weather = {
        "tokyo": {"temp_c": 22, "condition": "Clear sky"},
        "paris": {"temp_c": 18, "condition": "Light rain"},
        "new york": {"temp_c": 15, "condition": "Cloudy"}
    }
    data = mock_weather.get(location.lower(), {"temp_c": 20, "condition": "Unknown"})
    return json.dumps(data)

# Map tool names to Python functions so the host can dispatch calls.
TOOL_MAP = {
    "calculator": calculator,
    "web_search": web_search,
    "weather": weather
}

# ---------------------------------------------------------------------------
# 2. MOCK LLM WITH FUNCTION CALLING
# ---------------------------------------------------------------------------
# [REAL MODEL] In a real Colab you would do:
#   from transformers import AutoTokenizer, AutoModelForCausalLM
#   tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B-Instruct")
#   model = AutoModelForCausalLM.from_pretrained(...)
# and then generate() inside react_loop().

class MockLLM:
    """
    A deterministic mock that simulates an LLM trained for function calling.
    It inspects the user message and returns a JSON tool_call or a final answer.
    """
    def __init__(self):
        self.call_count = 0

    def generate(self, messages, tools):
        """
        WHY messages as a list?  Multi-turn agents accumulate history.
        Each turn appends new dicts so the model sees the full context.
        """
        user_msg = messages[-1]["content"].lower()
        self.call_count += 1

        # --- heuristic "model" logic ---
        if "weather" in user_msg:
            loc = "Tokyo"  # simplified extraction
            if "paris" in user_msg:
                loc = "Paris"
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": "weather",
                        "arguments": json.dumps({"location": loc})
                    }
                }]
            }
        elif "search" in user_msg or "capital" in user_msg or "population" in user_msg:
            q = user_msg.replace("search", "").strip()
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": json.dumps({"query": q})
                    }
                }]
            }
        elif any(op in user_msg for op in ["+", "*", "/", "-", "calculate", "math"]):
            # Extract a simple expression
            expr = "2+2"  # default fallback
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{self.call_count}",
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "arguments": json.dumps({"expression": expr})
                    }
                }]
            }
        else:
            return {
                "role": "assistant",
                "content": "I don't know how to help with that."
            }

# ---------------------------------------------------------------------------
# 3. AGENT / REACT LOOP
# ---------------------------------------------------------------------------
class ReActAgent:
    def __init__(self, llm, tools, tool_map):
        # WHY store history?  The LLM needs to see past thoughts and
        # observations or it will repeat actions or lose context.
        self.history = []
        self.llm = llm
        self.tools = tools
        self.tool_map = tool_map
        self.max_turns = 5  # safety guard against infinite loops

    def run(self, user_query):
        # Initial user message
        self.history.append({"role": "user", "content": user_query})
        print(f"\n{'='*60}")
        print(f"USER: {user_query}")
        print(f"{'='*60}")

        for turn in range(1, self.max_turns + 1):
            # WHY pass the full history every time?  LLMs are stateless;
            # they do not remember previous calls unless you resend the text.
            response = self.llm.generate(self.history, self.tools)

            # Extract assistant message
            assistant_msg = {
                "role": response["role"],
                "content": response.get("content"),
                "tool_calls": response.get("tool_calls", [])
            }
            self.history.append(assistant_msg)

            # --- THOUGHT ---
            # In a real model the "thought" is implicit in the token generation.
            # We print a proxy so the trace is readable.
            print(f"\n--- Turn {turn} ---")
            if assistant_msg["content"]:
                print(f"ASSISTANT (final): {assistant_msg['content']}")
                print("Task complete.\n")
                return assistant_msg["content"]
            else:
                print("ASSISTANT THOUGHT: I need to call a tool to answer this.")

            # --- ACTION & OBSERVATION ---
            for tc in assistant_msg["tool_calls"]:
                tool_name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                print(f"ACTION: call {tool_name} with {args}")

                # Execute tool on the HOST side (never inside the model)
                if tool_name in self.tool_map:
                    observation = self.tool_map[tool_name](**args)
                else:
                    observation = f"Error: unknown tool '{tool_name}'"

                print(f"OBSERVATION: {observation}")

                # WHY append tool result to history?  So the next turn the
                # model can read the observation and decide what to do next.
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tool_name,
                    "content": str(observation)
                })

        print("Max turns reached. Aborting.")
        return None

# ---------------------------------------------------------------------------
# 4. EXECUTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    llm = MockLLM()
    agent = ReActAgent(llm, TOOLS, TOOL_MAP)

    # Example multi-turn workflow
    queries = [
        "What is the weather in Paris?",
        "Search for the population of Tokyo",
        "Calculate 128 * 456"
    ]

    for q in queries:
        agent.run(q)
        # In a real chat UI you would keep the same agent instance so memory
        # persists across user messages. Here we reset per query for clarity,
        # but the internal history still demonstrates multi-turn *within* one task.
