# 8. STRATEGY: interchangeable assignment algorithms.
class AssignmentStrategy:
    name="Base"
    def choose(self,complaint,staff_list): raise NotImplementedError
class SkillMatchStrategy(AssignmentStrategy):
    name="Skill match"
    def choose(self,c,staff): return next((s for s in staff if s["skill"]==c["category"]),None)
class LeastLoadedStrategy(AssignmentStrategy):
    name="Least loaded"
    def choose(self,c,staff): return min(staff,key=lambda s:s["open_count"]) if staff else None
class RoundRobinStrategy(AssignmentStrategy):
    name="Round robin"; last=-1
    def choose(self,c,staff):
        if not staff:return None
        type(self).last=(type(self).last+1)%len(staff)
        return staff[type(self).last]
class ZoneBasedStrategy(AssignmentStrategy):
    name="Zone based"
    def choose(self,c,staff):
        loc=c["location"].strip().lower()
        return next((s for s in staff if s["building"].strip().lower()==loc),None)
class CompositeStrategy(AssignmentStrategy):
    name="Skill match + least loaded"
    def choose(self,c,staff):
        pool=[s for s in staff if s["skill"]==c["category"]] or staff
        return min(pool,key=lambda s:s["open_count"]) if pool else None
class AssignmentService:
    def __init__(self,strategy=None): self.strategy=strategy or SkillMatchStrategy()
    def set_strategy(self,strategy): self.strategy=strategy
    def assign(self,complaint,staff): return self.strategy.choose(complaint,staff)
