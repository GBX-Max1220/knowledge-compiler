"""
Cross-source analysis: ACSM vs NSCA alignment statistics.
Outputs merge report, conflict list, and ontology statistics.
"""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import yaml, os, json, glob
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "analysis")

def load_objects(book_path):
    """Load all objects from a book's objects/ directory."""
    objs = {}
    for fpath in glob.glob(os.path.join(book_path, "objects", "**", "*.yaml"), recursive=True):
        if fpath.endswith(("index.yaml", "registry.yaml")):
            continue
        try:
            doc = yaml.safe_load(open(fpath, encoding="utf-8"))
        except:
            continue
        if doc and doc.get("id"):
            objs[doc["id"]] = doc
    return objs

def get_defn_summary(doc):
    """Get a short summary of the definition for comparison."""
    defn = (doc.get("definition") or "").strip()
    return defn[:100].replace("\n", " ")

def count_rels(objs):
    """Count relationship predicate frequencies."""
    preds = Counter()
    for doc in objs.values():
        for rel in (doc.get("relationships") or []):
            preds[rel.get("predicate", "?")] += 1
    return preds

def count_types(objs):
    """Count object type and semantic_type frequencies."""
    types = Counter()
    semtypes = Counter()
    for doc in objs.values():
        types[doc.get("type", "?")] += 1
        semtypes[doc.get("semantic_type", "?")] += 1
    return types, semtypes

print("Loading ACSM objects...")
acsm = load_objects(os.path.join(ROOT, "sources", "books", "acsm12"))
if not acsm:
    acsm = load_objects(os.path.join(ROOT, "books", "acsm12"))
print(f"  {len(acsm)} objects")

print("Loading NSCA objects...")
nsca = load_objects(os.path.join(ROOT, "sources", "books", "nsca-cscs"))
if not nsca:
    nsca = load_objects(os.path.join(ROOT, "books", "nsca-cscs"))
print(f"  {len(nsca)} objects")

# ── Shared IDs ──────────────────────────────────────────────
acsm_ids = set(acsm.keys())
nsca_ids = set(nsca.keys())
shared_ids = acsm_ids & nsca_ids
only_acsm_ids = acsm_ids - nsca_ids
only_nsca_ids = nsca_ids - acsm_ids

# ── Conflict detection ──────────────────────────────────────
merged = []
conflicts = []
for oid in sorted(shared_ids):
    a = acsm[oid]
    n = nsca[oid]
    adef = get_defn_summary(a)
    ndef = get_defn_summary(n)
    atype = a.get("type")
    ntype = n.get("type")
    
    entry = {
        "id": oid,
        "type_acsm": atype,
        "type_nsca": ntype,
        "canonical_name": a.get("canonical_name", ""),
        "acsm_definition": adef,
        "nsca_definition": ndef,
        "status": "merged" if adef[:50] == ndef[:50] else "conflict",
    }
    
    if adef[:50] == ndef[:50]:
        merged.append(entry)
    else:
        conflicts.append(entry)

# ── Type distribution ───────────────────────────────────────
acsm_types, acsm_sems = count_types(acsm)
nsca_types, nsca_sems = count_types(nsca)
acsm_preds = count_rels(acsm)
nsca_preds = count_rels(nsca)

# All unique types and predicates
all_types = sorted(set(list(acsm_types.keys()) + list(nsca_types.keys())))
all_preds = sorted(set(list(acsm_preds.keys()) + list(nsca_preds.keys())))

