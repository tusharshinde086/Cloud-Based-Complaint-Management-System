# Part 5 — Notifications and Analytics

This part adds an authenticated notification inbox, a CSRF-protected “Mark read” action, and role-scoped complaint analytics with Chart.js.

## 1. Copy files
Extract this ZIP into the project root:
`C:\Users\Lenovo\Downloads\cms\Cloud-Based-Complaint-Management-System`

Allow it to merge with the existing `user_notifications`, `analytics_dashboard`, and `templates` folders. Do not delete your `.env` or `.venv`.

## 2. Check the Notification model
This part expects `user_notifications.models.Notification` to have:
- `user` (ForeignKey to the Django user model)
- `title` (optional or blank allowed)
- `message`
- `is_read` (BooleanField)
- `created_at` (DateTimeField)

If your existing Part 2C model uses different field names, do not overwrite it blindly; adjust the template/view to the exact model fields. The Part 2C model should be retained.

## 3. Add URL routes
Open `config/urls.py` and add these imports/routes to the existing `urlpatterns` (keep all routes already present):
```python
path("notifications/", include("user_notifications.urls")),
path("analytics/", include("analytics_dashboard.urls")),
```
Ensure `include` is imported:
```python
from django.urls import include, path
```
Do not add duplicate routes if already present.

## 4. Verify apps
In `config/settings.py`, ensure `analytics_dashboard` and `user_notifications` are in `INSTALLED_APPS`.

## 5. Run commands in PowerShell
Run these from the project folder with `(.venv)` active:
```powershell
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```
No new database migration is intended in this part. `migrate` applies any existing unapplied migrations.

## 6. URLs
- `/notifications/` — logged-in user's notifications
- `/analytics/` — status and category charts
- `/analytics/data/` — JSON analytics endpoint
- `/complaints/` — existing complaint list

## 7. Analytics visibility
- Admin: all complaints
- Staff: complaints assigned to that staff member
- User: complaints created by that user

## 8. Notes
- Chart.js is loaded from its public CDN, so the analytics charts require internet access in the browser. The rest of the Django app remains local.
- The JSON endpoint requires login and uses the same role-based visibility as the analytics page.
- If `python manage.py test` reports that no tests are found, that is not a failure by itself. Share any actual traceback if a test fails.
