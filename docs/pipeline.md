# Pipeline

> The Knowledge Compiler transforms textbook PDFs into structured, queryable knowledge objects.

## Overview

```
PDF
 |
 v
 [01] Chunk
 |  Extract section text from PDF using manifest.yaml
 |  Output: sources/{source}/chunks/{section_id}.md
 |
 v
 [02] Extract
 |  Label ontology items (Definition, Threshold, TableRow, ...)
 |  Output: sources/{source}/extraction/{section_id}.yaml
 |
 v
 [03] Generate (Normalize)
 |  Convert extraction items into standardized schema objects
 |  Output: sources/{source}/normalized/{section_id}.yaml
 |
 v
 [04] Decompose
 |  Split normalized stage output into per-object YAML files
 |  Infer object type from the `type` field
 |  Output: sources/{source}/objects/{Type}/{id}.yaml
 |
 v
 [05] Validate
 |  Check schema compliance, ID uniqueness, relationship resolution
 |  Output: sources/{source}/validation/{report_name}.md
 |
 v
 [06] Export
 |  Generate Neo4j/Vector/JSON output for downstream consumption
 |  Output: exports/{target}/
 |
 v
 Skill
   Agent-accessible knowledge base (via knowledge_compiler.Skill)
```

## Stage Details

### 01 — Chunk

- **Input:** `books/{source}/source/*.pdf` + `books/{source}/manifest.yaml`
- **Process:** Extract pages per section, preserve tables/headings/page markers
- **Output:** One markdown file per section at `books/{source}/chunks/{ss}.md`

### 02 — Extract

- **Input:** One chunk markdown file
- **Process:** Label ontology items with TYPE/TITLE/PAGE/ORIGINAL_TEXT
- **Output:** Extraction blocks (text format) → consolidated into `books/{source}/extraction/{ss}.yaml`

### 03 — Normalize

- **Input:** Extraction items
- **Process:** Convert to typed YAML objects per `schema/{type}.yaml`
- **Output:** `books/{source}/normalized/{ss}.yaml` — one YAML document per item

### 04 — Validate

- **Input:** All normalized YAML for a book
- **Process:** Run automated checks against ontology_spec.md and schema definitions
- **Output:** `books/{source}/validation/{report}.md`

### 05 — Export

- **Input:** All objects in `books/{source}/objects/`
- **Process:** Generate target-format files (Cypher, JSONL, JSON)
- **Output:** `exports/{target}/`

## State Machine

Every book passes through these directories, each representing one pipeline stage:

```
source/   → manifest.yaml   → chunks/   → extraction/   → normalized/   → objects/   → graph/
  raw         metadata          split        labeled         structured       deduplicated   export-ready
```

Files only move forward. If a stage fails, the file stays in its current directory.
