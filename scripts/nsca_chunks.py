"""Create NSCA chunk files for all 117 sections."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import yaml, os, PyPDF2

ROOT = "books/nsca-cscs"
PDF = f"{ROOT}/source/NSCA-CSCS5th.pdf"
CHUNK_DIR = f"{ROOT}/chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

m = yaml.safe_load(open(f"{ROOT}/manifest.yaml", encoding="utf-8"))
reader = PyPDF2.PdfReader(PDF)

count = 0
for ch in m["chapters"]:
    for sec in ch["sections"]:
        sid = sec["id"]
        parts = sid.split(".")
        fid = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
        start = sec["pdf_pages"]["start"]
        end = sec["pdf_pages"]["end"]
        title = sec["title"]
        
        # Extract text
        pages = []
        for p in range(start - 1, min(end, len(reader.pages))):
            try:
                pages.append(reader.pages[p].extract_text())
            except:
                pass
        
        content = "\n".join(pages)
        
        # Write chunk with header
        with open(f"{CHUNK_DIR}/{fid}.md", "w", encoding="utf-8") as f:
            f.write(f"# Section {sid}\n\n")
            f.write(f'**Book:** "Essentials of Strength Training and Conditioning", Edition 5\n\n')
            f.write(f"## Chapter {ch['id']}: {ch['title']}\n\n")
            f.write(f"**Section:** {sid} -- {title}\n\n")
            f.write(f"**PDF Pages:** {start}--{end}\n\n")
            f.write(content)
        
        count += 1
        if count % 20 == 0:
            print(f"  {count}/{sum(len(ch['sections']) for ch in m['chapters'])} chunks created...")

print(f"Done: {count} chunks created")
