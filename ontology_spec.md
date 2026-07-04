# Ontology Specification v1

> The language specification for the Knowledge Compiler.
> Every predicate, semantic type, and extraction rule is defined here.
> All books, regardless of source (ACSM, WHO, NSCA, Cochrane, GRADE),
> must conform to this specification.

---

## 1. Identity System

### 1.1 ID Format

```
{type}.{canonical_name}
```

Examples:
```
concept.exercise
threshold.met.moderate
table_row.basketball_game
procedure.test_termination
```

**Rules:**
- ID **must not** contain the source prefix (e.g. no `acsm.concept.exercise`)
- Source information belongs in `metadata.sources[]`, not in the ID
- Canonical name uses `snake_case`, US English spelling
- If two sources define the same concept (e.g. ACSM and WHO both define "Exercise"), they share the same ID and their `sources[]` arrays merge

### 1.2 Multi-Source Conflict Resolution

When two sources provide different definitions for the same ID:

1. If definitions are semantically equivalent → merge `aliases`, keep both `sources[]`
2. If definitions differ → create a new ID with `{type}.{concept}.{source_suffix}` and link via `related_concepts`
3. Always preserve full `provenance` so the conflict is traceable

### 1.3 ID Registration

Every new ID must be registered in `books/{source}/registry.yaml` to:
- Prevent duplicate IDs and name variants (e.g. "Exercise" vs "Exercises")
- Provide a single source of truth for canonical name ↔ ID mapping
- Enable cross-source lookup and merge

The registry is a flat mapping:

```yaml
# books/acsm12/registry.yaml
registry:
  "Physical Activity": concept.physical_activity
  "Exercise": concept.exercise
  "Physical Fitness": concept.physical_fitness
  "MET": concept.met
  "Light Intensity": threshold.met.light
  "Moderate Intensity": threshold.met.moderate
  "Vigorous Intensity": threshold.met.vigorous
```

**Rules:**
- Keys are canonical_names (US English, Title Case)
- Values are object IDs
- Every object file in `objects/{Type}/` must have a corresponding entry in registry.yaml
- Registry is the **single source of truth** — if a name is not in the registry, it doesn't exist as an object yet

---

## 2. Predicate Enumeration

Only these predicates are permitted in `relationships[].predicate`.
Any predicate not on this list is **banned**.

### 2.1 Hierarchical

| Predicate | Direction | Meaning | Example |
|-----------|-----------|---------|---------|
| `is_a` | child → parent | Class membership | `Exercise is_a Physical Activity` |
| `part_of` | part → whole | Composition | `Cardiorespiratory Endurance part_of Health-Related Fitness` |
| `instance_of` | instance → class | Specific instance | `Basketball Game instance_of Vigorous Activity` |

### 2.2 Relational

| Predicate | Meaning | Example |
|-----------|---------|---------|
| `adjacent_to` | Adjacent in a linear scale | `Light adjacent_to Moderate` |
| `applies_to` | Applies to a population/context | `MET Threshold applies_to Adults` |
| `used_for` | Instrumental use | `MET used_for Intensity Classification` |
| `has_attribute` | Has a defining attribute | `Exercise has_attribute "planned"` |
| `has_value` | Has a numerical value | `Basketball Game has_value 8.0 MET` |
| `classified_as` | Classification assignment | `Basketball Game classified_as Vigorous` |
| `has_purpose` | Purpose/goal | `Exercise has_purpose "improve fitness"` |
| `has_part` | Has a component | `Health-Related Fitness has_part Cardiorespiratory Endurance` |
| `contraindicates` | Contraindication relationship | `Condition contraindicates Exercise Testing` |
| `references` | References another object | `Section references Table 1.1` |

### 2.3 Banned Predicates

These are **never** allowed:
- `related_to` — too vague
- `associated_with` — too vague
- `connected_to` — too vague
- `linked` — too vague
- `depends_on` — prefer `used_for` or `has_purpose`

### 2.4 Adding New Predicates

New predicates must be proposed via a PR that:
1. Defines the predicate
2. Shows 3+ real examples from existing content
3. Explains why existing predicates are insufficient

---

## 3. Semantic Type Enumeration

`schema_type` (the YAML schema used) is separate from `semantic_type` (the domain category).

