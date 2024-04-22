import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import django
import numpy as np
import joblib
from django.core.wsgi import get_wsgi_application
import os
import sys
import plotly.graph_objs as go
from django.db.models import Sum
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
# from yellowbrick.classifier import DiscriminationThreshold

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CRM.settings')
django.setup()


# Import Django model after setup
from accounts.models import Customer
from accounts.models import ServiceDetails
from accounts.models import Revenue


def connect_db():
    conn = sqlite3.connect('db.sqlite3')
    return conn


# Function to fetch customer service data
def fetch_customer_service_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accounts_servicedetails')
    data = cursor.fetchall()
    conn.close()
    return data


# Function to fetch customer fields
def fetch_customer_fields():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(accounts_servicedetails)')
    columns = cursor.fetchall()
    fields = [col[1] for col in columns]
    conn.close()
    return fields


# Function to fetch customer acquisition data
def fetch_customer_acquisition_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT "Signup Date" FROM accounts_customer')  # Adjust column name if necessary
    data = cursor.fetchall()
    conn.close()
    return data


# Function to fetch customer demographics data
def fetch_customer_demographics_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT Gender FROM accounts_customer')  # Adjust column names if necessary
    data = cursor.fetchall()
    conn.close()
    return data


# Function to fetch revenue data
def fetch_revenue_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT date, total_amount FROM accounts_revenue')
    data = cursor.fetchall()
    conn.close()
    return data


# Function to count customers per service
def count_customers_per_service(customer_data, fields):
    services = ['PhoneService', 'MultipleLines', 'No_ofLines', 'InternetService',
                'OnlineSecurity', 'DeviceProtection', 'TechSupport',
                'StreamingTV', 'StreamingMovies', 'OnlineBackup']


    service_counts = {service: 0 for service in services}
    for row in customer_data:
        row_dict = dict(zip(fields, row))
        for service in services:
            if row_dict.get(service) == 'Yes':
                service_counts[service] += 1


    return service_counts


# Function to generate service usage chart
def generate_service_usage_chart():
    st.header('Service Usage')
    # Load data from the database
    customer_data = fetch_customer_service_data()
    customer_fields = fetch_customer_fields()


    # Count customers per service
    service_counts = count_customers_per_service(customer_data, customer_fields)


    # Create DataFrame
    df = pd.DataFrame.from_dict(service_counts, orient='index', columns=['Number of Customers'])
    df.index.name = 'Service'


    # Create pie chart without legend and with explicit text labels
    fig = px.pie(df, values='Number of Customers', names=df.index)
    fig.update_traces(textposition='inside', textinfo='percent')


    # Display chart
    st.plotly_chart(fig)


# Function to generate customer acquisition chart
def generate_customer_acquisition_chart():
    st.header('Customer Acquisition')
    # Load data from the database
    customer_acquisition_data = fetch_customer_acquisition_data()
    df_customer_acquisition = pd.DataFrame(customer_acquisition_data, columns=['Signup Date'])


    # Convert Signup Date to datetime
    df_customer_acquisition['Signup Date'] = pd.to_datetime(df_customer_acquisition['Signup Date'], errors='coerce')


    # Drop rows with NaT (not a valid datetime)
    df_customer_acquisition.dropna(subset=['Signup Date'], inplace=True)


    # Sort dataframe by Signup Date
    df_customer_acquisition.sort_values(by='Signup Date', inplace=True)


    # Create a column for cumulative sum of customers
    df_customer_acquisition['Cumulative Customers'] = df_customer_acquisition.index + 1


    # Create a new column for time increments (weeks)
    df_customer_acquisition['Weeks'] = df_customer_acquisition['Signup Date'] - df_customer_acquisition['Signup Date'].min()
    df_customer_acquisition['Weeks'] = df_customer_acquisition['Weeks'] // pd.Timedelta(days=7)


    # Group by weeks and calculate the cumulative sum of customers
    df_cumulative_customers = df_customer_acquisition.groupby('Weeks')['Cumulative Customers'].max().reset_index()


    # Create line chart for customer acquisition
    fig_line_customer_acquisition = px.line(df_cumulative_customers, x='Weeks', y='Cumulative Customers')


    # Remove negative numbers from x and y axes
    fig_line_customer_acquisition.update_layout(xaxis=dict(range=[0, df_cumulative_customers['Weeks'].max()]),
                                                 yaxis=dict(range=[0, df_cumulative_customers['Cumulative Customers'].max()]))


    # Display chart
    st.plotly_chart(fig_line_customer_acquisition)


