from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClientConfig(AppConfig):
    name = 'shopy.shop'
    verbose_name = _('Shop Storefront')
    verbose_name_plural = _('Shop Storefront')
    default_auto_field = 'django.db.models.BigAutoField'
