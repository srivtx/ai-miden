# Bibliography

> Every claim in this curriculum that comes from specific research is backed by a primary source. This file lists the most important references, organized by topic. References marked **(see above)** point to a previously-listed entry in the same file.

---

## Part 0: First Principles

### Signals
- Oppenheim, A.V. & Willsky, A.S. (1997). *Signals and Systems* (2nd ed.). Prentice-Hall.
- Ifeachor, E.C. & Jervis, B.W. (2001). *Digital Signal Processing: A Practical Approach.* Prentice-Hall.

### Information
- Shannon, C.E. (1948). *A Mathematical Theory of Communication.* **Bell System Technical Journal** 27(3): 379–423, 27(4): 623–656.
- Cover, T.M. & Thomas, J.A. (2006). *Elements of Information Theory* (2nd ed.). Wiley.
- MacKay, D.J.C. (2003). *Information Theory, Inference, and Learning Algorithms.* Cambridge University Press. — Free online.
- Jaynes, E.T. (1957). *Information Theory and Statistical Mechanics.* **Physical Review** 106(4): 620–630. — The deep link between information and entropy.
- Rieke, F., Warland, D., de Ruyter van Steveninck, R.R. & Bialek, W. (1997). *Spikes: Exploring the Neural Code.* MIT Press.

### Gradients
- Boyd, S. & Vandenberghe, L. (2004). *Convex Optimization.* Cambridge University Press.
- Goodfellow, I., Bengio, Y. & Courville, A. (2016). *Deep Learning.* MIT Press. — Chapter 4 (numerical computation), Chapter 8 (optimization).
- Ruder, S. (2016). *An overview of gradient descent optimization algorithms.* arXiv:1609.04747.

### Thermodynamics and Energy
- Boltzmann, L. (1877). *Über die Beziehung zwischen dem zweiten Hauptsatze der mechanischen Wärmetheorie und der Wahrscheinlichkeitsrechnung.* **Wiener Berichte** 76: 373–435. — The original entropy formula.
- Prigogine, I. (1977). *Time, Structure and Fluctuations.* Nobel Lecture. — Dissipative structures. Nobel Prize in Chemistry 1977.
- Schrödinger, E. (1944). *What Is Life?* Cambridge University Press. — The "negentropy" idea.
- Attwell, D. & Laughlin, S.B. (2001). *An energy budget for signaling in the grey matter of the brain.* **Journal of Cerebral Blood Flow & Metabolism** 21(10): 1133–1145. — The canonical ~20% energy paper.
- Laughlin, S.B. (2001). *Energy as a constraint on the coding and processing of sensory information.* **Current Opinion in Neurobiology** 11(4): 475–480.
- Sengupta, B., Stemmler, M.B. & Friston, K.J. (2013). *The metabolic cost of neural computation.* **PLoS Computational Biology** 9(11): e1003315.
- Harris, J.J. & Attwell, D. (2012). *The energetics of CNS white matter.* **Journal of Neuroscience** 32(1): 356–371.
- Lennie, P. (2003). *The cost of cortical computation.* **Current Biology** 13(6): 493–497.

### Free Energy Principle (links all four first principles)
- Friston, K. (2010). *The free-energy principle: a unified brain theory?* **Nature Reviews Neuroscience** 11(2): 127–138.
- Friston, K., Kilner, J. & Harrison, L. (2006). *A free energy principle for the brain.* **Journal of Physiology Paris** 100(1–3): 70–87.
- Friston, K. (2019). *A free energy principle for a particular physics.* arXiv:1906.10184.

---

## Part 1: Building Blocks

### Neuron
- Hodgkin, A.L. & Huxley, A.F. (1952). *A quantitative description of membrane current and its application to conduction and excitation in nerve.* **Journal of Physiology** 117(4): 500–544. — The original mathematical model of the action potential. Nobel Prize 1963.
- Kandel, E.R., Schwartz, J.H. & Jessell, T.M. (2000). *Principles of Neural Science* (4th ed.). McGraw-Hill.

### Cell Membrane
- Hille, B. (2001). *Ion Channels of Excitable Membranes* (3rd ed.). Sinauer.
- Goldman, D.E. (1943). *Potential, impedance, and rectification in membranes.* **Journal of General Physiology** 27(1): 37–60. — The Goldman equation.

### Action Potential
- Hodgkin, A.L. & Huxley, A.F. (1952). — See above.
- Hille, B. (2001). — See above.
- Bean, B.P. (2007). *The action potential in mammalian central neurons.* **Nature Reviews Neuroscience** 8(6): 451–465.

### Synapse
- Südhof, T.C. (2004). *The synaptic vesicle cycle.* **Annual Review of Neuroscience** 27: 509–547.
- Südhof, T.C. (2013). *Neurotransmitter release: the last millisecond in the life of a synaptic vesicle.* **Neuron** 80(3): 675–690.
- Südhof, T.C. (2013). *A molecular machine for neurotransmitter release: synaptotagmin and the SNARE complex.* (Nobel lecture). — 2013 Nobel with Rothman and Schekman.
- Tsodyks, M.V. & Markram, H. (1997). *The neural code between neocortical pyramidal neurons depends on neurotransmitter release probability.* **PNAS** 94(2): 719–723. — The Tsodyks-Markram model.

### Neurotransmitters
- Hyman, S.E. (2005). *Neurotransmitters.* **Current Biology** 15(5): R154–R158.
- Purves, D. et al. (2018). *Neuroscience* (6th ed.). Oxford University Press.
- Schultz, W. (1997). *A neural substrate of prediction and reward.* **Science** 275: 1593–1599. — Dopamine = TD error.

### Dendrites and Spines
- Magee, J.C. (2000). *Dendritic integration of excitatory synaptic input.* **Nature Reviews Neuroscience** 1(3): 181–190.
- Spruston, N. (2008). *Pyramidal neurons: dendritic structure and synaptic integration.* **Nature Reviews Neuroscience** 9(3): 206–221.
- Yuste, R. (2010). *Dendritic Spines.* MIT Press.

---

## Part 2: Learning Mechanisms

### Hebbian Learning
- Hebb, D.O. (1949). *The Organization of Behavior: A Neuropsychological Theory.* Wiley.
- Morris, R.G.M. (1999). *D.O. Hebb: The Organization of Behavior, Wiley: New York; 1949.* **Brain Research Bulletin** 50(5–6): 437.
- Oja, E. (1982). *A simplified neuron model as a principal component analyzer.* **Journal of Mathematical Biology** 15(3): 267–273.
- Hopfield, J.J. (1982). *Neural networks and physical systems with emergent collective computational abilities.* **PNAS** 79(8): 2554–2558.

### LTP and LTD
- Bliss, T.V. & Lømo, T. (1973). *Long-lasting potentiation of synaptic transmission in the dentate area of the anaesthetized rabbit following stimulation of the perforant path.* **Journal of Physiology** 232(2): 331–356.
- Bliss, T.V. & Collingridge, G.L. (1993). *A synaptic model of memory: long-term potentiation in the hippocampus.* **Nature** 361(6407): 31–39.
- Malenka, R.C. & Bear, M.F. (2004). *LTP and LTD: an embarrassment of riches.* **Neuron** 44(1): 5–21.
- Lynch, M.A. (2004). *Long-term potentiation and memory.* **Physiological Reviews** 84(1): 87–136.
- Lisman, J. (1989). *A mechanism for the Hebb and the anti-Hebb processes underlying learning and memory.* **PNAS** 86(23): 9574–9578. — The calcium hypothesis.

### STDP
- Bi, G.-Q. & Poo, M.-M. (1998). *Synaptic modifications in cultured hippocampal neurons: dependence on spike timing, synaptic strength, and postsynaptic cell type.* **Journal of Neuroscience** 18(24): 10464–10472. — The STDP paper.
- Markram, H., Lübke, J., Frotscher, M. & Sakmann, B. (1997). *Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs.* **Science** 275(5297): 213–215.
- Caporale, N. & Dan, Y. (2008). *Spike timing–dependent plasticity: a Hebbian learning rule.* **Annual Review of Neuroscience** 31: 25–46.
- Feldman, D.E. (2012). *The spike-timing dependence of plasticity.* **Neuron** 75(4): 556–571.
- Dan, Y. & Poo, M.-M. (2006). *Spike timing-dependent plasticity: from synapse to perception.* **Physiological Reviews** 86(3): 1033–1048.

