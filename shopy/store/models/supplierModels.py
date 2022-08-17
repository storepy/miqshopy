

from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin, Currency
from miq.core.utils import get_text_choices

from ..utils import price_to_dict

from .managers import SupplierOrderManager

app_name = 'store'


class SupplierChoice(models.TextChoices):
    SHEIN = 'SHEIN', _('Shein')
    PLT = 'PLT', _('Pretty Little Thing')
    ASOS = 'ASOS', _('Asos')
    FNOVA = 'FNOVA', _('Fashion Nova')
    # ZARA = 'ZARA', _('Zara')


SupplierChoices = get_text_choices(SupplierChoice)


SUPPLIER_MAP = {
    SupplierChoice.SHEIN: {
        'id': 'detail__goods_id',
        'productCode': 'detail__goods_sn',
        'category': 'currentCat__cat_name',
        'name': 'detail__goods_name',
        'cover': 'detail__original_img',
        'sale_price': 'detail__salePrice__amount',
        'retail_price': 'detail__retailPrice__amount',
        'is_on_sale': 'detail__is_on_sale',
        'in_stock': 'detail__is_stock_enough',
    },
    SupplierChoice.PLT: {
        'sku': 'sku',
        'name': 'name',
        'description': 'description',
        'cover': 'image',
        'availability': 'offers__availability',
        'attrs__couleur': 'color',
        'cost': 'offers__price',
        'cost_currency': 'offers__priceCurrency',
    },
    SupplierChoice.FNOVA: {
        'id': 'id',
        'sku': 'sku',
        'name': 'title',
        'category': 'product_type',
        'cover': 'featured_image',
        'handle': 'handle',
        'cost': 'price',
        'attrs': 'tags',
        'imgs': 'media'
    }
}


class SupplierOrder(BaseModelMixin):
    name = models.CharField(_("Name"), max_length=200, default='New supplier order')
    order_id = models.CharField(_("Order ID"), max_length=200, blank=True, null=True)

    currency = models.CharField(
        verbose_name=_('Currency'),
        max_length=10, choices=Currency.choices,
        null=True, blank=True)

    supplier = models.CharField(
        verbose_name=_('Supplier'),
        max_length=50, choices=SupplierChoice.choices,
        default=SupplierChoice.SHEIN)

    is_paid = models.BooleanField(_("Is paid"), default=False)
    is_paid_dt = models.DateTimeField(_("Date of payment"), blank=True, null=True)
    is_fulfilled_dt = models.DateTimeField(
        _("Date of fulfillment"), blank=True, null=True)

    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='FOB Price, excluding inbound shipping, taxes '
        'and others costs')

    products = models.ManyToManyField(
        f'{app_name}.Product', verbose_name=_("Products"),
        related_name='supplier_orders', through=f'{app_name}.SupplierItem',
        blank=True)

    objects = SupplierOrderManager()

    def get_category_count(self):
        return self.products.all().by_category_count()

    def get_avg_cost(self):
        return self.items.aggregate(Avg('cost')).get('cost__avg')

    def get_items_revenue(self):
        total = sum(product.get_price() for product in self.products.all())
        return price_to_dict(total, self.currency)

    def get_items_cost(self):
        total = sum(item.cost for item in self.items.all())
        return price_to_dict(total, self.currency)

    class Meta:
        verbose_name = _('Supplier Order')
        verbose_name_plural = _('Supplier Orders')
        ordering = ('-created',)


class SupplierItem(BaseModelMixin):
    order = models.ForeignKey(
        f'{app_name}.SupplierOrder', verbose_name=_("Order"),
        on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        f'{app_name}.Product', verbose_name=_("Product"),
        on_delete=models.CASCADE, related_name='supplier_items')

    item_sn = models.CharField(_("Item serial number"), max_length=200, null=True, blank=True)
    category = models.CharField(_("Supplier category"), max_length=200, null=True, blank=True)
    url = models.URLField(_("Supplier url"), max_length=900, null=True, blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='FOB Price, excluding inbound shipping, taxes '
        'and others costs'
    )
    data = models.JSONField(default=dict)

    def supplier(self):
        return self.order.supplier