Allowed `semantic_type` values:

| Semantic Type | Applies to Schema | Examples |
|---------------|-------------------|----------|
| `Activity` | Concept | Exercise, Walking, Basketball |
| `Entity` | Concept | Physical Fitness, Body Composition |
| `Property` | Concept | Intensity, Duration, Frequency |
| `Evidence` | Concept | Absolute SCD Risk, PA-CVD Dose-Response |
| `AnatomicalStructure` | Concept | Skeletal System, Sarcomere, Vertebra |
| `AnatomicalSystem` | Concept | Musculoskeletal System, Cardiovascular System |
| `PhysiologicalProcess` | Concept | Action Potential, Crossbridge Cycling |
| `Protein` | Concept | Myosin, Actin, Troponin |
| `Theory` | Concept | Sliding-Filament Theory |
| `Range` | Threshold | Light, Moderate, Vigorous |
| `Guideline` | Recommendation | PA Minimum, Exercise Prescription |
| `Protocol` | Procedure | Exercise Test, Screening Process |
| `Safety` | Warning | Cardiac Event Warning |
| `Contraindication` | Contraindication | Absolute CI, Relative CI |
| `Equation` | Formula | HRmax Formula |
| `TableRow` | TableRow | Row from Table 1.1 |

---

## 4. Extraction Rules

### 4.1 What counts as one Definition?

A definition is a single sentence (or paragraph) that:
- Explicitly defines a term (e.g. "X is defined as...", "X refers to...", "X is...")
- Has a clear subject and predicate

