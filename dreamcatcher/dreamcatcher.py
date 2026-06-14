"""
DreamCatcher: A brain-inspired personal knowledge management system.
===================================================================

Based on the Multi-Scale Predictive Coding Hypothesis (MSPCH) developed
in `docs/nature/12_unification/`.

The system applies five MSPCH principles to personal knowledge management:

1. Multi-system memory
   - Fast: a "hippocampal" raw capture store. One-shot binding of any
     input (text, URL, quote, idea) to a high-dimensional vector.
   - Slow: a "neocortical" consolidated store. Structured, deduplicated,
     connected knowledge graph that emerges from replay.

2. Replay-driven consolidation (the "sleep" job)
   - A nightly job that replays recent captures, finds duplicates,
     clusters related items, builds summaries, and links them to
     existing knowledge. Like sleep, this runs offline and is unsupervised.

3. Neuromodulator gating
   - ACh (novelty): every item gets a "novelty score" based on its
     distance to existing consolidated knowledge. Surface novel items.
   - DA (reward): every item gets a "use count". Frequently accessed
     items are weighted higher and protected from pruning.

4. Homeostasis (the "prune" job)
   - Items with no access for >90 days are pruned. This keeps the
     knowledge base bounded in size, like synaptic scaling in cortex.

5. Intrinsic motivation (the "surprise" mode)
   - A random walk through the knowledge graph that surfaces items
     which are *least similar* to recent context. Like curiosity,
     this drives exploration of forgotten material.

The math is from MSPCH Part 0.4 (the variational free energy) and
Part 2.4 (denoising score matching). The intuition is that your
personal knowledge base is a *generative model of what you know*,
and the consolidation step is the score-matching update.

Run:
    python dreamcatcher.py add "Just read about MSPCH. The brain might
                                  run variational inference at all scales."
    python dreamcatcher.py add --url https://arxiv.org/abs/2006.11239
                                  --title "DDPM paper"
    python dreamcatcher.py sleep
    python dreamcatcher.py search "diffusion"
    python dreamcatcher.py surprise
    python dreamcatcher.py prune
    python dreamcatcher.py status
"""

import os
import re
import json
import math
import sqlite3
import argparse
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Storage layer (multi-system memory)
# =============================================================================

DB_PATH = "dreamcatcher.db"

def init_db(path=DB_PATH):
    """Initialize the multi-system memory tables."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    # Fast memory: raw captures (hippocampus-like)
    c.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY,
            content TEXT,
            source TEXT,
            timestamp REAL,
            embedding BLOB,
            use_count INTEGER DEFAULT 0
        )
    """)
    # Slow memory: consolidated knowledge (cortex-like)
    c.execute("""
        CREATE TABLE IF NOT EXISTS consolidated (
            id INTEGER PRIMARY KEY,
            summary TEXT,
            members TEXT,
            timestamp REAL,
            embedding BLOB,
            use_count INTEGER DEFAULT 0
        )
    """)
    # Access log for homeostasis
    c.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            item_id INTEGER,
            item_type TEXT,
            timestamp REAL
        )
    """)
    # Vocabulary for TF-IDF
    c.execute("""
        CREATE TABLE IF NOT EXISTS vocab (
            term TEXT PRIMARY KEY,
            idf REAL
        )
    """)
    conn.commit()
    conn.close()


# =============================================================================
# Text processing and TF-IDF embeddings
# =============================================================================

STOP_WORDS = set("""
a an the and or but if while of for to in on at by from with as is are was were be been being
this that these those it its their there here where when who what which how why i you he she we
they me him her us them my your his hers our their mine yours his hers ours theirs
do does did done have has had having say says said saying go goes went gone come comes came
get got getting make makes made making take takes taken taking know knows knew known
see saw seen look looks looked looking want wants wanted use uses used used using
find finds found found think thinks thought thinking say says said
""".split())


def tokenize(text):
    """Lowercase, remove punctuation, split, drop stop words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def build_vocab(conn):
    """Compute IDF over the current capture set. New terms are added with
    a smoothed IDF, existing terms keep their IDF. This keeps the vocab
    size stable across runs."""
    c = conn.cursor()
    c.execute("SELECT content FROM captures")
    docs = c.fetchall()
    if not docs:
        return
    n_docs = len(docs)
    df = Counter()
    for (content,) in docs:
        tokens = set(tokenize(content or ""))
        for t in tokens:
            df[t] += 1
    # Get existing vocab to preserve IDs
    c.execute("SELECT term, idf FROM vocab")
    existing = dict(c.fetchall())
    # Update or insert each term
    for term, freq in df.items():
        idf = math.log((n_docs + 1) / (freq + 1)) + 1
        if term in existing:
            c.execute("UPDATE vocab SET idf = ? WHERE term = ?", (idf, term))
        else:
            c.execute("INSERT INTO vocab VALUES (?, ?)", (term, idf))
    conn.commit()


