import uuid
from pathlib import Path
from flask import render_template,request,redirect,url_for,session,flash,abort,current_app,send_from_directory
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from .db import get_db
from .repositories.user_repository import UserRepository
from .repositories.complaint_repository import ComplaintRepository
from .services.campusfix_facade import CampusFixFacade
from .patterns.strategy import (AssignmentService,SkillMatchStrategy,LeastLoadedStrategy,
    RoundRobinStrategy,ZoneBasedStrategy,CompositeStrategy)
from .patterns.command import AssignCommand,ChangePriorityCommand,CommandHistory

HISTORIES={}
STRATEGIES={"Skill match":SkillMatchStrategy,"Least loaded":LeastLoadedStrategy,
    "Round robin":RoundRobinStrategy,"Zone based":ZoneBasedStrategy,
    "Skill + least loaded":CompositeStrategy}
STATUSES=["All","New","Assigned","In Progress","Resolved","Closed","Rejected"]

def current_history():
    uid=session.get("user_id")
    if uid not in HISTORIES:HISTORIES[uid]=CommandHistory()
    return HISTORIES[uid]

def login_required(role=None):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapped(*args,**kwargs):
            if not session.get("user_id"):return redirect(url_for("login"))
            if role and session.get("role")!=role:abort(403)
            return fn(*args,**kwargs)
        return wrapped
    return decorator

def save_photo(file):
    if not file or not file.filename:return None
    ext=Path(file.filename).suffix.lower().lstrip(".")
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        raise ValueError("Photo must be PNG, JPG, JPEG or WEBP.")
    name=f"{uuid.uuid4().hex}.{ext}"
    file.save(Path(current_app.config["UPLOAD_FOLDER"])/secure_filename(name))
    return name

