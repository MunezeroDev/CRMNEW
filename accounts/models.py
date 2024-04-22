from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import datetime
from decimal import Decimal

# Custom validator for phone number
phone_regex = RegexValidator(
    regex=r'^\+?254\d{9}$',
    message="Phone number must be entered in the format: '+254xxxxxxxxx' for Kenya. Exactly 12 digits allowed."
)

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    # choices
    gender = models.CharField(max_length=6, choices=[('Male', 'Male'), ('Female', 'Female')])
    
    phone_number = models.CharField(validators=[phone_regex], max_length=13, blank=True)
    email = models.EmailField()
    occupation = models.CharField(max_length=100)
    town = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    
    nationality = models.CharField(max_length=20, choices=[('Kenyan', 'Kenyan'), ('Non-Kenyan', 'Non-Kenyan')])
    
    national_id = models.CharField(max_length=20, blank=True, null=True)
    passport = models.CharField(max_length=20, blank=True, null=True)
    
    DEPCHOICE = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    )
    Dependants = models.CharField(max_length=3, choices=DEPCHOICE)
  
    marital_status = models.CharField(max_length=20, choices=[('Married', 'Married'), ('Single', 'Single'), ('Divorced', 'Divorced'), ('Has_Partner', 'Has_Partner')])
    Partner = models.CharField(max_length=3)
    
    income_status = models.CharField(max_length=20, choices=[('LOW_INCOME', 'LOW_INCOME'), ('MIDDLE_INCOME', 'MIDDLE_INCOME'), ('HIGH_INCOME', 'HIGH_INCOME')])
    employment_status = models.CharField(max_length=20, choices=[('EMPLOYED', 'EMPLOYED'), ('UNEMPLOYED', 'UNEMPLOYED'), ('SELF_EMPLOYED', 'SELF_EMPLOYED')])

    join_month_year = models.CharField(max_length=7, help_text="Enter in the format 'MM/YYYY'")
   
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # derive age
    @property
    def age(self):
        import datetime
        return datetime.datetime.now().year - self.date_of_birth.year
    
    def save(self, *args, **kwargs):
        if self.marital_status == 'MARRIED' or self.marital_status == 'Has_Partner':
            self.partner = 'Yes'
        else:
            self.partner = 'No'
        if self.nationality == 'Kenyan':
            if not self.national_id:
                raise ValueError('National ID is required for Kenyan citizens.')
            self.passport = None
        else:
            if not self.passport:
                raise ValueError('Passport number is required for non-Kenyan citizens.')
            self.national_id = None
        super().save(*args, **kwargs)
 
            
    @property
    def tenure(self):
        current_month_year = datetime.date.today().strftime('%m/%Y')
        join_month_year = self.join_month_year
        
        current_month, current_year = map(int, current_month_year.split('/'))
        join_month,  join_year, = map(int, join_month_year.split('/'))

        tenure_months = (current_year - join_year) * 12 + (current_month - join_month)
        
        if (current_year, current_month) < (join_year, join_month):
            tenure_months -= 12

        return tenure_months

class ServiceDetails(models.Model):
    customer = models.OneToOneField(Customer,related_name='services', on_delete=models.CASCADE)
    SELECT = (
        ('Yes', 'Yes'),
        ('No', 'No'),
    )
    PhoneService = models.CharField(max_length=3, choices=SELECT)  # 8
  
    LINESCHOICES = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('No phone service', 'No phone service'),
    )
    MultipleLines = models.CharField(max_length=50, choices=LINESCHOICES)
  
    No_ofLines = models.IntegerField()
  
    NETCHOICES = (
        ('DSL', 'DSL'),
        ('Fiber optic', 'Fiber optic'),
        ('No', 'No'),
    )
    InternetService = models.CharField(max_length=50, choices=NETCHOICES)
  
    FEATURES = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('No internet service', 'No internet service'),
    )
    OnlineSecurity = models.CharField(max_length=50, choices=FEATURES)
    DeviceProtection = models.CharField(max_length=50, choices=FEATURES)
    TechSupport = models.CharField(max_length=50, choices=FEATURES)
    StreamingTV = models.CharField(max_length=50, choices=FEATURES)
    StreamingMovies = models.CharField(max_length=50, choices=FEATURES)
    OnlineBackUp = models.CharField(max_length=50, choices=FEATURES)

    def __str__(self):
        return f"ServiceDetail for {self.customer} "
    
