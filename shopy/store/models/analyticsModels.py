# from django.db import models

from miq.analytics.models import Hit

from .managers import ShopHitManager


class ShopHit(Hit):
    class Meta:
        proxy = True

    objects = ShopHitManager()
