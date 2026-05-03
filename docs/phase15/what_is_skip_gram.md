# What Is Skip-gram?

## 1. Why it exists (THE PROBLEM first)
We need a way to learn word embeddings from raw text without any human-provided labels. There is no pre-existing mapping telling us that "cat" and "feline" are similar. We must create a self-supervised task from plain sentences alone.

## 2. Definition (very simple)
Skip-gram is a self-supervised training algorithm that predicts the surrounding context words given a center word. By forcing the model to guess "what words appear near X," the model learns meaningful vectors for X.

## 3. Real-life analogy
A friend describing someone by listing who they hang out with. "He's always with Sarah and Mike" → you infer he's social. You never needed a dictionary definition; you learned his "meaning" from his context.

## 4. Tiny numeric example
Sentence: "the cat sat"
Window size = 1
- Center word: "cat"
- Context words to predict: ["the", "sat"]
- Input: one-hot vector for "cat"
- Targets: one-hot vectors for "the" and "sat"
- Loss: how badly the model predicted "the" and "sat" from "cat"
- After many sentences, the vector for "cat" becomes meaningful because it must reliably predict its neighbors.

## 5. Common confusion
- "Is skip-gram a model or a loss function?" It is an algorithm / training objective. The model underneath is usually a simple linear projection.
- "Does it predict words to the left, right, or both?" Both. All words within the window are predicted from the center.
- "Is CBOW the opposite?" Yes. CBOW predicts the center word from context; skip-gram predicts context from the center.
- "Why window size matter?" Larger windows capture broader topics; smaller windows capture tighter syntax.
- "Do we need labels?" No. The text itself provides the supervision.

## 6. Where it is used in our code
Implements the core training loop for the embedding layer: sliding a window over tokenized text and updating vectors so that center words predict their neighbors.
