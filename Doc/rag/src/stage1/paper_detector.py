from pathlib import Path
import hashlib
import json

# ============================================================
# CHANGE ONLY THIS PATH
# ============================================================

RESEARCH_PAPERS_PATH = r"D:\LE03\git\mambaX\Doc\rag\research_paper_2"


# ============================================================
# SAVED DATA
# ============================================================

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent

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
# LOAD MASTER FILE
# ============================================================


def load_master_file():

    if not MASTER_FILE.exists():

        return {"papers": []}

    with open(MASTER_FILE, "r", encoding="utf-8") as file:

        return json.load(file)


# ============================================================
# FIND PDF FILES
# ============================================================


def find_papers():

    folder = Path(RESEARCH_PAPERS_PATH)

    if not folder.exists():

        print()
        print("ERROR:")
        print("Research paper folder does not exist.")
        print()
        print("Current path:")
        print(folder)

        return []

    pdf_files = list(folder.glob("*.pdf"))

    return sorted(pdf_files)


# ============================================================
# DETECT NEW PAPERS
# ============================================================


def detect_new_papers():

    master_data = load_master_file()

    processed_hashes = {
        paper.get("file_hash") for paper in master_data.get("papers", [])
    }

    pdf_files = find_papers()

    new_papers = []

    for pdf_file in pdf_files:

        file_hash = get_file_hash(pdf_file)

        if file_hash not in processed_hashes:

            new_papers.append(
                {
                    "filename": pdf_file.name,
                    "path": str(pdf_file),
                    "file_hash": file_hash,
                }
            )

    return new_papers


# ============================================================
# MAIN
# ============================================================


def main():

    print()
    print("=" * 60)
    print("RESEARCH PAPER DETECTOR")
    print("=" * 60)

    print()
    print("Research papers folder:")
    print(RESEARCH_PAPERS_PATH)

    new_papers = detect_new_papers()

    print()
    print(f"New papers found: {len(new_papers)}")

    if new_papers:

        print()
        print("NEW PAPERS")
        print("-" * 60)

        for number, paper in enumerate(new_papers, start=1):

            print(f"{number}. {paper['filename']}")

    else:

        print()
        print("No new papers found.")

    print()
    print("=" * 60)


if __name__ == "__main__":

    main()