class BillingDetails(models.Model):
    service_details = models.OneToOneField(ServiceDetails,related_name='bills', on_delete=models.CASCADE)
    SELECT = (
       ('Yes', 'Yes'),
       ('No', 'No'),
    )
    PaperlessBilling = models.CharField(max_length=50, choices=SELECT)
  
    CONTRACT = (
        ('Month-to-month', 'Month-to-month'),
        ('One year', 'One year'),
        ('Two year', 'Two year'),
    )
    ContractType = models.CharField(max_length=50, choices=CONTRACT)
   
    PAYEMENT = (
        ('Bank transfer (automatic)', 'Bank transfer (automatic)'),
        ('Credit card (automatic)', 'Credit card (automatic)'),
        ('Electronic check', 'Electronic check'),
        ('Mailed check', 'Mailed check'),
    )
    PaymentMethod = models.CharField(max_length=50, choices=PAYEMENT)
  
    MonthlyCharges = models.IntegerField(null=True, blank=True)
    TotalCharges = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Billing Details for {self.service_details.customer.first_name} {self.service_details.customer.last_name}"



    def save(self, *args, **kwargs):
        monthly_charges, total_charges = calculate_monthly_charges(self.service_details)
        self.MonthlyCharges = monthly_charges
        self.TotalCharges = total_charges
        super().save(*args, **kwargs)

class Rates(models.Model):
   PHONE_SERVICE_COST = models.DecimalField(max_digits=10, decimal_places=2, default=800)
   LINES_COST_PER_LINE = models.DecimalField(max_digits=10, decimal_places=2, default=500)
   INTERNET_SERVICE_COST = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
   ONLINE_SECURITY_COST = models.DecimalField(max_digits=10, decimal_places=2, default=500)
   DEVICE_PROTECTION_COST_PER_DEVICE = models.DecimalField(max_digits=10, decimal_places=2, default=300)
   STREAMING_TV_COST = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
   STREAMING_MOVIES_COST = models.DecimalField(max_digits=10, decimal_places=2, default=700)
   ONLINE_BACKUP_COST = models.DecimalField(max_digits=10, decimal_places=2, default=500)
   TECH_SUPPORT_COST = models.DecimalField(max_digits=10, decimal_places=2, default=200)
  
   def __str__(self):
       return "Rates Table"

def calculate_monthly_charges(service_details):
    rates, created = Rates.objects.get_or_create(
        PHONE_SERVICE_COST=800,
        LINES_COST_PER_LINE=500,
        INTERNET_SERVICE_COST=2000,
        ONLINE_SECURITY_COST=500,
        DEVICE_PROTECTION_COST_PER_DEVICE=300,
        STREAMING_TV_COST=1000,
        STREAMING_MOVIES_COST=700,
        ONLINE_BACKUP_COST=500,
        TECH_SUPPORT_COST=200
    )

    monthly_charges = 0

    if service_details.PhoneService == 'Yes':
        monthly_charges += rates.PHONE_SERVICE_COST

    if service_details.MultipleLines == 'Yes':
        monthly_charges += rates.LINES_COST_PER_LINE * service_details.No_ofLines

    if service_details.InternetService == 'DSL' or service_details.InternetService == 'Fiber optic':
        monthly_charges += rates.INTERNET_SERVICE_COST

    if service_details.OnlineSecurity == 'Yes':
        monthly_charges += rates.ONLINE_SECURITY_COST

    if service_details.DeviceProtection == 'Yes':
        monthly_charges += rates.DEVICE_PROTECTION_COST_PER_DEVICE

    if service_details.StreamingTV == 'Yes':
        monthly_charges += rates.STREAMING_TV_COST

    if service_details.StreamingMovies == 'Yes':
        monthly_charges += rates.STREAMING_MOVIES_COST

    if service_details.OnlineBackUp == 'Yes':
        monthly_charges += rates.ONLINE_BACKUP_COST

    if service_details.TechSupport == 'Yes':
        monthly_charges += rates.TECH_SUPPORT_COST

    tenure = service_details.customer.tenure  # Assuming 'tenure' field exists in the Customer model
    total_charges = monthly_charges * tenure

    return int(monthly_charges), int(total_charges)


