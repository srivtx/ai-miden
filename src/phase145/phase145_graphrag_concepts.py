"""
Phase 145: Knowledge Graphs with LLMs (GraphRAG) — Concepts
Demonstrates why graph traversal beats vector retrieval on multi-hop questions.
Uses only NumPy and Matplotlib (no PyTorch) so it runs locally.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Build a simulated knowledge graph as an adjacency matrix
# ---------------------------------------------------------------------------
# We create a small graph of people, companies, and products.
# Nodes are entities; directed edges are relationships.

node_names = [
    'Alice',      # 0
    'Bob',        # 1
    'Carol',      # 2
    'Diana',      # 3
    'AcmeCorp',   # 4
    'WidgetCo',   # 5
    'TechGiant',  # 6
    'Gadget',     # 7
]

N = len(node_names)

# Adjacency matrix: adj[i, j] = 1 if there is a directed edge i -> j
adj = np.zeros((N, N), dtype=int)

# Define edges (subject -> object) with relationship labels stored separately
edges = [
    (0, 4, 'founded'),      # Alice founded AcmeCorp
    (4, 5, 'acquired'),     # AcmeCorp acquired WidgetCo
    (2, 4, 'CEO of'),       # Carol CEO of AcmeCorp
    (1, 5, 'founded'),      # Bob founded WidgetCo
    (6, 4, 'acquired'),     # TechGiant acquired AcmeCorp
    (3, 6, 'CEO of'),       # Diana CEO of TechGiant
    (1, 7, 'invented'),     # Bob invented Gadget
    (5, 7, 'produces'),     # WidgetCo produces Gadget
]

for src, dst, _ in edges:
    adj[src, dst] = 1

# ---------------------------------------------------------------------------
# 2. Simulate vector RAG: each node has a document embedding
# ---------------------------------------------------------------------------
# In real vector RAG, chunks are embedded and retrieved by similarity.
# Here we simulate embeddings so that chunks about acquisitions are close
# to acquisition questions, but chunks about CEOs are far away.
np.random.seed(42)
embed_dim = 16
node_embeddings = np.random.randn(N, embed_dim)
# Normalize for cosine similarity
node_embeddings = node_embeddings / np.linalg.norm(node_embeddings, axis=1, keepdims=True)

def vector_rag_retrieve(query_embedding, k=2):
    """Return top-k nodes by cosine similarity to query."""
    sims = node_embeddings @ query_embedding
    topk = np.argsort(sims)[::-1][:k]
    return topk, sims[topk]

# ---------------------------------------------------------------------------
# 3. Simulate graph traversal: BFS to find paths
# ---------------------------------------------------------------------------

def bfs_traversal(start_node, max_hops=3):
    """Return all nodes reachable within max_hops and their hop distance.
    WHY undirected traversal: reasoning questions often require walking
    against the edge direction (e.g., 'acquired by' is the inverse of 'acquired').
    """
    visited = {start_node: 0}
    queue = [start_node]
    while queue:
        current = queue.pop(0)
        if visited[current] >= max_hops:
            continue
        # Walk both outgoing and incoming edges so the graph is navigable both ways
        neighbors = np.where(adj[current] == 1)[0].tolist()
        neighbors += np.where(adj[:, current] == 1)[0].tolist()
        for neighbor in neighbors:
            if neighbor not in visited:
                visited[neighbor] = visited[current] + 1
                queue.append(neighbor)
    return visited

def find_path(start, end, max_hops=3):
    """Find shortest path from start to end using BFS on an undirected view."""
    if start == end:
        return [start]
    queue = [(start, [start])]
    visited = {start}
    while queue:
        current, path = queue.pop(0)
        if len(path) > max_hops + 1:
            continue
        neighbors = np.where(adj[current] == 1)[0].tolist()
        neighbors += np.where(adj[:, current] == 1)[0].tolist()
        for neighbor in neighbors:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None

# ---------------------------------------------------------------------------
# 4. Define multi-hop questions and evaluate both methods
# ---------------------------------------------------------------------------
# Each question is: (query_entity_name, query_embedding_hint, answer_name, description)
# The query_embedding_hint biases vector retrieval toward a specific node type.

questions = [
    {
        'q': 'Who is the CEO of the company that acquired WidgetCo?',
        'start': 'WidgetCo',
        'answer': 'Carol',
        'path_desc': 'WidgetCo -> acquired by -> AcmeCorp -> CEO -> Carol',
        # For vector RAG, we simulate that the query is close to the acquisition chunk
        'query_bias_node': 'AcmeCorp',
    },
    {
        'q': 'Who is the CEO of the company that acquired AcmeCorp?',
        'start': 'AcmeCorp',
        'answer': 'Diana',
        'path_desc': 'AcmeCorp -> acquired by -> TechGiant -> CEO -> Diana',
        'query_bias_node': 'TechGiant',
    },
    {
        'q': 'Who invented the product produced by WidgetCo?',
        'start': 'WidgetCo',
        'answer': 'Bob',
        'path_desc': 'WidgetCo -> produces -> Gadget -> invented by -> Bob',
        'query_bias_node': 'Gadget',
    },
]

vector_correct = 0
graph_correct = 0

print('=' * 70)
print('Phase 145: GraphRAG Concepts — Multi-Hop Question Evaluation')
print('=' * 70)

results = []

for item in questions:
    start_idx = node_names.index(item['start'])
    answer_idx = node_names.index(item['answer'])

    # --- Vector RAG simulation ---
    # The query embedding is biased toward the intermediate node (e.g., AcmeCorp)
    # but vector RAG only retrieves the top-k similar nodes, not the full path.
    bias_idx = node_names.index(item['query_bias_node'])
    query_emb = node_embeddings[bias_idx] + 0.3 * np.random.randn(embed_dim)
    query_emb = query_emb / np.linalg.norm(query_emb)
    topk, sims = vector_rag_retrieve(query_emb, k=2)

    # Vector RAG "succeeds" only if the answer node is in the top-k retrieved nodes.
    # For multi-hop, the answer is rarely in the top-k because it is semantically
    # distant from the question's surface form.
    vec_success = answer_idx in topk
    if vec_success:
        vector_correct += 1

    # --- Graph RAG simulation ---
    # Traverse from the start entity up to 3 hops.
    reachable = bfs_traversal(start_idx, max_hops=3)
    graph_success = answer_idx in reachable
    if graph_success:
        graph_correct += 1

    path = find_path(start_idx, answer_idx, max_hops=3)
    path_str = ' -> '.join([node_names[i] for i in path]) if path else 'NO PATH'

    results.append({
        'question': item['q'],
        'vector_success': vec_success,
        'graph_success': graph_success,
        'path': path_str,
        'topk': [node_names[i] for i in topk],
    })

    print(f"\nQuestion: {item['q']}")
    print(f"  Vector RAG retrieved: {results[-1]['topk']}  |  Correct? {vec_success}")
    print(f"  Graph RAG path:       {path_str}  |  Correct? {graph_success}")

print(f"\n{'=' * 70}")
print(f"Vector RAG accuracy: {vector_correct}/{len(questions)} ({vector_correct/len(questions)*100:.0f}%)")
print(f"Graph RAG accuracy:  {graph_correct}/{len(questions)} ({graph_correct/len(questions)*100:.0f}%)")
print(f"{'=' * 70}")

# ---------------------------------------------------------------------------
# 5. Visualization 1: Graph structure
# ---------------------------------------------------------------------------
# Layout nodes in a circle for clarity.
angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
pos = {i: (np.cos(a), np.sin(a)) for i, a in enumerate(angles)}

fig, ax = plt.subplots(figsize=(8, 8))
for i, (x, y) in pos.items():
    ax.scatter(x, y, s=800, c='steelblue', zorder=2)
    ax.text(x, y, node_names[i], ha='center', va='center', fontsize=9, color='white', fontweight='bold')

for src, dst, rel in edges:
    x1, y1 = pos[src]
    x2, y2 = pos[dst]
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    # Label the edge near the midpoint
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my, rel, fontsize=7, color='darkred', ha='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='wheat', alpha=0.7))

ax.set_title('Phase 145: Simulated Knowledge Graph')
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.axis('off')
plt.tight_layout()
plt.savefig('src/phase145/phase145_graph_structure.png', dpi=150)
plt.close()
print("Saved plot: src/phase145/phase145_graph_structure.png")

# ---------------------------------------------------------------------------
# 6. Visualization 2: Vector RAG vs Graph RAG accuracy comparison
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 4))
methods = ['Vector RAG', 'Graph RAG']
accuracies = [vector_correct / len(questions) * 100, graph_correct / len(questions) * 100]
colors = ['coral', 'seagreen']
bars = ax.bar(methods, accuracies, color=colors, edgecolor='black')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Multi-Hop Question Answering: Vector RAG vs Graph RAG')
ax.set_ylim(0, 110)
for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{acc:.0f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('src/phase145/phase145_accuracy_comparison.png', dpi=150)
plt.close()
print("Saved plot: src/phase145/phase145_accuracy_comparison.png")

# ---------------------------------------------------------------------------
# 7. Visualization 3: Retrieval path for each question
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, len(questions), figsize=(15, 5))
if len(questions) == 1:
    axes = [axes]

for ax_idx, (res, item) in enumerate(zip(results, questions)):
    ax = axes[ax_idx]
    # Highlight the path nodes and edges
    path_indices = [node_names.index(n) for n in res['path'].split(' -> ')] if res['path'] != 'NO PATH' else []

    for i, (x, y) in pos.items():
        color = 'gold' if i in path_indices else 'steelblue'
        size = 1000 if i in path_indices else 800
        ax.scatter(x, y, s=size, c=color, edgecolors='black', zorder=2)
        ax.text(x, y, node_names[i], ha='center', va='center', fontsize=8, color='white', fontweight='bold')

        for src, dst, rel in edges:
            x1, y1 = pos[src]
            x2, y2 = pos[dst]
            is_path_edge = False
            for k in range(len(path_indices) - 1):
                # Highlight edge if traversed in either direction
                if (path_indices[k] == src and path_indices[k+1] == dst) or \
                   (path_indices[k] == dst and path_indices[k+1] == src):
                    is_path_edge = True
                    break
            color = 'darkorange' if is_path_edge else 'lightgray'
            lw = 2.5 if is_path_edge else 1.0
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', color=color, lw=lw))

    ax.set_title(f"Q{ax_idx+1}: {'Found' if res['graph_success'] else 'Missed'}", fontsize=10)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')

plt.suptitle('Graph RAG Retrieval Paths for Multi-Hop Questions', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('src/phase145/phase145_retrieval_paths.png', dpi=150)
plt.close()
print("Saved plot: src/phase145/phase145_retrieval_paths.png")

print("\nPhase 145 concept demonstration complete.")
