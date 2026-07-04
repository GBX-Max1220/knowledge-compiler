"""Batch process NSCA Ch2-24: extract + generate for all chapters."""
import sys, os, time
sys.stdout.reconfigure(encoding="utf-8")
from openai import OpenAI

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

prompt_extract = open("prompts/02_extract.md", encoding="utf-8").read()
prompt_generate = open("prompts/03_object_generate.md", encoding="utf-8").read()

sections = [f"{c:02d}_01" for c in range(2, 25)]  # 02_01 through 24_01

total = len(sections)
for i, sec in enumerate(sections):
    print(f"[{i+1}/{total}] {sec}...", flush=True)

    chunk_path = f"books/nsca-cscs/chunks/{sec}.md"
    if not os.path.exists(chunk_path):
        print(f"  Chunk not found, skipping")
        continue

    chunk = open(chunk_path, encoding="utf-8").read()
    
    # Extract
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_extract}\n\n{chunk}"}],
            temperature=0.0)
        result = resp.choices[0].message.content
        result = result.replace("```yaml\n", "").replace("```\n", "").replace("```", "")
        open(f"books/nsca-cscs/extraction/{sec}.yaml", "w", encoding="utf-8").write(result)
        print(f"  Extract: {len(result)} chars", flush=True)
    except Exception as e:
        print(f"  Extract FAILED: {e}", flush=True)
        continue

    # Generate
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"{prompt_generate}\n\n{result}"}],
            temperature=0.0, max_tokens=8192)
        result2 = resp.choices[0].message.content
        result2 = result2.replace("```yaml\n", "").replace("```\n", "").replace("```", "")
        open(f"books/nsca-cscs/normalized/{sec}.yaml", "w", encoding="utf-8").write(result2)
        print(f"  Generate: {len(result2)} chars", flush=True)
    except Exception as e:
        print(f"  Generate FAILED: {e}", flush=True)

print(f"\nDone! Processed {total} sections")
