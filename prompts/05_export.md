# Prompt: 05 — Export

**Stage:** Objects → Export
**Input:** All YAML objects in `books/{source}/objects/`
**Output:** Target-format files in `exports/{target}/`

## Supported Export Targets

### Neo4j (graph/neo4j.cypher)

```cypher
// Nodes
CREATE (n:Concept {id: "concept.exercise", canonical_name: "Exercise"});

// Edges
MATCH (a {id: "concept.exercise"}), (b {id: "concept.physical_activity"})
CREATE (a)-[:is_a]->(b);
```

### OpenAI / Vector DB (exports/openai/batch.jsonl)

```jsonl
{"id": "concept.exercise", "text": "Exercise is a type of PA consisting of...", "metadata": {"type": "Concept", "source": "ACSM12", "section": "1.2"}}
```

### Claude / Generic JSON (exports/generic/objects.json)

```json
{
  "objects": [ ... ],
  "relationships": [
    {"source": "concept.exercise", "predicate": "is_a", "target": "concept.physical_activity"}
  ]
}
```

## Export Rules

1. All IDs must resolve — no dangling relationship targets.
2. All source pages must be preserved in metadata.
3. Provenance chain must be preserved in metadata.
4. Deduplicate edges on (source_id, predicate, target_id).
