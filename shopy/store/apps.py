from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StoreConfig(AppConfig):
    name = 'shopy.store'
    verbose_name = _('Store')
    verbose_name_plural = _('Store')
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from . import signals
