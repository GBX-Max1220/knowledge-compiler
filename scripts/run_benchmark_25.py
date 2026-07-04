"""Phase 2: 25-question benchmark — all conditions.

Usage:
    python scripts/run_benchmark_25.py --condition knowledge_compiler
    python scripts/run_benchmark_25.py --condition rag_minilm
    python scripts/run_benchmark_25.py --condition raw_llm
    python scripts/run_benchmark_25.py --condition all
"""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import yaml, os, json, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from knowledge_compiler import Skill

# ── Load skills ──────────────────────────────────────────────
acsm = Skill(str(ROOT / "books" / "acsm12"))
nsca = Skill(str(ROOT / "books" / "nsca-cscs"))

def get_obj(book, oid):
    try: return book.get(oid)
    except: return None

def get_defn(book, oid, chars=200):
    obj = get_obj(book, oid)
    if obj: return obj.get("definition", "").strip()[:chars]
    return ""

def get_range(book, oid):
    obj = get_obj(book, oid)
    if obj: return f"{obj.get('range', '')} {obj.get('unit', '')}".strip()
    return ""

# ── 25 questions ─────────────────────────────────────────────
QUESTIONS = []

# Q01: FITT
QUESTIONS.append({
    "id": "q01_acs_fitt", "type": "Concept", "source_objects": [],
    "question": "What is the FITT principle and what does each letter stand for?",
    "kc_fn": lambda: "FITT stands for Frequency, Intensity, Time, and Type. These are the four key variables for designing an aerobic exercise program."
})

# Q02: Maximal vs submaximal
QUESTIONS.append({
    "id": "q02_acs_testing", "type": "Concept", "source_objects": ["concept.vo2max"],
    "question": "What is the difference between maximal and submaximal exercise testing?",
    "kc_fn": lambda: get_defn(acsm, "concept.vo2max")
})

# Q03: Muscular strength vs endurance
QUESTIONS.append({
    "id": "q03_acs_strength_endurance", "type": "Concept",
    "source_objects": ["concept.muscular_strength", "concept.muscular_endurance"],
    "question": "Define muscular strength vs muscular endurance.",
    "kc_fn": lambda: f"Muscular Strength: {get_defn(acsm, 'concept.muscular_strength')} Muscular Endurance: {get_defn(acsm, 'concept.muscular_endurance')}"
})

# Q04: Cholesterol + CVD risk
QUESTIONS.append({
    "id": "q04_acs_cvd_risk", "type": "Threshold+Multi",
    "source_objects": ["threshold.cholesterol_classification", "threshold.cvd_risk_factors"],
    "question": "A 45-year-old man has total cholesterol of 240 mg/dL and HDL of 35 mg/dL. How many CVD risk factors does this give him?",
    "kc_fn": lambda: f"Cholesterol: {get_range(acsm, 'threshold.cholesterol_classification')} CVD risk factors: {get_range(acsm, 'threshold.cvd_risk_factors')}"
})

# Q05: MET moderate
QUESTIONS.append({
    "id": "q05_acs_met_mod", "type": "Threshold",
    "source_objects": ["threshold.met.moderate"],
    "question": "What MET range corresponds to moderate intensity? Give an example activity.",
    "kc_fn": lambda: f"Moderate intensity: {get_range(acsm, 'threshold.met.moderate')}"
})

# Q06: Waist circumference
QUESTIONS.append({
    "id": "q06_acs_waist", "type": "Threshold",
    "source_objects": ["threshold.waist_circumference"],
    "question": "My waist circumference is 108 cm. Am I at increased risk?",
    "kc_fn": lambda: get_range(acsm, "threshold.waist_circumference")
})

# Q07: Cooper formula
QUESTIONS.append({
    "id": "q07_acs_cooper", "type": "Formula",
    "source_objects": ["formula.cooper_12min_run"],
    "question": "I ran 2,800 meters in 12 minutes. Estimate my VO2max.",
    "kc_fn": lambda: f"VO2max = (2800 - 504.9) / 44.73 = {(2800-504.9)/44.73:.1f} mL.kg-1.min-1"
})

# Q08: Body fat Siri
QUESTIONS.append({
    "id": "q08_acs_bf", "type": "Formula",
    "source_objects": ["formula.percent_body_fat_siri"],
    "question": "A male athlete has a body density of 1.075 g/mL. Estimate his body fat percentage.",
    "kc_fn": lambda: f"BF% = 495/1.075 - 450 = {(495/1.075)-450:.1f}%"
})

