class ComplaintRepository:
    def __init__(self,db):self.db=db
    def create(self,draft,priority):
        cur=self.db.execute("""INSERT INTO complaints(title,description,category,location,photo_path,reporter_id,priority)
          VALUES(?,?,?,?,?,?,?)""",(draft.title,draft.description,draft.category,draft.location,draft.photo_path,draft.reporter_id,priority))
        return cur.lastrowid
    def get(self,cid):return self.db.execute("SELECT * FROM complaints WHERE id=?",(cid,)).fetchone()
    def for_student(self,uid,search="",status="All"):
        sql="SELECT c.*,u.name assignee_name FROM complaints c LEFT JOIN users u ON u.id=c.assignee_id WHERE c.reporter_id=?"
        args=[uid]
        if search:sql+=" AND (c.title LIKE ? OR c.location LIKE ? OR CAST(c.id AS TEXT)=?)";args += [f"%{search}%",f"%{search}%",search]
        if status!="All":sql+=" AND c.status=?";args.append(status)
        return self.db.execute(sql+" ORDER BY c.id DESC",args).fetchall()
    def all(self,search="",status="All"):
        sql="""SELECT c.*,r.name reporter_name,s.name assignee_name FROM complaints c
          JOIN users r ON r.id=c.reporter_id LEFT JOIN users s ON s.id=c.assignee_id WHERE 1=1"""
        args=[]
        if search:sql+=" AND (c.title LIKE ? OR c.location LIKE ? OR r.name LIKE ? OR CAST(c.id AS TEXT)=?)";args += [f"%{search}%",f"%{search}%",f"%{search}%",search]
        if status!="All":sql+=" AND c.status=?";args.append(status)
        return self.db.execute(sql+" ORDER BY c.id DESC",args).fetchall()
    def for_staff(self,uid,search="",status="All"):
        sql="SELECT c.*,r.name reporter_name FROM complaints c JOIN users r ON r.id=c.reporter_id WHERE c.assignee_id=?"
        args=[uid]
        if search:sql+=" AND (c.title LIKE ? OR c.location LIKE ? OR CAST(c.id AS TEXT)=?)";args += [f"%{search}%",f"%{search}%",search]
        if status!="All":sql+=" AND c.status=?";args.append(status)
        return self.db.execute(sql+" ORDER BY c.id DESC",args).fetchall()
