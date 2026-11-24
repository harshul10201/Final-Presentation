from .models import Meeting,Decision,Conflict,ActionItem
from .ai_engine import topic_for
from datetime import datetime

def seed(db):
    if db.query(Meeting).count(): return
    t1='''Maya: We reviewed launch readiness. QA has passed core flows.\nAlex: We agreed the launch date is 10 December 2026.\nMaya: Alex will prepare release notes by 2 December.\nAlex: I will prepare release notes by 2 December.\nPriya: Any risks with analytics?'''
    t2='''Maya: In this ad-hoc sync, the launch date moves to 15 December 2026 due to analytics validation.\nAlex: I will coordinate the validation checklist by 5 December.\nPriya: We need to confirm partner readiness.'''
    m1=Meeting(title='Launch Readiness Review',held_at='2026-11-20',transcript=t1,summary='Core QA flows passed. Launch date agreed for 10 December 2026. Release notes assigned to Alex.',discussion='["QA passed core flows","Launch planned for 10 December"]',questions='["Any risks with analytics?"]');db.add(m1);db.flush()
    d1=Decision(meeting_id=m1.id,text='Launch date: 10 December 2026',topic='Launch date',version=1,status='active');db.add(d1)
    db.add(ActionItem(meeting_id=m1.id,title='Prepare release notes',owner='Alex',deadline='2026-12-02',status='Pending',approval='approved',source_text='Alex: I will prepare release notes by 2 December.'))
    m2=Meeting(title='Ad-hoc Analytics Sync',held_at='2026-11-23',transcript=t2,summary='Analytics validation shifted launch to 15 December 2026; checklist assigned to Alex.',discussion='["Analytics validation required","Proposed launch date is 15 December"]',questions='["Confirm partner readiness"]');db.add(m2);db.flush()
    db.add(Conflict(previous_decision_id=d1.id,proposed_text='Launch date: 15 December 2026',proposed_meeting_id=m2.id,topic='Launch date'))
    db.add(ActionItem(meeting_id=m2.id,title='Coordinate validation checklist',owner='Alex',deadline='2026-12-05',status='Pending',approval='pending',source_text='Alex: I will coordinate the validation checklist by 5 December.'))
    db.commit()
