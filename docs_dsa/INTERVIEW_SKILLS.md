# INTERVIEW_SKILLS.md

## HOW TO INTERVIEW WELL

A tactical guide on performance, not just problem solving.
Interviews are evaluated on signal, not just correctness. The interviewer is tired, has back-to-back meetings, and wants to say yes. Your job is to make that easy.

---

## 1. The Communication Protocol

### Why Thinking Aloud Is Non-Negotiable

If you say nothing, the interviewer assumes you know nothing. Silence creates anxiety on both sides. Narration is not optional; it is the primary signal of competence. However, narration must be deliberate. Raw stream-of-consciousness is as bad as silence.

Communication converts internal thought into external evidence. The interviewer cannot grade what they cannot observe.

### The 4-Phase Verbal Structure

Every coding problem should move through these phases explicitly.

| Phase | Goal | Time Budget |
|---|---|---|
| Clarify | Understand the problem and constraints. | 2-4 min |
| Explore | Propose approaches, discuss trade-offs. | 3-6 min |
| Implement | Write clean, structured code. | 10-20 min |
| Verify | Test and analyze complexity. | 3-5 min |

### Scripts for Each Phase

#### Phase 1: Clarify

Use these exact phrases to demonstrate rigor:

- "Before I start, I want to make sure I understand the constraints. Are the inputs always valid, or should I handle edge cases like null or empty arrays?"
- "What is the expected range of N? Is it small enough for a quadratic solution, or should I aim for linear?"
- "Can I modify the input, or should I treat it as immutable?"
- "What should I return if there is no valid solution?"
- "Are there duplicates in the input, and does that change the expected output?"

Do not ask for hints disguised as clarification. Ask about scope, scale, and contract.

#### Phase 2: Explore

Signal that you are evaluating options, not guessing.

- "My first instinct is a brute-force approach using nested loops, which would be O(N^2). It is correct but likely too slow for large inputs."
- "I see a substructure here that suggests dynamic programming. Let me think if the optimal solution can be built from smaller optimal solutions."
- "This looks like a graph traversal problem. I am considering BFS because we need the shortest path, but DFS might work if the graph is a tree."
- "I will park the optimal solution for a moment and verify my intuition with a small example."

Always name the time and space complexity of each approach you mention.

#### Phase 3: Implement

Narrate structure, not keystrokes.

- "I will write the helper function first, then the main logic."
- "I am using a hash map here to store indices so the lookup is O(1)."
- "I am extracting this block into a helper to keep the main function readable."

If you need 20-30 seconds of pure silence to think about a tricky index calculation, say: "I need a moment to work out the boundary condition here." Then go silent. Do not mumble.

#### Phase 4: Verify

Do not say "I think it works." Prove it.

- "Let me trace this with the example input [2, 7, 11, 15] and target 9."
- "Let me check the edge case where the array is empty."
- "The time complexity is O(N) because we do a single pass. Space is O(N) for the hash map."

### When to Be Silent vs When to Narrate

Narrate when:
- Transitioning between phases.
- Choosing between two approaches.
- Writing high-level structure.
- Fixing a bug.

Be silent when:
- Performing arithmetic or index math.
- Writing a standard pattern you have written 50 times (e.g., binary search loop).
- Walking through a trace you have already announced.

If your silence exceeds 30 seconds, break it with a status update: "Still working through the pointer logic."

---

## 2. Getting Unstuck

### The 3-Minute Rule

If you have made zero progress on a new approach for 3 minutes, you are in a rut. You must change tactics. Do not double down on a dead end out of pride. The interviewer is watching the clock.

### Escalation Ladder

When stuck, escalate through these steps in order. Announce each step.

1. **Example**: "Let me plug in the example input and see what happens manually."
2. **Brute Force**: "I will write the naive solution first to make sure I understand the problem, then optimize."
3. **Optimize**: "The bottleneck is the inner loop. Can I replace it with a hash map or sort?"
4. **Hint**: "I am stuck on how to handle the cyclic dependency. Is there a standard pattern or data structure I should consider here?"

