import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import TrainingUploadForm
from .services import classify_complaint, train_classifier


def _is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
def classify_text_view(request):
    result = None
    title = ""
    description = ""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        if not title and not description:
            messages.error(request, "Enter a complaint title or description.")
        else:
            result = classify_complaint(title, description)
    return render(request, "complaint_classifier/classify.html", {
        "result": result, "title_value": title, "description_value": description,
    })


@login_required
@user_passes_test(_is_admin)
@require_http_methods(["GET", "POST"])
def train_model_view(request):
    form = TrainingUploadForm(request.POST or None, request.FILES or None)
    metrics = None
    if request.method == "POST" and form.is_valid():
        upload = form.cleaned_data["dataset"]
        if upload.size > 10 * 1024 * 1024:
            messages.error(request, "Maximum dataset upload size is 10 MB.")
        elif not upload.name.lower().endswith(".csv"):
            messages.error(request, "Upload a CSV file.")
        else:
            try:
                # Save to a temporary in-memory file; the training service accepts a path.
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as temp:
                    for chunk in upload.chunks():
                        temp.write(chunk)
                    temp.flush()
                    metrics = train_classifier(
                        temp.name,
                        text_column=form.cleaned_data["text_column"].strip(),
                        label_column=form.cleaned_data["label_column"].strip(),
                    )
                messages.success(request, "Model trained and saved successfully.")
            except (ValueError, UnicodeDecodeError, csv.Error) as exc:
                messages.error(request, f"Training failed: {exc}")
            except Exception as exc:
                messages.error(request, f"Training failed: {exc}")
    return render(request, "complaint_classifier/train.html", {
        "form": form, "metrics": metrics,
    })