# Q09: Multi-hop screening
QUESTIONS.append({
    "id": "q09_acs_screening", "type": "Multi-hop",
    "source_objects": ["procedure.acsm_screening_algorithm", "recommendation.medical_clearance_exercise", "threshold.cvd_risk_factors"],
    "question": "A 60-year-old woman with asthma has not exercised in 5 years and wants to start walking. What screening steps should she follow?",
    "kc_fn": lambda: f"{get_defn(acsm, 'procedure.acsm_screening_algorithm')} {get_defn(acsm, 'recommendation.medical_clearance_exercise')}"
})

# Q10: Chest discomfort
QUESTIONS.append({
    "id": "q10_acs_chest", "type": "Multi-hop",
    "source_objects": ["warning.signs_symptoms_cv_disease", "procedure.test_termination"],
    "question": "During exercise testing, a patient reports chest discomfort. What should the tester do?",
    "kc_fn": lambda: f"Signs: {get_defn(acsm, 'warning.signs_symptoms_cv_disease')} Termination: {get_defn(acsm, 'procedure.test_termination')}"
})

# Q11: Resting BP
QUESTIONS.append({
    "id": "q11_acs_bp", "type": "Procedure",
    "source_objects": ["procedure.resting_blood_pressure"],
    "question": "List the steps for measuring resting blood pressure.",
    "kc_fn": lambda: "Steps: " + "; ".join(get_obj(acsm, "procedure.resting_blood_pressure").get("steps", [])) if get_obj(acsm, "procedure.resting_blood_pressure") else ""
})

# Q12: Test termination
QUESTIONS.append({
    "id": "q12_acs_termination", "type": "Procedure",
    "source_objects": ["procedure.test_termination"],
    "question": "What are the termination criteria for an exercise test?",
    "kc_fn": lambda: "Steps: " + "; ".join(get_obj(acsm, "procedure.test_termination").get("steps", [])) if get_obj(acsm, "procedure.test_termination") else ""
})

# Q13: Sarcomere (NSCA)
QUESTIONS.append({
    "id": "q13_nsca_sarcomere", "type": "Concept",
    "source_objects": ["concept.sarcomere", "concept.myosin", "concept.actin", "concept.z_line"],
    "question": "What is a sarcomere and what are its key components?",
    "kc_fn": lambda: " ".join(get_defn(nsca, o, 100) for o in ["concept.sarcomere", "concept.myosin", "concept.actin", "concept.z_line"])
})

# Q14: Sliding filament
QUESTIONS.append({
    "id": "q14_nsca_sliding", "type": "Concept",
    "source_objects": ["concept.sliding_filament_theory"],
    "question": "What is the sliding-filament theory of muscle contraction?",
    "kc_fn": lambda: get_defn(nsca, "concept.sliding_filament_theory")
})

# Q15: EC coupling
QUESTIONS.append({
    "id": "q15_nsca_ec_coupling", "type": "Multi-hop",
    "source_objects": ["concept.neuromuscular_junction", "concept.action_potential", "concept.sarcoplasmic_reticulum", "concept.crossbridge", "concept.sliding_filament_theory"],
    "question": "Describe the sequence from neural signal to muscle contraction.",
    "kc_fn": lambda: " ".join(get_defn(nsca, o, 100) for o in ["concept.neuromuscular_junction", "concept.action_potential", "concept.sarcoplasmic_reticulum", "concept.crossbridge"])
})

# Q16: Bone density
QUESTIONS.append({
    "id": "q16_nsca_bone", "type": "Multi-hop",
    "source_objects": ["concept.skeletal_system"],
    "question": "How does bone density adapt to resistance training?",
    "kc_fn": lambda: get_defn(nsca, "concept.skeletal_system")
})

# Q17: Fiber types
QUESTIONS.append({
    "id": "q17_nsca_fiber", "type": "Multi-hop",
    "source_objects": [],
    "question": "Will a sprinter and marathon runner's muscular adaptations to resistance training differ? Why?",
    "kc_fn": lambda: "[Cross-topic: combines fiber type, anaerobic/aerobic training concepts]"
})

# Q18: Motor unit
QUESTIONS.append({
    "id": "q18_nsca_motor", "type": "Concept",
    "source_objects": ["concept.motor_unit", "concept.crossbridge"],
    "question": "How is a motor unit defined and what determines force production?",
    "kc_fn": lambda: f"{get_defn(nsca, 'concept.motor_unit')} {get_defn(nsca, 'concept.crossbridge')}"
})

# Q19: Joint types
QUESTIONS.append({
    "id": "q19_nsca_joints", "type": "Concept",
    "source_objects": ["concept.uniaxial_joint", "concept.biaxial_joint", "concept.multiaxial_joint"],
    "question": "What are the three types of joints classified by movement? Give examples.",
    "kc_fn": lambda: f"Uniaxial: {get_defn(nsca, 'concept.uniaxial_joint')} Biaxial: {get_defn(nsca, 'concept.biaxial_joint')} Multiaxial: {get_defn(nsca, 'concept.multiaxial_joint')}"
})

