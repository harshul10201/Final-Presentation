AI Tool: Claude
Purpose: Bug fix — chatbot HTTP 502 (JSON parser applied to plain-text replies)
Date: 24-11-2026
Evidence type: Debugging / refinement prompt (attached project zip)

--- PROMPT SENT ---

ROLE: You are a senior Python backend engineer debugging a FastAPI chatbot.

TASK: I've attached my project as meetflow_ai_for_claude.zip. Fix a bug in backend/ai_engine.py. The chat endpoint POST /api/chat returns HTTP 502 with:
{"detail":"AI chat request failed: Expecting value: line 1 column 1 (char 0)"}

CONTEXT: call_llm(prompt, system) always ends with `return json.loads(content)`. That is correct for parse(transcript), which must receive JSON extraction output, but chat_answer(question, context) reuses call_llm and returns plain-text answers (e.g. "10 December 2026"). json.loads() then crashes on plain text. Verified: the LLM API itself works and returns the correct plain-text reply.

CONSTRAINTS:
- Fix so chat_answer returns the raw plain-text reply WITHOUT JSON parsing.
- Keep parse() behavior unchanged: it must still parse JSON (including stripping ```json fences).
- Minimal change only — do not rewrite unrelated code, do not change function names, do not touch other files.
- No placeholders; output must be directly pasteable.

OUTPUT FORMAT:
1. The complete new contents of backend/ai_engine.py only.
2. Then a 3-bullet summary: what was broken, what you changed, why parse() still works.
