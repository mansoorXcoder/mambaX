from pathlib import Path
import hashlib
import json
import re

import pymupdf


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

PAPERS_DIR = ROOT / "research_paper_2"
MASTER_FILE = ROOT / "research_papers" / "saved" / "master_papers.json"


# ============================================================
# HELPERS
# ============================================================

def clean(text):
    """Normalize whitespace."""
    return re.sub(r"\s+", " ", text or "").strip()


def file_hash(path):
    """Return SHA-256 hash of a file."""
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def load_master():
    """Load the master paper database."""
    if not MASTER_FILE.exists():
        return {"papers": []}

    return json.loads(
        MASTER_FILE.read_text(encoding="utf-8")
    )


def save_master(data):
    """Save the master paper database."""
    MASTER_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    MASTER_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def first_page(path):
    """Extract text blocks from the first PDF page."""
    with pymupdf.open(path) as doc:
        if len(doc) == 0:
            return []

        blocks = doc[0].get_text("blocks")

    result = []

    for block in blocks:
        text = clean(block[4])

        if not text:
            continue

        result.append({
            "text": text,
            "size": block[3] - block[1],
            "x0": block[0],
            "y0": block[1],
        })

    return result


# ============================================================
# TITLE EXTRACTION
# ============================================================

def extract_title(blocks, filename):
    """Extract a likely paper title from first-page blocks."""

    filename_title = clean(
        Path(filename).stem
        .replace("_", " ")
        .replace("-", " ")
    )

    bad_words = (
        "copyright",
        "issn",
        "journal",
        "received",
        "accepted",
        "published",
        "doi",
        "abstract",
        "department",
        "university",
        "keywords",
    )

    candidates = []

    for block in blocks:
        text = block["text"]
        lower = text.lower()

        # Ignore very short lines.
        if len(text.split()) < 4:
            continue

        # Ignore extremely long blocks.
        if len(text) > 220:
            continue

        # Ignore obvious metadata.
        if any(word in lower for word in bad_words):
            continue

        candidates.append(block)

    if not candidates:
        return filename_title

    # Larger text is generally more likely to be the title.
    # Length is used as a secondary signal.
    best = max(
        candidates,
        key=lambda block: (
            block["size"],
            len(block["text"])
        )
    )

    return best["text"]


# ============================================================
# AUTHOR EXTRACTION
# ============================================================

def extract_authors(blocks, title):
    """Extract likely authors appearing after the title."""

    title_found = False

    for block in blocks:
        text = block["text"]

        if text == title:
            title_found = True
            continue

        if not title_found:
            continue

        lower = text.lower()

        # Stop/skip common metadata.
        if any(
            word in lower
            for word in (
                "abstract",
                "keywords",
                "copyright",
                "doi",
                "department",
                "university",
                "received",
                "accepted",
            )
        ):
            continue

        # Typical academic author line.
        if not re.search(
            r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",
            text
        ):
            continue

        names = re.split(
            r",|;|\band\b",
            text,
            flags=re.IGNORECASE
        )

        names = [
            clean(name)
            for name in names
            if clean(name)
        ]

        if 1 <= len(names) <= 10:
            return names

    return []


# ============================================================
# YEAR EXTRACTION
# ============================================================

