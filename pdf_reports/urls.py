from django.urls import path
from . import views

urlpatterns = [
    path("complaints/pdf/", views.complaint_report_pdf, name="complaint_report_pdf"),
]
