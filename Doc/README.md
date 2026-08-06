# AI Build 2026 - My Hackathon Playbook

Author : Pathan Mansoor Alikhan

Project :
Domain-Specific RAG Chatbot (Offline using Ollama)

Goal
-----
Build an AI chatbot that answers questions from uploaded documents using Local LLM (Llama3.1), RAG, and FAISS.

Tech Stack
----------
Backend
- Python
- FastAPI

AI
- Ollama
- Llama3.1
- LangChain

Vector Database
- FAISS

Frontend
- Streamlit

Others
- Git
- GitHub
- VS Code

------------------------------------------------------------

DAY 1

3:00 PM - 4:00 PM
Registration

Checklist
✔ Registration
✔ Meet teammates
✔ Laptop setup
✔ Internet check
✔ Create WhatsApp group
✔ Decide team leader

Output
------
Team is ready.

------------------------------------------------------------

4:00 PM - 4:45 PM

Problem Statement Briefing

Things to do

✔ Listen carefully

✔ Write important keywords

✔ Understand

- What is the problem?
- Who are the users?
- What should be submitted?
- Judging criteria
- Time limit

Output

One-page notes.

------------------------------------------------------------

4:45 PM - 5:15 PM

Brainstorm

Draw ideas

Problem
        ↓
Possible Solution
        ↓
AI Needed?
        ↓
Can we build in 18 Hours?
        ↓
YES
        ↓
Select Idea

Our Selected Project

Domain Specific RAG Chatbot

Features

✔ Upload PDF

✔ Ask Questions

✔ AI Answers

✔ Local Model

✔ Fast Search

Output

Project finalized.

------------------------------------------------------------

5:15 PM - 6:00 PM

Architecture

Draw

                  User

                    │

                    ▼

             Streamlit UI

                    │

                    ▼

              FastAPI Backend

                    │

                    ▼

            LangChain Pipeline

          ┌──────────┴──────────┐

          ▼                     ▼

      FAISS Index          Ollama
                           Llama3.1

                    │

                    ▼

                Final Answer

Output

Architecture ready.

------------------------------------------------------------

6:00 PM - 7:00 PM

Task Distribution

Member 1

Backend

----------------

Member 2

Frontend

----------------

Member 3

RAG Pipeline

----------------

Member 4

Testing

----------------

Member 5

Presentation

Output

Everyone starts coding.

------------------------------------------------------------

7:00 PM - Midnight

Development Sprint

Priority

1 Backend

↓

2 PDF Upload

↓

3 Embeddings

↓

4 FAISS

↓

5 Ollama

↓

6 Chat Interface

↓

7 Testing

↓

8 GitHub Push

Git Workflow

git init

↓

Create Repository

↓

Commit

↓

Push

↓

Repeat

Output

Working MVP

------------------------------------------------------------

DAY 2

Morning

Complete Remaining Features

Checklist

✔ Fix bugs

✔ Improve UI

✔ Better Prompt

✔ Better Answers

✔ Test

------------------------------------------------------------

11:00 AM

Submission

Checklist

✔ GitHub Updated

✔ README

✔ Screenshots

✔ Demo Ready

✔ Submit

------------------------------------------------------------

12:00 PM - 3:00 PM

Judging

Explain

Problem

↓

Existing Solution

↓

Our Solution

↓

Architecture

↓

AI Technologies

↓

Demo

↓

Future Scope

------------------------------------------------------------

3:00 PM - 5:00 PM

Final Presentation

Presentation Order

Slide 1

Problem

↓

Slide 2

Solution

↓

Slide 3

Architecture

↓

Slide 4

Demo

↓

Slide 5

Impact

↓

Slide 6

Future Scope

------------------------------------------------------------

Questions Judges May Ask

Why this idea?

Why Ollama?

Why Local AI?

Why RAG?

How does FAISS work?

What is LangChain?

Future Improvements?

Why this problem?

Why AI?

What datasets are used?

How scalable is this?

Security considerations?

Cost estimation?

Future roadmap?

What makes your solution unique?

------------------------------------------------------------

Final Checklist

☐ Problem clearly defined

☐ Unique solution

☐ Working MVP

☐ Clean UI

☐ Stable Backend

☐ AI working

☐ RAG working

☐ GitHub Repository

☐ README

☐ Working Demo

☐ Architecture Diagram

☐ Presentation

☐ Screenshots

☐ Test Cases

☐ Team Roles / Team knows their speaking roles

☐ Submission Done / Submission completed before deadline

☐ Backup copy available

☐ Confidence 😊 / Confidence and clear explanation

------------------------------------------------------------

Golden Rule

Think Less

↓

Plan Fast

