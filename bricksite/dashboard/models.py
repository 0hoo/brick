from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.models import TimeStampedModel


class Dashboard(TimeStampedModel):
    user = models.ForeignKey(User, related_name='dashboard_set')

    owned_count = models.PositiveIntegerField()
    owned_quantity = models.PositiveIntegerField()

    total_estimated_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_profit = models.DecimalField(max_digits=8, decimal_places=2)
    total_official_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_official_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_buying_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_target_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_target_price = models.DecimalField(max_digits=8, decimal_places=2)

    owned_new_min_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_new_max_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_new_average_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_min_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_max_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_average_price = models.DecimalField(max_digits=8, decimal_places=2)

    owned_new_min_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_new_max_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_new_average_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_min_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_max_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)
    owned_used_average_ebay_price = models.DecimalField(max_digits=8, decimal_places=2)

    target_at = models.DateField()

    def __str__(self):
        return '{} dashboard: {}'.format(self.user.username, self.target_at)

    class Meta:
        verbose_name = 'Dashboard'
        get_latest_by = 'target_at'
        ordering = ('-target_at',)
