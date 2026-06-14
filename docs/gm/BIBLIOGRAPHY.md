# Bibliography

> Every claim in this curriculum that comes from specific research is backed by a primary source. This file lists the most important references, organized by topic. References marked **(see above)** point to a previously-listed entry in the same file.

---

## Part 0: Foundations

### Probability
- Kolmogorov, A.N. (1933). *Grundbegriffe der Wahrscheinlichkeitsrechnung.* (Foundations of the Theory of Probability.) — The axioms.
- Feller, W. (1968). *An Introduction to Probability Theory and Its Applications.* Wiley.
- Jaynes, E.T. (2003). *Probability Theory: The Logic of Science.* Cambridge University Press.

### Sampling
- Metropolis, N. et al. (1953). *Equation of state calculations by fast computing machines.* **J. Chem. Phys.** 21: 1087–1092. — The first MCMC algorithm.
- Hastings, W.K. (1970). *Monte Carlo sampling methods using Markov chains and their applications.* **Biometrika** 57(1): 97–109.
- Geman, S. & Geman, D. (1984). *Stochastic relaxation, Gibbs distributions, and the Bayesian restoration of images.* **IEEE PAMI** 6(6): 721–741.
- Neal, R.M. (1993). *Probabilistic inference using Markov chain Monte Carlo methods.* Technical Report CRG-TR-93-1.
- Roberts, G.O. & Rosenthal, J.S. (2004). *General state space Markov chains and MCMC algorithms.* **Probab. Surveys** 1: 20–71.

### KL Divergence
- Kullback, S. & Leibler, R.A. (1951). *On information and sufficiency.* **Ann. Math. Statist.** 22(1): 79–86. — The KL divergence.
- Kullback, S. (1959). *Information Theory and Statistics.* Wiley.
- Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory* (2nd ed.). Wiley. — Standard reference.

### ELBO
- Jordan, M.I. et al. (1999). *An introduction to variational methods for graphical models.* **Machine Learning** 37(2): 183–233.
- Wainwright, M.J. & Jordan, M.I. (2008). *Graphical models, exponential families, and variational inference.* **Foundations and Trends in ML** 1(1–2): 1–305.
- Blei, D.M., Kucukelbir, A. & McAuliffe, J.D. (2017). *Variational inference: a review for statisticians.* **JASA** 112(518): 859–877.

### Score Function
- Hyvärinen, A. (2005). *Estimation of non-normalized statistical models by score matching.* **JMLR** 6: 695–709. — Score matching.
- Vincent, P. (2011). *A connection between score matching and denoising autoencoders.* **Neural Computation** 23(7): 1661–1674. — Denoising score matching.
- Efron, B. (2011). *Tweedie's formula and selection bias.* **JASA** 106(496): 1602–1614. — The Tweedie identity.
- Hyvärinen, A. & Dayan, P. (2005). *Estimation of non-normalized statistical models by score matching.* **JMLR** 6: 695–709.
- Song, Y. & Ermon, S. (2019). *Generative modeling by estimating gradients of the data distribution.* **NeurIPS 2019**. — The modern score-based generation paper.

---

## Part 1: Autoencoders and VAEs

### Autoencoders
- Hinton, G.E. & Salakhutdinov, R.R. (2006). *Reducing the dimensionality of data with neural networks.* **Science** 313(5786): 504–507. — Deep autoencoders.
- Vincent, P. et al. (2008). *Extracting and composing robust features with denoising autoencoders.* **ICML 2008**. — Denoising AE.
- Rifai, S. et al. (2011). *Contractive auto-encoders: explicit invariance during feature extraction.* **ICML 2011**.

### Variational Autoencoders
- Kingma, D.P. & Welling, M. (2014). *Auto-encoding variational Bayes.* **ICLR 2014**. — The VAE paper.
- Rezende, D.J., Mohamed, S. & Wierstra, D. (2014). *Stochastic backpropagation and approximate inference in deep generative models.* **ICML 2014**. — The reparameterization trick.
- Higgins, I. et al. (2017). *β-VAE: learning basic visual concepts with a constrained variational framework.* **ICLR 2017**.
- Burda, Y., Grosse, R. & Salakhutdinov, R. (2016). *Importance weighted autoencoders.* **ICLR 2016**. — IWAE.
- van den Oord, A., Vinyals, O. & Kavukcuoglu, K. (2017). *Neural discrete representation learning.* **NeurIPS 2017**. — VQ-VAE.
- Razavi, A., van den Oord, A. & Vinyals, O. (2019). *Generating diverse high-fidelity images with VQ-VAE-2.* **NeurIPS 2019**.

