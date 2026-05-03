# What is Method Archaeology?

## Problem it Solves
Papers are space-constrained and often leave out initialization schemes, learning rate schedules, or data preprocessing. These omitted details can dominate final performance.

## Definition
Method archaeology is the investigative work of recovering hidden implementation details from released code, author correspondence, or careful ablation. It treats the full method as an artifact that must be excavated.

## Analogy
Method archaeology is like restoring an ancient machine from a partial diagram. The diagram shows the gears, but the archaeologist must infer the missing springs and lubricants by studying working replicas.

## Example
A paper reports state-of-the-art results but does not specify batch normalization momentum. By examining the authors' official repository, a reader discovers momentum=0.9, which turns out to be critical for convergence.

## Common Confusion
Method archaeology is not reverse engineering. Reverse engineering aims to clone a black-box system; method archaeology aims to understand and document the scientific details that a paper failed to report.

## Code Location
See `src/phase93/phase93_paper_reading.py` for an example where missing initialization details are recovered and their impact is measured.
