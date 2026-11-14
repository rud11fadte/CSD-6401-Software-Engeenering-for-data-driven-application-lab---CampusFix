# 7. STATE: named states own the allowed actions for a complaint.
class ComplaintState:
    name="Unknown"
    allowed={}
    def transition(self,action):
        target=self.allowed.get(action)
        if not target: raise ValueError(f"Action '{action}' is not allowed while complaint is {self.name}.")
        return StateFactory.from_name(target)
class NewState(ComplaintState):
    name="New"; allowed={"assign":"Assigned","reject":"Rejected"}
class AssignedState(ComplaintState):
    name="Assigned"; allowed={"assign":"Assigned","start":"In Progress","reject":"Rejected"}
class InProgressState(ComplaintState):
    name="In Progress"; allowed={"resolve":"Resolved"}
class ResolvedState(ComplaintState):
    name="Resolved"; allowed={"close":"Closed","reopen":"In Progress"}
class ClosedState(ComplaintState):
    name="Closed"; allowed={}
class RejectedState(ComplaintState):
    name="Rejected"; allowed={}
class StateFactory:
    states={s.name:s for s in [NewState(),AssignedState(),InProgressState(),ResolvedState(),ClosedState(),RejectedState()]}
    @classmethod
    def from_name(cls,name):
        if name not in cls.states: raise ValueError("Unknown complaint state.")
        return cls.states[name]
def next_state(current,action): return StateFactory.from_name(current).transition(action).name
