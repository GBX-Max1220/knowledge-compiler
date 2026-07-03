# Prompt: 03 — Object Generation (v1.0 FREEZE)

> ⛔ This prompt is frozen. Do NOT modify during batch processing.
> Changes require a Design Review and a new minor version.
> See `prompts/CHANGELOG.md` for history.

**Stage:** Extraction → Normalized (per-section YAML)
**Input:** Extraction items from `books/{source}/extraction/{section_id}.yaml`
**Output:** One YAML file at `books/{source}/normalized/{section_id}.yaml`
**Next Step:** `scripts/decompose_objects.py` splits into individual objects/

## Instructions

You are an object generation engine.

Your task is to convert every extracted item into a standardized ontology object
conforming to the Knowledge Compiler schema (`schema/{type}.yaml`).

### Rules (hard constraints)

1. **Preserve every fact.** Do NOT summarize, rephrase, or remove.
2. **Preserve every numerical value.** Exact digits, units, operators.
3. **Preserve every citation.** Reference numbers, page numbers.
4. **Use canonical terminology.** US English, snake_case IDs.
5. **Build relationships only when explicitly stated.** No invented edges.
6. **Never invent information.** If the extraction doesn't have it, leave it empty.
7. **Return YAML only.** One YAML document per object, separated by `---`.

No explanations, no commentary, no markdown wrap. YAML only.

### Type Mapping

| Extraction Label → | Schema |
|--------------------|--------|
| Definition | `schema/concept.yaml` (type: Concept) |
| Recommendation | `schema/recommendation.yaml` |
| Procedure | `schema/procedure.yaml` |
| Threshold | `schema/threshold.yaml` |
| Warning | `schema/warning.yaml` |
| Contraindication | `schema/contraindication.yaml` |
| Formula | `schema/formula.yaml` |
| Table (with rows) | `schema/tablerow.yaml` — one object per row |
| Table (reference only) | Embed in the parent Definition's `related_concepts` |

### ID Generation

```
{type}.{canonical_name}
```

- snake_case, US English
- NO source prefix (no `acsm.`)
- e.g. `concept.exercise`, `threshold.met.moderate`, `table_row.basketball_game`
- e.g. `concept.cardiorespiratory_endurance`, `concept.muscular_strength`

### Threshold Splitting

A single extraction item like:

> "light-intensity PA is defined as 1.6–2.9 METs, moderate as 3.0–5.9 METs, and vigorous as ≥6.0 METs"

→ **Three** Threshold objects:
- `threshold.met.light` — range: "1.6–2.9"
- `threshold.met.moderate` — range: "3.0–5.9"
- `threshold.met.vigorous` — range: "≥6.0"

Each with `adjacent_to` relationships linking them in order.

### Hierarchy Handling

When an extraction item has PARENT / CHILDREN:

**Example: Box 1.1 — Health-Related Physical Fitness Components**

Create:
- `concept.health_related_physical_fitness` — the parent
  - `attributes: ["cardiorespiratory endurance", "body composition", "muscular strength", "muscular endurance", "flexibility"]`
- `concept.cardiorespiratory_endurance` — child
  - `relationship: [{predicate: "part_of", target: "concept.health_related_physical_fitness"}]`
- `concept.body_composition` — child
  - `relationship: [{predicate: "part_of", target: "concept.health_related_physical_fitness"}]`
- ... etc. for each child

Do NOT set `parent_concepts` / `child_concepts` fields. Hierarchy is expressed through `relationships[]` only.

### Relationship Derivation

| Extraction Text | Predicate |
|----------------|-----------|
| "X is a type of Y" / "X is Y" | `is_a` |
| "X is part of Y" / "X is a component of Y" | `part_of` |
| Items in same sequential list | `adjacent_to` |
| "X is used for Y" | `used_for` |
| "X has/consists of Y" | `has_attribute` |
| "X is classified as Y" | `classified_as` |

### Aliases Rule

`aliases` can ONLY contain terms explicitly stated as alternatives.

- Acceptable: `"PA (also called physical activity)"` → `aliases: ["Physical Activity"]`
- **Forbidden**: Adding synonyms not in the original text

### PDF Page Mapping

- `book_page`: the page number as printed in the book
- `pdf_page`: the actual PDF page number

For ACSM 12th edition: PDF page = book_page — 68 (the PDF starts counting from the cover, book page 1 = PDF page 69)
- book_page 69 → pdf_page 1 (or just use book_page as-is since manifest uses book pages)
- If in doubt, set `pdf_page: null`

### Output Format

```yaml
# ontology: knowledge-compiler/v1

id: concept.exercise
type: Concept
canonical_name: Exercise
semantic_type: Activity
aliases: []

source:
  book: "ACSM's Guidelines for Exercise Testing and Prescription"
  edition: 12
  chapter: 1
  chapter_title: "Benefits and Risks Associated With Physical Activity"
  section: "1.2"
  section_title: "Physical Activity and Fitness Terminology"
  book_page: 70
  pdf_page: 70

provenance:
  extraction: "reasonix-code-v1"
  generation: "reasonix-code-v1"
  reviewed: "auto"

evidence_level: ""

relationships:
  - predicate: is_a
    target: concept.physical_activity

definition: >
  A type of PA consisting of planned, structured, and
  repetitive bodily movement done to improve and/or
  maintain one or more components of physical fitness.

attributes:
  - planned
  - structured
  - repetitive

purpose:
  - improve physical fitness
  - maintain physical fitness

related_concepts:
  - concept.physical_fitness
---
```

### Output File Structure

Write all objects to a single file:
`books/acsm12/normalized/{section_id}.yaml`

Each object is a separate YAML document separated by `---`.
Order does not matter — `scripts/decompose_objects.py` will sort them by type.
