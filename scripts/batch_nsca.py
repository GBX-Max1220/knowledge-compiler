"""Batch process remaining NSCA chunks."""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8")
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

pending = ["02_02", "11_01", "12_01", "13_01", "14_01", "15_01", "16_01",
           "17_01", "18_01", "19_01", "20_01", "21_01", "22_01", "23_01",
           "24_01", "25_01", "26_01"]

total = len(pending)
for i, sec in enumerate(pending):
    chunk_path = f"books/nsca-cscs/chunks/{sec}.md"
    if not os.path.exists(chunk_path):
        print(f"[{i+1}/{total}] {sec}: no chunk, skip")
        continue

    chunk = open(chunk_path, encoding="utf-8").read()
    sz = len(chunk)
    print(f"[{i+1}/{total}] {sec}: {sz} chars...", end="", flush=True)

    # Extract
    prompt_e = open("prompts/02_extract.md", encoding="utf-8").read()
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_e}\n\n{chunk}"}],
            temperature=0.0)
        ext = resp.choices[0].message.content
        open(f"books/nsca-cscs/extraction/{sec}.yaml", "w", encoding="utf-8").write(ext)
        print(f" E{len(ext)}", end="", flush=True)
    except Exception as e:
        print(f" EXTRACT FAIL: {e}")
        continue

    # Generate
    prompt_g = open("prompts/03_object_generate.md", encoding="utf-8").read()
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_g}\n\n{ext}"}],
            temperature=0.0, max_tokens=4096)
        gen = resp.choices[0].message.content
        lines = gen.split("\n")
        gen = "\n".join(l for l in lines if not l.strip().startswith("```"))
        open(f"books/nsca-cscs/normalized/{sec}.yaml", "w", encoding="utf-8").write(gen)
        print(f" G{len(gen)}", flush=True)
    except Exception as e:
        print(f" GENERATE FAIL: {e}")

print(f"\nDone! Processed {total} sections")
