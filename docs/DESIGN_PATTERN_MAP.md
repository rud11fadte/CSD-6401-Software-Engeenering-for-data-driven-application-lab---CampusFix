# CampusFix – Design Pattern Map

| Pattern | Classes | Real use in the application |
|---|---|---|
| Singleton | `AppConfig` | Reads daily limit, duplicate window and notification retry settings once from `campusfix.ini`. |
| Factory Method | `ComplaintCreatorRegistry`, `ElectricalComplaintCreator`, `PlumbingComplaintCreator`, `NetworkComplaintCreator`, `FurnitureComplaintCreator`, `GeneralComplaintCreator` | The selected category determines complaint type metadata and default priority/SLA. |
| Builder | `ComplaintDraftBuilder`, `ComplaintDraft` | Builds a validated immutable draft from student form values and optional image path. |
| Decorator | `InAppNotifier`, `EmailNotifier`, `SmsNotifier`, `RetryNotifier`, `LoggingNotifier`, `NotifierFactory` | Wraps notification channels, retry and logging around a base in-app notifier. Email/SMS are simulated. |
| Facade | `CampusFixFacade` | Exposes submit, transition and reject operations to controllers, hiding the pattern/repository coordination. |
| Observer | `ComplaintSubject`, `StudentNotificationObserver`, `StaffNotificationObserver`, `DashboardObserver`, `AuditLogObserver` | A complaint state event is broadcast to subscribers; one observer failure does not stop the remaining observers. |
| State | `NewState`, `AssignedState`, `InProgressState`, `ResolvedState`, `ClosedState`, `RejectedState`, `StateFactory` | Enforces the allowed lifecycle and blocks illegal transitions. |
| Strategy | `SkillMatchStrategy`, `LeastLoadedStrategy`, `RoundRobinStrategy`, `ZoneBasedStrategy`, `CompositeStrategy`, `AssignmentService` | Admin chooses the staff assignment rule at runtime. |
| Command | `AssignCommand`, `ChangePriorityCommand`, `ChangeStatusCommand`, `BulkAssignCommand`, `CommandHistory` | Admin assignment and priority operations are command objects; latest changes can be undone/redone. |
| Chain of Responsibility | `AuthHandler`, `InputHandler`, `DuplicateHandler`, `RateLimitHandler`, `LanguageFilterHandler` | Submission is validated sequentially; any failed check stops the save pipeline. |

## Layer boundaries

`templates + browser → Flask route/controller → CampusFixFacade → services/domain/patterns → repository → SQLite`

The controllers do not construct SQL for the complaint listing/submission workflow; repositories own the primary complaint/user reads and writes. The Facade orchestrates the pattern sequence.