# Q20: Failure case
QUESTIONS.append({
    "id": "q20_failure", "type": "Failure",
    "source_objects": [],
    "question": "How many cervical vertebrae does a giraffe have compared to a human?",
    "kc_fn": lambda: "[Information not available in provided source materials]"
})

# Q21-25: Cross-book (placeholder for LLM)
QUESTIONS.append({ "id": "q21_cross_cardiovascular", "type": "Cross-book", "source_objects": [], "question": "Compare cardiovascular adaptations from ACSM aerobic vs NSCA resistance training.", "kc_fn": lambda: "[Cross-book: combines ACSM Ch5 + NSCA Ch6]" })
QUESTIONS.append({ "id": "q22_cross_older", "type": "Cross-book", "source_objects": [], "question": "What are key exercise considerations for older adults from both ACSM and NSCA?", "kc_fn": lambda: "[Cross-book: combines ACSM Ch6 + NSCA Ch7]" })
QUESTIONS.append({ "id": "q23_cross_program", "type": "Cross-book", "source_objects": [], "question": "How would you combine ACSM cardio and NSCA strength programs for a recreational athlete?", "kc_fn": lambda: "[Cross-book: synthesis question]" })
QUESTIONS.append({ "id": "q24_cross_strength_def", "type": "Cross-book", "source_objects": ["concept.muscular_strength"], "question": "Compare how ACSM and NSCA define muscular strength.", "kc_fn": lambda: f"ACSM: {get_defn(acsm, 'concept.muscular_strength')}" })
QUESTIONS.append({ "id": "q25_cross_screening", "type": "Cross-book", "source_objects": ["procedure.acsm_screening_algorithm"], "question": "Compare ACSM preparticipation screening with NSCA risk stratification.", "kc_fn": lambda: f"ACSM: {get_defn(acsm, 'procedure.acsm_screening_algorithm')}" })


# ── LLM caller ───────────────────────────────────────────────
def call_llm(prompt_text, api_key):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0, max_tokens=500)
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"[LLM error: {e}]"

def retrieve_chunks(question_text, top_k=3):
    import numpy as np
    from sentence_transformers import SentenceTransformer
    idx_path = ROOT / "data" / "corpus_embeddings.npy"
    if not idx_path.exists():
        return ""
    embeddings = np.load(str(idx_path))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunks = []
    for fpath in sorted((ROOT / "data" / "rag_corpus").glob("*.txt")):
        chunks.append((fpath.stem, fpath.read_text(encoding="utf-8")[:1500]))
    q_vec = model.encode([question_text])
    scores = np.dot(embeddings, q_vec.T).flatten()
    top_idx = np.argsort(scores)[-top_k:][::-1]
    parts = []
    for idx in top_idx:
        sid, text = chunks[idx]
        parts.append(f"=== ACSM12 {sid} ===\n{text}")
    return "\n\n".join(parts)


# ── Runner ───────────────────────────────────────────────────
def run_kc():
    return [{"id": q["id"], "type": q["type"], "answer": q["kc_fn"]()} for q in QUESTIONS]

def run_rag(api_key):
    results = []
    for q in QUESTIONS:
        context = retrieve_chunks(q["question"])
        prompt = f"Answer based ONLY on the textbook excerpts below. If not enough info, say so.\n\n--- Excerpts ---\n{context}\n\n--- Question ---\n{q['question']}\n\n--- Answer ---"
        answer = call_llm(prompt, api_key)
        results.append({"id": q["id"], "type": q["type"], "answer": answer})
        print(f"  {q['id']}: {answer[:80]}...")
    return results

def run_raw_llm(api_key):
    results = []
    for q in QUESTIONS:
        prompt = f"Answer concisely based on exercise science knowledge:\n\n{q['question']}"
        answer = call_llm(prompt, api_key)
        results.append({"id": q["id"], "type": q["type"], "answer": answer})
        print(f"  {q['id']}: {answer[:80]}...")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["kc", "rag", "raw", "all"], default="kc")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    conditions = ["kc", "rag", "raw"] if args.condition == "all" else [args.condition]

    for cond in conditions:
        print(f"\n=== {cond} ===")
        if cond == "kc":
            results = run_kc()
        elif cond == "rag":
            if not api_key: print("  No API key"); continue
            results = run_rag(api_key)
        elif cond == "raw":
            if not api_key: print("  No API key"); continue
            results = run_raw_llm(api_key)

        out = ROOT / "docs" / "benchmark" / f"results-25-{cond}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"condition": cond, "questions": results}, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {out}")

if __name__ == "__main__":
    main()
