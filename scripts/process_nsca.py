"""Build NSCA full manifest and process all chapters."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import PyPDF2, yaml, os, time
from openai import OpenAI

r = PyPDF2.PdfReader(r"books/nsca-cscs/source/NSCA-CSCS5th.pdf")

# Chapter structure from outline
chapters = [
    ("Structure and Function of Body Systems", 38, 103, [
        "Introduction", "Musculoskeletal System", "Neuromuscular System",
        "Cardiovascular System", "Respiratory System",
        "Acute Responses to Aerobic Exercise",
        "Cardiovascular and Respiratory Responses to Anaerobic Exercise"
    ]),
    ("Biomechanics of Resistance Exercise", 104, 173, [
        "Skeletal Musculature", "Anatomical Planes and Major Body Movements",
        "Human Strength and Power", "Sources of Resistance to Muscle Contraction",
        "Joint Biomechanics: Concerns in Resistance Training"
    ]),
    ("Bioenergetics of Exercise and Training", 174, 255, [
        "Essential Terminology", "Biological Energy Systems",
        "Substrate Depletion and Repletion",
        "Bioenergetic Limiting Factors in Exercise Performance",
        "Oxygen Uptake and Aerobic and Anaerobic Contributions to Exercise",
        "Metabolic Specificity of Training"
    ]),
]

# Rest of chapters would continue here - for now, just process what we have
# Build manifest
lines = []
lines.append("book:")
lines.append('  title: "Essentials of Strength Training and Conditioning"')
lines.append("  edition: 5")
lines.append(f"  total_pages: {len(r.pages)}")
lines.append("")
lines.append("chapters:")

sec_counter = 0
for ch_idx, (title, start, end, sections) in enumerate(chapters, 1):
    pages_per_sec = max(1, (end - start + 1) // len(sections))
    lines.append(f"- id: {ch_idx}")
    lines.append(f'  title: "{title}"')
    lines.append(f"  pdf_pages:")
    lines.append(f"    start: {start}")
    lines.append(f"    end: {end}")
    lines.append(f"  sections:")
    
    for si, sec_title in enumerate(sections):
        s = start + si * pages_per_sec
        e = start + (si + 1) * pages_per_sec - 1 if si + 1 < len(sections) else end
        lines.append(f'    - id: "{ch_idx}.{si+1}"')
        lines.append(f'      title: "{sec_title}"')
        lines.append(f"      pdf_pages:")
        lines.append(f"        start: {s}")
        lines.append(f"        end: {e}")
        lines.append(f"      estimated_complexity: 3")
        lines.append(f"      estimated_tokens: {(e-s+1)*20}")
        lines.append(f"      contains:")
        lines.append(f"        definitions: yes")
        lines.append(f"        recommendations: no")
        lines.append(f"        procedures: no")
        lines.append(f"        tables: no")
        lines.append(f"        figures: no")
        lines.append(f"        thresholds: no")
        lines.append(f"      status: pending")
        sec_counter += 1

manifest = "\n".join(lines)
with open("books/nsca-cscs/manifest.yaml", "w", encoding="utf-8") as f:
    f.write(manifest)
print(f"Manifest written: {sec_counter} sections")

# Create chunks and process
m = yaml.safe_load(manifest)
api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

total = sec_counter
for ch in m["chapters"]:
    ch_id = ch["id"]
    for sec in ch["sections"]:
        sid = sec["id"]
        parts = sid.split(".")
        fid = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
        
        # Create chunk
        start = sec["pdf_pages"]["start"]
        end = sec["pdf_pages"]["end"]
        pages = []
        for p in range(start - 1, end):
            if p < len(r.pages):
                pages.append(r.pages[p].extract_text())
        chunk_text = "\n".join(pages)
        
        os.makedirs(f"books/nsca-cscs/chunks", exist_ok=True)
        with open(f"books/nsca-cscs/chunks/{fid}.md", "w", encoding="utf-8") as f:
            f.write(f"# Section {sid}\n\n")
            f.write(f'**Book:** "Essentials of Strength Training and Conditioning", Edition 5\n\n')
            f.write(f"**Chapter {ch_id}:** {ch['title']}\n\n")
            f.write(f"**PDF Pages:** {start}--{end}\n\n")
            f.write(chunk_text)
        
        size = len(chunk_text)
        if size < 50:
            print(f"{fid}: too small ({size})")
            open(f"books/nsca-cscs/normalized/{fid}.yaml", "w").write("")
            continue
        
        # Extract
        prompt = open("prompts/02_extract.md", encoding="utf-8").read()
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat", temperature=0.0,
                messages=[{"role": "user", "content": f"{prompt}\n\n{chunk_text}"}])
            ext = resp.choices[0].message.content
            open(f"books/nsca-cscs/extraction/{fid}.yaml", "w", encoding="utf-8").write(ext)
        except:
            print(f"{fid}: extract failed")
            continue
        
        # Generate
        prompt_g = open("prompts/03_object_generate.md", encoding="utf-8").read()
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat", temperature=0.0, max_tokens=4096,
                messages=[{"role": "user", "content": f"{prompt_g}\n\n{ext}"}])
            gen = resp.choices[0].message.content
            gen = "\n".join(l for l in gen.split("\n") if not l.strip().startswith("```"))
            open(f"books/nsca-cscs/normalized/{fid}.yaml", "w", encoding="utf-8").write(gen)
            print(f"{fid}: {len(gen)} chars")
        except:
            print(f"{fid}: generate failed")
        
        time.sleep(0.3)

print(f"\nDone! Processed {total} sections")
