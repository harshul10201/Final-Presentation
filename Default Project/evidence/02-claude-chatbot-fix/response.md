AI Tool: Claude
Date: 24-11-2026
Task: Fix chatbot HTTP 502 in backend/ai_engine.py

--- CLAUDE'S RESPONSE (as received) ---

[Complete rewritten backend/ai_engine.py]

Key change: call_llm gained a new parameter `parse_json=True`:

    def call_llm(prompt, system=SYSTEM_PROMPT, parse_json=True):
        ...
        content=data['choices'][0]['message']['content']
        if not parse_json: return content.strip()
        content=re.sub(r'^```(?:json)?\s*|\s*```$','',content.strip())
        return json.loads(content)

And chat_answer now passes parse_json=False:

    def chat_answer(question, context):
        return call_llm('Meeting context:\n'+context+'\n\nQuestion: '+question,
            system='Answer the question using only supplied meeting context. If the context lacks the answer, say so. Be concise.',
            parse_json=False)

--- FULL CODE (as received, verified and applied by project owner) ---

import os, json, re, urllib.request, urllib.error
SYSTEM_PROMPT='''Analyze a meeting transcript. Return ONLY JSON with keys summary (string), discussion (array of strings), questions (array of strings), decisions (array of objects {topic,text}), actions (array of objects {title,owner,deadline,source_text}). Only infer owners when explicitly attributed. Dates should be ISO YYYY-MM-DD when clear; otherwise preserve the phrase. Avoid inventing facts. Transcript speakers are in format Speaker: words.'''
def call_llm(prompt, system=SYSTEM_PROMPT, parse_json=True):
    key=os.getenv('OPENAI_API_KEY'); endpoint=os.getenv('LLM_API_URL','https://api.openai.com/v1/chat/completions'); model=os.getenv('LLM_MODEL','gpt-4o-mini')
    if not key: return None
    payload=json.dumps({'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}], 'temperature':0.2}).encode()
    req=urllib.request.Request(endpoint,data=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as r: data=json.loads(r.read())
    content=data['choices'][0]['message']['content']
    if not parse_json: return content.strip()
    content=re.sub(r'^```(?:json)?\s*|\s*```$','',content.strip())
    return json.loads(content)
def parse(transcript):
    llm=call_llm(transcript)
    if llm: return llm
    # ... (offline fallback parser unchanged)
def chat_answer(question, context):
    return call_llm('Meeting context:\n'+context+'\n\nQuestion: '+question,system='Answer the question using only supplied meeting context. If the context lacks the answer, say so. Be concise.',parse_json=False)

--- VERIFICATION (performed after applying) ---
- POST /api/chat -> HTTP 200, real Gemini answer in 1.9s: "Based on the provided context, the launch date moved to 15 December 2026 ... and Alex owns the release notes."
- Empty question -> HTTP 400 "Question cannot be empty" (error handling intact)
- parse() LLM path -> still returns valid JSON dict (summary/decisions/actions extracted correctly)
- chat_answer() -> returns plain text "20 December 2026"
