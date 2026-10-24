# Routes and Modules Checklist

Expected module routes after integration. These are intended routes; a route only exists if it has been added to `config/urls.py` and its app URL file is present.

| Module | Expected route | Purpose |
|---|---|---|
| Accounts | `/accounts/login/` | User login |
| Accounts | `/accounts/register/` | Public user registration |
| Dashboard | `/dashboard/` | User landing page |
| Complaints | `/complaints/` | Search/list complaints |
| Complaints | `/complaints/new/` | Submit complaint |
| Notifications | `/notifications/` | Personal notification inbox |
| Analytics | `/analytics/` | Status/category charts |
| Analytics API | `/analytics/data/` | Role-scoped JSON metrics |
| AI classifier | `/ai/` | Classify complaint text |
| AI training | `/ai/train/` | Administrator model training |
| PDF report | `/reports/complaints/pdf/` | Download filtered PDF |
| Cloud sync | Management command | `python manage.py sync_cloud` |
| Admin | `/admin/` | Django administration |
| Health | `/health/` | Basic application health response |

## Common integration checks

- Ensure each app is listed once in `INSTALLED_APPS`.
- Ensure `from django.urls import include, path` is present where needed.
- Add each `include()` route only once.
- Keep `config/urls.py` route names consistent with templates.
- Confirm the `Notification`, `ComplaintHistory`, `Complaint`, and `SyncJob` model fields match code from all merged parts.
- Confirm `pdf_reports`, `analytics_dashboard`, `complaint_classifier`, and `cloud_sync_service` package directories each contain `__init__.py`.
- Confirm database migrations exist and are applied.
