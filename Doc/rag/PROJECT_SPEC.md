# Local Research Paper RAG System

## 1. Purpose

Build a completely local research-paper analysis system that can:

1. Store a collection of research papers.
2. Maintain one lightweight master index of all papers.
3. Automatically process only newly added papers.
4. Store detailed analysis of each paper separately.
5. Answer questions using the existing paper knowledge base.
6. Identify research gaps when the user explicitly triggers gap analysis.
7. Avoid repeatedly analyzing old papers.
8. Save all generated information as JSON and DOCX.
9. Keep all generated files inside the `research_papers/saved/` folder.

The system must be designed to minimize unnecessary LLM computation.

---

# 2. Core Design Principle

## DO NOT re-analyze all papers every time.

Once a paper has been analyzed, its extracted information must be stored.

When a new paper is added:

```text
New PDF
   ↓
Detect new paper
   ↓
Analyze ONLY new paper
   ↓
Save its information
   ↓
Update master paper index
```

Existing papers must not be processed again unless explicitly requested.

---

# 3. Project Structure

```text
research_rag/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── .env
│
├── research_papers/
│   │
│   ├── paper_001.pdf
│   ├── paper_002.pdf
│   ├── paper_003.pdf
│   ├── paper_004.pdf
│   │
│   └── saved/
│       │
│       ├── master_papers.json
│       │
│       ├── paper_info/
│       │   ├── paper_001.json
│       │   ├── paper_002.json
│       │   └── paper_003.json
│       │
│       ├── questions/
│       │   ├── question_001.json
│       │   └── question_002.json
│       │
│       ├── gaps/
│       │   ├── gap_analysis_001.json
│       │   └── gap_analysis_002.json
│       │
│       ├── documents/
│       │   │
│       │   ├── paper_analysis/
│       │   ├── question_analysis/
│       │   └── gap_analysis/
│       │
│       ├── database/
│       │   └── vector_database/
│       │
│       └── logs/
│
├── src/
│   │
│   ├── config.py
│   │
│   ├── stage1/
│   │   ├── paper_detector.py
│   │   ├── pdf_reader.py
│   │   ├── metadata_extractor.py
│   │   ├── paper_analyzer.py
│   │   └── master_index.py
│   │
│   ├── stage2/
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_db.py
│   │   ├── retriever.py
│   │   └── question_answer.py
│   │
│   ├── stage3/
│   │   ├── paper_comparison.py
│   │   ├── theme_detection.py
│   │   ├── contradiction_detection.py
│   │   ├── gap_detector.py
│   │   └── gap_verifier.py
│   │
│   ├── stage4/
│   │   ├── json_writer.py
│   │   ├── docx_writer.py
│   │   └── report_generator.py
│   │
│   └── utils/
│       ├── file_utils.py
│       ├── text_utils.py
│       └── logger.py
│
├── app.py
│
└── tests/
```

---

# 4. Master Paper Index

The system must maintain ONE lightweight file:

```text
research_papers/saved/master_papers.json
```

This file is designed to be cheap to load and should NOT contain full paper text, abstracts, explanations, summaries, gaps, or detailed analysis.

It should contain only basic identification information.

## Master index example

```json
{
    "papers": [
        {
            "paper_id": "paper_001",
            "filename": "paper_001.pdf",
            "title": "Example Research Paper",
            "authors": [
                "John Smith",
                "Jane Doe"
            ],
            "year": 2024
        },
        {
            "paper_id": "paper_002",
            "filename": "paper_002.pdf",
            "title": "Another Research Paper",
            "authors": [
                "Alice Brown"
            ],
            "year": 2023
        }
    ]
}
```

## Master index MUST NOT contain

```text
abstract
summary
full text
methodology explanation
research gaps
research questions
long descriptions
embeddings
chunks
LLM responses
```

This keeps the master file extremely lightweight.

---

# 5. Paper Detection

The system must detect whether a PDF is:

1. New
2. Already processed
3. Changed
4. Deleted

Example:

```text
research_papers/

paper_001.pdf  → already processed
paper_002.pdf  → already processed
paper_003.pdf  → NEW
paper_004.pdf  → NEW
```

When triggered:

```text
paper_003.pdf
paper_004.pdf
```

are analyzed.

The system must NOT reprocess:

```text
paper_001.pdf
paper_002.pdf
```

---

# 6. Paper Identity

Each paper should have a stable `paper_id`.

The system should preferably identify papers using:

1. DOI if available
2. Otherwise a generated file/content hash
3. Filename only as a fallback

This prevents the same paper from accidentally being added twice under different filenames.

---

# 7. STAGE 1 — New Paper Processing

## Trigger

The user explicitly triggers:

```text
Process new papers
```

or:

```text
Update research database
```

## Process

```text
Scan PDFs
   ↓
Compare with master_papers.json
   ↓
Find NEW papers
   ↓
Analyze ONLY NEW papers
   ↓
Extract basic metadata
   ↓
Extract detailed paper information
   ↓
Create embeddings/chunks
   ↓
Store paper information
   ↓
Update master_papers.json
```

