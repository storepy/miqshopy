from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesConfig(AppConfig):
    name = 'shopy.sales'
    verbose_name = _('Sales')
    verbose_name_plural = _('Sales')
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
