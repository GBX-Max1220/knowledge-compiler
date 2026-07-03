# Ontology Design

> This document explains the ontology design philosophy behind the Knowledge Compiler.

## Why Not Just Use LLMs to Answer Questions?

LLMs are good at synthesis but bad at:
- Verbatim recall of specific numbers (MET values, dosage ranges)
- Consistent naming across multiple retrievals
- Traceable provenance ("which page says this?")
- Cross-source consistency (ACSM vs WHO definition of "Exercise")

The Knowledge Compiler solves this by extracting structured objects that are:
- **Verbatim** — no summarization, no paraphrase
- **Typed** — each object knows what kind of thing it is
- **Sourced** — every object points to its exact page in the original
- **Related** — objects are connected by typed, enumerated predicates

## Ontology vs Taxonomy vs Schema

| Layer | Definition | Example |
|-------|------------|---------|
| **Schema** | Field structure for each type | `concept.yaml` requires `definition`, `attributes`, `purpose` |
| **Ontology** | Rules about what concepts mean and how they relate | `is_a` ≠ `part_of`; aliases require text evidence |
| **Taxonomy** | Hierarchical classification of concepts | Exercise is_a Physical Activity is_a Human Activity |

The Knowledge Compiler defines all three layers:
- Schema in `schema/{type}.yaml`
- Ontology in `ontology_spec.md`
- Taxonomy is emergent from the graph (derived from `is_a` / `part_of` edges)

## Why No confidence/parent_concepts/description in relationships?

These were removed in v0.2 based on design review:

| Removed | Reason |
|---------|--------|
| `confidence` | Ambiguous source — whose confidence? Replaced by `provenance` + `evidence_level` |
| `parent_concepts` | Redundant with graph relationships. Inferred from `is_a` / `part_of` edges |
| `relationships.description` | Graph engines (Neo4j, NetworkX) don't use it. Human-readable docs drift |

## Multi-Source Strategy

When a second source (e.g. WHO) defines "Exercise":
1. If the definition is semantically identical → merge into `concept.exercise`, union `sources[]`
2. If the definition differs → create `concept.exercise.who` and link with `related_concepts`
3. Conflicts are tracked in `validation/conflicts.json`

This enables queries like:
- "What does ACSM say about Exercise?" → filter by source
- "What does WHO say differently about Exercise?" → compare related_concepts
- "What do ALL sources agree on?" → intersection of objects sharing the same ID
