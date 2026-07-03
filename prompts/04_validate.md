# Prompt: 04 — Validate

**Stage:** Normalized → Validated
**Input:** One or more YAML objects from `books/{source}/normalized/`
**Output:** Validation report

## Validation Checklist

### 1. YAML Parsability
- [ ] File parses without errors
- [ ] All required fields present per schema/{type}.yaml
- [ ] No unknown fields

### 2. ID Compliance
- [ ] ID matches pattern `{type}.{name}`
- [ ] No duplicate IDs in the source
- [ ] No ID collisions across sources (check books/{*}/objects/index.yaml)

### 3. Predicate Compliance
- [ ] All predicates are in the ontology_spec.md allowlist
- [ ] No banned predicates used
- [ ] relationship.target IDs exist or are plausible

### 4. Source Completeness
- [ ] book, edition, chapter, section, book_page, pdf_page all present
- [ ] Pages fall within the source document's range

### 5. Numerical Integrity
- [ ] All numerical values match extraction exactly
- [ ] Threshold ranges are well-formed (min ≤ max)
- [ ] comparison_operator is valid

### 6. Content Integrity
- [ ] No summarization detected
- [ ] No invented relationships
- [ ] aliases have textual evidence

## Output Format

```yaml
validation:
  file: "books/acsm12/normalized/01_02.yaml"
  status: "PASS" | "FAIL" | "WARN"
  checks:
    - name: "yaml_parsability"
      status: "PASS"
    - name: "predicate_compliance"
      status: "FAIL"
      issues:
        - "Unknown predicate 'linked_to' in concept.exercise"
  stats:
    objects_created: 18
    relationships_created: 24
    warnings: 2
    errors: 0
```
