from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("business/", views.business_view, name="business_intake"),
]
