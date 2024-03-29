import logging


from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from miq.core.models import BaseModelMixin

from .managers import CategoryManager

logger = logging.getLogger(__name__)


class Category(BaseModelMixin):
    # new arrivals, best sellers, dresses, tops, lingerie, bodysuits, romper, accessories, SALE
    page = models.OneToOneField(
        'store.CategoryPage', on_delete=models.PROTECT, blank=True,
        related_name='shopy_category')

    parent = models.ForeignKey(
        'self', verbose_name=_("Parent category"), on_delete=models.PROTECT,
        blank=True, null=True, related_name='children'
    )

    cover = models.OneToOneField(
        'core.Image', verbose_name=_("Cover"), on_delete=models.SET_NULL,
        blank=True, null=True
    )

    name = models.CharField(max_length=200, db_index=True)
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
        max_length=200, unique=True, db_index=True,
        null=True, blank=True
    )

    objects = CategoryManager()

    def get_products(self):
        from .m_product import Product
        return Product.objects.filter(
            models.Q(category=self)
            | models.Q(category__in=self.children.all())
        ).distinct()

    def get_hit_data(self):
        data = super().get_hit_data()
        data.update({
            'name': self.name,
            'img': None,
        })

        if self.cover:
            data['img'] = self.cover.src.url
        return data

    def save(self, *args, **kwargs):
        if self.parent and self.parent.pk == self.pk:
            raise Exception("Can't be own parent")

        if self.is_published and not self.dt_published:
            self.dt_published = timezone.now()

        super().save(*args, **kwargs)

    def publish(self,):
        assert self.meta_slug, 'Category must have a meta slug'
        assert self.meta_title, 'Category must have a meta title'

        if self.is_published:
            logger.warning(f'[{self.name}]: Category already published')
            return

        self.is_published = True
        self.dt_published = timezone.now()
        self.save()

    def unpublish(self,):
        if not self.is_published:
            logger.warning(f'[{self.name}]: Category not published')
            return

        self.is_published = False
        self.save()

    def get_is_public(self):
        return self.meta_slug and self.is_published

    @property
    def detail_path(self):
        return reverse_lazy('shopy:category', args=[self.meta_slug])

    def __str__(self):
        return capfirst(self.name)

    class Meta:
        ordering = ('position', '-created', 'name')
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
