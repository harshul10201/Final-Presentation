# PROMPTS.md — MeetFlow AI · Prompt Engineering Documentation

> Required by the Final Project Guidelines §2.2 (Five Parts of a Good Prompt)
> and §2.4 (record of initial, modified, and final prompts).
> **This file is the evidence appendix of the project — keep it updated after every prompt you run.**

---

## 1. Initial Project-Building Prompt (The Five Parts)

This prompt was written **before any development** and used as the first
instruction given to **AI Tool #1**. Each of the five required parts is
labeled below.

### Part 1 — Role
> You are a senior full-stack web developer and AI solutions architect with 10+
> years of experience building production-grade SaaS products. You write clean,
> complete, runnable code with no placeholders, no "TODO" comments, and no
> omitted sections.

### Part 2 — Task
> Build the first working version of **"MeetFlow AI"**, an AI-powered
> meeting-to-execution web application. The application must:
> 1. Accept a pasted meeting transcript and produce an executive summary,
>    discussion points, and unresolved questions.
> 2. Extract **decisions** (e.g. "the launch date is 10 December") and store
>    them as permanent, versioned institutional memory.
> 3. Extract **action items** with speaker-attributed owners and parsed
>    deadlines, and hold them in a **Pending Approval** state — nothing becomes
>    active until a human clicks Approve.
> 4. Detect **conflicts** between meetings (e.g. launch date changed from
>    10 December to 15 December) and show them in a Conflict Review screen with
>    Confirm Change / Keep Previous Decision options. Never silently overwrite.
> 5. Provide a **Kanban task board** (Pending / In Progress / Completed /
>    Blocked) and a **weekly digest** page.
> 6. Include an **AI chatbot widget** that answers questions about the user's
>    meetings by calling a real LLM API.

### Part 3 — Context
> **Problem:** Engineering and product teams spend hours in meetings, but
> decisions vanish into notes and chat histories. Commitments silently
> contradict each other across meetings (a launch date agreed as 10 December is
> changed to 15 December in an ad-hoc sync with no tracking). Action items like
> "someone should deploy the app" end up owned by nobody. Existing AI meeting
> tools also post hallucinated tasks to trackers without any human review.
>
> **Purpose:** MeetFlow AI closes this meeting-to-execution gap by preserving
> every decision as versioned institutional memory, flagging contradictions
> before they cause damage, and only activating tasks after explicit human
> approval.
>
> **Target audience:** Team leads and project managers in software/product
> teams. (Also demonstrated as a Prompt Engineering course final project.)

### Part 4 — Constraints
> - **Backend:** Python 3.11+, FastAPI, SQLAlchemy with SQLite database.
> - **Frontend:** responsive single-page web UI using HTML/CSS/JavaScript
>   (modern, clean, dark-friendly design; no paid UI libraries).
> - **Chatbot:** must call a real AI model through an HTTP API using an API
>   key read from environment variables — never hardcode keys, never use
>   canned/predefined answers. Must show typing/loading state and handle API
>   errors and empty input gracefully.
> - **AI extraction:** dual-mode — use an LLM API when a key is present, with
>   a deterministic offline parser as fallback so the app works without a key.
> - **Data:** SQLite file; ship with seeded demo data (two meetings where the
>   second one changes the launch date, creating one conflict).
> - **Security:** no API keys or credentials in the source code; use a `.env`
>   / `.env.example` pattern.
> - **Scope limits:** no login system, no payment, no mobile app — only the
>   website described above.

### Part 5 — Output Format
> Deliver the project as a complete file tree with the full source code of
> every file, in this structure:
>
> ```
> meetflow-ai/
> ├── backend/            # FastAPI app: models, routers, AI engine, seed data
> ├── frontend/           # index.html + css + js (dashboard, meetings,
> │   │                   #   conflicts, tasks, digest, chatbot)
> ├── .env.example
> ├── requirements.txt
> ├── README.md           # objectives, features, tech stack, run instructions
> └── PROMPTS.md
> ```
>
> After the code, print: (a) a numbered feature list, (b) exact local run
> instructions, and (c) a short list of the five prompt parts you received.
> Output only files and commands — no conversational filler.

---

### 📋 Paste-ready combined prompt (use this exact text in AI Tool #1)

