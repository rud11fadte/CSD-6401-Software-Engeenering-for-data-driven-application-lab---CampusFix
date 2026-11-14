from datetime import datetime
from ..repositories.complaint_repository import ComplaintRepository
from ..patterns.builder import ComplaintDraftBuilder
from ..patterns.factory import ComplaintCreatorRegistry
from ..patterns.chain import build_validation_chain
from ..patterns.state import next_state
from ..patterns.observer import (StatusChangeEvent,ComplaintSubject,StudentNotificationObserver,
    StaffNotificationObserver,DashboardObserver,AuditLogObserver)
from ..patterns.decorator import NotifierFactory

# 5. FACADE: controllers call this interface instead of reaching into domain/pattern code.
class CampusFixFacade:
    def __init__(self,db):
        self.db=db
        self.complaints=ComplaintRepository(db)
        self.creators=ComplaintCreatorRegistry()
    def submit_complaint(self,student_id,form,photo_path=None):
        draft=(ComplaintDraftBuilder(student_id).title(form.get("title")).description(form.get("description"))
            .category(form.get("category")).location(form.get("location")).photo(photo_path).build())
        build_validation_chain().handle(draft,{"authenticated_student":True,"db":self.db})
        created=self.creators.creator_for(draft.category).create(draft)
        cid=self.complaints.create(draft,created.priority)
        self.db.execute("INSERT INTO status_history(complaint_id,from_state,to_state,changed_by,remark) VALUES(?,?,?,?,?)",
            (cid,None,"New",student_id,"Complaint submitted"))
        self._notify(student_id,cid,f"Your complaint #{cid} has been submitted.")
        return cid
    def transition(self,complaint,action,actor_id,remark=""):
        new_state=next_state(complaint["status"],action)
        old_state=complaint["status"]
        self.db.execute("UPDATE complaints SET status=?,updated_at=CURRENT_TIMESTAMP,resolution_note=? WHERE id=?",
            (new_state,remark if new_state=="Resolved" else complaint["resolution_note"],complaint["id"]))
        event=StatusChangeEvent(complaint["id"],old_state,new_state,actor_id,datetime.now().isoformat(timespec="seconds"),remark)
        subject=ComplaintSubject([StudentNotificationObserver(self.db),StaffNotificationObserver(self.db),
            DashboardObserver(),AuditLogObserver(self.db)])
        observer_errors=subject.notify(event)
        # Decorator chain persists in-app, simulated email/SMS and logging records.
        return new_state,observer_errors
    def _notify(self,user_id,cid,message):
        NotifierFactory.for_user(self.db).send(user_id,cid,message)
    def reject(self,complaint,admin_id,reason):
        if complaint["status"] not in ("New","Assigned"):
            raise ValueError("Only new or assigned complaints can be rejected.")
        self.db.execute("UPDATE complaints SET status='Rejected',rejected_reason=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (reason,complaint["id"]))
        event=StatusChangeEvent(complaint["id"],complaint["status"],"Rejected",admin_id,
            datetime.now().isoformat(timespec="seconds"),reason)
        ComplaintSubject([StudentNotificationObserver(self.db),StaffNotificationObserver(self.db),
            DashboardObserver(),AuditLogObserver(self.db)]).notify(event)
        self._notify(complaint["reporter_id"],complaint["id"],f"Complaint #{complaint['id']} was rejected: {reason}")