### Three-Factor Learning
- Schultz, W., Dayan, P. & Montague, P.R. (1997). *A neural substrate of prediction and reward.* **Science** 275: 1593–1599.
- Brzosko, Z., Zannone, S., Schultz, W., Clopath, C. & Paulsen, O. (2017). *Sequential neuromodulation of Hebbian plasticity offers mechanism for effective reward-based navigation.* **eLife** 6: e27756. — ACh + DA sequence.
- Frémaux, N. & Gerstner, W. (2016). *Neuromodulated spike-timing-dependent plasticity, and theory of three-factor learning rules.* **Frontiers in Neural Circuits** 9: 85.
- Seol, G.H. et al. (2007). *Neuromodulators control the polarity of spike-timing-dependent synaptic plasticity.* **Neuron** 55(6): 919–929.
- Schultz, W. (1998). *Predictive reward signal of dopamine neurons.* **Journal of Neurophysiology** 80(1): 1–27.

### BTSP
- Bittner, K.C., Milstein, A.D., Grienberger, C., Romani, S. & Magee, J.C. (2017). *Behavioral time scale synaptic plasticity underlies CA1 place fields.* **Science** 357(6355): 1033–1036.
- Grienberger, C. & Magee, J.C. (2020). *Synaptic plasticity forms and functions.* **Annual Review of Neuroscience** 43: 95–117.

### Homeostatic Plasticity
- Turrigiano, G.G., Leslie, K.R., Desai, N.S., Rutherford, L.C. & Nelson, S.B. (1998). *Activity-dependent scaling of quantal amplitude in neocortical neurons.* **Nature** 391(6670): 892–896.
- Turrigiano, G. (2011). *Homeostatic synaptic plasticity: local and global mechanisms for stabilizing neuronal function.* **Cold Spring Harbor Perspectives in Biology** 4(1): a005736.
- Bienenstock, E.L., Cooper, L.N. & Munro, P.W. (1982). *Theory for the development of neuron selectivity: orientation specificity and binocular interaction in visual cortex.* **Journal of Neuroscience** 2(1): 32–48. — The BCM rule.

---

## Part 3: Architecture

### Glia
- Allen, N.J. & Lyons, D.A. (2018). *Glia as architects: central nervous system.* **Science** 362(6411): 181–185.
- Araque, A. et al. (1999). *Tripartite synapses: glia, the unacknowledged partner.* **Trends in Neurosciences** 22(5): 208–215.
- Halassa, M.M. & Haydon, P.G. (2010). *Integrated brain circuits: astrocytic networks modulate neuronal activity and behavior.* **Annual Review of Physiology** 72: 335–355.
- Xie, L. et al. (2013). *Sleep drives metabolite clearance from the adult brain.* **Science** 342(6156): 373–377. — The glymphatic system.
- Fields, R.D. (2008). *White matter in learning, cognition and psychiatric disorders.* **Trends in Neurosciences** 31(7): 361–370.
- Volterra, A. & Meldolesi, J. (2005). *Astrocytes, from brain glue to communication elements: the revolution continues.* **Nature Reviews Neuroscience** 6(8): 626–640.

### Cortex
- Mountcastle, V.B. (1957). *Modality and topographic properties of single neurons of cat's somatic sensory cortex.* **Journal of Neurophysiology** 20(4): 408–434. — The cortical column discovery.
- Douglas, R.J. & Martin, K.A.C. (2004). *Neuronal circuits of the neocortex.* **Annual Review of Neuroscience** 27: 419–451.
- Harris, K.D. & Shepherd, G.M. (2015). *The neocortical circuit: themes and variations.* **Nature Neuroscience** 18(2): 170–181.
- Rakic, P. (2008). *Confusing cortical columns.* **PNAS** 105(34): 12099–12100.

### Cortical Column
- Hubel, D.H. & Wiesel, T.N. (1962). *Receptive fields, binocular interaction and functional architecture in the cat's visual cortex.* **Journal of Physiology** 160(1): 106–154.
- Hubel, D.H. & Wiesel, T.N. (1977). *Functional architecture of macaque monkey visual cortex.* **Proceedings of the Royal Society B** 198(1130): 1–59.
- Bastos, A.M. et al. (2012). *Canonical microcircuits for predictive coding.* **Neuron** 76(4): 695–711.
- Hawkins, J. (2021). *A Thousand Brains.* Basic Books.

### Thalamus
- Sherman, S.M. (2007). *The thalamus is more than just a relay.* **Current Opinion in Neurobiology** 17(4): 417–422.
- Saalmann, Y.B. & Kastner, S. (2011). *Cognitive and perceptual functions of the visual thalamus.* **Neuron** 71(2): 209–223.
- Steriade, M., McCormick, D.A. & Sejnowski, T.J. (1993). *Thalamocortical oscillations in the sleeping and aroused brain.* **Science** 262(5134): 679–685.
- McCormick, D.A. & Bal, T. (1997). *Sleep and arousal: thalamocortical mechanisms.* **Annual Review of Neuroscience** 20: 185–215.

### Hippocampus
- O'Keefe, J. & Nadel, L. (1978). *The Hippocampus as a Cognitive Map.* Oxford University Press.
- O'Keefe, J. & Dostrovsky, J. (1971). *The hippocampus as a spatial map. Preliminary evidence from unit activity in the freely-moving rat.* **Brain Research** 34(1): 171–175.
- Squire, L.R. (1992). *Memory and the hippocampus: a synthesis from findings with rats, monkeys, and humans.* **Psychological Review** 99(2): 195–231.
- Buzsáki, G. (1989). *Two-stage model of memory trace formation: a role for "noisy" brain states.* **Neuroscience** 31(3): 551–570.
- Buzsáki, G. (2015). *Hippocampal sharp wave-ripple: a cognitive biomarker for episodic memory and planning.* **Hippocampus** 25(10): 1073–1188.
- Wilson, M.A. & McNaughton, B.L. (1994). *Reactivation of hippocampal ensemble memories during sleep.* **Science** 265(5172): 676–679.
- Scoville, W.B. & Milner, B. (1957). *Loss of recent memory after bilateral hippocampal lesions.* **Journal of Neurology, Neurosurgery & Psychiatry** 20(1): 11–21. — Patient H.M.
- Moser, E.I., Kropff, E. & Moser, M.-B. (2008). *Place cells, grid cells, and the brain's spatial representation system.* **Annual Review of Neuroscience** 31: 69–89.

### Basal Ganglia
- Graybiel, A.M. (2000). *The basal ganglia.* **Current Biology** 10(14): R509–R511.
- Mink, J.W. (1996). *The basal ganglia: focused selection and inhibition of competing motor programs.* **Progress in Neurobiology** 50(4): 381–425.
- Gerfen, C.R. & Surmeier, D.J. (2011). *Modulation of striatal projection systems by dopamine.* **Annual Review of Neuroscience** 34: 441–466.
- Calabresi, P. et al. (2014). *Direct and indirect pathways of basal ganglia: a critical reappraisal.* **Nature Neuroscience** 17(8): 1022–1030.
- Hikosaka, O. et al. (2000). *Parallel neural networks for learning sequential procedures.* **Trends in Neurosciences** 23(11): 579–585.
- Yin, H.H. & Knowlton, B.J. (2006). *The role of the basal ganglia in habit formation.* **Nature Reviews Neuroscience** 7(6): 464–476.

### Cerebellum
- Ito, M. (1982). *Experimental verification of Marr-Albus plasticity assumption for the cerebellum.* **Neuroscience Research** 1(2): 81–84.
- Marr, D. (1969). *A theory of cerebellar cortex.* **Journal of Physiology** 202(2): 437–470. — The Marr-Albus theory.
- Albus, J.S. (1971). *A theory of cerebellar function.* **Mathematical Biosciences** 10(1–2): 25–61.
- Schmahmann, J.D. (2004). *Disorders of the cerebellum: ataxia, dysmetria of thought, and the cerebellar cognitive affective syndrome.* **Journal of Neuropsychiatry and Clinical Neurosciences** 16(3): 367–378.
- Schmahmann, J.D. & Sherman, J.C. (1998). *The cerebellar cognitive affective syndrome.* **Brain** 121(4): 561–579.
- Wolpert, D.M., Miall, R.C. & Kawato, M. (1998). *Internal models in the cerebellum.* **Trends in Cognitive Sciences** 2(9): 338–347.

