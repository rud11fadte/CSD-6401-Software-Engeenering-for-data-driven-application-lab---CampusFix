import sqlite3
import unittest
from campusfix.patterns.singleton import AppConfig
from campusfix.patterns.builder import ComplaintDraftBuilder
from campusfix.patterns.factory import ComplaintCreatorRegistry,ElectricalComplaint
from campusfix.patterns.state import next_state
from campusfix.patterns.strategy import AssignmentService,SkillMatchStrategy,LeastLoadedStrategy
from campusfix.patterns.chain import build_validation_chain
from campusfix.patterns.decorator import NotifierFactory
from campusfix.patterns.observer import (StatusChangeEvent,ComplaintSubject,StudentNotificationObserver,
    StaffNotificationObserver,DashboardObserver,AuditLogObserver)
from campusfix.patterns.command import ChangePriorityCommand,CommandHistory

class PatternTests(unittest.TestCase):
    def draft(self):
        return (ComplaintDraftBuilder(1).title("Broken classroom fan")
            .description("The ceiling fan in this classroom is not rotating.")
            .category("Electrical").location("Block A").build())

    def test_singleton(self): self.assertIs(AppConfig(),AppConfig())

    def test_builder_and_factory(self):
        with self.assertRaises(ValueError): ComplaintDraftBuilder(1).build()
        complaint=ComplaintCreatorRegistry().creator_for("Electrical").create(self.draft())
        self.assertIsInstance(complaint,ElectricalComplaint)
        self.assertEqual(complaint.priority,"High")
        self.assertEqual(complaint.required_skill,"Electrical")

    def test_chain_validation(self):
        db=sqlite3.connect(":memory:")
        db.row_factory=sqlite3.Row
        db.execute("""CREATE TABLE complaints(id INTEGER PRIMARY KEY,reporter_id INTEGER,category TEXT,location TEXT,status TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        build_validation_chain().handle(self.draft(),{"authenticated_student":True,"db":db})
        with self.assertRaises(ValueError):
            build_validation_chain().handle(self.draft(),{"authenticated_student":False,"db":db})

    def test_state_pattern(self):
        self.assertEqual(next_state("New","assign"),"Assigned")
        self.assertEqual(next_state("Assigned","start"),"In Progress")
        with self.assertRaises(ValueError):next_state("Closed","reopen")

    def test_strategy_pattern(self):
        c={"category":"Electrical","location":"Block A"}
        staff=[{"skill":"Plumbing","building":"Block A","open_count":0},
               {"skill":"Electrical","building":"Block B","open_count":2}]
        service=AssignmentService(SkillMatchStrategy())
        self.assertEqual(service.assign(c,staff)["skill"],"Electrical")
        service.set_strategy(LeastLoadedStrategy())
        self.assertEqual(service.assign(c,staff)["open_count"],0)

    def test_decorator_and_observer(self):
        db=sqlite3.connect(":memory:")
        db.row_factory=sqlite3.Row
        db.executescript("""
          CREATE TABLE users(id INTEGER PRIMARY KEY);
          CREATE TABLE complaints(id INTEGER PRIMARY KEY,reporter_id INTEGER,assignee_id INTEGER);
          CREATE TABLE notifications(id INTEGER PRIMARY KEY,user_id INTEGER,complaint_id INTEGER,message TEXT,channel TEXT);
          CREATE TABLE status_history(id INTEGER PRIMARY KEY,complaint_id INTEGER,from_state TEXT,to_state TEXT,changed_by INTEGER,remark TEXT);
          INSERT INTO users(id) VALUES(1),(2);
          INSERT INTO complaints(id,reporter_id,assignee_id) VALUES(10,1,2);
        """)
        NotifierFactory.for_user(db).send(1,10,"Test notification")
        channels={r[0] for r in db.execute("SELECT channel FROM notifications")}
        self.assertTrue({"In-app","Email","SMS","Log"}.issubset(channels))
        event=StatusChangeEvent(10,"New","Assigned",2,"2026-01-01T10:00:00","Assigned")
        subject=ComplaintSubject([StudentNotificationObserver(db),StaffNotificationObserver(db),DashboardObserver(),AuditLogObserver(db)])
        self.assertEqual(subject.notify(event),[])
        self.assertGreaterEqual(db.execute("SELECT COUNT(*) FROM status_history").fetchone()[0],1)

    def test_command_undo_redo_across_connections(self):
        db=sqlite3.connect(":memory:")
        db.row_factory=sqlite3.Row
        db.executescript("""
          CREATE TABLE complaints(id INTEGER PRIMARY KEY,priority TEXT,updated_at TEXT);
          CREATE TABLE admin_actions(id INTEGER PRIMARY KEY,admin_id INTEGER,command_type TEXT,complaint_id INTEGER,before_value TEXT,after_value TEXT,description TEXT,undone INTEGER DEFAULT 0);
          INSERT INTO complaints(id,priority) VALUES(7,'Medium');
        """)
        history=CommandHistory()
        history.run(ChangePriorityCommand(db,99,7,"High"))
        self.assertEqual(db.execute("SELECT priority FROM complaints WHERE id=7").fetchone()[0],"High")
        # Undo/redo receive the current request's connection, not a stale closed connection.
        self.assertIn("priority",history.undo(db).lower())
        self.assertEqual(db.execute("SELECT priority FROM complaints WHERE id=7").fetchone()[0],"Medium")
        history.redo(db)
        self.assertEqual(db.execute("SELECT priority FROM complaints WHERE id=7").fetchone()[0],"High")

if __name__=="__main__":unittest.main()
