### 1. Why it exists (THE PROBLEM first)
A raw GPT model is essentially a text-completion engine. When you feed it "What is the capital of France?" it does not recognize that you are asking a factual question requiring a specific answer. Instead, it treats the input as an incomplete sentence and continues it however the statistics of its training data suggest. It lacks the concept of a "user instruction" versus a "system response."

### 2. Definition (very simple)
Instruction following is the capability of a language model to recognize that a given input is a directive or question from a user, and to generate an appropriate, context-aware response rather than simply completing the text stream.

### 3. Real-life analogy
Think of teaching a child the difference between "Tell me a story" and "What is 2+2?" It is the same child with the same vocabulary, but they must learn to switch modes: creative narration for the first request, and a brief factual answer for the second. Instruction following is that contextual switch.

### 4. Tiny numeric example
Input prompt formatted for training:
```
User: What is 2+2?
Assistant:
```
Target output:
```
4
```
The model learns that whenever the text pattern ends with `Assistant:`, the next tokens should be a helpful answer to the preceding user question, not a random continuation.

### 5. Common confusion
- **Instruction following is not the same as SFT.** SFT is the *training method*; instruction following is the *resulting behavior*.
- **It does not require new knowledge.** The model already knows that 2+2=4; instruction following just teaches it *when* to deploy that knowledge.
- **System prompts matter.** Adding "You are a helpful assistant" is part of setting the instruction context, but the model must first learn to respect that context.
- **Not all instructions are questions.** "Summarize this paragraph" is an instruction too, and the model must learn to recognize the task type from the wording.

### 6. Where it is used in our code
Brief mention: Our training data is explicitly formatted with user and assistant tags so the model learns instruction-following patterns during the SFT stage.
