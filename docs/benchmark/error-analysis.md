# Error Analysis — Benchmark Failures

> Record: What did each condition get wrong? Why?
> This is the most valuable output for understanding the framework's boundaries.

## Structure

For each question where a condition's answer deviates from expected:

| Field | Description |
|-------|-------------|
| Question ID | q01–q25 |
| Condition | KC / RAG / Raw LLM |
| Expected | Ground truth answer |
| Actual | What the system produced |
| Failure Type | Missing info / Hallucination / Wrong citation / Incomplete / Refused |
| Root Cause | Object gap / Retrieval failure / Prompt issue / Knowledge cutoff |
| Severity | High / Medium / Low |

## Failure Types

| Type | Definition |
|------|-----------|
| Missing Info | Required knowledge exists in source but was not retrieved/provided |
| Hallucination | Answer contains information not present in source materials |
| Wrong Citation | Book/chapter/page reference is incorrect |
| Incomplete | Answer is partially correct but missing key components |
| Refused | System declined to answer ("not enough information") when answer exists |

---

## KC Failures

(Run Phase 3 evaluation to populate)

## RAG Failures

(Run Phase 3 evaluation to populate)

## Raw LLM Failures

(Run Phase 3 evaluation to populate)
