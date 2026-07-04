"""
Phase 0: Full Benchmark Runner

Evaluates all questions across 3 conditions:
  - knowledge_compiler: local only, no API needed
  - rag_minilm: retrieves chunks + calls LLM
  - raw_llm: calls LLM directly (no context)

Usage:
    python scripts/run_benchmark.py --condition knowledge_compiler
    python scripts/run_benchmark.py --condition rag_minilm --api-key sk-xxx
    python scripts/run_benchmark.py --condition raw_llm --api-key sk-xxx
    python scripts/run_benchmark.py --condition all --api-key sk-xxx
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from knowledge_compiler import Skill


# ── Questions ──────────────────────────────────────────────────

QUESTIONS = [
    {
        "id": "q01",
        "question": "What's the difference between physical activity and exercise?",
        "expected_answer": "Exercise is a subset of physical activity — it is planned, structured, and repetitive. Physical activity is any bodily movement produced by skeletal muscles that results in energy expenditure.",
        "source_objects": ["concept.physical_activity", "concept.exercise"],
        "type": "Concept",
    },
    {
        "id": "q02",
        "question": "What does MET measure and what is 1 MET equivalent to?",
        "expected_answer": "MET (Metabolic Equivalent) measures the energy cost of physical activities. 1 MET is the energy expended at rest, approximately 3.5 mL.kg-1.min-1 of oxygen consumption.",
        "source_objects": ["concept.met", "threshold.sedentary_met"],
        "type": "Concept",
    },
    {
        "id": "q03",
        "question": "How do cardiorespiratory endurance and muscular fitness differ?",
        "expected_answer": "Cardiorespiratory endurance is the ability of the circulatory and respiratory systems to supply oxygen during sustained physical activity. Muscular fitness refers to the ability of muscles to generate force (strength) and sustain repeated contractions (endurance).",
        "source_objects": ["concept.cardiorespiratory_endurance", "concept.muscular_strength", "concept.muscular_endurance"],
        "type": "Concept",
    },
    {
        "id": "q04",
        "question": "I weigh 85kg and my height is 1.77m. My BMI is about 27 — what category does this fall into?",
        "expected_answer": "BMI 27 falls into the Overweight category (25.0-29.9). It is also classified as a CVD risk factor threshold (BMI >= 25.0).",
        "source_objects": ["threshold.bmi_classification", "threshold.cvd_risk_factors"],
        "type": "Threshold",
    },
    {
        "id": "q05",
        "question": "A patient's resting blood pressure is 145/95 mmHg. How is this classified?",
        "expected_answer": "This is classified as hypertension (BP >=130/80). It counts as one CVD risk factor.",
        "source_objects": ["threshold.blood_pressure_classification", "threshold.cvd_risk_factors"],
        "type": "Threshold",
    },
    {
        "id": "q06",
        "question": "Walking at 3 METs, jogging at 6 METs, and running at 9 METs. What intensity categories do these fall into?",
        "expected_answer": "Moderate intensity is 3.0-5.9 METs. Vigorous is >=6.0 METs. So 3 METs = moderate, 6 and 9 METs = vigorous.",
        "source_objects": ["threshold.met.light", "threshold.met.moderate", "threshold.met.vigorous"],
        "type": "Threshold",
    },
    {
        "id": "q07",
        "question": "A 55-year-old man with hypertension has not exercised regularly in years and wants to start jogging. What steps should he take before beginning?",
        "expected_answer": "He has CVD risk factors (age >=45, hypertension). As a currently inactive person with 2+ risk factors wanting vigorous exercise, the screening algorithm recommends medical clearance before starting.",
        "source_objects": ["procedure.acsm_screening_algorithm", "recommendation.medical_clearance_exercise"],
        "type": "Procedure",
    },
    {
        "id": "q08",
        "question": "How do you safely measure someones maximum strength in a gym setting?",
        "expected_answer": "Familiarization, warm up, start at ~50-70% of perceived capacity, attempt with proper form, rest 3-5 min, increase weight, stop at failure, record last successful weight. Complete within 4 trials.",
        "source_objects": ["procedure.one_rm_testing"],
        "type": "Procedure",
    },
    {
        "id": "q09",
        "question": "What physical symptoms during exercise should prompt someone to stop and seek medical evaluation?",
        "expected_answer": "Pain or discomfort in chest/neck/jaw/arms, shortness of breath, dizziness or syncope, palpitations, leg pain, unusual fatigue, swelling.",
        "source_objects": ["warning.signs_symptoms_cv_disease"],
        "type": "Warning",
    },
    {
        "id": "q10",
        "question": "How common are serious cardiac events during physical activity?",
        "expected_answer": "SCD occurs every 1.5 million episodes of vigorous PA in men and every 36.5 million episodes of MVPA in women. Habitual PA reduces overall risk.",
        "source_objects": ["evidence.absolute_scd_risk_vigorous_pa", "warning.scd_ami_vigorous_pa"],
        "type": "Warning",
    },
]


# ── LLM Caller ────────────────────────────────────────────────

def call_llm(prompt, api_key, model="deepseek-chat", endpoint="https://api.deepseek.com"):
    """Call an OpenAI-compatible API (DeepSeek, OpenRouter, etc.)"""
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: pip install openai")
        return ""

    client = OpenAI(api_key=api_key, base_url=endpoint)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"  LLM error: {e}")
        return ""


# ── RAG Engine ────────────────────────────────────────────────

def load_rag_index():
    """Load corpus embeddings and model."""
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: pip install sentence-transformers numpy")
        return None, None, []

    index_path = ROOT / "data" / "corpus_embeddings.npy"
    if not index_path.exists():
        print(f"Index not found. Run: python scripts/rag_baseline.py --build-index")
        return None, None, []

    embeddings = np.load(str(index_path))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunks = []
    for fpath in sorted((ROOT / "data" / "rag_corpus").glob("*.txt")):
        chunks.append((fpath.stem, fpath.read_text(encoding="utf-8")))
    return model, embeddings, chunks


def retrieve_chunks(question, model, embeddings, chunks, top_k=3):
    """Retrieve top-k chunks."""
    import numpy as np
    q_vec = model.encode([question])
    scores = np.dot(embeddings, q_vec.T).flatten()
    top_idx = np.argsort(scores)[-top_k:][::-1]
    results = []
    for idx in top_idx:
        sid, text = chunks[idx]
        results.append({"section_id": sid, "text": text[:1500]})
    return results


def build_rag_prompt(question, chunks):
    """Build a prompt with retrieved context."""
    context = "\n\n".join(
        f"=== ACSM12 Section {c['section_id']} ===\n{c['text']}" for c in chunks
    )
    return (
        "Answer the question based ONLY on the textbook excerpts below. "
        "If the excerpts do not contain enough information, say so.\n\n"
        f"--- Textbook Excerpts ---\n{context}\n\n"
        f"--- Question ---\n{question}\n\n"
        f"--- Answer ---"
    )


# ── Answering Engines ─────────────────────────────────────────

def answer_with_kc(skill, question_data):
    """Answer using Knowledge Compiler object lookups."""
    answers = []
    for oid in question_data["source_objects"]:
        try:
            answers.append(skill.get(oid))
        except Exception:
            pass

    parts = []
    for obj in answers:
        if "definition" in obj and obj["definition"]:
            parts.append(obj["definition"].strip().rstrip("."))
        if "signs" in obj:
            parts.append("Signs: " + "; ".join(obj["signs"][:3]))
        if "action" in obj:
            parts.append("Action: " + obj["action"])
        if "steps" in obj:
            parts.append("Steps: " + "; ".join(obj["steps"][:3]))
        if "range" in obj:
            parts.append(f"Range: {obj['range']} {obj.get('unit', '')}")
        if "dosage" in obj:
            parts.append(obj["dosage"].strip().rstrip("."))
    return " ".join(parts) if parts else ""


def answer_with_rag(question_data, api_key, model, endpoint, rag_state):
    """Answer via RAG: retrieve chunks + LLM."""
    model_emb, embeddings, chunks = rag_state
    if model_emb is None:
        return "[RAG index not available]"
    retrieved = retrieve_chunks(question_data["question"], model_emb, embeddings, chunks)
    prompt = build_rag_prompt(question_data["question"], retrieved)
    return call_llm(prompt, api_key, model, endpoint)


def answer_with_raw_llm(question_data, api_key, model, endpoint):
    """Answer via raw LLM (no context)."""
    prompt = f"Answer concisely based on standard exercise science knowledge:\n\n{question_data['question']}"
    return call_llm(prompt, api_key, model, endpoint)


# ── Evaluation ─────────────────────────────────────────────────

def evaluate_condition(condition, api_key, model, endpoint, skill=None, rag_state=None):
    results = []
    for q in QUESTIONS:
        if condition == "knowledge_compiler":
            answer = answer_with_kc(skill, q)
        elif condition == "rag_minilm":
            answer = answer_with_rag(q, api_key, model, endpoint, rag_state)
        elif condition == "raw_llm":
            answer = answer_with_raw_llm(q, api_key, model, endpoint)
        else:
            answer = ""

        results.append({
            "id": q["id"],
            "question": q["question"],
            "expected_answer": q["expected_answer"],
            "actual_answer": answer.strip() if answer else "",
            "type": q["type"],
            "accuracy": None,
            "citation_correctness": None,
            "faithfulness": None,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Phase 0 Benchmark Runner")
    parser.add_argument("--condition", choices=["knowledge_compiler", "rag_minilm", "raw_llm", "all"],
                        default="knowledge_compiler")
    parser.add_argument("--api-key", type=str, default=None,
                        help="API key (or set DEEPSEEK_API_KEY / OPENAI_API_KEY env)")
    parser.add_argument("--model", type=str, default="deepseek-chat",
                        help="Model name (default: deepseek-chat)")
    parser.add_argument("--endpoint", type=str, default="https://api.deepseek.com",
                        help="API endpoint (default: https://api.deepseek.com)")
    args = parser.parse_args()

    # Resolve API key: CLI arg > DEEPSEEK_API_KEY > OPENAI_API_KEY
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    conditions = ["knowledge_compiler", "rag_minilm", "raw_llm"] if args.condition == "all" else [args.condition]
    needs_api = any(c in ("rag_minilm", "raw_llm") for c in conditions)

    if needs_api and not api_key:
        print("Error: API key required for rag_minilm / raw_llm.")
        print("Set DEEPSEEK_API_KEY env var or pass --api-key")
        return

    # Pre-load shared resources
    skill = None
    rag_state = None
    if "knowledge_compiler" in conditions:
        skill = Skill(str(ROOT / "books" / "acsm12"))
        print(f"KC loaded: {len(skill.list_objects())} objects")
    if "rag_minilm" in conditions:
        rag_state = load_rag_index()
        if rag_state[0] is None:
            print("Warning: RAG index not found, skipping rag_minilm")
            conditions = [c for c in conditions if c != "rag_minilm"]

    for cond in conditions:
        print(f"\n=== Condition: {cond} ===")
        results = evaluate_condition(cond, api_key, args.model, args.endpoint, skill, rag_state)

        output_dir = ROOT / "docs" / "benchmark"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"results-{cond}.json")

        answered = [r for r in results if r["actual_answer"] and not r["actual_answer"].startswith("[")]
        summary = {
            "condition": cond,
            "model": args.model if cond != "knowledge_compiler" else "deterministic",
            "total_questions": len(results),
            "answered_count": len(answered),
            "accuracy": None,
            "citation_correctness": None,
            "faithfulness": None,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"questions": results, "summary": summary}, f, indent=2, ensure_ascii=False)

        print(f"  Questions: {len(results)}, Generated: {len(answered)}")
        print(f"  Output: {output_path}")
        for r in results:
            ans = r["actual_answer"][:100] + "..." if len(r["actual_answer"]) > 100 else r["actual_answer"]
            print(f"\n  {r['id']} [{r['type']}]: {ans}")


if __name__ == "__main__":
    main()