def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {"statuses":STATUSES,"categories":["Electrical","Plumbing","Network","Furniture","General"]}

    @app.get("/")
    def index():
        return redirect(url_for("dashboard")) if session.get("user_id") else redirect(url_for("login"))

    @app.route("/register",methods=["GET","POST"])
    def register():
        if request.method=="POST":
            name=request.form.get("name","").strip()
            email=request.form.get("email","").strip().lower()
            password=request.form.get("password","")
            if len(name)<2 or "@" not in email or len(password)<8:
                flash("Enter your name, a valid email and a password of at least 8 characters.","error")
            else:
                db=get_db()
                try:
                    uid=UserRepository(db).create_student(name,email,generate_password_hash(password))
                    db.commit()
                    session.clear();session.update(user_id=uid,role="student",name=name)
                    flash("Your student account is ready. Welcome to CampusFix!","success")
                    return redirect(url_for("dashboard"))
                except Exception:
                    db.rollback();flash("That email is already registered. Please sign in.","error")
        return render_template("register.html")

    @app.route("/login",methods=["GET","POST"])
    def login():
        if request.method=="POST":
            user=UserRepository(get_db()).by_email(request.form.get("email",""))
            if not user or not check_password_hash(user["password_hash"],request.form.get("password","")):
                flash("Email or password is incorrect.","error")
            else:
                session.clear();session.update(user_id=user["id"],role=user["role"],name=user["name"])
                return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.get("/logout")
    def logout():
        session.clear();return redirect(url_for("login"))

    @app.get("/dashboard")
    @login_required()
    def dashboard():
        db=get_db();role=session["role"];uid=session["user_id"]
        search=request.args.get("q","").strip();status=request.args.get("status","All")
        repo=ComplaintRepository(db)
        if status not in STATUSES:status="All"
        if role=="student":rows=repo.for_student(uid,search,status)
        elif role=="staff":rows=repo.for_staff(uid,search,status)
        else:rows=repo.all(search,status)
        stats={
            "total":db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
            "open":db.execute("SELECT COUNT(*) FROM complaints WHERE status NOT IN ('Resolved','Closed','Rejected')").fetchone()[0],
            "resolved":db.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Resolved','Closed')").fetchone()[0],
            "pending":db.execute("SELECT COUNT(*) FROM complaints WHERE status='New'").fetchone()[0],
        }
        category_rows=db.execute("SELECT category,COUNT(*) total FROM complaints GROUP BY category ORDER BY total DESC").fetchall()
        status_rows=db.execute("SELECT status,COUNT(*) total FROM complaints GROUP BY status").fetchall()
        staff=UserRepository(db).staff() if role=="admin" else []
        notifications=db.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 8",(uid,)).fetchall()
        unread=db.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0",(uid,)).fetchone()[0]
        feedback_ids={r["complaint_id"] for r in db.execute("SELECT complaint_id FROM feedback WHERE student_id=?",(uid,)).fetchall()} if role=="student" else set()
        history_by_id={}
        for row in rows:
            history_by_id[row["id"]]=db.execute("""SELECT h.*,u.name actor_name FROM status_history h
                LEFT JOIN users u ON u.id=h.changed_by WHERE h.complaint_id=? ORDER BY h.id""",(row["id"],)).fetchall()
        return render_template("dashboard.html",complaints=rows,stats=stats,staff=staff,notifications=notifications,
            unread=unread,search=search,selected_status=status,category_rows=category_rows,status_rows=status_rows,
            feedback_ids=feedback_ids,history_by_id=history_by_id)

    @app.post("/complaints")
    @login_required("student")
    def create_complaint():
        photo=None
        try:
            photo=save_photo(request.files.get("photo"))
            cid=CampusFixFacade(get_db()).submit_complaint(session["user_id"],request.form,photo)
            get_db().commit();flash(f"Complaint #{cid} submitted successfully.","success")
        except Exception as exc:
            get_db().rollback()
            if photo:
                try:(Path(current_app.config["UPLOAD_FOLDER"])/photo).unlink(missing_ok=True)
                except OSError:pass
            flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/complaints/<int:cid>/assign")
    @login_required("admin")
    def assign(cid):
        db=get_db();complaint=ComplaintRepository(db).get(cid)
        if not complaint:abort(404)
        strategy_name=request.form.get("strategy","Skill match")
        strategy_cls=STRATEGIES.get(strategy_name,SkillMatchStrategy)
        staff=UserRepository(db).staff()
        selected=AssignmentService(strategy_cls()).assign(complaint,staff)
        manual=request.form.get("staff_id","")
        if manual:
            selected=next((s for s in staff if str(s["id"])==manual),None)
        if not selected:
            flash("No staff member matched this rule. Try another strategy or select a staff member manually.","error")
            return redirect(url_for("dashboard"))
        try:
            history=current_history()
            history.run(AssignCommand(db,session["user_id"],cid,selected["id"],
                f"Assign complaint #{cid} to {selected['name']}"))
            if complaint["status"]=="New":
                CampusFixFacade(db).transition(complaint,"assign",session["user_id"],"Assigned by administrator")
            if complaint["status"] != "New":
                db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",
                    (selected["id"],cid,f"Complaint #{cid} assigned to you: {complaint['title']}","In-app"))
            db.commit();flash(f"Complaint #{cid} assigned to {selected['name']}.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/complaints/<int:cid>/priority")
    @login_required("admin")
    def priority(cid):
        db=get_db()
        try:
            value=request.form.get("priority")
            if value not in ("Low","Medium","High","Critical"):raise ValueError("Invalid priority.")
            current_history().run(ChangePriorityCommand(db,session["user_id"],cid,value))
            db.commit();flash("Priority updated. You can undo this action.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/complaints/<int:cid>/reject")
    @login_required("admin")
    def reject(cid):
        db=get_db();c=ComplaintRepository(db).get(cid)
        if not c:abort(404)
        reason=request.form.get("reason","").strip()
        try:
            if len(reason)<4:raise ValueError("Please provide a rejection reason.")
            CampusFixFacade(db).reject(c,session["user_id"],reason)
            db.commit();flash(f"Complaint #{cid} rejected with a reason recorded.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/complaints/<int:cid>/status")
    @login_required()
    def update_status(cid):
        db=get_db();c=ComplaintRepository(db).get(cid)
        if not c:abort(404)
        role=session["role"]
        if role=="staff" and c["assignee_id"]!=session["user_id"]:abort(403)
        if role=="student" and (c["reporter_id"]!=session["user_id"] or request.form.get("action")!="reject"):abort(403)
        if role not in ("student","staff","admin"):abort(403)
        action=request.form.get("action","");remark=request.form.get("remark","").strip()
        if role=="student" and action=="reject":remark="Cancelled by student"
        try:
            CampusFixFacade(db).transition(c,action,session["user_id"],remark)
            db.commit();flash("Complaint status updated successfully.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/complaints/<int:cid>/feedback")
    @login_required("student")
    def feedback(cid):
        db=get_db();c=ComplaintRepository(db).get(cid)
        if not c or c["reporter_id"]!=session["user_id"]:abort(403)
        try:
            if c["status"] not in ("Resolved","Closed"):raise ValueError("Feedback is available after resolution.")
            rating=int(request.form.get("rating","5"))
            if rating not in range(1,6):raise ValueError("Choose a rating from 1 to 5.")
            db.execute("INSERT INTO feedback(complaint_id,student_id,rating,comment) VALUES(?,?,?,?)",
                (cid,session["user_id"],rating,request.form.get("comment","").strip()))
            db.commit();flash("Thank you for your feedback.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/admin/history/<action>")
    @login_required("admin")
    def history_action(action):
        if action not in ("undo","redo"):abort(404)
        db=get_db()
        try:
            result=current_history().undo(db) if action=="undo" else current_history().redo(db)
            db.commit()
            flash((result+" undone.") if result and action=="undo" else (result+" redone.") if result else "No action available.","success")
        except Exception as exc:db.rollback();flash(str(exc),"error")
        return redirect(url_for("dashboard"))

    @app.post("/notifications/read")
    @login_required()
    def mark_notifications_read():
        get_db().execute("UPDATE notifications SET is_read=1 WHERE user_id=?",(session["user_id"],))
        get_db().commit();flash("Notifications marked as read.","success")
        return redirect(url_for("dashboard"))

    @app.get("/uploads/<path:filename>")
    @login_required()
    def uploaded_file(filename):
        return send_from_directory(current_app.config["UPLOAD_FOLDER"],filename)

    @app.errorhandler(403)
    def forbidden(_):return render_template("error.html",code=403,message="You do not have permission to access this action."),403
    @app.errorhandler(404)
    def not_found(_):return render_template("error.html",code=404,message="The page or complaint could not be found."),404
