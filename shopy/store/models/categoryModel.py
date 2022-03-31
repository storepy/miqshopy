from django.db import models
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

from .managers import CategoryManager


class Category(BaseModelMixin):
    # new arrivals, best sellers, dresses, tops, lingerie, bodysuits, romper, accessories, SALE
    page = models.OneToOneField(
        'store.CategoryPage', on_delete=models.PROTECT, blank=True,
        related_name='shopy_category')

    cover = models.OneToOneField(
        'core.Image', verbose_name=_("Cover"), on_delete=models.SET_NULL,
        blank=True, null=True
    )

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    #
    is_published = models.BooleanField(
        default=False, help_text=_('Publish this category'))
    dt_published = models.DateTimeField(
        blank=True, null=True, help_text=_('Publication date'))
    position = models.PositiveIntegerField(default=1)

    #
    meta_title = models.CharField(
        max_length=250, help_text=_('Cat Meta title'),
        null=True, blank=True
    )
    meta_description = models.CharField(
        max_length=500, help_text=_('Cat Meta description'),
        null=True, blank=True
    )
    meta_slug = models.SlugField(
        max_length=100, unique=True, db_index=True,
        null=True, blank=True
    )

    objects = CategoryManager()

    def save(self, *args, **kwargs):
        if self.is_published and not self.dt_published:
            self.dt_published = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return capfirst(self.name)

    def get_is_public(self):
        return self.meta_slug and self.is_published
        # return reverse_lazy('shopy:category', args=[self.meta_slug])

    class Meta:
        ordering = ('position', '-created', 'name')
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
