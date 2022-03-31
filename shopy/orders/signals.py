
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.sites.models import Site

from .models import OrdersSetting


@receiver(signals.post_save, sender=Site)
def on_site_did_save(sender, instance, created, **kwargs):
    if not OrdersSetting.objects.filter(site=instance).exists():
        OrdersSetting.objects.create(site=instance)
