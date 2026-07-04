"""Create full NSCA manifest and chunks for all chapters."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import PyPDF2, os, yaml

PDF = "books/nsca-cscs/source/NSCA-CSCS5th.pdf"
r = PyPDF2.PdfReader(PDF)

# Chapter structure (estimated from headers found)
CHAPTERS = [
    (1, "Structure and Function of Body Systems", 38, 103),
    (2, "Biomechanics of Resistance Exercise", 104, 173),
    (3, "Bioenergetics of Exercise and Training", 174, 226),
    (4, "Endocrine Responses to Resistance Exercise and Training", 227, 280),
    (5, "Adaptations to Anaerobic Training", 281, 340),
    (6, "Adaptations to Aerobic Training", 341, 383),
    (7, "Age-Related Differences and Their Implications for Resistance Training", 384, 437),
    (8, "Sex-Related Differences and Their Implications for Resistance Training", 438, 464),
    (9, "Psychological Foundations of Performance", 465, 535),
    (10, "Basic Nutritional Factors Affecting Health", 536, 612),
    (11, "Nutrition Strategies for Maximizing Performance", 613, 658),
    (12, "Performance-Enhancing Substances and Methods", 659, 728),
    (13, "Principles of Test Selection and Administration", 729, 763),
    (14, "Administration, Scoring, and Interpretation of Selected Tests", 764, 853),
    (15, "Performance Preparation, Mobility, and Flexibility", 854, 946),
    (16, "Exercise Technique for Free Weight and Machine Training", 947, 1087),
    (17, "Exercise Technique for Alternative Modes and Nontraditional Implement Training", 1088, 1185),
    (18, "Program Design for Resistance Training", 1186, 1259),
    (19, "Program Design and Technique for Plyometric Training", 1260, 1397),
    (20, "Program Design and Technique for Speed and Agility Training", 1398, 1511),
    (21, "Program Design and Technique for Aerobic Endurance and Metabolic Training", 1512, 1578),
    (22, "Periodization", 1579, 1678),
    (23, "Rehabilitation, Reconditioning, and Medical Issues", 1679, 1726),
    (24, "Overreaching, Overtraining, and Recovery", 1727, 1774),
    (25, "Facility Design, Layout, and Organization", 1775, 1830),
    (26, "Facility Policies, Procedures, and Legal Issues", 1831, 1876),
]

chunk_dir = "books/nsca-cscs/chunks"
os.makedirs(chunk_dir, exist_ok=True)

# Create manifest
manifest = {
    "book": {"title": "Essentials of Strength Training and Conditioning", "edition": 5, "total_pages": 1876},
    "chapters": []
}

for ch_id, title, start, end in CHAPTERS:
    ch_entry = {
        "id": ch_id,
        "title": title,
        "pdf_pages": {"start": start, "end": end},
        "sections": [
            {
                "id": f"{ch_id}.1",
                "title": title,
                "pdf_pages": {"start": start, "end": end},
                "estimated_complexity": 3,
                "estimated_tokens": (end - start + 1) * 500,
                "contains": {"definitions": "yes", "recommendations": "no", "procedures": "no", "tables": "yes", "figures": "yes", "thresholds": "no"},
                "status": "pending"
            }
        ]
    }
    manifest["chapters"].append(ch_entry)

    # Extract chunk text
    pages_text = []
    for p in range(start - 1, min(end, len(r.pages))):
        try:
            pages_text.append(r.pages[p].extract_text())
        except:
            pass
    content = "\n".join(pages_text)

    fid = f"{ch_id:02d}_01"
    with open(f"{chunk_dir}/{fid}.md", "w", encoding="utf-8") as f:
        f.write(f"# Section {ch_id}.1\n\n")
        f.write(f'**Book:** "Essentials of Strength Training and Conditioning", Edition 5\n\n')
        f.write(f"## Chapter {ch_id}: {title}\n\n")
        f.write(f"**Section:** {ch_id}.1\n\n")
        f.write(f"**PDF Pages:** {start}--{end}\n\n")
        f.write(content)
    print(f"Ch{ch_id}: {fid} ({len(content)} chars)")

# Save manifest
with open("books/nsca-cscs/manifest.yaml", "w", encoding="utf-8") as f:
    yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print(f"\nManifest saved: {len(CHAPTERS)} chapters")
