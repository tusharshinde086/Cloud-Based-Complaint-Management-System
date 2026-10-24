# Part 9 — Sync Integration Helpers and Tests

## Included
- Transaction-safe integration helpers for complaint, history, and notification queueing.
- Tests for idempotent queue entries, missing cloud configuration, failed cloud attempts, and queue retention.
- Complaint workflow smoke tests.

## Installation
Extract/merge this ZIP into the project root. Keep `.env` and `.venv`.

## Important model compatibility
These tests expect the Part 2C models:
- `ComplaintHistory`: `complaint`, `changed_by`, `old_status`, `new_status`, `note`.
- `Notification`: `user`, `title`, `message`.
- `Complaint`: `created_by`, `title`, `description`, `category`, `priority`, `status`.
If your local model fields differ, adjust the tests to match your actual models. Do not overwrite your models with guessed fields.

## Wire queueing into existing views
This part provides helpers but intentionally does not overwrite the views built in earlier parts. In `complaint_records/views.py`, after the complaint is saved, call:
```python
from cloud_sync_service.integration import queue_complaint_after_commit
queue_complaint_after_commit(complaint.pk)
```
After creating a history record:
```python
from cloud_sync_service.integration import queue_history_after_commit
queue_history_after_commit(history.pk)
```
After creating a notification:
```python
from cloud_sync_service.integration import queue_notification_after_commit
queue_notification_after_commit(notification.pk)
```
These helpers use `transaction.on_commit`, so the job is queued only after the primary MySQL transaction succeeds. They look up the latest persisted state when called.

## Run checks in PowerShell
```powershell
python manage.py check
python manage.py test cloud_sync_service complaint_records
```
Then run the full test suite:
```powershell
python manage.py test
```

## Note about test database
Django tests create a temporary test database and may need permission to create it in MySQL. If MySQL user permissions are limited, grant the test database creation privileges or run against a local development database account with appropriate permissions.

## Scope
This part does not create migrations. It does not change existing models, and it does not schedule the sync worker automatically. Use `python manage.py sync_cloud` manually or configure a scheduled worker after verifying the queue.
