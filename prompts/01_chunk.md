# Prompt: 01 — Chunk

**Stage:** PDF → Chunk
**Input:** PDF + manifest.yaml
**Output:** One markdown file per section in `books/{source}/chunks/{section_id}.md`

## Instructions

1. For each section in manifest.yaml, extract the corresponding PDF pages.
2. Write the full text to `chunks/{ch_section}.md` (e.g. `01_02.md`).
3. Include the header metadata from the manifest.
4. Preserve all tables as markdown tables.
5. Preserve all headings at their original levels.
6. Preserve page numbers as `<!-- page 69 -->` comments.
7. Preserve all references/citations in their original form.

## Output Format

```markdown
# Section {id}

**Book:** {title}, Edition {edition}
**Chapter:** {chapter_id}: {chapter_title}
**Section:** {section_id} — {section_title}
**Pages:** {start}–{end}

<!-- page {n} -->
{full text content}

## Tables

### Table {ref}: {title}
| col1 | col2 | ... |
|------|------|-----|
| ...  | ...  | ...  |

## Figures

### Figure {ref}: {caption}
[Figure content / description]
```

## Constraints

- Do NOT summarize.
- Do NOT remove repeated content.
- Do NOT rephrase definitions.
- Do NOT merge sections.
