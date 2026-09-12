# FollowUp

Don't lose promises inside conversations.

## The problem

People make commitments inside conversations, emails, meeting notes, and
client messages, things like "I'll send the proposal tomorrow" or "we're
still waiting on the client to approve the design", but those commitments
usually never turn into an actual task. A task manager only has what someone
remembered to type into it. Everything said out loud or typed into a chat
thread just evaporates.

FollowUp reads a conversation and pulls out two things: commitments (things
someone said they would do) and waiting items (things the team is blocked
on). It keeps the exact sentence each one came from, works out a due date
where it can, and tells you what's due soon, what's overdue, and what looks
like it's been quietly forgotten.

## How it works

```
User
 |
 v
React UI
 |
 v
FastAPI
 |
 v
Document Parser (txt, md, json, pdf)
 |
 v
AI analyzer (OpenAI) or Local analyzer (regex/rules)
 |
 v
Pydantic validation
 |
 v
SQLite
 |
 v
Status engine (open / due soon / overdue / waiting / completed)
 |
 v
Risk engine (Follow-Up Risk score)
 |
 v
Follow-up queue (what you see in the app)
```

The AI (or the local analyzer, when there's no API key) only does one job:
find the commitments and waiting items and copy out the evidence. Everything
after that, due dates, overdue detection, the risk score, is plain backend
logic. That split matters: a model can misjudge what counts as a commitment,
but it should never get to invent whether something is overdue. Dates are
computed against the actual server clock, every time.

### AI mode vs. local mode

If `OPENAI_API_KEY` is set, FollowUp sends the conversation text to OpenAI
with a strict JSON schema and validates the response with Pydantic before
touching the database. If the key is missing, the request fails, or the
model returns something that doesn't validate, FollowUp falls back to a
local, regex-based analyzer and labels the project "Local analysis" instead
of pretending it ran AI analysis. The mode is always shown honestly in the
sidebar, it reflects what actually happened for that project, not what's
configured in the environment.

The local analyzer knows common ways people phrase commitments ("I'll...",
"I need to...", "can you remind me...") and waiting states ("still waiting
for...", "haven't received..."), and it deliberately skips hedged language
like "I think we should..." so it doesn't turn opinions into fake tasks. It
is not as sharp as a real model, and it says so.

### Follow-Up Risk

A 0-100 score computed per project, entirely from the database, no model
involved:

| Signal | Points |
|---|---|
| Each overdue commitment | +15 (capped at 60) |
| Each high-priority commitment that isn't overdue or done | +10 (capped at 30) |
| Each unresolved commitment with no clear owner | +5 (capped at 20) |
| Each unresolved commitment with no due date | +5 (capped at 20) |
| Each waiting item stale for 3+ days | +8 (capped at 30) |

The total is clamped to 0-100. 0-24 is Low, 25-49 Medium, 50-74 High, 75-100
Critical. The "why" list under the score is generated from whichever of the
above actually contributed, so it always matches the records in the project.

### Forgotten commitments

A commitment is flagged as forgotten when it's overdue, or when it has no
due date at all but the source text was a clear, explicit commitment (not a
vague suggestion) and it's still open. A waiting item is flagged once it's
been sitting unresolved for 5 days or more. This is the same idea as the
risk score, applied item by item instead of as one number.

## Tech stack

- **Frontend**: React, Vite, Tailwind CSS, Framer Motion, Lucide icons
- **Backend**: Python, FastAPI, Pydantic
- **Database**: SQLite (via SQLAlchemy)
- **AI**: OpenAI API (optional, gpt-4o-mini by default)
- **Documents**: PyMuPDF for PDF, standard library for txt/markdown/JSON

## Project structure

```
followup/
├── frontend/            React + Vite app
│   └── src/
│       ├── components/  Cards, badges, modal, app shell
│       ├── pages/       Overview, Analyze, Follow-ups, Completed
│       ├── hooks/       useProjectData (loads/refreshes a project)
│       └── lib/         api.js, the fetch client
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routes/          projects, analyze, commitments, waiting
│       ├── services/        ai_analyzer, fallback_analyzer, document_parser,
│       │                    date_parser, status_engine, risk_engine, pipeline
│       └── utils/forgotten.py
├── sample_data/demo_conversation.txt
└── backend/tests/
```

## Running it locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# optionally add your OpenAI key to .env, otherwise it runs in local mode
uvicorn app.main:app --reload --port 8000
```

The backend creates `backend/followup.db` (SQLite) automatically on first
run. `GET http://localhost:8000/api/health` should return
`{"status": "ok", "analysis_mode": "local"}` (or `"ai"` if a key is set).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`. It talks to the backend at
`http://localhost:8000` by default (set `VITE_API_BASE` in `.env` to change
that).

### Environment variables

Backend (`backend/.env`):

```
OPENAI_API_KEY=       # optional, leave blank to run in local mode
OPENAI_MODEL=         # optional, defaults to gpt-4o-mini
CORS_ORIGINS=         # optional, defaults to localhost:5173
```

Frontend (`frontend/.env`):

```
VITE_API_BASE=http://localhost:8000
```

### Trying the demo

Click "Try demo" on the Overview page, or "Use demo conversation" on the
Analyze page. Either one runs analysis against
`sample_data/demo_conversation.txt`, a short, clearly-labeled conversation
for a fictional project called "Atlas Client Portal". It's built to produce
a mix of results: a few commitments with dates, one without a date, a
waiting item, and one hedged opinion that should NOT turn into a commitment.

### Testing AI mode

Set `OPENAI_API_KEY` in `backend/.env`, restart the backend, and confirm
`/api/health` reports `"analysis_mode": "ai"`. Run the demo or paste your
own conversation, if the OpenAI call fails for any reason, FollowUp quietly
falls back to local analysis and the project is still labeled honestly.

### Backend tests

```bash
cd backend
python3 -m pytest tests/ -v
```

Covers the health endpoint, local extraction (including that hedged
opinions don't become commitments), date parsing, overdue/due-soon status
calculation, and a full API flow: run the demo, fetch commitments and
waiting items, check stats, complete an item, and confirm the stats update.

## API endpoints

```
GET    /api/health
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
DELETE /api/projects/{id}
GET    /api/projects/{id}/commitments
GET    /api/projects/{id}/waiting
GET    /api/projects/{id}/stats
GET    /api/projects/{id}/forgotten
POST   /api/projects/{id}/analyze
POST   /api/analyze
POST   /api/demo
PATCH  /api/commitments/{id}
DELETE /api/commitments/{id}
PATCH  /api/waiting/{id}
DELETE /api/waiting/{id}
```

## Genuine limitations

- The local analyzer is pattern-based. It will miss indirect or unusually
  phrased commitments that a real model would catch, that's the whole
  reason AI mode exists.
- Speaker attribution (who owns a commitment) only works when the source
  text uses a `Name: message` format, common in chat exports and meeting
  notes, but not universal. Free-flowing prose without speaker labels will
  often come back with "Unclear" as the person.
- Date parsing covers the common phrasings (today, tomorrow, weekdays,
  "next week", "in N days", explicit month/day), not every way a date can
  be written in English.
- AI mode was built and validated against the OpenAI API contract but
  couldn't be exercised end-to-end in this environment (no outbound access
  to api.openai.com here). The local fallback path, which AI mode also
  relies on whenever a call fails, is fully tested.
- There's no auth. Every project in the SQLite file is visible to whoever
  can reach the API. Fine for a local/portfolio tool, not for multi-user
  deployment as-is.
