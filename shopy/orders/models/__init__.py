import logging

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

from .managers import CartManager, OrderManager

logger = logging.getLogger(__name__)
User = get_user_model()

app_name = 'orders'

"""
============================ ORDER/CART
"""


class Order(BaseModelMixin):
    customer = models.ForeignKey(
        f'{app_name}.Customer',
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
        verbose_name = _('Orders settings')
        verbose_name_plural = _('Orders settings')


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
        f'{app_name}.Order', related_name='items',
        on_delete=models.PROTECT, null=True, blank=True)

    # PRODUCT DETAILS
    product_id = models.CharField(
        _("Product ID"), max_length=99,
        null=True, blank=True
    )
    name = models.CharField(_("Name"), max_length=99)
    url = models.URLField(_("Product link"), max_length=500)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True)
    size = models.CharField(
        _("Size"), max_length=150,
        null=True, blank=True
    )

    is_sale = models.BooleanField(_("Is on sale"), default=False)
    image_url = models.URLField(_("Image link"), max_length=500, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    # for anything else, add a json field

    def __str__(self):
        return f'{self.product}'

    def get_subtotal(self):
        return self.get_price() * self.quantity

    def get_price(self) -> 'Decimal':
        return self.price or self.product.get_price()


"""
============================ CUSTOMER
"""


class CustomerUser(User):
    class Meta:
        proxy = True


class Customer(BaseModelMixin):
    user = models.OneToOneField(
        CustomerUser, related_name='customer',
        null=True, blank=True,
        on_delete=models.PROTECT
    )
    added_by = models.ForeignKey(
        'staff.User', related_name='added_customers',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    name = models.CharField(
        _("Name"), max_length=99,
        validators=[
            MinLengthValidator(4, message=_("Veuillez entrer votre nom et prénom."))
        ],
    )
    phone = models.CharField(
        _("Phone Number"), max_length=50, unique=True,
        validators=[
            MinLengthValidator(4, message=_("Veuillez entrer votre numéro de téléphone."))]
    )
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else self.phone

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


"""
============================ SETTINGS
"""


class CheckoutMethod(models.TextChoices):
    # PAY = 'PAY', _('Use payment platforms')
    MSG = 'MSG', _('Use messaging platforms')


class OrdersSetting(BaseModelMixin):
    site = models.OneToOneField(
        Site, verbose_name=_("Site"),
        # null=True, blank=True,
        on_delete=models.SET_NULL, default=settings.SITE_ID,
        related_name='orders')
    checkout_method = models.CharField(
        _("Checkout method"), max_length=50,
        choices=CheckoutMethod.MSG, default=CheckoutMethod.MSG)
