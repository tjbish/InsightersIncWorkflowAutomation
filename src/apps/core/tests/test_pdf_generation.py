from __future__ import annotations

import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase
from pypdf import PdfReader

from ..forms import BusinessIntakeForm, PersonalIntakeForm
from ..pdf_engine import fill_business_pdf, fill_individual_pdf


class PDFGenerationTests(SimpleTestCase):
    def build_business_form_data(self) -> dict[str, object]:
        return {
            "owner1_name": "Alabama Test School LLC",
            "owner1_ssn": "111-11-1111",
            "owner1_ownership": "60.00",
            "owner2_name": "Generic Test Partner",
            "owner2_ssn": "222-22-2222",
            "owner2_ownership": "40.00",
            "business_name": "Alabama Test School",
            "fin_number": "12-3456789",
            "email": "alabama.test.school@example.com",
            "address": "100 Generic Avenue",
            "city": "Tuscaloosa",
            "state": "AL",
            "zip_code": "35401",
            "phone_number": "205-555-0100",
            "cell_number": "205-555-0101",
            "fax_number": "205-555-0102",
            "business_type": "service",
            "business_structure": "llc",
            "date_established": "2014-08-15",
            "date_last_return": "2025-03-20",
            "sales_yr1": "150000.00",
            "sales_yr2": "175000.00",
            "sales_yr3": "210000.00",
            "sales_current": "98000.00",
            "accounting_period": "fiscal",
            "fiscal_year_end": "2025-12-31",
            "bank_name": "First Generic Bank",
            "bank_account_type": "checking",
            "bank_account_number": "1234567890",
            "bank_contact_name": "Jordan Banker",
            "bank_contact_phone": "205-555-0103",
            "bank_name2": "Second Generic Bank",
            "bank_account_type2": "savings",
            "bank_account_number2": "0987654321",
            "bank_contact_name2": "Taylor Treasury",
            "bank_contact_phone2": "205-555-0104",
            "accounting_software": "Generic Ledger Pro",
            "has_payroll": "on",
            "num_employees": "12",
            "payroll_id_state": "AL-12345",
            "payroll_id_county": "TUSC-67890",
            "payroll_id_city": "CITY-11223",
            "sales_tax_state": "AL-ST-9988",
            "sales_tax_county": "TUSC-ST-7766",
            "sales_tax_city": "CITY-ST-5544",
        }

    def build_individual_form_data(self) -> dict[str, object]:
        current_year = datetime.date.today().year
        return {
            "client_status": "existing",
            "tax_year": str(current_year - 1),
            "client_name": "Alex Example",
            "client_dob": "1988-04-12",
            "client_ssn": "333-33-3333",
            "client_occupation": "Teacher",
            "client_dl": "ALX1234567",
            "client_dl_exp": "2028-04-12",
            "client_dl_issued": "2020-04-12",
            "spouse_name": "Jamie Example",
            "spouse_dob": "1989-09-21",
            "spouse_ssn": "444-44-4444",
            "spouse_occupation": "Nurse",
            "spouse_dl": "JME7654321",
            "spouse_dl_exp": "2028-09-21",
            "spouse_dl_issued": "2020-09-21",
            "address": "250 Example Lane",
            "city": "Birmingham",
            "state": "AL",
            "zip_code": "35203",
            "phone_number": "205-555-0200",
            "cell_number": "205-555-0201",
            "email": "alex.jamie@example.com",
            "filing_status": "mfj",
            "dep1_name": "Casey Example",
            "dep1_dob": "2015-06-10",
            "dep1_ssn": "555-55-5555",
            "dep1_rel": "Child",
            "dep1_months": "12",
            "dep2_name": "Morgan Example",
            "dep2_dob": "2018-08-22",
            "dep2_ssn": "666-66-6666",
            "dep2_rel": "Child",
            "dep2_months": "12",
            "dep3_name": "Riley Example",
            "dep3_dob": "2021-01-14",
            "dep3_ssn": "777-77-7777",
            "dep3_rel": "Child",
            "dep3_months": "12",
            "income_sources": ["income", "business", "other"],
            "income_other": "Test royalties",
            "expenses": ["education", "other_exp"],
            "expenses_other": "Generic classroom supplies",
            "certification": "on",
            "client_signature": "Alex Example",
            "date_signed": "2026-04-12",
        }

    def read_pdf_fields(self, pdf_path: Path) -> dict[str, object]:
        reader = PdfReader(str(pdf_path))
        return {
            field_name: field.get("/V")
            for field_name, field in (reader.get_fields() or {}).items()
        }

    def assert_pdf_created(self, output_path: Path) -> None:
        self.assertTrue(output_path.exists(), f"Expected generated PDF at {output_path}")
        self.assertGreater(output_path.stat().st_size, 0, "Generated PDF should not be empty")

    def test_business_form_validates_and_generates_pdf(self) -> None:
        form = BusinessIntakeForm(data=self.build_business_form_data())
        self.assertTrue(form.is_valid(), form.errors)

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "business_test_submission.pdf"
            result = fill_business_pdf(form.cleaned_data, output_path=output_path)

            self.assertEqual(result, output_path)
            self.assert_pdf_created(output_path)

            fields = self.read_pdf_fields(output_path)
            self.assertEqual(str(fields.get("business_name")), "Alabama Test School")
            self.assertEqual(str(fields.get("bank_accuont_type")), "Checking")
            self.assertEqual(str(fields.get("bank_account_type2")), "Savings")
            self.assertEqual(str(fields.get("accounting_software")), "Generic Ledger Pro")
            self.assertEqual(str(fields.get("business_structure3")), "X")
            self.assertEqual(str(fields.get("accounting_period2")), "X")
            self.assertEqual(str(fields.get("has_payroll")), "X")

    def test_individual_form_validates_and_generates_pdf(self) -> None:
        form = PersonalIntakeForm(data=self.build_individual_form_data())
        self.assertTrue(form.is_valid(), form.errors)

        with TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "individual_test_submission.pdf"
            result = fill_individual_pdf(form.cleaned_data, output_path=output_path)

            self.assertEqual(result, output_path)
            self.assert_pdf_created(output_path)

            fields = self.read_pdf_fields(output_path)
            self.assertEqual(str(fields.get("client_name")), "Alex Example")
            self.assertEqual(str(fields.get("spouse_name")), "Jamie Example")
            self.assertEqual(str(fields.get("client_status2")), "X")
            self.assertEqual(str(fields.get("filing_status2")), "X")
            self.assertEqual(str(fields.get("income_sources5")), "X")
            self.assertEqual(str(fields.get("income_other")), "Test royalties")
            self.assertEqual(str(fields.get("expenses3")), "X")
            self.assertEqual(str(fields.get("certification")), "X")
