from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
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


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%m/%d/%Y")
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


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



