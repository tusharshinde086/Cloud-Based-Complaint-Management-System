from django import forms
from .models import Complaint

class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("title", "description", "category", "priority", "attachment")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": "180", "placeholder": "Short complaint title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe the issue clearly"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("title", "description", "category", "priority")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": "180"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
        }
