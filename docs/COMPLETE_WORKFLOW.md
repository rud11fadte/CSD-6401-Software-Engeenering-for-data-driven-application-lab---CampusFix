# CampusFix – Complete Application Workflow

## 1. Roles and permissions

### Student
1. Register with name, email and password, or sign in.
2. Open the Student Dashboard.
3. Submit a complaint with title, category, building/location, description and optional photo.
4. Validation Chain runs before saving: Auth → Input → Duplicate → Rate Limit → Language Filter.
5. Builder creates an immutable ComplaintDraft.
6. Factory Method selects the category-specific complaint creator and default priority.
7. Facade saves the complaint and writes its initial status history.
8. Student can view the report, status, assigned staff, notifications and attached image.
9. Student can cancel a New or Assigned complaint (the State pattern maps this to Rejected).
10. After Resolved/Closed, student can submit a 1–5 rating and comment.

### Administrator
1. Sign in using the administrator demo account.
2. View all complaints, metrics, category breakdown and status overview.
3. Search by complaint ID, title, location or student and filter by status.
4. Assign a staff member using Skill Match, Least Loaded, Round Robin, Zone Based or Skill + Least Loaded. Manual staff selection can override the strategy.
5. Change priority (Low, Medium, High, Critical).
6. Reject New/Assigned complaints with a reason.
7. Undo/redo the latest assignment or priority action using CommandHistory.
8. See notifications and audit/status history.

### Staff
1. Sign in using a staff demo account.
2. View only complaints assigned to that staff member.
3. For Assigned, choose Accept & start work.
4. For In Progress, choose Mark as resolved and add an optional work note.
5. For Resolved, choose Close or Reopen work.
6. Status changes are checked by the State pattern and published through Observer subscribers.

## 2. End-to-end pipeline

`Browser UI → Flask route/controller → CampusFixFacade → Builder → Chain of Responsibility → Factory Method → ComplaintRepository → SQLite`

After a state transition:

`Facade → StateFactory/ComplaintState → ComplaintSubject → StudentNotificationObserver + StaffNotificationObserver + AuditLogObserver + DashboardObserver → Decorator notification chain → SQLite notifications`

Admin assignment/priority:

`Admin UI → Strategy selection → AssignmentService → CommandHistory.run(ChangeFieldCommand) → SQLite`

## 3. The ten design patterns

| # | Pattern | Implementation | Where it appears |
|---|---|---|---|
| 1 | Singleton | AppConfig | `campusfix/patterns/singleton.py` |
| 2 | Factory Method | ComplaintCreatorRegistry + five category creators | `factory.py` |
| 3 | Builder | ComplaintDraftBuilder | `builder.py` |
| 4 | Decorator | InApp, Email, SMS, Retry, Logging notifier wrappers | `decorator.py` |
| 5 | Facade | CampusFixFacade | `services/campusfix_facade.py` |
| 6 | Observer | ComplaintSubject and four observers | `observer.py` |
| 7 | State | New, Assigned, InProgress, Resolved, Closed, Rejected states | `state.py` |
| 8 | Strategy | Skill, Least Loaded, Round Robin, Zone, Composite strategies | `strategy.py` |
| 9 | Command | ChangeFieldCommand and CommandHistory | `command.py` |
| 10 | Chain of Responsibility | Auth, Input, Duplicate, RateLimit, LanguageFilter handlers | `chain.py` |

## 4. Database tables

- `users`: student, admin and staff accounts.
- `complaints`: problem details, photo, priority, status and assignment.
- `status_history`: state transitions, actor, timestamp and remark.
- `notifications`: in-app and simulated email/SMS/log records.
- `feedback`: student rating and comment.
- `admin_actions`: reversible admin priority/assignment actions.

## 5. Demo walkthrough for college

1. Sign in as Student: `student@campusfix.test` / `student123`.
2. Submit an Electrical complaint. Use title `Classroom fan not working`, location `Block A`, and a short description.
3. Sign out and sign in as Admin: `admin@campusfix.test` / `admin123`.
4. Find the new complaint and assign it using Skill match to the Electrical staff member.
5. Change its priority and demonstrate Undo, then Redo.
6. Sign out and sign in as Electrical Staff: `electric@campusfix.test` / `staff123`.
7. Accept and start work, then mark it resolved with a work note.
8. Sign back in as Student and inspect notifications/status; submit feedback.
9. Show the Admin dashboard's category and status analytics.
10. Explain the code files in the design-pattern table above.

## 6. Project limitations (state these accurately)

- Email and SMS are simulated and stored locally; no external mail/SMS provider is connected.
- This is a local college demonstration app. It is not hardened for public internet deployment.
- Admin command undo/redo stacks (action IDs) are in application memory; they reset if the server restarts. The action audit rows remain in SQLite.
- Passwords are hashed with Werkzeug.
- Uploaded photos are restricted to common image extensions and 5 MB.
- Your source diagram labels the UI as JavaFX. This deliverable uses a local Flask browser UI to make setup and demonstration simpler in VS Code. If JavaFX is a strict marking requirement, the presentation layer must be ported while reusing the service/domain/pattern layers.
