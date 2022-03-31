
from django.db import models
# from django.db.models import Count
# from django.db.models.functions import Concat


class OrderQueryset(models.QuerySet):
    def unpaid(self):
        return self.filter(is_paid=False)

    def sales(self):
        return self.filter(is_paid=True)


class OrderManager(models.Manager):
    def sales(self):
        return self.get_queryset().sales()

    def get_queryset(self, *args, **kwargs):
        return OrderQueryset(self.model, *args, using=self._db, **kwargs)\
            .exclude(is_completed=False)\
            .select_related('customer',)\
            .prefetch_related('products')


class CartManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_paid=False, is_completed=False)
