import logging

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin


logger = logging.getLogger(__name__)
User = get_user_model()


class CheckoutMethod(models.TextChoices):
    PAY = 'PAY', _('Use payment platforms')
    MSG = 'MSG', _('Use messaging platforms')


class OrdersSetting(BaseModelMixin):
    site = models.OneToOneField(
        Site, verbose_name=_("Site"), null=True,
        on_delete=models.SET_NULL, default=settings.SITE_ID,
        related_name='orders')
    checkout_method = models.CharField(
        _("Checkout method"), max_length=50,
        choices=CheckoutMethod.choices, default=CheckoutMethod.MSG)
