# from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import JsonResponse
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os

# mother views  
def dashboard(request):
    customers = Customer.objects.all()
    total_customers = customers.count()

    return render(request, 'accounts/dashboard.html',)

def login(request):
    return render(request, 'accounts/login.html')

# customer
def customers(request):
    customers= Customer.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(customers, 7)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    return render(request, 'accounts/customers.html', {'customers': customers})

def viewCustomerDetails(request, pk):
    customer = Customer.objects.get(id=pk)
    service_details = customer.services  
    billing_details = service_details.bills
    
    context = {
        'customer': customer,
        'service_details': service_details,
        'billing_details':billing_details
    }
    return render(request, 'accounts/customer_details.html', context)

# def addCustomer(request):
#     form = CustomerForm()
#     if request.method == 'POST':
#         form = CustomerForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('customers')

#     context = {'form':form}
#     return render(request, 'accounts/forms/customer_add.html', context)

# def updateCustomer(request,pk):
#     customer = Customer.objects.get(id=pk)
#     form = CustomerForm(instance=customer)

#     if request.method == 'POST':
#         form = CustomerForm(request.POST, instance=customer)
#         if form.is_valid():
#             form.save()
#             return redirect('customers')
#     context = {'form':form}
#     return render(request, 'accounts/forms/customer_update.html', context)

# def deleteCustomer(request,pk):
#     customer = Customer.objects.get(id=pk)
#     if request.method == 'POST':
#         customer.delete()
#         return redirect('customers')
#     context = {'customer':customer}
#     return render(request, 'accounts/forms/customer_delete.html', context)



# def updateCustomer(request,pk):
#     customer = Customer.objects.get(id=pk)
#     form = CustomerForm(instance=customer)

#     if request.method == 'POST':
#         form = CustomerForm(request.POST, instance=customer)
#         if form.is_valid():
#             form.save()
#             return redirect('customers')
#     context = {'form':form}
#     return render(request, 'accounts/forms/customer_update.html', context)

# def addSubscription(request, pk):
#     customer = get_object_or_404(Customer, id=pk)

#     if request.method == 'POST':
#         subscription_details_form = SubscriptionDetailsForm(request.POST)
#         if subscription_details_form.is_valid():
#             subscription_details = subscription_details_form.save(commit=False)
#             subscription_details.customer = customer
#             subscription_details.save()
#             customer.subscription_status = 'Subscribed'
#             customer.save()
#             return redirect('subscribedCustomers')
#     else:
#         subscription_details_form = SubscriptionDetailsForm()

#     context = {
#         'subscription_details_form': subscription_details_form,
#         'customer': customer,
#     }
#     return render(request, 'accounts/forms/customer_subscribe.html', context)




##visualization dashboard


def run_streamlit_app():
    # Run the Streamlit app as a subprocess
    os.system("streamlit run dashboard.py")


def get_data(request):
    data = YourModel.objects.all().values()  # Query your data from the database
    return JsonResponse(list(data), safe=False)


def streamlit_view(request):
    # Start the Streamlit app
    run_streamlit_app()


    return render(request, "streamlit.html")

def revenue_view(request):
    # Update revenue data
    Revenue.update_revenues()
   
    # Fetch specific revenues
    revenue = Revenue.objects.first()
   
    # Calculate total revenue
    total_revenue = Revenue.calculate_total_revenue()


    # Render the template with the revenue data
    return render(request, 'accounts/revenue_form.html', {'revenue': revenue, 'total_revenue': total_revenue})