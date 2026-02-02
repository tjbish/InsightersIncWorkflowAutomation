from django import forms


# TODO: Look for more secure ways to handle PII (SSN, Bank Account Number, etc.) - Likely a Django Form Library
# TODO: Have Checks for Numeric Values and Formatting for DB
class BusinessIntakeForm(forms.Form):
    #Section 1: Owner Information
    owner1_name = forms.CharField(label="Owner's Name (1)", max_length=100)
    owner1_ssn = forms.CharField(label="SSN (1)", max_length=11, widget=forms.PasswordInput(attrs={'placeholder': 'XXX-XX-XXXX', 'autocomplete': 'off'}))
    owner1_ownership = forms.DecimalField(label="% of Ownership (1)", max_digits=5, decimal_places=2)
    
    owner2_name = forms.CharField(label="Owner's Name (2)", max_length=100, required=False)
    owner2_ssn = forms.CharField(label="SSN (2)", max_length=11, required=False, widget=forms.PasswordInput(attrs={'placeholder': 'XXX-XX-XXXX', 'autocomplete': 'off'}))
    owner2_ownership = forms.DecimalField(label="% of Ownership (2)", max_digits=5, decimal_places=2, required=False)

    # Section 2: Business Contact Info
    business_name = forms.CharField(label="Business Name", max_length=200)
    fin_number = forms.CharField(label="FIN (Federal ID Number)", max_length=50)
    email = forms.EmailField(label="E-mail Address")
    
    address = forms.CharField(label="Address", max_length=200)
    city = forms.CharField(label="City", max_length=100)
    state = forms.CharField(label="State", max_length=50)
    zip_code = forms.CharField(label="Zip Code", max_length=20)
    
    phone_number = forms.CharField(label="Phone Number", max_length=20)
    cell_number = forms.CharField(label="Cell Number", max_length=20, required=False)
    fax_number = forms.CharField(label="Fax Number", max_length=20, required=False)

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
    sales_yr1 = forms.DecimalField(label="Sales: First Yr ($)", required=False)
    sales_yr2 = forms.DecimalField(label="Sales: Second Yr ($)", required=False)
    sales_yr3 = forms.DecimalField(label="Sales: Third Yr ($)", required=False)
    sales_current = forms.DecimalField(label="Sales: Current Yr ($)", required=False)

    ACCOUNTING_PERIODS = [('calendar', 'Calendar Yr'), ('fiscal', 'Fiscal Yr')]
    accounting_period = forms.ChoiceField(label="Accounting Period", choices=ACCOUNTING_PERIODS, widget=forms.RadioSelect)
    fiscal_year_end = forms.CharField(label="If Fiscal, Year Ending Date", required=False)

    # Section 5: Banking Information
    bank_name = forms.CharField(label="Bank Name", max_length=100, required=False)
    ACCOUNT_TYPES = [('checking', 'Checking'), ('savings', 'Savings')]
    bank_account_type = forms.ChoiceField(label="Account Type", choices=ACCOUNT_TYPES, required=False)
    bank_account_number = forms.CharField(label="Account Number", required=False, widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))
    bank_contact_name = forms.CharField(label="Bank Contact Phone", max_length=20, required=False)
    bank_contact_phone = forms.CharField(label="Bank Contact Person", required=False)

    # Section 6: Payroll & Tax ID
    accounting_software = forms.CharField(label="Current Accounting Software", required=False)
    has_payroll = forms.BooleanField(label="Payroll? (Yes/No)", required=False)
    num_employees = forms.IntegerField(label="Number of employees", required=False, min_value=0)
    
    payroll_id_state = forms.CharField(label="Payroll Number (State)", required=False)
    payroll_id_country = forms.CharField(label="Payroll Number (Country)", required=False)
    payroll_id_city = forms.CharField(label="Payroll Number (City)", required=False)
    sales_tax_state = forms.CharField(label="Sales Tax Number (State)", required=False)
    sales_tax_county = forms.CharField(label="Sales Tax Number (County)", required=False)
    sales_tax_city = forms.CharField(label="Sales Tax Number (City)", required=False)