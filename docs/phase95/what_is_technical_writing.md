# What is Technical Writing?

## Problem it Solves
Research code written without comments, docstrings, or clear variable names decays into unreadable legacy within weeks. Technical writing preserves intent and reduces onboarding cost.

## Definition
Technical writing is the practice of communicating complex information clearly to a specific audience. In ML, this includes docstrings, README files, papers, and blog posts that explain design decisions.

## Analogy
Technical writing is like writing the manual for a complicated appliance. Without it, even a brilliant engineer will struggle to operate the device safely.

## Example
Instead of a variable named `x`, a technical writer uses `normalized_image_batch`. Instead of a comment "# fix", they write "# Clip gradients to avoid exploding gradients in RNN training."

## Common Confusion
Technical writing is not creative blogging. Blogging prioritizes engagement and narrative; technical writing prioritizes precision, reproducibility, and actionable instructions.

## Code Location
See `src/phase95/phase95_research_communication.py` for a comparison of poorly commented research code versus a well-documented rewrite.
