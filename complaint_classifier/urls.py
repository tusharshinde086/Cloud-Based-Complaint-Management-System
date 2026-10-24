from django.urls import path
from . import views

urlpatterns = [
    path("", views.classify_text_view, name="classify_complaint"),
    path("train/", views.train_model_view, name="train_complaint_model"),
]
