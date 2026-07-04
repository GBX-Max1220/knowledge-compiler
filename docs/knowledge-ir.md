# Knowledge IR — Intermediate Representation for Knowledge

> **Knowledge IR** is the typed, structured, validated, backend-independent intermediate representation
> produced by the Knowledge Compiler. It is the core abstraction that separates knowledge
> **extraction** from knowledge **consumption**.

---

## Why IR?

Traditional compilers (LLVM, GCC) succeed because they define a **universal intermediate representation**
that decouples frontends (source languages) from backends (target architectures):

```
C Source ──┐
           ├──→ LLVM IR ──→ x86 / ARM / WASM
Rust ──────┘
```

Knowledge Compiler applies the same principle to knowledge:

```
Textbook PDF ──┐
               ├──→ Knowledge IR ──→ YAML / Neo4j / RDF / Skill / MCP
Clinical Guide ─┘
```

The IR is **not** the output. It is the **canonical form** that all sources compile into
and all backends consume from.

---

## IR Properties

### ✅ Typed

Every Knowledge IR node has an explicit type from a fixed schema:

```
Concept, Threshold, Procedure, Recommendation, Warning,
Contraindication, Formula, TableRow, Evidence, Figure,
DecisionRule, RiskFactor, Table
```

Each type defines:
- **Required fields** (e.g., `definition` for Concept, `steps` for Procedure)
- **Optional fields** (e.g., `attributes`, `purpose` for Concept)
- **Allowed semantic types** (e.g., `Activity`, `Entity`, `AnatomicalStructure`)

### ✅ Structured

Knowledge IR is not free text. It has a formal structure:

```yaml
id: concept.exercise
type: Concept
canonical_name: Exercise
semantic_type: Activity
definition: "A type of PA consisting of planned, structured..."
relationships:
  - predicate: is_a
    target: concept.physical_activity
```

Fields are consistent across all objects of the same type.

### ✅ Normalized

- No duplicate IDs (`concept.exercise` means the same thing regardless of source)
- Cross-source merge: ACSM and NSCA definitions of `muscular_strength` share one ID
- Canonical names are unique (duplicates are resolved by adding type suffix)
- Relationships are pure triples: `subject → predicate → object`

### ✅ Validated

Every IR node passes 5 layers of automated validation:

| Layer | Check | Failure Mode |
|-------|-------|-------------|
| 1 Syntax | YAML parsability, required fields | Structural error |
| 2 Schema | Type-specific field completeness | Warning |
| 3 Ontology | Relationship targets exist, predicates allowed | Structural error |
| 4 Graph | No duplicate IDs/names, orphan detection | Structural error |
| 5 Semantic | Non-empty definitions, valid ranges | Advisory |

### ✅ Backend-Independent

The same IR can be exported to multiple targets without modification:

| Backend | Purpose | Status |
|---------|---------|--------|
| YAML files | Direct query via `Skill` API | ✅ Active |
| Neo4j / Cypher | Graph database queries | 📝 Planned |
| JSON-LD / RDF | Semantic web integration | 📝 Planned |
| MCP Server | Agent tool integration | 📝 Planned |
| Vector embeddings | Hybrid RAG + IR retrieval | 📝 Planned |
| Fine-tuning dataset | Model training data | 📝 Planned |

### ✅ Source-Grounded

Every IR node carries provenance:

```yaml
source:
  book: "Essentials of Strength Training and Conditioning"
  edition: 5
  chapter: 1
  section: "1.2"
  book_page: 71
```

This means every fact is traceable to its exact source location.

---

## IR vs. Alternatives

| Property | Knowledge IR | RAG Chunks | Fine-tuning Data |
|----------|-------------|------------|-----------------|
| Typed | ✅ Yes | ❌ Raw text | ❌ Opaque |
| Validated | ✅ 5 layers | ❌ None | ❌ None |
| Composability | ✅ Object → Agent → Workflow | ❌ Retrieval only | ❌ Static |
| Deterministic | ✅ Same query → same result | ❌ Probabilistic | ✅ Fixed weights |
| Auditability | ✅ Page-level citation | ❌ Chunk-level | ❌ Source forgotten |
| Incremental update | ✅ Add/remove one object | ❌ Re-embed corpus | ❌ Re-train model |
| Machine-readable | ✅ `steps[]`, `range`, `numerical_value` | ❌ Free text | ❌ Weights only |

---

## The Compiler Pipeline

```
                         Frontend                    IR                          Backend
                    ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────────────┐
                    │                 │    │                  │    │                          │
  Textbook PDF ────→│  Chunk +        │    │                  │    │  YAML (Skill API)        │
                    │  Extract +      │───→│  Knowledge IR    │───→│  Neo4j (Graph DB)        │
  Clinical Guide ───→│  Generate +     │    │  (typed objects) │    │  RDF (Semantic Web)      │
                    │  Validate       │    │                  │    │  MCP (Agent Tool)        │
  Research Paper ───→│                 │    │                  │    │  Vector (Hybrid RAG)     │
                    │                 │    │                  │    │                          │
                    └─────────────────┘    └──────────────────┘    └──────────────────────────┘
```

The frontend converts a source document into IR nodes.
The IR is the canonical representation.
Backends consume IR and produce target-format output.

This decoupling means:
- Adding a **new source type** (e.g., research papers) only requires a new frontend
- Adding a **new backend** (e.g., RDF export) only requires a new exporter
- The IR itself remains stable across both

---

## Current Status

| Source Type | Status | Objects |
|-------------|--------|:-------:|
| Textbook (ACSM 12th) | ✅ Released | 707 |
| Textbook (NSCA-CSCS 5th) | ✅ Released | 1598 |
| Clinical Guidelines | 📝 Planned | — |
| Research Papers | 📝 Planned | — |
| Encyclopedic Sources | 📝 Planned | — |

| Backend | Status |
|---------|--------|
| YAML + Skill API | ✅ Active |
| Neo4j / Cypher | 📝 Planned |
| MCP Server | 📝 Planned |
| Vector Embeddings | 📝 Planned |
| RDF / JSON-LD | 📝 Planned |
