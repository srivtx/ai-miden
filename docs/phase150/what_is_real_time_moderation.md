## What Is Real-Time Moderation?

---

### The Problem

A social media platform receives 100,000 user posts per minute. A ride-sharing app processes 50,000 support chats per hour. A gaming platform hosts 1 million voice messages per day. In each case, harmful content — hate speech, scams, threats, explicit material — must be caught and acted on within seconds. Human moderators cannot scale to this volume. Batch processing at the end of the day is too slow; the damage is already done. How do you classify and act on content fast enough to matter?

---

### Definition

**Real-time moderation** is the automated classification of user-generated inputs and model-generated outputs at production latency (typically under 100-500 milliseconds) to detect policy violations as they occur. It sits at the boundary between the user and the system, making allow/block decisions on every interaction.

**How it works:**
```
User message arrives (text, image, or audio)
  |
  v
Feature extraction (embeddings, keyword hashes, metadata)
  |
  v
Lightweight classifier (small neural net, gradient-boosted tree, or rule engine)
  |
  v
Decision in <100ms:
  ALLOW  -> pass to model or publish
  BLOCK  -> reject immediately
  FLAG   -> allow but send to human review queue
  |
  v
Action logged for audit and model improvement
```

**Key requirements:**
- **Latency:** moderation must not dominate end-to-end response time. A 5-second safety check makes a chatbot unusable
- **Throughput:** the system must handle peak load without queuing
- **Calibration:** false positives alienate users; false negatives create liability. The decision threshold must be tunable per policy
- **Multi-modal:** text, images, audio, and video each need specialized classifiers running in parallel

**Why this matters:**
- A streaming platform must blur explicit frames before they reach viewers
- A children's app must block toxic messages before the child reads them
- A financial service must flag fraud attempts during the conversation, not after the transfer

---

### Real-Life Analogy

An airport security checkpoint.
- **No real-time moderation:** Passengers board the plane, fly to their destination, and then weeks later a security team reviews footage and realizes someone smuggled a banned item. The flight is long gone. The damage is done. This is batch moderation.
- **Real-time moderation:** Every bag is X-rayed and every passenger walks through a metal detector *before* boarding. Decisions are made in seconds. If a bag looks suspicious, it is pulled aside immediately. The plane does not wait. This is real-time moderation.
- **Latency trade-off:** A full bag search takes five minutes and catches everything, but it would cause missed flights and angry passengers. The X-ray takes ten seconds and catches 95% of threats. Real-time moderation is about finding the fastest check that catches enough threats to be worth the cost.
- **Layered checks:** The X-ray catches large metal objects. A chemical swab catches explosives. A document check catches fake IDs. No single check is perfect, but together they cover the threat space in under a minute.

---

### Tiny Numeric Example

**A moderation pipeline with three classifiers:**
```
Incoming message: "You are worthless and nobody likes you."

Classifier 1 — Toxicity (small BERT, 20ms):
  Score: 0.87  -> threshold 0.8 -> FLAG

Classifier 2 — Threat detection (regex + keywords, 2ms):
  No explicit threat words -> ALLOW

Classifier 3 — Sentiment drift (running average, 1ms):
  User's last 5 messages increasingly negative -> FLAG

Decision: FLAG (send to human review, hold from public feed)
Latency: 23ms
```

**Moderation latency budget for a chatbot:**
```
Total acceptable response time: 800ms
  LLM generation:               600ms
  Input moderation:              50ms
  Output moderation:             80ms
  Network overhead:              70ms
  ---
  Remaining slack:                0ms (tight budget)
```

**Throughput scaling:**
```
Single classifier instance:  500 messages/sec
Peak load:                  10,000 messages/sec
Required replicas:          20 (with load balancing)
Cost per 1M messages:       $0.40 (small CPU-based classifier)
```

**The shift:** Real-time moderation is an engineering constraint, not just a research problem. A classifier with 99% accuracy is useless if it takes 10 seconds per sample. The winning system is the one that sits on the latency-accuracy Pareto frontier at the exact latency budget of the product.

---

### Common Confusion

1. **"Real-time moderation means processing every frame of a video."** For video, real-time usually means sampling key frames or processing audio transcripts, not every pixel of every frame. Full-frame analysis is reserved for post-hoc review or flagged content.

2. **"Lower latency always means lower accuracy."** Not necessarily. Distilled models, quantization, and hardware accelerators (TPUs, GPUs) can maintain accuracy while cutting latency. The trade-off is between engineering investment and accuracy, not an immutable law.

3. **"Real-time moderation only applies to user-generated content."** Model outputs must also be moderated in real time. A chatbot that generates toxic responses is just as harmful as a user who posts them. Output moderation is often harder because the model can be adversarially prompted.

4. **"A single global threshold works for all users."** Different user segments need different thresholds. A gaming platform might allow trash talk between adult players while blocking the same language in children's lobbies. Thresholds must be configurable per context.

5. **"False positives are less harmful than false negatives."** This depends on the product. A false positive in a creative-writing tool blocks legitimate expression and drives users away. A false negative in a child-safety product creates legal liability. The cost matrix is domain-specific.

6. **"Real-time moderation replaces human moderators."** It augments them. Real-time systems handle the volume; humans handle the ambiguity. Content flagged with borderline scores goes to human review. The system learns from human decisions to improve over time.

7. **"Moderation models are static after deployment."** Language evolves. New slang, new attack patterns, and new cultural contexts appear constantly. Moderation models must be retrained or fine-tuned regularly, with feedback loops from human review queues.

---

### Where It Is Used in Our Code

`src/phase150/phase150_safety_production_concepts.py` — We simulate a moderation pipeline with tunable latency-accuracy trade-offs. We show that aggressive thresholding reduces latency but increases false negatives, and we plot the Pareto frontier of achievable operating points.

`src/phase150/phase150_safety_production_colab.py` — We implement a real safety pipeline around Llama-3.2-3B-Instruct with regex-based input checks and a lightweight toxicity classifier on outputs. We measure end-to-end latency and show the breakdown between generation time and moderation time.

(End of file - total 97 lines)