### How to Ask for a Hint Without Looking Bad

Bad: "I do not know. Can you tell me?"
Good: "I have tried a greedy approach and a DP approach, but both fail on this case. Is the correct path related to graph theory, or am I missing a constraint?"

Frame the hint request as a targeted question about a category or pattern, not a request for the answer. This shows you have done the work.

### What to Do When You Realize Your Approach Is Wrong Mid-Implementation

Stop immediately. Do not try to patch a broken foundation.

1. Announce the mistake: "I see a problem. My current approach fails when the input has duplicates because I am overwriting the index."
2. State the impact: "This means my hash map strategy needs to store lists of indices, not single values."
3. Decide: If the fix is local, apply it. If the fix invalidates the whole approach, backtrack to the Explore phase. Say: "I need to reconsider the approach. The core issue is that I assumed sorted input. Let me restart with a different structure."

Interviewers respect self-correction. They do not respect blind persistence.

---

## 3. Whiteboard / Virtual Interview Mechanics

### Code Structure First, Details Second

Write the function signature, then the high-level steps as comments or pseudocode. Fill in the implementation only after the skeleton is correct. This prevents rewriting half the board when you realize you missed a step.

Example:
```python
def solve(nums, target):
    # 1. Build a frequency map
    # 2. Iterate and check for complement
    # 3. Return indices
```

### Variable Naming Under Pressure

Do not use `a`, `b`, `c`, `x`, `y` unless they are standard mathematical notation (e.g., coordinates). Use names that telegraph intent.

Bad: `d`, `m`, `res`
Good: `char_freq`, `max_window`, `result_indices`

If you start with a bad name, rename it as soon as you realize. Say: "I am renaming `m` to `char_freq` to be clearer."

### Testing Your Solution Verbally

Never skip the trace. Pick a non-trivial example and walk through it line by line.

- State the initial values of all variables.
- State what changes on each iteration.
- State the final return value.
- Then state a second example: an edge case.

### Common Virtual Interview Pitfalls

- **Screen sharing**: Share only the IDE or editor, not your entire desktop. Close unrelated tabs and notifications before the call.
- **Audio**: Use headphones. Echo is unprofessional and wastes time. Test your mic beforehand.
- **Internet**: If your connection is unstable, warn the interviewer at the start. Offer to turn off video if bandwidth is an issue.
- **Typing noise**: If you use a mechanical keyboard, consider a noise gate or mute when not speaking.
- **IDE shortcuts**: Do not rely on Copilot or AI autocomplete. Many interviewers consider it a gray area; disable it to avoid an awkward conversation.
- **Eye contact**: Look at the camera when talking, not the screen. This takes practice.
- **Environment**: Ensure your background is neutral and you will not be interrupted. Lock the door.

---

## 4. Behavioral Interview (STAR Method)

### Situation-Task-Action-Result Framework

Every answer must have four parts. Do not skip any.

1. **Situation**: One sentence of context. Where were you? What team?
2. **Task**: What was your responsibility? What was the stakes?
3. **Action**: What did *you* do? Use "I," not "we." Be specific. This is the longest section.
4. **Result**: What was the outcome? Quantify if possible. Revenue, latency, bug count, user satisfaction.

If the result was negative, add a fifth part: **What you learned** and how you applied it later.

### 5 Stories Every Candidate Should Prepare

| Story Theme | What They Are Testing | Example Angle |
|---|---|---|
| Conflict | Can you disagree without being disagreeable? | Disagreed with a tech lead on architecture. Presented data. Found a hybrid solution. |
| Failure | Do you own your mistakes? | Pushed code that caused a 2-hour outage. Owned the rollback. Wrote the postmortem. Implemented CI check to prevent recurrence. |
| Leadership | Can you influence without authority? | Led a refactoring initiative by building a proof-of-concept and getting buy-in from skeptical senior engineers. |
| Impact | Can you deliver business value? | Reduced API latency by 40 percent by identifying an N+1 query and introducing caching. |
| Learning | Can you grow from feedback? | Received feedback that my code reviews were too harsh. Changed my review style to include praise and open-ended questions. |

