# Part 6: Flow Matching

> The straight-line path from noise to data. Fewer steps, same quality.

## Files

- [what_is_flow_matching.md](what_is_flow_matching.md) — Full treatment (Problem, Definition, Analogy, Numeric, Confusion, Properties, Comparison, Connection)

## Key insight

DDPM follows a curved path (Brownian random walk) from noise to data. Flow matching follows a straight line. Generation goes from 1000 steps to 20. Same model, same data, same training time. 50× faster inference.

## Connection to the curriculum

- Builds on [Part 2 (Diffusion)](../02_diffusion/)
- Complements [Part 3 (Latent Diffusion)](../03_latent_diffusion/) — apply flow matching in latent space for best results
- Leads into test-time optimization techniques

## Code impact

logogen: Replace DDPM ODE with Euler integration along straight path. ~30 lines. Generation from 30s → <1s.
