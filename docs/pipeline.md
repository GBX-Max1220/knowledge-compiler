# Pipeline

> The Knowledge Compiler transforms textbook PDFs into structured, queryable knowledge objects.

## Overview

```
PDF
 │
 ▼
 [01] Chunk
 │  Extract section text from PDF using manifest.yaml
 │  Output: books/{source}/chunks/{section_id}.md
 │
 ▼
 [02] Extract
 │  Label ontology items (Definition, Threshold, TableRow, ...)
 │  Output: books/{source}/extraction/{section_id}.yaml
 │
 ▼
 [03] Normalize
 │  Convert extraction items into standardized schema objects
 │  Output: books/{source}/normalized/{section_id}.yaml
 │
 ▼
 [04] Validate
 │  Check schema compliance, ID uniqueness, relationship resolution
 │  Output: books/{source}/validation/{report_name}.md
 │
 ▼
 [05] Export
 │  Generate Neo4j/Vector/JSON output for downstream consumption
 │  Output: exports/{target}/
 │
 ▼
 Skill
   Agent-accessible knowledge base
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
