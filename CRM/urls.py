
# URL configuration for CRM project.
from django.contrib import admin
from django.urls import path, include
# from streamlit_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('churn-prediction/', include('churn_prediction.urls')),
    # path('streamlit_app/', include('streamlit_app.urls')),
    
]
