"""
Phase 0: RAG Baseline — Corpus-based retrieval

Usage:
    pip install sentence-transformers numpy PyPDF2
    python scripts/build_rag_corpus.py        # extract text from PDF
    python scripts/rag_baseline.py --build-index  # build vector index
    python scripts/rag_baseline.py -q "question"  # retrieve
    python scripts/rag_baseline.py               # interactive mode
"""

import argparse
import json
import os
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("pip install sentence-transformers")
    exit(1)
try:
    import numpy as np
except ImportError:
    print("pip install numpy")
    exit(1)

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "data" / "rag_corpus"


def load_corpus():
    """Load all corpus text files as (section_id, text) pairs."""
    items = []
    for fpath in sorted(CORPUS_DIR.glob("*.txt")):
        items.append((fpath.stem, fpath.read_text(encoding="utf-8")))
    return items


def build_index(items, model_name="all-MiniLM-L6-v2"):
    """Build in-memory vector index from corpus items."""
    print(f"Loading model: {model_name} ...")
    model = SentenceTransformer(model_name)
    texts = [t for _, t in items]
    print(f"Encoding {len(texts)} chunks ...")
    embeddings = model.encode(texts, show_progress_bar=True)
    return model, np.array(embeddings)


def retrieve(question, model, embeddings, items, top_k=3):
    """Retrieve top-k sections for a question."""
    q_vec = model.encode([question])
    scores = np.dot(embeddings, q_vec.T).flatten()
    top_idx = np.argsort(scores)[-top_k:][::-1]
    results = []
    for idx in top_idx:
        section_id, text = items[idx]
        results.append({
            "section_id": section_id,
            "score": float(scores[idx]),
            "text": text[:1500],
        })
    return results


def format_context(results):
    """Format retrieved sections as a prompt context."""
    parts = []
    for r in results:
        parts.append(f"=== ACSM12 Section {r['section_id']} ===\n{r['text']}")
    return "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="RAG baseline for ACSM12")
    parser.add_argument("--question", "-q", type=str, help="Question to ask")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2")
    parser.add_argument("--build-index", action="store_true", help="Build and save index")
    args = parser.parse_args()

    items = load_corpus()

    if args.build_index:
        model, embeddings = build_index(items, args.model)
        out_dir = ROOT / "data"
        out_dir.mkdir(exist_ok=True)
        np.save(out_dir / "corpus_embeddings.npy", embeddings)
        with open(out_dir / "index_meta.json", "w") as f:
            json.dump({"model": args.model, "n_sections": len(items)}, f)
        print(f"Index saved to {out_dir / 'corpus_embeddings.npy'}")
        return

    # Load saved index or build on the fly
    index_path = ROOT / "data" / "corpus_embeddings.npy"
    if index_path.exists():
        embeddings = np.load(str(index_path))
        model = SentenceTransformer(args.model)
    else:
        model, embeddings = build_index(items, args.model)

    if not args.question:
        while True:
            try:
                q = input("\nQuestion: ").strip()
                if not q:
                    continue
            except (EOFError, KeyboardInterrupt):
                break
            results = retrieve(q, model, embeddings, items, args.top_k)
            print(f"\nTop {args.top_k} results:\n")
            for r in results:
                print(f"[{r['section_id']}] (score: {r['score']:.3f})")
                print(r["text"][:200] + "...")
                print()
    else:
        results = retrieve(args.question, model, embeddings, items, args.top_k)
        print(format_context(results))


if __name__ == "__main__":
    main()
