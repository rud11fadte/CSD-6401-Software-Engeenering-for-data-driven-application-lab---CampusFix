# 🏫 CampusFix – Campus Problem Reporter

### A Web-Based Campus Complaint Reporting and Management System

CampusFix is a web-based campus complaint reporting and management system developed using Python and Flask. It provides a centralized platform where students can report campus-related problems, administrators can manage and assign complaints, and maintenance staff can resolve them.

The project aims to make campus maintenance more organized, transparent and efficient through a digital complaint management system.

---

## 👥 1. Project Team

**Project developed by:**

| No. | Team Member | Primary Responsibility |
|---|---|---|
| 1 | Rudresh Fadate | Application Development, Backend Integration and Design Patterns |
| 2 | Aadarsh Sawant | Deployment and Hosting using PythonAnywhere |
| 3 | Prathamesh Naik | Application Functionality, Requirements and Testing |
| 4 | Kirtikesh Naik | Software Architecture and Deployment Assistance |

---

## 📌 2. Problem Statement

In educational institutions, students frequently encounter problems such as:

- Broken classroom fans and lights.
- Damaged furniture.
- Water leakage.
- Electrical problems.
- Washroom maintenance issues.
- Cleanliness problems.
- Internet connectivity issues.

Traditionally, students report these issues verbally to college authorities or maintenance staff.

This approach can make complaint management difficult because complaints may not be properly recorded, assigned, monitored or tracked.

### Our Solution

CampusFix provides a centralized online platform that digitizes the complete complaint management process.

Students can submit complaints and track their progress, administrators can manage and assign complaints, and maintenance staff can update the status of assigned tasks.

---

## 🎯 3. Project Objectives

- Provide students with an easy-to-use complaint reporting platform.
- Centralize campus complaint management.
- Enable administrators to assign complaints to maintenance staff.
- Allow staff to update complaint progress.
- Provide complaint status tracking.
- Maintain complaint records in a centralized database.
- Improve communication between students, administrators and maintenance staff.
- Apply software engineering principles and design patterns.
- Deploy the application online for browser-based access.

---

## ✨ 4. Key Features

### 👨‍🎓 Student Module

- Student registration and login.
- Submit new campus complaints.
- Select complaint categories.
- Add complaint descriptions and locations.
- Upload images as supporting evidence.
- Track complaint status.
- Receive notifications about complaint updates.
- Cancel complaints where permitted.
- Submit feedback.

### 🛠️ Admin Module

- View all submitted complaints.
- Manage complaint records.
- Assign complaints to maintenance staff.
- Set complaint priorities.
- Reject inappropriate complaints.
- Monitor complaint progress.
- View analytics and statistics.
- Undo and redo supported administrative actions.

### 👷 Staff Module

- View assigned complaints.
- Accept assigned tasks.
- Start working on complaints.
- Update complaint status.
- Mark complaints as resolved.
- Close or reopen complaints where permitted.
- View complaint history.

### 🔔 Notification System

- In-app notifications.
- Simulated email notifications.
- Simulated SMS notifications.
- Notification logging.
- Retry functionality.

**Note:** Email and SMS notifications are simulated in this project and are not connected to external email or SMS delivery services.

---

## 🏗️ 5. Software Architecture

CampusFix follows a modular, layered web application structure.

The application is organized into the following logical layers:

### 1. Presentation Layer

Responsible for the user interface and interaction.

Technologies:
- HTML
- CSS
- JavaScript
- Jinja2 Templates

This layer provides separate interfaces for students, administrators and maintenance staff.

### 2. Application Layer

Handles user requests, authentication, routing and application operations.

Technologies:
- Python
- Flask

### 3. Business Logic Layer

Contains the main application logic and business rules.

Responsibilities include:
- Complaint creation and management.
- Complaint validation.
- Staff assignment.
- Complaint lifecycle management.
- Notifications.
- Administrative operations.

This layer uses the ten implemented software design patterns.

### 4. Data Layer

Responsible for storing and retrieving application information.

Technology:
- SQLite

Stores:
- User information.
- Complaint details.
- Assignments.
- Notifications.
- Complaint history.
- Feedback.

### 5. Deployment Layer

The Flask application is deployed using PythonAnywhere, allowing users to access it through a web browser.

---

## 🎨 6. Software Design Patterns Implemented

One of the major technical aspects of CampusFix is the implementation of ten software design patterns.

A design pattern is a reusable solution to a commonly occurring software design problem.

We implemented the following patterns to improve modularity, flexibility, reusability and maintainability.

### 1. Singleton Pattern

**Implementation:** `AppConfig`

Ensures that only one shared instance of application configuration is used.

**Purpose:**
- Centralized application settings.
- Consistent configuration.
- Avoids unnecessary configuration instances.

