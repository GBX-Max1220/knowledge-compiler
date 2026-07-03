# Schema

> The Knowledge Compiler uses typed schemas stored in `schema/{type}.yaml`.
> Every normalized object must conform to its type's schema.

## Available Schemas

| Schema | File | Use Case |
|--------|------|----------|
| Concept | `schema/concept.yaml` | Defined terms with hierarchy |
| Threshold | `schema/threshold.yaml` | Cutoffs, ranges, classifications |
| TableRow | `schema/tablerow.yaml` | Individual rows from any table |
| Procedure | `schema/procedure.yaml` | Ordered step-by-step processes |
| Recommendation | `schema/recommendation.yaml` | Guidelines and prescriptions |
| Warning | `schema/warning.yaml` | Safety concerns |
| Contraindication | `schema/contraindication.yaml` | Prohibiting conditions |
| Formula | `schema/formula.yaml` | Equations with variables |

## Common Header Structure

Every object shares:

```
id               — unique identifier (no source prefix)
type             — schema type
canonical_name   — standardized name
semantic_type    — domain category (Activity, Range, Guideline...)
aliases          — ONLY from original text
source           — { book, edition, chapter, section, book_page, pdf_page }
provenance       — { extraction, normalization, reviewed }
evidence_level   — only when explicitly stated
relationships    — [{ predicate, target }] — pure triples, no descriptions
```

## Schema Design Principles

1. **Map for TableRow** — Flexible `fields` key-value map instead of fixed columns. Different table structures (ACSM vs WHO vs NSCA) use different keys without schema changes.
2. **Relationships are edges** — No nested parent/child in the body. Hierarchy is inferred from the graph.
3. **Source in metadata, not in ID** — IDs are source-agnostic. Sources merge on the same ID.
4. **Provenance is mandatory** — Every object is traceable back to its original page and extraction engine.
