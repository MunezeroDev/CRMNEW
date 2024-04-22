from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Revenue


@receiver(post_save, sender=Revenue)
def update_revenue_monthly(sender, instance, **kwargs):
    # Check if the revenue data is updated on the first day of the month
    if timezone.now().day == 1:
        # Update the revenue data
        Revenue.update_revenues()