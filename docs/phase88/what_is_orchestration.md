# What is Orchestration?

## Why it exists (THE PROBLEM first)

Training a modern AI system involves data preprocessing, model training, hyperparameter tuning, evaluation, and deployment. Each step has dependencies, resource requirements, and failure modes. Manually executing these steps in order across dozens of machines leads to missed steps, resource conflicts, and untracked experiments.

## Definition (very simple)

Orchestration is the automated coordination and management of multiple computational tasks, ensuring they run in the correct order, on the correct resources, and with proper handling of failures and retries.

## Real-life analogy

A conductor does not play any instrument. Instead, they wave a baton to tell the violins when to start, the brass when to join, and the percussion when to crescendo. Orchestration software is the conductor for ML pipelines: it tells each job when and where to run.

## Tiny numeric example

A pipeline has 5 stages: extract (1 CPU), transform (2 CPUs), train (4 GPUs), evaluate (1 GPU), and deploy (0 GPUs). An orchestrator queues these stages, launches extract first, waits for it to finish, then launches transform, and so on. If train fails, it retries twice before alerting the team.

## Common confusion

- **Orchestration is not the same as scheduling.** Scheduling decides where a job runs; orchestration decides when and in what order jobs run and how they connect.
- **It is not a replacement for good code.** A buggy training script will still fail no matter how well it is orchestrated.
- **Orchestration does not mean parallel execution of everything.** It respects dependencies; some tasks must wait for others.
- **It is not only for training.** Orchestration also manages data ingestion, monitoring, and model serving pipelines.
- **Airflow, Kubeflow, and Metaflow are orchestrators, not competitors to Kubernetes.** They often run on top of Kubernetes.

## Where it is used in our code

In `src/phase88/phase88_orchestration.py`, we write a Python loop that assigns jobs to nodes based on CPU, GPU, and memory availability. This is a toy version of what orchestrators like Kubernetes or Kubeflow do automatically across thousands of nodes.
