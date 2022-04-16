
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

app_name = 'store'


class ProductSize(BaseModelMixin):
    # sku = models.CharField(_("Sku"), max_length=99, null=True, blank=True,)
    product = models.ForeignKey(
        f'{app_name}.Product', related_name='sizes', on_delete=models.CASCADE)

    name = models.CharField(max_length=20, help_text='Select size')
    code = models.CharField(max_length=10, )
    quantity = models.PositiveIntegerField(
        default=1, help_text='Enter quantity',
        validators=[MinValueValidator(0)])

    # retail_price, sale_price

    def get_availability(self):
        if self.quantity <= 0:
            return 'out of stock'
        return 'in stock'

    class Meta:
        ordering = ('created', 'name')
        verbose_name = 'Product size'
        verbose_name_plural = 'Product sizes'

        constraints = [
            models.UniqueConstraint(
                fields=['product', 'name', 'code'], name='unique_product_size_name_code',
            )
        ]


class ProductAttribute(BaseModelMixin):

    product = models.ForeignKey(
        f'{app_name}.Product', related_name='attributes', on_delete=models.CASCADE)

    name = models.CharField(max_length=30, help_text=_('Name'))
    value = models.CharField(max_length=99, help_text=_('Value'))

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('created', 'name')
        verbose_name = 'Product attribute'
        verbose_name_plural = 'Product attributes'

        constraints = [
            models.UniqueConstraint(
                fields=['product', 'name'], name='unique_product_attribute_name',
            )
        ]
