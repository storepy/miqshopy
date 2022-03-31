
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site

from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin, Currency, Currencies


def jsondef():
    return dict({
        # on homepage
        'show_active_suppliers': False,

        # detail page
        'show_product_supplier': False,

        # settings
        'has_suppliers': False,

    })


class ShopSetting(BaseModelMixin):
    site = models.OneToOneField(
        Site, verbose_name=_("Site"),
        null=True, blank=True,
        on_delete=models.SET_NULL, default=settings.SITE_ID,
        related_name='shopy')

    config = models.JSONField(_("Config"), default=jsondef)

    currencies = Currencies
    currency = models.CharField(
        verbose_name=_('Currency'),
        max_length=10, choices=Currency.choices,
        default=Currency.XOF)

    # delivery

    # policies

    returns = models.TextField(
        _("Returns Policy"), null=True, blank=True)
    returns_html = models.TextField(
        _("Returns Policy"), null=True, blank=True)

    size_guide = models.TextField(
        _("Size Guide"), null=True, blank=True)
    size_guide_html = models.TextField(
        _("Size Guide"), null=True, blank=True)

    def save(self, *args, **kwargs):
        # maintain schema
        self.config = {**jsondef(), **self.config}
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.site} Shopy'

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Shop settings')
        verbose_name_plural = _('Shop settings')
