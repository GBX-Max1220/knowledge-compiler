# Prompt: 02 — Extract

**Stage:** Chunk → Extraction
**Input:** One markdown file from `books/{source}/chunks/`
**Output:** Ontology-labeled extraction items

## Instructions

You are an ontology extraction engine.

Read ONE section. Your ONLY job is labeling.

### Allowed Labels

| Label | When to Use |
|-------|-------------|
| Definition | Formal definition of a term (e.g. "X is defined as...", "X refers to...") |
| Recommendation | A guideline, prescription, or recommended action |
| Procedure | An ordered set of steps |
| Threshold | A cutoff, boundary, or classification range |
| Warning | Safety concern or potential adverse event |
| Contraindication | Condition that prohibits an activity |
| Risk Factor | A factor that increases risk |
| Evidence | A research finding or evidence statement |
| Formula | A mathematical equation |
| Figure | Reference to a figure/illustration |
| Table | Reference to a table (the table itself, not individual rows) |
| Decision Rule | An if-then decision logic |

### Rules

1. Do NOT summarize. Copy the original text verbatim.
2. Do NOT explain. Return only the labeled items.
3. Preserve page numbers.
4. Preserve section identifiers.
5. Preserve all citations.
6. Preserve all numerical values.
7. If a section has no labelable content, return "NONE".

### Hierarchy Detection

When a Definition contains sub-definitions (e.g. a box titled "Health-Related Physical Fitness Components" with a bullet list underneath), identify the parent-child relationship. The parent gets the main label; children are flagged as `child_of: {parent_id}`.

### Threshold Splitting

When a single sentence defines multiple thresholds (e.g. "light is 1.6–2.9, moderate is 3.0–5.9, vigorous is ≥6.0"), split into one Threshold item per category.

### Output Format

```
TYPE
Definition | Recommendation | Procedure | Threshold | ...

TITLE
The standardized title

PAGE
Page number(s)

SECTION
Section identifier — Section title

ORIGINAL TEXT
Verbatim text from the source

PARENT
(Optional) Parent concept title if this is a child definition

CHILDREN
(Optional) List of child titles if this is a parent definition

RELATIONSHIPS
(Optional) Predicate: target — only when explicitly stated in text

END
```
