# URL routing
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('admin_login')

urlpatterns = [
    path('', include('src.apps.core.urls')),
    path('admin/', admin.site.urls),
    path('accounts/social/login/cancelled/', redirect_to_login),
    path('accounts/social/login/cancelled/', redirect_to_login),
    path('accounts/', include('allauth.urls')),
]