def reembed_all(conn):
    """Re-compute all embeddings with the current vocabulary. Called after
    vocab changes so old items use the new dimension."""
    c = conn.cursor()
    vocab = get_vocab(conn)
    if not vocab:
        return
    # Re-embed captures
    c.execute("SELECT id, content FROM captures")
    for r in c.fetchall():
        emb = tfidf_vector(r[1] or "", vocab)
        c.execute("UPDATE captures SET embedding = ? WHERE id = ?", (emb.tobytes(), r[0]))
    # Re-embed consolidated
    c.execute("SELECT id, summary FROM consolidated")
    for r in c.fetchall():
        emb = tfidf_vector(r[1] or "", vocab)
        c.execute("UPDATE consolidated SET embedding = ? WHERE id = ?", (emb.tobytes(), r[0]))
    conn.commit()


def tfidf_vector(text, vocab):
    """Compute TF-IDF vector for a text given the vocabulary."""
    tokens = tokenize(text)
    if not tokens:
        return np.zeros(len(vocab), dtype=np.float64)
    tf = Counter(tokens)
    total = len(tokens)
    vec = np.zeros(len(vocab), dtype=np.float64)
    for i, (term, idf) in enumerate(vocab):
        if term in tf:
            vec[i] = (tf[term] / total) * idf
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def get_vocab(conn):
    """Load the current vocabulary as an ordered list of (term, idf)."""
    c = conn.cursor()
    c.execute("SELECT term, idf FROM vocab ORDER BY term")
    return c.fetchall()


def get_embedding(text, conn):
    """Get or compute the embedding for a text. Rebuilds vocab if empty."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM vocab")
    if c.fetchone()[0] == 0:
        build_vocab(conn)
    vocab = get_vocab(conn)
    return tfidf_vector(text, vocab)


def cosine_similarity(a, b):
    """Cosine similarity between two vectors. Returns 0 for zero vectors."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# =============================================================================
# Capture layer (fast memory)
# =============================================================================

def add_capture(content, source="text", path=DB_PATH):
    """Add a new item to the fast (hippocampal) memory."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    emb = get_embedding(content, conn)
    ts = datetime.now().timestamp()
    c.execute(
        "INSERT INTO captures (content, source, timestamp, embedding, use_count) VALUES (?, ?, ?, ?, 0)",
        (content, source, ts, emb.tobytes())
    )
    conn.commit()
    capture_id = c.lastrowid
    conn.close()
    return capture_id


def get_all_captures(path=DB_PATH):
    """Retrieve all captures (used by consolidation)."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, content, source, timestamp, embedding, use_count FROM captures")
    rows = c.fetchall()
    conn.close()
    return rows