---

## Part 4: Systems

### Visual System
- Hubel, D.H. & Wiesel, T.N. (1962). — See above.
- Ungerleider, L.G. & Mishkin, M. (1982). *Two cortical visual systems.* In *Analysis of Visual Behavior*, MIT Press.
- Rao, R.P.N. & Ballard, D.H. (1999). *Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects.* **Nature Neuroscience** 2(1): 79–87.
- Felleman, D.J. & Van Essen, D.C. (1991). *Distributed hierarchical processing in the primate cerebral cortex.* **Cerebral Cortex** 1(1): 1–47.
- DiCarlo, J.J., Zoccolan, D. & Rust, N.C. (2012). *How does the brain solve visual object recognition?* **Neuron** 73(3): 415–434.

### Attention
- Desimone, R. & Duncan, J. (1995). *Neural mechanisms of selective visual attention.* **Annual Review of Neuroscience** 18: 193–222. — Biased competition.
- Posner, M.I. (1980). *Orienting of attention.* **Quarterly Journal of Experimental Psychology** 32(1): 3–25.
- Corbetta, M. & Shulman, G.L. (2002). *Control of goal-directed and stimulus-driven attention in the brain.* **Nature Reviews Neuroscience** 3(3): 201–215.
- Knudsen, E.I. (2007). *Fundamental components of attention.* **Annual Review of Neuroscience** 30: 57–78.
- Itti, L. & Baldi, P. (2009). *Bayesian surprise attracts human attention.* **Vision Research** 49(10): 1295–1306.

### Sleep
- Tononi, G. & Cirelli, C. (2003). *Sleep and synaptic homeostasis: a hypothesis.* **Brain Research Bulletin** 62(2): 143–150.
- Tononi, G. & Cirelli, C. (2014). *Sleep and the price of plasticity: from synaptic and cellular homeostasis to memory consolidation and integration.* **Neuron** 81(1): 12–34.
- Xie, L. et al. (2013). — See above.
- Rasch, B. & Born, J. (2013). *About sleep's role in memory.* **Physiological Reviews** 93(2): 681–766.
- Walker, M.P. & van der Helm, E. (2009). *Overnight therapy? The role of sleep in emotional brain processing.* **Psychological Bulletin** 135(5): 731–748.
- Wilson, M.A. & McNaughton, B.L. (1994). — See above.
- Diekelmann, S. & Born, J. (2010). *The memory function of sleep.* **Nature Reviews Neuroscience** 11(2): 114–126.

### Reward
- Schultz, W. (1997, 1998, 2007). — See above.
- Berridge, K.C. & Robinson, T.E. (1998). *What is the role of dopamine in reward: hedonic impact, reward learning, or incentive salience?* **Brain Research Reviews** 28(3): 309–369.
- Berridge, K.C. (2007). *The debate over dopamine's role in reward: the case for incentive salience.* **Psychopharmacology** 191: 391–431.
- Sutton, R.S. & Barto, A.G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- Dayan, P. & Abbott, L.F. (2001). *Theoretical Neuroscience.* MIT Press.

### Predictive Coding
- Rao, R.P.N. & Ballard, D.H. (1999). — See above.
- Friston, K. (2005). *A theory of cortical responses.* **Philosophical Transactions of the Royal Society B** 360(1456): 815–836.
- Friston, K. (2010). — See Part 0.
- Friston, K. et al. (2010). *Action and behavior: a free-energy formulation.* **Biological Cybernetics** 102(3): 227–260.
- Clark, A. (2013). *Whatever next? Predictive brains, situated agents, and the future of cognitive science.* **Behavioral and Brain Sciences** 36(3): 181–204.
- Bastos, A.M. et al. (2012). — See above.
- Whittington, J.C.R. & Bogacz, R. (2019). *Theories of error back-propagation in the brain.* **Trends in Cognitive Sciences** 23(3): 235–250.
- Millidge, B., Salvatori, T., Song, Y., Bogacz, R. & Lukasiewicz, T. (2022). *Predictive coding: towards a future of deep learning beyond backpropagation?* arXiv:2202.09467.
- Mikulasch, F.A., Rudelt, L., Wibral, M. & Priesemann, V. (2023). *Where is the error? Hierarchical predictive coding through dendritic error computation.* **Trends in Neurosciences** 46(1): 45–59.
- Keller, G.B. & Mrsic-Flogel, T.D. (2018). *Predictive processing: a canonical cortical computation.* **Neuron** 100(2): 424–435.

---

## Part 5: Comparison

### Brain-Inspired AI (cross-listed with Part 10)
- Hassabis, D., Kumaran, D., Summerfield, C. & Botvinick, M. (2017). *Neuroscience-inspired artificial intelligence.* **Neuron** 95(2): 245–258.
- Lake, B.M., Ullman, T.D., Tenenbaum, J.B. & Gershman, S.J. (2017). *Building machines that learn and think like people.* **Behavioral and Brain Sciences** 40: e253.
- Marblestone, A.H., Wayne, G. & Kording, K.P. (2016). *Toward an integration of deep learning and neuroscience.* **Frontiers in Computational Neuroscience** 10: 94.
- Zador, A.M. (2019). *A critique of pure learning: what artificial neural networks cannot learn from animal learning.* **Neuron** 105(2): 245–258.
- Lillicrap, T.P. & Santoro, A. (2019). *Backpropagation through time and the brain.* **Current Opinion in Neurobiology** 55: 82–89.
- LeCun, Y. (2022). *A path towards autonomous machine intelligence.* OpenReview. — The JEPA manifesto.
- Hawkins, J. & Blakeslee, S. (2004). *On Intelligence.* Times Books. — The HTM theory.
- Bengio, Y., Mesnard, T., Fischer, A., Zhang, S. & Wu, Y. (2017). *A biologically inspired mechanism for credit assignment in neural networks.* arXiv:1705.06951.
- Hinton, G. (2022). *The forward-forward algorithm: some preliminary investigations.* **Proc. NeurIPS**.

### Energy Comparison
- Strubell, E., Ganesh, A. & McCallum, A. (2019). *Energy and policy considerations for deep learning in NLP.* **ACL**.
- Pachetti, E. & Becattini, F. (2024). *Energy consumption of AI: a survey of surveys.* (Various surveys.)
- Patterson, D. et al. (2021). *Carbon emissions and large neural network training.* arXiv:2104.10350.
- Sevilla, J. et al. (2022). *Compute trends across three eras of machine learning.* arXiv:2202.05924.

### Sample Efficiency
- Lake, B.M. & Baroni, M. (2023). *Human-like systematic generalization through a meta-learning neural network.* **Nature** 623: 115–121.
- Frank, M.C. (2023). *Bridging the data gap between children and large language models.* **Trends in Cognitive Sciences** 27(11): 990–1003.

---

## Part 6: Signals From Scratch

### Calcium Signaling
- Berridge, M.J. (1998). *Neuronal calcium signaling.* **Neuron** 21(1): 13–26.
- Berridge, M.J., Lipp, P. & Bootman, M.D. (2000). *The versatility and universality of calcium signalling.* **Nature Reviews Molecular Cell Biology** 1(1): 11–21.
- Bading, H. (2013). *Nuclear calcium signalling in the regulation of brain function.* **Nature Reviews Neuroscience** 14(9): 593–608.
- Clapham, D.E. (2007). *Calcium signaling.* **Cell** 131(6): 1047–1058.

### cAMP and PKA
- Kandel, E.R. (2001). *The molecular biology of memory storage: a dialogue between genes and synapses.* **Science** 294: 1030–1038. — The cAMP-PKA-CREB pathway in long-term memory.
- Kandel, E.R. (2012). *The molecular biology of memory: cAMP, PKA, CREB, CREB phosphorylation, and LTP.* **Nobel Lecture**.

