from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("intake-login/", views.intake_login, name="intake_login"),
    path("business/", views.business_view, name="business_intake"),
    path("individual/", views.personal_view, name="individual_intake"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard")
]