**Do NOT split** a definition that spans multiple sentences if they jointly define the same term.
**Do merge** standalone bullet-point definitions under the same parent heading (e.g. Box 1.1's component list → children of `Health-Related Physical Fitness Components`).

### 4.2 When to split into multiple Objects?

Split when:
- A single sentence defines multiple distinct thresholds (e.g. "light is 1.6–2.9, moderate is 3.0–5.9, vigorous is ≥6.0" → 3 Threshold objects)
- A table has multiple rows (each row → 1 TableRow object)
- A list defines multiple independent concepts (each bullet → 1 Concept + parent link)

Do NOT split when:
- A paragraph elaborates on a single definition (keep as one Concept)
- Multiple sentences describe the same procedure step (keep as one Procedure)

### 4.3 What to extract from tables?

Every row in a reference/prescriptive table becomes one TableRow object.
Table headers become the `fields` key names.
If a table has subtotals or notes, they become additional fields with `type: "note"`.

---

## 5. Normalization Rules

### 5.1 Aliases — Strict Rule

`aliases` **must** come from the original text.
- Acceptable: "PA is also referred to as physical activity" → alias: "Physical Activity"
- Acceptable: "Exercise (also called planned physical activity)" → alias: "Planned Physical Activity"
- **Forbidden**: AI-generated synonyms not present in the source text
- **Forbidden**: Adding common-sense aliases without source evidence

### 5.2 Attributes — What qualifies?

Attributes are **defining characteristics explicitly stated in the definition**.
- Acceptable: `Exercise` → `attributes: ["planned", "structured", "repetitive"]` (all stated in definition)
- **Forbidden**: Deriving attributes from general knowledge

### 5.3 Relationships — Evidence Requirement

Every relationship must have explicit textual evidence:
- `is_a` — requires "X is a type of Y" or "X is Y" in the text
- `part_of` — requires "X is part of Y" or "X is a component of Y"
- `adjacent_to` — requires items appearing in the same sequential list
- `used_for` — requires "X is used for Y" or "X is a method for Y"
- `has_attribute` — requires the attribute text in the definition

### 5.4 Numerical Precision

All numerical values must be preserved exactly as written:
- `≥6.0` → `numerical_value: 6.0`, `comparison_operator: "≥"`
- `3.0–5.9` → `numerical_value: 3.0`, `numerical_max: 5.9`, `comparison_operator: "range"`
- `~3.5` → `numerical_value: 3.5`, with the tilde noted in `condition`

### 5.5 Page Number Precision

Every object must have both:
- `book_page`: the page number as printed in the book (from manifest.pdf_pages)
- `pdf_page`: the actual PDF page number (book_page + PDF offset)

If the offset is unknown, mark `pdf_page: null` and note in provenance.

---

## 6. Graph Compatibility

### 6.1 Neo4j / NetworkX Mapping

```
Object → Node
  id           → node ID
  type         → label
  canonical_name → property
  fields       → properties (flattened)

relationships[] → Edge
  predicate    → edge type
  target       → target node ID
```

### 6.2 Cross-Source Fusion

When ingesting from multiple sources:
1. Load all nodes into a single graph
2. Nodes with the same ID are merged (union of `sources[]`, `aliases[]`)
3. Conflicting properties are flagged in `validation/conflicts.json`
4. Edge set is deduplicated on `(source_id, predicate, target_id)`

---

## 7. Validation Rules

### 7.1 Automated Checks

| Check | Fails When |
|-------|-----------|
| ID uniqueness | Duplicate ID found |
| Predicate whitelist | Unknown predicate used |
| Semantic type whitelist | Unknown semantic_type used |
| Source completeness | Missing book / edition / section / page |
| YAML parsability | File cannot be parsed |
| Target resolvability | relationship.target does not exist as an ID |

### 7.2 Manual Review Triggers

| Trigger | Action |
|---------|--------|
| New ID created | Reviewer checks for duplicates |
| Definition > 500 tokens | Reviewer checks if split needed |
| TableRow > 50 rows | Reviewer checks for sub-tables |
| Same predicate : target pair appears > 3 times | Reviewer checks for redundancy |

---

## 8. Pipeline Stages

### 8.1 Stage Definitions

```
chunks/         → Section-level markdown (one per section from PDF)
extraction/     → Labeled ontology items (TYPE/TITLE/PAGE/ORIGINAL blocks)
normalized/     → Schema-conformant YAML objects, one file per section (audit artifact)
objects/        → Decomposed individual object files, one file per ID
validation/     → Quality reports
graph/          → Neo4j/NetworkX export files
exports/        → Platform-specific exports
```

### 8.2 normalized/ vs objects/ — Why Two Dirs?

| Directory | Organization | Purpose |
|-----------|-------------|---------|
| `normalized/` | Per section (e.g. `01_02.yaml`) | Audit trail — review all objects from one section together |
| `objects/` | Per type + per ID (e.g. `Concept/exercise.yaml`) | Consumption — merge, query, update individual objects |

`normalized/` is the **AI's output** (one file per section).
`objects/` is the **decomposed result** (one file per object, split mechanically by script).

### 8.3 Decomposition

`scripts/decompose_objects.py` reads `normalized/{section}.yaml` and writes:
- `objects/Concept/exercise.yaml`
- `objects/Threshold/met.moderate.yaml`
- etc.

This is a **mechanical** split — no AI involved, no information loss.

---

## 9. Canonical Registry

### 9.1 Purpose

The canonical registry is the **single source of truth** for name → ID mapping.
It prevents duplicate objects caused by name variants ("Exercise" vs "Exercises" vs "Exercise Training").

### 9.2 Location

`books/{source}/registry.yaml`

### 9.3 Format

```yaml
# books/acsm12/registry.yaml
registry:
  "Canonical Name": concept.canonical_name
```

### 9.4 Rules

- Every object in `objects/{Type}/` must have an entry in `registry.yaml`
- Registry keys are **canonical names** (US English, Title Case)
- Registry values are **object IDs** (snake_case)
- When a new source adds an object with a canonical name already in the registry:
  - If IDs match → merge sources[]
  - If IDs differ → create a suffixed ID and link via related_concepts
- Registry entries are added by `scripts/decompose_objects.py` automatically
- Manual edits to `registry.yaml` should be reviewed for conflicts

### 9.5 Lookup Flow

```
Agent query: "What is Exercise?"
    → Search registry.yaml for "Exercise"
    → Found: concept.exercise
    → Load objects/Concept/exercise.yaml
    → Return structured object
```

No LLM needed for ID resolution.

The Knowledge Compiler uses semantic versioning:

- **Major**: Breaking changes to the ontology spec (predicate removal, ID format change)
- **Minor**: New predicates, new semantic types, new schema types
- **Patch**: Clarifications, examples, corrections

`ontology_spec.md` version is embedded as a comment at the top of each generated YAML file:
```yaml
# ontology: knowledge-compiler/v1
```