Write these stories down. Practice them out loud. Time them. Each should be 2-3 minutes.

### How to Prepare Stories That Also Show Technical Depth

Embed specific technical details into the Action and Result sections.

- "I introduced a write-behind cache using Redis, which dropped our P99 latency from 800ms to 120ms."
- "The root cause was a race condition in our async task queue. I added idempotency keys and a distributed lock."
- "I wrote a load test in k6 to prove the bottleneck was in the database connection pool, not the application logic."

Technical depth in behavioral answers signals seniority.

### The "Why This Company?" Answer Framework

Do not say "I am passionate about technology" or "I want to work with smart people." Those are generic and forgettable.

Use this structure:

1. **Specific product or problem**: "I have been using your payments API for two side projects, and I admire how you abstracted PCI compliance."
2. **Specific technology or scale**: "I read your blog post on migrating from Kafka to Pulsar for multi-region durability. That is the scale of distributed systems problem I want to work on."
3. **Personal alignment**: "Your engineering values mention "shipping over perfection." That resonates with me because I have seen how over-engineering kills momentum."

Research the company. Cite a blog post, a talk, or a product feature. If you cannot find anything specific, you have not done your homework.

---

## 5. System Design Signals

### When to Bring Up Trade-offs

Bring up trade-offs as soon as you propose a component. Do not wait to be asked.

- "I am choosing a SQL database here because we need ACID transactions. If we later need to shard by user ID, we will face cross-shard join complexity, which I am flagging now."
- "A cache will improve read latency but introduces eventual consistency. For this use case, a 5-second staleness is acceptable."

Trade-offs demonstrate engineering maturity.

### How to Show Breadth vs Depth

Start broad. Sketch the full system with boxes and arrows. Then dive deep on one or two components based on the interviewer's interest.

- Breadth: "Here is the client, the CDN, the API gateway, the load balancer, the application servers, the database, and the message queue."
- Depth: "Let me zoom into the database layer. I am choosing a leader-follower replication model with read replicas to handle the 10:1 read-write ratio."

If the interviewer asks about a different component, pivot smoothly. Do not cling to the area you prepared.

### The CLAPS Framework

Use CLAPS to structure your system design narrative.

- **C**onstraints: Ask about functional and non-functional requirements. Scale? Latency? Durability?
- **L**oad: Estimate QPS, storage, and bandwidth. Show your math.
- **A**PI: Define the interface first. What are the inputs and outputs?
- **P**attern: Choose architectural patterns (microservices, event-driven, CQRS) and justify them.
- **S**cale: Discuss how the system grows. Sharding, replication, caching, rate limiting.

Do not skip the back-of-the-envelope math. It is a signal of rigor.

---

## 6. Red Flags & Green Flags

### 10 Things That Make Interviewers Say No

1. **Silent coding**: The candidate writes code for 15 minutes without speaking. The interviewer has no signal.
2. **Ignoring hints**: The interviewer suggests an optimization, and the candidate dismisses it or does not hear it.
3. **No complexity analysis**: The candidate finishes the code but never discusses time or space complexity.
4. **No testing**: The candidate claims the code works but never traces an example.
5. **Overconfidence**: The candidate asserts a wrong answer without checking. "This is obviously O(N)." It is not.
6. **Blaming the platform**: "The whiteboard is too small," "The connection is bad." These may be true, but they do not earn points.
7. **Answering a different question**: The candidate solves a harder version of the problem and ignores the actual prompt.
8. **Incoherent variable names**: Code is unreadable because every variable is a single letter with no context.
9. **No clarifying questions**: The candidate jumps into code without understanding constraints and has to rewrite.
10. **Defensiveness**: When challenged, the candidate argues rather than explores. "No, that is wrong." instead of "Let me check that case."