# Function to generate customer demographics by gender chart
def generate_customer_demographics_by_gender_chart():
    st.header('Customer Demographics by Gender')
    # Load data from the database
    customer_demographics_data = fetch_customer_demographics_data()
    df_customer_demographics = pd.DataFrame(customer_demographics_data, columns=['Gender'])


    # Convert gender to lowercase
    df_customer_demographics['Gender'] = df_customer_demographics['Gender'].str.lower()


    # Count customers by gender
    customer_gender_counts = df_customer_demographics['Gender'].value_counts().reset_index()
    customer_gender_counts.columns = ['Gender', 'Number of Customers']


    # Create bar chart for customer demographics by gender
    fig_customer_demographics_gender = px.bar(customer_gender_counts, x='Gender', y='Number of Customers',  
                                        labels={'Gender': 'Gender', 'Number of Customers': 'Number of Customers'})


    # Display chart
    st.plotly_chart(fig_customer_demographics_gender)


    # Service Usage by Gender
    st.title('Usage of Service by Gender')
    # Function to fetch data from the database
    def fetch_service_data(service_name):
        # Fetch data from ServiceDetails table
        service_data = ServiceDetails.objects.filter(**{service_name: 'Yes'})


        # Convert data to DataFrame
        df_service = pd.DataFrame(list(service_data.values()))


        # Get IDs of customers using the service
        customer_ids = df_service['customer_id']


        # Fetch data from Customer table for these customer IDs
        customer_data = Customer.objects.filter(id__in=customer_ids).values()


        # Convert data to DataFrame
        df_customer = pd.DataFrame(list(customer_data))


        # Merge the Customer and ServiceDetails tables on the appropriate column
        merged_df = pd.merge(df_service, df_customer, left_on='customer_id', right_on='id', how='inner')


        return merged_df


    # Function to create a donut chart
    def create_donut_chart(df, service_name):
        # Count the number of males and females using the service
        service_counts = df.groupby('gender').size()


        # Create donut
        fig = px.pie(service_counts, values=service_counts, names=service_counts.index, hole=0.5,
                     title=f'{service_name}')


        # Change color based on gender
        fig.update_traces(marker=dict(colors=['pink', 'blue']), selector=dict(type='pie'))


        return fig


    # Main code
    services = ["PhoneService", "OnlineSecurity", "DeviceProtection"]  


    # Create columns for charts
    col1, col2, col3 = st.columns(3)


    # Fetch data and create charts for each service
    for service_name, col in zip(services, [col1, col2, col3]):
        # Fetch data from the database
        merged_df = fetch_service_data(service_name)


        # Create a donut chart
        fig = create_donut_chart(merged_df, service_name)


        # Display chart with individual title
        col.plotly_chart(fig, use_container_width=True)


