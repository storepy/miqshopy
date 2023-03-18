import logging

from django.db import models, transaction
from rest_framework import serializers

from miq.analytics.utils import get_hit_data
from shopy.store.models import Product, Category, ProductHit, CategoryHit
from shopy.sales.models import Customer


log = logging.getLogger(__name__)
price_ranges = ['5000', '10000', '25000', '50000']


class ProductFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering products.
    """

    q = serializers.CharField(required=False)
    sale = serializers.ChoiceField(choices=['all'], required=False)
    price = serializers.ChoiceField(choices=price_ranges, required=False)


def product_qs(*, filters: dict = {}) -> models.QuerySet:
    """
    Return a queryset of published products filtered by the given filters.
    """

    # qs = Product.objects.to_cart()
    qs: models.QuerySet = Product.objects.published()
    if not filters:
        return qs

    if q := filters.get('q'):
        qs = qs.search_by_query(q)

    if sale := filters.get('sale'):
        if sale == 'all':
            qs = qs.is_on_sale()

    if price := filters.get('price'):
        qs = qs.by_price(price)

    return qs


def category_qs(*, filters: dict = None) -> models.QuerySet:
    """
    Return a queryset of published categories filtered by the given filters.
    Categories must have at least one published product.
    """

    qs = Category.objects.published().has_products()
    if not filters:
        return qs

    return qs


def customer_get_from_request(request, /, response=None) -> Customer:
    """
    Return the customer from the given request or None.
    """

    if request.user.is_authenticated and (cus := getattr(request.user, 'customer', None)):
        return cus

    return request.customer


@transaction.atomic
def product_hit_create(*, product: Product, customer, request, response, **kwargs) -> ProductHit:

    _ = get_hit_data(request, response)
    filter = {'url': _['url'], 'user_agent': _['user_agent'], 'ip': _['ip'], }

    hits = ProductHit.objects.filter(**filter)
    if not hits.exists():
        hit = ProductHit.objects.create(**filter, product=product, customer=customer)
        log.info(f'[{hit.id}]: Product hit created')
        return hit

    hit = hits.first()
    hit.count += 1

    if not hit.customer and customer:
        hit.customer = customer

    hit.save()

    category_hit_create(category=product.category, customer=customer, request=request, response=response)

    log.info(f'[{hit.id}]: Product hit updated')
    return hit


def category_hit_create(*, category: Category, customer, request, response, **kwargs) -> CategoryHit:
    _ = get_hit_data(request, response)
    filter = {'url': _['url'], 'user_agent': _['user_agent'], 'ip': _['ip'], }

    hits = CategoryHit.objects.filter(**filter)
    if not hits.exists():
        hit = CategoryHit.objects.create(**filter, category=category, customer=customer)
        log.info(f'[{hit.id}]: Category hit created')
        return hit

    hit = hits.first()
    hit.count += 1

    if not hit.customer and customer:
        hit.customer = customer

    hit.save()

    log.info(f'[{hit.id}]: Category hit updated')
    return hit
