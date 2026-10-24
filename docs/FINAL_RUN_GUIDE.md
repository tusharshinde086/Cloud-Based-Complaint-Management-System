# Cloud-Based Complaint Management System — Final Run Guide

This guide assumes Parts 1–9 have been merged into the same Django project. Because each part was delivered as a separate ZIP, verify the actual local files before treating the application as fully integrated.

## A. Start the project in PowerShell

```powershell
cd "C:\Users\Lenovo\Downloads\cms\Cloud-Based-Complaint-Management-System"
.\.venv\Scripts\Activate.ps1
python --version
python -m django --version
```

If PowerShell blocks activation, do not change execution policy just for this guide; you can run commands directly using `.\.venv\Scripts\python.exe`.

## B. Verify environment and MySQL

Confirm `.env` exists and contains your local MySQL connection settings. Do not share or commit real credentials.

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
```

Run `createsuperuser` only if you do not already have an administrator account.

## C. Check migrations and configuration

```powershell
python manage.py showmigrations
python manage.py system_readiness
```

`system_readiness` is added in Part 10. It checks expected apps, primary database connectivity, pending migrations, and deployment-related settings. Warnings need review; a successful command is not a substitute for testing every workflow.

## D. Run automated tests

```powershell
python manage.py test
```

If tests fail, fix the first traceback before proceeding. Tests may need MySQL permissions to create a temporary test database. Do not interpret a test run as successful if it stopped on an exception.

## E. Start the development server

```powershell
python manage.py runserver
```

Open these routes, adjusting any route that you did not add in your local `config/urls.py`:

- `/accounts/login/`
- `/accounts/register/`
- `/dashboard/`
- `/complaints/`
- `/notifications/`
- `/analytics/`
- `/ai/`
- `/ai/train/` (administrator only)
- `/reports/complaints/pdf/`
- `/admin/`
- `/health/`

## F. Functional test sequence

1. Register a normal user and sign in.
2. Submit a complaint and confirm its generated complaint ID.
3. Confirm the owner can view the complaint.
4. Sign in as an administrator and assign the complaint to a staff user.
5. Sign in as that staff user and update the complaint status.
6. Confirm status history and notifications behave as expected.
7. Open analytics and check counts against the visible complaints.
8. Export a PDF and verify its records and filters.
9. Classify a sample complaint. Treat predictions as suggestions.
10. Run `python manage.py cloud_sync_status`, then `python manage.py sync_cloud` after Atlas configuration and queue integration are complete.

## G. MySQL and MongoDB roles

- MySQL is the primary database and source of truth.
- MongoDB Atlas is a replica destination, not the Django ORM primary database.
- The cloud queue must be explicitly called from the complaint/history/notification write paths. Part 9 provides integration helpers; verify they have been wired into the actual views.
- The sync command is manual. It does not automatically run continuously.

## H. Version control

```powershell
git status
git add .
git status
```

Check that `.env`, `.venv`, database dumps, uploaded private attachments, and trained models containing sensitive data are not staged. Then commit only reviewed files:

```powershell
git commit -m "Integrate complaint management system modules"
```

If Git is not initialized yet:

```powershell
git init
git add .gitignore
git status
```

Review `.gitignore` before adding the rest of the project.
