from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.index, name="index"),
    path("job/<uuid:job_id>/", views.job_detail, name="job_detail"),
    path("job/<uuid:job_id>/export/", views.export_csv, name="export_csv"),
]
