# 9. COMMAND: assignment and priority changes can be reversed and replayed.
class Command:
    def execute(self): raise NotImplementedError
    def undo(self): raise NotImplementedError
    def describe(self): raise NotImplementedError
class ChangeFieldCommand(Command):
    def __init__(self,db,admin_id,cid,field,new_value,description):
        if field not in {"priority","assignee_id"}:raise ValueError("Unsupported command.")
        row=db.execute(f"SELECT {field} FROM complaints WHERE id=?",(cid,)).fetchone()
        if not row:raise ValueError("Complaint not found.")
        self.db,self.admin_id,self.cid,self.field=db,admin_id,cid,field
        self.before,self.after,self.label=row[field],new_value,description
        self.action_id=None
    def execute(self):
        self.db.execute(f"UPDATE complaints SET {self.field}=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(self.after,self.cid))
    def undo(self):
        self.db.execute(f"UPDATE complaints SET {self.field}=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(self.before,self.cid))
    def describe(self):return self.label
    def persist(self):
        cur=self.db.execute("INSERT INTO admin_actions(admin_id,command_type,complaint_id,before_value,after_value,description) VALUES(?,?,?,?,?,?)",
          (self.admin_id,self.field,self.cid,str(self.before),str(self.after),self.label))
        self.action_id=cur.lastrowid
class CommandHistory:
    """Stores action IDs, not live DB connections, so it works across Flask requests."""
    def __init__(self): self.undo_stack=[]; self.redo_stack=[]
    def run(self,cmd):
        cmd.execute()
        cmd.persist()
        ids=getattr(cmd,"action_ids",None) or [cmd.action_id]
        self.undo_stack.append(ids)
        self.redo_stack.clear()
    def _apply(self,db,action_id,use_before):
        row=db.execute("SELECT * FROM admin_actions WHERE id=?",(action_id,)).fetchone()
        if not row: raise ValueError("The command history entry is no longer available.")
        value=row["before_value"] if use_before else row["after_value"]
        field=row["command_type"]
        if field not in {"priority","assignee_id","status"}: raise ValueError("Unknown command type in history.")
        if field=="assignee_id": value=int(value) if value not in (None,"None","") else None
        db.execute(f"UPDATE complaints SET {field}=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(value,row["complaint_id"]))
        db.execute("UPDATE admin_actions SET undone=? WHERE id=?",(1 if use_before else 0,action_id))
        return row["description"]
    def undo(self,db):
        if not self.undo_stack:return None
        action_ids=self.undo_stack.pop()
        descriptions=[self._apply(db,action_id,True) for action_id in reversed(action_ids)]
        self.redo_stack.append(action_ids)
        return descriptions[-1] if descriptions else None
    def redo(self,db):
        if not self.redo_stack:return None
        action_ids=self.redo_stack.pop()
        descriptions=[self._apply(db,action_id,False) for action_id in action_ids]
        self.undo_stack.append(action_ids)
        return descriptions[-1] if descriptions else None


class AssignCommand(ChangeFieldCommand):
    def __init__(self,db,admin_id,cid,new_staff_id,description):
        super().__init__(db,admin_id,cid,"assignee_id",new_staff_id,description)

class ChangePriorityCommand(ChangeFieldCommand):
    def __init__(self,db,admin_id,cid,new_priority):
        super().__init__(db,admin_id,cid,"priority",new_priority,f"Change priority for complaint #{cid}")

class ChangeStatusCommand(Command):
    def __init__(self,db,admin_id,cid,new_status,description):
        row=db.execute("SELECT status FROM complaints WHERE id=?",(cid,)).fetchone()
        if not row: raise ValueError("Complaint not found.")
        self.db,self.admin_id,self.cid=db,admin_id,cid
        self.before,self.after,self.label=row["status"],new_status,description
        self.action_id=None
    def execute(self):
        self.db.execute("UPDATE complaints SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(self.after,self.cid))
    def undo(self):
        self.db.execute("UPDATE complaints SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(self.before,self.cid))
    def describe(self): return self.label
    def persist(self):
        cur=self.db.execute("INSERT INTO admin_actions(admin_id,command_type,complaint_id,before_value,after_value,description) VALUES(?,?,?,?,?,?)",
            (self.admin_id,"status",self.cid,self.before,self.after,self.label))
        self.action_id=cur.lastrowid

class BulkAssignCommand(Command):
    def __init__(self,commands):
        self.commands=list(commands)
        self.action_ids=[]
    def execute(self):
        self.action_ids=[]
        for command in self.commands:
            command.execute()
            command.persist()
            self.action_ids.append(command.action_id)
    def persist(self): return None  # Child commands each store their own audit record.
    def undo(self):
        for command in reversed(self.commands): command.undo()
    def describe(self): return f"Bulk assignment ({len(self.commands)} complaints)"