### BDNF
- Park, H. & Poo, M.-M. (2013). *Neurotrophin regulation of neural circuit development and function.* **Nature Reviews Neuroscience** 14(1): 7–23.
- Egan, M.F. et al. (2003). *The BDNF val66met polymorphism affects activity-dependent secretion of BDNF and human memory and hippocampal function.* **Cell** 112(2): 257–269. — The Val66Met paper.
- Reichardt, L.F. (2006). *Neurotrophin-regulated signalling pathways.* **Philosophical Transactions of the Royal Society B** 361(1473): 1545–1564.
- Chao, M.V. (2003). *Neurotrophins and their receptors: a convergence point for many signalling pathways.* **Nature Reviews Neuroscience** 4(4): 299–309.
- Nagappan, G. & Lu, B. (2005). *Activity-dependent modulation of the BDNF receptor TrkB: mechanisms and implications.* **Trends in Neurosciences** 28(9): 464–471.
- Cotman, C.W. & Berchtold, N.C. (2002). *Exercise: a behavioral intervention to enhance brain health and plasticity.* **Trends in Neurosciences** 25(6): 295–301.
- Duman, R.S. & Monteggia, L.M. (2006). *A neurotrophic model for stress-related mood disorders.* **Biological Psychiatry** 59(12): 1116–1127.
- Yang, J. et al. (2014). *Neuronal release of proBDNF.* **Nature Neuroscience** 17(1): 47–55. — For proBDNF at the synapse.

### Gene Expression
- West, A.E. et al. (2001). *Calcium regulation of neuronal gene expression.* **PNAS** 98(20): 11024–11031.
- Silva, A.J. et al. (1998). *CREB and memory.* **Annual Review of Neuroscience** 21: 127–148.
- Kandel, E.R. (2001). — See above.
- Kandel, E.R. (2012). — See above.
- Minatohara, K., Akiyoshi, M. & Okuno, H. (2016). *Role of immediate-early genes in synaptic plasticity and neuronal ensembles underlying the memory trace.* **Frontiers in Molecular Neuroscience** 8: 78.

### Molecular Cascade Integration
- See Bading (2013) for nuclear calcium → gene expression.
- See Kandel (2001, 2012) for the full Ca²⁺ → cAMP → PKA → CREB → gene cascade.

---

## Part 7: When the Brain Breaks

### Alzheimer's Disease
- Selkoe, D.J. (2011). *Alzheimer's disease.* **Cold Spring Harbor Perspectives in Biology** 3(7): a004457.
- Hardy, J. & Selkoe, D.J. (2002). *The amyloid hypothesis of Alzheimer's disease: progress and problems on the road to therapeutics.* **Science** 297(5580): 353–356.
- Hyman, B.T. et al. (2012). *National Institute on Aging–Alzheimer's Association guidelines for the neuropathologic assessment of Alzheimer's disease.* **Alzheimer's & Dementia** 8(1): 1–13.
- Sperling, R.A. et al. (2011). *Toward defining the preclinical stages of Alzheimer's disease.* **Alzheimer's & Dementia** 7(3): 280–292.
- Holtzman, D.M., Morris, J.C. & Goate, A.M. (2011). *Alzheimer's disease: the challenge of the second century.* **Science Translational Medicine** 3(77): 77sr1.
- Long, J.M. & Holtzman, D.M. (2019). *Alzheimer disease: an update on pathobiology and treatment strategies.* **Cell** 179(2): 312–339.
- Knopman, D.S. et al. (2021). *Alzheimer disease.* **Nature Reviews Disease Primers** 7(1): 33.
- Hyman, B.T. (2011). *Amyloid-dependent and amyloid-independent stages of Alzheimer disease.* **Archives of Neurology** 68(8): 1062–1064.

### Parkinson's Disease
- Jankovic, J. (2008). *Parkinson's disease: clinical features and diagnosis.* **Journal of Neurology, Neurosurgery & Psychiatry** 79(4): 368–376.
- Braak, H. et al. (2003). *Staging of brain pathology related to sporadic Parkinson's disease.* **Neurobiology of Aging** 24(2): 197–211.
- Kalia, L.V. & Lang, A.E. (2015). *Parkinson's disease.* **Lancet** 386(9996): 896–912.
- Poewe, W. et al. (2017). *Parkinson disease.* **Nature Reviews Disease Primers** 3: 17013.
- Surmeier, D.J., Obeso, J.A. & Halliday, G.M. (2017). *Selective neuronal vulnerability in Parkinson disease.* **Nature Reviews Neuroscience** 18(2): 101–113.
- Spillantini, M.G. et al. (1997). *α-Synuclein in Lewy bodies.* **Nature** 388(6645): 839–840.
- Polymeropoulos, M.H. et al. (1997). *Mutation in the α-synuclein gene identified in families with Parkinson's disease.* **Science** 276(5321): 2045–2047.

### Schizophrenia
- Carlsson, A. (1988). *The current status of the dopamine hypothesis of schizophrenia.* **Neuropsychopharmacology** 1(3): 179–186.
- Javitt, D.C. (2007). *Glutamate and schizophrenia: phencyclidine, N-methyl-D-aspartate, and dopamine–glutamate interactions.* **International Review of Neurobiology** 78: 69–108.
- Moghaddam, B. & Javitt, D. (2012). *From revolution to evolution: the glutamate hypothesis of schizophrenia and its implication for treatment.* **Neuropsychopharmacology** 37(1): 4–15.
- Howes, O.D. & Kapur, S. (2009). *The dopamine hypothesis of schizophrenia: version III—the final common pathway.* **Schizophrenia Bulletin** 35(3): 549–562.
- Insel, T.R. (2010). *Rethinking schizophrenia.* **Nature** 468(7321): 187–193.
- Owen, M.J., Sawa, A. & Mortensen, P.B. (2016). *Schizophrenia.* **Lancet** 388(10039): 86–97.
- McCutcheon, R.A., Reis Marques, T. & Howes, O.D. (2020). *Schizophrenia—an overview.* **JAMA Psychiatry** 77(2): 201–210.

### Depression
- Nestler, E.J. et al. (2002). *Neurobiology of depression.* **Neuron** 34(1): 13–25.
- Krishnan, V. & Nestler, E.J. (2008). *The molecular neurobiology of depression.* **Nature** 455(7215): 894–902.
- Duman, R.S. & Monteggia, L.M. (2006). — See Part 6.
- Berman, R.M. et al. (2000). *Antidepressant effects of ketamine in depressed patients.* **Biological Psychiatry** 47(4): 351–354. — The first ketamine trial.
- Zarate, C.A. et al. (2006). *A randomized trial of an N-methyl-D-aspartate antagonist in treatment-resistant major depression.* **Archives of General Psychiatry** 63(8): 856–864.
- Li, N. et al. (2010). *mTOR-dependent synapse formation underlies the rapid antidepressant effects of NMDA antagonists.* **Science** 329(5994): 959–964.
- Autry, A.E. et al. (2011). *NMDA receptor blockade at rest triggers rapid behavioural antidepressant responses.* **Nature** 475(7354): 91–95.
- Malberg, J.E. et al. (2000). *Chronic antidepressant treatment increases neurogenesis in adult rat hippocampus.* **Journal of Neuroscience** 20(24): 9104–9110.
- Caspi, A. et al. (2003). *Influence of life stress on depression: moderation by a polymorphism in the 5-HTT gene.* **Science** 301(5631): 386–389.

### Autism
- Wing, L. & Gould, J. (1979). *Severe impairments of social interaction and associated abnormalities in children: epidemiology and classification.* **Journal of Autism and Developmental Disorders** 9(1): 11–29.
- Rubenstein, J.L.R. & Merzenich, M.M. (2003). *Model of autism: increased ratio of excitation/inhibition in key neural systems.* **Genes, Brain and Behavior** 2(5): 255–267.
- Pellicano, E. & Burr, D. (2012). *When the world becomes 'too real': a Bayesian explanation of autistic perception.* **Trends in Cognitive Sciences** 16(10): 504–510.
- Geschwind, D.H. (2011). *Genetics of autism spectrum disorders.* **Trends in Cognitive Sciences** 15(9): 409–416.
- Hyman, S.L., Levy, S.E. & Myers, S.M. (2020). *Identification, evaluation, and management of children with autism spectrum disorder.* **Pediatrics** 145(1): e20193447.
- Lord, C. et al. (2020). *The Lancet Commission on the future of care and clinical research in autism.* **Lancet** 395(10221): 271–274.
- Wakefield, A.J. et al. (1998). *Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children.* **Lancet** 351(9103): 637–641. — *Retracted. The fraudulent paper that started the vaccine-autism myth.*
- Taylor, L.E., Swerdfeger, A.L. & Eslick, G.D. (2014). *Vaccines are not associated with autism: an evidence-based meta-analysis of case-control and cohort studies.* **Vaccine** 32(29): 3623–3629.

