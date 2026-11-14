class UserRepository:
    def __init__(self,db):self.db=db
    def by_email(self,email):return self.db.execute("SELECT * FROM users WHERE lower(email)=lower(?)",(email.strip(),)).fetchone()
    def by_id(self,uid):return self.db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    def create_student(self,name,email,password_hash):
        cur=self.db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,'student')",(name,email.lower(),password_hash))
        return cur.lastrowid
    def staff(self):
        return self.db.execute("""SELECT u.*,(SELECT COUNT(*) FROM complaints c WHERE c.assignee_id=u.id
          AND c.status NOT IN ('Resolved','Closed','Rejected')) open_count FROM users u WHERE role='staff' ORDER BY u.name""").fetchall()
