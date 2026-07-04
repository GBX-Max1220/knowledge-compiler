"""Batch process NSCA full book via DeepSeek."""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8")
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

prompt_extract = open("prompts/02_extract.md", encoding="utf-8").read()
prompt_gen = open("prompts/03_object_generate.md", encoding="utf-8").read()

total = 26
for ch in range(1, 27):
    fid = f"{ch:02d}_01"
    print(f"\n[{ch}/{total}] Ch{ch} ({fid})")

    # Skip if already processed
    norm_path = f"books/nsca-cscs/normalized/{fid}.yaml"
    if os.path.exists(norm_path):
        with open(norm_path, encoding="utf-8") as f:
            if f.read().strip():
                print(f"  Already done, skipping")
                continue

    chunk = open(f"books/nsca-cscs/chunks/{fid}.md", encoding="utf-8").read()
    print(f"  Chunk: {len(chunk)} chars")

    # Extract
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_extract}\n\n{chunk}"}],
            temperature=0.0)
        ext = resp.choices[0].message.content
        open(f"books/nsca-cscs/extraction/{fid}.yaml", "w", encoding="utf-8").write(ext)
        print(f"  Extract: {len(ext)} chars")
    except Exception as e:
        print(f"  Extract FAIL: {e}")
        continue

    # Generate
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_gen}\n\n{ext}"}],
            temperature=0.0, max_tokens=8192)
        gen = resp.choices[0].message.content
        lines = gen.split("\n")
        gen = "\n".join(l for l in lines if not l.strip().startswith("```"))
        open(norm_path, "w", encoding="utf-8").write(gen)
        print(f"  Generate: {len(gen)} chars")
    except Exception as e:
        print(f"  Generate FAIL: {e}")

    time.sleep(0.5)

print(f"\nDone! All {total} chapters processed")
