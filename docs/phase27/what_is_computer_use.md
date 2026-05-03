### 1. Why it exists (THE PROBLEM first)
Most software has a graphical user interface (GUI) with buttons, menus, and text fields. APIs are not always available. To interact with these systems — booking a flight on a website, filling out a form, or using a desktop application — an agent needs to see the screen and control the mouse and keyboard, just like a human user.

### 2. Definition (very simple)
Computer Use is the capability of an AI agent to perceive visual screen content (screenshots) and control the computer by moving the mouse, clicking, typing, and pressing keys. It treats the computer as an environment to be navigated rather than an API to be called.

### 3. Real-life analogy
A robot sitting at a desk using a mouse and keyboard. It looks at the screen (perception), decides what to click (planning), moves the mouse and clicks (action), sees what changed (observation), and repeats. It does not need special APIs — it uses the same interface a human would use.

### 4. Tiny numeric example
Task: "Go to example.com and fill out the contact form."

Step 1: Screenshot shows browser on Google homepage.
- Agent thinks: "I need to navigate to example.com."
- Agent acts: Click the address bar, type "example.com", press Enter.

Step 2: Screenshot shows example.com homepage.
- Agent thinks: "I see a 'Contact' link in the top menu."
- Agent acts: Click the "Contact" link.

Step 3: Screenshot shows a form with Name, Email, and Message fields.
- Agent thinks: "I need to fill in all three fields and submit."
- Agent acts: Click Name field, type "Alice". Click Email field, type "alice@example.com". Click Message field, type "Hello!".

Step 4: Screenshot shows the filled form.
- Agent acts: Click the "Submit" button.

Step 5: Screenshot shows "Thank you for contacting us!"
- Agent thinks: "Task complete."

### 5. Common confusion
- **Computer Use is not screen scraping.** Screen scraping reads the HTML source code. Computer Use looks at pixels (or accessibility trees) and interacts visually, making it work even on non-web applications.
- **It is slower and more fragile than APIs.** A button moving by 10 pixels can break the agent. APIs are the preferred interface when available.
- **It requires vision capabilities.** The model must be able to understand screenshots, which means it needs a vision encoder (like GPT-4o or Claude with vision).
- **Safety is a major concern.** An agent with computer use can delete files, make purchases, or send emails. It should run in a sandboxed environment with strict permission controls.
- **Not all agents need computer use.** Most production agents use APIs and tools. Computer use is for edge cases where no API exists.

### 6. Where it is used in our code
`src/phase27/phase27_agentic_ai.py` simulates computer use with a toy "desktop environment" (a dictionary of windows and buttons) that the agent navigates by taking "screenshots" and performing "clicks."
