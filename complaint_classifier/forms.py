from django import forms


class TrainingUploadForm(forms.Form):
    dataset = forms.FileField(
        help_text="CSV file with text and category columns (at least 10 labelled rows)."
    )
    text_column = forms.CharField(initial="text", max_length=100)
    label_column = forms.CharField(initial="category", max_length=100)
