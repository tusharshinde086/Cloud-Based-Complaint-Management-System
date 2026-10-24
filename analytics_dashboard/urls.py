from django.urls import path
from . import views

urlpatterns = [
    path("", views.analytics_page, name="analytics_page"),
    path("data/", views.analytics_data, name="analytics_data"),
]
