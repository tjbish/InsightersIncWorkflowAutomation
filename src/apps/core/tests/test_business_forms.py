from django.test import TestCase
from ..forms import BusinessIntakeForm

# TO RUN Tests: docker-compose exec web python manage.py test src.apps.core.tests.test_business_forms


class BusinessIntakeFormTests(TestCase):
    def setUp(self):
        # A dictionary of valid data to use as a baseline for tests
        self.valid_data = {
            'owner1_name': 'Jane Doe',
            'owner1_ssn': '123-45-6789',
            'owner1_ownership': 50.00,
            'business_name': 'Insighters Inc.',
            'fin_number': '12-3456789',
            'email': 'jane@example.com',
            'address': '123 Business Rd',
            'city': 'Metropolis',
            'state': 'NY',
            'zip_code': '10001',
            'phone_number': '555-123-4567',
            'business_type': 'llc',
            'date_established': '2020-01-01',
            'accounting_period': 'calendar',
        }

    def test_valid_form(self):
        """Test that the form is valid with correct data."""
        form = BusinessIntakeForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_ssn_validation(self):
        """Test SSN format validation (XXX-XX-XXXX)."""
        data = self.valid_data.copy()
        
        # Invalid format (missing dashes)
        data['owner1_ssn'] = '123456789' 
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('owner1_ssn', form.errors)
        
        # Invalid length
        data['owner1_ssn'] = '123-45-678' 
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_ownership_limits(self):
        """Test ownership percentage limits (0-100)."""
        data = self.valid_data.copy()
        
        # Test negative
        data['owner1_ownership'] = -5
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('owner1_ownership', form.errors)

        # Test > 100
        data['owner1_ownership'] = 105
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('owner1_ownership', form.errors)

    def test_zip_code_validation(self):
        """Test Zip Code validation."""
        data = self.valid_data.copy()
        
        # Too short
        data['zip_code'] = '1234' 
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('zip_code', form.errors)

        # Non-numeric characters
        data['zip_code'] = 'ABCDE' 
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_phone_number_validation(self):
        """Test Phone Number validation."""
        data = self.valid_data.copy()
        
        # Invalid format
        data['phone_number'] = 'not-a-number'
        form = BusinessIntakeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)