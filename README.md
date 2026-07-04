# Knowledge Compiler

**Compile expert textbooks into typed, validated, machine-readable knowledge objects that power deterministic AI Skills.**

```
PDF → Compiler → Objects → Registry → Skill → Agent → Evaluation
```

Most AI systems that use textbooks do one of two things:
- **RAG** — retrieve chunks of raw text. Fast but unstructured. No guarantees on what the model will find.
- **Fine-tuning** — expensive, opaque, hard to update.

This is a third path: **compile textbooks into typed, validated, machine-readable knowledge objects** that an agent can query directly.

> **Example source:** ACSM's *Guidelines for Exercise Testing and Prescription*, 12th Ed. (Chapters 1–3)

---

## What can it do right now?

Ask it anything from the textbook:

```
Q: "Can a 55-year-old man with hypertension begin vigorous exercise?"

The system loads:
  → threshold.cvd_risk_factors    (age ≥45 = risk factor, BP ≥130/80 = risk factor)
  → procedure.acsm_screening      (non-exerciser + 2+ risk factors + vigorous = clearance needed)
  → recommendation.medical_clearance

Answer: Medical clearance is recommended before starting vigorous exercise.
Sources: ACSM12 Ch2.2.11 (p.150), Ch2.2.7 (p.142)
```

Not a chunk. Not a guess. **A typed decision chain with page-level citations.**

---

## Quick demo

```python
from knowledge_compiler import Skill

skill = Skill("books/acsm12")

# Safety check — what signs suggest I should see a doctor?
warnings = skill.get("warning.signs_symptoms_cv_disease")
# →
# {
#   "type": "Warning",
#   "signs": [
#     "Pain or discomfort in chest/neck/jaw/arms",
#     "Shortness of breath at rest or mild exertion",
#     "Dizziness or syncope",
#     ...
#   ],
#   "action": "Seek medical evaluation before initiating exercise",
#   "severity": "high",
#   "source": "ACSM12 Ch2.4 (p.133)"
# }

# Threshold check
bmi = skill.get("threshold.bmi_classification")
# → BMI 27 → "Overweight (25.0-29.9)"

# Procedure lookup
protocol = skill.get("procedure.one_rm_testing")
# → 8 steps, from warm-up to failure
```

Every query returns an **object** — typed, sourced, validated — not generated text.

---

## Coverage (v0.1)

```
74 Objects · 23 Edges · 6 Types · 5 Validation Layers ✅
```

| Type | Count | What it covers |
|------|-------|---------------|
| Concept | 38 | PA, Exercise, MET, VO₂max, fitness components, sedentary behavior, CVD risk factors |
| Threshold | 11 | MET intensity, BMI, BP, cholesterol, waist circumference, body fat % |
| Procedure | 9 | Screening algorithm, BP measurement, 1-RM testing, YMCA protocol, test termination |
| Recommendation | 8 | PA guidelines, medical clearance, screening for young athletes, cardiac prevention |
| Warning | 5 | CV signs/symptoms, cardiac prodromal symptoms, SCD/AMI risk, MSI risk |
| Formula | 3 | Cooper 12-min run, body density (Jackson-Pollock), % body fat (Siri) |
| **Total** | **74** | **ACSM 12th Ed., Chapters 1–3** |

> **Scope note:** v0.1 is validated on ACSM 12th Ed., Chapters 1–3. The ontology and pipeline are designed to be domain-agnostic, but cross-domain generalization (e.g., chemistry, law) has not yet been tested.

---

## How it's different

| | RAG | Fine-tuning | RAG + Knowledge Compiler |
|---|---|---|---|
| Source-grounded | ✅ Sometimes | ❌ | ✅ Always (page-level) |
| Typed output | ❌ | ❌ | ✅ Concept / Threshold / Procedure / ... |
| Machine-readable | ❌ | ❌ | ✅ `numerical_value`, `steps[]`, `signs[]` |
| Composable | ❌ | ❌ | ✅ Object → Agent → Workflow |
| Validation | ❌ | ❌ | ✅ 5-layer automated |
| Update cost | Low | High | Low (re-run one section) |
| Agent integration | Probabilistic | Opaque | Deterministic |

Knowledge Compiler is a **complement to RAG, not a replacement**. The typed objects it produces can be indexed by a vector store and retrieved alongside raw chunks — giving agents both structured facts and full-context passages.

---

## Validation

Every object passes 5 layers. Validation is **deterministic and fully automated** — no LLM judges, no probabilistic scoring.

1. **Syntax** — YAML parses, required fields exist
2. **Schema** — type-specific fields complete (Threshold has `range`, Procedure has `steps`)
3. **Ontology** — all relationship targets resolve, predicates are in allowlist
4. **Graph** — no duplicate IDs, no orphan edges
5. **Semantic** — definitions are non-empty, thresholds have numerical bounds

**Current status: ✅ ALL 5 LAYERS PASS**

---

## Repository structure

```
knowledge-compiler/
├── ontology_spec.md          # Language spec for the compiler
├── schema/                   # Type definitions (8 files)
├── prompts/                  # Pipeline prompts (6 files)
├── scripts/                  # Automation
├── compiler/                 # CLI + task queue + provider abstraction
├── books/acsm12/
│   ├── objects/              # 74 validated objects ← core asset
│   ├── skill/                # Agent skill definition + evaluation set
│   ├── registry.yaml         # Canonical name → ID mapping
│   └── validation/           # 5-layer validation report
├── docs/                     # Pipeline + schema + ontology docs
└── releases/                 # Release plans
```

---

## Quick start

```bash
# Clone
git clone https://github.com/GBX-Max1220/knowledge-compiler.git
cd knowledge-compiler

# See it in action — no API keys, no setup
python demo.py

# Validate the objects
python scripts/validate.py --book acsm12

# List all registered concepts
python -c "
import yaml, os
reg = yaml.safe_load(open('books/acsm12/registry.yaml'))
for name, oid in sorted(reg['registry'].items()):
    print(f'{name:40s} → {oid}')
"
```

### Running the full pipeline

The pipeline stages (chunk, extract, normalize) use an AI provider to generate objects from textbook content. Two options:

- **Reasonix CLI** — default provider. Install separately as `reasonix` and run `python scripts/run_queue.py books/acsm12`
- **OpenAI** — set `OPENAI_API_KEY` and pass `--provider openai` to the compiler

---

## Applications

- **Medical guideline agents** — query screening algorithms, contraindications, and treatment protocols
- **Exercise coaching** — personalized prescription based on validated thresholds and procedures
- **Clinical decision support** — deterministic risk assessment from structured knowledge
- **Educational tutoring** — students explore typed concepts with verified definitions
- **Scientific knowledge bases** — multi-source, versioned, queryable

---

## Roadmap

| Version | Coverage | Status |
|---------|----------|--------|
| v0.1 | Ch1–3: Benefits, Screening, Fitness Testing | ✅ Released |
| v0.2 | Ch4–6: Clinical Testing, Exercise Prescription | 🔜 |
| v0.3 | Ch7–9: Environment, Disease Populations | 🔜 |
| v1.0 | Full ACSM 12th Edition | 🔜 |

**Future books (framework-agnostic):**
- NSCA's Essentials of Strength Training and Conditioning
- WHO Physical Activity Guidelines
- General medical / HCI handbooks

---

## License

MIT

## Citation

```bibtex
@software{guo_knowledge_compiler_2025,
  author = {Guo, Max},
  title = {Knowledge Compiler: From Textbook to Structured Skill},
  year = {2025},
  url = {https://github.com/GBX-Max1220/knowledge-compiler}
}
```
