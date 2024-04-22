from django.urls import path

from . import views 

from .views import streamlit_view,revenue_view

urlpatterns = [
    # ======================main==========
    path('', views.dashboard, name=""),
    path('login/', views.login,name="login"),
    
    # customers
    path('customers/', views. customers,name="customers"),
    path('customer_details/<str:pk>/',views.viewCustomerDetails,name="customer_details"),
    # path('customer_add/', views.addCustomer, name='customer_add'),
    # path('customer_update/<str:pk>/', views.updateCustomer, name='customer_update'),
    # path('customer_delete/<str:pk>/', views.deleteCustomer, name='customer_delete'),
    # path('customer_details/<str:pk>/',views.viewCustomerDetails,name="customer_details"),#p
    # path('customer_subscribe/<str:pk>/',views.addSubscription,name="customer_subscribe")
    
    
    ###visualization
    path('streamlit/', views.streamlit_view, name='streamlit'),

    #######revenue
    path('revenue/', revenue_view, name='revenue'),

]
