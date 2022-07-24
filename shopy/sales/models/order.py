import logging

from django.db import models
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

from .. import __app_name__
from .managers import CartManager, OrderManager

logger = logging.getLogger(__name__)
User = get_user_model()


class Order(BaseModelMixin):
    customer = models.ForeignKey(
        f'{__app_name__}.Customer',
        on_delete=models.PROTECT, related_name='orders',
        null=True, blank=True,
    )

    # discount

    # delivery location, etc
    notes = models.TextField(blank=True, null=True)

    # Carts are orders that are not yet completed
    is_completed = models.BooleanField(default=False)

    # Finance
    is_paid = models.BooleanField(default=False)
    total = models.DecimalField(
        decimal_places=2, max_digits=50,
        null=True, blank=True
    )
    # delivery_cost = models.DecimalField(
    #     decimal_places=2, max_digits=50,
    #     default=0.00
    # )

    # When customer would like to be delivered. 7 days window
    dt_delivery = models.DateTimeField(null=True, blank=True)

    # barcode
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    dt_delivered = models.DateTimeField(null=True, blank=True)

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

    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items.all())

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f'Order {self.id}: {self.items_count}'

    def __len__(self):
        return self.items_count

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Orders')
        verbose_name_plural = _('Orders')


class Cart(Order):
    class Meta:
        proxy = True

    objects = CartManager()


class OrderItem(BaseModelMixin):
    class Meta:
        ordering = ('-created',)
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

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
        blank=True, null=True
    )
    quantity = models.PositiveIntegerField(default=1)

    # for anything else, add a json field

    def __str__(self):
        return f'{self.product}'

    def get_subtotal(self):
        return self.get_price() * self.quantity

    def get_price(self) -> 'Decimal':
        return self.price or self.product.get_price()
