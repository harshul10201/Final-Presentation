import json
import re
from typing import Literal, Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .ai_engine import call_llm, chat_answer
from .db import Base, engine, get_db
from .models import ScheduledMeeting

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MeetFlow AI")

SCHEDULE_SYSTEM_PROMPT = (
    "You extract structured meeting details from user text. "
    'Return ONLY valid JSON with exact keys: '
    '{"title": "...", "date": "YYYY-MM-DD", "time": "HH:MM", "participants": "...", "agenda": "..."}. '
    'Normalize date to YYYY-MM-DD ("TBD" if missing or unclear). '
    'Normalize time to 24-hour HH:MM ("TBD" if missing). '
    "Never invent participants that are not explicitly mentioned in the text. "
    "Use empty string \"\" for participants or agenda if not mentioned."
)

ALLOWED_STATUSES = {"scheduled", "completed", "cancelled"}


class ScheduleCreateRequest(BaseModel):
    title: str
    date: str
    time: str = "TBD"
    participants: str = ""
    agenda: str = ""


class AIScheduleRequest(BaseModel):
    text: str


class StatusUpdateRequest(BaseModel):
    status: Literal["scheduled", "completed", "cancelled"]


class ChatRequest(BaseModel):
    question: str


def _parse_schedule_payload(raw_result) -> Optional[dict]:
    if raw_result is None:
        return None
    if isinstance(raw_result, dict):
        data = raw_result
    elif isinstance(raw_result, str):
        cleaned = raw_result.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None
    else:
        return None

    if not isinstance(data, dict):
        return None

    title = str(data.get("title") or "").strip() or "Untitled Meeting"
    date = str(data.get("date") or "TBD").strip() or "TBD"
    time = str(data.get("time") or "TBD").strip() or "TBD"
    participants = str(data.get("participants") or "").strip()
    agenda = str(data.get("agenda") or "").strip()

    return {
        "title": title,
        "date": date,
        "time": time,
        "participants": participants,
        "agenda": agenda,
    }


def _extract_meeting_with_ai(text: str, parse_json: bool = False) -> Optional[dict]:
    if parse_json:
        raw = call_llm(SCHEDULE_SYSTEM_PROMPT, text, parse_json=True)
    else:
        raw = call_llm(SCHEDULE_SYSTEM_PROMPT, text)
    return _parse_schedule_payload(raw)


def _create_meeting_record(db: Session, payload: dict) -> ScheduledMeeting:
    meeting = ScheduledMeeting(
        title=payload["title"],
        date=payload["date"],
        time=payload["time"],
        participants=payload["participants"],
        agenda=payload["agenda"],
        status="scheduled",
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@app.get("/api/schedule")
def list_scheduled_meetings(db: Session = Depends(get_db)):
    meetings = db.query(ScheduledMeeting).order_by(ScheduledMeeting.id.desc()).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "date": m.date,
            "time": m.time,
            "participants": m.participants,
            "agenda": m.agenda,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in meetings
    ]


@app.post("/api/schedule")
def create_manual_meeting(body: ScheduleCreateRequest, db: Session = Depends(get_db)):
    payload = {
        "title": body.title.strip() or "Untitled Meeting",
        "date": body.date.strip() or "TBD",
        "time": body.time.strip() or "TBD",
        "participants": body.participants.strip(),
        "agenda": body.agenda.strip(),
    }
    meeting = _create_meeting_record(db, payload)
    return {
        "id": meeting.id,
        "title": meeting.title,
        "date": meeting.date,
        "time": meeting.time,
        "participants": meeting.participants,
        "agenda": meeting.agenda,
        "status": meeting.status,
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
    }


@app.post("/api/schedule/ai")
def create_ai_meeting(body: AIScheduleRequest, db: Session = Depends(get_db)):
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Meeting description text is required.")

    try:
        payload = _extract_meeting_with_ai(text, parse_json=False)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI scheduling failed: {exc}")

    if not payload:
        raise HTTPException(status_code=502, detail="AI scheduling returned an invalid or empty response.")

    meeting = _create_meeting_record(db, payload)
    return {
        "id": meeting.id,
        "title": meeting.title,
        "date": meeting.date,
        "time": meeting.time,
        "participants": meeting.participants,
        "agenda": meeting.agenda,
        "status": meeting.status,
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
    }


@app.patch("/api/schedule/{meeting_id}/status")
def update_meeting_status(meeting_id: int, body: StatusUpdateRequest, db: Session = Depends(get_db)):
    if body.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status value.")

    meeting = db.query(ScheduledMeeting).filter(ScheduledMeeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Scheduled meeting not found.")

    meeting.status = body.status
    db.commit()
    db.refresh(meeting)
    return {
        "id": meeting.id,
        "title": meeting.title,
        "date": meeting.date,
        "time": meeting.time,
        "participants": meeting.participants,
        "agenda": meeting.agenda,
        "status": meeting.status,
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
    }


@app.delete("/api/schedule/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(ScheduledMeeting).filter(ScheduledMeeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Scheduled meeting not found.")

    db.delete(meeting)
    db.commit()
    return {"deleted": True, "id": meeting_id}


@app.post("/api/chat")
def chat_endpoint(body: ChatRequest, db: Session = Depends(get_db)):
    question = body.question or ""
    q_lower = question.lower()
    if "schedule" in q_lower and "meeting" in q_lower:
        try:
            payload = _extract_meeting_with_ai(question, parse_json=True)
            if payload:
                meeting = _create_meeting_record(db, payload)
                participants_label = meeting.participants or "no listed participants"
                return {
                    "answer": (
                        f"Scheduled '{meeting.title}' on {meeting.date} "
                        f"at {meeting.time} with {participants_label}."
                    )
                }
        except Exception:
            pass

    return {"answer": chat_answer(question, db)}