```text
ROLE: You are a senior full-stack web developer and AI solutions architect with 10+ years of experience building production-grade SaaS products. You write clean, complete, runnable code with no placeholders, no TODO comments, and no omitted sections.

TASK: Build the first working version of "MeetFlow AI", an AI-powered meeting-to-execution web application that: (1) accepts a pasted meeting transcript and produces an executive summary, discussion points, and unresolved questions; (2) extracts decisions and stores them as permanent versioned institutional memory; (3) extracts action items with speaker-attributed owners and parsed deadlines, held in a "Pending Approval" state until a human approves them; (4) detects conflicts between meetings (e.g. launch date changed from 10 December to 15 December) and shows them in a Conflict Review screen with "Confirm Change" / "Keep Previous Decision" options, never silently overwriting; (5) provides a Kanban task board (Pending / In Progress / Completed / Blocked) and a weekly digest page; (6) includes an AI chatbot widget that answers questions about the user's meetings by calling a real LLM API.

CONTEXT: Engineering and product teams lose decisions in meeting notes, commitments silently contradict each other across meetings (a launch date agreed as 10 December is changed to 15 December in an ad-hoc sync with no tracking), and action items end up owned by nobody. Existing AI meeting tools also post hallucinated tasks without human review. MeetFlow AI closes this meeting-to-execution gap by preserving every decision as versioned institutional memory, flagging contradictions before they cause damage, and only activating tasks after explicit human approval. Target audience: team leads and project managers in software/product teams.

CONSTRAINTS: Backend = Python 3.11+, FastAPI, SQLAlchemy + SQLite. Frontend = responsive single-page HTML/CSS/JavaScript UI, modern clean design, no paid UI libraries. Chatbot = must call a real AI model through an HTTP API using an API key read from environment variables; never hardcode keys; never use canned answers; show loading state; handle API errors and empty input. AI extraction = dual-mode (LLM API when key present, deterministic offline parser fallback). Ship seeded demo data (two meetings, the second changing the launch date, creating one conflict). No API keys in source; use .env.example. Scope limits: no login system, no payments, no mobile app.

OUTPUT FORMAT: Deliver a complete file tree with full source code for every file: backend/ (FastAPI models, routers, AI engine, seed data), frontend/ (index.html, css, js for dashboard, meetings, conflicts, tasks, digest, chatbot), .env.example, requirements.txt, README.md (objectives, features, tech stack, run instructions), PROMPTS.md. After the code print: (a) a numbered feature list, (b) exact local run instructions, (c) a short list of the five prompt parts you received. Output only files and commands — no conversational filler.
```

---

## 2. Prompt Log (initial → modified → final)

Add one row for **every** prompt you run, in any of the three AI tools.
"Technique" must be one of: role-based, chain/step-by-step, context-based,
structured, refinement/optimization, constraints, reverse prompting.

| # | Date | AI Tool | Purpose / Feature | Technique | Prompt (short) | Output / Evidence file | Result & refinement notes |
|---|------|---------|-------------------|-----------|----------------|------------------------|---------------------------|
| 1 | 2026-11-24 | ChatGPT | Initial website generation (5-part prompt above) | role + context + constraints + structured | Full paste-ready prompt in §1 | `evidence/01-chatgpt-initial/` | Complete 13-file project generated (FastAPI + SQLite + vanilla JS): meetings, conflict review, approval workflow, Kanban, digest, chatbot. Original zip saved as-is. |
| 2 | 2026-11-24 | Claude | Fix chatbot HTTP 502: `json.loads()` applied to plain-text chat replies | debugging with precise root-cause context + hard constraints | "Fix backend/ai_engine.py: chat_answer returns plain text but call_llm forces JSON parsing…" (project zip attached) | `evidence/02-claude-chatbot-fix/` | Added `parse_json` flag: chat returns raw text, extraction still parses JSON. **Verified after applying:** chat → 200 OK (real Gemini answer, 1.9s), empty input → 400, parse() → valid JSON dict. |
| 3 | 2026-11-24 | Google Gemini | Add "AI Meeting Scheduler" feature (new model, 5 endpoints, chatbot scheduling, Schedule page) | structured + context + constraints + response evaluation | "Add AI Meeting Scheduler… (project zip attached)" | `evidence/03-gemini-scheduler/` | Gemini's output rewrote the whole app shell and dropped every existing endpoint, with misused APIs (swapped call_llm args, Session passed to chat_answer). **Integrated surgically** with corrections (retry + explicit error message). **Verified:** POST /api/schedule/ai -> 200 (correct extraction), chat schedule -> 200, PATCH/DELETE -> 200/400/404, all legacy endpoints still 200, Schedule page renders with cards + Complete/Cancel/Delete. |

**Evidence folder convention:** save screenshots / exported chats under
`evidence/<NN>-<tool>-<purpose>/` (e.g. `evidence/03-claude-chatbot-fix/`).

---

## 3. Prompt Refinement Examples (before → after)

For at least **two** prompts, show an initial weak version, the improved
version, and what changed in the AI output. Example skeleton:

### Refinement 1 — Chatbot backend
| | Prompt |
|---|---|
| **Before (weak)** | "make a chatbot" |
| **After (improved)** | Role + exact API, error cases, response format (see row #N of the log) |
| **What improved in the output** | *(fill: e.g. before → static answers, no error handling; after → real API call, timeout, empty-input validation, JSON error responses)* |

### Refinement 2 — Conflict detection UI
| | Prompt |
|---|---|
| **Before (weak)** | |
| **After (improved)** | |
| **What improved in the output** | |

---

## 4. AI Tool Contributions (§2.3 — all three tools)

| AI Tool | Tasks performed with it | Evidence |
|---------|-------------------------|----------|
| 1. ChatGPT | Initial website generation from the 5-part prompt (complete source code, 13 files) | `evidence/01-chatgpt-initial/` |
| 2. Claude | Debugging the chatbot HTTP 502 — root-cause analysis + minimal fix, attached project as zip | `evidence/02-claude-chatbot-fix/` |
| 3. Google Gemini | Added the AI Meeting Scheduler feature: new ScheduledMeeting model, 5 endpoints, chatbot scheduling route, and Schedule page UI | `evidence/03-gemini-scheduler/`

---

## 5. Techniques Demonstrated Checklist (§2.4)

- [ ] Role-based prompting (see §1 Part 1)
- [ ] Chain / step-by-step prompting
- [ ] Context-based prompting (see §1 Part 3)
- [ ] Structured prompting (see §1 Part 5 output format)
- [ ] Prompt refinement & optimization (see §3)
- [ ] Clear instructions and constraints (see §1 Part 4)
- [ ] Reverse prompting & response evaluation (ask the AI to critique/review its own output)
