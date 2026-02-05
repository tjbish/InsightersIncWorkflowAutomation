from django import forms
from django.core.validators import RegexValidator


# TODO: Look for more secure ways to handle PII (SSN, Bank Account Number, etc.) - Likely a Django Form Library
# TODO: Have Checks for Numeric Values and Formatting for DB
# TODO: Verify that all fields have necessary validators; and then add encryption; make sure that all necessary fields are required
class BusinessIntakeForm(forms.Form):
    # Common Validators
    ssn_validator = RegexValidator(r'^(\d{3}-?\d{2}-?\d{4}|XXX-XX-XXXX)$', 'Enter SSN in XXX-XX-XXXX format.')
    zip_validator = RegexValidator(r'^\d{5}(?:-\d{4})?$', 'Enter a valid ZIP code.')
    phone_validator = RegexValidator(r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$', 'Enter a valid phone number.')

    #Section 1: Owner Information
    owner1_name = forms.CharField(label="Owner's Name (1)", max_length=100)
    owner1_ssn = forms.CharField(
        label="SSN (1)", 
        max_length=11, 
        min_length=11, 
        validators=[ssn_validator],
        widget=forms.PasswordInput(attrs={'placeholder': 'XXX-XX-XXXX', 'autocomplete': 'off'})
    )
    owner1_ownership = forms.DecimalField(
        label="% of Ownership (1)", 
        max_digits=5, 
        decimal_places=2,
        min_value=0,
        max_value=100
    )
    
    owner2_name = forms.CharField(label="Owner's Name (2)", max_length=100, required=False)
    owner2_ssn = forms.CharField(
        label="SSN (2)", 
        max_length=11, 
        min_length=11, 
        required=False, 
        validators=[ssn_validator],
        widget=forms.PasswordInput(attrs={'placeholder': 'XXX-XX-XXXX', 'autocomplete': 'off'})
    )
    owner2_ownership = forms.DecimalField(
        label="% of Ownership (2)", 
        max_digits=5, 
        decimal_places=2, 
        required=False,
        min_value=0,
        max_value=100
    )

    # Section 2: Business Contact Info
    business_name = forms.CharField(label="Business Name", max_length=200)
    fin_number = forms.CharField(label="FIN (Federal ID Number)", max_length=50)
    email = forms.EmailField(label="E-mail Address") # EmailValidator built into field, no need to have a second EmailValidator
    
    address = forms.CharField(label="Address", max_length=200)
    city = forms.CharField(label="City", max_length=100)
    
    US_STATES = [
        ('', 'Select State'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'),
        ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'),
        ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
        ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
        ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'),
        ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'),
        ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    ]
    state = forms.ChoiceField(label="State", choices=US_STATES)
    zip_code = forms.CharField(label="Zip Code", max_length=10, validators=[zip_validator])
    
    phone_number = forms.CharField(label="Phone Number", max_length=20, widget=forms.TextInput(attrs={'placeholder': '(XXX) XXX-XXXX'}), validators=[phone_validator])
    cell_number = forms.CharField(label="Cell Number", max_length=20, widget=forms.TextInput(attrs={'placeholder': '(XXX) XXX-XXXX'}), required=False, validators=[phone_validator])
    fax_number = forms.CharField(label="Fax Number", max_length=20, widget=forms.TextInput(attrs={'placeholder': '(XXX) XXX-XXXX'}), required=False, validators=[phone_validator])

    # Section 3: Business Type & History
    BUSINESS_TYPES = [
        ('proprietorship', 'Proprietorship'),
        ('partnership', 'Partnership'),
        ('llc', 'LLC'),
        ('c_corp', 'C-Corp'),
        ('s_corp', 'S-Corp'),
    ]
    business_type = forms.ChoiceField(label="Type of Business", choices=BUSINESS_TYPES, widget=forms.RadioSelect)
    date_established = forms.DateField(label="Date Established", widget=forms.DateInput(attrs={'type': 'date'}))
    date_last_return = forms.DateField(label="Date last tax return filed", widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    # Section 4: Financial History
    sales_yr1 = forms.DecimalField(label="Sales: First Yr ($)", required=False, min_value=0)
    sales_yr2 = forms.DecimalField(label="Sales: Second Yr ($)", required=False, min_value=0)
    sales_yr3 = forms.DecimalField(label="Sales: Third Yr ($)", required=False, min_value=0)
    sales_current = forms.DecimalField(label="Sales: Current Yr ($)", required=False, min_value=0)

    ACCOUNTING_PERIODS = [('calendar', 'Calendar Yr'), ('fiscal', 'Fiscal Yr')]
    accounting_period = forms.ChoiceField(label="Accounting Period", choices=ACCOUNTING_PERIODS, widget=forms.RadioSelect)
    fiscal_year_end = forms.CharField(label="If Fiscal, Year Ending Date", required=False)

    # Section 5: Banking Information
    bank_name = forms.CharField(label="Bank Name", max_length=100, required=False)
    ACCOUNT_TYPES = [('checking', 'Checking'), ('savings', 'Savings')]
    bank_account_type = forms.ChoiceField(label="Account Type", choices=ACCOUNT_TYPES, required=False)
    bank_account_number = forms.CharField(label="Account Number", max_length=30, required=False, widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))
    bank_contact_name = forms.CharField(label="Bank Contact Person", max_length=100, required=False)
    bank_contact_phone = forms.CharField(label="Bank Contact Phone", max_length=20, required=False, validators=[phone_validator])

    # Section 6: Payroll & Tax ID
    accounting_software = forms.CharField(label="Current Accounting Software", max_length=100, required=False)
    has_payroll = forms.BooleanField(label="Payroll? (Yes/No)", required=False)
    num_employees = forms.IntegerField(label="Number of employees", required=False, min_value=0)
    
    payroll_id_state = forms.CharField(label="Payroll Number (State)", max_length=50, required=False)
    payroll_id_country = forms.CharField(label="Payroll Number (Country)", max_length=50, required=False)
    payroll_id_city = forms.CharField(label="Payroll Number (City)", max_length=50, required=False)
    sales_tax_state = forms.CharField(label="Sales Tax Number (State)", max_length=50, required=False)
    sales_tax_county = forms.CharField(label="Sales Tax Number (County)", max_length=50, required=False)
    sales_tax_city = forms.CharField(label="Sales Tax Number (City)", max_length=50, required=False)