# ── Save reports ────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Statistics JSON
stats = {
    "acsm_objects": len(acsm),
    "nsca_objects": len(nsca),
    "total_objects": len(acsm) + len(nsca),
    "shared_ids": len(shared_ids),
    "merged": len(merged),
    "conflicts": len(conflicts),
    "conflict_rate": round(len(conflicts) / max(len(shared_ids), 1) * 100, 1),
    "only_acsm": len(only_acsm_ids),
    "only_nsca": len(only_nsca_ids),
}
with open(os.path.join(OUT_DIR, "alignment_statistics.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)
print(f"\nStatistics: {json.dumps(stats, indent=2)}")

# 2. Conflicts JSON
with open(os.path.join(OUT_DIR, "conflicts.json"), "w", encoding="utf-8") as f:
    json.dump(conflicts, f, indent=2, ensure_ascii=False)
print(f"Conflicts: {len(conflicts)}")

# 3. Merge report (markdown)
md = []
md.append("# Cross-Source Alignment Report")
md.append(f"\n> Generated: automatic")
md.append(f"> ACSM: {len(acsm)} objects | NSCA: {len(nsca)} objects")
md.append("")
md.append("## Summary")
md.append("")
md.append("| Metric | Value |")
md.append("|--------|------:|")
md.append(f"| Total ACSM objects | {len(acsm)} |")
md.append(f"| Total NSCA objects | {len(nsca)} |")
md.append(f"| Combined (pre-merge) | {len(acsm) + len(nsca)} |")
md.append(f"| Shared IDs | {len(shared_ids)} |")
md.append(f"| Merged (compatible) | {len(merged)} |")
md.append(f"| Conflicts | {len(conflicts)} |")
md.append(f"| Conflict rate | {stats['conflict_rate']}% |")
md.append(f"| Unique to ACSM | {len(only_acsm_ids)} |")
md.append(f"| Unique to NSCA | {len(only_nsca_ids)} |")
md.append(f"| Post-merge total | {len(merged) + len(only_acsm_ids) + len(only_nsca_ids)} |")
md.append("")

# Schema type comparison
md.append("## Schema Type Distribution")
md.append("")
md.append("| Type | ACSM | NSCA | Total |")
md.append("|------|:----:|:----:|:----:|")
for t in all_types:
    a = acsm_types.get(t, 0)
    n = nsca_types.get(t, 0)
    md.append(f"| {t} | {a} | {n} | {a+n} |")
md.append(f"| **Total** | {len(acsm)} | {len(nsca)} | {len(acsm)+len(nsca)} |")
md.append("")

# Semantic type distribution
md.append("## Semantic Type Distribution")
md.append("")
all_sems = sorted(set([str(s) for s in list(acsm_sems.keys()) + list(nsca_sems.keys())]))
md.append("| Semantic Type | ACSM | NSCA | Total |")
md.append("|--------------|:----:|:----:|:----:|")
for s in all_sems:
    a = acsm_sems.get(s, 0)
    n = nsca_sems.get(s, 0)
    md.append(f"| {s} | {a} | {n} | {a+n} |")
md.append("")

# Relationship predicate distribution
md.append("## Relationship Predicate Distribution")
md.append("")
md.append("| Predicate | ACSM | NSCA | Total |")
md.append("|----------|:----:|:----:|:----:|")
for p in all_preds:
    a = acsm_preds.get(p, 0)
    n = nsca_preds.get(p, 0)
    md.append(f"| {p} | {a} | {n} | {a+n} |")
md.append("")

# Conflict details
if conflicts:
    md.append("\n## Conflict Details")
    md.append("")
    md.append("Objects with the same ID but different definitions across books:")
    md.append("")
    md.append("| ID | ACSM Definition | NSCA Definition |")
    md.append("|----|----------------|----------------|")
    for c in conflicts[:20]:
        md.append(f"| {c['id']} | {c['acsm_definition'][:80]} | {c['nsca_definition'][:80]} |")
    if len(conflicts) > 20:
        md.append(f"\n... and {len(conflicts)-20} more")

# Shared examples
if merged:
    md.append("\n## Shared Concepts (Sample)")
    md.append("")
    md.append("IDs that appear in both books with compatible definitions:")
    md.append("")
    for m in merged[:15]:
        md.append(f"- `{m['id']}` ({m['canonical_name']})")
    if len(merged) > 15:
        md.append(f"\n... and {len(merged)-15} more")

with open(os.path.join(OUT_DIR, "merge_report.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Merge report written: {OUT_DIR}/merge_report.md")
print(f"Conflicts: {OUT_DIR}/conflicts.json")
