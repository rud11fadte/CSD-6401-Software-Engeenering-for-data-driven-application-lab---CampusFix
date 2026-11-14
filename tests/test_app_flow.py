import os
import tempfile
import unittest
from campusfix import create_app

class CampusFixFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_path=os.path.join(self.temp.name,"test.sqlite3")
        self.uploads=os.path.join(self.temp.name,"uploads")
        self.app=create_app({"TESTING":True,"DATABASE":self.db_path,"UPLOAD_FOLDER":self.uploads,"SECRET_KEY":"test"})
        self.client=self.app.test_client()
    def tearDown(self): self.temp.cleanup()
    def login(self,email,password):
        return self.client.post("/login",data={"email":email,"password":password},follow_redirects=True)
    def test_student_submit_admin_assign_staff_resolve(self):
        response=self.login("student@campusfix.test","student123")
        self.assertEqual(response.status_code,200)
        response=self.client.post("/complaints",data={
            "title":"Classroom fan not working",
            "description":"The ceiling fan in this classroom is not rotating.",
            "category":"Electrical","location":"Block A"
        },follow_redirects=True)
        self.assertEqual(response.status_code,200)
        with self.app.app_context():
            from campusfix.db import get_db
            complaint=get_db().execute("SELECT * FROM complaints ORDER BY id DESC").fetchone()
            self.assertEqual(complaint["status"],"New")
            cid=complaint["id"]
        self.client.get("/logout")
        self.login("admin@campusfix.test","admin123")
        response=self.client.post(f"/complaints/{cid}/assign",data={"strategy":"Skill match"},follow_redirects=True)
        self.assertEqual(response.status_code,200)
        self.client.get("/logout")
        self.login("electric@campusfix.test","staff123")
        self.client.post(f"/complaints/{cid}/status",data={"action":"start","remark":"Work started"},follow_redirects=True)
        self.client.post(f"/complaints/{cid}/status",data={"action":"resolve","remark":"Fan repaired"},follow_redirects=True)
        with self.app.app_context():
            from campusfix.db import get_db
            row=get_db().execute("SELECT status FROM complaints WHERE id=?",(cid,)).fetchone()
            self.assertEqual(row["status"],"Resolved")
            count=get_db().execute("SELECT COUNT(*) FROM status_history WHERE complaint_id=?",(cid,)).fetchone()[0]
            self.assertGreaterEqual(count,3)

if __name__=="__main__":unittest.main()
