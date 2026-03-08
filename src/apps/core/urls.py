from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("intake-login/", views.intake_login, name="intake_login"),
    path("business/", views.business_view, name="business_intake"),
    path("individual/", views.personal_view, name="individual_intake"),
    path("submission-processing/", views.submission_processing_view, name="submission_processing"),
    path("api/monday/create-item/", views.monday_create_item_api, name="monday_create_item_api"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-login/", views.admin_login, name="admin_login")
]
