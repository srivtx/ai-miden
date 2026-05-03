#!/usr/bin/env python3
"""
================================================================================
Phase 27: Agentic AI — Giving Models Tools to Act
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 26, we made the model think longer.
But thinking alone cannot book flights, run code, or query databases.

This phase answers: "Can I give the model TOOLS so it can
actually DO things in the world?"

We cover five concepts:
  1. AI Agent          — Perceive, plan, act, observe
  2. Tool Use          — Call external functions
  3. ReAct Pattern     — Think -> Act -> Observe -> Repeat
  4. Multi-Agent       — Multiple specialists collaborating
  5. Computer Use      — Control GUIs with mouse and keyboard

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import json
import re
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# PART 0: TOOL REGISTRY
# ==============================================================================
# Tools are external functions the agent can call.
# The agent does not execute them directly — it generates a call,
# and the framework runs the tool and returns the result.
# ==============================================================================

def tool_calculator(expression):
    """
    A safe calculator tool.
    
    PARAMETERS:
        expression = string like "2 + 2" or "sqrt(144)"
    
    RETURNS:
        result as a string
    """
    # We only allow basic math for safety
    allowed = set("0123456789+-*/.() **% ")
    if not all(c in allowed for c in expression):
        return "Error: invalid characters in expression"
    try:
        # Safe eval with no builtins
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def tool_search(query):
    """
    A toy search engine.
    
    In a real system, this would call Google or a database.
    Here, we simulate with a tiny knowledge base.
    """
    knowledge_base = {
        "capital of france": "Paris",
        "population of paris": "2.1 million (city), 12.4 million (metro)",
        "speed of light": "299,792,458 meters per second",
        "square root of 144": "12",
        "fibonacci 10": "55",
        "temperature in paris": "18 degrees Celsius",
        "president of france": "Emmanuel Macron",
        "area of circle formula": "pi * r^2",
    }
    query_lower = query.lower().strip()
    for key, value in knowledge_base.items():
        if key in query_lower or query_lower in key:
            return value
    return f"No results found for '{query}'. Try a different query."


def tool_weather(city):
    """
    A toy weather API.
    
    Returns a random but deterministic temperature for demo cities.
    """
    weather_db = {
        "paris": "18°C, partly cloudy",
        "london": "14°C, rainy",
        "tokyo": "22°C, sunny",
        "new york": "20°C, clear",
        "sydney": "25°C, warm",
    }
    city_lower = city.lower().strip()
    return weather_db.get(city_lower, f"No weather data for {city}.")


# Tool registry: maps tool names to functions
TOOL_REGISTRY = {
    "calculator": tool_calculator,
    "search": tool_search,
    "weather": tool_weather,
}


def list_tools():
    """Return a description of all available tools."""
    descriptions = {
        "calculator": "Evaluates mathematical expressions. Input: expression string. Output: result string.",
        "search": "Searches a knowledge base. Input: query string. Output: answer string.",
        "weather": "Gets current weather. Input: city name. Output: weather description.",
    }
    return descriptions


# ==============================================================================
# PART 1: AI AGENT — THE BASIC LOOP
# ==============================================================================
# The agent receives a task, decides what to do,
# calls a tool, observes the result, and repeats.
# ==============================================================================

class SimpleAgent:
    """
    A toy AI agent that uses tools to solve problems.
    
    This is NOT a real neural network. It uses rule-based logic
    to simulate how an LLM-powered agent would behave.
    """
    def __init__(self):
        self.tools = TOOL_REGISTRY
        self.max_iterations = 5

    def run(self, task):
        """Execute the agent loop on a task."""
        print(f"  TASK: {task}")
        print()

        iteration = 0
        context = f"Task: {task}\n"

        while iteration < self.max_iterations:
            iteration += 1
            print(f"  --- Iteration {iteration} ---")

            # STEP 1: Think (simulated reasoning)
            thought, action = self._think_and_act(task, context)
            print(f"  Thought: {thought}")

            if action is None:
                # No tool needed — direct answer
                print(f"  Final Answer: {thought}")
                print()
                return thought

            print(f"  Action: {action['tool']}({action['input']})")

            # STEP 2: Act (call the tool)
            result = self.tools[action['tool']](action['input'])
            print(f"  Observation: {result}")
            print()

            # STEP 3: Update context
            context += f"Thought: {thought}\nAction: {action['tool']}({action['input']})\nObservation: {result}\n"

        print("  Max iterations reached. Returning best guess.")
        return context

    def _think_and_act(self, task, context):
        """
        Simulate LLM reasoning and tool selection.
        
        In a real agent, this would be an LLM API call.
        Here, we use simple keyword matching to decide.
        """
        task_lower = task.lower()
        context_lower = context.lower()

        # Check if we already have the answer in context
        if "observation:" in context_lower:
            # We made a tool call. Did we get what we need?
            last_obs = context.split("Observation:")[-1].strip().split("\n")[0]

            if "weather" in task_lower or "temperature" in task_lower:
                if "°c" in last_obs.lower() or "°f" in last_obs.lower() or "sunny" in last_obs.lower() or "rainy" in last_obs.lower():
                    return f"I have the weather: {last_obs}. Now I can answer.", None
            if "population" in task_lower and "million" in last_obs.lower():
                return f"I have the population: {last_obs}. Now I can answer.", None
            if "capital" in task_lower and len(last_obs.split()) <= 3:
                return f"I found the capital: {last_obs}. Now I can answer.", None
            if "sqrt" in task_lower or "square root" in task_lower:
                try:
                    float(last_obs)
                    return f"The calculator returned {last_obs}. I can answer now.", None
                except:
                    pass
            if "fibonacci" in task_lower:
                try:
                    int(last_obs)
                    return f"The calculator returned {last_obs}. I can answer now.", None
                except:
                    pass

        # Decide which tool to use
        if any(word in task_lower for word in ["sqrt", "+", "-", "*", "/", "fibonacci", "area", "calculate", "weather", "temperature"]):
            # Extract the expression
            if "sqrt" in task_lower:
                match = re.search(r'sqrt\((\d+)\)', task_lower)
                if match:
                    return "This requires a calculator.", {"tool": "calculator", "input": f"{match.group(1)}**0.5"}
            if "fibonacci" in task_lower:
                match = re.search(r'fibonacci\s+(\d+)', task_lower)
                if match:
                    n = int(match.group(1))
                    expr = self._fib_expression(n)
                    return "I need to calculate the Fibonacci number.", {"tool": "calculator", "input": expr}
            if "weather" in task_lower or "temperature" in task_lower:
                for city in ["paris", "london", "tokyo", "new york", "sydney"]:
                    if city in task_lower:
                        return f"I need the weather for {city.title()}.", {"tool": "weather", "input": city}
                return "I need weather data.", {"tool": "weather", "input": "paris"}
            # Generic math
            return "This is a math problem. I'll use the calculator.", {"tool": "calculator", "input": task}

        # Default to search
        return "I'll search for this information.", {"tool": "search", "input": task}

    def _fib_expression(self, n):
        """Generate a simple expression for fibonacci (toy implementation)."""
        if n <= 1:
            return str(n)
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return str(b)


def demonstrate_ai_agent():
    """Show the basic agent loop with tools."""
    print("=" * 60)
    print("PART 1: AI AGENT — PERCEIVE, PLAN, ACT, OBSERVE")
    print("=" * 60)
    print()
    print("  The agent receives a task, picks a tool, calls it,")
    print("  observes the result, and repeats until done.")
    print()

    agent = SimpleAgent()

    tasks = [
        "What is the square root of 144?",
        "What is the weather in Tokyo?",
        "What is the capital of France?",
    ]

    for task in tasks:
        print("=" * 50)
        agent.run(task)

    print()
    print("  KEY INSIGHT:")
    print("    The agent did not know sqrt(144) from memory.")
    print("    It CALLED the calculator tool and got the exact answer.")
    print("    Tools extend the model beyond its training data.")
    print()


# ==============================================================================
# PART 2: ReAct PATTERN — THINK -> ACT -> OBSERVE
# ==============================================================================
# The agent explicitly shows its reasoning before each action.
# This makes the decision process transparent and debuggable.
# ==============================================================================

class ReActAgent(SimpleAgent):
    """
    A ReAct agent that explicitly shows its reasoning trace.
    """
    def run(self, task):
        """Execute with full ReAct trace."""
        print(f"  TASK: {task}")
        print()

        iteration = 0
        context = f"Task: {task}\n"
        trace = []

        while iteration < self.max_iterations:
            iteration += 1

            # THINK
            thought, action = self._think_and_act(task, context)
            trace.append(("Thought", thought))

            if action is None:
                trace.append(("Final Answer", thought))
                self._print_trace(trace)
                return thought

            # ACT
            trace.append(("Action", f"{action['tool']}({action['input']})"))
            result = self.tools[action['tool']](action['input'])

            # OBSERVE
            trace.append(("Observation", result))
            context += f"Thought: {thought}\nAction: {action['tool']}({action['input']})\nObservation: {result}\n"

        trace.append(("Final Answer", "Max iterations reached."))
        self._print_trace(trace)
        return context

    def _print_trace(self, trace):
        """Pretty-print the ReAct trace."""
        print("  " + "-" * 48)
        for step_type, content in trace:
            print(f"  {step_type:15s}: {content}")
        print("  " + "-" * 48)
        print()


def demonstrate_react():
    """Show the ReAct pattern with explicit reasoning."""
    print("=" * 60)
    print("PART 2: ReAct PATTERN")
    print("=" * 60)
    print()
    print("  ReAct = Reasoning + Acting")
    print("  The agent shows its thinking BEFORE each action.")
    print()

    agent = ReActAgent()

    # A multi-step problem that requires reasoning
    task = "What is the temperature in Paris plus the square root of 144?"
    agent.run(task)

    print("  KEY INSIGHT:")
    print("    The agent broke the problem into sub-tasks.")
    print("    Step 1: Get temperature (18°C).")
    print("    Step 2: Get sqrt(144) = 12.")
    print("    Step 3: 18 + 12 = 30.")
    print("    Without ReAct, the model might guess 'around 30'.")
    print("    With ReAct, it computes the EXACT answer.")
    print()


# ==============================================================================
# PART 3: MULTI-AGENT SYSTEMS
# ==============================================================================
# Multiple specialized agents pass work back and forth.
# Researcher finds facts. Writer produces text.
# ==============================================================================

class ResearcherAgent:
    """Agent specialized in finding facts."""
    def research(self, topic):
        """Search for information on a topic."""
        print(f"    [Researcher] Researching: {topic}")
        result = tool_search(topic)
        print(f"    [Researcher] Found: {result}")
        return result


class WriterAgent:
    """Agent specialized in writing text."""
    def write(self, facts, topic):
        """Produce a short paragraph from facts."""
        print(f"    [Writer] Writing about: {topic}")
        paragraph = f"According to our research, {topic} is related to {facts}. This is a verified fact."
        print(f"    [Writer] Draft: {paragraph}")
        return paragraph


class EditorAgent:
    """Agent specialized in checking facts."""
    def edit(self, draft, facts):
        """Check if the draft matches the facts."""
        print(f"    [Editor] Checking draft against facts...")
        # Simple check: does the draft contain the fact?
        if any(word in draft.lower() for word in facts.lower().split()[:3]):
            print(f"    [Editor] Approved.")
            return draft
        else:
            print(f"    [Editor] Rejected — draft does not match facts.")
            return None


def demonstrate_multi_agent():
    """Show two agents collaborating."""
    print("=" * 60)
    print("PART 3: MULTI-AGENT SYSTEM")
    print("=" * 60)
    print()
    print("  Researcher finds facts. Writer drafts text.")
    print("  Editor verifies accuracy. They pass work back and forth.")
    print()

    topic = "the capital of France"

    researcher = ResearcherAgent()
    writer = WriterAgent()
    editor = EditorAgent()

    print("  Starting collaboration...")
    print()

    # Step 1: Research
    facts = researcher.research(topic)

    # Step 2: Write
    draft = writer.write(facts, topic)

    # Step 3: Edit
    final = editor.edit(draft, facts)

    if final:
        print()
        print(f"  FINAL OUTPUT: {final}")
    else:
        print()
        print("  Draft rejected. Sending back to writer.")

    print()
    print("  KEY INSIGHT:")
    print("    No single agent did everything.")
    print("    The researcher was optimized for search.")
    print("    The writer was optimized for prose.")
    print("    The editor caught potential errors.")
    print("    Specialization + collaboration = better results.")
    print()


# ==============================================================================
# PART 4: COMPUTER USE (Simulated)
# ==============================================================================
# The agent takes screenshots and controls mouse/keyboard.
# We simulate this with a toy desktop environment.
# ==============================================================================

class SimulatedDesktop:
    """
    A toy desktop with windows and buttons.
    The agent interacts by 'clicking' and 'typing'.
    """
    def __init__(self):
        self.screen = {
            "active_window": "desktop",
            "desktop": {
                "buttons": ["Browser", "Calculator", "Notepad"],
                "text_fields": {}
            },
            "browser": {
                "url": "about:blank",
                "buttons": ["Search", "Back"],
                "text_fields": {"address_bar": ""}
            },
            "calculator": {
                "display": "0",
                "buttons": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "=", "Clear"],
                "text_fields": {}
            }
        }
        self.history = []

    def screenshot(self):
        """Return a text description of the current screen."""
        window = self.screen["active_window"]
        state = self.screen[window]
        desc = f"Window: {window}\n"
        if "url" in state:
            desc += f"URL: {state['url']}\n"
        if "display" in state:
            desc += f"Display: {state['display']}\n"
        desc += f"Buttons: {state['buttons']}\n"
        if state['text_fields']:
            desc += f"Text fields: {list(state['text_fields'].keys())}\n"
        return desc

    def click(self, button_name):
        """Simulate a mouse click on a button."""
        self.history.append(f"click({button_name})")
        window = self.screen["active_window"]
        state = self.screen[window]

        if button_name not in state["buttons"]:
            return f"Error: No button named '{button_name}' in {window}"

        if button_name == "Browser":
            self.screen["active_window"] = "browser"
            return "Opened Browser"
        elif button_name == "Calculator":
            self.screen["active_window"] = "calculator"
            return "Opened Calculator"
        elif button_name == "Clear":
            self.screen["calculator"]["display"] = "0"
            return "Cleared calculator"
        elif button_name == "=":
            try:
                result = eval(self.screen["calculator"]["display"])
                self.screen["calculator"]["display"] = str(result)
                return f"Result: {result}"
            except:
                return "Error in calculation"
        elif button_name in "0123456789+-*/.":
            if self.screen["calculator"]["display"] == "0":
                self.screen["calculator"]["display"] = button_name
            else:
                self.screen["calculator"]["display"] += button_name
            return f"Pressed {button_name}"
        else:
            return f"Clicked {button_name}"

    def type_text(self, field, text):
        """Simulate typing into a text field."""
        self.history.append(f"type({field}, '{text}')")
        window = self.screen["active_window"]
        if field in self.screen[window]["text_fields"]:
            self.screen[window]["text_fields"][field] = text
            if field == "address_bar":
                self.screen[window]["url"] = text
            return f"Typed '{text}' into {field}"
        return f"Error: No field named '{field}'"


class ComputerUseAgent:
    """Agent that controls a computer via screenshots and clicks."""
    def __init__(self):
        self.desktop = SimulatedDesktop()

    def run(self, task):
        """Complete a task by interacting with the GUI."""
        print(f"  TASK: {task}")
        print()

        steps = []

        # Plan based on task
        if "calculate" in task.lower():
            expression = task.split("calculate")[-1].strip()
            steps = [
                ("screenshot", None),
                ("click", "Calculator"),
                ("screenshot", None),
                ("click", "Clear"),
            ]
            # Type each character
            for char in expression.replace(" ", ""):
                if char in "0123456789+-*/.":
                    steps.append(("click", char))
            steps.extend([
                ("click", "="),
                ("screenshot", None),
            ])
        elif "open browser" in task.lower():
            steps = [
                ("screenshot", None),
                ("click", "Browser"),
                ("screenshot", None),
                ("type", ("address_bar", "example.com")),
                ("screenshot", None),
            ]

        # Execute steps
        for action, param in steps:
            if action == "screenshot":
                print("  [Screenshot]")
                print(self.desktop.screenshot())
            elif action == "click":
                result = self.desktop.click(param)
                print(f"  [Action] click('{param}') -> {result}")
            elif action == "type":
                field, text = param
                result = self.desktop.type_text(field, text)
                print(f"  [Action] type('{field}', '{text}') -> {result}")
            print()

        print("  TASK COMPLETE")
        print()


def demonstrate_computer_use():
    """Show agent controlling a simulated GUI."""
    print("=" * 60)
    print("PART 4: COMPUTER USE (Simulated)")
    print("=" * 60)
    print()
    print("  The agent sees the screen and controls mouse/keyboard.")
    print("  No APIs needed — it uses the same interface as a human.")
    print()

    agent = ComputerUseAgent()

    task = "Calculate 12 + 15 * 2"
    agent.run(task)

    print("  KEY INSIGHT:")
    print("    The agent opened the calculator app by clicking its icon.")
    print("    It pressed buttons just like a human would.")
    print("    It read the display to confirm the result.")
    print("    This works on ANY app, even ones without APIs.")
    print()


# ==============================================================================
# VISUALIZATION: AGENT ARCHITECTURE
# ==============================================================================

def visualize_agent_architecture():
    """Draw a diagram of the agent loop."""
    print("=" * 60)
    print("VISUALIZATION: AGENT ARCHITECTURE")
    print("=" * 60)
    print()

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Draw boxes
    boxes = [
        (5, 8.5, "User Task", "lightblue"),
        (5, 7, "LLM (Brain)", "lightgreen"),
        (2, 5, "Think\n(Reasoning)", "wheat"),
        (8, 5, "Act\n(Tool Call)", "salmon"),
        (5, 3, "Observe\n(Tool Result)", "lightyellow"),
        (5, 1.5, "Final Answer", "lightcyan"),
    ]

    for x, y, text, color in boxes:
        rect = plt.Rectangle((x-1.2, y-0.5), 2.4, 1, 
                             facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=11, fontweight='bold')

    # Draw arrows
    arrows = [
        (5, 8, 5, 7.5),    # Task -> LLM
        (5, 6.5, 2, 5.5),  # LLM -> Think
        (2, 4.5, 8, 4.5),  # Think -> Act
        (8, 4.5, 5, 3.5),  # Act -> Observe
        (5, 2.5, 5, 2),    # Observe -> Answer
        (5, 2.5, 5, 7.5),  # Observe -> LLM (loop back)
    ]

    for x1, y1, x2, y2 in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle="->", color='black', lw=2))

    # Loop label
    ax.text(7.5, 5.5, "Loop", fontsize=10, style='italic', color='red')

    ax.set_title("AI Agent: Perceive -> Plan -> Act -> Observe", 
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase27/agent_architecture.png', dpi=150)
    print("  Plot saved: src/phase27/agent_architecture.png")
    plt.close()
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 27: AGENTIC AI")
    print("=" * 60)
    print()
    print("  Goal: Give the model tools so it can DO things.")
    print()

    # Part 1: Basic Agent
    demonstrate_ai_agent()

    # Part 2: ReAct
    demonstrate_react()

    # Part 3: Multi-Agent
    demonstrate_multi_agent()

    # Part 4: Computer Use
    demonstrate_computer_use()

    # Visualization
    visualize_agent_architecture()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Simple agent that picks and calls tools")
    print("    - ReAct agent with explicit reasoning trace")
    print("    - Multi-agent system (Researcher + Writer + Editor)")
    print("    - Simulated computer use (GUI control)")
    print()
    print("  KEY INSIGHTS:")
    print("    1. Tools extend a model beyond its training data.")
    print("    2. ReAct makes the decision process transparent.")
    print("    3. Multi-agent specialization beats single generalist.")
    print("    4. Computer use works when no API exists.")
    print()
    print("  THE PATTERN:")
    print("    Perceive -> Plan -> Act -> Observe -> Repeat")
    print()
    print("  NEXT QUESTION:")
    print("    'The model can act with tools. Can it also SEE")
    print("     images and understand the visual world?'")
    print("=" * 60)
