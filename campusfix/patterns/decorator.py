from .singleton import AppConfig

# 4. DECORATOR: each wrapper adds a channel or behaviour around a base notifier.
class Notifier:
    def send(self,user_id,complaint_id,message): raise NotImplementedError
class InAppNotifier(Notifier):
    def __init__(self,db): self.db=db
    def send(self,uid,cid,msg):
        self.db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",(uid,cid,msg,"In-app"))
class NotifierDecorator(Notifier):
    def __init__(self,inner): self.inner=inner
    @property
    def db(self): return self.inner.db
    def send(self,uid,cid,msg): self.inner.send(uid,cid,msg)
class EmailNotifier(NotifierDecorator):
    def send(self,uid,cid,msg):
        super().send(uid,cid,msg)
        self.inner.db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",(uid,cid,"[Simulated email] "+msg,"Email"))
class SmsNotifier(NotifierDecorator):
    def send(self,uid,cid,msg):
        super().send(uid,cid,msg)
        self.inner.db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",(uid,cid,"[Simulated SMS] "+msg,"SMS"))
class RetryNotifier(NotifierDecorator):
    def send(self,uid,cid,msg):
        last=None
        for _ in range(max(1,AppConfig().get_int("notification_retries",3))):
            try:return super().send(uid,cid,msg)
            except Exception as exc:last=exc
        raise RuntimeError(f"Notification failed: {last}")
class LoggingNotifier(NotifierDecorator):
    def send(self,uid,cid,msg):
        super().send(uid,cid,msg)
        self.inner.db.execute("INSERT INTO notifications(user_id,complaint_id,message,channel) VALUES(?,?,?,?)",(uid,cid,"Delivery logged: "+msg,"Log"))
class NotifierFactory:
    @staticmethod
    def for_user(db,preferences=None):
        preferences=preferences or ["in_app","email","sms"]
        n=InAppNotifier(db)
        if "email" in preferences:n=EmailNotifier(n)
        if "sms" in preferences:n=SmsNotifier(n)
        return LoggingNotifier(RetryNotifier(n))
