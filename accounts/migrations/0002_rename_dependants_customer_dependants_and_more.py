# Generated by Django 5.0.2 on 2024-04-20 10:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='dependants',
            new_name='Dependants',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='partner',
            new_name='Partner',
        ),
        migrations.CreateModel(
            name='ServiceDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PhoneService', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=3)),
                ('MultipleLines', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No phone service', 'No phone service')], max_length=50)),
                ('No_ofLines', models.IntegerField()),
                ('InternetService', models.CharField(choices=[('DSL', 'DSL'), ('Fiber optic', 'Fiber optic'), ('No', 'No')], max_length=50)),
                ('OnlineSecurity', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('DeviceProtection', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('TechSupport', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('StreamingTV', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('StreamingMovies', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('OnlineBackUp', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No'), ('No internet service', 'No internet service')], max_length=50)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_details', to='accounts.customer')),
            ],
        ),
    ]
