# Planned project structure

```text
Cloud-Based-Complaint-Management-System/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/          # Django settings, root URLs, WSGI, ASGI
├── accounts/        # Authentication, roles, profiles
├── complaints/      # Complaint records and lifecycle
├── assignments/     # Staff assignment and resolution
├── history/         # Status changes and action history
├── notifications/   # In-app notifications
├── reports/         # PDF exports
├── dashboard/       # Dashboard and statistics
├── classifier/      # TF-IDF and Scikit-learn classification
├── cloudsync/       # MongoDB Atlas sync queue, retries and logs
├── templates/       # Django HTML templates
├── static/css/
├── static/js/
├── static/images/
├── tests/
└── docs/
```

This setup pack contains setup/configuration files only. Working Django application code will be delivered in the next implementation part, rather than including misleading empty placeholder modules.
