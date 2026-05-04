"""
Phase 145: Knowledge Graphs with LLMs (GraphRAG) — Colab Script
FRONTIER TRACK: Advanced production concept. Run on Google Colab T4.

What this does:
1. Loads Qwen/Qwen2.5-3B-Instruct for entity/relation extraction.
2. Takes a synthetic document about a tech acquisition scenario.
3. Extracts entities and relations using the LLM.
4. Builds a networkx knowledge graph.
5. Answers multi-hop questions via graph traversal.
6. Compares against a simulated vector-RAG baseline.

Every line explains WHY.
"""

# ---------------------------------------------------------------------------
# FRONTIER TRACK — Phase 145: GraphRAG on Colab T4
# ---------------------------------------------------------------------------

import gc
import re
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import networkx as nx
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------------------------------------------------------------------
# 1. Configuration — keep memory usage tight on T4
# ---------------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Device: {DEVICE}")
print(f"Model: {MODEL_NAME}")

# ---------------------------------------------------------------------------
# 2. Load model and tokenizer — 3B fits comfortably in T4 fp16
# ---------------------------------------------------------------------------
# WHY fp16: halves GPU memory with negligible accuracy loss at 3B scale.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    device_map="auto" if DEVICE == "cuda" else None,
)
model.eval()

# ---------------------------------------------------------------------------
# 3. Synthetic document — structured enough for extraction, small enough for speed
# ---------------------------------------------------------------------------
# WHY synthetic: deterministic so the script is reproducible without external downloads.
DOCUMENT = """
Alice Zhang founded QuantumAI in 2015 after graduating from MIT.
QuantumAI developed the NeuroChip, a breakthrough processor for edge devices.
In 2021, the semiconductor giant TitanCorp acquired QuantumAI for 2 billion dollars.
Bob Lee had been the Chief Technology Officer at QuantumAI since 2017.
After the acquisition, Bob Lee left QuantumAI and joined Stellar Labs as VP of Engineering.
Carol White is the CEO of TitanCorp and previously worked at Intel for ten years.
TitanCorp also acquired PhotonSys, a laser sensor startup founded by David Kim in 2019.
David Kim stayed on as head of the PhotonSys division after the acquisition.
Stellar Labs is a venture-backed startup in San Francisco focused on quantum networking.
Eve Brown is the founder and CEO of Stellar Labs.
"""

# ---------------------------------------------------------------------------
# 4. Prompt engineering for entity and relation extraction
# ---------------------------------------------------------------------------
# WHY structured output: LLMs are messy. Forcing a rigid format makes parsing reliable.
# WHY one-shot: showing an example in the prompt dramatically improves format adherence.

EXTRACTION_PROMPT = """You are a knowledge-graph extraction engine.
Read the following text and extract all entities and their relationships.

Output format rules:
- Entities: list each entity as "Entity: <name> (<type>)"
- Relations: list each relation as "Relation: <subject> | <predicate> | <object>"
- Do not include any other text, headers, or explanations.

Example:
Text: "Marie Curie discovered radium. She won the Nobel Prize."
Entity: Marie Curie (Person)
Entity: radium (Concept)
Entity: Nobel Prize (Award)
Relation: Marie Curie | discovered | radium
Relation: Marie Curie | won | Nobel Prize

Now extract from this text:
{text}

Entities and Relations:"""

# ---------------------------------------------------------------------------
# 5. Helper: run LLM generation with controlled sampling
# ---------------------------------------------------------------------------
# WHY temperature=0.1: extraction needs consistency, not creativity.
# WHY max_new_tokens=512: the document is short; this prevents runaway generation.

def generate(prompt, max_new_tokens=512):
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.1,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id,
        )
    # WHY skip input tokens: generate returns prompt + completion; we only want the new text.
    new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)

# ---------------------------------------------------------------------------
# 6. Extract entities and relations
# ---------------------------------------------------------------------------
print("\nExtracting entities and relations from document...")
prompt = EXTRACTION_PROMPT.format(text=DOCUMENT.strip())
raw_output = generate(prompt)
print("\n--- Raw LLM output ---")
print(raw_output)
print("--- End raw output ---\n")

# ---------------------------------------------------------------------------
# 7. Parse structured output with regex — fragile LLM output needs defense
# ---------------------------------------------------------------------------
# WHY regex: cheaper and more deterministic than asking the LLM to parse itself.
entities = []
relations = []

