AI Tool: Google Gemini
Purpose: Add "AI Meeting Scheduler" feature (new page + API + chatbot scheduling)
Date: 24-11-2026
Evidence type: Feature-addition prompt (project zip attached)

--- PROMPT SENT ---
ROLE: You are a senior full-stack developer adding a feature to an existing FastAPI + vanilla JavaScript web app (project attached as zip: meetflow_ai_for_gemini.zip).

TASK: Add an "AI Meeting Scheduler" to MeetFlow AI. The user types a plain-English description like "Schedule a meeting with Rahul and Priya on 25 December 2026 at 15:00 about launch prep" and the AI extracts the structured details and saves it.

FEATURE REQUIREMENTS:
1. New model in backend/models.py — ScheduledMeeting:
   id (Integer PK), title (String), date (String, YYYY-MM-DD), time (String, HH:MM or "TBD"), participants (String), agenda (String), status (String, default 'scheduled'), created_at (DateTime).
2. New endpoints in backend/main.py (keep ALL existing endpoints unchanged):
   - GET /api/schedule → all scheduled meetings, newest first
   - POST /api/schedule → manual creation from a form
   - POST /api/schedule/ai → body {"text": "..."} → use the existing call_llm() with a system prompt that returns ONLY JSON {"title","date","time","participants","agenda"} (normalize date to YYYY-MM-DD, time to 24h HH:MM, "TBD" if missing; never invent participants not mentioned). Save the row and return it. If call_llm returns None or fails, return HTTP 502 with a clear message.
   - PATCH /api/schedule/{id}/status → {"status": "scheduled"|"completed"|"cancelled"}
   - DELETE /api/schedule/{id}
3. Chatbot scheduling: inside POST /api/chat, BEFORE normal answering: if the question matches (case-insensitive) both "schedule" and "meeting", try to extract details with call_llm(..., parse_json=True) using the same scheduling system prompt; on success save the ScheduledMeeting and reply {"answer": "Scheduled '<title>' on <date> at <time> with <participants>."}. On any failure, fall through to the normal chat_answer() behavior.
4. Frontend — new "Schedule" page:
   - index.html: add nav button <button data-page="schedule">📅 Schedule</button> before the Weekly digest button (the rest of index.html stays byte-for-byte identical).
   - frontend/js/app.js: add case 'schedule' to the render() switch, add 'schedule':'Schedule' to the pageTitle map, and add async function schedule() that renders: (a) an AI row: text input + "Schedule with AI" button → POST /api/schedule/ai → re-render on success, show error text on failure; (b) a manual form (title, date, time, participants, agenda) → POST /api/schedule; (c) cards listing each meeting with status pill and buttons: Complete / Cancel / Delete (PATCH/DELETE). Keep the existing api() helper, esc() and card() helpers and the existing code style.

CONSTRAINTS:
- Do not modify any existing endpoint behavior, models, or UI other than the additions above.
- Reproduce unchanged parts of files byte-for-byte — output the COMPLETE contents of every file you change.
- No placeholders, no TODOs, no "rest unchanged" remarks.
- No new dependencies; no API keys in code.

OUTPUT FORMAT (strict):
1. Complete backend/models.py
2. Complete backend/main.py
3. Complete frontend/index.html
4. Complete frontend/js/app.js
5. A 5-bullet summary of what you added

--- GEMINI'S RESPONSE ---
Four files received (saved as response-*.py/.html/.js in this folder), plus a 5-bullet summary.

--- ADAPTATION NOTES (response evaluation, applied during integration) ---
Gemini's output was NOT byte-for-byte: it rewrote the whole app shell (new nav, renamed DOM IDs #page-title/#content, dropped all existing pages) and wrote a standalone main.py that DELETED every existing endpoint (meetings, decisions, conflicts, tasks, digest, overview, health, CORS, seed). It also misused the existing API:
  - call_llm() arguments were swapped (system text passed as prompt).
  - chat_answer(question, db) called with a Session object instead of a context string.
  - models.py imported Base from .db (circular — Base lives in models.py).
  - _extract_meeting_with_ai(text, parse_json=False) called call_llm with the system prompt as the user prompt.
Integration fixes applied:
  - Kept all original endpoints/UI; surgically added only the schedule feature + nav button + schedule() page.
  - Corrected call_llm() calls to (text, system=SCHEDULE_SYSTEM_PROMPT, parse_json=True).
  - chat_answer() called with a proper context string; schedule intent short-circuits with an explicit error message on failure.
  - ScheduledMeeting added to the existing models.py using the existing Base.
  - Added a retry loop and clear failure message for robustness.
Verification after integration:
  - POST /api/schedule/ai -> 200, correctly extracted {title, date 2026-12-25, time 15:00, participants Rahul, Priya}.
  - POST /api/chat (schedule intent) -> 200 "Scheduled 'release checklist' on 2026-12-28 at 10:00 with Chirayu."
  - PATCH /api/schedule/{id}/status -> 200/400; DELETE -> 200/404.
  - All pre-existing endpoints (overview, meetings, conflicts, tasks, digest, chat) still return 200.
  - Schedule page renders in the browser with AI box, manual form, and 2 meeting cards with Complete/Cancel/Delete buttons.