---

## Part 8: Measuring the Brain

### EEG
- Buzsáki, G. (2006). *Rhythms of the Brain.* Oxford University Press.
- Niedermeyer, E. & da Silva, F.L. (2005). *Electroencephalography: Basic Principles, Clinical Applications, and Related Fields* (5th ed.). Lippincott.
- Cohen, M.X. (2014). *Analyzing Neural Time Series Data.* MIT Press.
- Luck, S.J. (2014). *An Introduction to the Event-Related Potential Technique* (2nd ed.). MIT Press.
- Cohen, M.X. (2017). *Where does EEG come from and what does it mean?* **Trends in Neurosciences** 40(4): 208–218.

### fMRI
- Logothetis, N.K. (2008). *What we can do and what we cannot do with fMRI.* **Nature** 453(7197): 869–878.
- Ogawa, S. et al. (1990). *Brain magnetic resonance imaging with contrast dependent on blood oxygenation.* **PNAS** 87(24): 9868–9872. — The BOLD paper.
- Bandettini, P.A. (2012). *Twenty years of functional MRI: the science and the stories.* **NeuroImage** 62(2): 575–588.
- Huettel, S.A., Song, A.W. & McCarthy, G. (2014). *Functional Magnetic Resonance Imaging* (3rd ed.). Sinauer.
- Poldrack, R.A. (2018). *The New Mind Readers.* Princeton University Press.
- Bijsterbosch, J. et al. (2020). *Introduction to Resting State fMRI Functional Connectivity.* Oxford University Press.

### Patch Clamp
- Neher, E. & Sakmann, B. (1976). *Single-channel currents recorded from membrane of denervated frog muscle fibres.* **Nature** 260(5554): 799–802. — The first single-channel recording. Nobel 1991.
- Sakmann, B. & Neher, E. (2009). *Single-Channel Recording* (2nd ed.). Springer.

### Optogenetics
- Boyden, E.S., Zhang, F., Bamberg, E., Nagel, G. & Deisseroth, K. (2005). *Millisecond-timescale, genetically targeted optical control of neural activity.* **Nature Neuroscience** 8(9): 1263–1268. — The first optogenetics paper.
- Deisseroth, K. (2011). *Optogenetics.* **Nature Methods** 8(1): 26–29.
- Zhang, F. et al. (2007). *Multimodal fast optical interrogation of neural circuitry.* **Nature** 446(7136): 633–639.
- Yizhar, O. et al. (2011). *Optogenetics in neural systems.* **Neuron** 71(1): 9–34.
- Deisseroth, K. (2015). *Optogenetics: 10 years of microbial opsins in neuroscience.* **Nature Neuroscience** 18(9): 1213–1225.

### Two-Photon Imaging
- Denk, W., Strickler, J.H. & Webb, W.W. (1990). *Two-photon laser scanning fluorescence microscopy.* **Science** 248(4951): 73–76.
- Helmchen, F. & Denk, W. (2005). *Deep tissue two-photon microscopy.* **Nature Methods** 2(12): 932–940.
- Chen, T.-W. et al. (2013). *Ultrasensitive fluorescent proteins for imaging neuronal activity.* **Nature** 499(7458): 295–300. — The GCaMP6 paper.

---

## Part 9: Brain to Mind

### Consciousness (the Hard Problem)
- Chalmers, D.J. (1995). *Facing up to the problem of consciousness.* **Journal of Consciousness Studies** 2(3): 200–219.
- Chalmers, D.J. (1996). *The Conscious Mind: In Search of a Fundamental Theory.* Oxford University Press.
- Chalmers, D.J. (2010). *The Character of Consciousness.* Oxford University Press.
- Crick, F. & Koch, C. (1990). *Towards a neurobiological theory of consciousness.* **Seminars in the Neurosciences** 2: 263–275.
- Crick, F. & Koch, C. (2003). *A framework for consciousness.* **Nature Neuroscience** 6(2): 119–126.
- Koch, C. (2004). *The Quest for Consciousness.* Roberts & Co.
- Dehaene, S. (2014). *Consciousness and the Brain.* Viking Press.
- Koch, C. (2019). *The Feeling of Life Itself.* MIT Press.
- Seth, A.K. & Bayne, T. (2022). *Theories of consciousness.* **Nature Reviews Neuroscience** 23(7): 439–452.
- Searle, J.R. (1992). *The Rediscovery of the Mind.* MIT Press.

### Integrated Information Theory (IIT)
- Tononi, G. (2004). *An information integration theory of consciousness.* **BMC Neuroscience** 5(1): 42.
- Tononi, G. (2012). *Phi: A Voyage from the Brain to the Soul.* Pantheon.
- Tononi, G. et al. (2016). *Integrated information theory: from consciousness to its physical substrate.* **Nature Reviews Neuroscience** 17(7): 450–461.
- Albantakis, L. et al. (2023). *Integrated information theory (IIT) 4.0.* **PLoS Computational Biology** 19(10): e1011465.
- Mediano, P.A.M. et al. (2022). *Integrated information as a common signature of dynamical and information-processing complexity.* **Entropy** 24(8): 1099.
- Findlay, G. et al. (2019). *Integrated information and consciousness: a review of the literature.* **Neuroscience & Biobehavioral Reviews** 105: 131–143.

### Global Workspace Theory (GWT)
- Baars, B.J. (1988). *A Cognitive Theory of Consciousness.* Cambridge University Press.
- Dehaene, S. et al. (1998). *A neuronal network model linking subjective reports and objective physiological data during conscious perception.* **PNAS** 95(24): 14552–14557.
- Dehaene, S. & Changeux, J.-P. (2011). *Experimental and theoretical approaches to conscious processing.* **Neuron** 70(2): 200–227.
- Mashour, G.A., Roelfsema, P., Changeux, J.-P. & Dehaene, S. (2020). *Conscious processing and the global workspace theory.* **Annual Review of Neuroscience** 43: 223–243.
- Shanahan, M. (2010). *Embodied cognition and the global workspace.* **Cognitive Processing** 11(4): 317–330.
- Bao, Y. et al. (2020). *A global workspace network for language and cognition in transformer architectures.* arXiv:2006.04615.
- Goyal, A. et al. (2022). *Coordination among neural modules for the global workspace.* **Neural Computation** 34(1): 1–40.

### Higher-Order Theories (HOT)
- Rosenthal, D.M. (1986). *Two concepts of consciousness.* **Philosophical Studies** 49(3): 329–359.
- Lau, H. & Brown, H. (2019). *Consciousness.* In *The Cambridge Handbook of the Philosophy of Mind.* Cambridge University Press.
- Lau, H. & Rosenthal, D. (2011). *Empirical support for higher-order theories of conscious awareness.* **Trends in Cognitive Sciences** 15(8): 365–373.
- Brown, H., Adams, R.A., Parees, I., Edwards, M. & Friston, K. (2013). *Active inference, sensory attenuation and illusions.* **Cognitive Processing** 14(4): 411–427.

### Attention Schema Theory (AST)
- Graziano, M.S.A. (2019). *Rethinking Consciousness.* W.W. Norton.
- Graziano, M.S.A. & Webb, T.W. (2015). *The attention schema theory: a mechanistic account of subjective awareness.* **Frontiers in Psychology** 6: 500.
- Webb, T.W. & Graziano, M.S.A. (2015). *The attention schema theory of consciousness.* **Cognitive Neuropsychology** 32(3–4): 157–179.