def extract_year(blocks):
    """Extract publication year from first-page text."""

    # Prefer years explicitly associated with publication metadata.
    for block in blocks:
        match = re.search(
            r"(?:published|publication|copyright|©)"
            r"\D{0,40}"
            r"(20\d{2})",
            block["text"],
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    # Fall back to any plausible year.
    for block in blocks:
        match = re.search(
            r"\b(19\d{2}|20\d{2})\b",
            block["text"]
        )

        if match:
            return int(match.group(1))

    return None


# ============================================================
# PAPER PROCESSING
# ============================================================

def process_pdf(pdf, existing, hash_map):
    """Extract metadata and update the master record."""

    current_hash = file_hash(pdf)

    # --------------------------------------------------------
    # Existing unchanged paper
    # --------------------------------------------------------

    existing_paper = existing.get(pdf.name)

    if (
        existing_paper
        and existing_paper.get("metadata_version") == 2
        and existing_paper.get("file_hash") == current_hash
    ):
        return {
            "status": "skipped",
            "paper": existing_paper,
        }

    # --------------------------------------------------------
    # Read PDF
    # --------------------------------------------------------

    blocks = first_page(pdf)

    title = extract_title(
        blocks,
        pdf.name
    )

    authors = extract_authors(
        blocks,
        title
    )

    year = extract_year(
        blocks
    )

    # --------------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------------

    duplicate_of = None

    if current_hash in hash_map:
        duplicate_paper = hash_map[current_hash]

        # Do not mark the same paper as a duplicate of itself.
        if duplicate_paper.get("filename") != pdf.name:
            duplicate_of = duplicate_paper.get("paper_id")

    # --------------------------------------------------------
    # Create or update paper
    # --------------------------------------------------------

    paper = existing_paper

    if paper is None:
        paper = {
            "paper_id": f"paper_{current_hash[:12]}",
            "filename": pdf.name,
        }

        existing[pdf.name] = paper

    paper.update({
        "title": title,
        "authors": authors,
        "year": year,
        "file_hash": current_hash,
        "duplicate_of": duplicate_of,
        "metadata_version": 2,
    })

    hash_map[current_hash] = paper

    return {
        "status": "updated",
        "paper": paper,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    data = load_master()

    papers = data.setdefault(
        "papers",
        []
    )

    # --------------------------------------------------------
    # Build lookup maps
    # --------------------------------------------------------

    existing = {
        paper.get("filename"): paper
        for paper in papers
        if paper.get("filename")
    }

    hash_map = {
        paper.get("file_hash"): paper
        for paper in papers
        if paper.get("file_hash")
    }

    # --------------------------------------------------------
    # Find PDFs
    # --------------------------------------------------------

    pdfs = sorted(
        PAPERS_DIR.glob("*.pdf")
    )

    print()
    print("=" * 70)
    print("METADATA EXTRACTION")
    print("=" * 70)

    print(f"\nPDF directory : {PAPERS_DIR}")
    print(f"Master file   : {MASTER_FILE}")
    print(f"PDFs found    : {len(pdfs)}")

    if not pdfs:
        print("\nNo PDF files found.")
        return

    # --------------------------------------------------------
    # Process PDFs
    # --------------------------------------------------------

    processed = 0
    skipped = 0
    duplicates = 0

    for pdf in pdfs:

        try:
            result = process_pdf(
                pdf,
                existing,
                hash_map
            )

        except Exception as exc:
            print(f"\n✗ {pdf.name}")
            print(f"  ERROR: {exc}")
            continue

        # ----------------------------------------------------
        # Unchanged
        # ----------------------------------------------------

        if result["status"] == "skipped":
            skipped += 1

            print(f"\n→ {pdf.name}")
            print("  Unchanged — skipped")

            continue

        # ----------------------------------------------------
        # Updated
        # ----------------------------------------------------

        processed += 1

        paper = result["paper"]

        print(f"\n✓ {pdf.name}")
        print(f"  ID      : {paper['paper_id']}")
        print(f"  Title   : {paper['title']}")
        print(f"  Authors : {paper['authors'] or 'N/A'}")
        print(f"  Year    : {paper['year'] or 'N/A'}")

        if paper.get("duplicate_of"):
            duplicates += 1
            print(
                f"  DUPLICATE OF: "
                f"{paper['duplicate_of']}"
            )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_master(data)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Total PDFs       : {len(pdfs)}")
    print(f"Processed        : {processed}")
    print(f"Skipped          : {skipped}")
    print(f"Duplicates       : {duplicates}")
    print(f"Total master     : {len(papers)}")

    print()
    print(f"Saved: {MASTER_FILE}")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()