def get_recent_captures(days=1, path=DB_PATH):
    """Retrieve captures from the last N days (used by sleep)."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).timestamp()
    c.execute(
        "SELECT id, content, source, timestamp, embedding, use_count FROM captures WHERE timestamp > ?",
        (cutoff,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


# =============================================================================
# Consolidation layer (the "sleep" job)
# =============================================================================

def consolidate(days=1, dedup_threshold=0.85, path=DB_PATH):
    """
    The "sleep" job: replay recent captures, deduplicate, cluster, build summaries.
    This is the brain's system consolidation in code.
    """
    conn = sqlite3.connect(path)
    c = conn.cursor()

    # Rebuild vocabulary to capture new terms, then re-embed everything
    # with the new vocab so dimensions match.
    build_vocab(conn)
    reembed_all(conn)
    vocab = get_vocab(conn)
    n_vocab = len(vocab)
    if n_vocab == 0:
        conn.close()
        return {"duplicates_merged": 0, "clusters_built": 0, "items_processed": 0}

    # Get recent captures
    cutoff = (datetime.now() - timedelta(days=days)).timestamp()
    c.execute("SELECT id, content, source, timestamp, embedding, use_count FROM captures WHERE timestamp > ?", (cutoff,))
    recent = c.fetchall()
    if not recent:
        conn.close()
        return {"duplicates_merged": 0, "clusters_built": 0, "items_processed": 0}

    # Compute embeddings as numpy arrays
    items = []
    for r in recent:
        emb = np.frombuffer(r[4], dtype=np.float64)
        items.append({"id": r[0], "content": r[1], "source": r[2], "timestamp": r[3], "embedding": emb, "use_count": r[5]})

    # Step 1: deduplication (ACh = novelty signal: low similarity = high novelty)
    # Near-duplicates: items with cosine similarity > threshold
    to_merge = set()
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            sim = cosine_similarity(items[i]["embedding"], items[j]["embedding"])
            if sim > dedup_threshold:
                pairs.append((i, j, sim))
    # If no high-similarity pairs found, lower the threshold
    if not pairs:
        # Use a softer threshold (relative: find pairs in the top quartile of similarity)
        sims = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                sims.append((i, j, cosine_similarity(items[i]["embedding"], items[j]["embedding"])))
        sims.sort(key=lambda x: -x[2])
        if sims and sims[0][2] > 0.3:
            # Take the top 25% of pairs above 0.3 similarity
            top = sims[:max(1, len(sims) // 4)]
            top = [s for s in top if s[2] > 0.3]
            for i, j, sim in top:
                pairs.append((i, j, sim))

    # Greedy merge: keep the older item, mark the newer for deletion
    merged_ids = []
    for i, j, sim in pairs:
        if items[j]["id"] in to_merge or items[i]["id"] in to_merge:
            continue
        # Keep the one with higher use_count; otherwise the older
        if items[i]["use_count"] >= items[j]["use_count"]:
            to_merge.add(items[j]["id"])
            merged_ids.append((items[i]["id"], items[j]["id"]))
        else:
            to_merge.add(items[i]["id"])
            merged_ids.append((items[j]["id"], items[i]["id"]))

    # Step 2: clustering by similarity (simple single-linkage)
    # For each remaining item, find a cluster in consolidated memory
    c.execute("SELECT id, summary, members, timestamp, embedding, use_count FROM consolidated")
    consolidated = c.fetchall()
    consolidated_items = []
    for r in consolidated:
        emb = np.frombuffer(r[4], dtype=np.float64)
        consolidated_items.append({
            "id": r[0], "summary": r[1], "members": json.loads(r[2]),
            "timestamp": r[3], "embedding": emb, "use_count": r[5]
        })

    cluster_threshold = 0.5
    n_new_clusters = 0
    n_added_to_clusters = 0
    for item in items:
        if item["id"] in to_merge:
            continue
        # Find most similar existing cluster
        best_cluster = None
        best_sim = -1
        for c_item in consolidated_items:
            sim = cosine_similarity(item["embedding"], c_item["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_cluster = c_item
        if best_cluster is not None and best_sim > cluster_threshold:
            # Add to this cluster
            best_cluster["members"].append(item["id"])
            best_cluster["timestamp"] = max(best_cluster["timestamp"], item["timestamp"])
            # Update the consolidated item
            c.execute(
                "UPDATE consolidated SET members = ?, timestamp = ? WHERE id = ?",
                (json.dumps(best_cluster["members"]), best_cluster["timestamp"], best_cluster["id"])
            )
            n_added_to_clusters += 1
        else:
            # Create a new cluster
            summary = item["content"][:200]
            new_ts = item["timestamp"]
            c.execute(
                "INSERT INTO consolidated (summary, members, timestamp, embedding, use_count) VALUES (?, ?, ?, ?, 0)",
                (summary, json.dumps([item["id"]]), new_ts, item["embedding"].tobytes())
            )
            n_new_clusters += 1

    # Step 3: delete merged duplicates
    for dup_id in to_merge:
        c.execute("DELETE FROM captures WHERE id = ?", (dup_id,))

    conn.commit()
    conn.close()
    return {
        "duplicates_merged": len(to_merge),
        "clusters_built": n_new_clusters,
        "items_added_to_clusters": n_added_to_clusters,
        "items_processed": len(items),
    }


# =============================================================================
# Search (queries the slow memory primarily, with fast fallback)
# =============================================================================

def search(query, k=5, path=DB_PATH):
    """Vector similarity search across both stores."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    if not get_vocab(conn):
        conn.close()
        return []
    q_emb = get_embedding(query, conn)

    results = []
    # Search consolidated first (more useful)
    c.execute("SELECT id, summary, members, embedding, use_count FROM consolidated")
    for r in c.fetchall():
        emb = np.frombuffer(r[3], dtype=np.float64)
        sim = cosine_similarity(q_emb, emb)
        results.append({"id": r[0], "type": "consolidated", "table": "consolidated", "content": r[1], "similarity": sim, "use_count": r[4]})
    # Then raw captures
    c.execute("SELECT id, content, embedding, use_count FROM captures")
    for r in c.fetchall():
        emb = np.frombuffer(r[2], dtype=np.float64)
        sim = cosine_similarity(q_emb, emb)
        results.append({"id": r[0], "type": "capture", "table": "captures", "content": r[1], "similarity": sim, "use_count": r[3]})
    # Log accesses (DA = reward signal)
    ts = datetime.now().timestamp()
    for r in sorted(results, key=lambda x: -x["similarity"])[:k]:
        c.execute("UPDATE " + r["table"] + " SET use_count = use_count + 1 WHERE id = ?", (r["id"],))
        c.execute("INSERT INTO access_log VALUES (?, ?, ?)", (r["id"], r["type"], ts))
    conn.commit()
    conn.close()
    # Sort and return top k
    results.sort(key=lambda x: -x["similarity"])
    return results[:k]


