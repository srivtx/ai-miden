# What is a Multi-Turn Agent?

## 1. Why it exists (THE PROBLEM)
A chatbot that resets its memory after every message is useless for complex workflows. If you say "Book me a flight to Paris" and then "Make it business class," a single-turn system forgets the destination. Multi-turn agents maintain state (memory, context, plan) across many exchanges so they can handle long, evolving tasks.

## 2. Definition
A Multi-Turn Agent is an autonomous system that persists information (history, variables, plans) across multiple interaction cycles (turns), allowing it to refine goals, correct mistakes, and execute multi-step strategies.

## 3. Real-life analogy
A project manager running a week-long project. Each morning they hold a stand-up (turn). They review yesterday's notes (memory), decide today's tasks (planning), execute them (action), and write new notes (state update). By Friday, the accumulated state lets them deliver the final report.

## 4. Tiny numeric example
Turn 1: User asks "What is 15% of 200?"
- Agent state: `{'history': [], 'current_task': 'calc_percent'}`
- Action: calculator(200, 0.15) → Observation: 30
- State update: `{'history': [('Q1', 30)], 'current_task': 'done'}`

Turn 2: User asks "Now add 10 to that."
- Agent reads history, sees previous result = 30.
- Action: calculator(30, 10) → Observation: 40
- State update: `{'history': [('Q1', 30), ('Q2', 40)], 'current_task': 'done'}`

Without state, the agent would not know what "that" refers to.

## 5. Common confusion
- **"Multi-turn just means a long conversation."** No. It means the agent actively uses accumulated state to change its behavior.
- **"Memory is unlimited."** No. Context windows are finite; agents use summarization or external memory stores.
- **"State is only the chat history."** No. State can include plans, retrieved documents, error counts, and user preferences.
- **"Multi-turn agents never make mistakes."** They can compound errors across turns if observations are wrong.
- **"You need a database for state."** Helpful, but state can live in a simple Python dictionary for small demos.
- **"All LLM chats are multi-turn agents."** A basic chat API replays history but does not reason or plan across turns.
- **"Planning is automatic."** The agent must be explicitly designed to plan and update its plan each turn.

## 6. Where it is used in our code
`src/phase72/phase72_real_agents.py` tracks agent state in a dictionary (`agent_state`) that records turn count, tool usage history, success flags, and observations. `src/phase72/phase72_real_agents_colab.py` maintains a conversation history list and updates it after every Thought/Action/Observation cycle, enabling the agent to reference earlier turns.
