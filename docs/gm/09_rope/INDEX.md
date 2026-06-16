# Part 9: RoPE (Rotary Position Embedding)

> Relative position encoding. Train on 256 tokens, generate 10,000.

## Files

- [what_is_rope.md](what_is_rope.md) — Full treatment

## Key insight

Instead of assigning position 47 a fixed embedding, rotate the query and key vectors by an angle proportional to position. The attention score depends only on relative distance (i-j), not absolute position. No new parameters. No sequence length limit.

## Connection to the curriculum

- Builds on attention mechanism fundamentals
- Replaces learned position embeddings (pos_emb = nn.Embedding)
- Used by every frontier LLM: Llama, Mistral, Gemma, Qwen

## Code impact

cortexcode: Replace `self.pos_emb = nn.Embedding(max_seq_len, dim)` with `apply_rotary_emb(q, k, positions)`. ~30 lines. Train on block_size=128, serve at block_size=1024.
