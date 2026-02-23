from django.test import TestCase
from ..forms import PersonalIntakeForm
import datetime

# TO RUN TESTS: docker-compose exec web python manage.py test src.apps.core.tests.test_personal_forms

class PersonalIntakeFormTests(TestCase):
    def setUp(self):
        # Setup valid data for PersonalIntakeForm
        self.valid_data = {
            'client_status': 'new',
            'tax_year': str(datetime.date.today().year - 1),
            'client_name': 'John Doe',
            'client_dob': '1990-01-01',
            'client_ssn': '123-45-6789',
            'client_occupation': 'Developer',
            'address': '123 Test Lane',
            'city': 'Testville',
            'state': 'CA',
            'zip_code': '90210',
            'phone_number': '555-123-4567',
            'email': 'test@example.com',
            'filing_status': 'single',
            'certification': True,
            'client_signature': 'John Doe',
            'date_signed': '2023-04-15',
        }

    def test_valid_form(self):
        """Test that the form is valid with correct data."""
        form = PersonalIntakeForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_ssn_validation(self):
        """Test SSN format validation."""
        data = self.valid_data.copy()
        data['client_ssn'] = '123456789'  # Missing dashes
        form = PersonalIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('client_ssn', form.errors)

    def test_zip_code_validation(self):
        """Test Zip Code validation."""
        data = self.valid_data.copy()
        data['zip_code'] = 'ABCDE' # Non-numeric
        form = PersonalIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('zip_code', form.errors)

    def test_phone_number_validation(self):
        """Test Phone Number validation."""
        data = self.valid_data.copy()
        data['phone_number'] = 'not-a-number'
        form = PersonalIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)