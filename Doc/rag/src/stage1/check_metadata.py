from pathlib import Path
import json
from collections import defaultdict

# ============================================================
# CONFIG
# ============================================================

MASTER_FILE = (
    Path(__file__).resolve().parents[2]
    / "research_papers"
    / "saved"
    / "master_papers.json"
)


# ============================================================
# LOAD
# ============================================================

with MASTER_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)


papers = data.get("papers", [])


# ============================================================
# DISPLAY
# ============================================================

print()
print("=" * 80)
print("RESEARCH PAPER METADATA")
print("=" * 80)

print(f"\nTotal papers: {len(papers)}")


for number, paper in enumerate(papers, 1):

    authors = paper.get("authors") or []

    if isinstance(authors, list):
        authors = ", ".join(authors)

    print()
    print(f"[{number}] {paper.get('title', 'N/A')}")
    print("-" * 80)

    print(f"Paper ID : {paper.get('paper_id', 'N/A')}")
    print(f"Authors  : {authors or 'N/A'}")
    print(f"Year     : {paper.get('year', 'N/A')}")
    print(f"File     : {paper.get('filename', 'N/A')}")


# ============================================================
# DUPLICATE CHECK
# ============================================================

hash_groups = defaultdict(list)

for paper in papers:

    file_hash = paper.get("file_hash")

    if file_hash:
        hash_groups[file_hash].append(paper.get("filename"))


duplicates = [files for files in hash_groups.values() if len(files) > 1]


print()
print("=" * 80)
print("DUPLICATE PAPERS")
print("=" * 80)

if duplicates:

    for group in duplicates:

        print()

        for filename in group:
            print(f"  • {filename}")

else:

    print("\nNo duplicate PDF contents found.")


print()
print("=" * 80)
print(f"Master file: {MASTER_FILE}")
print("=" * 80)
