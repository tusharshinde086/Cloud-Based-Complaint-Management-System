# Part 7 — AI/ML Complaint Classification

## Features
- Text cleaning and category prediction.
- Uses a trained TF-IDF + Logistic Regression pipeline when `ml_models/complaint_classifier.joblib` exists.
- Uses a deterministic keyword fallback before a model is trained.
- Admin-only CSV training page with a 10 MB upload cap.
- Training metrics include holdout accuracy and classification report.
- Management command to classify a complaint from the terminal.

## Integration
1. Extract/merge this ZIP into the project root. Do not delete `.env` or `.venv`.
2. Ensure `complaint_classifier` is in `INSTALLED_APPS` in `config/settings.py`.
3. Add to `config/urls.py` while retaining all existing routes:
```python
path("ai/", include("complaint_classifier.urls")),
```
Ensure `include` is imported.

## Run in PowerShell
```powershell
python manage.py check
python manage.py test
python manage.py runserver
```

## URLs
- `/ai/` — classify a sample complaint (requires login)
- `/ai/train/` — upload a labelled CSV and train (Django superuser/staff only)
- `/ai/` uses the trained model if available; otherwise uses keyword fallback.

## CSV format
A CSV needs at least 10 labelled rows and at least two distinct category labels. Default columns:
```csv
text,category
"Cannot log in to the portal","Technical"
"Payment was taken twice","Billing"
"Water is leaking in the washroom","Facilities"
"Support team has not replied","Service"
```
The sample rows above are examples only. For a meaningful model, use a larger representative labelled dataset with enough examples per category. A tiny sample is only for smoke testing and will not produce a reliable classifier.

## Terminal test
```powershell
python manage.py classify_complaint --title "Payment failed" --description "My card was charged twice"
```

## Important
- This part does not alter the Complaint database model and needs no migrations.
- Predictions are suggestions; staff should verify categories.
- The uploaded CSV is temporarily written to disk during training and is not stored as a permanent dataset.
- If the training page reports a scikit-learn / joblib version error, retrain the model in the same virtual environment that runs Django.