# Function to generate revenue chart
def generate_revenue_chart():
    st.title('Revenue Generated by Service')

    # Fetch revenue data
    revenue = Revenue.objects.first()

    # Create data for the chart
    service_labels = ['Phone Service', 'Internet Service', 'Online Security', 'Device Protection',
                      'Streaming TV', 'Streaming Movies', 'Online Backup', 'Tech Support']
    service_revenues = [revenue.phone_service_revenue, revenue.internet_service_revenue,
                        revenue.online_security_revenue, revenue.device_protection_revenue,
                        revenue.streaming_tv_revenue, revenue.streaming_movies_revenue,
                        revenue.online_backup_revenue, revenue.tech_support_revenue]

    # Create a Plotly bar chart
    fig = go.Figure(data=[go.Bar(x=service_labels, y=service_revenues)])
    fig.update_layout(xaxis_title='Service',
                      yaxis_title='Revenue')
                      

    # Display the chart
    st.plotly_chart(fig)

    #revenue time series
    st.title('Revenue Time Analysis')
    # Fetch revenue data
    revenues = Revenue.objects.all().order_by('time_recorded')

    # Extract data for the chart
    time_values = [revenue.time_recorded for revenue in revenues]
    total_revenues = [revenue.calculate_total_revenue() for revenue in revenues]

    # Create a Plotly line chart
    fig = go.Figure(data=go.Scatter(x=time_values, y=total_revenues, mode='lines+markers'))
    fig.update_layout(xaxis_title='Time',
                      yaxis_title='Total Revenue')
    
    # Display the chart 
    st.plotly_chart(fig)


    st.title('Revenue Profit and Loss Analysis')

    # Fetch revenue data
    revenues = Revenue.objects.all().order_by('time_recorded')

    # Extract data for the chart
    time_values = [revenue.time_recorded for revenue in revenues]
    total_revenues = [revenue.calculate_total_revenue() for revenue in revenues]

    # Calculate profit and loss
    profits_losses = [total_revenues[i] - total_revenues[i-1] if i > 0 else 0 for i in range(len(total_revenues))]

    # Create a Plotly scatter plot for profit and loss
    fig = go.Figure(data=go.Scatter(x=time_values, y=profits_losses, mode='markers'))
    fig.update_layout(xaxis_title='Time',
                      yaxis_title='Profit / Loss')

    # Display the chart
    st.plotly_chart(fig)



###########prediction visualization
# Sample data
data = pd.read_csv("Telco-Customer-Churn.csv") 


# Drop non-numeric columns or encode them
data.drop(columns=['customerID'], inplace=True)  # Drop non-numeric identifier

# Encoding categorical variables
label_encoders = {}
for column in data.select_dtypes(include=['object']).columns:
    label_encoders[column] = LabelEncoder()
    data[column] = label_encoders[column].fit_transform(data[column])

X = data.drop(columns=['Churn'])
y_true = data['Churn']

# Fit your model
model = RandomForestClassifier()
model.fit(X, y_true)
y_pred_proba = model.predict_proba(X)[:, 1]

st.title('ML MODEL CHURN PREDICTION CHARTS')

# # Confusion Matrix
# st.subheader("Confusion Matrix")
# cm = confusion_matrix(y_true, model.predict(X))
# st.write(cm)

# # ROC Curve
# st.subheader("ROC Curve")
# fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
# roc_auc = auc(fpr, tpr)
# fig, ax = plt.subplots()
# ax.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
# ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
# ax.set_xlabel('False Positive Rate')
# ax.set_ylabel('True Positive Rate')
# ax.set_title('Receiver Operating Characteristic (ROC) Curve')
# ax.legend(loc="lower right")
# st.pyplot(fig)

# Feature Importance
st.subheader("Feature Importance")
importances = model.feature_importances_
features = X.columns
feat_importances = pd.Series(importances, index=features)
fig, ax = plt.subplots()
feat_importances.nlargest(10).plot(kind='barh', ax=ax)
ax.set_xlabel('Relative Importance')
ax.set_title('Feature Importance')
st.pyplot(fig)

# Probability Distribution
st.subheader("Probability Distribution of Churn Predictions")
fig, ax = plt.subplots()
ax.hist(y_pred_proba, bins=25, alpha=0.7, color='blue')
ax.set_xlabel('Predicted Probability of Churn')
ax.set_ylabel('Frequency')
ax.set_title('Probability Distribution of Churn Predictions')
st.pyplot(fig)

# # Lift Curve
# st.subheader("Lift Curve")
# fig, ax = plt.subplots()
# visualizer = DiscriminationThreshold(model)
# visualizer.fit(X, y_true)
# visualizer.poof()
# st.pyplot(fig)

# Sidebar navigation
st.sidebar.header("Navigation: ")


if st.sidebar.button("Service Usage"):
    generate_service_usage_chart()


if st.sidebar.button("Customer Acquisition"):
    generate_customer_acquisition_chart()


if st.sidebar.button("Customer Demographics"):
    generate_customer_demographics_by_gender_chart()


if st.sidebar.button("Revenues"):
    generate_revenue_chart()