class Revenue(models.Model):
    phone_service_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    internet_service_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    online_security_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    device_protection_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    streaming_tv_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    streaming_movies_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    online_backup_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tech_support_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_recorded = models.DateTimeField(auto_now_add=True)


    @classmethod
    def update_revenues(cls):
        rates = Rates.objects.first()
        phone_service_count = ServiceDetails.objects.filter(PhoneService='Yes').count()
        internet_service_count = ServiceDetails.objects.filter(InternetService='Yes').count()
        online_security_count = ServiceDetails.objects.filter(OnlineSecurity='Yes').count()
        device_protection_count = ServiceDetails.objects.filter(DeviceProtection='Yes').count()
        streaming_tv_count = ServiceDetails.objects.filter(StreamingTV='Yes').count()
        streaming_movies_count = ServiceDetails.objects.filter(StreamingMovies='Yes').count()
        online_backup_count = ServiceDetails.objects.filter(OnlineBackUp='Yes').count()
        tech_support_count = ServiceDetails.objects.filter(TechSupport='Yes').count()


        # Calculate revenue for each service
        phone_service_revenue = rates.PHONE_SERVICE_COST * phone_service_count
        internet_service_revenue = rates.INTERNET_SERVICE_COST * internet_service_count
        online_security_revenue = rates.ONLINE_SECURITY_COST * online_security_count
        device_protection_revenue = rates.DEVICE_PROTECTION_COST_PER_DEVICE * device_protection_count
        streaming_tv_revenue = rates.STREAMING_TV_COST * streaming_tv_count
        streaming_movies_revenue = rates.STREAMING_MOVIES_COST * streaming_movies_count
        online_backup_revenue = rates.ONLINE_BACKUP_COST * online_backup_count
        tech_support_revenue = rates.TECH_SUPPORT_COST * tech_support_count


        # Update revenue model instance
        revenue, _ = cls.objects.get_or_create(id=1)
        revenue.phone_service_revenue = phone_service_revenue
        revenue.internet_service_revenue = internet_service_revenue
        revenue.online_security_revenue = online_security_revenue
        revenue.device_protection_revenue = device_protection_revenue
        revenue.streaming_tv_revenue = streaming_tv_revenue
        revenue.streaming_movies_revenue = streaming_movies_revenue
        revenue.online_backup_revenue = online_backup_revenue
        revenue.tech_support_revenue = tech_support_revenue
        revenue.save()


    @classmethod
    def calculate_total_revenue(cls):
        total_revenue = cls.objects.aggregate(
            total=models.Sum(
                models.F('phone_service_revenue') +
                models.F('internet_service_revenue') +
                models.F('online_security_revenue') +
                models.F('device_protection_revenue') +
                models.F('streaming_tv_revenue') +
                models.F('streaming_movies_revenue') +
                models.F('online_backup_revenue') +
                models.F('tech_support_revenue')
            )
        )['total'] or 0
        return total_revenue
   
    def __str__(self):
        return f"Revenue Data - {self.time_recorded}"



