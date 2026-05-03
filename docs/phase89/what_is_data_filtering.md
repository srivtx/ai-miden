# What is Data Filtering?

## Why it exists (THE PROBLEM first)

The internet is full of low-quality text: spam, ads, garbled HTML, code snippets with no context, and pages written by bots. Feeding this noise into a language model teaches it bad grammar, biases, and nonsensical patterns. Garbage in, garbage out.

## Definition (very simple)

Data filtering is the process of selecting training examples that meet quality, length, language, and content criteria while discarding the rest.

## Real-life analogy

A gold panner sifts river sediment through a mesh, letting sand and pebbles wash away while retaining gold flakes. Data filtering is the mesh: it lets low-quality documents wash away while retaining valuable training text.

## Tiny numeric example

A raw dataset contains 10 million documents. A filter removes documents shorter than 100 characters (3 million), documents where more than 50% of characters are punctuation (1 million), and documents not in English (2 million). The remaining 4 million documents are higher average quality and train a better model.

## Common confusion

- **Filtering is not the same as deduplication.** Filtering removes low-quality single documents; deduplication removes redundant copies.
- **Aggressive filtering does not guarantee a better model.** It can accidentally remove rare but valuable documents.
- **Filtering rules are not universal.** A rule that works for English may delete valid Chinese text.
- **It is not always about removing data.** Sometimes filtering means re-weighting or tagging examples rather than deleting them.
- **Manual filtering does not scale.** At web scale, filtering must be automated with heuristics or classifier models.

## Where it is used in our code

In `src/phase89/phase89_data_pipelines.py`, we define a `quality_score` function that penalizes short texts and texts with excessive punctuation. We apply it to an array of document statistics and print which documents pass or fail the filter.