### 10 Things That Make Interviewers Say Yes

1. **Explicit phase transitions**: "I have clarified the problem. Now I will explore two approaches." This is easy to follow.
2. **Self-correction**: The candidate catches their own bug and fixes it cleanly.
3. **Trade-off discussion**: The candidate explains why they chose approach A over B.
4. **Clean code structure**: Functions are short. Logic is separated. Naming is clear.
5. **Edge case awareness**: The candidate proactively tests empty input, duplicates, or integer overflow.
6. **Listening to hints**: The interviewer nudges, and the candidate integrates the hint seamlessly. "That is a good point. I can use a heap here instead of sorting."
7. **Strong behavioral stories**: STAR format, quantified results, technical depth.
8. **Back-of-the-envelope math**: In system design, the candidate estimates load and capacity with reasonable assumptions.
9. **Enthusiasm and curiosity**: The candidate asks a genuine question about the team or the company's infrastructure at the end.
10. **Professionalism**: On time, prepared, camera on, no distractions. Basics matter.

---

## 7. Post-Interview Reflection

### Self-Assessment Rubric

Rate yourself 1-5 on each dimension immediately after the interview while it is fresh.

| Dimension | 1 (Poor) | 5 (Excellent) |
|---|---|---|
| Problem Understanding | Did not ask clarifying questions. | Fully mapped constraints and edge cases. |
| Approach Quality | Chose a brute force and never improved. | Found optimal solution and discussed alternatives. |
| Communication | Silent or rambling. | Clear phase transitions, concise narration. |
| Code Quality | Unreadable, buggy. | Clean, modular, well-named. |
| Verification | Skipped testing. | Thorough trace and complexity analysis. |
| Behavioral | Vague, no structure. | STAR format, specific, technical. |
| System Design | No trade-offs, no math. | CLAPS framework, justified decisions. |

### What to Write Down Within 30 Minutes

- The exact problem statement(s) asked.
- Your initial approach and the approach you ended with.
- Any hints the interviewer gave.
- Any questions you asked that landed well or fell flat.
- One thing you did well.
- One thing you would do differently.

This log is your study guide. Patterns will emerge over multiple interviews.

### How to Improve for Next Time

1. **Targeted practice**: If you were slow on dynamic programming, spend the next three days on DP problems. Do not generalize.
2. **Mock interviews**: Do a mock interview with a peer. Ask them to evaluate you on the rubric above, not just correctness.
3. **Record yourself**: Record a 45-minute self-mock. Watch for filler words ("um," "like"), long silences, and unclear explanations.
4. **Fix one thing**: Do not try to overhaul everything. Pick the lowest-scoring dimension from your rubric and fix it for the next round.
5. **Sleep and schedule**: Do not schedule interviews back-to-back on the same day. Cognitive performance degrades significantly after 90 minutes of high-stakes problem solving.

---

## Checklist: Before Every Interview

- [ ] Camera and microphone tested.
- [ ] IDE or whiteboard environment ready. Notifications off.
- [ ] One glass of water within reach.
- [ ] Company-specific research complete (one blog post or product feature noted).
- [ ] Two STAR stories mentally rehearsed.
- [ ] Example inputs prepared for common patterns (empty array, single element, all duplicates).
- [ ] Alarm set for 10 minutes before the interview to settle in.
- [ ] Questions for the interviewer written down.

## Checklist: During the Interview

- [ ] Clarified constraints before coding.
- [ ] Discussed at least two approaches.
- [ ] Stated time and space complexity.
- [ ] Used descriptive variable names.
- [ ] Traced at least one non-trivial example.
- [ ] Asked one genuine question at the end.

## Checklist: After the Interview

- [ ] Wrote down problem details within 30 minutes.
- [ ] Completed the self-assessment rubric.
- [ ] Scheduled time to practice the weakest dimension.
- [ ] Sent a brief thank-you email within 24 hours (optional but positive).