for line in raw_output.split('\n'):
    line = line.strip()
    if not line:
        continue
    ent_match = re.match(r'Entity:\s*(.+?)\s*\((.+?)\)', line)
    if ent_match:
        name = ent_match.group(1).strip()
        etype = ent_match.group(2).strip()
        entities.append((name, etype))
        continue
    rel_match = re.match(r'Relation:\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)', line)
    if rel_match:
        subj = rel_match.group(1).strip()
        pred = rel_match.group(2).strip()
        obj = rel_match.group(3).strip()
        relations.append((subj, pred, obj))

print(f"Parsed {len(entities)} entities and {len(relations)} relations.")
for e in entities:
    print(f"  Entity: {e[0]} ({e[1]})")
for r in relations:
    print(f"  Relation: {r[0]} | {r[1]} | {r[2]}")

# ---------------------------------------------------------------------------
# 8. Build networkx directed graph from extracted triples
# ---------------------------------------------------------------------------
# WHY networkx: standard graph library; handles traversal, visualization, and analysis.
G = nx.DiGraph()

for name, etype in entities:
    # WHY lowercase normalization: reduces duplicate nodes from capitalization variance.
    G.add_node(name.lower(), type=etype)

for subj, pred, obj in relations:
    s = subj.lower()
    o = obj.lower()
    # WHY add missing nodes: LLMs sometimes mention objects without explicit entity lines.
    if s not in G:
        G.add_node(s, type='unknown')
    if o not in G:
        G.add_node(o, type='unknown')
    G.add_edge(s, o, relation=pred)

print(f"\nGraph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

# ---------------------------------------------------------------------------
# 9. Define multi-hop questions and graph traversal answerer
# ---------------------------------------------------------------------------
# WHY manual question design: we need ground-truth answers to measure accuracy.

QUESTIONS = [
    {
        'question': 'Who is the CEO of the company that acquired QuantumAI?',
        'start': 'QuantumAI',
        'expected_answer': 'Carol White',
        ' hops': 2,
    },
    {
        'question': 'Who founded the company that was acquired by TitanCorp and developed NeuroChip?',
        'start': 'TitanCorp',
        'expected_answer': 'Alice Zhang',
        'hops': 2,
    },
    {
        'question': 'Who is the CEO of the company where Bob Lee works now?',
        'start': 'Bob Lee',
        'expected_answer': 'Eve Brown',
        'hops': 3,
    },
]

def answer_with_graph(graph, start_entity, max_hops=3):
    """
    BFS traversal to collect all reachable nodes within max_hops.
    Returns the subgraph nodes and edges for LLM reasoning.
    WHY BFS: guarantees shortest paths, which are usually the most relevant.
    """
    start = start_entity.lower()
    if start not in graph:
        return None, []

    visited = {start: 0}
    queue = [start]
    while queue:
        current = queue.pop(0)
        if visited[current] >= max_hops:
            continue
        for neighbor in graph.successors(current):
            if neighbor not in visited:
                visited[neighbor] = visited[current] + 1
                queue.append(neighbor)
        for neighbor in graph.predecessors(current):
            if neighbor not in visited:
                visited[neighbor] = visited[current] + 1
                queue.append(neighbor)

    # Extract subgraph edges as textual facts
    subgraph_nodes = set(visited.keys())
    facts = []
    for u, v, data in graph.edges(data=True):
        if u in subgraph_nodes and v in subgraph_nodes:
            facts.append(f"{u} {data['relation']} {v}")
    return list(subgraph_nodes), facts

# ---------------------------------------------------------------------------
# 10. Answer questions with Graph RAG and Vector RAG baseline
# ---------------------------------------------------------------------------
# WHY vector baseline simulated: real embeddings require an embedding model.
# We simulate by checking if expected answer is in a random sample of nodes.

print("\n" + "=" * 70)
print("Evaluating multi-hop questions")
print("=" * 70)

graph_results = []
vector_results = []

for q_item in tqdm(QUESTIONS, desc="Questions"):
    question = q_item['question']
    start = q_item['start']
    expected = q_item['expected_answer'].lower()

    # --- Graph RAG ---
    nodes, facts = answer_with_graph(G, start, max_hops=3)
    # Build a reasoning prompt with the subgraph facts
    facts_text = '\n'.join(facts) if facts else 'No relevant facts found.'
    reasoning_prompt = (
        f"You are a helpful assistant. Use ONLY the following facts to answer the question.\n"
        f"If the answer is not in the facts, say 'I don't know'.\n\n"
        f"Facts:\n{facts_text}\n\n"
        f"Question: {question}\nAnswer:"
    )
    graph_answer = generate(reasoning_prompt, max_new_tokens=64).strip().lower()
    graph_hit = expected in graph_answer
    graph_results.append(graph_hit)

    # --- Vector RAG simulation ---
    # WHY random sample: simulates that vector retrieval returns top-k semantically
    # similar chunks, which often miss the multi-hop answer node.
    np.random.seed(hash(question) % 2**31)
    sample_size = min(4, len(nodes)) if nodes else 0
    sampled = np.random.choice(list(G.nodes()), size=min(4, G.number_of_nodes()), replace=False)
    sample_facts = []
    for u, v, data in G.edges(data=True):
        if u in sampled or v in sampled:
            sample_facts.append(f"{u} {data['relation']} {v}")
    sample_text = '\n'.join(sample_facts) if sample_facts else 'No relevant facts found.'
    vec_prompt = (
        f"You are a helpful assistant. Use ONLY the following facts to answer the question.\n"
        f"If the answer is not in the facts, say 'I don't know'.\n\n"
        f"Facts:\n{sample_text}\n\n"
        f"Question: {question}\nAnswer:"
    )
    vec_answer = generate(vec_prompt, max_new_tokens=64).strip().lower()
    vec_hit = expected in vec_answer
    vector_results.append(vec_hit)

    print(f"\nQ: {question}")
    print(f"  Graph RAG answer: {graph_answer[:120]}... | Match: {graph_hit}")
    print(f"  Vector RAG answer: {vec_answer[:120]}... | Match: {vec_hit}")

graph_acc = np.mean(graph_results) * 100
vec_acc = np.mean(vector_results) * 100
print(f"\nGraph RAG accuracy: {graph_acc:.0f}%")
print(f"Vector RAG accuracy: {vec_acc:.0f}%")

# ---------------------------------------------------------------------------
# 11. Visualization: extracted graph
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
pos = nx.spring_layout(G, k=1.5, seed=42)

# Color nodes by type
type_colors = {}
colors = ['steelblue', 'coral', 'seagreen', 'gold', 'mediumpurple']
for idx, ntype in enumerate(set(nx.get_node_attributes(G, 'type').values())):
    type_colors[ntype] = colors[idx % len(colors)]

node_colors = [type_colors.get(G.nodes[n].get('type', 'unknown'), 'gray') for n in G.nodes()]

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500, ax=ax, edgecolors='black')
nx.draw_networkx_labels(G, pos, font_size=8, font_color='white', ax=ax)

