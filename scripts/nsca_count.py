"""Count NSCA manifest sections."""
import yaml
m = yaml.safe_load(open("books/nsca-cscs/manifest.yaml", encoding="utf-8"))
total = sum(len(ch["sections"]) for ch in m["chapters"])
print(f"Total chapters: {len(m['chapters'])}")
print(f"Total sections: {total}")
