"""
Phase 72: Real Agents with Tool Use — NumPy Concept Demo
--------------------------------------------------------
This script simulates a ReAct agent using only NumPy and standard library.
It demonstrates:
  - Tool use (calculator, search)
  - ReAct loop: Thought -> Action -> Observation
  - Multi-turn state tracking
  - Visualization of tool usage and success rate
"""

import os
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. TOOL DEFINITIONS
# ---------------------------------------------------------------------------
def calculator(a, b, op):
    """Simple calculator tool."""
    if op == 'add':
        return a + b
    elif op == 'sub':
        return a - b
    elif op == 'mul':
        return a * b
    elif op == 'div':
        return a / b if b != 0 else float('inf')
    else:
        return None

def search(query):
    """Mock search tool returning a numeric fact."""
    facts = {
        'population tokyo': 37.4,
        'population paris': 2.1,
        'area france': 643801,
        'gdp usa': 23320,
    }
    return facts.get(query.lower(), random.uniform(10, 100))

# ---------------------------------------------------------------------------
# 2. AGENT LOGIC (ReAct loop)
# ---------------------------------------------------------------------------
class SimpleAgent:
    def __init__(self):
        self.state = {
            'turn': 0,
            'history': [],
            'tool_counts': {'calculator': 0, 'search': 0},
            'success_history': [],
        }

    def decide_tool(self, task):
        """Decide which tool to use based on simple keyword matching."""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ['calculate', 'math', 'plus', 'minus', 'times', 'divided', 'sqrt', '*', '+', '-', '/']):
            return 'calculator'
        else:
            return 'search'

    def react_loop(self, tasks):
        """Run ReAct loop over a list of tasks."""
        for task in tasks:
            self.state['turn'] += 1
            turn_num = self.state['turn']

            # THOUGHT
            tool_name = self.decide_tool(task)
            thought = f"Turn {turn_num}: I need to use {tool_name} to solve '{task}'."
            print(thought)

            # ACTION
            action = None
            observation = None
            success = False

            if tool_name == 'calculator':
                # Simulate parsing numbers from task
                nums = [int(s) for s in task.split() if s.isdigit()]
                if len(nums) >= 2:
                    a, b = nums[0], nums[1]
                    if 'plus' in task or '+' in task:
                        observation = calculator(a, b, 'add')
                    elif 'minus' in task or '-' in task:
                        observation = calculator(a, b, 'sub')
                    elif 'times' in task or '*' in task:
                        observation = calculator(a, b, 'mul')
                    elif 'divided' in task or '/' in task:
                        observation = calculator(a, b, 'div')
                    else:
                        observation = calculator(a, b, 'add')
                    action = f"calculator({a}, {b}) -> {observation}"
                    success = True
                else:
                    observation = "Error: not enough numbers"
                    action = "calculator(parse_error)"
                    success = False
            else:
                # SEARCH
                observation = search(task)
                action = f"search('{task}') -> {observation}"
                success = True

            # Update state
            self.state['tool_counts'][tool_name] += 1
            self.state['history'].append({
                'turn': turn_num,
                'task': task,
                'tool': tool_name,
                'thought': thought,
                'action': action,
                'observation': observation,
                'success': success,
            })
            self.state['success_history'].append(1 if success else 0)

            # OBSERVATION printed
            print(f"  Action: {action}")
            print(f"  Observation: {observation}")
            print(f"  Success: {success}\n")

        return self.state

# ---------------------------------------------------------------------------
# 3. RUN SIMULATION
# ---------------------------------------------------------------------------
tasks = [
    "Calculate 15 plus 27",
    "What is the population of Tokyo",
    "Calculate 100 divided by 5",
    "What is the area of France",
    "Calculate 8 times 7",
    "Search GDP USA",
    "Calculate 50 minus 20",
    "Search population Paris",
]

agent = SimpleAgent()
final_state = agent.react_loop(tasks)

# ---------------------------------------------------------------------------
# 4. PLOT RESULTS
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Tool usage distribution
tools = list(final_state['tool_counts'].keys())
counts = list(final_state['tool_counts'].values())
axes[0].bar(tools, counts, color=['#3498db', '#e74c3c'])
axes[0].set_title('Tool Usage Distribution')
axes[0].set_ylabel('Count')
axes[0].set_ylim(0, max(counts) + 1)

# Plot 2: Success rate over turns
turns = np.arange(1, len(final_state['success_history']) + 1)
cumulative_success = np.cumsum(final_state['success_history'])
success_rate = cumulative_success / turns
axes[1].plot(turns, success_rate, marker='o', linestyle='-', color='#2ecc71')
axes[1].set_title('Success Rate Over Turns')
axes[1].set_xlabel('Turn')
axes[1].set_ylabel('Cumulative Success Rate')
axes[1].set_ylim(0, 1.1)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
output_path = os.path.join(os.path.dirname(__file__), 'real_agents.png')
plt.savefig(output_path)
print(f"Plot saved to {output_path}")
