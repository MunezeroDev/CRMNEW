from django.urls import path

from . import views 

urlpatterns = [
    # ======================main==========
    path('churn/', views.predict_churn, name="predict-churn"),
    
]
