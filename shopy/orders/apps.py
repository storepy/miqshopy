from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    name = 'shopy.orders'
    verbose_name = _('Orders')
    verbose_name_plural = _('Orders')
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
