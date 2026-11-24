from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()
class Meeting(Base):
    __tablename__='meetings'
    id=Column(Integer,primary_key=True); title=Column(String,nullable=False); held_at=Column(String,default=lambda:datetime.utcnow().isoformat()); transcript=Column(Text,nullable=False); summary=Column(Text,default=''); discussion=Column(Text,default='[]'); questions=Column(Text,default='[]')
    decisions=relationship('Decision',back_populates='meeting'); actions=relationship('ActionItem',back_populates='meeting')
class Decision(Base):
    __tablename__='decisions'
    id=Column(Integer,primary_key=True); meeting_id=Column(Integer,ForeignKey('meetings.id')); text=Column(Text,nullable=False); topic=Column(String,default='General'); version=Column(Integer,default=1); status=Column(String,default='active'); created_at=Column(DateTime,default=datetime.utcnow); supersedes_id=Column(Integer,nullable=True)
    meeting=relationship('Meeting',back_populates='decisions')
class Conflict(Base):
    __tablename__='conflicts'
    id=Column(Integer,primary_key=True); previous_decision_id=Column(Integer,ForeignKey('decisions.id')); proposed_text=Column(Text,nullable=False); proposed_meeting_id=Column(Integer,ForeignKey('meetings.id')); topic=Column(String,default='General'); status=Column(String,default='pending'); created_at=Column(DateTime,default=datetime.utcnow)
class ActionItem(Base):
    __tablename__='actions'
    id=Column(Integer,primary_key=True); meeting_id=Column(Integer,ForeignKey('meetings.id')); title=Column(Text,nullable=False); owner=Column(String,default='Unassigned'); deadline=Column(String,default=''); status=Column(String,default='Pending'); approval=Column(String,default='pending'); source_text=Column(Text,default='')
    meeting=relationship('Meeting',back_populates='actions')
class ScheduledMeeting(Base):
    __tablename__='scheduled_meetings'
    id=Column(Integer,primary_key=True); title=Column(String,nullable=False); date=Column(String,nullable=False); time=Column(String,default='TBD'); participants=Column(String,default=''); agenda=Column(String,default=''); status=Column(String,default='scheduled'); created_at=Column(DateTime,default=datetime.utcnow)
