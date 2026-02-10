# URL routing
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('src.apps.core.urls')),
    path('admin/', admin.site.urls),
]
