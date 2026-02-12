from functools import wraps

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables

from .forms import BusinessIntakeForm, PersonalIntakeForm, IntakeLoginForm, AdminLoginForm
from .models import BusinessIntakeSubmission, PersonalIntakeSubmission


def validate_intake_login(login_id: str, password: str) -> bool:
    # TODO: Replace with DB lookup when credentials are stored.
    return login_id == settings.INTAKE_LOGIN_ID and password == settings.INTAKE_LOGIN_PASSWORD

def require_intake_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        allowed_path = request.session.get("intake_login_ok_for")
        if allowed_path == request.path:
            # One-time access after successful login to ensure login is required each visit.
            request.session.pop("intake_login_ok_for", None)
            return view_func(request, *args, **kwargs)

        request.session["intake_login_next"] = request.path
        return redirect("intake_login")

    return _wrapped

def validate_admin_login(login_id: str, password: str) -> bool:
    # TODO: Replace with DB lookup when credentials are stored.
    return login_id == settings.ADMIN_LOGIN_ID and password == settings.ADMIN_LOGIN_PASSWORD

def require_admin_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        allowed_path = request.session.get("admin_login_ok_for")
        if allowed_path == request.path:
            # One-time access after successful login to ensure login is required each visit.
            request.session.pop("admin_login_ok_for", None)
            return view_func(request, *args, **kwargs)

        request.session["admin_login_next"] = request.path
        return redirect("admin_login")

    return _wrapped


def home(request):
    return render(request, "home.html")

@require_admin_login
def admin_dashboard(request):
    return render(request, "admin.html")


