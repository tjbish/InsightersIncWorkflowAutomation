from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import re
from typing import Any


X_MARK = "X"


DIRECT_TEXT_FIELDS = {
    "tax_year": "tax_year",
    "client_name": "client_name",
    "spouse_name": "spouse_name",
    "client_dob": "client_dob",
    "spouse_dob": "spouse_dob",
    "client_ssn": "client_ssn",
    "spouse_ssn": "spouse_ssn",
    "client_dl": "drivers_license",
    "client_dl_exp": "drivers_license_exp",
    "client_dl_issued": "drivers_license_issued",
    "spouse_dl": "spouse_dl",
    "spouse_dl_exp": "spouse_dl_exp",
    "spouse_dl_issued": "spouse_dl_issued",
    "client_occupation": "client_occupation",
    "spouse_occupation": "spouse_occupation",
    "address": "address",
    "city": "city",
    "state": "state",
    "zip_code": "zip_code",
    "phone_number": "phone_number",
    "cell_number": "cell_number",
    "email": "email",
    "client_signature": "client_signature",
    "date_signed": "date_signed",
    "income_other": "income_other",
    "expenses_other": "expenses_other",
}


DEPENDENT_FIELDS = [
    "dep1_name",
    "dep1_ssn",
    "dep1_dob",
    "dep1_rel",
    "dep1_months",
    "dep2_name",
    "dep2_ssn",
    "dep2_dob",
    "dep2_rel",
    "dep2_months",
    "dep3_name",
    "dep3_ssn",
    "dep3_dob",
    "dep3_rel",
    "dep3_months",
]


CLIENT_STATUS_FIELDS = {
    "new": "client_status",
    "existing": "client_status2",
}


FILING_STATUS_FIELDS = {
    "single": "filing_status1",
    "mfj": "filing_status2",
    "mfs": "filing_status3",
    "hoh": "filing_status4",
}


INCOME_SOURCE_FIELDS = {
    "income": "income_sources1",
    "pension": "income_sources2",
    "gambling": "income_sources3",
    "other": "income_sources4",
    "business": "income_sources5",
    "ss": "income_sources6",
    "unemployment": "income_sources7",
}


EXPENSE_FIELDS = {
    "education": "expenses1",
    "business_exp": "expenses2",
    "other_exp": "expenses3",
}


BUSINESS_DIRECT_TEXT_FIELDS = {
    "owner1_name": "owner1_name",
    "owner1_ssn": "owner1_ssn",
    "owner1_ownership": "owner1_ownership",
    "owner2_name": "owner2_name",
    "owner2_ssn": "owner2_ssn",
    "owner2_ownership": "owner2_ownership",
    "email": "email",
    "business_name": "business_name",
    "fin_number": "fin_number",
    "address": "address",
    "city": "city",
    "state": "state",
    "zip_code": "zip_code",
    "business_type": "business_type",
    "date_established": "date_established",
    "date_last_return": "date_last_return",
    "sales_yr1": "sales_yr1",
    "sales_yr2": "sales_yr2",
    "sales_yr3": "sales_yr3",
    "sales_current": "sales_current",
    "fiscal_year_end": "fiscal_year_end",
    "bank_name": "bank_name",
    "bank_account_type": "bank_account_type",
    "bank_account_number": "bank_account_number",
    "bank_contact_name": "bank_contact",
    "bank_name2": "bank_name2",
    "bank_account_type2": "bank_account_type2",
    "bank_account_number2": "bank_account_number2",
    "bank_contact_name2": "bank_contact2",
    "accounting_software": "accounting_software",
    "num_employees": "num_employees",
    "payroll_id_state": "payroll_id_state",
    "payroll_id_county": "payroll_id_country",
    "payroll_id_city": "payroll_id_city",
    "sales_tax_state": "sales_tax_state",
    "sales_tax_county": "sales_tax_country",
    "sales_tax_city": "sales_tax_city",
}


BUSINESS_STRUCTURE_FIELDS = {
    "corp": "business_structure",
    "s_corp": "business_structure2",
    "llc": "business_structure3",
    "partnership": "business_structure4",
    "proprietorship": "business_structure5",
}


