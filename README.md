# FollowUp | AI Conversation Action Tracker

A full-stack application I built to turn conversations into actionable follow-ups.

FollowUp analyzes conversations and identifies **commitments** and **waiting items**, then tracks their due dates, status, and follow-up risk in one place.

## What I Built

Important tasks and promises often get buried inside client conversations, meeting notes, and messages.

For example:

> "I'll send the proposal tomorrow."

or:

> "We're still waiting for the client to approve the design."

FollowUp turns these statements into structured items that can be reviewed and tracked instead of being forgotten.

The application can:

* Extract commitments from conversations
* Identify waiting items
* Keep the original sentence as evidence
* Detect common due dates such as today, tomorrow, next week, and specific dates
* Track open, due soon, overdue, waiting, and completed items
* Calculate a follow-up risk score
* Flag potentially forgotten items
* Allow users to edit and complete follow-ups
* Analyze documents in TXT, Markdown, JSON, and PDF formats

## How It Works

```text
Conversation / Document
        ↓
Document Parser
        ↓
AI or Local Analysis
        ↓
Commitments + Waiting Items
        ↓
Date & Status Processing
        ↓
Risk Calculation
        ↓
Follow-up Dashboard
```

The project supports two analysis modes.

### AI Analysis

When an OpenAI API key is available, the conversation is sent to the configured model and the response is validated before being saved.

### Local Analysis

The application can also run without an API key using a rule-based NLP approach.

This makes the project easier to run locally and also gives the application a fallback when the AI service is unavailable.

The local analyzer handles common patterns such as:

* "I'll send..."
* "I need to..."
* "Can you remind me..."
* "We're waiting for..."
* "Haven't received..."

It also avoids treating uncertain statements such as "I think we should..." as confirmed commitments.

## Follow-Up Risk

Each project receives a risk score from 0 to 100 based on the current follow-up data.

The score considers:

| Signal                              | Score |
| ----------------------------------- | ----: |
| Overdue commitment                  |   +15 |
| High-priority unresolved commitment |   +10 |
| Commitment without a clear owner    |    +5 |
| Commitment without a due date       |    +5 |
| Waiting item older than 3 days      |    +8 |

The score is limited to 100.

|  Score | Risk     |
| -----: | -------- |
|   0-24 | Low      |
|  25-49 | Medium   |
|  50-74 | High     |
| 75-100 | Critical |

The risk calculation is handled by the backend rather than the AI model, so the score is based on the actual records stored in the database.

## Screenshots

### Overview

![Overview](screenshots/overview.png)

### Conversation Analysis

![Conversation Analysis](screenshots/analyze.png)

### Follow-ups

![Follow-ups](screenshots/followups.png)

### Completed Items

![Completed Items](screenshots/completed.png)

> Screenshots show the actual application running locally.

## Tech Stack

### Frontend

* React
* Vite
* Tailwind CSS
* Framer Motion
* Lucide Icons

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

### Database

* SQLite

### AI

* OpenAI API
* Local rule-based analyzer

### Document Processing

* PyMuPDF
* TXT
* Markdown
* JSON

## Project Structure

```text
followup/
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── lib/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── test_data/
│   └── test_data.txt
│
└── README.md
```

## Running Locally

### 1. Backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

The backend will run at:

```text
http://localhost:8000
```

SQLite is created automatically when the backend starts.

### 2. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
.env
npm run dev
```

Open:

```text
http://localhost:5173
```

### 3. Environment Variables

Backend:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
CORS_ORIGINS=http://localhost:5173
```

The OpenAI key is optional. The application can run using the local analyzer.

Frontend:

```env
VITE_API_BASE=http://localhost:8000
```

## Demo

The project includes a sample conversation:

```text
test_data/test_data.txt
```

From the Overview page, click **Try Demo**.

The demo contains a fictional client conversation with different types of commitments and waiting items.

It demonstrates how FollowUp extracts actionable information and turns it into trackable items.

## Testing

The backend includes automated tests for:

* API health
* Commitment extraction
* Waiting item extraction
* Date parsing
* Due-soon and overdue status
* Risk calculations
* Complete API workflow

Run the tests from the backend folder:

```powershell
python -m pytest tests/ -v
```

## API

Main endpoints include:

```text
GET    /api/health

GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
DELETE /api/projects/{id}

POST   /api/projects/{id}/analyze
POST   /api/analyze
POST   /api/demo

GET    /api/projects/{id}/commitments
PATCH  /api/commitments/{id}
DELETE /api/commitments/{id}

GET    /api/projects/{id}/waiting
PATCH  /api/waiting/{id}
DELETE /api/waiting/{id}

GET    /api/projects/{id}/stats
GET    /api/projects/{id}/forgotten
```

## Limitations

The current version is designed as a portfolio and local-use project, so there are a few limitations:

* The local analyzer works with common patterns and may miss unusual wording.
* Speaker detection works best with `Name: message` formatted conversations.
* Date parsing focuses on common English date expressions.
* AI analysis requires an OpenAI API key.
* There is currently no authentication or multi-user access control.
* SQLite is suitable for local use but would need to be replaced or configured differently for a larger production deployment.

## What I Learned

This project gave me practical experience combining NLP, LLM integration, backend APIs, database design, frontend development, and automated testing in one application.

One of the main things I focused on was keeping the AI part separate from the core application logic. The model helps identify information from conversations, while dates, status, risk calculations, and database operations are handled by the application itself.

## About

I built FollowUp as a practical AI application to explore how conversation data can be converted into useful workflows.

It combines AI-assisted text analysis with traditional backend logic rather than relying entirely on an LLM.

**Built by Muhammad Rameez**

AI/ML Engineer | RAG Pipelines, NLP, LangChain, Python
