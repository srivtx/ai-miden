## Why it exists (THE PROBLEM)

Your model needs data. You have data in 5 places: S3 bucket, PostgreSQL database, Kafka stream, CSV files, and an API you call. The data is messy: missing values, wrong types, duplicates. You need to combine, clean, transform, and feed it to training. Every day. Automatically. With retries when something fails. Without you SSH-ing in at 3 AM.

**Data pipelines** automate the flow: extract → validate → transform → load → train. The pipeline runs on a schedule (daily/hourly), handles failures (retry × 3, then alert), and maintains lineage (which model was trained on which data?).

For ML specifically, the pipeline includes:
- Feature computation (not just CSV columns — embeddings, rolling statistics, ratios)
- Train/val/test splits (stratified, temporal, or random, based on the problem)
- Data versioning (which snapshot of data produced model v3?)

## Definition (very simple)

A **data pipeline** is a DAG (directed acyclic graph) of tasks. Each task is one operation: extract CSV → validate schema → compute features → split → train → evaluate. The scheduler (Airflow/Prefect/Dagster) runs the DAG on a schedule, handling dependencies (B starts when A finishes) and retries (if B fails, retry 3 times with 5-minute backoff).

**Key patterns:**
- **Extract:** read from source (S3, DB, API, Kafka), cache locally (Parquet for tabular, TFRecords for images, Arrow for streaming)
- **Validate:** check schema (column types, non-null constraints), check distributions (drift from last snapshot), flag anomalies
- **Transform:** compute features, normalize, encode categoricals, tokenize text
- **Version:** snapshot the transformed data with a unique ID (DVC, Delta Lake time travel)
- **Load:** feed to training dataloader, with data augmentation applied on-the-fly

## Practice: Minimal data pipeline for cortexcode

```python
import dvc.api
import hashlib
import json
from pathlib import Path
from datetime import datetime


def pipeline_step_extract(sources):
    """Extract code from multiple repos, deduplicate, write to staging."""
    texts = []
    for source in sources:
        if source.startswith("git@"):
            # Clone repo, walk .py files
            import subprocess, tempfile
            tmp = tempfile.mkdtemp()
            subprocess.run(["git", "clone", "--depth", "1", source, tmp])
            for path in Path(tmp).rglob("*.py"):
                texts.append(path.read_text(errors="ignore"))
        elif source.endswith(".csv") or source.endswith(".jsonl"):
            texts.extend(open(source).readlines())
        elif source.startswith("s3://"):
            # Use boto3 for S3
            pass
    return texts


def pipeline_step_validate(texts):
    """Validate code snippets: min length, valid UTF-8, not empty."""
    valid = []
    for t in texts:
        if len(t) > 50 and len(t) < 20000:
            try:
                t.encode("utf-8")
                valid.append(t)
            except UnicodeError:
                continue
    return valid


def pipeline_step_version(texts, storage_dir="/data/versions"):
    """Version the dataset with a content hash."""
    content = "\n---FILE---\n".join(texts)
    data_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
    version_path = Path(storage_dir) / f"codebase_{data_hash}"
    version_path.mkdir(parents=True, exist_ok=True)
    (version_path / "data.txt").write_text(content)
    (version_path / "metadata.json").write_text(json.dumps({
        "hash": data_hash,
        "num_files": len(texts),
        "total_chars": sum(len(t) for t in texts),
        "created_at": datetime.now().isoformat(),
    }))
    return str(version_path), data_hash


def run_pipeline_daily():
    """Daily data refresh pipeline."""
    sources = ["git@github.com:Textualize/rich.git",
               "git@github.com:kellyjonbrazil/jc.git",
               "s3://my-bucket/private-code/"]

    print("[1/4] Extract...")
    texts = pipeline_step_extract(sources)
    print(f"  Extracted {len(texts)} files")

    print("[2/4] Validate...")
    valid = pipeline_step_validate(texts)
    print(f"  Valid: {len(valid)} (removed {len(texts) - len(valid)})")

    print("[3/4] Version...")
    path, hash_id = pipeline_step_version(valid)
    print(f"  Version: {hash_id} at {path}")

    print("[4/4] Train...")
    subprocess.run(["python", "train.py", "--data-dir", path])

    print(f"Pipeline complete. Model trained on dataset {hash_id}")
```

Run this daily: `python pipeline.py`. Every run produces a versioned dataset + trained model. Six months later, you can trace "model v37 was trained on dataset `a3f8b2c1d4e5` which had 1,234 files from rich v2.3.1 + jc v1.25.0." Full lineage.

## Key properties

| Property | Manual data prep | Automated pipeline |
|---|---|---|
| Freshness | When you remember | On schedule (daily/hourly) |
| Reproducibility | "Which data was this?" | Content-hash versioned |
| Lineage | None | Dataset hash → model version |
| Failure handling | Manual retry | Automatic retry + alert |
| Data drift detection | None | Compare distributions across runs |

## Tech comparison

| Tool | Best for | Notes |
|---|---|---|
| **Airflow** | ETL, batch pipelines, scheduling | Mature, Python DAGs, hard to debug |
| **Prefect** | Modern data pipelines | Python-native, easy local testing |
| **Dagster** | ML data pipelines | Asset-based (every step is versioned) |
| **DVC** | Data versioning (Git for data) | `dvc add data.csv && dvc push` |
| **Delta Lake** | Data lake with time travel | Rollback to any snapshot |
| **Spark** | Large-scale (TB+) data processing | Overkill for < 100GB |
| **Great Expectations** | Data validation | Schema + distribution checks |

## Common confusion

1. **"I only train once a month — do I need a pipeline?"** The LOWER the frequency, the MORE you need automation, because you'll forget the steps between runs. A pipeline ensures you don't skip validation or versioning just because "last time it worked fine."

2. **"Airflow vs Prefect?"** Airflow is for orchestrating external systems (Spark, Snowflake, APIs). Prefect is for orchestrating Python functions (your code). For ML: Prefect or Dagster. For data warehouse ETL: Airflow.

3. **"DVC vs. data versioning?"** DVC version-controls the data FILES (like Git LFS). Content hashing versions the data STATE (like a snapshot). Use both: DVC for the raw data, content hash for the processed feature set.

## Connection to cortexcode

Replace the manual `git clone` + `python train.py` flow with the pipeline above. Run it daily. Every dataset is versioned. Every model is traceable to its dataset. Six months of experiments become a queryable lineage graph instead of a mess of `.pt` files.
