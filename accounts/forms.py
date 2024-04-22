from django import forms
from django.forms import ModelForm
from .models import *

class CustomerForm(ModelForm):
    class Meta: 
        model = Customer
        fields = '__all__' 
        
# class SubscriptionDetailsForm(forms.ModelForm):
#     class Meta:
#         model = SubscriptionDetails
#         fields = '__all__'
#         exclude = ['customer']