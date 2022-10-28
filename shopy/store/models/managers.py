import datetime as dt
from django.apps import apps
from django.db import models
from django.utils import timezone
from django.db.models import Count
# from django.db.models.functions import Concat
from django.contrib.postgres.search import SearchQuery, SearchVector

from miq.analytics.models.managers import HitManager


class ProductQueryset(models.QuerySet):
    def to_cart(self):
        return self.published().exclude(is_oos=True).has_sizes()

    def has_no_category(self):
        return self.filter(category__isnull=True)

    def has_meta_slug_gt_100(self):
        # Facebook recommends that meta slugs be less than 100 characters
        return self.filter(meta_slug__gt=100)

    def has_name_gt_65(self):
        # Facebook recommends that product names be less than 65 characters
        return self.filter(name__gt=65)

    def has_no_description(self):
        return self.filter(
            models.Q(description='') | models.Q(description=None) | models.Q(description__isnull=True)
        ).distinct()

    def has_no_sizes(self):
        return self\
            .annotate(sizes_count=Count('sizes', filter=models.Q(sizes__quantity__gt=0)))\
            .filter(sizes_count=0)

    def has_sizes(self):
        return self\
            .annotate(sizes_count=Count('sizes', filter=models.Q(sizes__quantity__gt=0)))\
            .exclude(sizes_count=0)

        # from shopy.store.models import ProductSize

        # sizes = ProductSize.objects.exclude(quantity__lt=1)
        # return self.filter(id__in=sizes.values_list('product_id', flat=True))

    def hits(self):
        if not apps.is_installed('miq.analytics'):
            return self.none()

        from miq.analytics.models import Hit

        return Hit.objects.filter(path__contains='/shop/')  # type: models.Queryset

    def by_category_count(self):
        return self.values('category__name').order_by('category__name').annotate(count=Count('category__name'))

    def search_by_query(self, query: str):
        """
        # https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/search/#searchvector
        """
        if not isinstance(query, str) or not query:
            return self.none()

        search_vector = SearchVector(
            'name', 'description', 'category__name', 'category__description',
            'attributes__value', 'supplier_items__item_sn')
        search_qs = self.annotate(search=search_vector).filter(search=SearchQuery(query))\
            .values('id').annotate(count=Count('id')).values_list('id', flat=True)
        return self.filter(id__in=search_qs)

        # return qs.distinct('position', 'created', 'name')

    # def by_name(self, value):
    #     if not isinstance(value, str):
    #         return self.none()

    #     keys = (
    #         'name', 'description', 'category__name',
    #         'category__description', 'attributes__value',
    #         'supplier_items__item_sn'
    #     )

    #     return self.annotate(
    #         values=Concat(*keys, output_field=models.CharField())
    #     ).filter(values__icontains=value.lower())\
    #         .order_by('name').distinct('name')

    def by_price(self, amount: int):
        return self.filter(
            models.Q(retail_price__lte=amount)
            | models.Q(sale_price__lte=amount)
        ).distinct()

    def is_new(self, *, days: int = 30):
        if not isinstance(days, int):
            days = 30

        return self\
            .filter(created__date__gte=timezone.now() - dt.timedelta(days=days))

    def is_on_sale(self):
        return self.filter(is_on_sale=True, sale_price__gt=0)

    def slice(self, *, count: int = None) -> list:
        """
        Return a list(not a queryset) of products. Empty list if count is not specified
        """
        if isinstance(count, int):
            return self[:count]
        return []

    def draft(self):
        return self.exclude(slug__in=self.published().values_list('slug', flat=True))

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
    def total(self):
        return self.filter(is_paid=True).aggregate(total=models.Sum('total_cost'))['total']


class SupplierOrderManager(ManagerMixin, models.Manager):
    def get_queryset(self):
        return SupplierOrderQuerySet(self.model, using=self._db)\
            .prefetch_related('items')


class ShopHitManager(HitManager):
    def products(self):
        return self.get_queryset().exclude(
            models.Q(model='category')
            | models.Q(path='/shop/')
            | models.Q(path__startswith='/api/v1/')
        )

    def categories(self):
        return self.get_queryset().exclude(models.Q(model='product'))

    def get_queryset(self):
        return super().get_queryset()\
            .exclude(is_bot=True)\
            .exclude(path__icontains='/feed')\
            .exclude(path__icontains='fb-products')\
            .filter(models.Q(path__startswith='/shop'))
