from dataclasses import dataclass

# 2. FACTORY METHOD: registry selects a concrete complaint creator by category.
@dataclass
class Complaint:
    draft: object
    priority: str
    required_skill: str
    sla_hours: int

class ElectricalComplaint(Complaint): pass
class PlumbingComplaint(Complaint): pass
class NetworkComplaint(Complaint): pass
class FurnitureComplaint(Complaint): pass
class GeneralComplaint(Complaint): pass

class ComplaintCreator:
    def create(self,draft): raise NotImplementedError
class ElectricalComplaintCreator(ComplaintCreator):
    def create(self,d): return ElectricalComplaint(d,"High","Electrical",8)
class PlumbingComplaintCreator(ComplaintCreator):
    def create(self,d): return PlumbingComplaint(d,"Medium","Plumbing",24)
class NetworkComplaintCreator(ComplaintCreator):
    def create(self,d): return NetworkComplaint(d,"High","Network",8)
class FurnitureComplaintCreator(ComplaintCreator):
    def create(self,d): return FurnitureComplaint(d,"Low","Furniture",48)
class GeneralComplaintCreator(ComplaintCreator):
    def create(self,d): return GeneralComplaint(d,"Medium","General",24)

class ComplaintCreatorRegistry:
    def __init__(self):
        self.creators={"Electrical":ElectricalComplaintCreator(),"Plumbing":PlumbingComplaintCreator(),
          "Network":NetworkComplaintCreator(),"Furniture":FurnitureComplaintCreator(),"General":GeneralComplaintCreator()}
    def register(self,category,creator): self.creators[category]=creator
    def creator_for(self,category):
        if category not in self.creators: raise ValueError("Select a valid complaint category.")
        return self.creators[category]
