# Part 4 — Complaint submission, tracking, assignment and history

Copy the files into your existing project, preserving paths. This part expects the Part 2C models and Part 3 UserProfile model to be present.

Run in activated virtual environment:
```powershell
python manage.py check
python manage.py makemigrations complaint_records complaint_history
python manage.py migrate
python manage.py runserver
```

Use:
- `/complaints/` list, search and filters
- `/complaints/new/` submit complaint
- Click View for complaint details and history
- Staff/Admin roles can update assigned complaints; administrators can assign staff

Create staff users in Django admin > Users, then set their profile role to Staff in User Profiles. The assign form takes the numeric Django user ID. Only the complaint owner can edit their complaint while it is pending.

This part does not yet include PDF reports, cloud synchronization, AI/ML prediction, or advanced dashboard charts; those come in later parts.
