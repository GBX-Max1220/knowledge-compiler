"""Build NSCA full book manifest and chunks for all 24 chapters."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import PyPDF2, os, re

PDF = "books/nsca-cscs/source/NSCA-CSCS5th.pdf"
reader = PyPDF2.PdfReader(PDF)
total_pages = len(reader.pages)

# Chapter titles and page ranges (from earlier analysis)
chapters = [
    (1, "Structure and Function of Body Systems", 38, 103),
    (2, "Biomechanics of Resistance Exercise", 104, 173),
    (3, "Bioenergetics of Exercise and Training", 174, 230),
    (4, "Endocrine Responses to Resistance Exercise and Training", 231, 280),
    (5, "Adaptations to Anaerobic Training", 281, 340),
    (6, "Adaptations to Aerobic Training", 341, 383),
    (7, "Age-Related Differences and Their Implications for Resistance Training", 384, 437),
    (8, "Sex-Related Differences and Their Implications for Resistance Training", 438, 464),
    (9, "Psychological Foundations of Performance", 465, 535),
    (10, "Basic Nutritional Factors Affecting Health", 536, 612),
    (11, "Nutrition Strategies for Maximizing Performance", 613, 658),
    (12, "Performance-Enhancing Substances and Methods", 659, 720),
    (13, "Principles of Test Selection and Administration", 721, 763),
    (14, "Administration, Scoring, and Interpretation of Selected Tests", 764, 853),
    (15, "Performance Preparation, Mobility, and Flexibility", 854, 946),
    (16, "Exercise Technique for Free Weight and Machine Training", 947, 1050),
    (17, "Exercise Technique for Alternative Modes and Nontraditional Implement Training", 1051, 1185),
    (18, "Program Design for Resistance Training", 1186, 1259),
    (19, "Program Design and Technique for Plyometric Training", 1260, 1340),
    (20, "Program Design and Technique for Speed and Agility Training", 1341, 1511),
    (21, "Program Design and Technique for Aerobic Endurance and Metabolic Training", 1512, 1578),
    (22, "Periodization", 1579, 1678),
    (23, "Rehabilitation, Reconditioning, and Medical Issues", 1679, 1726),
    (24, "Overreaching, Overtraining, and Recovery", 1727, 1776),
]

# Create manifest
lines = []
lines.append("book:")
lines.append(f'  title: "Essentials of Strength Training and Conditioning"')
lines.append(f"  edition: 5")
lines.append(f"  total_pages: {total_pages}")
lines.append("")
lines.append("chapters:")

for ch_num, ch_title, ch_start, ch_end in chapters:
    lines.append(f"- id: {ch_num}")
    lines.append(f'  title: "{ch_title}"')
    lines.append(f"  pdf_pages:")
    lines.append(f"    start: {ch_start}")
    lines.append(f"    end: {ch_end}")
    lines.append(f"  sections:")
    lines.append(f'    - id: "{ch_num}.1"')
    lines.append(f'      title: "{ch_title} (full chapter)"')
    lines.append(f"      pdf_pages:")
    lines.append(f"        start: {ch_start}")
    lines.append(f"        end: {ch_end}")
    lines.append(f"      estimated_complexity: 4")
    lines.append(f"      estimated_tokens: {((ch_end - ch_start + 1) * 500)}")
    lines.append(f"      contains:")
    lines.append(f'        definitions: yes')
    lines.append(f'        recommendations: {"yes" if ch_num >= 18 else "no"}')
    lines.append(f'        procedures: {"yes" if ch_num >= 13 else "no"}')
    lines.append(f'        tables: yes')
    lines.append(f'        figures: yes')
    lines.append(f'        thresholds: {"yes" if ch_num >= 3 else "no"}')
    lines.append(f"      status: pending")

manifest = "\n".join(lines)
with open("books/nsca-cscs/manifest.yaml", "w", encoding="utf-8") as f:
    f.write(manifest)
print(f"Manifest written: {len(chapters)} chapters")

# Create chunks (one per chapter)
chunk_dir = "books/nsca-cscs/chunks"
extraction_dir = "books/nsca-cscs/extraction"
normalized_dir = "books/nsca-cscs/normalized"
os.makedirs(chunk_dir, exist_ok=True)
os.makedirs(extraction_dir, exist_ok=True)
os.makedirs(normalized_dir, exist_ok=True)

# Keep existing Ch1 chunks (01_01, 01_02, 01_03)
existing_chunks = {"01_01", "01_02", "01_03"}

# Remove old pilot-only chunks
for f in os.listdir(chunk_dir):
    if f.endswith(".md") and f.replace(".md","") not in existing_chunks:
        os.remove(os.path.join(chunk_dir, f))

total_chars = 0
for ch_num, ch_title, ch_start, ch_end in chapters:
    if ch_num == 1:
        print(f"  Ch{ch_num}: keeping existing chunks")
        continue
    
    pages = []
    for p in range(ch_start - 1, min(ch_end, total_pages)):
        try:
            text = reader.pages[p].extract_text()
            pages.append(text)
        except:
            pass
    
    content = "\n".join(pages)
    file_id = f"{ch_num:02d}_01"
    fpath = os.path.join(chunk_dir, f"{file_id}.md")
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(f"# Chapter {ch_num}: {ch_title}\n\n")
        f.write(f'**Book:** "Essentials of Strength Training and Conditioning", Edition 5\n\n')
        f.write(f"**PDF Pages:** {ch_start}--{ch_end}\n\n")
        f.write(content)
    
    total_chars += len(content)
    print(f"  Ch{ch_num} ({file_id}): {len(content)} chars, pages {ch_start}-{ch_end}")

print(f"\nTotal: {len(chapters)} chapters, {total_chars} chars")
print(f"Previously processed: Ch1 (01_01, 01_02, 01_03)")
print(f"New chunks: {len(chapters) - 1} (01_01 kept, 01_02 kept, 01_03 kept)")
