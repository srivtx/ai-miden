# What is Perplexity Filtering?

## Why it exists (THE PROBLEM first)

Some documents are grammatically correct but still worthless for training: random word salads, machine-generated spam, or text in the wrong language. Simple length and punctuation filters miss these. A language model can score how "surprised" it is by a document, flagging outliers.

## Definition (very simple)

Perplexity filtering uses a reference language model to compute the perplexity of each document. Documents with extremely high perplexity (the model is very surprised) or extremely low perplexity (the model has memorized them) are flagged for removal.

## Real-life analogy

A fluent English speaker reading a sentence like "Colorless green ideas sleep furiously" is not surprised by grammar but is surprised by meaning. Perplexity measures that surprise. A document that makes the model far more surprised than average is probably low quality.

## Tiny numeric example

A reference model computes average perplexity on a held-out set of 50. A new document receives perplexity 2,000. This is 40 times higher than average, indicating the document is likely garbled or in a different language. It is removed.

## Common confusion

- **High perplexity does not always mean bad text.** A valid physics paper may contain rare technical terms that surprise a general-domain model.
- **Perplexity filtering is not a spam detector.** It measures linguistic surprise, not intent or topic.
- **The reference model matters.** A model trained on tweets will score legal documents poorly.
- **It is computationally expensive.** Running a forward pass on every candidate document adds significant preprocessing cost.
- **Perplexity is not accuracy.** It is an inverse probability measure, not a direct quality label.

## Where it is used in our code

In `src/phase89/phase89_data_pipelines.py`, we mention perplexity as a conceptual quality signal. While our toy example uses simpler heuristics (length and punctuation ratio), the pipeline structure is identical: score each document, set a threshold, and keep only those that pass.
