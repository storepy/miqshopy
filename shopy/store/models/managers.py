import datetime as dt
from django.apps import apps

from django.db import models
from django.db.models import Count
from django.db.models.functions import Concat

from miq.analytics.models.managers import HitManager


class ProductQueryset(models.QuerySet):

    def has_sizes(self):
        from shopy.store.models import ProductSize

        sizes = ProductSize.objects.exclude(quantity__lt=1)
        return self.filter(id__in=sizes.values_list('product_id', flat=True))

    def hits(self):
        if not apps.is_installed('miq.analytics'):
            return self.none()

        from miq.analytics.models import Hit

        return Hit.objects.filter(path__contains='/shop/')  # type: models.Queryset

    def by_category_count(self):
        return self.values('category__name').order_by('category__name').annotate(count=Count('category__name'))

    # for search

    def by_name(self, value):
        if not isinstance(value, str):
            return self.none()

        keys = (
            'name', 'description', 'category__name',
            'category__description', 'attributes__value',
            'supplier_items__item_sn'
        )

        return self.annotate(
            values=Concat(*keys, output_field=models.CharField())
        ).filter(values__icontains=value.lower())\
            .order_by('name').distinct('name')

    def by_price(self, amount: int):
        return self.filter(
            models.Q(retail_price__lte=amount)
            | models.Q(sale_price__lte=amount)
        ).distinct()

    def is_new(self, *, days: int = 30):
        if not isinstance(days, int):
            days = 30

        days = dt.date.today() - dt.timedelta(days=days)
        return self.filter(created__date__gte=days)

    def is_on_sale(self):
        return self.filter(is_on_sale=True, sale_price__gte=0)

    def slice(self, *, count: int = None) -> list:
        """
        Return a list(not a queryset) of products. Empty list if count is not specified
        """
        if isinstance(count, int):
            return self[:count]
        return []

    def draft(self):
        return self.exclude(slug__in=self.published().values_list('slug', flat=True))

    def to_cart(self):
        # TODO: Exclude invalid sizes
        return self.published()

    def published(self):
        """
        Products that have a retail price, a category, are published
        """
        return self\
            .exclude(retail_price__isnull=True)\
            .exclude(category__isnull=True)\
            .exclude(category__meta_slug__isnull=True)\
            .filter(category__is_published=True, is_published=True)

    def order_for_shop(self):
        return self.order_by('-is_pinned', 'is_oos', 'stage', 'position', '-created', 'name')


class ManagerMixin:
    def draft(self):
        return self.get_queryset().draft()

    def published(self):
        return self.get_queryset().published()


class ProductManager(ManagerMixin, models.Manager):

    def get_queryset(self, *args, **kwargs):
        return ProductQueryset(self.model, *args, using=self._db, **kwargs)\
            .select_related('category', 'cover')\
            .prefetch_related('images')


class CategoryQuerySet(models.QuerySet):
    def has_products(self, *, published=True):
        """
        Filter categories that have products
        """
        qs = self.products_count()
        if not published:
            return qs.filter(products_count__gte=1)
        return qs.filter(published_count__gte=1)

    def products_count(self):
        """
        Annotates queryset items with 'products_count','published_count' and 'draft_count' fields
        """
        return self.annotate(
            products_count=Count('products'),
            published_count=Count(
                'products', filter=models.Q(products__is_published=True)
            ),
            draft_count=Count(
                'products', filter=models.Q(products__is_published=False)
            ),
        )

    def draft(self):
        return self.exclude(slug__in=self.published().values_list('slug', flat=True))

    def published(self):
        """
        Categories with a public slug and is_published is True
        """
        return self\
            .exclude(meta_slug__isnull=True)\
            .filter(is_published=True)


class CategoryManager(ManagerMixin, models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)\
            .select_related('cover')


class SupplierOrderQuerySet(models.QuerySet):
    pass


class SupplierOrderManager(ManagerMixin, models.Manager):
    def get_queryset(self):
        return SupplierOrderQuerySet(self.model, using=self._db)\
            .prefetch_related('items')


class ShopHitManager(HitManager):
    def get_queryset(self):
        return super().get_queryset()\
            .exclude(is_bot=True)\
            .filter(path__icontains='/shop')\
            .exclude(path__icontains='/feed')\
            .exclude(path__icontains='fb-products')