### 2. Factory Method Pattern

**Implementation:** Complaint Creators

Provides a structured way to create different complaint objects without spreading object creation logic throughout the application.

**Purpose:**
- Organized object creation.
- Easier extension of complaint types.
- Reduced dependency on direct object creation.

### 3. Builder Pattern

**Implementation:** `ComplaintDraftBuilder`

Constructs complaint objects step by step using information such as:
- Title.
- Description.
- Category.
- Location.
- Priority.
- Image information.

**Purpose:**
- Structured complaint construction.
- Better management of complex objects.

### 4. Decorator Pattern

**Implementation:** Notification Channels

Adds additional functionality to notification components without modifying their original implementation.

Implemented functionality includes:
- In-app notifications.
- Simulated email notifications.
- Simulated SMS notifications.
- Logging.
- Retry functionality.

**Purpose:**
- Extend notification functionality.
- Maintain flexible notification components.

### 5. Facade Pattern

**Implementation:** `CampusFixFacade`

Provides a simplified interface to interact with different application subsystems.

**Purpose:**
- Simplifies application interactions.
- Reduces complexity between components.
- Provides a common interface to application operations.

### 6. Observer Pattern

**Implementation:** Status Notifications and Audit System

Allows interested components to receive updates when complaint-related changes occur.

**Purpose:**
- Generate relevant notifications.
- Record complaint-related changes.
- Reduce tight coupling between components.

### 7. State Pattern

**Implementation:** Complaint Lifecycle Management

Manages complaint behaviour according to its current state.

Example lifecycle:

`Submitted → Assigned → In Progress → Resolved → Closed`

**Purpose:**
- Manage complaint status transitions.
- Organize state-dependent behaviour.
- Help prevent invalid state changes.

### 8. Strategy Pattern

**Implementation:** Staff Assignment Algorithms

Allows different staff assignment algorithms to be selected independently.

**Purpose:**
- Flexible assignment logic.
- Easier extension of assignment algorithms.
- Reduced dependency on a single assignment approach.

### 9. Command Pattern

**Implementation:** Assignment and Priority Commands

Encapsulates administrative operations as command objects.

Supported operations include:
- Staff assignment.
- Priority changes.
- Undo and redo of supported actions.

**Purpose:**
- Encapsulate administrative operations.
- Support undo/redo functionality.
- Improve control over application actions.

### 10. Chain of Responsibility Pattern

**Implementation:** Complaint Validation

Passes complaint information through multiple validation handlers.

Examples:
- Title validation.
- Description validation.
- Category validation.
- Location validation.

**Purpose:**
- Separate validation responsibilities.
- Organize validation logic.
- Make the validation process easier to extend.

---

## 🔄 7. Application Workflow

The following example explains how CampusFix works.

Suppose a student notices that a classroom fan is not working.

1. The student logs into CampusFix.
2. The student submits a complaint with its category, description and location.
3. The system validates the complaint information.
4. The complaint is stored in the SQLite database.
5. The administrator views the submitted complaint.
6. The administrator assigns it to maintenance staff.
7. The staff member accepts the complaint.
8. The staff member starts working on the issue.
9. After completing the repair, the staff member updates the status to Resolved.
10. Relevant notifications are generated.
11. The student can view the updated complaint status.

### Workflow Summary

**Student Reports → Admin Assigns → Staff Resolves → Student Tracks**

---

## 🗄️ 8. Database Integration

CampusFix uses **SQLite**, a lightweight relational database, for application data management.

The Flask backend communicates with SQLite using Python database connectivity and SQL queries.

The database is responsible for storing and managing information such as:

- User details.
- Student and staff accounts.
- Complaint information.
- Complaint assignments.
- Complaint status.
- Notifications.
- Complaint history.
- Feedback.

### How Database Integration Works

1. Flask establishes a connection to the SQLite database.
2. Application operations execute SQL queries.
3. New user and complaint information is inserted into the database.
4. Existing information is retrieved when users open their dashboards.
5. Complaint status and assignment details are updated when changes occur.
6. The information remains stored for future access.

### Common SQL Operations

| SQL Operation | Purpose |
|---|---|
| INSERT | Store new records |
| SELECT | Retrieve records |
| UPDATE | Modify existing records |
| DELETE | Remove records where permitted |

The database provides centralized and persistent storage for the application.

---

## 💻 9. Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Template Engine | Jinja2 |
| Database | SQLite |
| Version Control | Git |
| Source Code Hosting | GitHub |
| Cloud Hosting | PythonAnywhere |

---

## ☁️ 10. Deployment and Hosting

CampusFix was initially developed and tested in a local development environment.

