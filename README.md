# Knowledge Compiler

**A deterministic knowledge layer for AI agents.**

Knowledge Compiler transforms expert textbooks into **Knowledge IR** — a typed, validated,
backend-independent intermediate representation that decouples knowledge extraction from consumption.

```
Source → Knowledge IR → Target Backend (YAML / Neo4j / RDF / Skill / MCP)
```

Most AI systems that use textbooks do one of two things:
- **RAG** — retrieve chunks of raw text. Fast but unstructured. No guarantees on what the model will find.
- **Fine-tuning** — expensive, opaque, hard to update.

This is a third path: **compile knowledge into a deterministic, auditable, composable intermediate representation** that an agent can query directly.

> **Current sources:** ACSM 12th Ed. (707 objects) + NSCA-CSCS 5th Ed. (1598 objects)
> **Total: 2305 validated Knowledge IR nodes**

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

# Load compiled Knowledge IR
skill = Skill("sources/books/acsm12")

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

## Why Knowledge IR?

Knowledge Compiler addresses four fundamental problems that RAG and fine-tuning cannot solve:

| Problem | RAG | Fine-tuning | **Knowledge IR** |
|---------|-----|-------------|----------------|
| **Determinism** | ❌ Same query, different answer | ❌ Same input, same weights | ✅ Same query, same objects, same result |
| **Auditability** | ❌ Chunk-level at best | ❌ Source forgotten | ✅ Page-level citation on every fact |
| **Composability** | ❌ Retrieval only | ❌ Static | ✅ Object → Agent → Workflow |
| **Maintainability** | ❌ Re-embed entire corpus | ❌ Re-train entire model | ✅ Add/remove one object |

These properties do not depend on model context window size. Even with infinite context, a deterministic, auditable, composable knowledge layer provides guarantees that probabilistic retrieval cannot.

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

> 📖 See [`docs/knowledge-ir.md`](docs/knowledge-ir.md) for the formal definition of Knowledge IR.

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
├── ontology_spec.md          # Language spec for the Knowledge IR
├── schema/                   # Type definitions (8 files)
├── prompts/                  # Pipeline prompts (6 files)
├── scripts/                  # Automation
├── compiler/                 # CLI + task queue + provider abstraction
├── sources/                  # Source documents compiled into IR
│   └── books/                # Textbook sources
│       ├── acsm12/           # 707 IR nodes (12 chapters)
│       └── nsca-cscs/        # 1598 IR nodes (26 chapters)
│   (future: papers/ guidelines/ wiki/)
├── knowledge_compiler/       # Skill API for querying compiled IR
├── docs/                     # Pipeline + schema + ontology + IR docs
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
