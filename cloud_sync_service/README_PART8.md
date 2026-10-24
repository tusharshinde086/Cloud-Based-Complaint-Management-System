# Part 8 — MongoDB Atlas Cloud Replica and Retry Queue

## Design
- MySQL remains the source of truth and the Django ORM database.
- MongoDB Atlas is a separate cloud replica.
- Sync jobs are stored in MySQL, so jobs survive app restarts and temporary cloud outages.
- Failed jobs use exponential backoff and remain available for a later retry.
- Upserts use `local_object_id` so retrying the same job does not create duplicate documents.

## 1. Merge files
Extract this ZIP into:
`C:\Users\Lenovo\Downloads\cms\Cloud-Based-Complaint-Management-System`

Do not remove `.env` or `.venv`.

## 2. Configure Django settings
In `config/settings.py`, ensure `cloud_sync_service` is in `INSTALLED_APPS`, and add near the bottom:
```python
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "complaint_management_cloud")
CLOUD_SYNC_ENABLED = os.getenv("CLOUD_SYNC_ENABLED", "False").lower() in ("1", "true", "yes")
CLOUD_SYNC_BATCH_SIZE = int(os.getenv("CLOUD_SYNC_BATCH_SIZE", "100"))
CLOUD_SYNC_RETRY_SECONDS = int(os.getenv("CLOUD_SYNC_RETRY_SECONDS", "60"))
```
This assumes settings already imports `os`. If not, add `import os`.

## 3. Add URL routes
No web routes are required for the sync worker. Keep all existing routes.

## 4. Environment variables
Set these in `.env`:
```dotenv
MONGODB_URI=
MONGODB_DATABASE=complaint_management_cloud
CLOUD_SYNC_ENABLED=False
CLOUD_SYNC_BATCH_SIZE=100
CLOUD_SYNC_RETRY_SECONDS=60
```
Put your real MongoDB Atlas connection URI in `MONGODB_URI` locally. Never commit it to Git or paste it into public messages. In Atlas, configure a database user and allow network access from your current IP; prefer a restricted IP rule rather than `0.0.0.0/0`.

## 5. Database migration
The SyncJob model was introduced in Part 2C. Run:
```powershell
python manage.py check
python manage.py migrate
```
If SyncJob migrations were never created, run:
```powershell
python manage.py makemigrations cloud_sync_service
python manage.py migrate
```

## 6. Test the worker
Run:
```powershell
python manage.py cloud_sync_status
python manage.py sync_cloud
```
Without a configured `MONGODB_URI`, the command safely reports that the URI is not configured and leaves local MySQL data untouched.

## 7. Queueing changes
This part supplies enqueue helpers for complaints, history, and notifications. Call them after the corresponding MySQL write succeeds. For example, after saving a complaint:
```python
from cloud_sync_service.services import enqueue_complaint_sync
enqueue_complaint_sync(complaint)
```
After creating history:
```python
from cloud_sync_service.services import enqueue_history_sync
enqueue_history_sync(history)
```
After creating a notification:
```python
from cloud_sync_service.services import enqueue_notification_sync
enqueue_notification_sync(notification)
```
Do not import these functions at module import time into models. Call them from views/signals after the local transaction commits. Use `transaction.on_commit(lambda: enqueue_complaint_sync(complaint))` where appropriate.

## 8. Run the app
```powershell
python manage.py runserver
```
The sync worker is deliberately separate from normal requests. Run `python manage.py sync_cloud` when needed. For ongoing automatic retries, configure a scheduled task or a background worker later; do not rely on a web request to keep syncing.
