
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site

from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin, Currency, Currencies


class Discount(BaseModelMixin):

    code = models.CharField(max_length=50, unique=True)
    valid_to = models.DateField(
        null=True, blank=True, help_text='format: yyyy-mm-dd')
    models.DecimalField(
        verbose_name=_("Current price"),
        max_digits=10, decimal_places=2,
        null=True, blank=True)

    use_count = models.PositiveIntegerField(default=0)

    value_fixed = models.PositiveIntegerField(default=0)
    value_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='0 to 100')

    active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.site} Shopy'

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Shop settings')
        verbose_name_plural = _('Shop settings')
