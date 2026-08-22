from pathlib import Path

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# RESEARCH PAPERS
# ============================================================

RESEARCH_PAPERS_DIR = PROJECT_ROOT / "research_papers"


# ============================================================
# SAVED DATA
# ============================================================

SAVED_DIR = RESEARCH_PAPERS_DIR / "saved"


# ============================================================
# STAGE 1
# ============================================================

PAPER_INFO_DIR = SAVED_DIR / "paper_info"

MASTER_PAPERS_FILE = SAVED_DIR / "master_papers.json"


# ============================================================
# STAGE 2
# ============================================================

QUESTIONS_DIR = SAVED_DIR / "questions"


# ============================================================
# STAGE 3
# ============================================================

GAPS_DIR = SAVED_DIR / "gaps"


# ============================================================
# STAGE 4
# ============================================================

DOCUMENTS_DIR = SAVED_DIR / "documents"

PAPER_DOCUMENTS_DIR = DOCUMENTS_DIR / "paper_analysis"

QUESTION_DOCUMENTS_DIR = DOCUMENTS_DIR / "question_analysis"

GAP_DOCUMENTS_DIR = DOCUMENTS_DIR / "gap_analysis"


# ============================================================
# VECTOR DATABASE
# ============================================================

DATABASE_DIR = SAVED_DIR / "database"

VECTOR_DATABASE_DIR = DATABASE_DIR / "vector_database"


# ============================================================
# LOGS
# ============================================================

LOGS_DIR = SAVED_DIR / "logs"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

DIRECTORIES = [
    RESEARCH_PAPERS_DIR,
    SAVED_DIR,
    PAPER_INFO_DIR,
    QUESTIONS_DIR,
    GAPS_DIR,
    DOCUMENTS_DIR,
    PAPER_DOCUMENTS_DIR,
    QUESTION_DOCUMENTS_DIR,
    GAP_DOCUMENTS_DIR,
    DATABASE_DIR,
    VECTOR_DATABASE_DIR,
    LOGS_DIR,
]


def create_directories():
    """
    Create all project directories if they do not already exist.
    """

    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# DISPLAY CONFIGURATION
# ============================================================


def show_configuration():

    print()
    print("=" * 60)
    print("RESEARCH RAG CONFIGURATION")
    print("=" * 60)

    print(f"Project root       : {PROJECT_ROOT}")
    print(f"Research papers    : {RESEARCH_PAPERS_DIR}")
    print(f"Saved data         : {SAVED_DIR}")

    print()
    print("Stage 1")
    print(f"Paper information  : {PAPER_INFO_DIR}")
    print(f"Master index       : {MASTER_PAPERS_FILE}")

    print()
    print("Stage 2")
    print(f"Questions          : {QUESTIONS_DIR}")

    print()
    print("Stage 3")
    print(f"Gaps               : {GAPS_DIR}")

    print()
    print("Stage 4")
    print(f"Documents          : {DOCUMENTS_DIR}")

    print()
    print("Vector database")
    print(f"Database           : {VECTOR_DATABASE_DIR}")

    print("=" * 60)


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    create_directories()

    show_configuration()

    print()
    print("Project directories are ready.")
