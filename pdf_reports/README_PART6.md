# Part 6 — PDF Complaint Reports

## Included
- Authenticated PDF export using ReportLab.
- Optional filters for status, exact category, and created-date range.
- Access scope follows the account role: administrators see all complaints, staff see assigned complaints, and users see their own complaints.
- Landscape A4 report with complaint ID, title, category, priority, status, creator, assignee, and created date.

## Install
Extract/merge this ZIP into the project root. Do not delete `.env` or `.venv`.

Ensure `pdf_reports` is in `INSTALLED_APPS` in `config/settings.py`.

Add the following route to `config/urls.py` while keeping all existing routes:
```python
path("reports/", include("pdf_reports.urls")),
```
Ensure `include` is imported from `django.urls`.

## Run in PowerShell
```powershell
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/reports/complaints/pdf/` to download a report. Optional filters can be passed in the query string. This endpoint directly generates the PDF, so the `templates/reports/report_home.html` file is a starter form template; a separate report landing-page view can be added if you want a filter page before download.

## Important
The report uses the existing Complaint fields: `complaint_id`, `title`, `category`, `priority`, `status`, `created_by`, `assigned_to`, and `created_at`. If your current local model differs, align these field names before running the export. No new database model or migration is required.
