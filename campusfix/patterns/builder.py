from dataclasses import dataclass

# 3. BUILDER: creates an immutable complaint draft after checking required fields.
@dataclass(frozen=True)
class ComplaintDraft:
    reporter_id: int
    title: str
    description: str
    category: str
    location: str
    photo_path: str | None = None

class ComplaintDraftBuilder:
    def __init__(self, reporter_id): self.data={"reporter_id":reporter_id,"photo_path":None}
    def title(self,v): self.data["title"]=(v or "").strip(); return self
    def description(self,v): self.data["description"]=(v or "").strip(); return self
    def category(self,v): self.data["category"]=(v or "").strip(); return self
    def location(self,v): self.data["location"]=(v or "").strip(); return self
    def photo(self,v): self.data["photo_path"]=v or None; return self
    def build(self):
        missing=[k for k in ("reporter_id","title","description","category","location") if not self.data.get(k)]
        if missing: raise ValueError("Please complete all required complaint fields.")
        return ComplaintDraft(**self.data)
