from functools import wraps

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables
from .forms import BusinessIntakeForm, PersonalIntakeForm, IntakeLoginForm

TEMP_LOGIN_ID = settings.INTAKE_LOGIN_ID
TEMP_LOGIN_PASSWORD = settings.INTAKE_LOGIN_PASSWORD


def validate_intake_login(login_id: str, password: str) -> bool:
    # TODO: Replace with DB lookup when credentials are stored.
    return login_id == TEMP_LOGIN_ID and password == TEMP_LOGIN_PASSWORD


def require_intake_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.session.get("intake_logged_in"):
            return view_func(request, *args, **kwargs)

        request.session["intake_login_next"] = request.path
        return redirect("intake_login")

    return _wrapped


def home(request):
    return render(request, "home.html")


@sensitive_variables()  # Hides all local variables in this view from error logs
@require_intake_login
def business_view(request):
    if request.method == 'POST':
        form = BusinessIntakeForm(request.POST)
        if form.is_valid():
            # TODO: Save this data to the database or send email
            return HttpResponse("Thank you! We have received your information.")
    else:
        form = BusinessIntakeForm()

    return render(request, 'business_intake.html', {'form': form})


@sensitive_variables()
@require_intake_login
def personal_view(request):
    if request.method == 'POST':
        form = PersonalIntakeForm(request.POST)
        if form.is_valid():
            # TODO: Save this data to the database or send email
            return HttpResponse("Thank you! Individual Intake received.")
    else:
        form = PersonalIntakeForm()

    return render(request, 'personal_intake.html', {'form': form})


@sensitive_variables("login_id", "password")
def intake_login(request):
    if request.method == "POST":
        form = IntakeLoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data["login_id"]
            password = form.cleaned_data["password"]
            if validate_intake_login(login_id, password):
                request.session["intake_logged_in"] = True
                request.session["intake_login_id"] = login_id
                next_path = request.session.pop("intake_login_next", None)
                if next_path:
                    return redirect(next_path)
                return redirect("home")

            form.add_error(None, "Invalid login ID or password.")
    else:
        form = IntakeLoginForm()

    return render(request, "intake_login.html", {"form": form})
