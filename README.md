# Knowledge Compiler — v0.1
#
# A structured, validated ACSM-based exercise science skill.
# Extracted from ACSM's Guidelines for Exercise Testing and Prescription, 12th Ed.
#
# Coverage: Chapters 1–3 (Benefits & Risks, Preparticipation Evaluation, Fitness Testing)
# Objects: 74 · Types: 6 · Validation: 5-layer PASS

## Quick Stats

| Metric | Value |
|--------|-------|
| Book | ACSM's Guidelines 12th Ed. |
| Coverage | Chapters 1–3 |
| Objects | 74 |
| Types | Concept (38), Threshold (11), Procedure (9), Recommendation (8), Warning (5), Formula (3) |
| Edges | 23 |
| Validation | 5-layer PASS |
| Status | Beta / v0.1 |

## Repository Structure

```
knowledge-compiler/
├── ontology_spec.md          # Ontology specification (frozen v1.0)
├── schema/                   # Type definitions (8 files)
├── prompts/                  # Pipeline stage prompts (6 files)
├── scripts/                  # Automation scripts
├── compiler/                 # Production infrastructure
│   ├── cli.py                # knowledge-compiler CLI
│   ├── queue.py              # Task queue with retry/resume
│   └── providers/            # Provider abstraction
├── books/acsm12/
│   ├── objects/              # 74 validated objects
│   │   ├── Concept/          #   Definitions and evidence
│   │   ├── Threshold/        #   Classification boundaries
│   │   ├── Procedure/        #   Step-by-step protocols
│   │   ├── Recommendation/   #   Evidence-based guidelines
│   │   ├── Warning/          #   Safety alerts
│   │   └── Formula/          #   Equations
│   ├── skill/
│   │   ├── skill.md          # Agent-usable skill definition
│   │   └── evaluation_set_v0.1.yaml  # 25-question benchmark
│   ├── registry.yaml         # Canonical name → ID mapping
│   └── validation/           # 5-layer validation report
├── docs/                     # Documentation
└── releases/                 # Release plans
```

## What This Is

A **structured, validated knowledge skill** for exercise science. Unlike raw PDFs or RAG pipelines, this project produces:

- **Typed objects** — each piece of knowledge knows what kind of thing it is (Concept, Threshold, Procedure, etc.)
- **Sourced** — every object points to its exact page in the textbook
- **Related** — objects are connected by typed, enumerated relationships
- **Validated** — 5-layer automated validation (syntax, schema, ontology, graph, semantic)
- **Agent-ready** — skill.md defines exactly how an AI should use the objects

## Skill Capabilities (v0.1)

The skill can answer questions about:

- **Exercise terminology** — PA vs Exercise, MET, VO2max, fitness components
- **Intensity classification** — MET ranges (light/moderate/vigorous), BMI, blood pressure, cholesterol
- **Screening protocols** — ACSM preparticipation algorithm, PAR-Q+, medical clearance
- **Safety** — signs/symptoms of CV disease, test termination criteria, cardiac prodromal symptoms
- **Assessment procedures** — resting BP, 1-RM testing, YMCA cycle protocol, sit-and-reach
- **Recommendations** — PA guidelines, bout duration rules, weight management
- **Formulas** — VO2max estimation, body density, percent body fat

## Example

```python
# Load a threshold and compare
from knowledge_compiler import load_object

bmi = load_object("threshold.bmi_classification")
# bmi.range = "<18.5 Underweight, 18.5-24.9 Normal, 25.0-29.9 Overweight, ..."
# bmi.numerical_value = 18.5
# bmi.numerical_max = 39.9

if 25.0 <= user_bmi <= 29.9:
    category = "Overweight"
```

## Validation

Every object passes 5 layers of automated validation:

| Layer | Check | Status |
|-------|-------|--------|
| 1 Syntax | YAML parsability, required fields | ✅ PASS |
| 2 Schema | Type-specific required fields | ✅ PASS |
| 3 Ontology | Relationship targets exist, predicates allowed | ✅ PASS |
| 4 Graph | No duplicate IDs, no orphan edges | ✅ PASS |
| 5 Semantic | Meaningful definitions, complete thresholds | ✅ PASS |

## Pipeline

```bash
# Initialize task queue
knowledge-compiler build acsm12 --init

# Check progress
knowledge-compiler status acsm12

# Validate generated objects
knowledge-compiler validate acsm12

# Tag a release
knowledge-compiler release acsm12 v0.1
```

## Roadmap

| Version | Coverage | Status |
|---------|----------|--------|
| v0.1 | Chapters 1–3 | ✅ Released |
| v0.2 | Chapters 4–6 | 🔜 |
| v0.3 | Chapters 7–9 | 🔜 |
| v1.0 | Full ACSM 12th Ed. | 🔜 |

## License

MIT

## Citation

```bibtex
@software{guo_knowledge_compiler_2025,
  author = {Guo, Max},
  title = {Knowledge Compiler: A Structured ACSM Exercise Science Skill},
  year = {2025},
  url = {https://github.com/max-guo/knowledge-compiler}
}
```
