from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(ServiceDetails)
admin.site.register(BillingDetails)
admin.site.register(Rates)
admin.site.register(Revenue)
# admin.site.register(Promotion)