### Normalizing Flows
- Dinh, L., Krueger, D. & Bengio, Y. (2015). *NICE: non-linear independent components estimation.* **ICLR Workshop 2015**.
- Dinh, L., Sohl-Dickstein, J. & Bengio, S. (2017). *Density estimation using Real NVP.* **ICLR 2017**.
- Kingma, D.P. & Dhariwal, P. (2018). *Glow: generative flow with invertible 1x1 convolutions.* **NeurIPS 2018**.

---

## Part 2: Diffusion Models

### DDPM and Variants
- Ho, J., Jain, A. & Abbeel, P. (2020). *Denoising diffusion probabilistic models.* **NeurIPS 2020**. — The DDPM paper.
- Sohl-Dickstein, J. et al. (2015). *Deep unsupervised learning using nonequilibrium thermodynamics.* **ICML 2015**. — The original diffusion paper.
- Nichol, A. & Dhariwal, P. (2021). *Improved denoising diffusion probabilistic models.* **ICML 2021**. — Cosine schedule, learnable variance.
- Song, J., Meng, C. & Ermon, S. (2021). *Denoising diffusion implicit models (DDIM).* **ICLR 2021**. — Faster sampling.
- Ho, J. & Salimans, T. (2022). *Classifier-free diffusion guidance.* **NeurIPS Workshop 2022**.

### Score-Based Models
- Song, Y. & Ermon, S. (2019). *Generative modeling by estimating gradients of the data distribution.* **NeurIPS 2019**. — NCSN.
- Song, Y. et al. (2021). *Score-based generative modeling through stochastic differential equations.* **ICLR 2021**. — The continuous-time view.
- Song, Y. et al. (2021). *Maximum likelihood training of score-based diffusion models.* **NeurIPS 2021**.

### Flow Matching
- Lipman, Y. et al. (2023). *Flow matching for generative modeling.* **ICLR 2023**.
- Liu, X., Gong, C. & Liu, Q. (2023). *Flow straight and fast: learning to generate and transfer data with rectified flow.* **ICLR 2023**.
- Albergo, M.S. & Vanden-Eijnden, E. (2023). *Building normalizing flows with stochastic interpolants.* **ICLR 2023**.

### Consistency Models
- Song, Y. et al. (2023). *Consistency models.* **ICML 2023**. — Few-step sampling.

### Forward Process Design
- Lin, L., Li, Z. et al. (2024). *Common diffusion noise schedules and sample steps are flawed.* **WACV 2024**.

---

## Part 3: Latent Diffusion (Stable Diffusion)

### Latent Diffusion
- Rombach, R. et al. (2022). *High-resolution image synthesis with latent diffusion models.* **CVPR 2022**. — The Stable Diffusion paper.
- Esser, P., Rombach, R. & Ommer, B. (2021). *Taming transformers for high-resolution image synthesis.* **CVPR 2021**. — VQGAN.
- Rombach, R. & Ommer, B. (2018). *Attacking generative models with deep convolutional neural networks.* — Early latent diffusion.

### Text Conditioning
- Radford, A. et al. (2021). *Learning transferable visual models from natural language supervision.* **ICML 2021**. — CLIP.
- Raffel, C. et al. (2020). *Exploring the limits of transfer learning with a unified text-to-text transformer.* **JMLR** 21(140): 1–67. — T5.
- Ramesh, A. et al. (2022). *Hierarchical text-conditional image generation with CLIP latents.* **NeurIPS 2022**. — DALL-E 2.
- Saharia, C. et al. (2022). *Photorealistic text-to-image diffusion models with deep language understanding.* **NeurIPS 2022**. — Imagen.
- Podell, D. et al. (2024). *SDXL: improving latent diffusion models for high-resolution image synthesis.* **ICLR 2024**.

### U-Net Architecture
- Ronneberger, O. et al. (2015). *U-Net: convolutional networks for biomedical image segmentation.* **MICCAI 2015**.
- Vaswani, A. et al. (2017). *Attention is all you need.* **NeurIPS 2017**.

### Transformers for Images
- Peebles, W. & Xie, S. (2023). *Scalable diffusion models with transformers.* **ICCV 2023**. — DiT.
- Chen, S. et al. (2023). *PixArt-α: fast training of diffusion transformer for photorealistic text-to-image synthesis.* **ICLR 2024**.
- Peebles, W. et al. (2024). *DiT-XL.* — See above.
- Gao, S. et al. (2023). *FLUX.* — See Black Forest Labs announcement.