---

# 8. Detailed Paper Information

Each processed paper gets its own JSON file:

```text
saved/paper_info/paper_001.json
```

Unlike the master index, this file can contain detailed information.

Example:

```json
{
    "paper_id": "paper_001",

    "basic_info": {
        "title": "...",
        "authors": [],
        "year": 2024,
        "journal": "...",
        "doi": "..."
    },

    "research_problem": "...",

    "research_question": "...",

    "objectives": [],

    "methodology": "...",

    "dataset": "...",

    "population": "...",

    "sample_size": "...",

    "variables": [],

    "models": [],

    "main_findings": [],

    "contributions": [],

    "limitations": [],

    "future_work": [],

    "keywords": [],

    "source": {
        "filename": "paper_001.pdf",
        "pages": 12
    }
}
```

This detailed analysis is generated ONCE for each paper.

---

# 9. STAGE 1 Computational Optimization

The system must avoid unnecessary LLM calls.

## First time

```text
New Paper
   ↓
PDF extraction
   ↓
LLM analysis
   ↓
Save JSON
   ↓
Save embeddings
```

## Later

```text
Existing Paper
   ↓
DO NOTHING
```

The existing paper should not be sent to the LLM again unless explicitly requested.

---

# 10. STAGE 2 — Question Answering

The user can ask questions at any time.

Example:

```text
What methodologies are commonly used?
```

The system should use the existing stored knowledge.

## Retrieval priority

Use:

1. Existing structured paper information
2. Existing vector database
3. Original PDF chunks when detailed evidence is required

Process:

```text
Question
   ↓
Determine question type
   ↓
Retrieve relevant stored information
   ↓
Retrieve paper evidence if necessary
   ↓
Local LLM
   ↓
Answer
   ↓
Citations
```

The system must NOT re-analyze the entire paper collection for every question.

---

# 11. Question Types

The system should support:

## Single-paper questions

```text
What methodology does Paper 003 use?
```

## Multi-paper questions

```text
Compare the methodologies used in Papers 001–010.
```

## Literature questions

```text
What methods are most commonly used?
```

## Evidence questions

```text
Which papers use Dataset X?
```

## Comparison questions

```text
Compare Paper 001 and Paper 007.
```

## Trend questions

```text
How has the research changed from 2020 to 2025?
```

---

# 12. Question Output

Every question should be saved.

Location:

```text
saved/questions/
```

Example:

```json
{
    "question_id": "question_001",

    "question": "What methodologies are commonly used?",

    "answer": "...",

    "supporting_papers": [
        "paper_001",
        "paper_003",
        "paper_007"
    ],

    "citations": [
        {
            "paper_id": "paper_001",
            "page": 5,
            "section": "Methodology"
        }
    ],

    "created_at": "...",

    "model": "local-model"
}
```

---

# 13. STAGE 3 — Research Gap Detection

Gap analysis is NOT automatically executed for every question.

It is a separate operation.

The user explicitly triggers:

```text
Find research gaps
```

or:

```text
Analyze research gaps
```

---

# 14. Gap Analysis Optimization

The system should NOT repeatedly analyze all original PDFs.

Instead:

```text
Existing paper JSON files
        +
Existing structured information
        +
Existing vector database
        ↓
Cross-paper analysis
        ↓
Candidate gaps
        ↓
Evidence verification
        ↓
Final gaps
```

The original PDFs are only retrieved when additional evidence is required.

---

# 15. Gap Categories

The system should identify:

1. Methodological gaps
2. Dataset gaps
3. Population gaps
4. Geographic gaps
5. Temporal gaps
6. Theoretical gaps
7. Evaluation gaps
8. Contradiction gaps
9. Reproducibility gaps
10. Research-design gaps
11. Application gaps
12. Validation gaps

---

# 16. Gap Output

Each gap should contain:

```json
{
    "gap_id": "GAP_001",

    "category": "Methodological",

    "description": "...",

    "reasoning": "...",

    "supporting_papers": [
        "paper_001",
        "paper_003",
        "paper_007"
    ],

    "evidence": [],

    "confidence": 0.87,

    "novelty_score": 8,

    "importance_score": 9,

    "feasibility_score": 8,

    "overall_score": 8.3,

    "possible_research_question": "...",

    "possible_objective": "...",

    "possible_contribution": "..."
}
```

---

# 17. Gap Verification

Every automatically detected gap must be checked against evidence.

Process:

```text
Candidate gap
     ↓
Find supporting papers
     ↓
Retrieve evidence
     ↓
Check evidence
     ↓
Is the gap actually supported?
     │
     ├── YES → keep
     │
     └── NO → reject
```

The system must distinguish between:

### Explicit gap

The paper author directly states that something is missing.

### Inferred gap

The system identifies a missing area by comparing multiple papers.

These must be labeled separately.

---

# 18. Adding a New Paper

Example:

Initially:

```text
paper_001.pdf
paper_002.pdf
paper_003.pdf
```

The database contains:

```text
paper_001 → processed
paper_002 → processed
paper_003 → processed
```

Now the user adds:

```text
paper_004.pdf
```

The user triggers:

```text
Update research database
```

The system performs:

```text
Scan
 ↓
paper_001 → existing → skip
paper_002 → existing → skip
paper_003 → existing → skip
paper_004 → NEW → process
```

Only `paper_004` consumes LLM computation.

Then:

```text
paper_004.json
```

is created and:

```text
master_papers.json
```

is updated.

---

# 19. Gap Analysis After New Paper

Adding a new paper does NOT automatically trigger expensive gap analysis.

Instead:

```text
New paper
   ↓
Process new paper
   ↓
Update knowledge base
   ↓
STOP
```

The user can later explicitly trigger:

```text
Find research gaps
```

Then the system compares the updated collection.

This prevents unnecessary computation.

---

# 20. STAGE 4 — Saving

All generated content must be saved under:

```text
research_papers/saved/
```

## JSON

```text
saved/
├── master_papers.json
├── paper_info/
├── questions/
└── gaps/
```

## DOCX

```text
saved/documents/

├── paper_analysis/
│   ├── paper_001.docx
│   └── paper_002.docx
│
├── question_analysis/
│   ├── question_001.docx
│   └── question_002.docx
│
└── gap_analysis/
    ├── gap_analysis_001.docx
    └── gap_analysis_002.docx
```

---

# 21. Master Index vs Detailed Data

The system must keep these separate.

## Lightweight master index

```text
master_papers.json

Contains:

Paper ID
Filename
Title
Authors
Year
```

Purpose:

```text
Fast paper listing
Fast new-paper detection
Fast UI display
Low memory usage
```

## Detailed paper JSON

```text
paper_info/paper_001.json

Contains:

Abstract
Research problem
Research question
Methodology
Dataset
Findings
Limitations
Future work
etc.
```

Purpose:

```text
Detailed analysis
Question answering
Cross-paper comparison
Gap detection
```

---

# 22. Vector Database

The vector database should also be persistent.

Location:

```text
saved/database/vector_database/
```

Each paper's chunks should be stored with:

```text
paper_id
page
section
chunk_id
text
embedding
```

When a new paper is added:

```text
New paper
   ↓
Create chunks
   ↓
Create embeddings
   ↓
Add only new chunks to vector DB
```

Existing embeddings must not be regenerated.

---

# 23. No Duplicate Processing

The system should maintain processing information.

Example:

```json
{
    "paper_id": "paper_001",
    "processed": true,
    "processed_at": "2026-08-22T10:30:00",
    "file_hash": "...",
    "analysis_version": "1.0",
    "embedding_version": "1.0"
}
```

If the PDF hasn't changed:

```text
DO NOT PROCESS
```

If the PDF has changed:

```text
DETECT CHANGE
      ↓
ASK USER / REPROCESS
```

---

# 24. Important Rule

The system should never assume:

> New question = reprocess papers.

Instead:

```text
New question
    ↓
Use existing knowledge
```

Only these actions should trigger expensive computation:

```text
New paper
    ↓
Analyze new paper
```

or:

```text
User explicitly requests
"Re-analyze Paper 003"
```

or:

```text
User explicitly requests
"Find research gaps"
```

---

# 25. Final Workflow

```text
                    PDFs
                     │
                     ▼
              Paper Detector
                     │
            ┌────────┴────────┐
            │                 │
        Existing             NEW
            │                 │
            ▼                 ▼
           SKIP          Analyze Paper
                              │
                              ▼
                        Save JSON
                              │
                              ▼
                     Create Embeddings
                              │
                              ▼
                     Update Master Index
                              │
                              ▼
                            DONE


                     USER QUESTION
                           │
                           ▼
                      Retrieval
                           │
                           ▼
                   Existing Knowledge
                           │
                           ▼
                       Local LLM
                           │
                           ▼
                    Answer + Evidence
                           │
                           ▼
                    Save JSON + DOCX


                   USER: FIND GAPS
                           │
                           ▼
                Load Stored Paper Data
                           │
                           ▼
                   Compare Papers
                           │
                           ▼
                    Find Patterns
                           │
                           ▼
                    Candidate Gaps
                           │
                           ▼
                   Evidence Retrieval
                           │
                           ▼
                    Gap Verification
                           │
                           ▼
                     Rank Gaps
                           │
                           ▼
                    Save JSON + DOCX
```

---

# 26. Primary Design Goal

The system must follow this principle:

> **Process once, store permanently, retrieve repeatedly.**

The expensive operations are performed only when necessary.

```text
             COMPUTATION
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
    New Paper  New Gap  Explicit
                       Re-analysis
        │        │        │
        └────────┼────────┘
                 ▼
              Process
                 │
                 ▼
               STORE
                 │
                 ▼
        ┌─────────────────┐
        │ Reuse stored    │
        │ knowledge       │
        └─────────────────┘
```

This architecture is intended to minimize local CPU/GPU/RAM usage while still allowing detailed research analysis.