After development, the application was deployed using **PythonAnywhere**, a cloud-based hosting platform for Python web applications.

### Deployment Objectives

- Make the application accessible online.
- Allow users to access CampusFix through a browser.
- Avoid requiring users to run the application locally.
- Demonstrate the application in a hosted environment.

### Deployment Platform

**PythonAnywhere**

The Flask application is configured for the hosted environment and made accessible through a public web address.

---

## 🧪 11. Testing

The application should be tested across its major user modules and workflows.

Important test cases include:

| Test Case | Expected Result |
|---|---|
| Student registration | Student account is created |
| Student login | Student dashboard opens |
| Complaint submission | Complaint is stored |
| Complaint validation | Invalid information is rejected |
| Admin complaint viewing | Submitted complaints are displayed |
| Staff assignment | Complaint is assigned |
| Staff status update | Complaint status changes |
| Student tracking | Updated complaint status is visible |
| Notification generation | Relevant notification is generated |

Testing helps verify the functionality of the application and identify errors.

---

## 📂 12. Project Structure

The project is organized into separate application components and supporting files.

```text
CampusFix/
│
├── campusfix/
│   ├── __init__.py
│   ├── routes/
│   ├── patterns/
│   ├── services/
│   ├── models/
│   ├── database/
│   ├── templates/
│   └── static/
│
├── tests/
│
├── docs/
│
├── requirements.txt
├── run.py
├── README.md
└── .gitignore
```

The structure above represents the main logical organization. Refer to the actual repository for the complete list of files and folders.

---

## ⚙️ 13. Installation and Local Setup

Follow these steps to run CampusFix locally.

### Prerequisites

- Python 3 installed.
- Git installed.
- Visual Studio Code or another code editor.

### Step 1: Clone the Repository

```bash
git clone https://github.com/rud11fadte/CampusFix.git
```

### Step 2: Navigate to the Project Directory

```bash
cd CampusFix
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```bash
.venv\Scripts\activate
```

For Linux / WSL:

```bash
source .venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python run.py
```

Open the local URL displayed in the terminal in your web browser.

---

## 🚀 14. Future Enhancements

Possible improvements for future versions include:

- Real email and SMS integration.
- Real-time notifications.
- Advanced complaint analytics.
- Mobile application support.
- More advanced staff assignment algorithms.
- Improved reporting and export functionality.
- Integration with institutional authentication systems.
- Enhanced security and access control.

---

## 🌟 15. Project Highlights

- Role-based complaint management.
- Three separate user modules.
- Complaint submission with image uploads.
- Complaint tracking and status management.
- Administrative staff assignment.
- Notification functionality.
- SQLite database integration.
- Ten software design patterns.
- Modular Flask application architecture.
- Online deployment using PythonAnywhere.
- Source code maintained on GitHub.

---

## 👨‍💻 16. Team Contributions

### Rudresh Fadate

- Primary application development.
- Flask backend development.
- Integration of application modules.
- Implementation of ten software design patterns.
- Database integration.
- GitHub source code management.

### Aadarsh Sawant

- Deployment of the application using PythonAnywhere.
- Hosting configuration.
- Preparation of the application for online access.

### Prathamesh Naik

- Application requirements and functionality review.
- Application workflow understanding.
- Testing and verification of application modules.

### Kirtikesh Naik

- Software architecture understanding and explanation.
- Application component organization.
- Assistance with deployment preparation and configuration.

---

## 📌 17. Conclusion

CampusFix demonstrates how a real-world campus maintenance problem can be addressed through a web-based complaint management system.

The application provides a centralized platform connecting students, administrators and maintenance staff.

By using Python, Flask, SQLite and ten software design patterns, the project demonstrates practical software development, modular architecture, database integration and software engineering concepts.

The deployment on PythonAnywhere makes the application accessible online, while GitHub provides source code management and collaboration.

**CampusFix aims to make campus complaint management simpler, more organized, transparent and efficient.**

---

## 🔗 18. Project Links

**GitHub Repository:**

[https://github.com/rud11fadte/CampusFix](https://github.com/rud11fadte/CampusFix)

**Live Application:**

[PythonAnywhere application URL.](https://aadarsh2508.pythonanywhere.com/dashboard)

---

## 📜 Academic Project

Developed as a group software engineering project.

**Project Title:** CampusFix – Campus Problem Reporter

**Team Members:**

1. Rudresh Fadate
2. Aadarsh Sawant
3. Prathamesh Naik
4. Kirtikesh Naik

**Technologies:** Python, Flask, SQLite, HTML, CSS, JavaScript

**Design Patterns:** 10 Software Design Patterns

**Deployment:** PythonAnywhere

---

⭐ If you find this project useful, feel free to explore the repository and its implementation.
