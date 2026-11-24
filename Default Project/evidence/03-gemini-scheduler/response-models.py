from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from .db import Base


class ScheduledMeeting(Base):
    __tablename__ = "scheduled_meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False, default="TBD")
    participants = Column(String, nullable=False, default="")
    agenda = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)