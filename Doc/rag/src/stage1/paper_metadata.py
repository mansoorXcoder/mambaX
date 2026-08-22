from pathlib import Path
import hashlib
import json
import re

# ============================================================
# PATHS
# ============================================================

PROJECT_PATH = Path(r"D:\LE03\git\mambaX\Doc\rag")

RESEARCH_PAPERS_PATH = PROJECT_PATH / "research_paper_2"

SAVED_PATH = PROJECT_PATH / "research_papers" / "saved"

MASTER_FILE = SAVED_PATH / "master_papers.json"


# ============================================================
# FILE HASH
# ============================================================


def get_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# ============================================================
# CREATE PAPER ID
# ============================================================


def create_paper_id(file_hash):

    return "paper_" + file_hash[:12]


# ============================================================
# EXTRACT YEAR FROM FILENAME
# ============================================================


def extract_year(filename):

    match = re.search(r"\b(19|20)\d{2}\b", filename)

    if match:

        return int(match.group())

    return None


# ============================================================
# CLEAN TITLE FROM FILENAME
# ============================================================


def create_title(filename):

    title = Path(filename).stem

    title = title.replace("_", " ")

    title = title.replace("-", " ")

    title = re.sub(r"\s+", " ", title)

    return title.strip()


# ============================================================
# LOAD EXISTING MASTER FILE
# ============================================================


def load_master_file():

    if not MASTER_FILE.exists():

        return {"papers": []}

    with open(MASTER_FILE, "r", encoding="utf-8") as file:

        return json.load(file)


# ============================================================
# SAVE MASTER FILE
# ============================================================


def save_master_file(data):

    SAVED_PATH.mkdir(parents=True, exist_ok=True)

    with open(MASTER_FILE, "w", encoding="utf-8") as file:

        json.dump(data, file, indent=4, ensure_ascii=False)


# ============================================================
# PROCESS PAPERS
# ============================================================


def process_papers():

    master_data = load_master_file()

    existing_hashes = {paper.get("file_hash") for paper in master_data["papers"]}

    pdf_files = sorted(RESEARCH_PAPERS_PATH.glob("*.pdf"))

    new_count = 0

    for pdf_file in pdf_files:

        file_hash = get_file_hash(pdf_file)

        # --------------------------------------------
        # SKIP ALREADY PROCESSED PAPER
        # --------------------------------------------

        if file_hash in existing_hashes:

            continue

        # --------------------------------------------
        # CREATE BASIC INFORMATION
        # --------------------------------------------

        paper_id = create_paper_id(file_hash)

        title = create_title(pdf_file.name)

        year = extract_year(pdf_file.name)

        paper_data = {
            "paper_id": paper_id,
            "title": title,
            "authors": [],
            "year": year,
            "filename": pdf_file.name,
            "file_hash": file_hash,
        }

        master_data["papers"].append(paper_data)

        new_count += 1

        print(f"Added: {title}")

    # --------------------------------------------
    # SAVE
    # --------------------------------------------

    save_master_file(master_data)

    return new_count


# ============================================================
# MAIN
# ============================================================


def main():

    print()
    print("=" * 60)
    print("PAPER METADATA PROCESSOR")
    print("=" * 60)

    print()

    print(f"Source folder:\n{RESEARCH_PAPERS_PATH}")

    print()

    new_count = process_papers()

    print()
    print("-" * 60)

    print(f"New papers added: {new_count}")

    print()

    print(f"Master file:\n{MASTER_FILE}")

    print()
    print("=" * 60)


if __name__ == "__main__":

    main()
