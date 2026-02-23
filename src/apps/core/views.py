from functools import wraps
from datetime import timedelta
import secrets

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from .forms import (
    BusinessIntakeForm,
    PersonalIntakeForm,
    IntakeLoginForm,
    AdminLoginForm,
    TemporaryIntakeCredentialCreateForm,
)
from .models import (
    BusinessIntakeSubmission,
    PersonalIntakeSubmission,
    TemporaryIntakeCredential,
)


def _path_to_form_type(path: str):
    if path == "/business/":
        return TemporaryIntakeCredential.BUSINESS
    if path == "/individual/":
        return TemporaryIntakeCredential.INDIVIDUAL
    return None


def _cleanup_expired_temp_credentials():
    TemporaryIntakeCredential.objects.filter(expires_at__lte=timezone.now()).delete()


def _generate_unique_intake_login_id():
    for _ in range(10):
        candidate = f"INT-{secrets.token_hex(4).upper()}"
        if not TemporaryIntakeCredential.objects.filter(login_id=candidate).exists():
            return candidate
    raise RuntimeError("Unable to generate a unique intake login ID.")


def authenticate_intake_login(login_id: str, password: str, next_path: str = None):
    # Env bypass check
    if (
        login_id == settings.INTAKE_LOGIN_ID
        and password == settings.INTAKE_LOGIN_PASSWORD
    ):
        return "ENV_BYPASS"

    credential = TemporaryIntakeCredential.objects.filter(login_id=login_id).first()
    if credential is None:
        return None

    expected_form_type = _path_to_form_type(next_path) if next_path else None
    if expected_form_type and credential.form_type != expected_form_type:
        return None

    if not credential.is_valid_for_login():
        return None

    if not check_password(password, credential.password_hash):
        return None

    return credential

def require_intake_login(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        allowed_path = request.session.get("intake_login_ok_for")
        if allowed_path == request.path:
            # One-time access after successful login to ensure login is required each visit.
            # We do not pop here because we need the session to persist for the POST request.
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
            # Keep this through GET->POST flow so admin dashboard actions can submit.
            return view_func(request, *args, **kwargs)

        request.session["admin_login_next"] = request.path
        return redirect("admin_login")

    return _wrapped


def home(request):
    request.session.pop("admin_login_ok_for", None)
    return render(request, "home.html")

@require_admin_login
def admin_dashboard(request):
    # Currently cleans up expired credentials on dashboard startup, can disable this to maintain temp ID persistence in the DB
    _cleanup_expired_temp_credentials()

    generated_credential = None
    if request.method == "POST":
        form = TemporaryIntakeCredentialCreateForm(request.POST)
        if form.is_valid():
            expires_at = timezone.now() + timedelta(hours=24)
            generated_password = secrets.token_urlsafe(12)
            created_by_login_id = request.session.get("admin_login_id", "unknown-admin")
            try:
                login_id = _generate_unique_intake_login_id()
            except RuntimeError:
                form.add_error(None, "Unable to generate a unique login ID. Try again.")
            else:
                credential = TemporaryIntakeCredential.objects.create(
                    login_id=login_id,
                    password_hash=make_password(generated_password),
                    form_type=form.cleaned_data["form_type"],
                    client_email=form.cleaned_data["client_email"],
                    created_by_login_id=created_by_login_id,
                    expires_at=expires_at,
                )
                generated_credential = {
                    "login_id": credential.login_id,
                    "password": generated_password,
                    "form_type": credential.get_form_type_display(),
                    "expires_at": credential.expires_at,
                    "client_email": credential.client_email,
                }
                form = TemporaryIntakeCredentialCreateForm()
    else:
        form = TemporaryIntakeCredentialCreateForm()

    return render(
        request,
        "admin.html",
        {
            "create_credential_form": form,
            "generated_credential": generated_credential,
        },
    )


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
                business_structure=data["business_structure"],
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
                
                bank_name2=data.get("bank_name2") or None,
                bank_account_type2=data.get("bank_account_type2") or None,
                bank_contact_name2=data.get("bank_contact_name2") or None,
                bank_contact_phone2=data.get("bank_contact_phone2") or None,

                # --- Payroll & tax id ---
                accounting_software=data.get("accounting_software") or None,
                has_payroll=data.get("has_payroll", False),
                num_employees=data.get("num_employees") or None,

                payroll_id_state=data.get("payroll_id_state") or None,
                payroll_id_county=data.get("payroll_id_county") or None,
                payroll_id_city=data.get("payroll_id_city") or None,
                sales_tax_state=data.get("sales_tax_state") or None,
                sales_tax_county=data.get("sales_tax_county") or None,
                sales_tax_city=data.get("sales_tax_city") or None,
            )
            
            is_bypass = request.session.get("intake_is_env_bypass", False)

            if not is_bypass:
                login_id = request.session.get("intake_login_id")

                if login_id:
                    credential = TemporaryIntakeCredential.objects.filter(login_id=login_id).first()
                    if credential:
                        credential.used_at = timezone.now()
                        credential.save(update_fields=["used_at"])

            request.session.pop("intake_login_id", None)
            request.session.pop("intake_login_ok_for", None)
            request.session.pop("intake_is_env_bypass", None)
            # IMPORTANT: SSNs + bank_account_number were accepted/validated but NOT saved.
            return HttpResponse("Thank you! We have received your information.")
        else:
            print(f"Business Form Validation Errors: {form.errors}")
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
            income_list = data.get("income_sources", [])
            if data.get("income_other"):
                income_list.append(f"{data['income_other']}")
            income_str = ",".join(income_list)

            expense_list = data.get("expenses", [])
            if data.get("expenses_other"):
                expense_list.append(f"{data['expenses_other']}")
            expense_str = ",".join(expense_list)

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
                certification = data.get("certification", False),
                client_signature=data["client_signature"],
                date_signed=data["date_signed"],
            )

            is_bypass = request.session.get("intake_is_env_bypass", False)

            if not is_bypass:
                login_id = request.session.get("intake_login_id")

                if login_id:
                    credential = TemporaryIntakeCredential.objects.filter(login_id=login_id).first()
                    if credential:
                        credential.used_at = timezone.now()
                        credential.save(update_fields=["used_at"])

            request.session.pop("intake_login_id", None)
            request.session.pop("intake_login_ok_for", None)
            request.session.pop("intake_is_env_bypass", None)
            # IMPORTANT: SSNs were accepted/validated but NOT saved.
            return HttpResponse("Thank you! Individual Intake received.")
        else:
            print(f"Personal Form Validation Errors: {form.errors}")
    else:
        form = PersonalIntakeForm()

    return render(request, "personal_intake.html", {"form": form})


@sensitive_variables("login_id", "password")
def intake_login(request):
    if request.method == "POST":
        form = IntakeLoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data["login_id"]
            password = form.cleaned_data["password"]
            next_path = request.session.get("intake_login_next")

            credential = authenticate_intake_login(login_id, password, next_path=next_path)
            if credential:
                next_path = request.session.pop("intake_login_next", None)

                if credential == "ENV_BYPASS":
                    request.session["intake_login_ok_for"] = next_path
                    request.session["intake_is_env_bypass"] = True
                    return redirect(next_path)

                if next_path:
                    request.session["intake_login_ok_for"] = next_path
                    request.session["intake_login_id"] = credential.login_id
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
                request.session["admin_login_id"] = login_id
                if next_path:
                    request.session["admin_login_ok_for"] = next_path
                    return redirect(next_path)

                return redirect("home")

            form.add_error(None, "Invalid login ID or password.")
    else:
        form = AdminLoginForm()

    return render(request, "admin_login.html", {"form": form})