BUSINESS_ACCOUNTING_PERIOD_FIELDS = {
    "calendar": "accounting_period1",
    "fiscal": "accounting_period2",
}


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%m/%d/%Y")
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _split_phone_number(value: Any) -> tuple[str, str]:
    digits = re.sub(r"\D", "", _to_text(value))
    if not digits:
        return "", ""
    return digits[:3], digits[3:10]


def _empty_choice_fields() -> dict[str, str]:
    return {
        "client_status": "",
        "client_status2": "",
        "filing_status1": "",
        "filing_status2": "",
        "filing_status3": "",
        "filing_status4": "",
        "filing_status5": "",
        "income_sources1": "",
        "income_sources2": "",
        "income_sources3": "",
        "income_sources4": "",
        "income_sources5": "",
        "income_sources6": "",
        "income_sources7": "",
        "expenses1": "",
        "expenses2": "",
        "expenses3": "",
        "certification": "",
    }


def build_individual_pdf_field_values(cleaned_data: dict[str, Any]) -> dict[str, str]:
    field_values = _empty_choice_fields()

    for django_field, pdf_field in DIRECT_TEXT_FIELDS.items():
        field_values[pdf_field] = _to_text(cleaned_data.get(django_field))

    for field_name in DEPENDENT_FIELDS:
        field_values[field_name] = _to_text(cleaned_data.get(field_name))

    # Keep both keys so template typo changes do not block generation.
    field_values["deb3_dob"] = _to_text(cleaned_data.get("dep3_dob"))

    client_status = cleaned_data.get("client_status")
    if client_status in CLIENT_STATUS_FIELDS:
        field_values[CLIENT_STATUS_FIELDS[client_status]] = X_MARK

    filing_status = cleaned_data.get("filing_status")
    if filing_status in FILING_STATUS_FIELDS:
        field_values[FILING_STATUS_FIELDS[filing_status]] = X_MARK

    income_sources = cleaned_data.get("income_sources") or []
    for choice in income_sources:
        pdf_field = INCOME_SOURCE_FIELDS.get(choice)
        if pdf_field:
            field_values[pdf_field] = X_MARK

    expenses = cleaned_data.get("expenses") or []
    for choice in expenses:
        pdf_field = EXPENSE_FIELDS.get(choice)
        if pdf_field:
            field_values[pdf_field] = X_MARK

    if cleaned_data.get("certification"):
        field_values["certification"] = X_MARK

    return field_values


def build_business_pdf_field_values(cleaned_data: dict[str, Any]) -> dict[str, str]:
    field_values = {
        "business_structure": "",
        "business_structure2": "",
        "business_structure3": "",
        "business_structure4": "",
        "business_structure5": "",
        "accounting_period1": "",
        "accounting_period2": "",
        "has_payroll": "",
        "phone_number1": "",
        "phone_number2": "",
        "cell_number1": "",
        "cell_number2": "",
        "fax_number1": "",
        "fax_number2": "",
    }

    for django_field, pdf_field in BUSINESS_DIRECT_TEXT_FIELDS.items():
        field_values[pdf_field] = _to_text(cleaned_data.get(django_field))

    phone_fields = {
        "phone_number": ("phone_number1", "phone_number2"),
        "cell_number": ("cell_number1", "cell_number2"),
        "fax_number": ("fax_number1", "fax_number2"),
    }
    for django_field, (pdf_field_1, pdf_field_2) in phone_fields.items():
        first, second = _split_phone_number(cleaned_data.get(django_field))
        field_values[pdf_field_1] = first
        field_values[pdf_field_2] = second

    business_structure = cleaned_data.get("business_structure")
    if business_structure in BUSINESS_STRUCTURE_FIELDS:
        field_values[BUSINESS_STRUCTURE_FIELDS[business_structure]] = X_MARK

    accounting_period = cleaned_data.get("accounting_period")
    if accounting_period in BUSINESS_ACCOUNTING_PERIOD_FIELDS:
        field_values[BUSINESS_ACCOUNTING_PERIOD_FIELDS[accounting_period]] = X_MARK

    if cleaned_data.get("has_payroll"):
        field_values["has_payroll"] = X_MARK

    return field_values
