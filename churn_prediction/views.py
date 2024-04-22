import pickle
import os
from django.shortcuts import render
from accounts.models import *
import numpy as np

def load_model():
    dir = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(dir, 'model.sav')

    try:
        # Load the saved model
        model = pickle.load(open(model_path, 'rb'))
        return model
    except FileNotFoundError:
        return None
    except pickle.UnpicklingError:
        return None

def preprocess_data():
    # Retrieve the customer and contract data from the database
    customers = Customer.objects.all()
    contracts = ServiceDetails.objects.all()
    billings = BillingDetails.objects.all()

    # Preprocess the data
    input_data = []
    for customer in customers:
        contract = contracts.filter(customer=customer).first()
        billing = billings.filter(service_details=contract).first() if contract else None
        if contract and billing:
            row = preprocess_row(customer, contract, billing)
            input_data.append(row)

    return input_data

def preprocess_row(customer,contract,billing):
    row = [
        # billing
        billing.MonthlyCharges,
        billing.TotalCharges,
        
        # customer
        int(customer.gender == 'Female'),
        int(customer.gender == 'Male'),
        
        int(customer.Partner == 'No'),
        int(customer.Partner == 'Yes'),
        
        int(customer.Dependants == 'No'),
        int(customer.Dependants == 'Yes'),
        
        # services 
        int(contract.PhoneService == 'No'),
        int(contract.PhoneService == 'Yes'),
        
        int(contract.MultipleLines == 'No'),
        int(contract.MultipleLines == 'No phone service'),
        int(contract.MultipleLines == 'Yes'),
        
        int(contract.InternetService == 'DSL'),
        int(contract.InternetService == 'Fiber optic'),
        int(contract.InternetService == 'No'),
        
        int(contract.OnlineSecurity == 'No'),
        int(contract.OnlineSecurity == 'No internet service'),
        int(contract.OnlineSecurity == 'Yes'),
        
        int(contract.DeviceProtection == 'No'),
        int(contract.DeviceProtection == 'No internet service'),
        int(contract.DeviceProtection == 'Yes'),
        
        int(contract.TechSupport == 'No'),
        int(contract.TechSupport == 'No internet service'),
        int(contract.TechSupport == 'Yes'),
        
        int(contract.StreamingTV == 'No'),
        int(contract.StreamingTV == 'No internet service'),
        int(contract.StreamingTV == 'Yes'),
        
        int(contract.StreamingMovies == 'No'),
        int(contract.StreamingMovies == 'No internet service'),
        int(contract.StreamingMovies == 'Yes'),
        
        # billing
        int(billing.ContractType == 'Month-to-month'),
        int(billing.ContractType == 'One year'),
        int(billing.ContractType == 'Two year'),
        
        int(billing.PaperlessBilling == 'No'),
        int(billing.PaperlessBilling == 'Yes'),
        
        int(billing.PaymentMethod == 'Bank transfer (automatic)'),
        int(billing.PaymentMethod == 'Credit card (automatic)'),
        int(billing.PaymentMethod == 'Electronic check'),
        int(billing.PaymentMethod == 'Mailed check'),
        
        int(contract.OnlineBackUp == 'NO'),
        int(contract.OnlineBackUp == 'Yes'),
        int(contract.OnlineBackUp == 'No internet service'),
        
        # customer
        int(1 <= customer.tenure <= 12),
        int(13 <= customer.tenure <= 24),
        int(25 <= customer.tenure <= 36),
        int(37 <= customer.tenure <= 48),
        int(49 <= customer.tenure <= 60),
        int(61 <= customer.tenure <= 72)
    ]
    return row

def predict_churn(request):
    model = load_model()
    if model is None:
        return render(request, 'churn_prediction/error.html', {'error': 'Model file not found or error loading the model.'})

    input_data = preprocess_data()

    # Make the predictions
    y_pred = model.predict(input_data)
    y_pred_proba = model.predict_proba(input_data)

    # Zip the customer data, predictions, and probabilities together
    customers = Customer.objects.all()
    customer_predictions = []
    promotion_messages = []
    for customer, prediction, proba in zip(customers, y_pred, y_pred_proba):
        churn_confidence = np.max(proba) * 100
        if prediction == 0:  # Not churned
            promotion_message = f"Dear valued customer {customer.first_name}, we appreciate your continued support and loyalty.\n We offer you 1 Free Month of Tech Support (FREE ROUTER UPGRADE)"
        else:  # Churned
            if churn_confidence < 30:
                promotion_message = "Ksh. 10% NEXT MONTH PAYMENT DISCOUNT AWARDED"
            elif 30 <= churn_confidence < 50:
                promotion_message = "Ksh. 20% NEXT MONTH PAYMENT DISCOUNT AWARDED"
            elif 50 <= churn_confidence < 70:
                promotion_message = "Ksh. 20% NEXT MONTH PAYMENT DISCOUNT AWARDED\n 1Free Month of Tech Support (FREE ROUTER UPGRADE)"
            elif 70 <= churn_confidence < 90:
                promotion_message = "Ksh. 20% NEXT MONTH PAYMENT DISCOUNT AWARDED\n 1Free Month of Tech Support (FREE ROUTER UPGRADE, SOFTWARE UPGRADES)\n50% Discount On Next Month TV Streaming Service\n5GB OUTDOOR INTERNET BUNDLES"
            else:
                promotion_message = "EMERGENT PHONE CALL (REGARDING OUR SERVICE COMPLAINT)\nKsh. 20% NEXT MONTH PAYMENT DISCOUNT AWARDED\n1 Free Month of Tech Support (FREE ROUTER UPGRADE, SOFTWARE UPGRADES)\n50% Discount On Next Month TV Streaming Service"
        customer_predictions.append((customer, prediction, churn_confidence))
        promotion_messages.append((customer, promotion_message))

    # Calculate the overall prediction
    total_customers = len(customers)
    churned_customers = sum(1 for _, prediction in zip(customers, y_pred) if prediction == 1)
    overall_churn_rate = churned_customers / total_customers * 100

    return render(request, 'churn_prediction/prediction.html', {
        'customer_predictions': customer_predictions,
        'overall_churn_rate': overall_churn_rate,
        'promotion_messages': promotion_messages
    })
