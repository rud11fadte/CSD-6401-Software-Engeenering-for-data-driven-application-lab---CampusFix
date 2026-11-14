# CampusFix – Campus Problem Reporter

**A complete VS Code college project** with Student, Admin and Staff interfaces, SQLite persistence, photo attachments, notifications, complaint lifecycle, analytics and all ten design patterns from the system design.

## Important technology note
The supplied architecture diagram labels the UI as JavaFX. This project uses a Flask web UI that runs locally in Chrome/Edge, because it is much easier to install and demonstrate from VS Code. The business workflow, supporting repository/database layers and all ten pattern responsibilities are implemented in Python. If your evaluator requires JavaFX specifically, this is an adaptation of the UI layer, not a JavaFX implementation.

## Requirements
- Windows 10/11 or Ubuntu/WSL
- Python 3.10+
- Visual Studio Code
- Internet for the first Flask installation only

## Easiest setup – WSL / Ubuntu terminal
Open the extracted project folder in VS Code. In Terminal → New Terminal, make sure the terminal is in the folder containing `run.py` and `requirements.txt`.

Run:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```
Then open **http://127.0.0.1:5000**. Keep the terminal open while using the app.

### Windows PowerShell
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```
If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.

### One-command WSL setup
```bash
chmod +x run_linux.sh
./run_linux.sh
```
The script creates `.venv`, installs packages and starts the server. On later runs, activate `.venv` and run `python run.py`.

## Demo login accounts
| Role | Email | Password |
|---|---|---|
| Student | `student@campusfix.test` | `student123` |
| Admin | `admin@campusfix.test` | `admin123` |
| Electrical Staff | `electric@campusfix.test` | `staff123` |
| Plumbing Staff | `plumber@campusfix.test` | `staff123` |
| IT / Network Staff | `it@campusfix.test` | `staff123` |
| General Staff | `maintenance@campusfix.test` | `staff123` |
| Furniture Staff | `furniture@campusfix.test` | `staff123` |

New student accounts can be created from the Register link. Admin and staff accounts are seeded for demonstration.

## Features included
- Student registration and login; separate role-based dashboards.
- Complaint form with category, campus location, description and optional photo.
- Search and status filters.
- Admin dashboard metrics and category/status analytics.
- Staff assignment using Skill Match, Least Loaded, Round Robin, Zone Based and Composite strategy.
- Priority management, rejection with reason, undo and redo.
- Staff accept/start, resolve, close and reopen workflow.
- Student cancellation before work starts and feedback after resolution.
- Status history, observer notifications and simulated email/SMS channels.
- SQLite database created automatically on first launch.

## Ten design patterns
See `docs/COMPLETE_WORKFLOW.md` for the detailed end-to-end pipeline and demo walkthrough. Source implementations are in `campusfix/patterns/` and `campusfix/services/`.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Database reset
Stop the server, then delete `instance/campusfix.sqlite3`. Restart with `python run.py` to recreate the database and demo accounts. Uploaded photos are in `uploads/`.

## Project structure
```text
CampusFix/
├── app.py / run.py
├── config.py
├── campusfix.ini
├── requirements.txt
├── campusfix/
│   ├── db.py
│   ├── web.py
│   ├── patterns/       # all ten patterns
│   ├── services/      # Facade and business workflow
│   └── repositories/  # SQLite data access
├── templates/         # Login, registration, dashboard
├── static/css/        # Responsive UI styling
├── static/js/
├── uploads/
├── instance/          # generated SQLite database
├── tests/
└── docs/COMPLETE_WORKFLOW.md
```
