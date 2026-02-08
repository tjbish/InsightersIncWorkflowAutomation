from django.db import models


class BusinessIntakeSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Owner info (NO SSN STORED) ---
    owner1_name = models.CharField(max_length=100)
    owner1_ownership = models.DecimalField(max_digits=5, decimal_places=2)

    owner2_name = models.CharField(max_length=100, blank=True, null=True)
    owner2_ownership = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # --- Business contact info ---
    business_name = models.CharField(max_length=200)
    fin_number = models.CharField(max_length=50)
    email = models.EmailField()

    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    phone_number = models.CharField(max_length=20)
    cell_number = models.CharField(max_length=20, blank=True, null=True)
    fax_number = models.CharField(max_length=20, blank=True, null=True)

    # --- Business type & history ---
    business_type = models.CharField(max_length=20)
    date_established = models.DateField()
    date_last_return = models.DateField(blank=True, null=True)

    # --- Financial history ---
    sales_yr1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sales_yr2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sales_yr3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sales_current = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    accounting_period = models.CharField(max_length=10)
    fiscal_year_end = models.CharField(max_length=50, blank=True, null=True)

    # --- Banking info (NO ACCOUNT NUMBER STORED) ---
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_type = models.CharField(max_length=20, blank=True, null=True)
    bank_contact_name = models.CharField(max_length=100, blank=True, null=True)
    bank_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # --- Payroll & tax id ---
    accounting_software = models.CharField(max_length=100, blank=True, null=True)
    has_payroll = models.BooleanField(default=False)
    num_employees = models.IntegerField(blank=True, null=True)

    payroll_id_state = models.CharField(max_length=50, blank=True, null=True)
    payroll_id_country = models.CharField(max_length=50, blank=True, null=True)
    payroll_id_city = models.CharField(max_length=50, blank=True, null=True)
    sales_tax_state = models.CharField(max_length=50, blank=True, null=True)
    sales_tax_county = models.CharField(max_length=50, blank=True, null=True)
    sales_tax_city = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Business Intake: {self.business_name} ({self.created_at.date()})"


class PersonalIntakeSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # --- Filing details ---
    client_status = models.CharField(max_length=10)  # new/existing
    tax_year = models.CharField(max_length=4)

    # --- Client info (NO SSN STORED) ---
    client_name = models.CharField(max_length=100)
    client_dob = models.DateField()
    client_occupation = models.CharField(max_length=100)

    client_dl = models.CharField(max_length=50, blank=True, null=True)
    client_dl_exp = models.DateField(blank=True, null=True)
    client_dl_issued = models.DateField(blank=True, null=True)

    # --- Spouse info (NO SSN STORED) ---
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_dob = models.DateField(blank=True, null=True)
    spouse_occupation = models.CharField(max_length=100, blank=True, null=True)

    spouse_dl = models.CharField(max_length=50, blank=True, null=True)
    spouse_dl_exp = models.DateField(blank=True, null=True)
    spouse_dl_issued = models.DateField(blank=True, null=True)

    # --- Contact & filing info ---
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    phone_number = models.CharField(max_length=20)
    cell_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()

    filing_status = models.CharField(max_length=10)

    # --- Dependents (NO SSN STORED) ---
    dep1_name = models.CharField(max_length=100, blank=True, null=True)
    dep1_dob = models.DateField(blank=True, null=True)
    dep1_rel = models.CharField(max_length=50, blank=True, null=True)
    dep1_months = models.IntegerField(blank=True, null=True)

    dep2_name = models.CharField(max_length=100, blank=True, null=True)
    dep2_dob = models.DateField(blank=True, null=True)
    dep2_rel = models.CharField(max_length=50, blank=True, null=True)
    dep2_months = models.IntegerField(blank=True, null=True)

    dep3_name = models.CharField(max_length=100, blank=True, null=True)
    dep3_dob = models.DateField(blank=True, null=True)
    dep3_rel = models.CharField(max_length=50, blank=True, null=True)
    dep3_months = models.IntegerField(blank=True, null=True)

    # --- "list in one column" fields ---
    # Store selections like: "wages,pension,ss"
    income_sources = models.TextField(blank=True, null=True)
    expenses = models.TextField(blank=True, null=True)

    # --- Certification ---
    certification = models.BooleanField(default=False)
    client_signature = models.CharField(max_length=100)
    date_signed = models.DateField()

    def __str__(self):
        return f"Personal Intake: {self.client_name} ({self.created_at.date()})"
