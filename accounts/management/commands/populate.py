from django.core.management.base import BaseCommand
from accounts.models import Customer
from datetime import datetime

class Command(BaseCommand):
    help = 'Populates the customer data in the database'

    def handle(self, *args, **options):
        customers = [
            {
                'first_name': 'Juma',
                'last_name': 'Wambua',
                'date_of_birth': '1988-02-15',
                'gender': 'Male',
                'phone_number': '+254712345678',
                'email': 'juma.wambua@gmail.com',
                'occupation': 'Teacher',
                'town': 'Mombasa',
                'county': 'Mombasa',
                'nationality': 'Kenyan',
                'national_id': '12345678',
                'passport': None,
                'dependants': 'Yes',
                'marital_status': 'Married',
                'partner': 'Yes',
                'income_status': 'MIDDLE_INCOME',
                'employment_status': 'EMPLOYED',
                'join_month_year': '09/2019'
            },
            {
                'first_name': 'Asha',
                'last_name': 'Odhiambo',
                'date_of_birth': '1992-07-20',
                'gender': 'Female',
                'phone_number': '+254789012345',
                'email': 'asha.odhiambo@gmail.com',
                'occupation': 'Nurse',
                'town': 'Kisumu',
                'county': 'Kisumu',
                'nationality': 'Kenyan',
                'national_id': '98765432',
                'passport': None,
                'dependants': 'No',
                'marital_status': 'Single',
                'partner': 'No',
                'income_status': 'MIDDLE_INCOME',
                'employment_status': 'EMPLOYED',
                'join_month_year': '03/2020'
            },
            {
                'first_name': 'Kamau',
                'last_name': 'Kimani',
                'date_of_birth': '1985-11-05',
                'gender': 'Male',
                'phone_number': '+254765432109',
                'email': 'kamau.kimani@gmail.com',
                'occupation': 'Software Engineer',
                'town': 'Nairobi',
                'county': 'Nairobi',
                'nationality': 'Kenyan',
                'national_id': '45678912',
                'passport': None,
                'dependants': 'Yes',
                'marital_status': 'Married',
                'partner': 'Yes',
                'income_status': 'HIGH_INCOME',
                'employment_status': 'EMPLOYED',
                'join_month_year': '06/2019'
            },
            {
                'first_name': 'Amina',
                'last_name': 'Muthoni',
                'date_of_birth': '1990-03-12',
                'gender': 'Female',
                'phone_number': '+254723456789',
                'email': 'amina.muthoni@gmail.com',
                'occupation': 'Accountant',
                'town': 'Nakuru',
                'county': 'Nakuru',
                'nationality': 'Kenyan',
                'national_id': '23456789',
                'passport': None,
                'dependants': 'No',
                'marital_status': 'Has_Partner',
                'partner': 'Yes',
                'income_status': 'MIDDLE_INCOME',
                'employment_status': 'EMPLOYED',
                'join_month_year': '11/2020'
            },
            {
                'first_name': 'Omondi',
                'last_name': 'Otieno',
                'date_of_birth': '1982-09-28',
                'gender': 'Male',
                'phone_number': '+254734567890',
                'email': 'omondi.otieno@gmail.com',
                'occupation': 'Farmer',
                'town': 'Eldoret',
                'county': 'Uasin Gishu',
                'nationality': 'Kenyan',
                'national_id': '67890123',
                'passport': None,
                'dependants': 'Yes',
                'marital_status': 'Married',
                'partner': 'Yes',
                'income_status': 'LOW_INCOME',
                'employment_status': 'SELF_EMPLOYED',
                'join_month_year': '02/2022'
            }
        ]

        for customer_data in customers:
            Customer.objects.create(
                first_name=customer_data['first_name'],
                last_name=customer_data['last_name'],
                date_of_birth=datetime.strptime(customer_data['date_of_birth'], '%Y-%m-%d').date(),
                gender=customer_data['gender'],
                phone_number=customer_data['phone_number'],
                email=customer_data['email'],
                occupation=customer_data['occupation'],
                town=customer_data['town'],
                county=customer_data['county'],
                nationality=customer_data['nationality'],
                national_id=customer_data['national_id'],
                passport=customer_data['passport'],
                dependants=customer_data['dependants'],
                marital_status=customer_data['marital_status'],
                partner=customer_data['partner'],
                income_status=customer_data['income_status'],
                employment_status=customer_data['employment_status'],
                join_month_year=customer_data['join_month_year']
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated customer data'))
