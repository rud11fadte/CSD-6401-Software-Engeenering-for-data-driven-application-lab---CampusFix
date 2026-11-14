from dataclasses import dataclass

# 6. OBSERVER: status change event is broadcast to independent subscribers.
@dataclass
class StatusChangeEvent:
    complaint_id:int
    from_state:str
    to_state:str
    changed_by:int
    timestamp:str
    remark:str

class ComplaintObserver:
    def on_status_changed(self,event): raise NotImplementedError
class StudentNotificationObserver(ComplaintObserver):
    def __init__(self,db): self.db=db
    def on_status_changed(self,e):
        row=self.db.execute("SELECT reporter_id FROM complaints WHERE id=?",(e.complaint_id,)).fetchone()
        if row:
            from .decorator import NotifierFactory
            NotifierFactory.for_user(self.db).send(row["reporter_id"],e.complaint_id,
                f"Complaint #{e.complaint_id} is now {e.to_state}.")
class StaffNotificationObserver(ComplaintObserver):
    def __init__(self,db): self.db=db
    def on_status_changed(self,e):
        row=self.db.execute("SELECT assignee_id FROM complaints WHERE id=?",(e.complaint_id,)).fetchone()
        if row and row["assignee_id"]: self.db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",
          (row["assignee_id"],e.complaint_id,f"Complaint #{e.complaint_id} status changed to {e.to_state}.","In-app"))
class DashboardObserver(ComplaintObserver):
    def on_status_changed(self,e): return None
class AuditLogObserver(ComplaintObserver):
    def __init__(self,db): self.db=db
    def on_status_changed(self,e):
        self.db.execute("INSERT INTO status_history(complaint_id,from_state,to_state,changed_by,remark) VALUES(?,?,?,?,?)",
          (e.complaint_id,e.from_state,e.to_state,e.changed_by,e.remark))
class ComplaintSubject:
    def __init__(self,observers): self.observers=list(observers)
    def attach(self,o): self.observers.append(o)
    def detach(self,o): self.observers.remove(o)
    def notify(self,event):
        errors=[]
        for o in self.observers:
            try: o.on_status_changed(event)
            except Exception as exc: errors.append(str(exc))
        return errors