↓

Build MVP

↓

Test

↓

Improve

↓

Present Clearly

Winning Formula

Problem

+

Working Demo

+

Simple UI

+

Confidence

=

Higher Chance of Winning

------------------------------------------------------------

MISSING SECTIONS FOR A COMPLETE HACKATHON BLUEPRINT

------------------------------------------------------------

1. API Flow

User
   │
   ▼
Frontend (Streamlit / React)
   │
HTTP Request
   │
   ▼
FastAPI Backend
   │
   ├── Upload PDF
   ├── Ask Question
   ├── Get Chat History
   └── Health Check
   │
   ▼
LangChain
   │
   ▼
FAISS Vector DB
   │
Relevant Chunks
   │
   ▼
Ollama (Llama3.1)
   │
Generated Answer
   │
   ▼
Backend
   │
   ▼
Frontend

Endpoints

- POST /upload
- POST /chat
- GET /history
- GET /health

------------------------------------------------------------

2. Database / Storage Design

Project/

documents/
    pdf files

embeddings/
    FAISS index

history/
    chat history

logs/
    application logs

config/
    settings

temp/
    temporary uploads

Optional Database

- SQLite
- MongoDB

Collections

Users

Documents

Chats

Logs

------------------------------------------------------------

3. Folder Structure

project/

backend/

    app.py

    routes/

    services/

    models/

frontend/

    streamlit_app.py

rag/

    loader.py

    splitter.py

    embeddings.py

    retriever.py

llm/

    ollama.py

database/

    faiss/

documents/

static/

templates/

tests/

README.md

requirements.txt

Dockerfile

.gitignore

------------------------------------------------------------

4. Prompt Templates

System Prompt

You are an AI assistant.
Answer only using the uploaded documents.
If information is unavailable, say "I don't know."
Keep answers concise and accurate.

User Prompt

Answer the following question using the uploaded documents.

Question:

{user_question}

RAG Prompt

Context

{retrieved_chunks}

Question

{question}

Answer

------------------------------------------------------------

5. GitHub Milestones

Milestone 1

Repository Created

Milestone 2

Backend Ready

Milestone 3

Frontend Ready

Milestone 4

RAG Working

Milestone 5

Testing

Milestone 6

Final Submission

Git Commit Strategy

Initial Setup

↓

Backend

↓

Frontend

↓

RAG

↓

Testing

↓

README

↓

Final Submission

------------------------------------------------------------

6. Future Enhancements

- Authentication
- Multi-user support
- Voice Input
- Voice Output
- OCR Support
- Image Understanding
- Multiple LLM Support
- Cloud Deployment
- Analytics Dashboard
- Feedback System
- Admin Panel
- Multi-language Support
- Mobile App
- AI Agent Workflow
- Email Integration
- Slack Integration
- Teams Integration

------------------------------------------------------------

7. Risk Management

Possible Risks

- Ollama not running
- Model loading slowly
- FAISS index failure
- PDF parsing issues
- Internet unavailable
- Git merge conflicts
- Laptop battery issues

Backup Plan

- Keep one local backup
- Push to GitHub regularly
- Save FAISS index frequently
- Keep offline documentation
- Test before submission

------------------------------------------------------------

8. Testing Checklist

Backend

- Upload API
- Chat API
- Error Handling
- Response Time

Frontend

- Upload Button
- Chat Window
- Loading Animation
- Error Messages

AI

- Correct Answers
- Hallucination Check
- Empty Query
- Invalid PDF

Performance

- Large PDF
- Multiple Questions
- Memory Usage

------------------------------------------------------------

9. README Template

Project Name

Overview

Problem Statement

Solution

Features

Architecture

Tech Stack

Installation

Usage

Screenshots

Future Scope

Team Members

License

------------------------------------------------------------

10. Demo Script

1. Introduce Team

2. Explain Problem

3. Existing Challenges

4. Our Solution

5. Architecture

6. Live Demo

7. AI Technologies Used

8. Impact

9. Future Scope

10. Thank You

------------------------------------------------------------

11. Deployment Plan

Development

↓

Local Testing

↓

Bug Fixes

↓

Final Testing

↓

GitHub Push

↓

Submission

↓

Presentation

------------------------------------------------------------

12. Success Metrics

- Response Time
- Accuracy
- User Experience
- Ease of Use
- AI Quality
- Innovation
- Scalability
- Reliability

------------------------------------------------------------

13. Team Communication

Before Coding

- Finalize Idea
- Assign Tasks

During Coding

- Update every 30 minutes
- Push code frequently
- Report blockers immediately

Before Submission

- Merge code
- Test everything
- Prepare presentation
- Verify GitHub repository
