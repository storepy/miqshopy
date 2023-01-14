import hashlib
import logging
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin


from .. import __app_name__
from .managers import CartManager, OrderManager

logger = logging.getLogger(__name__)
User = get_user_model()

# Abandonned cart->placed?->cart->paid?->order->delivered?->sale


def get_transaction_id(instance):
    return hashlib.shake_128(bytes(f'{instance.slug}', encoding='utf-8')).hexdigest(4)


class Discount(BaseModelMixin):
    # currency
    order = models.ForeignKey(f'{__app_name__}.Order', on_delete=models.CASCADE, related_name='discounts',)

    description = models.TextField()
    amt = models.DecimalField(verbose_name=_("amount"), max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'-{self.value}'

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')


class Order(BaseModelMixin):
    customer = models.ForeignKey(
        f'{__app_name__}.Customer',
        on_delete=models.PROTECT, related_name='orders',
        null=True, blank=True,
    )

    # discount

    # Cart #

    # delivery location, etc
    notes = models.TextField(blank=True, null=True)

    # Carts are orders that are not yet completed
    # use to differenciiate abandoned carts
    is_placed = models.BooleanField(default=False)
    # When customer would like to be delivered. 7 days window
    dt_delivery = models.DateTimeField(null=True, blank=True)
    # delivery_cost = models.DecimalField(
    #     decimal_places=2, max_digits=50,
    #     default=0.00
    # )

    # Order #

    # Finance
    is_paid = models.BooleanField(default=False)
    total = models.DecimalField(
        decimal_places=2, max_digits=50,
        null=True, blank=True
    )

    # Sales #

    # barcode
    is_delivered = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    dt_delivered = models.DateTimeField(null=True, blank=True)

    # Admin

    added_by = models.ForeignKey(
        'staff.User', related_name='added_orders',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    products = models.ManyToManyField(
        'store.Product', through=f'{__app_name__}.OrderItem',
        blank=True)

    # placeorder: generate trans_id, barcode

    # notify admins

    objects = OrderManager()

    def mark_delivered(self):
        assert self.is_paid, 'Cart is not paid'
        assert self.is_delivered is False, 'Order is already delivered'

        self.is_delivered = True
        self.dt_delivered = timezone.now()

        self.save()
        logger.info(f'Order[{self.id}] delivered')

    def get_total(self):
        return self.get_subtotal() - self.get_discounts()

    def get_discounts(self):
        return self.discounts.all().aggregate(models.Sum('amt'))['amt__sum'] or Decimal(0)
        return sum(item.amt for item in self.discounts.all())

    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = get_transaction_id(self)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_paid:
            raise Exception('Cannot delete paid order')

        self.items.all().delete()
        return super().delete(*args, **kwargs)

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Orders')
        verbose_name_plural = _('Orders')

    def __str__(self) -> str:
        return f'Order {self.id}: {self.items_count}'

    def __len__(self) -> int:
        return self.items_count


class Cart(Order):
    class Meta:
        proxy = True
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    objects = CartManager()

    def mark_paid(self):
        # TODO: check if cart is placed and not delivered
        assert self.is_placed, 'Cart is not placed'
        assert self.is_delivered is False, 'Cart is already delivered'

        logger.info(f'Cart[{self.id}]: Updating {self.items_count} items.')

        # TODO: update stock
        for item in self.items.all():
            size = item.size
            size.quantity -= item.quantity
            size.save()

        # self.items.update(size__quantity=models.F('size__quantity') - models.F('quantity'))

        self.is_paid = True
        #
        self.total = self.get_total()
        #
        self.transaction_id = get_transaction_id(self)
        self.save()
        logger.info(f'Cart[{self.id}] paid')

        # TODO: notify admins, send email

        return self

    def place(self):
        assert self.items_count > 0, 'Cart is empty'
        assert self.customer, 'Cart has no customer'
        assert self.is_paid is False, 'Cart is already paid'

        if self.is_placed:
            logger.info(f'Cart[{self.id}]: Already placed')
            return self

        self.is_placed = True
        self.save()

        logger.info(f'Cart[{self.id}] placed')
        return self


class OrderItem(BaseModelMixin):

    order = models.ForeignKey(
        f'{__app_name__}.Order', related_name='items',
        on_delete=models.PROTECT, null=True, blank=True)

    # PRODUCT DETAILS
    product = models.ForeignKey(
        "store.Product", verbose_name=_("Product"),
        related_name='order_items', on_delete=models.PROTECT
    )

    name = models.CharField(_("Name"), max_length=99)
    price = models.DecimalField(
        verbose_name=_("Current price"),
        max_digits=10, decimal_places=2,
        null=True, blank=True)
    size = models.ForeignKey(
        "store.ProductSize", verbose_name=_("Size"),
        on_delete=models.PROTECT,
    )
    was_sale = models.BooleanField(_("Is on sale"), default=False)
    img = models.OneToOneField(
        'store.ProductImage', verbose_name=_("Image"), on_delete=models.PROTECT,
        blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # for anything else, add a json field

    def get_subtotal(self):
        return self.get_price() * self.quantity

    def get_price(self) -> 'Decimal':
        return self.price or self.product.get_price()

    def __str__(self):
        return f'{self.product}'

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
