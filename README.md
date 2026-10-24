# Cloud-Based Complaint Management System

## Technology
- Frontend: HTML, CSS, Bootstrap, JavaScript
- Backend: Python, Django, Django REST Framework
- Primary database: local MySQL
- Cloud replica: MongoDB Atlas, synchronized asynchronously
- Reports: ReportLab; charts: Chart.js; ML: Pandas, TF-IDF, Scikit-learn
- Testing: Django tests and VS Code terminal; Git for version control

## Reliability design
MySQL is the source of truth. Complaint operations save to MySQL first. Cloud synchronization runs separately and retries pending records when MongoDB Atlas becomes available. A cloud outage must not block local operations while the computer and MySQL are running.

## Prerequisites
1. Windows 10/11
2. Python 3.12 recommended
3. MySQL Server 8.x
4. Git for Windows
5. VS Code with the Python extension
6. MongoDB Atlas account/connection string (can be configured later)

Check in VS Code PowerShell terminal:
```powershell
py --version
git --version
mysql --version
```

## Setup
1. Extract this ZIP and open the `Cloud-Based-Complaint-Management-System` folder in VS Code.
2. Open Terminal > New Terminal and select PowerShell.
3. Run from the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If activation is blocked, run in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If Python 3.12 is not installed, use an installed supported version by changing `py -3.12` accordingly. We will verify package compatibility during setup.

## MySQL database
Connect to MySQL as an administrator and run this SQL. Replace the sample password with your own strong password:

```sql
CREATE DATABASE complaint_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'complaint_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON complaint_management.* TO 'complaint_app'@'localhost';
FLUSH PRIVILEGES;
```

Use the same database credentials in `.env`. Do not commit `.env` to Git.

## Git
```powershell
git init
git add .
git status
git commit -m "Initial project setup"
```

If Git identity is not configured:
```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```
Replace with your own details. Never commit passwords or connection strings.

## Implementation parts
- Part 1: setup, virtual environment, dependencies, environment variables, Git
- Part 2: Django foundation, MySQL settings, models, migrations, health check
- Part 3: registration, login, roles and permissions
- Part 4: complaint submission, unique ID, assignment, status changes and history
- Part 5: search, filters, notifications and Chart.js dashboard
- Part 6: ReportLab PDF exports and AI/ML classification
- Part 7: MongoDB Atlas cloud sync, durable MySQL sync queue, retries and logs
- Part 8: complete responsive frontend
- Part 9: automated tests, terminal verification, documentation and Git cleanup

Parts can be delivered as separate ZIPs and/or chat messages if code does not fit in one message. All parts must use the same structure. Do not replace newer files with older versions.
