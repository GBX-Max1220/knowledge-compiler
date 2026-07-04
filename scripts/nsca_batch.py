"""Batch NSCA: extraction + generation for all sections."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import yaml, os, time
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

m = yaml.safe_load(open("books/nsca-cscs/manifest.yaml", encoding="utf-8"))

total = 0
for ch in m["chapters"]:
    for sec in ch["sections"]:
        sid = sec["id"]
        parts = sid.split(".")
        fid = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
        total += 1

done = 0
for ch in m["chapters"]:
    for sec in ch["sections"]:
        sid = sec["id"]
        parts = sid.split(".")
        fid = f"{int(parts[0]):02d}_{int(parts[1]):02d}"
        
        # Skip if already done
        norm_path = f"books/nsca-cscs/normalized/{fid}.yaml"
        if os.path.exists(norm_path) and os.path.getsize(norm_path) > 100:
            done += 1
            continue
        
        chunk_path = f"books/nsca-cscs/chunks/{fid}.md"
        if not os.path.exists(chunk_path):
            open(norm_path, "w").write("")
            done += 1
            continue
        
        chunk = open(chunk_path, encoding="utf-8").read()
        if len(chunk) < 50:
            open(norm_path, "w").write("")
            done += 1
            continue
        
        # Extraction
        prompt_e = open("prompts/02_extract.md", encoding="utf-8").read()
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": f"{prompt_e}\n\n{chunk}"}],
                temperature=0.0)
            ext = resp.choices[0].message.content
            os.makedirs("books/nsca-cscs/extraction", exist_ok=True)
            open(f"books/nsca-cscs/extraction/{fid}.yaml", "w", encoding="utf-8").write(ext)
        except Exception as e:
            print(f"  EXTRACT FAIL {fid}: {e}")
            continue
        
        # Generation
        prompt_g = open("prompts/03_object_generate.md", encoding="utf-8").read()
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": f"{prompt_g}\n\n{ext}"}],
                temperature=0.0, max_tokens=4096)
            gen = resp.choices[0].message.content
            gen = gen.replace("```yaml\n", "").replace("```\n", "").replace("```", "")
            os.makedirs("books/nsca-cscs/normalized", exist_ok=True)
            open(norm_path, "w", encoding="utf-8").write(gen)
        except Exception as e:
            print(f"  GEN FAIL {fid}: {e}")
            continue
        
        done += 1
        print(f"[{done}/{total}] {fid}: {len(gen)} chars")
        time.sleep(0.2)

print(f"\nDone! Processed {done}/{total} sections")