### Classifier Guidance
- Dhariwal, P. & Nichol, A. (2021). *Diffusion models beat GANs on image synthesis.* **NeurIPS 2021**. — Classifier guidance.
- Ho, J. & Salimans, T. (2022). *Classifier-free diffusion guidance.* — See Part 2.

### Conditioning Extensions
- Zhang, L. & Agrawala, M. (2023). *Adding conditional control to text-to-image diffusion models.* **ICCV 2023**. — ControlNet.
- Ye, H. et al. (2023). *IP-Adapter: text compatible image prompt adapter for text-to-image diffusion models.* — IP-Adapter.
- Hu, E.J. et al. (2022). *LoRA: low-rank adaptation of large language models.* **ICLR 2022**. — LoRA.

---

## Part 4: Video Diffusion

### Early Video Diffusion
- Ho, J. et al. (2022). *Video diffusion models.* **arXiv:2204.03458**. — The first video diffusion paper.
- Singer, U. et al. (2022). *Make-a-video: text-to-video generation without text-video data.* **ICLR 2023**.

### 3D U-Net and Temporal Attention
- Yu, L. et al. (2023). *MAGVIT: masked generative video transformer.* **CVPR 2023**.
- Blattmann, A. et al. (2023). *Align your latents: high-resolution video synthesis with latent diffusion models.* **CVPR 2023**. — Stable Video Diffusion.
- Blattmann, A. et al. (2023). *Stable video diffusion: scaling latent video diffusion models to large datasets.* **arXiv:2311.15127**.

### Modern Video Models
- Bar-Tal, O. et al. (2024). *Lumiere: a space-time diffusion model for video generation.* — Google's video model.
- Brooks, T. et al. (2024). *Video generation models as world simulators.* — The Sora technical report.
- DeepMind. (2024). *Veo.* — Google DeepMind's video model.
- Wan, A. et al. (2025). *Wan: open and advanced large-scale video generative models.* — Open-source video model.
- Yang, Z. et al. (2024). *CogVideoX: text-to-video diffusion models with an expert transformer.* — Open-source video model.
- Wang, Y. et al. (2023). *AnimateDiff: animate your personalized text-to-image diffusion models without specific tuning.* **ICLR 2024**.

### Long Video Generation
- Tian, Y. et al. (2024). *A survey on video diffusion models.* **arXiv:2402.17471**.

---

## Foundational Textbooks

- Goodfellow, I., Bengio, Y. & Courville, A. (2016). *Deep Learning.* MIT Press.
- Bishop, C.M. (2006). *Pattern Recognition and Machine Learning.* Springer.
- Murphy, K.P. (2012). *Machine Learning: A Probabilistic Perspective.* MIT Press.
- Goodfellow, I. (2016). *NIPS 2016 tutorial: generative adversarial networks.* **arXiv:1701.00160**.
- Ruthotto, L. & Haber, E. (2021). *An introduction to deep generative modeling.* **GAMM Mitteilungen** 44(2): e202100008.

---

## Frameworks and Tools

- Paszke, A. et al. (2019). *PyTorch: an imperative style, high-performance deep learning library.* **NeurIPS 2019**.
- Harris, C.R. et al. (2020). *Array programming with NumPy.* **Nature** 585(7825): 357–362.
- Bradbury, J. et al. (2018). *JAX: composable transformations of Python+NumPy programs.*
- von Platen, P. et al. (2022). *Diffusers: state-of-the-art diffusion models.* GitHub. — Hugging Face library.
- Rombach, R. et al. (2022). *Stable Diffusion.* GitHub. — Stability AI release.
- The Hugging Face team. *Hugging Face Diffusers documentation.* https://huggingface.co/docs/diffusers.

---

## Where to go from here

**For a deep dive into diffusion theory**: read the score-based SDE paper (Song et al. 2021) and the flow matching papers (Lipman et al. 2023, Liu et al. 2023). These give the modern continuous-time view.

**For latent diffusion code**: clone the Stability AI Stable Diffusion repo. Run inference with a small model. Fine-tune with LoRA.

**For video generation**: start with Stable Video Diffusion (open source). Try AnimateDiff. Then look at the Sora technical report for the architecture.

**For text-to-image benchmarks**: COCO, FID, CLIP score. For video: UCF-101, VBench.

**For the latest**: follow researchers on Twitter/X (@JonathanHoML, @yang_song_9, @RobbieGKingma, @ajmooch, @nbardy). Or read arXiv: cs.CV, cs.LG, cs.AI.

---

Last updated: 2026.
