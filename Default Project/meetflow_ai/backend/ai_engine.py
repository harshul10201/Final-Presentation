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
    lines=[x.strip() for x in transcript.splitlines() if x.strip()]; speakers=[]; decisions=[]; actions=[]; questions=[]
    for line in lines:
        m=re.match(r'^([^:]{1,60}):\s*(.*)$',line); speaker=m.group(1).strip() if m else ''; body=m.group(2).strip() if m else line
        if speaker: speakers.append(speaker)
        low=body.lower()
        if any(w in low for w in ['decided','decision','agree','approved','will launch','launch date','deadline','committed']):
            decisions.append({'topic':topic_for(body),'text':body})
        if any(w in low for w in [' will ',' action','todo','to do','follow up','follow-up','need to','should send','send the','prepare']):
            deadline=''; date=re.search(r'\b(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b',body,re.I)
            if date: deadline=date.group(1)
            actions.append({'title':body,'owner':speaker or 'Unassigned','deadline':deadline,'source_text':line})
        if '?' in body: questions.append(body)
    if not decisions: decisions=[{'topic':topic_for(l),'text':l} for l in lines if re.search(r'\b(agreed|decide|approved)\b',l,re.I)]
    return {'summary':' '.join(lines[:4])[:900] or 'No summary available.','discussion':lines[:12],'questions':questions,'decisions':decisions,'actions':actions}
def topic_for(text):
    if re.search(r'launch|release|ship|date',text,re.I): return 'Launch date'
    if re.search(r'budget|cost|spend',text,re.I): return 'Budget'
    if re.search(r'feature|product|scope',text,re.I): return 'Product scope'
    return 'General'
def chat_answer(question, context):
    return call_llm('Meeting context:\n'+context+'\n\nQuestion: '+question,system='Answer the question using only supplied meeting context. If the context lacks the answer, say so. Be concise.',parse_json=False)
