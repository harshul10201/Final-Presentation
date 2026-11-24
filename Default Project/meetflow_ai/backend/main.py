from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
import re
from .db import get_db
from .models import Meeting,Decision,Conflict,ActionItem,ScheduledMeeting
from .ai_engine import parse,chat_answer,topic_for,call_llm
from .seed import seed
app=FastAPI(title='MeetFlow AI',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    from .db import Session as S
    db=S();seed(db);db.close()
class TranscriptIn(BaseModel): title:str; transcript:str; held_at:str|None=None
class ChatIn(BaseModel): question:str
class TaskStatus(BaseModel): status:str
class TaskApproval(BaseModel): approval:str
class ConflictChoice(BaseModel): choice:str
class ScheduleCreate(BaseModel): title:str; date:str; time:str='TBD'; participants:str=''; agenda:str=''
class AIScheduleIn(BaseModel): text:str
class ScheduleStatusIn(BaseModel): status:str
SCHEDULE_SYSTEM_PROMPT='''Extract meeting details from the user's text. Return ONLY JSON with keys: title (string), date (YYYY-MM-DD or "TBD"), time (24h HH:MM or "TBD"), participants (comma-separated string of people explicitly mentioned, "" if none), agenda (short string, "" if none). Normalize dates to YYYY-MM-DD (use the current year if the year is not stated). Never invent participants or facts not present in the text.'''
def _extract_schedule(text):
    data=None
    for _attempt in range(2):
        try:
            data=call_llm(text,system=SCHEDULE_SYSTEM_PROMPT,parse_json=True)
        except Exception:
            data=None
        if isinstance(data,dict): break
    if not isinstance(data,dict): return None
    return {'title':str(data.get('title') or '').strip() or 'Untitled meeting','date':str(data.get('date') or '').strip() or 'TBD','time':str(data.get('time') or '').strip() or 'TBD','participants':str(data.get('participants') or '').strip(),'agenda':str(data.get('agenda') or '').strip()}
def _save_schedule(db,payload):
    m=ScheduledMeeting(**payload);db.add(m);db.commit();db.refresh(m);return m
def _schedule_json(m):return {'id':m.id,'title':m.title,'date':m.date,'time':m.time,'participants':m.participants,'agenda':m.agenda,'status':m.status,'created_at':str(m.created_at)}
@app.get('/api/health')
def health():return {'status':'ok'}
@app.get('/api/overview')
def overview(db:Session=Depends(get_db)):
    return {'meetings':db.query(Meeting).count(),'decisions':db.query(Decision).count(),'pending_tasks':db.query(ActionItem).filter(ActionItem.approval=='pending').count(),'conflicts':db.query(Conflict).filter(Conflict.status=='pending').count()}
@app.get('/api/meetings')
def meetings(db:Session=Depends(get_db)):
    return [{'id':m.id,'title':m.title,'held_at':m.held_at,'summary':m.summary} for m in db.query(Meeting).order_by(desc(Meeting.id)).all()]
@app.get('/api/meetings/{mid}')
def meeting(mid:int,db:Session=Depends(get_db)):
    m=db.get(Meeting,mid)
    if not m: raise HTTPException(404,'Meeting not found')
    return {'id':m.id,'title':m.title,'held_at':m.held_at,'transcript':m.transcript,'summary':m.summary,'discussion':json.loads(m.discussion or '[]'),'questions':json.loads(m.questions or '[]'),'decisions':[{'id':d.id,'text':d.text,'topic':d.topic,'version':d.version,'status':d.status} for d in m.decisions],'actions':[task(a) for a in m.actions]}
def task(a):return {'id':a.id,'meeting_id':a.meeting_id,'title':a.title,'owner':a.owner,'deadline':a.deadline,'status':a.status,'approval':a.approval,'source_text':a.source_text}
@app.post('/api/meetings')
def create_meeting(payload:TranscriptIn,db:Session=Depends(get_db)):
    if not payload.transcript.strip():raise HTTPException(400,'Transcript cannot be empty')
    try: result=parse(payload.transcript)
    except Exception as e: raise HTTPException(502,'AI extraction failed: '+str(e))
    m=Meeting(title=payload.title.strip() or 'Untitled meeting',held_at=payload.held_at or '',transcript=payload.transcript,summary=result.get('summary',''),discussion=json.dumps(result.get('discussion',[])),questions=json.dumps(result.get('questions',[])));db.add(m);db.flush()
    for item in result.get('decisions',[]):
        text=item.get('text','').strip()
        if not text:continue
        topic=item.get('topic') or topic_for(text); previous=db.query(Decision).filter(Decision.topic==topic,Decision.status=='active').order_by(desc(Decision.version)).first()
        if previous and previous.text.lower()!=text.lower():db.add(Conflict(previous_decision_id=previous.id,proposed_text=text,proposed_meeting_id=m.id,topic=topic))
        else:db.add(Decision(meeting_id=m.id,text=text,topic=topic,version=1,status='active'))
    for a in result.get('actions',[]):
        if a.get('title'):db.add(ActionItem(meeting_id=m.id,title=a['title'],owner=a.get('owner') or 'Unassigned',deadline=a.get('deadline') or '',status='Pending',approval='pending',source_text=a.get('source_text','')))
    db.commit();db.refresh(m)
    return {'id':m.id,'extraction':result,'message':'Meeting saved. Action items await approval; conflicts await review.'}
@app.get('/api/decisions')
def decisions(db:Session=Depends(get_db)):
    return [{'id':d.id,'meeting_id':d.meeting_id,'meeting':d.meeting.title,'text':d.text,'topic':d.topic,'version':d.version,'status':d.status,'created_at':str(d.created_at)} for d in db.query(Decision).order_by(desc(Decision.created_at)).all()]
@app.get('/api/conflicts')
def conflicts(db:Session=Depends(get_db)):
    result=[]
    for c in db.query(Conflict).filter(Conflict.status=='pending').all():
        d=db.get(Decision,c.previous_decision_id);oldmeeting=db.get(Meeting,d.meeting_id);newmeeting=db.get(Meeting,c.proposed_meeting_id)
        result.append({'id':c.id,'topic':c.topic,'previous':d.text,'previous_version':d.version,'previous_meeting':oldmeeting.title,'proposed':c.proposed_text,'proposed_meeting':newmeeting.title,'proposed_meeting_id':newmeeting.id})
    return result
@app.post('/api/conflicts/{cid}/review')
def review_conflict(cid:int,p:ConflictChoice,db:Session=Depends(get_db)):
    c=db.get(Conflict,cid)
    if not c or c.status!='pending':raise HTTPException(404,'Pending conflict not found')
    if p.choice not in ['confirm','keep']:raise HTTPException(400,'choice must be confirm or keep')
    old=db.get(Decision,c.previous_decision_id)
    if p.choice=='confirm':
        old.status='superseded';new=db.query(Decision).filter(Decision.meeting_id==c.proposed_meeting_id,Decision.topic==c.topic).first()
        db.add(Decision(meeting_id=c.proposed_meeting_id,text=c.proposed_text,topic=c.topic,version=old.version+1,status='active',supersedes_id=old.id))
        c.status='confirmed'
    else:c.status='kept_previous'
    db.commit();return {'status':c.status}
@app.get('/api/tasks')
def tasks(db:Session=Depends(get_db)):
    return [task(a) for a in db.query(ActionItem).order_by(desc(ActionItem.id)).all()]
@app.post('/api/tasks/{tid}/approval')
def approve(tid:int,p:TaskApproval,db:Session=Depends(get_db)):
    a=db.get(ActionItem,tid)
    if not a:raise HTTPException(404,'Task not found')
    if p.approval not in ['approved','rejected']:raise HTTPException(400,'Invalid approval')
    a.approval=p.approval;db.commit();return task(a)
@app.patch('/api/tasks/{tid}/status')
def status(tid:int,p:TaskStatus,db:Session=Depends(get_db)):
    a=db.get(ActionItem,tid)
    if not a:raise HTTPException(404,'Task not found')
    if a.approval!='approved':raise HTTPException(400,'Approve task before moving it')
    if p.status not in ['Pending','In Progress','Completed','Blocked']:raise HTTPException(400,'Invalid status')
    a.status=p.status;db.commit();return task(a)
@app.get('/api/digest')
def digest(db:Session=Depends(get_db)):
    tasks=db.query(ActionItem).filter(ActionItem.approval=='approved',ActionItem.status!='Completed').all();conf=db.query(Conflict).filter(Conflict.status=='pending').all();meet=db.query(Meeting).order_by(desc(Meeting.id)).limit(5).all()
    return {'tasks':[task(a) for a in tasks],'conflicts':len(conf),'meetings':[{'title':m.title,'summary':m.summary,'held_at':m.held_at} for m in meet]}
@app.get('/api/schedule')
def schedule_list(db:Session=Depends(get_db)):
    return [_schedule_json(m) for m in db.query(ScheduledMeeting).order_by(desc(ScheduledMeeting.id)).all()]
@app.post('/api/schedule')
def schedule_create(p:ScheduleCreate,db:Session=Depends(get_db)):
    if not p.title.strip():raise HTTPException(400,'Title cannot be empty')
    return _schedule_json(_save_schedule(db,{'title':p.title.strip(),'date':p.date.strip() or 'TBD','time':p.time.strip() or 'TBD','participants':p.participants.strip(),'agenda':p.agenda.strip()}))
@app.post('/api/schedule/ai')
def schedule_ai(p:AIScheduleIn,db:Session=Depends(get_db)):
    text=p.text.strip()
    if not text:raise HTTPException(400,'Meeting description cannot be empty')
    try: payload=_extract_schedule(text)
    except Exception as e: raise HTTPException(502,'AI scheduling failed: '+str(e))
    if not payload:raise HTTPException(503,'AI scheduling requires an API key, or the AI returned an invalid response.')
    return _schedule_json(_save_schedule(db,payload))
@app.patch('/api/schedule/{sid}/status')
def schedule_status(sid:int,p:ScheduleStatusIn,db:Session=Depends(get_db)):
    m=db.get(ScheduledMeeting,sid)
    if not m:raise HTTPException(404,'Scheduled meeting not found')
    if p.status not in ['scheduled','completed','cancelled']:raise HTTPException(400,'Invalid status')
    m.status=p.status;db.commit();return _schedule_json(m)
@app.delete('/api/schedule/{sid}')
def schedule_delete(sid:int,db:Session=Depends(get_db)):
    m=db.get(ScheduledMeeting,sid)
    if not m:raise HTTPException(404,'Scheduled meeting not found')
    db.delete(m);db.commit();return {'deleted':True,'id':sid}
@app.post('/api/chat')
def chat(p:ChatIn,db:Session=Depends(get_db)):
    q=p.question.strip()
    if not q:raise HTTPException(400,'Question cannot be empty')
    if re.search('schedule',q,re.I) and re.search('meeting',q,re.I):
        payload=_extract_schedule(q)
        if payload:
            m=_save_schedule(db,payload)
            return {'answer':f"Scheduled '{m.title}' on {m.date} at {m.time} with "+(m.participants or 'no listed participants')+'.'}
        return {'answer':"I couldn't schedule that meeting — the AI extraction failed or is temporarily unavailable. Please try again, or use the Schedule page to add it manually."}
    context='\n'.join([f'Meeting: {m.title}\nSummary: {m.summary}\nTranscript: {m.transcript}' for m in db.query(Meeting).all()])+'\nDecisions: '+ '\n'.join(d.text for d in db.query(Decision).all())+'\nTasks: '+ '\n'.join(f'{a.title} owner {a.owner}, due {a.deadline}, status {a.status}, approval {a.approval}' for a in db.query(ActionItem).all())
    try:
        answer=chat_answer(q,context)
        if not answer:raise HTTPException(503,'Chat requires OPENAI_API_KEY. Configure it and restart the server.')
        return {'answer':answer}
    except HTTPException:raise
    except Exception as e:raise HTTPException(502,'AI chat request failed: '+str(e))

_FRONTEND=Path(__file__).resolve().parent.parent/'frontend'
if _FRONTEND.is_dir():
    app.mount('/',StaticFiles(directory=str(_FRONTEND),html=True),name='frontend')