@sensitive_variables()  # helps prevent sensitive values showing up in debug output
@require_intake_login
def business_view(request):
    if request.method == "POST":
        form = BusinessIntakeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            BusinessIntakeSubmission.objects.create(
                # --- Owner info (NO SSN STORED) ---
                owner1_name=data["owner1_name"],
                owner1_ownership=data["owner1_ownership"],

                owner2_name=data.get("owner2_name") or None,
                owner2_ownership=data.get("owner2_ownership") or None,

                # --- Business contact info ---
                business_name=data["business_name"],
                fin_number=data["fin_number"],
                email=data["email"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone_number=data["phone_number"],
                cell_number=data.get("cell_number") or None,
                fax_number=data.get("fax_number") or None,

                # --- Business type & history ---
                business_type=data["business_type"],
                date_established=data["date_established"],
                date_last_return=data.get("date_last_return") or None,

                # --- Financial history ---
                sales_yr1=data.get("sales_yr1") or None,
                sales_yr2=data.get("sales_yr2") or None,
                sales_yr3=data.get("sales_yr3") or None,
                sales_current=data.get("sales_current") or None,

                accounting_period=data["accounting_period"],
                fiscal_year_end=data.get("fiscal_year_end") or None,

                # --- Banking info (NO ACCOUNT NUMBER STORED) ---
                bank_name=data.get("bank_name") or None,
                bank_account_type=data.get("bank_account_type") or None,
                bank_contact_name=data.get("bank_contact_name") or None,
                bank_contact_phone=data.get("bank_contact_phone") or None,

                # --- Payroll & tax id ---
                accounting_software=data.get("accounting_software") or None,
                has_payroll=bool(data.get("has_payroll")),
                num_employees=data.get("num_employees") or None,

                payroll_id_state=data.get("payroll_id_state") or None,
                payroll_id_country=data.get("payroll_id_country") or None,
                payroll_id_city=data.get("payroll_id_city") or None,
                sales_tax_state=data.get("sales_tax_state") or None,
                sales_tax_county=data.get("sales_tax_county") or None,
                sales_tax_city=data.get("sales_tax_city") or None,
            )

            # IMPORTANT: SSNs + bank_account_number were accepted/validated but NOT saved.
            return HttpResponse("Thank you! We have received your information.")
    else:
        form = BusinessIntakeForm()

    return render(request, "business_intake.html", {"form": form})


@sensitive_variables()
@require_intake_login
def personal_view(request):
    if request.method == "POST":
        form = PersonalIntakeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # MultipleChoiceField returns a python list -> store as "wages,pension,ss"
            income_str = ",".join(data.get("income_sources", []))
            expense_str = ",".join(data.get("expenses", []))

            PersonalIntakeSubmission.objects.create(
                # --- Filing details ---
                client_status=data["client_status"],
                tax_year=data["tax_year"],

                # --- Client info (NO SSN STORED) ---
                client_name=data["client_name"],
                client_dob=data["client_dob"],
                client_occupation=data["client_occupation"],
                client_dl=data.get("client_dl") or None,
                client_dl_exp=data.get("client_dl_exp") or None,
                client_dl_issued=data.get("client_dl_issued") or None,

                # --- Spouse info (NO SSN STORED) ---
                spouse_name=data.get("spouse_name") or None,
                spouse_dob=data.get("spouse_dob") or None,
                spouse_occupation=data.get("spouse_occupation") or None,
                spouse_dl=data.get("spouse_dl") or None,
                spouse_dl_exp=data.get("spouse_dl_exp") or None,
                spouse_dl_issued=data.get("spouse_dl_issued") or None,

                # --- Contact & filing info ---
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                phone_number=data["phone_number"],
                cell_number=data.get("cell_number") or None,
                email=data["email"],
                filing_status=data["filing_status"],

                # --- Dependents (NO SSN STORED) ---
                dep1_name=data.get("dep1_name") or None,
                dep1_dob=data.get("dep1_dob") or None,
                dep1_rel=data.get("dep1_rel") or None,
                dep1_months=data.get("dep1_months") or None,

                dep2_name=data.get("dep2_name") or None,
                dep2_dob=data.get("dep2_dob") or None,
                dep2_rel=data.get("dep2_rel") or None,
                dep2_months=data.get("dep2_months") or None,

                dep3_name=data.get("dep3_name") or None,
                dep3_dob=data.get("dep3_dob") or None,
                dep3_rel=data.get("dep3_rel") or None,
                dep3_months=data.get("dep3_months") or None,

                # --- list in one column ---
                income_sources=income_str or None,
                expenses=expense_str or None,

                # --- Certification ---
                certification=bool(data.get("certification")),
                client_signature=data["client_signature"],
                date_signed=data["date_signed"],
            )

            # IMPORTANT: SSNs were accepted/validated but NOT saved.
            return HttpResponse("Thank you! Individual Intake received.")
    else:
        form = PersonalIntakeForm()

    return render(request, "personal_intake.html", {"form": form})


# TODO Implement database storage of login_id and password when submitted (Logs users that actually use their ID/password to access forms)
@sensitive_variables("login_id", "password")
def intake_login(request):
    if request.method == "POST":
        form = IntakeLoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data["login_id"]
            password = form.cleaned_data["password"]

            if validate_intake_login(login_id, password):
                next_path = request.session.pop("intake_login_next", None)
                if next_path:
                    request.session["intake_login_ok_for"] = next_path
                    return redirect(next_path)

                return redirect("home")

            form.add_error(None, "Invalid login ID or password.")
    else:
        form = IntakeLoginForm()

    return render(request, "intake_login.html", {"form": form})

@sensitive_variables("login_id", "password")
def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST) # create class in form
        if form.is_valid():
            login_id = form.cleaned_data["login_id"]
            password = form.cleaned_data["password"]

            if validate_admin_login(login_id, password):
                next_path = request.session.pop("admin_login_next", None)
                if next_path:
                    request.session["admin_login_ok_for"] = next_path
                    return redirect(next_path)

                return redirect("home")

            form.add_error(None, "Invalid login ID or password.")
    else:
        form = AdminLoginForm()

    return render(request, "admin_login.html", {"form": form})