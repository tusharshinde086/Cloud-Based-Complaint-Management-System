# Part 2C — Foundation code

Copy these files into your existing project, preserving folder paths. This pack assumes these app packages already exist: complaint_accounts, complaint_records, staff_assignments, complaint_history, user_notifications, pdf_reports, analytics_dashboard, complaint_classifier, cloud_sync_service.

If an app package is missing, create it from the project root with `python manage.py startapp APP_NAME` before copying files for it. Do not create duplicate app folders.

Ensure `.env` has your real MySQL password. Never share or commit it.

Run in activated virtual environment:
```powershell
python manage.py check
python manage.py makemigrations complaint_records complaint_history user_notifications cloud_sync_service
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/health/` and `http://127.0.0.1:8000/admin/`.

MySQL is the primary database. The SyncJob table stores durable sync work, but the actual MongoDB worker is implemented in a later part. This is the foundation code, not the completed user-facing workflow.