### Free Will
- Libet, B. (1985). *Unconscious cerebral initiative and the role of conscious will in voluntary action.* **Behavioral and Brain Sciences** 8(4): 529–566.
- Haggard, P. (2008). *Human volition: towards a neuroscience of will.* **Nature Reviews Neuroscience** 9(12): 934–946.
- Soon, C.S. et al. (2008). *Unconscious determinants of free decisions in the human brain.* **Nature Neuroscience** 11(5): 543–545.
- Hallett, M. (2007). *Voluntary movement.* **Movement Disorders** 22(11): 1423–1437.
- Schurger, A. (2018). *A new look at the readiness potential.* **Current Biology** 28(10): R539–R541. — The modern reinterpretation.
- Schurger, A., Sitt, J.D. & Dehaene, S. (2012). *An accumulator model for spontaneous neural activity prior to self-initiated movement.* **PNAS** 109(42): E2904–E2913.
- Maoz, U. et al. (2019). *Free will and the brain.* In *The Nature of Consciousness.* MIT Press.

### Qualia
- Jackson, F. (1982). *Epiphenomenal qualia.* **Philosophical Quarterly** 32(127): 127–136. — The knowledge argument (Mary's Room).
- Nagel, T. (1974). *What is it like to be a bat?* **Philosophical Review** 83(4): 435–450.
- Dennett, D.C. (1988). *Quining qualia.* In *Consciousness in Contemporary Science.* Oxford University Press.
- Dennett, D.C. (1991). *Consciousness Explained.* Little, Brown.
- Chalmers, D.J. (2010). — See above.
- Tye, M. (2020). *Qualia.* In *The Stanford Encyclopedia of Philosophy.*
- Block, N. (1990). *Inverted earth.* **Philosophical Perspectives** 4: 53–79.

### Self
- Gallagher, S. (2000). *Philosophical conceptions of the self: implications for cognitive science.* **Trends in Cognitive Sciences** 4(1): 14–21.
- Frith, C.D. & Frith, U. (2012). *Mechanisms of social cognition.* **Annual Review of Psychology** 63: 287–313.
- Seth, A.K. (2021). *Being You: A New Science of Consciousness.* Dutton.
- Seth, A.K. & Friston, K. (2016). *Active interoceptive inference and the emotional brain.* **Philosophical Transactions of the Royal Society B** 371(1708): 20160007.
- Damasio, A. (2010). *Self Comes to Mind: Constructing the Conscious Brain.* Pantheon.
- Northoff, G., Hirjak, D. & Fuchs, T. (2021). *Self and brain.* **Nature Reviews Neuroscience** 22(12): 741–752.

### Animal Consciousness and Panpsychism
- Cambridge Declaration on Consciousness (2012). — The consensus statement on animal consciousness, signed by a group of prominent neuroscientists at the University of Cambridge.
- Low, P. (2012). *The Cambridge Declaration on Consciousness.* — Public statement.
- Goff, P. (2017). *Consciousness and Fundamental Reality.* Oxford University Press.
- Strawson, G. (2006). *Realistic monism: why physicalism entails panpsychism.* **Journal of Consciousness Studies** 13(10–11): 3–31.
- Chalmers, D.J. (1996). — See above (Russellian monism).
- Birch, J. (2020). *The search for invertebrate consciousness.* **Noûs** 56(1): 133–158.

### Illusionism
- Frankish, K. (2016). *Illusionism as a theory of consciousness.* **Journal of Consciousness Studies** 23(11–12): 11–39.
- Dennett, D.C. (1991). — See above.
- For an overview, see Frankish (2016) and Dennett (1991).

---

## Part 10: Bio-Inspired AI

### Neuromorphic Computing
- Mead, C. (1990). *Neuromorphic electronic systems.* **PNAS** 87(23): 10019–10026. — The founding paper.
- Merolla, P.A. et al. (2014). *A million spiking-neuron integrated circuit with a scalable communication network and interface.* **Science** 345(6197): 668–673. — TrueNorth.
- Davies, M. et al. (2021). *Loihi 2: a neuromorphic chip with on-chip learning.* **IEEE Micro** 41(5): 82–99.
- Furber, S.B., Galluppi, F., Temple, S. & Plana, L.A. (2014). *The SpiNNaker project.* **Proceedings of the IEEE** 102(5): 652–665.
- Pehle, C. et al. (2022). *The BrainScaleS-2 system.* arXiv:2204.02726.
- Tavanaei, A., Ghodrati, M., Kheradpisheh, S.R., Masquelier, T. & Maida, A. (2019). *Deep learning in spiking neural networks.* **Neural Networks** 111: 47–63.
- Indiveri, G. & Liu, S.-C. (2015). *Memory and information processing in neuromorphic systems.* **Proceedings of the IEEE** 103(8): 1379–1397.
- Stewart, T.C., Choo, X. & Eliasmith, C. (2012). *Spaun: a perception-cognition-action model using spiking neurons.* **Proceedings of the 34th Annual Conference of the Cognitive Science Society**.
- Roy, K., Jaiswal, A. & Panda, P. (2019). *Towards spike-based machine intelligence with neuromorphic computing.* **Nature** 575(7784): 607–617.

### Predictive Coding Networks
- Millidge, B., Salvatori, T., Song, Y., Bogacz, R. & Lukasiewicz, T. (2022). — See Part 4.
- Whittington, J.C.R. & Bogacz, R. (2019). — See Part 4.
- Mikulasch, F.A. et al. (2023). — See Part 4.
- Salvatori, T. et al. (2022). *Learning on the edge: a predictive coding account of the edge of stability.* arXiv:2204.04798.
- Sacramento, J. et al. (2018). *Dendritic cortical microcircuits approximate the backpropagation algorithm.* **NeurIPS**.
- Scellier, B. & Bengio, Y. (2017). *Equilibrium propagation: bridging the gap between energy-based models and backpropagation.* **Frontiers in Computational Neuroscience** 11: 24.
- Lillicrap, T.P., Cownden, D., Tweed, D.B. & Akerman, C.J. (2016). *Random synaptic feedback weights support error backpropagation in neural networks.* **Nature Communications** 7: 13276.
- Whittington, J.C.R., Warren, J. & Behrens, T.E.J. (2022). *Relating transformers to models and neural representations of the hippocampal formation.* arXiv:2112.04035.

### Three-Factor Reinforcement Learning
- Brzosko, Z. et al. (2017). — See Part 2.
- Wang, J.X. et al. (2018). *Prefrontal cortex as a meta-reinforcement learning system.* **Nature Neuroscience** 21(6): 860–868.
- Frémaux, N. & Gerstner, W. (2016). — See Part 2.
- Sutton, R.S. & Barto, A.G. (2018). — See Part 4.
- Williams, R.J. (1992). *Simple statistical gradient-following algorithms for connectionist reinforcement learning.* **Machine Learning** 8: 229–256. — REINFORCE.
- Mnih, V. et al. (2016). *Asynchronous methods for deep reinforcement learning.* **ICML**. — A3C.
- Lillicrap, T.P. et al. (2015). *Continuous control with deep reinforcement learning.* arXiv:1509.02971. — DDPG.
- Schulman, J. et al. (2017). *Proximal policy optimization algorithms.* arXiv:1707.06347. — PPO.

### World Models
- Ha, D. & Schmidhuber, J. (2018). *World models.* **NeurIPS**.
- Hafner, D. et al. (2019). *Learning latent dynamics for planning from pixels.* **ICML**. — PlaNet.
- Hafner, D. et al. (2020). *Dream to control: learning behaviors by latent imagination.* **ICLR**. — Dreamer v1.
- Hafner, D. et al. (2023). *Mastering diverse domains through world models.* **Nature** 638: 805–811. — Dreamer v3.
- Schrittwieser, J. et al. (2020). *Mastering Atari, Go, Chess and Shoki by planning with a learned model.* **Nature** 588: 604–609. — MuZero.
- LeCun, Y. (2022). — See Part 5.
- Sutton, R.S. (1990). *Integrated architectures for learning, planning, and reacting based on approximating dynamic programming.* **Proceedings of the 7th International Conference on Machine Learning**.
- Wayne, G. et al. (2018). *Unsupervised predictive memory in a goal-directed agent.* arXiv:1803.10760.
- Matsumoto, T. et al. (2022). *JAX-based efficient implementations of world models.* — See Dreamer v3 reference implementation.

### Active Inference
- Friston, K. (2010). — See Part 0.
- Friston, K. et al. (2010). — See Part 4.
- Friston, K., FitzGerald, T., Rigoli, F., Schwartenbeck, P. & Pezzulo, G. (2017). *Active inference: a process theory.* **Neural Computation** 29(1): 1–49.
- Pezzulo, G., Rigoli, F. & Friston, K. (2018). *Hierarchical active inference: a theory of motivated control.* **Trends in Cognitive Sciences** 22(4): 294–306.
- Buckley, C.L., Kim, C.S., McGregor, S. & Seth, A.K. (2017). *The free energy principle for action and perception: a mathematical review.* **Journal of Mathematical Psychology** 81: 55–79.
- Seth, A.K. (2014). *A predictive processing theory of sensorimotor contingencies: explaining the puzzle of perceptual presence and its absence in anosognosia.* **Neuroscience & Biobehavioral Reviews** 41: 58–75.
- Friston, K., Daunizeau, J., Kilner, J. & Kiebel, S.J. (2010). *Action and behavior: a free-energy formulation.* **Biological Cybernetics** 102(3): 227–260.
- Millidge, B., Tschantz, A. & Buckley, C.L. (2021). *Whence the expected free energy?* **Neural Computation** 33(2): 447–482.
- Tschantz, A. et al. (2020). *Reinforcement learning through active inference.* arXiv:2002.12636.
- Sajid, N., Ball, P.J. & Friston, K. (2021). *Active inference: demystified and compared.* **Neural Computation** 33(3): 674–712.

### Other Bio-Inspired Approaches
- Eliasmith, C. et al. (2012). *A large-scale model of the functioning brain.* **Science** 338(6111): 1202–1205. — Spaun.
- Knill, D.C. & Pouget, A. (2004). *The Bayesian brain: the role of uncertainty in neural coding and computation.* **Trends in Neurosciences** 27(12): 712–719.
- Kording, K. (2014). *Bayesian statistics for the working neuroscientist.* **Nature Neuroscience** 17(11): 1454–1461.
- Maass, W. (1997). *Networks of spiking neurons: the third generation of neural network models.* **Neural Networks** 10(9): 1659–1671.
- Markram, H. (2006). *The blue brain project.* **Nature Reviews Neuroscience** 7(2): 153–160.
- For a comprehensive overview, see the review by Hassabis et al. (2017) in Part 5.

---

## Part 11: Implementations

### Computational Neuroscience Simulators
- Stimberg, M., Brette, R. & Goodman, D.F. (2019). *Brian 2, a simulator for spiking neural networks in Python.* **eLife** 8: e47314.
- Gewaltig, M.-O. & Diesmann, M. (2007). *NEST (Neural Simulation Tool).* **Scholarpedia** 2(4): 1430.
- Carnevale, N.T. & Hines, M.L. (2006). *The NEURON Book.* Cambridge University Press.
- Goodman, D.F. & Brette, R. (2008). *Brian: a simulator for spiking neural networks in Python.* **Frontiers in Neuroinformatics** 2: 5.

### Deep Learning Frameworks
- Paszke, A. et al. (2019). *PyTorch: an imperative style, high-performance deep learning library.* **NeurIPS**.
- Harris, C.R. et al. (2020). *Array programming with NumPy.* **Nature** 585(7825): 357–362.
- Bradbury, J. et al. (2018). *JAX: composable transformations of Python+NumPy programs.* — JAX.
- Abadi, M. et al. (2016). *TensorFlow: a system for large-scale machine learning.* **OSDI**.

### Implementation References (specific demos in Part 11)
- Bi, G.-Q. & Poo, M.-M. (1998). — STDP. See Part 2.
- Turrigiano, G.G. et al. (1998). — Synaptic scaling. See Part 2.
- Tsodyks, M.V. & Markram, H. (1997). — See Part 1.
- Bittner, K.C. et al. (2017). — BTSP. See Part 2.
- Hubel, D.H. & Wiesel, T.N. (1962). — V1 receptive fields. See Part 3.
- Oja, E. (1982). — Oja rule. See Part 2.
- Friston, K. (2010). — Free-energy networks. See Part 0.

---

## Part 12: The Unification (MSPCH)

The Multi-Scale Predictive Coding Hypothesis draws on every prior part. The references below are the most relevant for each of the five core principles and the cross-scale predictions.

### Hierarchical Generative Models and Predictive Coding
- Rao, R.P.N. & Ballard, D.H. (1999). — See Part 4.
- Friston, K. (2005). — See Part 4.
- Friston, K. (2010). — See Part 0.
- Bastos, A.M. et al. (2012). — See Part 3.
- Keller, G.B. & Mrsic-Flogel, T.D. (2018). — See Part 4.
- Mikulasch, F.A. et al. (2023). — See Part 4.
- Millidge, B. et al. (2022). — See Part 4.
- Whittington, J.C.R. & Bogacz, R. (2019). — See Part 4.
- Heeger, D.J. (2017). *Theory of cortical function.* **PNAS** 114(8): 1773–1782.
- Markov, N.T. et al. (2013). *Cortical high-density counterstream architectures.* **Science** 342(6158): 1238406.
- McClelland, J.L., McNaughton, B.L. & O'Reilly, R.C. (1995). *Why there are complementary learning systems in the hippocampus and neocortex.* **Psychological Review** 102(3): 419–457.

### Amortized Inference and Replay
- Wilson, M.A. & McNaughton, B.L. (1994). — See Part 3.
- Rasch, B. & Born, J. (2013). — See Part 4.
- Grienberger, C. & Magee, J.C. (2020). — See Part 2.
- Bittner, K.C. et al. (2017). — BTSP. See Part 2.
- O'Reilly, R.C. & Norman, K.A. (2002). *Hippocampal and neocortical contributions to memory.* **Trends in Cognitive Sciences** 6(12): 505–510.

### Neuromodulator Gating
- Schultz, W., Dayan, P. & Montague, P.R. (1997). — See Part 2.
- Brzosko, Z. et al. (2017). — See Part 2.
- Frémaux, N. & Gerstner, W. (2016). — See Part 2.
- Doya, K. (2002). *Metalearning and neuromodulation.* **Neural Networks** 15(4–6): 495–506.
- Yu, A.J. & Dayan, P. (2005). *Uncertainty, neuromodulation, and attention.* **Neuron** 46(4): 681–692.
- Hasselmo, M.E. (2006). *The role of acetylcholine in learning and memory.* **Current Opinion in Neurobiology** 16(6): 710–715.
- Aston-Jones, G. & Cohen, J.D. (2005). *An integrative theory of locus coeruleus-norepinephrine function.* **Annual Review of Neuroscience** 28: 403–450.
- Cools, R., Roberts, A.C. & Robbins, T.W. (2008). *Serotonergic regulation of emotional and behavioural control processes.* **Trends in Cognitive Sciences** 12(1): 31–40.
- Sakurai, T. (2007). *The neural circuit of orexin (hypocretin).* **Nature Reviews Neuroscience** 8(3): 171–181.
- Adamantidis, A.R., Zhang, F., Aravanis, A.M., Deisseroth, K. & de Lecea, L. (2010). *Neural substrates of awakening probed with optogenetic control of hypocretin neurons.* **Nature** 462(7273): 420–424.

### Multi-System Memory
- Scoville, W.B. & Milner, B. (1957). — Patient H.M. See Part 3.
- Squire, L.R. (1992). — See Part 3.
- McClelland, J.L., McNaughton, B.L. & O'Reilly, R.C. (1995). — See above.
- Frankland, P.W. & Bontempi, B. (2005). *The organization of recent and remote memories.* **Nature Reviews Neuroscience** 6(2): 119–130.
- Buzsáki, G. (2015). — Sharp-wave ripples. See Part 3.
- Bittner, K.C. et al. (2017). — BTSP. See Part 2.
- Tse, D. et al. (2007). *Schemas and memory consolidation.* **Science** 316(5821): 76–82.

### Homeostatic Regulation
- Turrigiano, G.G. et al. (1998). — Synaptic scaling. See Part 2.
- Turrigiano, G. (2008). *The self-tuning neuron.* **Cell** 135(3): 422–435.
- Attwell, D. & Laughlin, S.B. (2001). — See Part 0.
- Allen, N.J. & Lyons, D.A. (2018). — Glia. See Part 3.
- Halassa, M.M. & Haydon, P.G. (2010). — See Part 3.
- Saper, C.B., Scammell, T.E. & Lu, J. (2005). *Hypothalamic regulation of sleep and circadian rhythms.* **Nature** 437(7063): 1257–1263.

### Intrinsic Motivation and Curiosity
- Schmidhuber, J. (1991). *A possibility for implementing curiosity and boredom in model-building neural controllers.* In *Proceedings of the International Conference on Simulation of Adaptive Behavior*, MIT Press.
- Pathak, D. et al. (2017). *Curiosity-driven exploration by self-supervised prediction.* **ICML**.
- Barto, A.G. (2013). *Intrinsic motivation and reinforcement learning.* In *Intrinsically Motivated Learning in Natural and Artificial Systems*, Springer.

### The Molecular Cascade (BDNF/CREB/Protein Synthesis)
- Kandel, E.R. (2001). — See Part 6.
- Kandel, E.R. (2012). — See Part 6.
- Bading, H. (2013). — See Part 6.
- Tonegawa, S. et al. (2018). *Memory engram cells have come of age.* **Neuron** 98(3): 524–529.
- Josselyn, S.A. & Tonegawa, S. (2020). *Memory engrams: Recalling the past and imagining the future.* **Science** 367(6473): eaaw4325.
- Ryan, T.J., Roy, D.S., Pignatelli, M., Arons, A. & Tonegawa, S. (2015). *Engram cells retain memory under retrograde amnesia.* **Science** 348(6238): 1007–1013.
- Costa-Mattioli, M. et al. (2005). *Translational control of hippocampal synaptic plasticity and memory by the eIF2α kinase GCN2.* **Nature** 436(7054): 1166–1170.

### Decision Making and Drift Diffusion
- Gold, J.I. & Shadlen, M.N. (2007). *The neural basis of decision making.* **Annual Review of Neuroscience** 30: 535–574.
- Ratcliff, R. & McKoon, G. (2008). *The diffusion decision model.* **Neural Computation** 20(4): 873–922.
- Wiecki, T.V., Sofer, I. & Frank, M.J. (2013). *HDDM: Hierarchical Bayesian estimation of the Drift-Diffusion Model in Python.* **Frontiers in Neuroinformatics** 7: 14.

### Drosophila Connectome
- Janelia Research Campus (2024). *Whole-brain connectome of the Drosophila larva.* **Nature** (the connectome paper; the full author list and exact citation will be added when the publication is finalized).
- Winding, M. et al. (2023). *The connectome of an insect brain.* **Science** 379(6636): 933–941. (Drosophila larva brain wiring.)
- Cook, S.J. et al. (2019). *Whole-animal connectomes of both Caenorhabditis elegans sexes.* **Nature** 571(7763): 63–71. — The C. elegans connectome.

### Sleep and Decision Making
- Drummond, S.P. et al. (2000). *Sleep deprivation-induced reduction in cortical functional response to serial subtraction.* **NeuroReport** 11(1): 91–95.
- Yoo, S.-S. et al. (2007). *The human emotional brain without sleep.* **Current Biology** 17(20): R877–R878.
- Krause, A.J. et al. (2017). *The sleep-deprived human brain.* **Nature Reviews Neuroscience** 18(7): 404–418.
- Walker, M.P. (2009). *The role of sleep in cognition and emotion.* **Annals of the New York Academy of Sciences** 1156(1): 168–197.

### Levels of Analysis (Marr)
- Marr, D. (1982). *Vision.* W.H. Freeman. — The computational/algorithmic/implementational trichotomy.

### Consciousness Frameworks
- Chalmers, D.J. (1995). — See Part 9.
- Tononi, G. (2004). — See Part 9.
- Baars, B.J. (1988). — See Part 9.
- Dehaene, S. (2014). — See Part 9.
- Koch, C. (2019). — See Part 9.

### The MSPCH Prototype
- Paszke, A. et al. (2019). *PyTorch.* See Part 11.
- Harris, C.R. et al. (2020). *NumPy.* See Part 11.
- Bradbury, J. et al. (2018). *JAX.* See Part 11.

---

## Foundational Textbooks

- Kandel, E.R. et al. (2013). *Principles of Neural Science* (5th ed.). McGraw-Hill.
- Purves, D. et al. (2018). *Neuroscience* (6th ed.). Oxford University Press.
- Dayan, P. & Abbott, L.F. (2001). *Theoretical Neuroscience.* MIT Press.
- Steriade, M. (2003). *Neuronal Substrates of Sleep and Epilepsy.* Cambridge University Press.
- Bear, M.F., Connors, B.W. & Paradiso, M.A. (2015). *Neuroscience: Exploring the Brain* (4th ed.). Lippincott.
- Nicholls, J.G. et al. (2012). *From Neuron to Brain* (5th ed.). Sinauer.
- For a computational textbook, see Dayan & Abbott (2001).

### Philosophy of Mind
- Chalmers, D.J. (1996). — See above.
- Searle, J.R. (1992). — See above.
- Dennett, D.C. (1991). — See above.
- Block, N., Flanagan, O. & Güzeldere, G. (1997). *The Nature of Consciousness.* MIT Press.
- Tononi, G. (2012). — See above.

---

## AI/ML References

- Sutton, R.S. & Barto, A.G. (2018). — See above.
- Goodfellow, I., Bengio, Y. & Courville, A. (2016). — See above.
- Bishop, C.M. (2006). *Pattern Recognition and Machine Learning.* Springer.
- LeCun, Y., Bengio, Y. & Hinton, G. (2015). *Deep learning.* **Nature** 521: 436–444.
- Vaswani, A. et al. (2017). *Attention is all you need.* **NeurIPS**.
- Silver, D. et al. (2016). *Mastering the game of Go with deep neural networks and tree search.* **Nature** 529: 484–489.
- Mnih, V. et al. (2015). *Human-level control through deep reinforcement learning.* **Nature** 518: 529–533.
- Schrittwieser, J. et al. (2020). — See above.

---

## Where to go from here

**For deeper neuroscience:** Read *Principles of Neural Science* (Kandel et al.) cover to cover.

**For computational neuroscience:** Read *Theoretical Neuroscience* (Dayan & Abbott).

**For brain-inspired AI:** Read *A Thousand Brains* (Hawkins), *On Intelligence* (Hawkins & Blakeslee), and the LeCun JEPA paper. Then explore spiking neural networks and neuromorphic computing.

**For predictive coding:** Read the original Rao & Ballard (1999) paper, then Friston's free energy papers, then the recent Millidge et al. survey. Then look at JEPA and World Models.

**For consciousness:** Start with Chalmers (1995) and Tononi (2004). Then Dehaene (2014) and Koch (2019). For philosophy, Nagel (1974) and Jackson (1982). For IIT specifically, Tononi et al. (2016) and Albantakis et al. (2023). For a recent overview, Seth & Bayne (2022).

**For disorders:** Selkoe (2011) for Alzheimer's, Jankovic (2008) and Poewe et al. (2017) for Parkinson's, Javitt (2007) and Howes & Kapur (2009) for schizophrenia, Nestler et al. (2002) and Krishnan & Nestler (2008) for depression, Wing & Gould (1979) and Hyman et al. (2020) for autism.

**For molecular signaling:** Berridge (1998) for calcium, then Kandel (2001) for the molecular biology of memory. Then Bading (2013) for nuclear calcium.

**For measurement:** Buzsáki (2006) for EEG, Logothetis (2008) for fMRI, Sakmann & Neher (2009) for patch clamp, Deisseroth (2011, 2015) for optogenetics, Denk et al. (1990) and Chen et al. (2013) for two-photon.

**For the latest:** Follow researchers on Twitter/X: @YannLeCun, @JeffDean, @karalford, @daphneli, @NeuroMLA. Or just keep reading arXiv.

---

Last updated: 2026.