# Draw edges with relation labels
edge_labels = {(u, v): d['relation'] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15, edge_color='gray', ax=ax)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, ax=ax,
                              bbox=dict(boxstyle='round,pad=0.2', facecolor='wheat', alpha=0.7))

ax.set_title('Phase 145: LLM-Extracted Knowledge Graph')
ax.axis('off')
plt.tight_layout()
plt.savefig('src/phase145/phase145_colab_extracted_graph.png', dpi=150)
plt.close()
print("\nSaved plot: src/phase145/phase145_colab_extracted_graph.png")

# ---------------------------------------------------------------------------
# 12. Visualization: accuracy comparison
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4))
methods = ['Vector RAG\n(simulated)', 'Graph RAG']
accuracies = [vec_acc, graph_acc]
bars = ax.bar(methods, accuracies, color=['coral', 'seagreen'], edgecolor='black')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Multi-Hop QA: Vector RAG vs Graph RAG')
ax.set_ylim(0, 110)
for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{acc:.0f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('src/phase145/phase145_colab_accuracy_comparison.png', dpi=150)
plt.close()
print("Saved plot: src/phase145/phase145_colab_accuracy_comparison.png")

# ---------------------------------------------------------------------------
# 13. Memory cleanup — T4 has limited VRAM; free it for the next cell
# ---------------------------------------------------------------------------
# WHY explicit cleanup: prevents OOM when users rerun cells or run subsequent phases.
del model
del tokenizer
if DEVICE == "cuda":
    torch.cuda.empty_cache()
gc.collect()

print("\nPhase 145 Colab script complete. Model unloaded.")
