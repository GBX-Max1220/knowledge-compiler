# Knowledge Compiler

**From textbook PDF → structured, validated, agent-ready knowledge objects.**

```
PDF → Chunk → Extract → Normalize → Validate → Skill
```

Most AI systems that use textbooks do one of two things:
- **RAG** — retrieve chunks of raw text. Fast but unstructured. No guarantees on what the model will find.
- **Fine-tuning** — expensive, opaque, hard to update.

This is a third path: **compile textbooks into typed, validated, machine-readable knowledge objects** that an agent can query directly.

---

## What can it do right now?

Ask it anything from ACSM's *Guidelines for Exercise Testing and Prescription*, Chapters 1–3:

```
Q: "Can a 55-year-old man with hypertension begin vigorous exercise?"

The system loads:
  → threshold.cvd_risk_factors    (age ≥45 = risk factor, BP ≥130/80 = risk factor)
  → procedure.acsm_screening      (non-exerciser + 2+ risk factors + vigorous = clearance needed)
  → recommendation.medical_clearance

Answer: Medical clearance is recommended before starting vigorous exercise.
Sources: ACSM12 Ch2.2.11 (p.150), Ch2.2.7 (p.142)
```

Not a chunk. Not a guess. A typed decision chain with page-level citations.

---

## Quick demo

```python
from knowledge_compiler import Skill

skill = Skill("books/acsm12")

# Threshold check
bmi = skill.get("threshold.bmi_classification")
# → BMI 27 → "Overweight (25.0-29.9)"

# Procedure lookup
protocol = skill.get("procedure.one_rm_testing")
# → 8 steps, from warm-up to failure

# Safety check
warnings = skill.get("warning.signs_symptoms_cv_disease")
# → 9 signs, action: seek medical evaluation
```

Every query returns an **object** — typed, sourced, validated — not generated text.

---

## Coverage (v0.1)

| Type | Count | What it covers |
|------|-------|---------------|
| Concept | 38 | PA, Exercise, MET, VO₂max, fitness components, sedentary behavior, CVD risk factors |
| Threshold | 11 | MET intensity, BMI, BP, cholesterol, waist circumference, body fat % |
| Procedure | 9 | Screening algorithm, BP measurement, 1-RM testing, YMCA protocol, test termination |
| Recommendation | 8 | PA guidelines, medical clearance, screening for young athletes, cardiac prevention |
| Warning | 5 | CV signs/symptoms, cardiac prodromal symptoms, SCD/AMI risk, MSI risk |
| Formula | 3 | Cooper 12-min run, body density (Jackson-Pollock), % body fat (Siri) |
| **Total** | **74** | **ACSM 12th Ed., Chapters 1–3** |

---

## How it's different

| | RAG | Fine-tuning | Knowledge Compiler |
|---|---|---|---|
| Source-grounded | ✅ Sometimes | ❌ | ✅ Always (page-level) |
| Typed output | ❌ | ❌ | ✅ Concept / Threshold / Procedure / ... |
| Machine-readable | ❌ | ❌ | ✅ `numerical_value`, `steps[]`, `signs[]` |
| Validation | ❌ | ❌ | ✅ 5-layer automated |
| Update cost | Low | High | Low (re-run one section) |
| Agent integration | Probabilistic | Opaque | Deterministic |

---

## Validation

Every object passes 5 layers:

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

---

## Roadmap

| Version | Coverage | Status |
|---------|----------|--------|
| v0.1 | Ch1–3: Benefits, Screening, Fitness Testing | ✅ Released |
| v0.2 | Ch4–6: Clinical Testing, Exercise Prescription | 🔜 |
| v0.3 | Ch7–9: Environment, Disease Populations | 🔜 |
| v1.0 | Full ACSM 12th Edition | 🔜 |

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