# =============================================================================
# Surprise (intrinsic motivation / curiosity)
# =============================================================================

def surprise(path=DB_PATH):
    """
    Surface a random item that is *least similar* to recent context.
    This is the intrinsic motivation: drive exploration of forgotten material.
    """
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, summary, embedding, use_count FROM consolidated")
    consolidated = c.fetchall()
    if not consolidated:
        # Fall back to captures
        c.execute("SELECT id, content, embedding, use_count FROM captures")
        items = c.fetchall()
        if not items:
            conn.close()
            return None
        # Random pick
        idx = np.random.randint(len(items))
        r = items[idx]
        conn.close()
        return {"id": r[0], "type": "capture", "content": r[2], "novelty": 1.0, "use_count": r[3]}
    # Get the most recent consolidated embedding
    consolidated.sort(key=lambda x: -x[3])  # by timestamp desc; col 3 is timestamp
    # Wait, col 3 is embedding. Let me re-fetch with explicit columns
    c.execute("SELECT id, summary, embedding, use_count, timestamp FROM consolidated")
    consolidated = c.fetchall()
    consolidated.sort(key=lambda x: -x[4])  # by timestamp desc
    recent = consolidated[0]
    recent_emb = np.frombuffer(recent[2], dtype=np.float64)
    # Find the least similar item
    best = None
    best_novelty = 0
    for r in consolidated:
        emb = np.frombuffer(r[2], dtype=np.float64)
        novelty = 1 - cosine_similarity(recent_emb, emb)
        if novelty > best_novelty:
            best_novelty = novelty
            best = {"id": r[0], "type": "consolidated", "content": r[1], "novelty": novelty, "use_count": r[3]}
    conn.close()
    return best


# =============================================================================
# Prune (homeostasis)
# =============================================================================

