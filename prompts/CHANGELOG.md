# Prompt Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | — | Initial extraction prompt (TYPE/TITLE/PAGE/ORIGINAL format) |
| 0.2 | — | Added hierarchy detection (PARENT/CHILDREN) and threshold splitting |
| 0.3 | — | Added ID generation rules, type mapping table |
| 0.4 | — | Removed confidence, parent_concepts, relationships.description |
| 0.5 | — | Added provenance fields, separated book_page/pdf_page |
| 0.6 | — | Added registry requirement, canonical_name must match registry key |
| 0.7 | — | Added YAML colon escaping rule (values with `:` must be quoted) |
| 0.8 | — | Added list field normalization (empty lists = `[]`, not `null`) |
| 0.9 | — | Added Evidence to semantic_type allowlist |
| **1.0** | **2026-07-04** | **FREEZE — Chapter 1 validated, all 5 layers PASS** |
