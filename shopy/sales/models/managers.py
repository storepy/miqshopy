
from django.db import models
# from django.db.models import Count
from django.db.models.functions import Concat

#
# CUSTOMER
#


class CustomerQuerySet(models.QuerySet):
    def by_amount_spent(self, order: str = None):

        qs = self.annotate(spent=models.Sum('orders__total'))
        if order == 'asc':
            return qs.order_by('spent')
        elif order == 'desc':
            return qs.order_by('-spent')

        return qs

    def find(self, q: str, **kwargs):
        if not isinstance(q, str):
            return self.none()

        q = q.lower()
        keys = ('phone', 'first_name', 'last_name', 'email')

        return self.annotate(values=Concat(*keys, output_field=models.CharField()))\
            .filter(values__icontains=q).distinct()


class CustomerManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        return CustomerQuerySet(self.model, *args, using=self._db, **kwargs)


#
# ORDER
#

class OrderQuerySet(models.QuerySet):
    def total(self):
        return self.aggregate(total=models.Sum('total'))['total']


class OrderManager(models.Manager):
    def sales(self):
        return self.get_queryset().filter(is_delivered=True)

    def pending(self):
        return self.get_queryset().filter(is_delivered=False)

    def get_queryset(self, *args, **kwargs):
        # return super().get_queryset()\
        return OrderQuerySet(self.model, *args, using=self._db, **kwargs)\
            .filter(is_paid=True)\
            .select_related('customer',)\
            .prefetch_related('products', 'items')


class CartManager(models.Manager):
    def placed(self):
        return self.get_queryset().filter(is_placed=True)

    def abandonned(self):
        return self.get_queryset().filter(is_placed=False)

    def get_queryset(self):
        return super().get_queryset()\
            .filter(is_paid=False, is_delivered=False)\
            .select_related('customer',)\
            .prefetch_related('products', 'items')