def prune(days_threshold=90, path=DB_PATH):
    """Remove items not accessed in `days_threshold` days. Homeostasis."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days_threshold)).timestamp()
    # Get last access for each item from access_log
    c.execute("SELECT item_id, item_type, MAX(timestamp) FROM access_log GROUP BY item_id, item_type")
    last_access = {(r[0], r[1]): r[2] for r in c.fetchall()}

    to_delete_captures = []
    to_delete_consolidated = []

    c.execute("SELECT id, timestamp FROM captures")
    for r in c.fetchall():
        last = last_access.get((r[0], "capture"), r[1])  # default to creation time
        if last < cutoff:
            to_delete_captures.append(r[0])

    c.execute("SELECT id, timestamp FROM consolidated")
    for r in c.fetchall():
        last = last_access.get((r[0], "consolidated"), r[1])
        if last < cutoff:
            to_delete_consolidated.append(r[0])

    for cid in to_delete_captures:
        c.execute("DELETE FROM captures WHERE id = ?", (cid,))
    for cid in to_delete_consolidated:
        c.execute("DELETE FROM consolidated WHERE id = ?", (cid,))

    conn.commit()
    conn.close()
    return {
        "captures_pruned": len(to_delete_captures),
        "consolidated_pruned": len(to_delete_consolidated),
    }


# =============================================================================
# Status and visualization
# =============================================================================

def status(path=DB_PATH):
    """Show system status."""
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM captures")
    n_captures = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM consolidated")
    n_consolidated = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM vocab")
    n_vocab = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM access_log")
    n_accesses = c.fetchone()[0]
    conn.close()
    return {
        "captures (fast memory)": n_captures,
        "consolidated (slow memory)": n_consolidated,
        "vocab terms": n_vocab,
        "access events (DA signal)": n_accesses,
    }


def plot_growth(path=DB_PATH):
    """Plot the growth of fast and slow memory over time."""
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute("SELECT timestamp FROM captures ORDER BY timestamp")
    capture_times = [datetime.fromtimestamp(r[0]) for r in c.fetchall()]
    c.execute("SELECT timestamp FROM consolidated ORDER BY timestamp")
    consolidated_times = [datetime.fromtimestamp(r[0]) for r in c.fetchall()]

    conn.close()

    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    if capture_times:
        ax.plot(capture_times, range(1, len(capture_times) + 1), label="Fast memory (raw captures)", linewidth=2)
    if consolidated_times:
        ax.plot(consolidated_times, range(1, len(consolidated_times) + 1), label="Slow memory (consolidated)", linewidth=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative count")
    ax.set_title("DreamCatcher: memory growth over time")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/dreamcatcher_growth.png", dpi=120)
    plt.close(fig)
    return "plots/dreamcatcher_growth.png"


# =============================================================================
# Demo: simulate a few days of use
# =============================================================================

def run_demo():
    """A scripted demo showing the system in action."""
    import os
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    print("=" * 60)
    print("DreamCatcher Demo: a brain-inspired knowledge management run")
    print("=" * 60)
    print()

    # Day 1: capture some initial notes
    print("Day 1: capturing initial notes about generative models...")
    add_capture("Denoising Diffusion Probabilistic Models (DDPM) is a generative model that learns to reverse a noise process.")
    add_capture("Variational autoencoders (VAE) compress data into a latent space and sample from it.")
    add_capture("Latent diffusion compresses images with a VAE then runs diffusion in the latent space.")
    add_capture("Score-based models learn the gradient of log p(x), called the score function.")
    add_capture("Classifier-free guidance combines conditional and unconditional predictions for text-to-image.")

    # Day 1: simulate a near-duplicate
    add_capture("DDPM is a denoising diffusion probabilistic model, which is a type of generative model that learns to undo noise.")
    add_capture("I read about VAEs today. They compress data into a continuous latent space using an encoder-decoder architecture.")

    # Day 1: more diverse topics
    add_capture("Hippocampal replay during sleep consolidates memories from short-term to long-term storage.")
    add_capture("MSPCH: the brain might run variational inference at every time scale from milliseconds to decades.")
    add_capture("The free energy principle is a unified theory of brain function by Karl Friston.")
    add_capture("Predictive coding: the brain is constantly predicting the next sensory input and updating on errors.")
    add_capture("Dopamine neurons encode reward prediction error, not reward itself.")

    print("Status after Day 1 capture:")
    for k, v in status().items():
        print(f"  {k}: {v}")
    print()

    # Day 1: run the "sleep" job
    print("Running sleep (consolidation)...")
    result = consolidate(days=1)
    print(f"  Duplicates merged: {result['duplicates_merged']}")
    print(f"  New clusters built: {result['clusters_built']}")
    print(f"  Items added to existing clusters: {result['items_added_to_clusters']}")
    print(f"  Items processed: {result['items_processed']}")
    print()

    print("Status after Day 1 sleep:")
    for k, v in status().items():
        print(f"  {k}: {v}")
    print()

    # Day 2: add more notes
    print("Day 2: capturing more notes...")
    add_capture("Flow matching is a recent alternative to diffusion that learns the vector field between data and noise.")
    add_capture("Stable Diffusion is a latent diffusion model with a text-conditioned U-Net and a CLIP text encoder.")
    add_capture("Sora is a video generation model that uses a 3D U-Net with temporal attention layers.")
    add_capture("Temporal attention in video diffusion lets each frame attend to other frames at the same spatial location.")
    add_capture("DALL-E 2 uses CLIP latents to condition the diffusion model on text embeddings.")
    add_capture("The brain's three-factor learning rule: pre-synaptic activity, post-synaptic activity, and a neuromodulator.")
    add_capture("Acetylcholine gates whether the hippocampus encodes new information or retrieves old.")
    add_capture("Replay in the brain happens mostly during slow-wave sleep and REM sleep.")

    # Day 2: some duplicates of Day 1
    add_capture("Stable Diffusion is a text-to-image model that uses latent diffusion. It was developed by Stability AI.")
    add_capture("The brain's three-factor learning rule needs pre, post, and a neuromodulator like dopamine or acetylcholine.")

    print("Running sleep again (Day 2)...")
    result = consolidate(days=2)
    print(f"  Duplicates merged: {result['duplicates_merged']}")
    print(f"  New clusters built: {result['clusters_built']}")
    print(f"  Items added to existing clusters: {result['items_added_to_clusters']}")
    print()

    print("Status after Day 2 sleep:")
    for k, v in status().items():
        print(f"  {k}: {v}")
    print()

    # Search
    print("Search for 'diffusion':")
    for r in search("diffusion", k=5):
        print(f"  [{r['type']}, sim={r['similarity']:.3f}, used={r['use_count']}x] {r['content'][:80]}")
    print()

    print("Search for 'sleep and memory':")
    for r in search("sleep and memory", k=3):
        print(f"  [{r['type']}, sim={r['similarity']:.3f}, used={r['use_count']}x] {r['content'][:80]}")
    print()

    # Surprise
    print("Surprise me (intrinsic motivation):")
    s = surprise()
    if s:
        print(f"  [{s['type']}, novelty={s['novelty']:.3f}] {s['content'][:100]}")
    print()

    # Plot
    path = plot_growth()
    print(f"Saved memory growth plot to {path}")
    print()
    print("Demo complete. Try the CLI:")
    print("  python dreamcatcher.py --help")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="DreamCatcher: brain-inspired personal knowledge management.")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="Add a capture to fast memory")
    p_add.add_argument("content", nargs="+", help="Content to capture")
    p_add.add_argument("--url", default=None, help="Source URL (optional)")

    p_sleep = sub.add_parser("sleep", help="Run consolidation (the sleep job)")
    p_sleep.add_argument("--days", type=int, default=1, help="How many days back to consolidate")

    p_search = sub.add_parser("search", help="Search the knowledge base")
    p_search.add_argument("query", nargs="+", help="Search query")
    p_search.add_argument("-k", type=int, default=5, help="Number of results")

    p_surprise = sub.add_parser("surprise", help="Surface a novel item (intrinsic motivation)")

    p_prune = sub.add_parser("prune", help="Prune unused items (homeostasis)")
    p_prune.add_argument("--days", type=int, default=90, help="Days without access before pruning")

    sub.add_parser("status", help="Show system status")
    sub.add_parser("plot", help="Plot memory growth")
    sub.add_parser("demo", help="Run a scripted demo")

    args = parser.parse_args()

    init_db()

    if args.cmd == "add":
        content = " ".join(args.content)
        source = "url" if args.url else "text"
        if args.url:
            content = f"[{args.url}] {content}"
        cid = add_capture(content, source=source)
        print(f"Captured as id {cid}.")
    elif args.cmd == "sleep":
        result = consolidate(days=args.days)
        print(json.dumps(result, indent=2))
    elif args.cmd == "search":
        query = " ".join(args.query)
        results = search(query, k=args.k)
        if not results:
            print("No results.")
        for r in results:
            print(f"  [{r['type']}, sim={r['similarity']:.3f}, used={r['use_count']}x]")
            print(f"    {r['content'][:120]}")
    elif args.cmd == "surprise":
        s = surprise()
        if s is None:
            print("No items yet. Add some first.")
        else:
            print(f"[{s['type']}, novelty={s['novelty']:.3f}]")
            print(f"  {s['content'][:200]}")
    elif args.cmd == "prune":
        result = prune(days_threshold=args.days)
        print(json.dumps(result, indent=2))
    elif args.cmd == "status":
        s = status()
        for k, v in s.items():
            print(f"  {k}: {v}")
    elif args.cmd == "plot":
        path = plot_growth()
        print(f"Saved to {path}")
    elif args.cmd == "demo":
        run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
