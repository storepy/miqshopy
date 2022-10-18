
from django.db import models

from django.utils.translation import gettext_lazy as _

from miq.analytics.models import Hit
from miq.core.models import BaseModelMixin
from .managers import ShopHitManager


class ShopHit(Hit):
    class Meta:
        proxy = True

    objects = ShopHitManager()


class AbstractHit(BaseModelMixin):
    url = models.TextField(max_length=500)
    referrer = models.TextField(blank=True, null=True)

    # visitor
    user_agent = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(
        unpack_ipv4=True, verbose_name=_('Ip address'),
        null=True, blank=True)

    count = models.PositiveIntegerField(default=1)

    #
    # is_bot = models.BooleanField(_('Is bot'), default=False)

    class Meta:
        abstract = True


class ProductHit(AbstractHit):
    customer = models.ForeignKey("sales.Customer", verbose_name=_(
        "Customer"), on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey("store.Product", verbose_name=_("Product Hit"), on_delete=models.CASCADE)


class CategoryHit(AbstractHit):
    customer = models.ForeignKey("sales.Customer", verbose_name=_(
        "Customer"), on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey("store.Category", verbose_name=_("Category Hit"), on_delete=models.CASCADE)

    #
