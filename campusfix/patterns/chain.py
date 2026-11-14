from .singleton import AppConfig

# 10. CHAIN OF RESPONSIBILITY: validation runs in a fixed order; an error stops the chain.
class ValidationHandler:
    def __init__(self): self.next=None
    def link_with(self,nxt): self.next=nxt; return nxt
    def handle(self,draft,context):
        self.check(draft,context)
        if self.next: self.next.handle(draft,context)
    def check(self,draft,context): raise NotImplementedError

class AuthHandler(ValidationHandler):
    def check(self,d,c):
        if not c.get("authenticated_student"): raise ValueError("Only logged-in students can submit complaints.")
class InputHandler(ValidationHandler):
    def check(self,d,c):
        if len(d.title)<4: raise ValueError("Title must contain at least 4 characters.")
        if len(d.description)<10: raise ValueError("Description must contain at least 10 characters.")
        if len(d.location)<2: raise ValueError("Enter a valid campus location.")
class DuplicateHandler(ValidationHandler):
    def check(self,d,c):
        hours=AppConfig().get_int("duplicate_window_hours",24)
        row=c["db"].execute("""SELECT id FROM complaints WHERE reporter_id=? AND category=? AND lower(location)=lower(?)
          AND status NOT IN ('Resolved','Closed','Rejected') AND created_at>=datetime('now',?) LIMIT 1""",
          (d.reporter_id,d.category,d.location,f"-{hours} hours")).fetchone()
        if row: raise ValueError(f"A similar open complaint already exists (#{row['id']}).")
class RateLimitHandler(ValidationHandler):
    def check(self,d,c):
        limit=AppConfig().get_int("daily_complaint_limit",5)
        n=c["db"].execute("SELECT COUNT(*) FROM complaints WHERE reporter_id=? AND date(created_at)=date('now')",(d.reporter_id,)).fetchone()[0]
        if n>=limit: raise ValueError(f"Daily complaint limit reached ({limit}).")
class LanguageFilterHandler(ValidationHandler):
    BLOCKED={"idiot","stupid","abuseword"}
    def check(self,d,c):
        words=set((d.title+" "+d.description).lower().split())
        if words & self.BLOCKED: raise ValueError("Please remove abusive language and submit again.")

def build_validation_chain():
    a,b,c,d,e=AuthHandler(),InputHandler(),DuplicateHandler(),RateLimitHandler(),LanguageFilterHandler()
    a.link_with(b).link_with(c).link_with(d).link_with(e)
    return a
