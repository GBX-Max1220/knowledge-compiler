"""Extract NSCA full chapter structure from PDF outline."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import PyPDF2, re

r = PyPDF2.PdfReader(r"books/nsca-cscs/source/NSCA-CSCS5th.pdf")
outlines = r.outline if hasattr(r, "outline") else []

def get_title(item):
    return item.title if hasattr(item, "title") else str(item)[:60]

for item in outlines:
    title = get_title(item)
    if not (title.startswith("Chapter") or "Appendix" in title or "Index" in title):
        continue
    
    # Count subsections
    subs = []
    if isinstance(item, list):
        subs = item
    elif hasattr(item, "children"):
        children = item.children
        if isinstance(children, list):
            subs = children
    elif hasattr(item, "_items"):
        subs = item._items
    
    print(f"  {title}")
    for s in subs[:10]:  # first 10 subsections
        st = get_title(s)
        print(f"    - {st}")
    if len(subs) > 10:
        print(f"    ... and {len(subs)-10} more")
