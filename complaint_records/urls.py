from django.urls import path
from . import views

urlpatterns = [
    path("", views.complaint_list, name="complaint_list"),
    path("new/", views.complaint_create, name="complaint_create"),
    path("<int:pk>/", views.complaint_detail, name="complaint_detail"),
    path("<int:pk>/edit/", views.complaint_edit, name="complaint_edit"),
    path("<int:pk>/assign/", views.complaint_assign, name="complaint_assign"),
    path("<int:pk>/status/", views.complaint_change_status, name="complaint_change_status"),
]
