# Part 3 — Accounts, login, roles and dashboard

Copy this ZIP's contents into your existing project directory, preserving paths. It adds UserProfile, registration, login/logout, dashboard and admin support. It assumes Part 2C's settings include `complaint_accounts` in INSTALLED_APPS and the templates directory.

Run in activated `.venv` from project root:
```powershell
python manage.py check
python manage.py makemigrations complaint_accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open:
- http://127.0.0.1:8000/accounts/register/
- http://127.0.0.1:8000/accounts/login/
- http://127.0.0.1:8000/dashboard/
- http://127.0.0.1:8000/admin/

New registrations are assigned User role. Change roles in Django admin > User Profiles. Django superusers/staff are treated as administrators. Complaint submission and assignment will be implemented in Part 4.
